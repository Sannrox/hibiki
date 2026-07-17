from __future__ import annotations

import pytest

from hibiki.contracts import sekai_pb2
from hibiki.discovery import discover_public_revision
from hibiki.proposals import ProposalWorkflowError, draft_source
from hibiki.records import CausalRepositories, SourceRecord
from hibiki.selection import commit_evidence_hash, legacy_commit_evidence_hash
from tests.fakes import FakeChiseiGateway, FakeSekaiGateway
from tests.test_discovery import fixture_runner
from tests.test_drafting import draft_response
from tests.test_validation import validation_response


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
    decision = sekai.decisions[drafted.proposal.decision_ref]
    assert decision.action == "hibiki.proposal_draft"
    assert decision.evidence["draft_hash"] == drafted.proposal.draft_hash
    validation = next(
        decision
        for decision in sekai.decisions.values()
        if decision.action == "hibiki.claim_validation"
    )
    assert validation.outcome == "supported"


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
