from __future__ import annotations

from dataclasses import replace

import pytest

from hibiki.contracts import sekai_pb2
from hibiki.discovery import discover_public_revision
from hibiki.proposals import (
    ProposalWorkflowError,
    approve_proposal,
    draft_source,
    require_current_approval,
    validate_proposal_edit,
)
from hibiki.records import CausalRepositories, SourceRecord
from hibiki.selection import commit_evidence_hash, legacy_commit_evidence_hash
from tests.fakes import FakeChiseiGateway, FakeSekaiGateway
from tests.test_discovery import fixture_runner
from tests.test_drafting import draft_response
from tests.test_validation import inventory_response, validation_response


def test_draft_source_persists_proposal_and_governed_lineage() -> None:
    runner = fixture_runner()
    bundle = discover_public_revision(runner, "example/tenkai", "abc123")
    sekai = FakeSekaiGateway()
    repositories = CausalRepositories.create(sekai, "hibiki", clock_ms=lambda: 100)
    source = repositories.sources.put(
        SourceRecord(
            stable_id="example/tenkai@abc123",
            repository="example/tenkai",
            revision="abc123",
            public_url="https://github.com/example/tenkai/commit/abc123",
            evidence_hash=commit_evidence_hash(bundle, "abc123"),
        )
    )

    drafted = draft_source(
        fixture_runner(),
        sekai,
        FakeChiseiGateway((draft_response(), validation_response())),
        source.external_id,
        "hibiki",
        clock_ms=lambda: 200,
    )

    assert drafted.proposal.source_external_id == source.external_id
    assert repositories.proposals.get(source.stable_id) == drafted.proposal
    draft_decision = next(
        decision
        for decision in sekai.decisions.values()
        if decision.action == "hibiki.proposal_draft"
    )
    assert draft_decision.evidence["draft_hash"] == drafted.proposal.draft_hash
    validation = next(
        decision
        for decision in sekai.decisions.values()
        if decision.action == "hibiki.claim_validation"
    )
    assert validation.outcome == "supported"
    assert drafted.proposal.decision_ref == validation.id


def test_draft_source_does_not_persist_unsupported_generated_text() -> None:
    bundle = discover_public_revision(fixture_runner(), "example/tenkai", "abc123")
    sekai = FakeSekaiGateway()
    repositories = CausalRepositories.create(sekai, "hibiki", clock_ms=lambda: 100)
    source = repositories.sources.put(
        SourceRecord(
            stable_id="example/tenkai@abc123",
            repository="example/tenkai",
            revision="abc123",
            public_url="https://github.com/example/tenkai/commit/abc123",
            evidence_hash=commit_evidence_hash(bundle, "abc123"),
        )
    )

    with pytest.raises(ProposalWorkflowError, match="unsupported factual claim"):
        draft_source(
            fixture_runner(),
            sekai,
            FakeChiseiGateway((draft_response(), validation_response(supported=False))),
            source.external_id,
            "hibiki",
        )

    assert repositories.proposals.get(source.stable_id) is None


def test_draft_source_migrates_traceable_legacy_evidence_hash() -> None:
    bundle = discover_public_revision(fixture_runner(), "example/tenkai", "abc123")
    sekai = FakeSekaiGateway()
    repositories = CausalRepositories.create(sekai, "hibiki")
    source = repositories.sources.put(
        SourceRecord(
            stable_id="example/tenkai@abc123",
            repository="example/tenkai",
            revision="abc123",
            public_url="https://github.com/example/tenkai/commit/abc123",
            evidence_hash=legacy_commit_evidence_hash(bundle, "abc123"),
        )
    )
    sekai.record_decision(
        sekai_pb2.Decision(
            id="legacy-selection",
            timestamp=100,
            actor="hibiki",
            action="hibiki.source_selection",
            evidence={
                "repository": source.repository,
                "revision": source.revision,
                "source_evidence_hash": source.evidence_hash,
            },
            target_id=source.external_id,
            outcome="selected",
        )
    )

    draft_source(
        fixture_runner(),
        sekai,
        FakeChiseiGateway((draft_response(), validation_response())),
        source.external_id,
        "hibiki",
    )

    migrated = repositories.sources.get(source.stable_id)
    assert migrated is not None
    assert migrated.evidence_hash == commit_evidence_hash(bundle, "abc123")


def test_edited_text_must_validate_before_exact_hash_approval() -> None:
    bundle = discover_public_revision(fixture_runner(), "example/tenkai", "abc123")
    sekai = FakeSekaiGateway()
    repositories = CausalRepositories.create(sekai, "hibiki")
    source = repositories.sources.put(
        SourceRecord(
            stable_id="example/tenkai@abc123",
            repository="example/tenkai",
            revision="abc123",
            public_url="https://github.com/example/tenkai/commit/abc123",
            evidence_hash=commit_evidence_hash(bundle, "abc123"),
        )
    )
    drafted = draft_source(
        fixture_runner(),
        sekai,
        FakeChiseiGateway((draft_response(), validation_response())),
        source.external_id,
        "hibiki",
    )
    edited_text = "I made retries deterministic with a stable identity for each attempt."

    validated = validate_proposal_edit(
        fixture_runner(),
        sekai,
        FakeChiseiGateway(
            (inventory_response(edited_text), validation_response(claim=edited_text))
        ),
        drafted.proposal.external_id,
        edited_text,
        "hibiki",
    )
    approved = approve_proposal(
        sekai,
        drafted.proposal.external_id,
        validated.proposal.draft_hash,
        "hibiki",
    )

    assert validated.persisted is True
    assert validated.proposal.status == "drafted"
    assert approved.proposal.status == "approved"
    assert require_current_approval(sekai, approved.proposal, edited_text) == approved.approval_id
    with pytest.raises(ProposalWorkflowError, match="stale or absent"):
        require_current_approval(sekai, approved.proposal, edited_text + " Edited again.")


def test_edit_invalidates_approval_even_when_new_text_is_unsupported() -> None:
    bundle = discover_public_revision(fixture_runner(), "example/tenkai", "abc123")
    sekai = FakeSekaiGateway()
    repositories = CausalRepositories.create(sekai, "hibiki")
    source = repositories.sources.put(
        SourceRecord(
            stable_id="example/tenkai@abc123",
            repository="example/tenkai",
            revision="abc123",
            public_url="https://github.com/example/tenkai/commit/abc123",
            evidence_hash=commit_evidence_hash(bundle, "abc123"),
        )
    )
    drafted = draft_source(
        fixture_runner(),
        sekai,
        FakeChiseiGateway((draft_response(), validation_response())),
        source.external_id,
        "hibiki",
    )
    approved = approve_proposal(
        sekai, drafted.proposal.external_id, drafted.proposal.draft_hash, "hibiki"
    )
    unsupported = "I guarantee retries can never fail."

    result = validate_proposal_edit(
        fixture_runner(),
        sekai,
        FakeChiseiGateway(
            (
                inventory_response(unsupported),
                validation_response(supported=False, claim=unsupported),
            )
        ),
        approved.proposal.external_id,
        unsupported,
        "hibiki",
    )

    assert result.persisted is False
    assert result.proposal.status == "invalidated"
    with pytest.raises(ProposalWorkflowError, match="stale or absent"):
        require_current_approval(sekai, result.proposal, drafted.proposal.draft)


def test_approval_rejects_hash_that_does_not_match_validated_text() -> None:
    bundle = discover_public_revision(fixture_runner(), "example/tenkai", "abc123")
    sekai = FakeSekaiGateway()
    repositories = CausalRepositories.create(sekai, "hibiki")
    source = repositories.sources.put(
        SourceRecord(
            stable_id="example/tenkai@abc123",
            repository="example/tenkai",
            revision="abc123",
            public_url="https://github.com/example/tenkai/commit/abc123",
            evidence_hash=commit_evidence_hash(bundle, "abc123"),
        )
    )
    drafted = draft_source(
        fixture_runner(),
        sekai,
        FakeChiseiGateway((draft_response(), validation_response())),
        source.external_id,
        "hibiki",
    )

    with pytest.raises(ProposalWorkflowError, match="does not match"):
        approve_proposal(sekai, drafted.proposal.external_id, "0" * 64, "hibiki")


@pytest.mark.parametrize("status", ["published", "rejected"])
def test_terminal_proposal_cannot_be_reopened_by_validation(status: str) -> None:
    bundle = discover_public_revision(fixture_runner(), "example/tenkai", "abc123")
    sekai = FakeSekaiGateway()
    repositories = CausalRepositories.create(sekai, "hibiki")
    source = repositories.sources.put(
        SourceRecord(
            stable_id="example/tenkai@abc123",
            repository="example/tenkai",
            revision="abc123",
            public_url="https://github.com/example/tenkai/commit/abc123",
            evidence_hash=commit_evidence_hash(bundle, "abc123"),
        )
    )
    drafted = draft_source(
        fixture_runner(),
        sekai,
        FakeChiseiGateway((draft_response(), validation_response())),
        source.external_id,
        "hibiki",
    )
    terminal = repositories.proposals.put(drafted.proposal.with_status(status))

    with pytest.raises(ProposalWorkflowError, match="cannot accept edited text"):
        validate_proposal_edit(
            fixture_runner(),
            sekai,
            FakeChiseiGateway((inventory_response(terminal.draft), validation_response())),
            terminal.external_id,
            terminal.draft,
            "hibiki",
        )

    assert repositories.proposals.get(terminal.stable_id) == terminal


def test_approval_does_not_depend_on_global_decision_window() -> None:
    bundle = discover_public_revision(fixture_runner(), "example/tenkai", "abc123")
    sekai = FakeSekaiGateway()
    repositories = CausalRepositories.create(sekai, "hibiki")
    source = repositories.sources.put(
        SourceRecord(
            stable_id="example/tenkai@abc123",
            repository="example/tenkai",
            revision="abc123",
            public_url="https://github.com/example/tenkai/commit/abc123",
            evidence_hash=commit_evidence_hash(bundle, "abc123"),
        )
    )
    drafted = draft_source(
        fixture_runner(),
        sekai,
        FakeChiseiGateway((draft_response(), validation_response())),
        source.external_id,
        "hibiki",
    )
    for index in range(101):
        sekai.record_decision(
            sekai_pb2.Decision(
                id=f"newer-validation-{index}",
                timestamp=1_000 + index,
                actor="hibiki",
                action="hibiki.claim_validation",
                target_id=f"other-{index}",
                outcome="supported",
            )
        )

    approved = approve_proposal(
        sekai, drafted.proposal.external_id, drafted.proposal.draft_hash, "hibiki"
    )

    assert approved.validation_decision_id == drafted.proposal.decision_ref
    assert (
        require_current_approval(sekai, approved.proposal, approved.proposal.draft)
        == approved.approval_id
    )


def test_legacy_approved_proposal_resolves_deterministic_approval_id() -> None:
    bundle = discover_public_revision(fixture_runner(), "example/tenkai", "abc123")
    sekai = FakeSekaiGateway()
    repositories = CausalRepositories.create(sekai, "hibiki")
    source = repositories.sources.put(
        SourceRecord(
            stable_id="example/tenkai@abc123",
            repository="example/tenkai",
            revision="abc123",
            public_url="https://github.com/example/tenkai/commit/abc123",
            evidence_hash=commit_evidence_hash(bundle, "abc123"),
        )
    )
    drafted = draft_source(
        fixture_runner(),
        sekai,
        FakeChiseiGateway((draft_response(), validation_response())),
        source.external_id,
        "hibiki",
    )
    approved = approve_proposal(
        sekai, drafted.proposal.external_id, drafted.proposal.draft_hash, "hibiki"
    )
    legacy = replace(approved.proposal, decision_ref=approved.validation_decision_id)

    assert require_current_approval(sekai, legacy, legacy.draft) == approved.approval_id


def test_legacy_approved_record_without_approval_decision_is_rejected() -> None:
    bundle = discover_public_revision(fixture_runner(), "example/tenkai", "abc123")
    sekai = FakeSekaiGateway()
    repositories = CausalRepositories.create(sekai, "hibiki")
    source = repositories.sources.put(
        SourceRecord(
            stable_id="example/tenkai@abc123",
            repository="example/tenkai",
            revision="abc123",
            public_url="https://github.com/example/tenkai/commit/abc123",
            evidence_hash=commit_evidence_hash(bundle, "abc123"),
        )
    )
    drafted = draft_source(
        fixture_runner(),
        sekai,
        FakeChiseiGateway((draft_response(), validation_response())),
        source.external_id,
        "hibiki",
    )
    approved = approve_proposal(
        sekai, drafted.proposal.external_id, drafted.proposal.draft_hash, "hibiki"
    )
    legacy = replace(approved.proposal, decision_ref=approved.validation_decision_id)
    del sekai.decisions[approved.approval_id]

    with pytest.raises(ProposalWorkflowError, match="stale or absent"):
        require_current_approval(sekai, legacy, legacy.draft)


def test_failed_redraft_preserves_existing_approval() -> None:
    bundle = discover_public_revision(fixture_runner(), "example/tenkai", "abc123")
    sekai = FakeSekaiGateway()
    repositories = CausalRepositories.create(sekai, "hibiki")
    source = repositories.sources.put(
        SourceRecord(
            stable_id="example/tenkai@abc123",
            repository="example/tenkai",
            revision="abc123",
            public_url="https://github.com/example/tenkai/commit/abc123",
            evidence_hash=commit_evidence_hash(bundle, "abc123"),
        )
    )
    drafted = draft_source(
        fixture_runner(),
        sekai,
        FakeChiseiGateway((draft_response(), validation_response())),
        source.external_id,
        "hibiki",
    )
    approved = approve_proposal(
        sekai, drafted.proposal.external_id, drafted.proposal.draft_hash, "hibiki"
    )

    with pytest.raises(ProposalWorkflowError, match="unsupported factual claim"):
        draft_source(
            fixture_runner(),
            sekai,
            FakeChiseiGateway((draft_response(), validation_response(supported=False))),
            source.external_id,
            "hibiki",
        )

    assert repositories.proposals.get(drafted.proposal.stable_id) == approved.proposal
