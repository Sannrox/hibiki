from __future__ import annotations

import json

import pytest

from hibiki.contracts import sekai_pb2
from hibiki.evidence import PRODUCER_IDENTITY, REPLY_TYPE, SNAPSHOT_TYPE
from hibiki.outcomes import (
    CATEGORIES,
    OutcomeWorkflowError,
    build_outcome_report,
    classify_replies,
    confirm_classification,
)
from hibiki.records import CausalRepositories, ProposalRecord, PublicationRecord
from tests.fakes import FakeChiseiGateway, FakeSekaiGateway


def setup_publication(reply_count: int = 1) -> tuple[FakeSekaiGateway, PublicationRecord]:
    sekai = FakeSekaiGateway()
    repositories = CausalRepositories.create(sekai, "hibiki", clock_ms=lambda: 100)
    proposal = repositories.proposals.put(
        ProposalRecord(
            stable_id="proposal-1",
            source_external_id="hibiki.source:hibiki:example/tenkai@abc123",
            evidence_hash="evidence-hash",
            draft="A grounded post.",
            status="published",
        )
    )
    publication = repositories.publications.put(
        PublicationRecord(
            stable_id="publication-1",
            proposal_external_id=proposal.external_id,
            final_text=proposal.draft,
            target_account="builder",
            attempted_at=1,
            status="posted",
            approval_id="approval-1",
            post_id="1900000000000000000",
        )
    )
    for index in range(reply_count):
        add_submission(
            sekai,
            publication,
            evidence_type=REPLY_TYPE,
            submission_id=f"reply-submission-{index}",
            source_record_id=f"reply-{index}",
            source_version="1",
            observed_at=10,
        )
    return sekai, publication


def add_submission(
    sekai: FakeSekaiGateway,
    publication: PublicationRecord,
    *,
    evidence_type: str,
    submission_id: str,
    source_record_id: str,
    source_version: str,
    observed_at: int = 604_800_000,
) -> None:
    sekai.evidence_results.append(
        sekai_pb2.EvidenceSubmissionResult(
            submission=sekai_pb2.EvidenceSubmissionRecord(
                id=submission_id,
                producer_identity=PRODUCER_IDENTITY,
                source_record_id=source_record_id,
                source_version=source_version,
                target_external_id=publication.external_id,
                target_kind="hibiki.publication",
                evidence_type=evidence_type,
                lifecycle_state="available",
                observed_at_ms=observed_at,
            ),
            admitted=True,
            projected=True,
        )
    )


def classification_payload(count: int, category: str = "potential_user") -> str:
    return json.dumps(
        {
            "classifications": [
                {
                    "submission_id": f"reply-submission-{index}",
                    "reply_id": f"reply-{index}",
                    "category": category,
                    "confidence_bps": 9500,
                }
                for index in range(count)
            ]
        }
    )


def test_first_classifications_require_confirmation_and_are_idempotent() -> None:
    sekai, publication = setup_publication(2)
    chisei = FakeChiseiGateway(classification_payload(2))

    first = classify_replies(sekai, chisei, publication.external_id, "hibiki", clock_ms=lambda: 200)
    second = classify_replies(
        sekai, chisei, publication.external_id, "hibiki", clock_ms=lambda: 300
    )

    assert [item.disposition for item in first.classifications] == [
        "confirmation_required",
        "confirmation_required",
    ]
    assert second.classifications == first.classifications
    assert len(chisei.executed_plans) == 1


def test_confirmation_persists_correction_as_evaluation_evidence() -> None:
    sekai, publication = setup_publication()
    classify_replies(
        sekai,
        FakeChiseiGateway(classification_payload(1)),
        publication.external_id,
        "hibiki",
    )

    result = confirm_classification(
        sekai, "reply-submission-0", "substantive_technical_discussion", clock_ms=lambda: 300
    )

    assert result.corrected is True
    assert result.confirmed_count == 1
    confirmation = next(item for item in sekai.decisions.values() if item.actor == "operator")
    assert confirmation.outcome == "corrected"
    assert confirmation.evidence["predicted_category"] == "potential_user"
    assert confirmation.evidence["confirmed_category"] == "substantive_technical_discussion"


def test_calibrated_high_confidence_classification_can_be_automatic() -> None:
    sekai, publication = setup_publication()
    for index in range(25):
        sekai.record_decision(
            sekai_pb2.Decision(
                id=f"confirmation-{index}",
                timestamp=index,
                actor="operator",
                action="hibiki.reply_classification_confirmation",
                target_id=f"prior-{index}",
                outcome="correct",
                evidence={"confirmed_category": "potential_user"},
            )
        )

    result = classify_replies(
        sekai, FakeChiseiGateway(classification_payload(1)), publication.external_id, "hibiki"
    )

    assert result.calibrated is True
    assert result.classifications[0].disposition == "automatic"


def test_low_accuracy_does_not_enable_automatic_classification() -> None:
    sekai, publication = setup_publication()
    for index in range(25):
        sekai.record_decision(
            sekai_pb2.Decision(
                id=f"confirmation-{index}",
                timestamp=index,
                actor="operator",
                action="hibiki.reply_classification_confirmation",
                target_id=f"prior-{index}",
                outcome="correct" if index < 20 else "corrected",
                evidence={"confirmed_category": "potential_user"},
            )
        )

    result = classify_replies(
        sekai, FakeChiseiGateway(classification_payload(1)), publication.external_id, "hibiki"
    )

    assert result.calibrated is False
    assert result.classifications[0].disposition == "confirmation_required"


def test_final_report_counts_confirmed_qualified_replies_and_exposes_lineage() -> None:
    sekai, publication = setup_publication()
    add_submission(
        sekai,
        publication,
        evidence_type=SNAPSHOT_TYPE,
        submission_id="snapshot-7d",
        source_record_id=publication.post_id,
        source_version="7d:complete-v2",
    )
    chisei = FakeChiseiGateway(
        (
            classification_payload(1),
            json.dumps(
                {
                    "metrics": {
                        "impressions": 1200,
                        "likes": 20,
                        "replies": 1,
                        "reposts": 3,
                        "quotes": 2,
                    }
                }
            ),
        )
    )
    classify_replies(sekai, chisei, publication.external_id, "hibiki")
    confirm_classification(sekai, "reply-submission-0", "potential_user")

    report = build_outcome_report(sekai, chisei, publication.external_id, "7d", "hibiki")

    assert report.status == "final"
    assert report.outcome.qualified_replies == 1
    assert report.outcome.metrics["impressions"] == 1200
    assert report.lineage == {
        "source_external_id": "hibiki.source:hibiki:example/tenkai@abc123",
        "proposal_external_id": "hibiki.proposal:hibiki:proposal-1",
        "publication_external_id": publication.external_id,
        "snapshot_submission_id": "snapshot-7d",
        "reply_submission_ids": ["reply-submission-0"],
        "outcome_external_id": "hibiki.outcome:hibiki:publication-1:7d",
    }


def test_report_rejects_unconfirmed_reply_and_invalid_category() -> None:
    sekai, publication = setup_publication()
    add_submission(
        sekai,
        publication,
        evidence_type=SNAPSHOT_TYPE,
        submission_id="snapshot-24h",
        source_record_id=publication.post_id,
        source_version="24h:complete-v2",
    )
    chisei = FakeChiseiGateway(classification_payload(1))

    with pytest.raises(OutcomeWorkflowError, match="must be confirmed"):
        build_outcome_report(sekai, chisei, publication.external_id, "24h", "hibiki")
    with pytest.raises(OutcomeWorkflowError, match="category is invalid"):
        confirm_classification(sekai, "reply-submission-0", "spam")


def test_preliminary_report_excludes_replies_after_its_fixed_window() -> None:
    sekai, publication = setup_publication()
    late_reply = sekai.evidence_results[0].submission
    late_reply.observed_at_ms = publication.attempted_at + 86_400_001
    add_submission(
        sekai,
        publication,
        evidence_type=SNAPSHOT_TYPE,
        submission_id="snapshot-24h",
        source_record_id=publication.post_id,
        source_version="24h:complete-v2",
        observed_at=publication.attempted_at + 86_400_000,
    )
    chisei = FakeChiseiGateway(
        (
            classification_payload(1),
            json.dumps(
                {
                    "metrics": {
                        "impressions": 100,
                        "likes": 1,
                        "replies": 0,
                        "reposts": 0,
                        "quotes": 0,
                    }
                }
            ),
        )
    )
    classify_replies(sekai, chisei, publication.external_id, "hibiki")

    report = build_outcome_report(sekai, chisei, publication.external_id, "24h", "hibiki")

    assert report.status == "preliminary"
    assert report.outcome.qualified_replies == 0
    assert report.classifications == ()
    assert report.lineage["reply_submission_ids"] == []


def test_report_requires_the_supported_complete_snapshot_marker() -> None:
    sekai, publication = setup_publication(0)
    add_submission(
        sekai,
        publication,
        evidence_type=SNAPSHOT_TYPE,
        submission_id="snapshot-partial",
        source_record_id=publication.post_id,
        source_version="7d:partial",
    )

    with pytest.raises(OutcomeWorkflowError, match="complete 7d snapshot"):
        build_outcome_report(
            sekai, FakeChiseiGateway("{}"), publication.external_id, "7d", "hibiki"
        )


def test_report_validates_lineage_before_persisting_an_outcome() -> None:
    sekai, publication = setup_publication(0)
    add_submission(
        sekai,
        publication,
        evidence_type=SNAPSHOT_TYPE,
        submission_id="snapshot-7d",
        source_record_id=publication.post_id,
        source_version="7d:complete-v2",
    )
    proposal_id = next(
        object_id for object_id, item in sekai.objects.items() if item.kind == "hibiki.proposal"
    )
    del sekai.objects[proposal_id]

    with pytest.raises(OutcomeWorkflowError, match="proposal record was not found"):
        build_outcome_report(
            sekai, FakeChiseiGateway("{}"), publication.external_id, "7d", "hibiki"
        )

    assert all(item.kind != "hibiki.outcome" for item in sekai.objects.values())


def test_classification_rejects_malformed_operation_receipt() -> None:
    sekai, publication = setup_publication()
    chisei = FakeChiseiGateway(classification_payload(1), receipt_json="truncated")

    with pytest.raises(OutcomeWorkflowError, match="receipt response is not valid JSON"):
        classify_replies(sekai, chisei, publication.external_id, "hibiki")

    assert not sekai.decisions


def test_every_documented_category_is_accepted() -> None:
    assert {
        "potential_user",
        "potential_tester_or_contributor",
        "substantive_technical_discussion",
        "general_reaction",
        "irrelevant_or_low_signal",
    } == CATEGORIES
