from __future__ import annotations

import json

from hibiki.contracts import sekai_pb2
from hibiki.recommendation import recommend_source
from tests.fakes import FakeChiseiGateway, FakeSekaiGateway
from tests.test_discovery import fixture_runner


def _candidate_response() -> str:
    return json.dumps(
        {
            "candidate": {
                "revision": "abc123",
                "topic": "Deterministic retries",
                "reason": "Concrete invariant with passing tests.",
                "scores": {
                    "usefulness": 90,
                    "novelty": 80,
                    "evidence_strength": 95,
                    "audience_relevance": 85,
                },
            }
        }
    )


def test_recommendation_uses_last_successful_scan_and_records_lineage() -> None:
    sekai = FakeSekaiGateway()
    sekai.record_decision(
        sekai_pb2.Decision(
            id="prior-scan",
            timestamp=100,
            actor="hibiki",
            action="hibiki.source_scan",
            evidence={"scanned_at": "2026-07-16T09:00:00Z"},
            target_id="example/tenkai",
            outcome="success",
        )
    )
    chisei = FakeChiseiGateway(_candidate_response())

    recommendation = recommend_source(
        fixture_runner(),
        sekai,
        chisei,
        "example/tenkai",
        "hibiki",
        clock_ms=lambda: 200,
    )

    assert recommendation.candidate is not None
    assert recommendation.source is not None
    assert recommendation.source.revision == "abc123"
    assert recommendation.operation_id == "operation-1"
    selection = next(
        decision
        for decision in sekai.decisions.values()
        if decision.action == "hibiki.source_selection"
    )
    assert selection.outcome == "selected"
    assert selection.evidence["receipt_json"] == '{"operation_id":"operation-1"}'
    assert selection.evidence["topic"] == "Deterministic retries"
    scans = [
        decision for decision in sekai.decisions.values() if decision.action == "hibiki.source_scan"
    ]
    assert len(scans) == 2
    assert max(scans, key=lambda decision: decision.timestamp).outcome == "success"
