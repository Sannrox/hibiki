from __future__ import annotations

import hashlib
import json
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass

from hibiki.chisei import ChiseiGateway
from hibiki.contracts import chisei_pb2, sekai_pb2
from hibiki.records import (
    CausalRepositories,
    HypothesisRecord,
    OutcomeRecord,
    RecordValidationError,
)
from hibiki.sekai import SekaiGateway


class LearningWorkflowError(RuntimeError):
    """Raised when hypothesis surfacing or strategy recommendation cannot proceed."""


HYPOTHESIS_ACTION = "hibiki.hypothesis_surfacing"
STRATEGY_ACTION = "hibiki.strategy_recommendation"

HYPOTHESIS_MINIMUM_POSTS = 3
STRATEGY_MINIMUM_POSTS = 8
STRATEGY_MINIMUM_PERIODS = 2

PERIOD_BOUNDARY_MS = 7 * 24 * 60 * 60 * 1000  # 7 days


@dataclass(frozen=True, slots=True)
class HypothesisResult:
    hypotheses: tuple[SurfacedHypothesis, ...]
    comparable_posts: int
    operation_id: str


@dataclass(frozen=True, slots=True)
class SurfacedHypothesis:
    stable_id: str
    statement: str
    evidence_external_ids: tuple[str, ...]
    status: str


@dataclass(frozen=True, slots=True)
class StrategyRecommendation:
    hypothesis_external_id: str
    statement: str
    recommendation: str
    confidence_bps: int
    posts_evaluated: int
    periods_covered: int
    actionable: bool


@dataclass(frozen=True, slots=True)
class StrategyResult:
    recommendations: tuple[StrategyRecommendation, ...]
    gated_hypotheses: tuple[GatedHypothesis, ...]
    comparable_posts: int
    periods: int
    operation_id: str


@dataclass(frozen=True, slots=True)
class GatedHypothesis:
    hypothesis_external_id: str
    statement: str
    reason: str
    posts_evaluated: int
    periods_covered: int


@dataclass(frozen=True, slots=True)
class HypothesisStatusResult:
    hypothesis: HypothesisRecord
    previous_status: str
    new_status: str


def surface_hypotheses(
    sekai: SekaiGateway,
    chisei: ChiseiGateway,
    publication_external_id: str,
    namespace: str,
    *,
    clock_ms: Callable[[], int] | None = None,
) -> HypothesisResult:
    """Surface hypotheses from completed outcomes of comparable posts.

    PUBLICATION_ID is a trigger anchor — it gates invocation to publications
    that have a completed 7d outcome and labels the decision target.  In v0 all
    namespace outcomes are considered comparable; per-topic or per-style scoping
    is not implemented.  ADR 004's "three comparable posts" refers to the
    namespace-wide count of final outcomes.
    """
    now = (clock_ms or (lambda: time.time_ns() // 1_000_000))()
    repositories = CausalRepositories.create(sekai, namespace, clock_ms=clock_ms)

    outcomes = _completed_outcomes(sekai, namespace)
    if len(outcomes) < HYPOTHESIS_MINIMUM_POSTS:
        raise LearningWorkflowError(
            f"hypothesis surfacing requires at least {HYPOTHESIS_MINIMUM_POSTS} "
            f"comparable posts with completed outcomes; found {len(outcomes)}"
        )

    # Verify the requested publication has a completed outcome
    publication_outcomes = [
        outcome
        for outcome in outcomes
        if outcome.publication_external_id == publication_external_id
    ]
    if not publication_outcomes:
        raise LearningWorkflowError(
            "requested publication does not have a completed 7d outcome"
        )

    evidence_ids = tuple(outcome.external_id for outcome in outcomes)
    spec = {
        "task": "Surface hypotheses about post resonance from completed outcome evidence.",
        "evidence_external_ids": list(evidence_ids),
        "outcomes": [
            {
                "external_id": outcome.external_id,
                "publication_external_id": outcome.publication_external_id,
                "metrics": dict(outcome.metrics),
                "qualified_replies": outcome.qualified_replies,
                "window": outcome.window,
            }
            for outcome in outcomes
        ],
        "response_schema": {
            "hypotheses": [
                {
                    "stable_id": "short deterministic identifier",
                    "statement": "falsifiable hypothesis about audience resonance",
                    "evidence_external_ids": ["outcome external ids supporting this"],
                }
            ]
        },
    }

    content, operation_id = _execute(chisei, namespace, "hypothesis_surfacing", spec, 2000)
    payload = _json_object(content, "hypothesis surfacing")
    raw = payload.get("hypotheses")
    if not isinstance(raw, list):
        raise LearningWorkflowError("Chisei hypothesis response is not a list")

    # Validate all items before persisting any — surfacing is all-or-nothing
    evidence_set = set(evidence_ids)
    required_keys = {"stable_id", "statement", "evidence_external_ids"}
    validated: list[dict[str, object]] = []
    for item in raw:
        if not isinstance(item, dict) or not required_keys.issubset(item.keys()):
            raise LearningWorkflowError("Chisei hypothesis has unexpected structure")
        if (
            not isinstance(item["stable_id"], str)
            or not item["stable_id"].strip()
            or not isinstance(item["statement"], str)
            or not item["statement"].strip()
        ):
            raise LearningWorkflowError("Chisei hypothesis has invalid field values")
        refs = item["evidence_external_ids"]
        if not isinstance(refs, list) or not refs or any(ref not in evidence_set for ref in refs):
            raise LearningWorkflowError(
                "Chisei hypothesis references invalid or unknown evidence"
            )
        validated.append(item)

    # Persist only after full validation succeeds
    surfaced: list[SurfacedHypothesis] = []
    for item in validated:
        refs = item["evidence_external_ids"]
        # Preserve operator decisions on existing hypotheses
        existing = repositories.hypotheses.get(item["stable_id"])
        if existing is not None and existing.status != "surfaced":
            surfaced.append(
                SurfacedHypothesis(
                    stable_id=existing.stable_id,
                    statement=existing.statement,
                    evidence_external_ids=existing.evidence_external_ids,
                    status=existing.status,
                )
            )
            continue
        record = repositories.hypotheses.put(
            HypothesisRecord(
                namespace=namespace,
                stable_id=item["stable_id"],
                statement=item["statement"],
                evidence_external_ids=tuple(refs),
                status="surfaced",
            )
        )
        surfaced.append(
            SurfacedHypothesis(
                stable_id=record.stable_id,
                statement=record.statement,
                evidence_external_ids=record.evidence_external_ids,
                status=record.status,
            )
        )

    # Record the surfacing decision — include operation_id so distinct runs are auditable
    decision_id = _decision_id("hypothesis-surfacing", f"{publication_external_id}:{operation_id}")
    sekai.record_decision(
        sekai_pb2.Decision(
            id=decision_id,
            timestamp=now,
            actor="hibiki",
            action=HYPOTHESIS_ACTION,
            reason="governed hypothesis surfacing after comparable outcome evidence",
            evidence={
                "publication_external_id": publication_external_id,
                "comparable_posts": str(len(outcomes)),
                "operation_id": operation_id,
            },
            target_id=publication_external_id,
            outcome="surfaced",
        )
    )

    return HypothesisResult(
        hypotheses=tuple(surfaced),
        comparable_posts=len(outcomes),
        operation_id=operation_id,
    )


def evaluate_strategy(
    sekai: SekaiGateway,
    chisei: ChiseiGateway,
    namespace: str,
    *,
    clock_ms: Callable[[], int] | None = None,
) -> StrategyResult:
    """Evaluate hypotheses against strategy gates and return recommendations."""
    now = (clock_ms or (lambda: time.time_ns() // 1_000_000))()
    outcomes = _completed_outcomes(sekai, namespace)
    periods = _count_periods(outcomes)
    all_hypotheses = _load_surfaced_hypotheses(sekai, namespace)

    recommendations: list[StrategyRecommendation] = []
    gated: list[GatedHypothesis] = []
    operation_ids: list[str] = []

    for hypothesis in all_hypotheses:
        posts_for_hypothesis = sum(
            1
            for outcome in outcomes
            if outcome.external_id in hypothesis.evidence_external_ids
        )
        periods_for_hypothesis = _count_periods(
            [
                outcome
                for outcome in outcomes
                if outcome.external_id in hypothesis.evidence_external_ids
            ]
        )

        if posts_for_hypothesis < STRATEGY_MINIMUM_POSTS:
            gated.append(
                GatedHypothesis(
                    hypothesis_external_id=hypothesis.external_id,
                    statement=hypothesis.statement,
                    reason=f"insufficient posts: {posts_for_hypothesis}/{STRATEGY_MINIMUM_POSTS}",
                    posts_evaluated=posts_for_hypothesis,
                    periods_covered=periods_for_hypothesis,
                )
            )
            continue

        if periods_for_hypothesis < STRATEGY_MINIMUM_PERIODS:
            gated.append(
                GatedHypothesis(
                    hypothesis_external_id=hypothesis.external_id,
                    statement=hypothesis.statement,
                    reason=(
                        f"insufficient periods: {periods_for_hypothesis}/{STRATEGY_MINIMUM_PERIODS}"
                    ),
                    posts_evaluated=posts_for_hypothesis,
                    periods_covered=periods_for_hypothesis,
                )
            )
            continue

        # Hypothesis passes gates — ask Chisei for a strategy recommendation
        spec = {
            "task": "Recommend a strategy adjustment based on the supported hypothesis.",
            "hypothesis": {
                "external_id": hypothesis.external_id,
                "statement": hypothesis.statement,
                "evidence_external_ids": list(hypothesis.evidence_external_ids),
            },
            "outcomes": [
                {
                    "external_id": outcome.external_id,
                    "metrics": dict(outcome.metrics),
                    "qualified_replies": outcome.qualified_replies,
                }
                for outcome in outcomes
                if outcome.external_id in hypothesis.evidence_external_ids
            ],
            "response_schema": {
                "recommendation": "concise strategy adjustment",
                "confidence_bps": "integer 0..10000",
            },
        }
        content, operation_id = _execute(
            chisei, namespace, "strategy_recommendation", spec, 1000
        )
        operation_ids.append(operation_id)
        payload = _json_object(content, "strategy recommendation")
        rec_text = payload.get("recommendation")
        conf = payload.get("confidence_bps")
        if (
            not isinstance(rec_text, str)
            or not rec_text.strip()
            or not isinstance(conf, int)
            or not 0 <= conf <= 10_000
        ):
            raise LearningWorkflowError("Chisei strategy recommendation has invalid values")

        recommendations.append(
            StrategyRecommendation(
                hypothesis_external_id=hypothesis.external_id,
                statement=hypothesis.statement,
                recommendation=rec_text,
                confidence_bps=conf,
                posts_evaluated=posts_for_hypothesis,
                periods_covered=periods_for_hypothesis,
                actionable=True,
            )
        )

    # Record the strategy evaluation decision for auditability
    evidence_digest = hashlib.sha256(
        ",".join(o.external_id for o in outcomes).encode()
    ).hexdigest()[:16]
    combined_operation_id = ",".join(operation_ids) if operation_ids else ""
    # Include operation_ids so distinct runs are independently auditable
    decision_key = f"{namespace}:{evidence_digest}:{combined_operation_id or str(now)}"
    sekai.record_decision(
        sekai_pb2.Decision(
            id=_decision_id("strategy-evaluation", decision_key),
            timestamp=now,
            actor="hibiki",
            action=STRATEGY_ACTION,
            reason="governed strategy evaluation against hypothesis gates",
            evidence={
                "comparable_posts": str(len(outcomes)),
                "periods": str(periods),
                "hypotheses_evaluated": str(len(all_hypotheses)),
                "recommendations_produced": str(len(recommendations)),
                "operation_ids": combined_operation_id,
            },
            target_id=namespace,
            outcome="evaluated",
        )
    )

    return StrategyResult(
        recommendations=tuple(recommendations),
        gated_hypotheses=tuple(gated),
        comparable_posts=len(outcomes),
        periods=periods,
        operation_id=combined_operation_id,
    )


def update_hypothesis_status(
    sekai: SekaiGateway,
    hypothesis_external_id: str,
    new_status: str,
    namespace: str,
    *,
    clock_ms: Callable[[], int] | None = None,
) -> HypothesisStatusResult:
    """Accept, reject, or retire a hypothesis without silently changing strategy."""
    if new_status not in {"accepted", "rejected", "retired"}:
        raise LearningWorkflowError(
            f"status must be accepted, rejected, or retired; got {new_status!r}"
        )
    now = (clock_ms or (lambda: time.time_ns() // 1_000_000))()
    repositories = CausalRepositories.create(sekai, namespace, clock_ms=clock_ms)
    hypothesis = repositories.hypotheses.get_external(hypothesis_external_id)
    if hypothesis is None:
        raise LearningWorkflowError("hypothesis was not found")
    if hypothesis.status not in {"surfaced", "accepted"}:
        raise LearningWorkflowError(
            f"hypothesis in status {hypothesis.status!r} cannot transition to {new_status!r}"
        )
    previous_status = hypothesis.status
    updated = HypothesisRecord(
        namespace=hypothesis.namespace,
        stable_id=hypothesis.stable_id,
        statement=hypothesis.statement,
        evidence_external_ids=hypothesis.evidence_external_ids,
        status=new_status,
    )
    result = repositories.hypotheses.put(updated)

    # Record the status decision
    sekai.record_decision(
        sekai_pb2.Decision(
            id=_decision_id(f"hypothesis-{new_status}", hypothesis_external_id),
            timestamp=now,
            actor="operator",
            action=f"hibiki.hypothesis_{new_status}",
            reason=f"operator {new_status} hypothesis",
            evidence={
                "hypothesis_external_id": hypothesis_external_id,
                "previous_status": previous_status,
            },
            target_id=hypothesis_external_id,
            outcome=new_status,
        )
    )

    return HypothesisStatusResult(
        hypothesis=result,
        previous_status=previous_status,
        new_status=new_status,
    )


def _completed_outcomes(sekai: SekaiGateway, namespace: str) -> list[OutcomeRecord]:
    """Load all 7d final outcomes in the namespace."""
    objects = sekai.list_objects_by_kind(kind="hibiki.outcome", namespace=namespace, limit=1000)
    if len(objects) >= 1000:
        print(
            "hibiki: warning: outcome count reached query limit; results may be truncated",
            file=sys.stderr,
        )
    results: list[OutcomeRecord] = []
    for obj in objects:
        try:
            record = OutcomeRecord.from_properties(obj.namespace, obj.name, obj.properties)
            stored_hash = obj.properties.get("content_hash", "")
            if stored_hash and stored_hash != record.content_hash:
                raise RecordValidationError(
                    "stored outcome content_hash does not match its properties"
                )
            if record.window == "7d":
                results.append(record)
        except RecordValidationError as error:
            print(
                f"hibiki: skipping invalid outcome {obj.external_id}: {error}",
                file=sys.stderr,
            )
            continue
    return results


def _load_surfaced_hypotheses(sekai: SekaiGateway, namespace: str) -> list[HypothesisRecord]:
    """Load all hypothesis records in 'surfaced' status."""
    objects = sekai.list_objects_by_kind(
        kind="hibiki.hypothesis", namespace=namespace, limit=1000
    )
    if len(objects) >= 1000:
        print(
            "hibiki: warning: hypothesis count reached query limit; results may be truncated",
            file=sys.stderr,
        )
    results: list[HypothesisRecord] = []
    for obj in objects:
        try:
            record = HypothesisRecord.from_properties(
                obj.namespace, obj.name, obj.properties
            )
            stored_hash = obj.properties.get("content_hash", "")
            if stored_hash and stored_hash != record.content_hash:
                raise RecordValidationError(
                    "stored hypothesis content_hash does not match its properties"
                )
            if record.status == "surfaced":
                results.append(record)
        except RecordValidationError as error:
            print(
                f"hibiki: skipping invalid hypothesis {obj.external_id}: {error}",
                file=sys.stderr,
            )
            continue
    return results


def _count_periods(outcomes: list[OutcomeRecord]) -> int:
    """Count distinct 7-day periods covered by the outcomes."""
    if not outcomes:
        return 0
    timestamps = sorted(outcome.observed_at for outcome in outcomes)
    periods = 1
    period_start = timestamps[0]
    for timestamp in timestamps[1:]:
        if timestamp - period_start >= PERIOD_BOUNDARY_MS:
            periods += 1
            period_start = timestamp
    return periods


def _execute(
    chisei: ChiseiGateway,
    namespace: str,
    task_type: str,
    spec: dict[str, object],
    max_tokens: int,
) -> tuple[str, str]:
    digest = hashlib.sha256(json.dumps(spec, sort_keys=True).encode()).hexdigest()[:24]
    plan = chisei.plan_execution(
        chisei_pb2.PlanExecutionRequest(
            input=chisei_pb2.ExecutionInput(
                request_id=f"hibiki-{task_type}-{digest}",
                namespace=namespace,
                spec=json.dumps(spec, separators=(",", ":"), sort_keys=True),
                task_type=task_type,
                task_class="governed_learning",
                max_tokens=max_tokens,
                messages=(
                    chisei_pb2.ChatMessage(
                        role="user",
                        content="Evaluate only the referenced governed outcome evidence.",
                    ),
                ),
                system=(
                    "Return only the required JSON. Do not infer facts beyond the "
                    "provided outcome evidence."
                ),
            )
        )
    )
    if not plan.plan_id or not plan.executable or not plan.budget.allowed:
        raise LearningWorkflowError("Chisei rejected governed learning execution")
    executed = chisei.execute_plan(plan)
    receipt = chisei.get_operation_receipt(
        chisei_pb2.GetOperationReceiptRequest(operation_id=plan.plan_id)
    )
    if not receipt.receipt_json:
        raise LearningWorkflowError("Chisei returned no operation receipt")
    _json_object(receipt.receipt_json, "operation receipt")
    if not receipt.complete or receipt.missing_surfaces:
        raise LearningWorkflowError("Chisei operation receipt is incomplete")
    return executed.response.content, plan.plan_id


def _json_object(content: str, label: str) -> dict[str, object]:
    try:
        payload = json.loads(content)
    except json.JSONDecodeError as error:
        raise LearningWorkflowError(f"Chisei {label} response is not valid JSON") from error
    if not isinstance(payload, dict):
        raise LearningWorkflowError(f"Chisei {label} response must be a JSON object")
    return payload


def _decision_id(kind: str, target: str) -> str:
    return f"hibiki-{kind}-{hashlib.sha256(target.encode()).hexdigest()[:24]}"
