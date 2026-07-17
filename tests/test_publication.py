from __future__ import annotations

import json
from dataclasses import dataclass, field

import pytest

from hibiki.boundaries import ProcessResult
from hibiki.discovery import discover_public_revision
from hibiki.proposals import (
    ProposalWorkflowError,
    approve_proposal,
    draft_source,
    validate_proposal_edit,
)
from hibiki.publication import PublicationWorkflowError, publish_proposal
from hibiki.records import (
    CausalRepositories,
    ProposalRecord,
    PublicationRecord,
    RecordValidationError,
    SourceRecord,
)
from hibiki.selection import commit_evidence_hash
from tests.fakes import FakeChiseiGateway, FakeSekaiGateway
from tests.test_discovery import fixture_runner
from tests.test_drafting import draft_response
from tests.test_validation import validation_response

ATTEMPTED_AT = 1_750_000_000_000
SINCE = "2025-06-15T15:01:40Z"


@dataclass
class BirdClawRunner:
    results: list[ProcessResult]
    calls: list[tuple[tuple[str, ...], float]] = field(default_factory=list)

    def run(self, argv: tuple[str, ...], timeout: float) -> ProcessResult:
        self.calls.append((argv, timeout))
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


def _authored_post(proposal: ProposalRecord, post_id: str) -> dict[str, object]:
    return {
        "id": post_id,
        "accountId": "builder",
        "text": proposal.draft,
        "createdAt": "2025-06-15T15:01:41Z",
    }


def _publish(
    runner: BirdClawRunner,
    sekai: FakeSekaiGateway,
    proposal: ProposalRecord,
    *,
    account: str = "builder",
    allow_live_writes: bool = True,
):
    return publish_proposal(
        runner,
        sekai,
        proposal.external_id,
        account,
        "hibiki",
        allow_live_writes=allow_live_writes,
        clock_ms=lambda: ATTEMPTED_AT,
    )


def _readback_calls(proposal: ProposalRecord) -> list[tuple[tuple[str, ...], float]]:
    return [
        (
            (
                "birdclaw",
                "sync",
                "authored",
                "--account",
                "builder",
                "--mode",
                "xurl",
                "--limit",
                "100",
                "--json",
            ),
            30.0,
        ),
        (
            (
                "birdclaw",
                "search",
                "tweets",
                "--resource",
                "authored",
                "--account",
                "builder",
                "--since",
                SINCE,
                "--limit",
                "100",
                "--json",
            ),
            30.0,
        ),
    ]


def test_publish_persists_intent_then_reads_back_exact_birdclaw_post() -> None:
    sekai = FakeSekaiGateway()
    proposal = _approved_proposal(sekai)
    runner = BirdClawRunner(
        [
            _result({"ok": True, "tweetId": "tweet_local"}),
            _result({"ok": True, "kind": "authored"}),
            _result([_authored_post(proposal, "1900000000000000000")]),
        ]
    )

    result = _publish(runner, sekai, proposal)

    assert result.publication.status == "posted"
    assert result.publication.post_id == "1900000000000000000"
    assert result.publication.target_account == "builder"
    assert result.publication.attempted_at == ATTEMPTED_AT
    assert result.proposal.status == "published"
    assert result.reconciled is False
    assert runner.calls == [
        (
            (
                "birdclaw",
                "compose",
                "post",
                "--account",
                "builder",
                proposal.draft,
                "--json",
            ),
            30.0,
        ),
        *_readback_calls(proposal),
    ]
    repositories = CausalRepositories.create(sekai, "hibiki")
    assert repositories.publications.get(proposal.stable_id) == result.publication
    assert repositories.proposals.get(proposal.stable_id) == result.proposal


def test_live_write_guard_fails_before_intent_or_birdclaw_call() -> None:
    sekai = FakeSekaiGateway()
    proposal = _approved_proposal(sekai)
    runner = BirdClawRunner([])

    with pytest.raises(PublicationWorkflowError, match="live publication is disabled"):
        _publish(runner, sekai, proposal, allow_live_writes=False)

    assert CausalRepositories.create(sekai, "hibiki").publications.get(proposal.stable_id) is None
    assert runner.calls == []


def test_uncertain_post_reconciles_stored_account_before_any_retry() -> None:
    sekai = FakeSekaiGateway()
    proposal = _approved_proposal(sekai)
    first_runner = BirdClawRunner([_result({}, returncode=4, stderr="connection lost")])

    with pytest.raises(PublicationWorkflowError, match="outcome is uncertain"):
        _publish(first_runner, sekai, proposal)

    publication = CausalRepositories.create(sekai, "hibiki").publications.get(
        proposal.stable_id
    )
    assert publication is not None
    assert publication.status == "uncertain"
    assert publication.target_account == "builder"

    reconcile_runner = BirdClawRunner(
        [
            _result({"ok": True, "kind": "authored"}),
            _result([_authored_post(proposal, "1900000000000000001")]),
        ]
    )
    result = _publish(reconcile_runner, sekai, proposal, account="changed-account")

    assert result.publication.status == "posted"
    assert result.reconciled is True
    assert reconcile_runner.calls == _readback_calls(proposal)


def test_retry_requires_a_separate_no_match_reconciliation() -> None:
    sekai = FakeSekaiGateway()
    proposal = _approved_proposal(sekai)
    with pytest.raises(PublicationWorkflowError):
        _publish(
            BirdClawRunner([_result({}, returncode=4, stderr="connection lost")]),
            sekai,
            proposal,
        )

    reconcile_runner = BirdClawRunner(
        [_result({"ok": True, "kind": "authored"}), _result([])]
    )
    with pytest.raises(PublicationWorkflowError, match="retry is now safe"):
        _publish(reconcile_runner, sekai, proposal)

    publication = CausalRepositories.create(sekai, "hibiki").publications.get(
        proposal.stable_id
    )
    assert publication is not None
    assert publication.status == "failed"
    assert reconcile_runner.calls == _readback_calls(proposal)


def test_pending_attempt_blocks_proposal_edits_until_reconciled() -> None:
    sekai = FakeSekaiGateway()
    proposal = _approved_proposal(sekai)
    with pytest.raises(PublicationWorkflowError):
        _publish(
            BirdClawRunner([_result({}, returncode=4, stderr="connection lost")]),
            sekai,
            proposal,
        )

    with pytest.raises(ProposalWorkflowError, match="needs reconciliation"):
        validate_proposal_edit(
            fixture_runner(),
            sekai,
            FakeChiseiGateway(validation_response()),
            proposal.external_id,
            proposal.draft + " Edited.",
            "hibiki",
        )


def test_published_result_is_idempotent_without_birdclaw_call() -> None:
    sekai = FakeSekaiGateway()
    proposal = _approved_proposal(sekai)
    first = _publish(
        BirdClawRunner(
            [
                _result({"ok": True, "tweetId": "tweet_local"}),
                _result({"ok": True, "kind": "authored"}),
                _result([_authored_post(proposal, "post-1")]),
            ]
        ),
        sekai,
        proposal,
    )

    second_runner = BirdClawRunner([])
    second = _publish(second_runner, sekai, proposal)

    assert second.publication == first.publication
    assert second.reconciled is True
    assert second_runner.calls == []


def test_posted_publication_requires_an_x_post_identifier() -> None:
    with pytest.raises(RecordValidationError, match="must contain a post_id"):
        PublicationRecord(
            stable_id="publication-1",
            proposal_external_id="hibiki.proposal:hibiki:proposal-1",
            final_text="Exact final text",
            target_account="builder",
            attempted_at=ATTEMPTED_AT,
            status="posted",
            approval_id="approval-1",
        )
