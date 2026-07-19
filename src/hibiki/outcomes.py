from __future__ import annotations

import hashlib
import json
import time
from collections.abc import Callable
from dataclasses import dataclass

from hibiki.chisei import ChiseiGateway
from hibiki.contracts import chisei_pb2, sekai_pb2
from hibiki.evidence import PRODUCER_IDENTITY, REPLY_TYPE, SNAPSHOT_TYPE
from hibiki.records import CausalRepositories, OutcomeRecord, PublicationRecord
from hibiki.sekai import SekaiGateway


class OutcomeWorkflowError(RuntimeError):
    """Raised when classification or reporting cannot be trusted."""


CATEGORIES = frozenset(
    {
        "potential_user",
        "potential_tester_or_contributor",
        "substantive_technical_discussion",
        "general_reaction",
        "irrelevant_or_low_signal",
    }
)
QUALIFIED_CATEGORIES = frozenset(
    {
        "potential_user",
        "potential_tester_or_contributor",
        "substantive_technical_discussion",
    }
)
CONFIRMATION_TARGET = 25
AUTOMATIC_CONFIDENCE_BPS = 9_000
CALIBRATION_ACCURACY_BPS = 9_000
CLASSIFICATION_ACTION = "hibiki.reply_classification"
CONFIRMATION_ACTION = "hibiki.reply_classification_confirmation"
CALIBRATION_ACTION = "hibiki.reply_classification_evaluation"
CLASSIFICATION_BATCH_SIZE = 20


@dataclass(frozen=True, slots=True)
class ReplyClassification:
    submission_id: str
    reply_id: str
    category: str
    confidence_bps: int
    disposition: str
    operation_id: str


@dataclass(frozen=True, slots=True)
class ClassificationResult:
    publication_external_id: str
    classifications: tuple[ReplyClassification, ...]
    confirmed_count: int
    calibrated: bool


@dataclass(frozen=True, slots=True)
class ConfirmationResult:
    submission_id: str
    predicted_category: str
    confirmed_category: str
    corrected: bool
    confirmed_count: int
    calibrated: bool


@dataclass(frozen=True, slots=True)
class OutcomeReport:
    outcome: OutcomeRecord
    status: str
    snapshot_submission_id: str
    classifications: tuple[ReplyClassification, ...]
    lineage: dict[str, object]


def classify_replies(
    sekai: SekaiGateway,
    chisei: ChiseiGateway,
    publication_external_id: str,
    namespace: str,
    *,
    clock_ms: Callable[[], int] | None = None,
) -> ClassificationResult:
    publication = _publication(sekai, publication_external_id, namespace)
    replies = _submissions(sekai, publication.external_id, REPLY_TYPE)
    action = _scoped_action(CLASSIFICATION_ACTION, publication.external_id)
    existing = _latest_by_target(sekai.list_decisions(actor="hibiki", action=action, limit=1000))
    pending = tuple(reply for reply in replies if reply.id not in existing)
    confirmed_count, calibrated = _calibration(sekai, namespace)
    if pending:
        now = (clock_ms or (lambda: time.time_ns() // 1_000_000))()
        for batch_start in range(0, len(pending), CLASSIFICATION_BATCH_SIZE):
            batch = pending[batch_start : batch_start + CLASSIFICATION_BATCH_SIZE]
            response, operation_id = _execute_classification(chisei, batch, namespace)
            for item_index, item in enumerate(response):
                disposition = _disposition(item["confidence_bps"], calibrated)
                decision = sekai_pb2.Decision(
                    id=_decision_id("classification", item["submission_id"]),
                    timestamp=now + batch_start + item_index,
                    actor="hibiki",
                    action=action,
                    reason="governed native Chisei reply classification",
                    evidence={
                        "reply_id": item["reply_id"],
                        "category": item["category"],
                        "confidence_bps": str(item["confidence_bps"]),
                        "disposition": disposition,
                        "operation_id": operation_id,
                    },
                    target_id=item["submission_id"],
                    outcome=disposition,
                )
                sekai.record_decision(decision)
                existing[item["submission_id"]] = decision
    classifications = tuple(_decode_classification(existing[item.id]) for item in replies)
    return ClassificationResult(
        publication.external_id, classifications, confirmed_count, calibrated
    )


def confirm_classification(
    sekai: SekaiGateway,
    submission_id: str,
    category: str,
    *,
    clock_ms: Callable[[], int] | None = None,
) -> ConfirmationResult:
    if category not in CATEGORIES:
        raise OutcomeWorkflowError("confirmation category is invalid")
    submission = sekai.get_evidence_submission(submission_id)
    if submission.evidence_type != REPLY_TYPE or submission.lifecycle_state != "available":
        raise OutcomeWorkflowError("confirmation target is not available reply evidence")
    classification_action = _scoped_action(CLASSIFICATION_ACTION, submission.target_external_id)
    confirmation_action = _scoped_action(CONFIRMATION_ACTION, submission.target_external_id)
    predictions = _latest_by_target(
        sekai.list_decisions(actor="hibiki", action=classification_action, limit=1000)
    )
    prediction = predictions.get(submission_id)
    if prediction is None:
        raise OutcomeWorkflowError("reply must be classified before confirmation")
    predicted = prediction.evidence.get("category", "")
    existing = _latest_by_target(
        sekai.list_decisions(actor="operator", action=confirmation_action, limit=1000)
    ).get(submission_id)
    if existing is not None and existing.evidence.get("confirmed_category") != category:
        raise OutcomeWorkflowError("classification confirmation is already recorded")
    if existing is None:
        now = (clock_ms or (lambda: time.time_ns() // 1_000_000))()
        confirmation = sekai.record_decision(
            sekai_pb2.Decision(
                id=_decision_id("confirmation", submission_id),
                timestamp=now,
                actor="operator",
                action=confirmation_action,
                reason="operator evaluation of governed reply classification",
                evidence={
                    "predicted_category": predicted,
                    "confirmed_category": category,
                    "prediction_decision_id": prediction.id,
                },
                target_id=submission_id,
                outcome="correct" if predicted == category else "corrected",
            )
        )
    else:
        confirmation = existing
    evaluation_action = calibration_action(submission.namespace)
    evaluations = sekai.list_decisions(actor="operator", action=evaluation_action, limit=500)
    evaluated_targets = {item.target_id for item in evaluations}
    recoverable = len(evaluations) < 500 or confirmation.timestamp > min(
        item.timestamp for item in evaluations
    )
    if submission_id not in evaluated_targets and recoverable:
        sekai.record_decision(
            sekai_pb2.Decision(
                id=_decision_id("evaluation", submission_id),
                timestamp=confirmation.timestamp,
                actor="operator",
                action=evaluation_action,
                reason="calibration evaluation for governed reply classification",
                evidence={"publication_external_id": submission.target_external_id},
                target_id=submission_id,
                outcome=confirmation.outcome,
            )
        )
    confirmed_count, calibrated = _calibration(sekai, submission.namespace)
    return ConfirmationResult(
        submission_id, predicted, category, predicted != category, confirmed_count, calibrated
    )


def build_outcome_report(
    sekai: SekaiGateway,
    chisei: ChiseiGateway,
    publication_external_id: str,
    window: str,
    namespace: str,
    *,
    clock_ms: Callable[[], int] | None = None,
) -> OutcomeReport:
    if window not in {"24h", "7d"}:
        raise OutcomeWorkflowError("outcome window must be 24h or 7d")
    publication = _publication(sekai, publication_external_id, namespace)
    snapshots = tuple(
        item
        for item in _submissions(sekai, publication.external_id, SNAPSHOT_TYPE)
        if item.source_version == f"{window}:complete-v2"
        and item.source_record_id == publication.post_id
    )
    if len(snapshots) != 1:
        raise OutcomeWorkflowError(f"exactly one complete {window} snapshot is required")
    repositories = CausalRepositories.create(sekai, namespace, clock_ms=clock_ms)
    raw_outcome = repositories.outcomes.get(f"{publication.stable_id}:{window}")
    if raw_outcome is None:
        raise OutcomeWorkflowError("deterministically collected raw outcome metrics were not found")
    if (
        raw_outcome.publication_external_id != publication.external_id
        or raw_outcome.observed_at != snapshots[0].observed_at_ms
    ):
        raise OutcomeWorkflowError("raw outcome metrics do not match the selected snapshot")
    classification_result = classify_replies(
        sekai, chisei, publication.external_id, namespace, clock_ms=clock_ms
    )
    replies_by_id = {
        item.id: item for item in _submissions(sekai, publication.external_id, REPLY_TYPE)
    }
    window_end = publication.attempted_at + (86_400_000 if window == "24h" else 604_800_000)
    window_classifications = tuple(
        item
        for item in classification_result.classifications
        if replies_by_id[item.submission_id].observed_at_ms <= window_end
    )
    confirmed = _latest_by_target(
        sekai.list_decisions(
            actor="operator",
            action=_scoped_action(CONFIRMATION_ACTION, publication.external_id),
            limit=1000,
        )
    )
    unresolved = tuple(
        item
        for item in window_classifications
        if item.disposition == "confirmation_required" and item.submission_id not in confirmed
    )
    if unresolved:
        raise OutcomeWorkflowError(
            "all confirmation-required replies must be confirmed before reporting"
        )
    categories = {
        item.submission_id: confirmed[item.submission_id].evidence["confirmed_category"]
        if item.submission_id in confirmed
        else item.category
        for item in window_classifications
    }
    proposal = CausalRepositories.create(sekai, namespace).proposals.get_external(
        publication.proposal_external_id
    )
    if proposal is None:
        raise OutcomeWorkflowError("publication proposal record was not found")
    qualified = sum(
        categories[item.submission_id] in QUALIFIED_CATEGORIES for item in window_classifications
    )
    observed_at = snapshots[0].observed_at_ms
    outcome = repositories.outcomes.put(
        OutcomeRecord(
            stable_id=f"{publication.stable_id}:{window}",
            publication_external_id=publication.external_id,
            window=window,
            observed_at=observed_at,
            metrics=raw_outcome.metrics,
            qualified_replies=qualified,
        )
    )
    return OutcomeReport(
        outcome=outcome,
        status="preliminary" if window == "24h" else "final",
        snapshot_submission_id=snapshots[0].id,
        classifications=window_classifications,
        lineage={
            "source_external_id": proposal.source_external_id,
            "proposal_external_id": proposal.external_id,
            "publication_external_id": publication.external_id,
            "snapshot_submission_id": snapshots[0].id,
            "reply_submission_ids": [item.submission_id for item in window_classifications],
            "outcome_external_id": outcome.external_id,
        },
    )


def _execute_classification(
    chisei: ChiseiGateway,
    replies: tuple[sekai_pb2.EvidenceSubmissionRecord, ...],
    namespace: str,
) -> tuple[list[dict[str, object]], str]:
    ids = [item.id for item in replies]
    spec = {
        "task": "Classify each governed social.reply evidence submission.",
        "evidence_submission_ids": ids,
        "categories": sorted(CATEGORIES),
        "response_schema": {
            "classifications": [
                {
                    "submission_id": "string",
                    "reply_id": "source record id",
                    "category": "category",
                    "confidence_bps": "integer 0..10000",
                }
            ]
        },
    }
    content, operation_id = _execute(chisei, namespace, "reply_classification", spec, 2000)
    payload = _json_object(content, "classification")
    raw = payload.get("classifications")
    if not isinstance(raw, list) or len(raw) != len(replies):
        raise OutcomeWorkflowError("Chisei classification response is incomplete")
    by_id = {item.id: item for item in replies}
    parsed: list[dict[str, object]] = []
    seen: set[str] = set()
    for item in raw:
        if not isinstance(item, dict) or set(item) != {
            "submission_id",
            "reply_id",
            "category",
            "confidence_bps",
        }:
            raise OutcomeWorkflowError("Chisei classification has unexpected fields")
        submission_id = item["submission_id"]
        if (
            not isinstance(submission_id, str)
            or submission_id not in by_id
            or submission_id in seen
        ):
            raise OutcomeWorkflowError("Chisei classification references invalid evidence")
        if item["reply_id"] != by_id[submission_id].source_record_id:
            raise OutcomeWorkflowError(
                "Chisei classification reply identity does not match evidence"
            )
        if (
            item["category"] not in CATEGORIES
            or type(item["confidence_bps"]) is not int
            or not 0 <= item["confidence_bps"] <= 10_000
        ):
            raise OutcomeWorkflowError("Chisei classification values are invalid")
        seen.add(submission_id)
        parsed.append(item)
    return parsed, operation_id


def _execute(
    chisei: ChiseiGateway, namespace: str, task_type: str, spec: dict[str, object], max_tokens: int
) -> tuple[str, str]:
    digest = hashlib.sha256(json.dumps(spec, sort_keys=True).encode()).hexdigest()[:24]
    spec_json = json.dumps(spec, separators=(",", ":"), sort_keys=True)
    plan = chisei.plan_execution(
        chisei_pb2.PlanExecutionRequest(
            input=chisei_pb2.ExecutionInput(
                request_id=f"hibiki-{task_type}-{digest}",
                namespace=namespace,
                spec=spec_json,
                task_type=task_type,
                task_class="public_evidence_evaluation",
                max_tokens=max_tokens,
                # Carry the spec in the user message: Chisei does not forward
                # ``spec`` to the model when a message is present and enrichment
                # is a passthrough (see select_candidate for the full rationale).
                messages=(
                    chisei_pb2.ChatMessage(
                        role="user",
                        content=(
                            "Evaluate only the referenced governed evidence. "
                            "Use only the specification below.\n\n" + spec_json
                        ),
                    ),
                ),
                system=(
                    "Return only the required JSON. Do not use facts outside governed "
                    "evidence context."
                ),
            )
        )
    )
    if not plan.plan_id or not plan.executable or not plan.budget.allowed:
        raise OutcomeWorkflowError("Chisei rejected governed evidence execution")
    executed = chisei.execute_plan(plan)
    receipt = chisei.get_operation_receipt(
        chisei_pb2.GetOperationReceiptRequest(operation_id=plan.plan_id)
    )
    if not receipt.receipt_json:
        raise OutcomeWorkflowError("Chisei returned no operation receipt")
    _json_object(receipt.receipt_json, "operation receipt")
    if not receipt.complete or receipt.missing_surfaces:
        raise OutcomeWorkflowError("Chisei operation receipt is incomplete")
    return executed.response.content, plan.plan_id


def _publication(sekai: SekaiGateway, external_id: str, namespace: str) -> PublicationRecord:
    publication = CausalRepositories.create(sekai, namespace).publications.get_external(external_id)
    if publication is None or publication.status != "posted" or not publication.post_id:
        raise OutcomeWorkflowError("posted publication was not found")
    return publication


def _submissions(
    sekai: SekaiGateway, target: str, evidence_type: str
) -> tuple[sekai_pb2.EvidenceSubmissionRecord, ...]:
    items = sekai.list_evidence_submissions(
        producer_identity=PRODUCER_IDENTITY,
        target_external_id=target,
        evidence_type=evidence_type,
        limit=1000,
    )
    if any(item.lifecycle_state != "available" for item in items):
        raise OutcomeWorkflowError("evidence contains unavailable submissions")
    return items


def _latest_by_target(decisions: tuple[sekai_pb2.Decision, ...]) -> dict[str, sekai_pb2.Decision]:
    result: dict[str, sekai_pb2.Decision] = {}
    for decision in sorted(decisions, key=lambda item: item.timestamp, reverse=True):
        result.setdefault(decision.target_id, decision)
    return result


def _calibration(sekai: SekaiGateway, namespace: str) -> tuple[int, bool]:
    confirmations = _latest_by_target(
        sekai.list_decisions(actor="operator", action=calibration_action(namespace), limit=500)
    )
    count = len(confirmations)
    correct = sum(item.outcome == "correct" for item in confirmations.values())
    accuracy_bps = correct * 10_000 // count if count else 0
    return count, count >= CONFIRMATION_TARGET and accuracy_bps >= CALIBRATION_ACCURACY_BPS


def _disposition(confidence_bps: int, calibrated: bool) -> str:
    return (
        "automatic"
        if calibrated and confidence_bps >= AUTOMATIC_CONFIDENCE_BPS
        else "confirmation_required"
    )


def _decode_classification(decision: sekai_pb2.Decision) -> ReplyClassification:
    return ReplyClassification(
        decision.target_id,
        decision.evidence["reply_id"],
        decision.evidence["category"],
        int(decision.evidence["confidence_bps"]),
        decision.evidence["disposition"],
        decision.evidence["operation_id"],
    )


def _decision_id(kind: str, target: str) -> str:
    return f"hibiki-{kind}-{hashlib.sha256(target.encode()).hexdigest()[:24]}"


def _scoped_action(action: str, publication_external_id: str) -> str:
    digest = hashlib.sha256(publication_external_id.encode()).hexdigest()[:24]
    return f"{action}:{digest}"


def calibration_action(namespace: str) -> str:
    return _scoped_action(CALIBRATION_ACTION, namespace)


def _json_object(content: str, label: str) -> dict[str, object]:
    try:
        payload = json.loads(content)
    except json.JSONDecodeError as error:
        raise OutcomeWorkflowError(f"Chisei {label} response is not valid JSON") from error
    if not isinstance(payload, dict):
        raise OutcomeWorkflowError(f"Chisei {label} response must be a JSON object")
    return payload
