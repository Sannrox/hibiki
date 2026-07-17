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
    sekai.record_decision(
        sekai_pb2.Decision(
            id="prior-selection",
            timestamp=99,
            actor="hibiki",
            action="hibiki.source_selection",
            evidence={"topic": "Prior selected topic"},
            target_id="example/tenkai",
            outcome="selected",
        )
    )
    for index in range(11):
        sekai.record_decision(
            sekai_pb2.Decision(
                id=f"no-candidate-{index}",
                timestamp=101 + index,
                actor="hibiki",
                action="hibiki.source_selection",
                target_id="example/tenkai",
                outcome="no_candidate",
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
    plan_spec = json.loads(chisei.plan_requests[0].input.spec)
    assert plan_spec["recent_topics"] == ["Prior selected topic"]
    selection = next(
        decision
        for decision in sekai.decisions.values()
        if decision.id == recommendation.decision_id
    )
    assert selection.outcome == "selected"
    assert selection.evidence["receipt_json"] == '{"operation_id":"operation-1"}'
    assert selection.evidence["topic"] == "Deterministic retries"
    scans = [
        decision for decision in sekai.decisions.values() if decision.action == "hibiki.source_scan"
    ]
    assert len(scans) == 2
    assert max(scans, key=lambda decision: decision.timestamp).outcome == "success"
