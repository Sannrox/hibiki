from __future__ import annotations

import json
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass

from hibiki.boundaries import ProcessRunner
from hibiki.chisei import ChiseiGateway
from hibiki.contracts import sekai_pb2
from hibiki.discovery import DiscoveryLimits, discover_public_revision
from hibiki.drafting import DraftClaim, DraftResult, SourceReference, generate_draft
from hibiki.records import CausalRepositories, ProposalRecord, sha256_text
from hibiki.sekai import SekaiGateway
from hibiki.selection import commit_evidence_hash

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
        raise ProposalWorkflowError("reloaded source evidence does not match the selected source")

    drafted = generate_draft(chisei, bundle, namespace=namespace)
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
