from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any

from hibiki.chisei import ChiseiGateway
from hibiki.contracts import chisei_pb2
from hibiki.discovery import EvidenceBundle


class SelectionError(RuntimeError):
    """Raised when governed candidate selection cannot be trusted."""


@dataclass(frozen=True, slots=True)
class Candidate:
    revision: str
    topic: str
    reason: str
    scores: dict[str, int]


@dataclass(frozen=True, slots=True)
class SelectionResult:
    candidate: Candidate | None
    reason: str
    operation_id: str
    request_id: str
    provider: str
    model: str
    receipt_json: str
    receipt_complete: bool
    missing_surfaces: tuple[str, ...]


_SCORE_NAMES = frozenset({"usefulness", "novelty", "evidence_strength", "audience_relevance"})


def select_candidate(
    gateway: ChiseiGateway,
    bundle: EvidenceBundle,
    recent_topics: tuple[str, ...],
    *,
    namespace: str = "hibiki",
) -> SelectionResult:
    request_id = f"hibiki-selection-{bundle.content_hash[:24]}"
    spec = _selection_spec(bundle, recent_topics)
    plan = gateway.plan_execution(
        chisei_pb2.PlanExecutionRequest(
            input=chisei_pb2.ExecutionInput(
                request_id=request_id,
                namespace=namespace,
                spec=spec,
                task_type="source_selection",
                task_class="public_content_recommendation",
                max_tokens=1_000,
                messages=(
                    chisei_pb2.ChatMessage(
                        role="user",
                        content="Select one eligible public commit, or return no candidate.",
                    ),
                ),
                system=(
                    "Return only the JSON object required by the supplied specification. "
                    "Do not use tools or infer facts outside the evidence bundle."
                ),
            )
        )
    )
    if not plan.plan_id:
        raise SelectionError("Chisei returned a plan without an operation ID")
    if not plan.executable or not plan.budget.allowed:
        reason = plan.budget.reason or ", ".join(plan.warnings) or "plan is not executable"
        raise SelectionError(f"Chisei rejected selection plan: {reason}")

    executed = gateway.execute_plan(plan)
    candidate, reason = _parse_response(executed.response.content, bundle, recent_topics)
    receipt = gateway.get_operation_receipt(
        chisei_pb2.GetOperationReceiptRequest(
            operation_id=plan.plan_id,
        )
    )
    if not receipt.receipt_json:
        raise SelectionError("Chisei returned an empty operation receipt")
    try:
        parsed_receipt = json.loads(receipt.receipt_json)
    except json.JSONDecodeError as error:
        raise SelectionError("Chisei returned an invalid operation receipt") from error
    if not isinstance(parsed_receipt, dict):
        raise SelectionError("Chisei operation receipt must be a JSON object")

    return SelectionResult(
        candidate=candidate,
        reason=reason,
        operation_id=plan.plan_id,
        request_id=request_id,
        provider=executed.response.provider,
        model=plan.resolved_model,
        receipt_json=receipt.receipt_json,
        receipt_complete=receipt.complete,
        missing_surfaces=tuple(receipt.missing_surfaces),
    )


def _selection_spec(bundle: EvidenceBundle, recent_topics: tuple[str, ...]) -> str:
    return json.dumps(
        {
            "task": "Select at most one Tenkai commit for a grounded standalone post.",
            "eligibility": [
                "meaningful behavior or design change",
                "supporting tests, documentation, checks, or other concrete evidence",
                "explainable without private context",
                "useful takeaway beyond announcing a feature",
                "topic does not repeat a recent subject",
            ],
            "ranking": [
                "usefulness",
                "novelty",
                "evidence_strength",
                "audience_relevance",
            ],
            "recent_topics": list(recent_topics),
            "response_schema": {
                "candidate": {
                    "revision": "string",
                    "topic": "string",
                    "reason": "string",
                    "scores": {name: "integer 0..100" for name in sorted(_SCORE_NAMES)},
                },
                "reason": "required string when candidate is null",
            },
            "no_candidate": "Return candidate=null when no commit passes every eligibility rule.",
            "evidence_bundle": bundle.to_dict(),
        },
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _parse_response(
    content: str, bundle: EvidenceBundle, recent_topics: tuple[str, ...]
) -> tuple[Candidate | None, str]:
    try:
        payload = json.loads(content)
    except json.JSONDecodeError as error:
        raise SelectionError("Chisei selection response is not valid JSON") from error
    if not isinstance(payload, dict) or set(payload) - {"candidate", "reason"}:
        raise SelectionError("Chisei selection response has unexpected fields")
    if "candidate" not in payload:
        raise SelectionError("Chisei selection response is missing candidate")
    raw_candidate = payload.get("candidate")
    if raw_candidate is None:
        reason = _nonempty_string(payload.get("reason"), "no-candidate reason")
        return None, reason
    if not isinstance(raw_candidate, dict) or set(raw_candidate) != {
        "revision",
        "topic",
        "reason",
        "scores",
    }:
        raise SelectionError("Chisei candidate has unexpected or missing fields")
    revision = _nonempty_string(raw_candidate["revision"], "candidate revision")
    if revision not in {commit["revision"] for commit in bundle.commits}:
        raise SelectionError("Chisei selected a revision outside the evidence bundle")
    topic = _nonempty_string(raw_candidate["topic"], "candidate topic")
    reason = _nonempty_string(raw_candidate["reason"], "candidate reason")
    scores = raw_candidate["scores"]
    if not isinstance(scores, dict) or set(scores) != _SCORE_NAMES:
        raise SelectionError("Chisei candidate scores are incomplete")
    if any(type(value) is not int or not 0 <= value <= 100 for value in scores.values()):
        raise SelectionError("Chisei candidate scores must be integers from 0 to 100")
    normalized_topic = _normalize_topic(topic)
    if normalized_topic in {_normalize_topic(value) for value in recent_topics}:
        return None, f"repeat topic rejected: {topic}"
    return Candidate(revision, topic, reason, dict(scores)), reason


def commit_evidence_hash(bundle: EvidenceBundle, revision: str) -> str:
    commit = next((entry for entry in bundle.commits if entry["revision"] == revision), None)
    if commit is None:
        raise SelectionError("selected revision is absent from the evidence bundle")
    immutable_evidence = {key: value for key, value in commit.items() if key != "checks"}
    encoded = json.dumps(
        immutable_evidence, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def legacy_commit_evidence_hash(bundle: EvidenceBundle, revision: str) -> str:
    """Return the pre-immutable-identity hash for migration checks."""
    commit = next((entry for entry in bundle.commits if entry["revision"] == revision), None)
    if commit is None:
        raise SelectionError("selected revision is absent from the evidence bundle")
    encoded = json.dumps(commit, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode()
    return hashlib.sha256(encoded).hexdigest()


def _normalize_topic(topic: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", topic.lower()))


def _nonempty_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SelectionError(f"{name} must be a non-empty string")
    return value.strip()
