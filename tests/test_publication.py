from __future__ import annotations

import json
from dataclasses import dataclass, field, replace

import pytest

from hibiki.boundaries import ProcessResult
from hibiki.discovery import discover_public_revision
from hibiki.proposals import (
    ProposalWorkflowError,
    approve_proposal,
    draft_source,
    validate_proposal_edit,
)
from hibiki.publication import (
    PublicationWorkflowError,
    _safe_x_text_weight,
    publish_proposal,
)
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
from tests.test_validation import inventory_response, validation_response

ATTEMPTED_AT = 1_750_000_000_000
SINCE_ID = "1934265052165046271"
UNTIL_ID = "1934267568751640576"


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


def _approved_edited_proposal(
    sekai: FakeSekaiGateway,
    proposal: ProposalRecord,
    final_text: str,
) -> ProposalRecord:
    validated = validate_proposal_edit(
        fixture_runner(),
        sekai,
        FakeChiseiGateway(
            (inventory_response(final_text), validation_response(claim=final_text))
        ),
        proposal.external_id,
        final_text,
        "hibiki",
    ).proposal
    return approve_proposal(
        sekai,
        validated.external_id,
        validated.draft_hash,
        "hibiki",
    ).proposal


def _result(payload: object, *, returncode: int = 0, stderr: str = "") -> ProcessResult:
    return ProcessResult(returncode, json.dumps(payload), stderr)


def _authored_post(proposal: ProposalRecord, post_id: str) -> dict[str, object]:
    return {
        "id": post_id,
        "text": proposal.draft,
        "createdAt": "2025-06-15T15:01:41Z",
    }


def _sync_result(posts: list[dict[str, object]]) -> ProcessResult:
    return _result(
        {
            "ok": True,
            "kind": "authored",
            "partial": False,
            "payload": {"data": posts},
        }
    )


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
                "--since-id",
                SINCE_ID,
                "--until-id",
                UNTIL_ID,
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
            _sync_result([_authored_post(proposal, "1900000000000000000")]),
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


def test_readback_expands_x_url_entities_before_matching_text() -> None:
    sekai = FakeSekaiGateway()
    proposal = _approved_edited_proposal(
        sekai,
        _approved_proposal(sekai),
        "I documented the retry contract at https://example.com/retries.",
    )
    authored = _authored_post(proposal, "1900000000000000002")
    authored["text"] = "I documented the retry contract at https://t.co/abc."
    authored["entities"] = {
        "urls": [
            {
                "url": "https://t.co/abc",
                "expanded_url": "https://example.com/retries",
            }
        ]
    }

    result = _publish(
        BirdClawRunner(
            [_result({"ok": True, "tweetId": "tweet_local"}), _sync_result([authored])]
        ),
        sekai,
        proposal,
    )

    assert result.publication.post_id == "1900000000000000002"


def test_live_write_guard_fails_before_intent_or_birdclaw_call() -> None:
    sekai = FakeSekaiGateway()
    proposal = _approved_proposal(sekai)
    runner = BirdClawRunner([])

    with pytest.raises(PublicationWorkflowError, match="live publication is disabled"):
        _publish(runner, sekai, proposal, allow_live_writes=False)

    assert CausalRepositories.create(sekai, "hibiki").publications.get(proposal.stable_id) is None
    assert runner.calls == []


def test_long_form_text_is_rejected_before_intent_or_birdclaw_call() -> None:
    sekai = FakeSekaiGateway()
    proposal = _approved_edited_proposal(
        sekai,
        _approved_proposal(sekai),
        "x" * 281,
    )
    runner = BirdClawRunner([])

    with pytest.raises(PublicationWorkflowError, match="safe 280-character"):
        _publish(runner, sekai, proposal)

    assert CausalRepositories.create(sekai, "hibiki").publications.get(proposal.stable_id) is None
    assert runner.calls == []


def test_x_url_weight_is_applied_before_intent_or_birdclaw_call() -> None:
    sekai = FakeSekaiGateway()
    proposal = _approved_edited_proposal(
        sekai,
        _approved_proposal(sekai),
        f"{'a' * 266} https://x.com",
    )
    runner = BirdClawRunner([])

    with pytest.raises(PublicationWorkflowError, match="safe 280-character"):
        _publish(runner, sekai, proposal)

    assert CausalRepositories.create(sekai, "hibiki").publications.get(proposal.stable_id) is None
    assert runner.calls == []


def test_non_url_suffix_is_not_hidden_by_x_url_weighting() -> None:
    sekai = FakeSekaiGateway()
    proposal = _approved_edited_proposal(
        sekai,
        _approved_proposal(sekai),
        f"{'a' * 256} https://x.com😀",
    )
    runner = BirdClawRunner([])

    with pytest.raises(PublicationWorkflowError, match="safe 280-character"):
        _publish(runner, sekai, proposal)

    assert CausalRepositories.create(sekai, "hibiki").publications.get(proposal.stable_id) is None
    assert runner.calls == []


def test_current_tld_url_is_not_undercounted_by_stale_parser_data() -> None:
    sekai = FakeSekaiGateway()
    proposal = _approved_edited_proposal(
        sekai,
        _approved_proposal(sekai),
        f"{'a' * 257} https://nic.music",
    )
    runner = BirdClawRunner([])

    with pytest.raises(PublicationWorkflowError, match="safe 280-character"):
        _publish(runner, sekai, proposal)

    assert CausalRepositories.create(sekai, "hibiki").publications.get(proposal.stable_id) is None
    assert runner.calls == []


def test_known_url_is_not_double_counted_by_fallback_matcher() -> None:
    assert _safe_x_text_weight(f"{'a' * 243} https://github.com") == 267


def test_idn_with_current_tld_is_not_undercounted() -> None:
    assert _safe_x_text_weight(f"{'a' * 257} https://例.music") == 281


def test_idn_url_does_not_absorb_adjacent_ascii_punctuation() -> None:
    assert _safe_x_text_weight(f"{'a' * 256} https://例.music(") == 281


def test_url_fallback_does_not_rescan_overlapping_protocols() -> None:
    text = "https://" * 10_000

    assert _safe_x_text_weight(text) >= 280


def test_explicit_url_after_underscore_is_still_weighted() -> None:
    assert _safe_x_text_weight(f"{'a' * 257}_https://nic.music") == 281


def test_fuzzy_domain_is_not_treated_as_explicit_url() -> None:
    assert _safe_x_text_weight(f"{'a' * 264} foo.web") == 272


def test_protocol_after_ascii_letter_is_not_given_a_synthetic_boundary() -> None:
    assert _safe_x_text_weight(f"{'a' * 258}https://nic.music") == 275


def test_protocol_after_x_valid_ascii_symbol_is_weighted() -> None:
    assert _safe_x_text_weight(f"{'a' * 257}+https://nic.music") == 281


def test_protocol_inside_recognized_url_is_not_counted_twice() -> None:
    text = "https://example.com/日https://nic.music"

    assert _safe_x_text_weight(text) == 48


def test_protocol_inside_fallback_url_path_is_not_counted_twice() -> None:
    text = f"{'a' * 240} https://a.music/https://b.music"

    assert _safe_x_text_weight(text) == 272


def test_protocol_inside_fallback_url_query_is_not_counted_twice() -> None:
    text = f"{'a' * 240} https://a.music/?url=https://b.music"

    assert _safe_x_text_weight(text) == 277


def test_x_delimiter_splits_protocol_inside_linkifier_span() -> None:
    text = f"{'a' * 234} https://a.music/^https://b.music"

    assert _safe_x_text_weight(text) == 282


def test_path_only_character_splits_protocol_inside_query() -> None:
    text = f"{'a' * 233} https://a.music/?q=éhttps://b.music"

    assert _safe_x_text_weight(text) == 281


def test_protocol_inside_balanced_path_parentheses_is_not_counted_twice() -> None:
    text = f"{'a' * 246} https://a.music/(https://b.music)"

    assert _safe_x_text_weight(text) == 280


def test_unreachable_balanced_path_group_does_not_hide_protocol() -> None:
    text = f"{'a' * 245} https://a.music/,(https://b.music)"

    assert _safe_x_text_weight(text) == 295


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
            _sync_result([_authored_post(proposal, "1900000000000000001")]),
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

    reconcile_runner = BirdClawRunner([_sync_result([])])
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

    with pytest.raises(ProposalWorkflowError, match="publication record is active"):
        validate_proposal_edit(
            fixture_runner(),
            sekai,
            FakeChiseiGateway(validation_response()),
            proposal.external_id,
            proposal.draft + " Edited.",
            "hibiki",
        )


def test_completed_publication_cannot_be_attached_to_different_approved_text() -> None:
    sekai = FakeSekaiGateway()
    proposal = _approved_proposal(sekai)
    repositories = CausalRepositories.create(sekai, "hibiki")
    repositories.publications.put(
        PublicationRecord(
            stable_id=proposal.stable_id,
            proposal_external_id=proposal.external_id,
            final_text=proposal.draft,
            target_account="builder",
            attempted_at=ATTEMPTED_AT,
            status="posted",
            approval_id=proposal.decision_ref,
            post_id="post-old",
        )
    )
    changed = repositories.proposals.put(
        replace(
            proposal,
            draft=proposal.draft + " Changed after a partial persistence failure.",
            decision_ref="approval-new",
        )
    )

    with pytest.raises(PublicationWorkflowError, match="does not match"):
        _publish(BirdClawRunner([]), sekai, changed)

    with pytest.raises(ProposalWorkflowError, match="publication record is active"):
        validate_proposal_edit(
            fixture_runner(),
            sekai,
            FakeChiseiGateway(validation_response()),
            proposal.external_id,
            proposal.draft + " Edited.",
            "hibiki",
        )


def test_stale_uncertain_intent_is_not_persisted_as_posted() -> None:
    sekai = FakeSekaiGateway()
    proposal = _approved_proposal(sekai)
    repositories = CausalRepositories.create(sekai, "hibiki")
    stale = repositories.publications.put(
        PublicationRecord(
            stable_id=proposal.stable_id,
            proposal_external_id=proposal.external_id,
            final_text=proposal.draft + " Stale.",
            target_account="builder",
            attempted_at=ATTEMPTED_AT,
            status="uncertain",
            approval_id=proposal.decision_ref,
        )
    )

    with pytest.raises(PublicationWorkflowError, match="does not match"):
        _publish(BirdClawRunner([]), sekai, proposal)

    assert repositories.publications.get(proposal.stable_id) == stale


def test_published_result_is_idempotent_without_birdclaw_call() -> None:
    sekai = FakeSekaiGateway()
    proposal = _approved_proposal(sekai)
    first = _publish(
        BirdClawRunner(
            [
                _result({"ok": True, "tweetId": "tweet_local"}),
                _sync_result([_authored_post(proposal, "post-1")]),
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


def test_legacy_publication_record_round_trips_without_new_metadata() -> None:
    sekai = FakeSekaiGateway()
    repositories = CausalRepositories.create(sekai, "hibiki")
    legacy = PublicationRecord(
        stable_id="publication-legacy",
        proposal_external_id="hibiki.proposal:hibiki:proposal-legacy",
        final_text="Legacy final text",
        target_account="",
        attempted_at=0,
        status="uncertain",
        approval_id="approval-legacy",
        _legacy=True,
    )

    stored = repositories.publications.put(legacy)

    assert stored == legacy
    assert repositories.publications.get(legacy.stable_id) == legacy
    assert "target_account" not in legacy.to_properties()
