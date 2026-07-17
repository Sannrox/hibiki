from __future__ import annotations

import errno
import json
import os
import tempfile
import time
import uuid
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, replace

if os.name == "nt":
    import msvcrt
else:
    import fcntl

from hibiki.boundaries import ProcessRunner
from hibiki.chisei import ChiseiGateway
from hibiki.contracts import sekai_pb2
from hibiki.discovery import DiscoveryLimits, EvidenceBundle, discover_public_revision
from hibiki.drafting import DraftClaim, DraftResult, SourceReference, generate_draft
from hibiki.records import CausalRepositories, ProposalRecord, SourceRecord, sha256_text
from hibiki.sekai import SekaiGateway
from hibiki.selection import commit_evidence_hash, legacy_commit_evidence_hash
from hibiki.validation import (
    ClaimInventoryResult,
    ValidationResult,
    inventory_claims,
    validate_claims,
)

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


@dataclass(frozen=True, slots=True)
class EditedProposalValidation:
    proposal: ProposalRecord
    validation: ValidationResult
    validation_decision_id: str
    persisted: bool


@dataclass(frozen=True, slots=True)
class ProposalApproval:
    proposal: ProposalRecord
    approval_id: str
    validation_decision_id: str


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
    proposal_external_id = _proposal_external_id_for_source(source_external_id, namespace)
    with _proposal_lock(proposal_external_id):
        return _draft_source_locked(
            process_runner,
            sekai,
            chisei,
            source_external_id,
            namespace,
            limits=limits,
            clock_ms=clock_ms,
        )


def _draft_source_locked(
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
    existing_proposal = repositories.proposals.get(source.stable_id)
    if existing_proposal is not None and existing_proposal.status in {"published", "rejected"}:
        raise ProposalWorkflowError(
            f"proposal in {existing_proposal.status} state cannot be drafted again"
        )
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
    proposal = ProposalRecord(
        namespace=namespace,
        stable_id=source.stable_id,
        source_external_id=source.external_id,
        evidence_hash=evidence_hash,
        draft=drafted.draft,
        decision_ref="pending-validation",
        operation_id=validation.operation_id,
    )
    validation_decision_id = _validation_decision_id(
        namespace, proposal.external_id, proposal.draft_hash
    )
    proposal = replace(proposal, decision_ref=validation_decision_id)
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
            id=validation_decision_id,
            timestamp=now_ms,
            actor="hibiki",
            action="hibiki.claim_validation",
            reason=validation.reasoning,
            evidence=_validation_evidence(validation, proposal.draft_hash),
            target_id=proposal.external_id,
            outcome="supported",
        )
    )
    proposal = repositories.proposals.put(proposal)
    return DraftedProposal(
        proposal=proposal,
        reasoning=drafted.reasoning,
        claims=drafted.claims,
        source_references=drafted.source_references,
        operation_id=drafted.operation_id,
        receipt_complete=drafted.receipt_complete,
        missing_surfaces=drafted.missing_surfaces,
    )


def validate_proposal_edit(
    process_runner: ProcessRunner,
    sekai: SekaiGateway,
    chisei: ChiseiGateway,
    proposal_external_id: str,
    final_text: str,
    namespace: str,
    *,
    limits: DiscoveryLimits | None = None,
    clock_ms: Callable[[], int] | None = None,
) -> EditedProposalValidation:
    with _proposal_lock(proposal_external_id):
        return _validate_proposal_edit_locked(
            process_runner,
            sekai,
            chisei,
            proposal_external_id,
            final_text,
            namespace,
            limits=limits,
            clock_ms=clock_ms,
        )


def _validate_proposal_edit_locked(
    process_runner: ProcessRunner,
    sekai: SekaiGateway,
    chisei: ChiseiGateway,
    proposal_external_id: str,
    final_text: str,
    namespace: str,
    *,
    limits: DiscoveryLimits | None = None,
    clock_ms: Callable[[], int] | None = None,
) -> EditedProposalValidation:
    now_ms = (clock_ms or (lambda: time.time_ns() // 1_000_000))()
    repositories = CausalRepositories.create(sekai, namespace, clock_ms=lambda: now_ms)
    proposal = repositories.proposals.get_external(proposal_external_id)
    if proposal is None:
        raise ProposalWorkflowError(f"proposal not found: {proposal_external_id}")
    if not final_text.strip():
        raise ProposalWorkflowError("final text must be a non-empty string")
    if proposal.status not in {"drafted", "approved", "invalidated"}:
        raise ProposalWorkflowError(
            f"proposal in {proposal.status} state cannot accept edited text"
        )

    edited = final_text != proposal.draft
    source = repositories.sources.get_external(proposal.source_external_id)
    if source is None:
        raise ProposalWorkflowError(f"source not found: {proposal.source_external_id}")
    bundle = discover_public_revision(
        process_runner, source.repository, source.revision, limits=limits
    )
    evidence_hash = commit_evidence_hash(bundle, source.revision)
    if evidence_hash != source.evidence_hash:
        source = _migrate_legacy_source_hash(sekai, repositories, source, bundle, evidence_hash)
    if proposal.evidence_hash != source.evidence_hash:
        proposal = repositories.proposals.put(replace(proposal, evidence_hash=source.evidence_hash))

    inventory = inventory_claims(chisei, final_text, bundle, namespace=namespace)
    validation = validate_claims(
        chisei,
        final_text,
        bundle,
        expected_claims=inventory.claims,
        namespace=namespace,
    )
    final_text_hash = sha256_text(final_text)
    decision_id = _validation_decision_id(namespace, proposal.external_id, final_text_hash)
    outcome = "supported" if validation.valid else "unsupported"
    evidence = _validation_evidence(validation, final_text_hash)
    evidence.update(_inventory_evidence(inventory))
    sekai.record_decision(
        sekai_pb2.Decision(
            id=decision_id,
            timestamp=now_ms,
            actor="hibiki",
            action="hibiki.claim_validation",
            reason=validation.reasoning,
            evidence=evidence,
            target_id=proposal.external_id,
            outcome=outcome,
        )
    )
    if not validation.valid:
        if proposal.status != "invalidated":
            proposal = repositories.proposals.put(proposal.with_status("invalidated"))
        return EditedProposalValidation(proposal, validation, decision_id, False)

    if edited or proposal.status != "approved":
        proposal = repositories.proposals.put(
            replace(
                proposal,
                draft=final_text,
                status="drafted",
                decision_ref=decision_id,
                operation_id=validation.operation_id,
            )
        )
    return EditedProposalValidation(proposal, validation, decision_id, True)


def approve_proposal(
    sekai: SekaiGateway,
    proposal_external_id: str,
    final_text_hash: str,
    namespace: str,
    *,
    clock_ms: Callable[[], int] | None = None,
) -> ProposalApproval:
    with _proposal_lock(proposal_external_id):
        return _approve_proposal_locked(
            sekai,
            proposal_external_id,
            final_text_hash,
            namespace,
            clock_ms=clock_ms,
        )


def _approve_proposal_locked(
    sekai: SekaiGateway,
    proposal_external_id: str,
    final_text_hash: str,
    namespace: str,
    *,
    clock_ms: Callable[[], int] | None = None,
) -> ProposalApproval:
    now_ms = (clock_ms or (lambda: time.time_ns() // 1_000_000))()
    repositories = CausalRepositories.create(sekai, namespace, clock_ms=lambda: now_ms)
    proposal = repositories.proposals.get_external(proposal_external_id)
    if proposal is None:
        raise ProposalWorkflowError(f"proposal not found: {proposal_external_id}")
    if proposal.status != "drafted":
        raise ProposalWorkflowError("only a validated drafted proposal can be approved")
    if final_text_hash != proposal.draft_hash:
        raise ProposalWorkflowError("approval hash does not match the validated final text")
    expected_validation_id = _validation_decision_id(
        namespace, proposal.external_id, proposal.draft_hash
    )
    if proposal.decision_ref != expected_validation_id:
        raise ProposalWorkflowError("proposal does not reference its successful claim validation")
    validation_decision_id = proposal.decision_ref
    approval_id = _approval_id(namespace, proposal.external_id, final_text_hash)
    sekai.record_decision(
        sekai_pb2.Decision(
            id=approval_id,
            timestamp=now_ms,
            actor="hibiki",
            action="hibiki.proposal_approval",
            reason="operator approved the exact validated final-text hash",
            evidence={
                "final_text_hash": final_text_hash,
                "validation_decision_id": validation_decision_id,
            },
            target_id=proposal.external_id,
            outcome="approved",
        )
    )
    approved = repositories.proposals.put(
        replace(proposal, status="approved", decision_ref=approval_id)
    )
    return ProposalApproval(approved, approval_id, validation_decision_id)


def require_current_approval(
    sekai: SekaiGateway,
    proposal: ProposalRecord,
    final_text: str,
) -> str:
    if proposal.status != "approved" or sha256_text(final_text) != proposal.draft_hash:
        raise ProposalWorkflowError("proposal approval is stale or absent for the final text")
    expected_approval_id = _approval_id(
        proposal.namespace, proposal.external_id, proposal.draft_hash
    )
    if proposal.decision_ref != expected_approval_id:
        raise ProposalWorkflowError("proposal approval is stale or absent for the final text")
    return proposal.decision_ref


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


def _validation_decision_id(namespace: str, target_id: str, final_text_hash: str) -> str:
    return str(
        uuid.uuid5(
            PROPOSAL_DECISION_NAMESPACE,
            f"{namespace}:validation:{target_id}:{final_text_hash}",
        )
    )


def _approval_id(namespace: str, proposal_external_id: str, final_text_hash: str) -> str:
    return str(
        uuid.uuid5(
            PROPOSAL_DECISION_NAMESPACE,
            f"{namespace}:approval:{proposal_external_id}:{final_text_hash}",
        )
    )


def _proposal_external_id_for_source(source_external_id: str, namespace: str) -> str:
    prefix = f"hibiki.source:{namespace}:"
    if not source_external_id.startswith(prefix) or source_external_id == prefix:
        raise ProposalWorkflowError(f"source external ID must identify {namespace}/hibiki.source")
    return f"hibiki.proposal:{namespace}:{source_external_id.removeprefix(prefix)}"


@contextmanager
def _proposal_lock(proposal_external_id: str) -> Iterator[None]:
    lock_name = f"hibiki-proposal-{sha256_text(proposal_external_id)}.lock"
    lock_path = os.path.join(tempfile.gettempdir(), lock_name)
    flags = os.O_CREAT | os.O_RDWR | getattr(os, "O_CLOEXEC", 0)
    descriptor = os.open(lock_path, flags, 0o600)
    acquired = False
    try:
        _lock_descriptor(descriptor)
        acquired = True
        yield
    finally:
        try:
            if acquired:
                _unlock_descriptor(descriptor)
        finally:
            os.close(descriptor)


def _lock_descriptor(descriptor: int) -> None:
    if os.name != "nt":
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        return
    if os.fstat(descriptor).st_size == 0:
        os.write(descriptor, b"\0")
    while True:
        try:
            os.lseek(descriptor, 0, os.SEEK_SET)
            msvcrt.locking(descriptor, msvcrt.LK_NBLCK, 1)
            return
        except OSError as error:
            winerror = getattr(error, "winerror", None)
            if error.errno not in {errno.EACCES, errno.EAGAIN} and winerror not in {33, 36}:
                raise
            time.sleep(0.05)


def _unlock_descriptor(descriptor: int) -> None:
    if os.name != "nt":
        fcntl.flock(descriptor, fcntl.LOCK_UN)
        return
    os.lseek(descriptor, 0, os.SEEK_SET)
    msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)


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


def _inventory_evidence(inventory: ClaimInventoryResult) -> dict[str, str]:
    return {
        "inventory_claims": json.dumps(
            list(inventory.claims), ensure_ascii=False, separators=(",", ":")
        ),
        "inventory_operation_id": inventory.operation_id,
        "inventory_provider": inventory.provider,
        "inventory_model": inventory.model,
        "inventory_receipt_json": inventory.receipt_json,
        "inventory_receipt_complete": str(inventory.receipt_complete).lower(),
        "inventory_missing_surfaces": json.dumps(
            list(inventory.missing_surfaces), separators=(",", ":")
        ),
    }
