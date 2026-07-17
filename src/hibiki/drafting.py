from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from hibiki.chisei import ChiseiGateway
from hibiki.contracts import chisei_pb2
from hibiki.discovery import EvidenceBundle


class DraftingError(RuntimeError):
    """Raised when a governed draft cannot be trusted."""


@dataclass(frozen=True, slots=True)
class SourceReference:
    revision: str
    path: str


@dataclass(frozen=True, slots=True)
class DraftClaim:
    text: str
    source_references: tuple[SourceReference, ...]


@dataclass(frozen=True, slots=True)
class DraftResult:
    draft: str
    reasoning: str
    claims: tuple[DraftClaim, ...]
    operation_id: str
    request_id: str
    provider: str
    model: str
    receipt_json: str
    receipt_complete: bool
    missing_surfaces: tuple[str, ...]

    @property
    def source_references(self) -> tuple[SourceReference, ...]:
        return tuple(
            dict.fromkeys(
                reference for claim in self.claims for reference in claim.source_references
            )
        )


def generate_draft(
    gateway: ChiseiGateway,
    bundle: EvidenceBundle,
    *,
    namespace: str = "hibiki",
) -> DraftResult:
    if len(bundle.commits) != 1:
        raise DraftingError("drafting requires exactly one selected evidence revision")
    request_id = f"hibiki-draft-{bundle.content_hash[:24]}"
    plan = gateway.plan_execution(
        chisei_pb2.PlanExecutionRequest(
            input=chisei_pb2.ExecutionInput(
                request_id=request_id,
                namespace=namespace,
                spec=_draft_spec(bundle),
                task_type="standalone_post_drafting",
                task_class="public_content_drafting",
                max_tokens=1_500,
                messages=(
                    chisei_pb2.ChatMessage(
                        role="user",
                        content="Draft one grounded standalone post from the selected evidence.",
                    ),
                ),
                system=(
                    "Return only the JSON object required by the supplied specification. "
                    "Do not use tools or make claims outside the evidence bundle."
                ),
            )
        )
    )
    if not plan.plan_id:
        raise DraftingError("Chisei returned a draft plan without an operation ID")
    if not plan.executable or not plan.budget.allowed:
        reason = plan.budget.reason or ", ".join(plan.warnings) or "plan is not executable"
        raise DraftingError(f"Chisei rejected draft plan: {reason}")

    executed = gateway.execute_plan(plan)
    draft, reasoning, claims = _parse_draft(executed.response.content, bundle)
    receipt = gateway.get_operation_receipt(
        chisei_pb2.GetOperationReceiptRequest(operation_id=plan.plan_id)
    )
    _validate_receipt(receipt.receipt_json)
    return DraftResult(
        draft=draft,
        reasoning=reasoning,
        claims=claims,
        operation_id=plan.plan_id,
        request_id=request_id,
        provider=executed.response.provider,
        model=plan.resolved_model,
        receipt_json=receipt.receipt_json,
        receipt_complete=receipt.complete,
        missing_surfaces=tuple(receipt.missing_surfaces),
    )


def _draft_spec(bundle: EvidenceBundle) -> str:
    return json.dumps(
        {
            "task": "Write one standalone X post grounded only in the selected evidence.",
            "voice": [
                "direct first-person builder voice",
                "concrete and slightly opinionated",
                "no marketing filler, hashtags, engagement bait, or invented outcomes",
            ],
            "response_schema": {
                "draft": "non-empty string",
                "reasoning": "non-empty string",
                "claims": [
                    {
                        "text": "non-empty factual claim from the draft",
                        "source_references": [
                            {"revision": "selected revision", "path": "changed file path"}
                        ],
                    }
                ],
            },
            "requirements": [
                "identify every factual claim in the draft",
                "attach at least one evidence reference to every factual claim",
                "use only revisions and changed file paths present in the evidence bundle",
            ],
            "evidence_bundle": bundle.to_dict(),
        },
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _parse_draft(content: str, bundle: EvidenceBundle) -> tuple[str, str, tuple[DraftClaim, ...]]:
    try:
        payload = json.loads(content)
    except json.JSONDecodeError as error:
        raise DraftingError("Chisei draft response is not valid JSON") from error
    if not isinstance(payload, dict) or set(payload) != {"draft", "reasoning", "claims"}:
        raise DraftingError("Chisei draft response has unexpected or missing fields")
    draft = _nonempty_string(payload["draft"], "draft")
    reasoning = _nonempty_string(payload["reasoning"], "draft reasoning")
    raw_claims = payload["claims"]
    if not isinstance(raw_claims, list) or not raw_claims:
        raise DraftingError("Chisei draft claims must be a non-empty list")

    commit = bundle.commits[0]
    revision = commit["revision"]
    evidence_paths = {entry["path"] for key in ("patches", "documents") for entry in commit[key]}
    claims: list[DraftClaim] = []
    for raw_claim in raw_claims:
        if not isinstance(raw_claim, dict) or set(raw_claim) != {"text", "source_references"}:
            raise DraftingError("Chisei draft claim has unexpected or missing fields")
        text = _nonempty_string(raw_claim["text"], "claim text")
        if text not in draft:
            raise DraftingError("draft claim text must appear verbatim in the draft")
        raw_references = raw_claim["source_references"]
        if not isinstance(raw_references, list) or not raw_references:
            raise DraftingError("every draft claim must have a source reference")
        references: list[SourceReference] = []
        for raw_reference in raw_references:
            if not isinstance(raw_reference, dict) or set(raw_reference) != {"revision", "path"}:
                raise DraftingError("draft source reference has unexpected or missing fields")
            reference_revision = _nonempty_string(raw_reference["revision"], "source revision")
            path = _nonempty_string(raw_reference["path"], "source path")
            if reference_revision != revision or path not in evidence_paths:
                raise DraftingError("draft source reference is outside the evidence bundle")
            references.append(SourceReference(reference_revision, path))
        claims.append(DraftClaim(text, tuple(references)))
    return draft, reasoning, tuple(claims)


def _validate_receipt(receipt_json: str) -> None:
    if not receipt_json:
        raise DraftingError("Chisei returned an empty operation receipt")
    try:
        parsed = json.loads(receipt_json)
    except json.JSONDecodeError as error:
        raise DraftingError("Chisei returned an invalid operation receipt") from error
    if not isinstance(parsed, dict):
        raise DraftingError("Chisei operation receipt must be a JSON object")


def _nonempty_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DraftingError(f"{name} must be a non-empty string")
    return value.strip()
