from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from hibiki.chisei import ChiseiGateway
from hibiki.contracts import chisei_pb2
from hibiki.discovery import EvidenceBundle
from hibiki.drafting import SourceReference


class ClaimValidationError(RuntimeError):
    """Raised when claim validation cannot produce a trustworthy verdict."""


@dataclass(frozen=True, slots=True)
class ValidatedClaim:
    text: str
    supported: bool
    reason: str
    source_references: tuple[SourceReference, ...]


@dataclass(frozen=True, slots=True)
class ValidationResult:
    valid: bool
    reasoning: str
    claims: tuple[ValidatedClaim, ...]
    operation_id: str
    request_id: str
    provider: str
    model: str
    receipt_json: str
    receipt_complete: bool
    missing_surfaces: tuple[str, ...]


def validate_claims(
    gateway: ChiseiGateway,
    text: str,
    bundle: EvidenceBundle,
    *,
    namespace: str = "hibiki",
) -> ValidationResult:
    if not text.strip():
        raise ClaimValidationError("final text must be a non-empty string")
    if len(bundle.commits) != 1:
        raise ClaimValidationError("claim validation requires exactly one evidence revision")
    text_hash = hashlib.sha256(text.encode()).hexdigest()
    request_id = f"hibiki-validation-{text_hash[:24]}-{bundle.content_hash[:12]}"
    plan = gateway.plan_execution(
        chisei_pb2.PlanExecutionRequest(
            input=chisei_pb2.ExecutionInput(
                request_id=request_id,
                namespace=namespace,
                spec=_validation_spec(text, bundle),
                task_type="factual_claim_validation",
                task_class="public_content_validation",
                max_tokens=1_500,
                messages=(
                    chisei_pb2.ChatMessage(
                        role="user",
                        content=(
                            "Validate every factual claim in the final text against the evidence."
                        ),
                    ),
                ),
                system=(
                    "Return only the JSON object required by the supplied specification. "
                    "Fail closed on any unsupported claim and do not use tools."
                ),
            )
        )
    )
    if not plan.plan_id:
        raise ClaimValidationError("Chisei returned a validation plan without an operation ID")
    if not plan.executable or not plan.budget.allowed:
        reason = plan.budget.reason or ", ".join(plan.warnings) or "plan is not executable"
        raise ClaimValidationError(f"Chisei rejected validation plan: {reason}")

    executed = gateway.execute_plan(plan)
    valid, reasoning, claims = _parse_validation(executed.response.content, text, bundle)
    receipt = gateway.get_operation_receipt(
        chisei_pb2.GetOperationReceiptRequest(operation_id=plan.plan_id)
    )
    _validate_receipt(receipt.receipt_json)
    return ValidationResult(
        valid=valid,
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


def _validation_spec(text: str, bundle: EvidenceBundle) -> str:
    return json.dumps(
        {
            "task": "Inventory and validate every factual claim in the final text.",
            "final_text": text,
            "response_schema": {
                "valid": "boolean; true only when every claim is supported",
                "reasoning": "non-empty string",
                "claims": [
                    {
                        "text": "exact non-empty substring of final_text",
                        "supported": "boolean",
                        "reason": "non-empty string",
                        "source_references": [
                            {"revision": "selected revision", "path": "evidenced file path"}
                        ],
                    }
                ],
            },
            "requirements": [
                "include every factual claim from final_text exactly once",
                "mark valid=false when any claim is unsupported",
                "supported claims require at least one in-bundle evidence reference",
                "unsupported claims must have no source references",
            ],
            "evidence_bundle": bundle.to_dict(),
        },
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _parse_validation(
    content: str, text: str, bundle: EvidenceBundle
) -> tuple[bool, str, tuple[ValidatedClaim, ...]]:
    try:
        payload = json.loads(content)
    except json.JSONDecodeError as error:
        raise ClaimValidationError("Chisei validation response is not valid JSON") from error
    if not isinstance(payload, dict) or set(payload) != {"valid", "reasoning", "claims"}:
        raise ClaimValidationError("Chisei validation response has unexpected or missing fields")
    if type(payload["valid"]) is not bool:
        raise ClaimValidationError("validation verdict must be a boolean")
    reasoning = _nonempty_string(payload["reasoning"], "validation reasoning")
    raw_claims = payload["claims"]
    if not isinstance(raw_claims, list) or not raw_claims:
        raise ClaimValidationError("validation claims must be a non-empty list")

    commit = bundle.commits[0]
    revision = commit["revision"]
    evidence_paths = {entry["path"] for key in ("patches", "documents") for entry in commit[key]}
    claims: list[ValidatedClaim] = []
    seen_claims: set[str] = set()
    for raw_claim in raw_claims:
        if not isinstance(raw_claim, dict) or set(raw_claim) != {
            "text",
            "supported",
            "reason",
            "source_references",
        }:
            raise ClaimValidationError("validated claim has unexpected or missing fields")
        claim_text = _nonempty_string(raw_claim["text"], "validated claim text")
        if claim_text not in text:
            raise ClaimValidationError("validated claim text must appear verbatim in final text")
        if claim_text in seen_claims:
            raise ClaimValidationError("validation response contains a duplicate claim")
        seen_claims.add(claim_text)
        if type(raw_claim["supported"]) is not bool:
            raise ClaimValidationError("claim support verdict must be a boolean")
        reason = _nonempty_string(raw_claim["reason"], "claim validation reason")
        raw_references = raw_claim["source_references"]
        if not isinstance(raw_references, list):
            raise ClaimValidationError("claim source references must be a list")
        references: list[SourceReference] = []
        for raw_reference in raw_references:
            if not isinstance(raw_reference, dict) or set(raw_reference) != {"revision", "path"}:
                raise ClaimValidationError(
                    "validation source reference has unexpected or missing fields"
                )
            reference_revision = _nonempty_string(raw_reference["revision"], "source revision")
            path = _nonempty_string(raw_reference["path"], "source path")
            if reference_revision != revision or path not in evidence_paths:
                raise ClaimValidationError(
                    "validation source reference is outside the evidence bundle"
                )
            references.append(SourceReference(reference_revision, path))
        supported = raw_claim["supported"]
        if supported != bool(references):
            raise ClaimValidationError(
                "supported claims require references and unsupported claims forbid them"
            )
        claims.append(ValidatedClaim(claim_text, supported, reason, tuple(references)))

    valid = payload["valid"]
    if valid != all(claim.supported for claim in claims):
        raise ClaimValidationError("validation verdict does not match claim support results")
    return valid, reasoning, tuple(claims)


def _validate_receipt(receipt_json: str) -> None:
    if not receipt_json:
        raise ClaimValidationError("Chisei returned an empty operation receipt")
    try:
        parsed = json.loads(receipt_json)
    except json.JSONDecodeError as error:
        raise ClaimValidationError("Chisei returned an invalid operation receipt") from error
    if not isinstance(parsed, dict):
        raise ClaimValidationError("Chisei operation receipt must be a JSON object")


def _nonempty_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ClaimValidationError(f"{name} must be a non-empty string")
    return value.strip()
