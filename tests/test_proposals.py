from __future__ import annotations

from hibiki.discovery import discover_public_revision
from hibiki.proposals import draft_source
from hibiki.records import CausalRepositories, SourceRecord
from hibiki.selection import commit_evidence_hash
from tests.fakes import FakeChiseiGateway, FakeSekaiGateway
from tests.test_discovery import fixture_runner
from tests.test_drafting import draft_response


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
        FakeChiseiGateway(draft_response()),
        source.external_id,
        "hibiki",
        clock_ms=lambda: 200,
    )

    assert drafted.proposal.source_external_id == source.external_id
    assert repositories.proposals.get(source.stable_id) == drafted.proposal
    decision = sekai.decisions[drafted.proposal.decision_ref]
    assert decision.action == "hibiki.proposal_draft"
    assert decision.evidence["draft_hash"] == drafted.proposal.draft_hash
