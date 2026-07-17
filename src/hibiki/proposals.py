from __future__ import annotations

import json
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, replace

from hibiki.boundaries import ProcessRunner
from hibiki.chisei import ChiseiGateway
from hibiki.contracts import sekai_pb2
from hibiki.discovery import DiscoveryLimits, EvidenceBundle, discover_public_revision
from hibiki.drafting import DraftClaim, DraftResult, SourceReference, generate_draft
from hibiki.records import CausalRepositories, ProposalRecord, SourceRecord, sha256_text
from hibiki.sekai import SekaiGateway
from hibiki.selection import commit_evidence_hash, legacy_commit_evidence_hash
from hibiki.validation import ValidationResult, validate_claims

PROPOSAL_DECISION_NAMESPACE = uuid.UUID("36937fca-08bd-4f67-a62d-56eecdb0d9f5")


class ProposalWorkflowError(RuntimeError):
    """Raised when a proposal workflow cannot preserve its causal guarantees."""


@dataclass(frozen=True, slots=True)
class DraftedProposal:
    proposal: ProposalRecord
    reasoning: str
    claims: tuple[DraftClaim, ...]
    source_references: tuple[SourceReference, ...]
    operation_id: str
    receipt_complete: bool
    missing_surfaces: tuple[str, ...]


def draft_source(
    process_runner: ProcessRunner,
    sekai: SekaiGateway,
    chisei: ChiseiGateway,
    source_external_id: str,
    namespace: str,
    *,
    limits: DiscoveryLimits | None = None,
    clock_ms: Callable[[], int] | None = None,
) -> DraftedProposal:
    now_ms = (clock_ms or (lambda: time.time_ns() // 1_000_000))()
    repositories = CausalRepositories.create(sekai, namespace, clock_ms=lambda: now_ms)
    source = repositories.sources.get_external(source_external_id)
    if source is None:
        raise ProposalWorkflowError(f"source not found: {source_external_id}")
    bundle = discover_public_revision(
        process_runner,
        source.repository,
        source.revision,
        limits=limits,
    )
    evidence_hash = commit_evidence_hash(bundle, source.revision)
    if evidence_hash != source.evidence_hash:
        source = _migrate_legacy_source_hash(sekai, repositories, source, bundle, evidence_hash)

    drafted = generate_draft(chisei, bundle, namespace=namespace)
    validation = validate_claims(
        chisei,
        drafted.draft,
        bundle,
        expected_claims=tuple(claim.text for claim in drafted.claims),
        namespace=namespace,
    )
    if not validation.valid:
        raise ProposalWorkflowError("generated draft contains an unsupported factual claim")
    decision_id = str(
        uuid.uuid5(
            PROPOSAL_DECISION_NAMESPACE,
            f"{namespace}:draft:{source.external_id}:{drafted.request_id}",
        )
    )
    proposal = repositories.proposals.put(
        ProposalRecord(
            namespace=namespace,
            stable_id=source.stable_id,
            source_external_id=source.external_id,
            evidence_hash=evidence_hash,
            draft=drafted.draft,
            decision_ref=decision_id,
            operation_id=drafted.operation_id,
        )
    )
    sekai.record_decision(
        sekai_pb2.Decision(
            id=decision_id,
            timestamp=now_ms,
            actor="hibiki",
            action="hibiki.proposal_draft",
            reason=drafted.reasoning,
            evidence=_draft_evidence(drafted, evidence_hash),
            target_id=proposal.external_id,
            outcome="drafted",
        )
    )
    sekai.record_decision(
        sekai_pb2.Decision(
            id=_validation_decision_id(namespace, source.external_id, validation.request_id),
            timestamp=now_ms,
            actor="hibiki",
            action="hibiki.claim_validation",
            reason=validation.reasoning,
            evidence=_validation_evidence(validation, proposal.draft_hash),
            target_id=proposal.external_id,
            outcome="supported",
        )
    )
    return DraftedProposal(
        proposal=proposal,
        reasoning=drafted.reasoning,
        claims=drafted.claims,
        source_references=drafted.source_references,
        operation_id=drafted.operation_id,
        receipt_complete=drafted.receipt_complete,
        missing_surfaces=drafted.missing_surfaces,
    )


def _draft_evidence(drafted: DraftResult, evidence_hash: str) -> dict[str, str]:
    claims = [
        {
            "text": claim.text,
            "source_references": [
                {"revision": reference.revision, "path": reference.path}
                for reference in claim.source_references
            ],
        }
        for claim in drafted.claims
    ]
    return {
        "evidence_hash": evidence_hash,
        "draft_hash": sha256_text(drafted.draft),
        "claims": json.dumps(claims, ensure_ascii=False, separators=(",", ":"), sort_keys=True),
        "operation_id": drafted.operation_id,
        "provider": drafted.provider,
        "model": drafted.model,
        "receipt_json": drafted.receipt_json,
        "receipt_complete": str(drafted.receipt_complete).lower(),
        "missing_surfaces": json.dumps(list(drafted.missing_surfaces), separators=(",", ":")),
    }


def _migrate_legacy_source_hash(
    sekai: SekaiGateway,
    repositories: CausalRepositories,
    source: SourceRecord,
    bundle: EvidenceBundle,
    evidence_hash: str,
) -> SourceRecord:
    legacy_hash = legacy_commit_evidence_hash(bundle, source.revision)
    selections = sekai.list_decisions(actor="hibiki", action="hibiki.source_selection", limit=100)
    traceable = any(
        decision.target_id == source.external_id
        and decision.outcome == "selected"
        and decision.evidence.get("repository") == source.repository
        and decision.evidence.get("revision") == source.revision
        and decision.evidence.get("source_evidence_hash") == source.evidence_hash
        for decision in selections
    )
    if source.evidence_hash != legacy_hash and not traceable:
        raise ProposalWorkflowError("reloaded source evidence does not match the selected source")
    return repositories.sources.put(replace(source, evidence_hash=evidence_hash))


def _validation_decision_id(namespace: str, target_id: str, request_id: str) -> str:
    return str(
        uuid.uuid5(
            PROPOSAL_DECISION_NAMESPACE,
            f"{namespace}:validation:{target_id}:{request_id}",
        )
    )


def _validation_evidence(validation: ValidationResult, text_hash: str) -> dict[str, str]:
    claims = [
        {
            "text": claim.text,
            "supported": claim.supported,
            "reason": claim.reason,
            "source_references": [
                {"revision": reference.revision, "path": reference.path}
                for reference in claim.source_references
            ],
        }
        for claim in validation.claims
    ]
    return {
        "final_text_hash": text_hash,
        "claims": json.dumps(claims, ensure_ascii=False, separators=(",", ":"), sort_keys=True),
        "undeclared_claims": json.dumps(
            list(validation.undeclared_claims), ensure_ascii=False, separators=(",", ":")
        ),
        "operation_id": validation.operation_id,
        "provider": validation.provider,
        "model": validation.model,
        "receipt_json": validation.receipt_json,
        "receipt_complete": str(validation.receipt_complete).lower(),
        "missing_surfaces": json.dumps(list(validation.missing_surfaces), separators=(",", ":")),
    }
