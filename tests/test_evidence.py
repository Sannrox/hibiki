from __future__ import annotations

import json
from dataclasses import dataclass, field

import pytest

from hibiki.boundaries import ProcessResult
from hibiki.evidence import (
    PRODUCER_IDENTITY,
    REPLY_TYPE,
    SNAPSHOT_TYPE,
    EvidenceWorkflowError,
    collect_publication_evidence,
    register_evidence_contracts,
)
from hibiki.records import CausalRepositories, PublicationRecord
from tests.fakes import FakeSekaiGateway

ATTEMPTED_AT = 1_750_000_000_000
NOW_MS = ATTEMPTED_AT + 7 * 24 * 60 * 60 * 1000


@dataclass
class SequenceRunner:
    results: list[ProcessResult]
    calls: list[tuple[tuple[str, ...], float]] = field(default_factory=list)

    def run(self, argv: tuple[str, ...], timeout: float) -> ProcessResult:
        self.calls.append((argv, timeout))
        return self.results.pop(0)


def _json_result(payload: object, *, returncode: int = 0) -> ProcessResult:
    return ProcessResult(returncode, json.dumps(payload), "")


def _posted_publication(gateway: FakeSekaiGateway) -> PublicationRecord:
    repositories = CausalRepositories.create(gateway, "hibiki", clock_ms=lambda: ATTEMPTED_AT)
    return repositories.publications.put(
        PublicationRecord(
            stable_id="owner/repo@abc123",
            proposal_external_id="hibiki.proposal:hibiki:owner/repo@abc123",
            final_text="A grounded post",
            target_account="builder",
            attempted_at=ATTEMPTED_AT,
            status="posted",
            approval_id="approval-1",
            post_id="1900000000000000000",
        )
    )


def _authored_payload() -> dict[str, object]:
    return {
        "ok": True,
        "partial": False,
        "payload": {
            "data": [
                {
                    "id": "1900000000000000000",
                    "public_metrics": {
                        "impression_count": 1200,
                        "like_count": 22,
                        "reply_count": 1,
                        "retweet_count": 4,
                        "quote_count": 2,
                    },
                }
            ]
        },
    }


def _mentions_payload() -> dict[str, object]:
    return {
        "ok": True,
        "partial": False,
        "payload": {
            "data": [
                {
                    "id": "1900000000000000001",
                    "author_id": "user-1",
                    "text": "How does the retry boundary work?",
                    "created_at": "2025-06-23T10:00:00Z",
                    "conversation_id": "1900000000000000000",
                    "referenced_tweets": [
                        {"type": "replied_to", "id": "1900000000000000000"}
                    ],
                    "public_metrics": {
                        "impression_count": 30,
                        "like_count": 3,
                        "reply_count": 1,
                        "retweet_count": 0,
                        "quote_count": 0,
                    },
                },
                {
                    "id": "unrelated",
                    "conversation_id": "another-post",
                    "referenced_tweets": [{"type": "replied_to", "id": "another-post"}],
                },
            ],
            "includes": {"users": [{"id": "user-1", "username": "curious_builder"}]},
        },
    }


def test_registers_a_narrow_birdclaw_producer_and_versioned_schemas() -> None:
    gateway = FakeSekaiGateway()

    result = register_evidence_contracts(gateway, "hibiki", "builder")

    assert result.producer_identity == PRODUCER_IDENTITY
    capability = gateway.evidence_producers[0]
    assert tuple(capability.source_types) == ("birdclaw",)
    assert tuple(capability.source_instances) == ("builder",)
    assert tuple(capability.namespaces) == ("hibiki",)
    assert tuple(capability.target_kinds) == ("hibiki.publication",)
    assert tuple(capability.evidence_types) == (SNAPSHOT_TYPE, REPLY_TYPE)
    assert tuple(capability.allowed_intents) == ("upsert",)
    assert capability.allow_operation_attachment is False
    assert [(item.schema_id, item.schema_version) for item in gateway.evidence_schemas] == [
        (SNAPSHOT_TYPE, "1.0.0"),
        (REPLY_TYPE, "1.0.0"),
    ]


def test_collects_raw_snapshot_and_replies_onto_the_publication() -> None:
    gateway = FakeSekaiGateway()
    publication = _posted_publication(gateway)
    runner = SequenceRunner([_json_result(_authored_payload()), _json_result(_mentions_payload())])

    result = collect_publication_evidence(
        runner,
        gateway,
        publication.external_id,
        "builder",
        "hibiki",
        "7d",
        clock_ms=lambda: NOW_MS,
    )

    assert result.snapshot_deduplicated is False
    assert len(result.reply_submission_ids) == 1
    assert [envelope.evidence_type for envelope in gateway.evidence_envelopes] == [
        SNAPSHOT_TYPE,
        REPLY_TYPE,
    ]
    snapshot, reply = gateway.evidence_envelopes
    assert snapshot.target_external_id == publication.external_id
    assert snapshot.target_kind == "hibiki.publication"
    assert snapshot.source_instance == "builder"
    assert snapshot.idempotency_key.endswith(":1900000000000000000:7d")
    assert json.loads(snapshot.content_json) == {
        "metrics": {
            "impressions": 1200,
            "likes": 22,
            "quotes": 2,
            "replies": 1,
            "reposts": 4,
        },
        "post_id": "1900000000000000000",
        "window": "7d",
    }
    assert json.loads(reply.content_json) == {
        "author_reference": "curious_builder",
        "collected_at_ms": NOW_MS,
        "parent_post_id": "1900000000000000000",
        "public_metrics": {
            "impressions": 30,
            "likes": 3,
            "quotes": 0,
            "replies": 1,
            "reposts": 0,
        },
        "reply_id": "1900000000000000001",
        "text": "How does the retry boundary work?",
    }
    assert all(envelope.content_digest for envelope in gateway.evidence_envelopes)
    assert "digest" not in json.loads(snapshot.content_json)


def test_duplicate_collection_reuses_snapshot_and_reply_submissions() -> None:
    gateway = FakeSekaiGateway()
    publication = _posted_publication(gateway)
    first = SequenceRunner([_json_result(_authored_payload()), _json_result(_mentions_payload())])
    collect_publication_evidence(
        first,
        gateway,
        publication.external_id,
        "builder",
        "hibiki",
        "7d",
        clock_ms=lambda: NOW_MS,
    )
    second = SequenceRunner([_json_result(_mentions_payload())])

    result = collect_publication_evidence(
        second,
        gateway,
        publication.external_id,
        "builder",
        "hibiki",
        "7d",
        clock_ms=lambda: NOW_MS + 1,
    )

    assert result.snapshot_deduplicated is True
    assert result.reply_submission_ids == ()
    assert result.replies_deduplicated == 1
    assert len(gateway.evidence_envelopes) == 2
    assert len(second.calls) == 1
    assert second.calls[0][0][1:3] == ("sync", "mentions")


def test_rejects_partial_birdclaw_data_without_submitting_evidence() -> None:
    gateway = FakeSekaiGateway()
    publication = _posted_publication(gateway)
    partial = _authored_payload() | {"ok": False, "partial": True}

    with pytest.raises(EvidenceWorkflowError, match="incomplete result"):
        collect_publication_evidence(
            SequenceRunner([_json_result(partial, returncode=5)]),
            gateway,
            publication.external_id,
            "builder",
            "hibiki",
            "7d",
            clock_ms=lambda: NOW_MS,
        )

    assert gateway.evidence_envelopes == []


def test_refuses_collection_before_the_requested_window() -> None:
    gateway = FakeSekaiGateway()
    publication = _posted_publication(gateway)

    with pytest.raises(EvidenceWorkflowError, match="24h evidence window has not elapsed"):
        collect_publication_evidence(
            SequenceRunner([]),
            gateway,
            publication.external_id,
            "builder",
            "hibiki",
            "24h",
            clock_ms=lambda: ATTEMPTED_AT + 1,
        )
