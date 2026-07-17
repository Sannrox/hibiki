from __future__ import annotations

import json
from dataclasses import dataclass, field

import pytest

from hibiki.boundaries import ProcessResult
from hibiki.discovery import discover_public_revision
from hibiki.proposals import approve_proposal, draft_source
from hibiki.publication import PublicationWorkflowError, publish_proposal
from hibiki.records import CausalRepositories, ProposalRecord, SourceRecord
from hibiki.selection import commit_evidence_hash
from tests.fakes import FakeChiseiGateway, FakeSekaiGateway
from tests.test_discovery import fixture_runner
from tests.test_drafting import draft_response
from tests.test_validation import validation_response


@dataclass
class BirdClawRunner:
    results: list[ProcessResult]
    calls: list[tuple[tuple[str, ...], float]] = field(default_factory=list)
    requests: list[dict[str, object]] = field(default_factory=list)

    def run(
        self,
        argv: tuple[str, ...],
        timeout: float,
        *,
        input_text: str | None = None,
    ) -> ProcessResult:
        self.calls.append((argv, timeout))
        assert input_text is not None
        self.requests.append(json.loads(input_text))
        return self.results.pop(0)


def _approved_proposal(sekai: FakeSekaiGateway) -> ProposalRecord:
    bundle = discover_public_revision(fixture_runner(), "example/tenkai", "abc123")
    source = CausalRepositories.create(sekai, "hibiki").sources.put(
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
    return approve_proposal(
        sekai,
        drafted.proposal.external_id,
        drafted.proposal.draft_hash,
        "hibiki",
    ).proposal


def _result(payload: object, *, returncode: int = 0, stderr: str = "") -> ProcessResult:
    return ProcessResult(returncode, json.dumps(payload), stderr)


def test_publish_persists_intent_then_reads_back_exact_birdclaw_post() -> None:
    sekai = FakeSekaiGateway()
    proposal = _approved_proposal(sekai)
    client_reference = f"hibiki.publication:hibiki:{proposal.stable_id}"
    runner = BirdClawRunner(
        [
            _result({"accepted": True}),
            _result(
                {
                    "posts": [
                        {
                            "client_reference": client_reference,
                            "post_id": "1900000000000000000",
                        }
                    ]
                }
            ),
        ]
    )

    result = publish_proposal(
        runner,
        sekai,
        proposal.external_id,
        "builder",
        "hibiki",
        allow_live_writes=True,
    )

    assert result.publication.status == "posted"
    assert result.publication.post_id == "1900000000000000000"
    assert result.proposal.status == "published"
    assert result.reconciled is False
    assert runner.calls == [
        (("birdclaw", "post", "--json"), 30.0),
        (("birdclaw", "authored-posts", "--json"), 30.0),
    ]
    assert runner.requests[0] == {
        "account": "builder",
        "client_reference": client_reference,
        "text": proposal.draft,
    }
    assert runner.requests[1] == {
        "account": "builder",
        "client_reference": client_reference,
    }
    repositories = CausalRepositories.create(sekai, "hibiki")
    assert repositories.publications.get(proposal.stable_id) == result.publication
    assert repositories.proposals.get(proposal.stable_id) == result.proposal


def test_live_write_guard_fails_before_intent_or_birdclaw_call() -> None:
    sekai = FakeSekaiGateway()
    proposal = _approved_proposal(sekai)
    runner = BirdClawRunner([])

    with pytest.raises(PublicationWorkflowError, match="live publication is disabled"):
        publish_proposal(
            runner,
            sekai,
            proposal.external_id,
            "builder",
            "hibiki",
            allow_live_writes=False,
        )

    assert CausalRepositories.create(sekai, "hibiki").publications.get(proposal.stable_id) is None
    assert runner.calls == []


def test_uncertain_post_is_reconciled_before_any_retry() -> None:
    sekai = FakeSekaiGateway()
    proposal = _approved_proposal(sekai)
    client_reference = f"hibiki.publication:hibiki:{proposal.stable_id}"
    first_runner = BirdClawRunner([_result({}, returncode=1, stderr="connection lost")])

    with pytest.raises(PublicationWorkflowError, match="outcome is uncertain"):
        publish_proposal(
            first_runner,
            sekai,
            proposal.external_id,
            "builder",
            "hibiki",
            allow_live_writes=True,
        )

    publication = CausalRepositories.create(sekai, "hibiki").publications.get(
        proposal.stable_id
    )
    assert publication is not None
    assert publication.status == "uncertain"

    reconcile_runner = BirdClawRunner(
        [
            _result(
                {
                    "posts": [
                        {
                            "client_reference": client_reference,
                            "post_id": "1900000000000000001",
                        }
                    ]
                }
            )
        ]
    )
    result = publish_proposal(
        reconcile_runner,
        sekai,
        proposal.external_id,
        "builder",
        "hibiki",
        allow_live_writes=True,
    )

    assert result.publication.status == "posted"
    assert result.reconciled is True
    assert reconcile_runner.calls == [
        (("birdclaw", "authored-posts", "--json"), 30.0)
    ]


def test_retry_requires_a_separate_no_match_reconciliation() -> None:
    sekai = FakeSekaiGateway()
    proposal = _approved_proposal(sekai)
    first_runner = BirdClawRunner([_result({}, returncode=1, stderr="connection lost")])
    with pytest.raises(PublicationWorkflowError):
        publish_proposal(
            first_runner,
            sekai,
            proposal.external_id,
            "builder",
            "hibiki",
            allow_live_writes=True,
        )

    reconcile_runner = BirdClawRunner([_result({"posts": []})])
    with pytest.raises(PublicationWorkflowError, match="retry is now safe"):
        publish_proposal(
            reconcile_runner,
            sekai,
            proposal.external_id,
            "builder",
            "hibiki",
            allow_live_writes=True,
        )

    publication = CausalRepositories.create(sekai, "hibiki").publications.get(
        proposal.stable_id
    )
    assert publication is not None
    assert publication.status == "failed"
    assert reconcile_runner.calls == [
        (("birdclaw", "authored-posts", "--json"), 30.0)
    ]


def test_published_result_is_idempotent_without_birdclaw_call() -> None:
    sekai = FakeSekaiGateway()
    proposal = _approved_proposal(sekai)
    client_reference = f"hibiki.publication:hibiki:{proposal.stable_id}"
    first_runner = BirdClawRunner(
        [
            _result({"accepted": True}),
            _result(
                {
                    "posts": [
                        {"client_reference": client_reference, "post_id": "post-1"}
                    ]
                }
            ),
        ]
    )
    first = publish_proposal(
        first_runner,
        sekai,
        proposal.external_id,
        "builder",
        "hibiki",
        allow_live_writes=True,
    )

    second_runner = BirdClawRunner([])
    second = publish_proposal(
        second_runner,
        sekai,
        proposal.external_id,
        "builder",
        "hibiki",
        allow_live_writes=True,
    )

    assert second.publication == first.publication
    assert second.reconciled is True
    assert second_runner.calls == []
