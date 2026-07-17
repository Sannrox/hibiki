from __future__ import annotations

import json
from dataclasses import replace

import pytest

from hibiki.discovery import EvidenceBundle
from hibiki.selection import SelectionError, commit_evidence_hash, select_candidate
from tests.fakes import FakeChiseiGateway


def bundle() -> EvidenceBundle:
    return EvidenceBundle(
        repository="example/tenkai",
        default_branch="main",
        scanned_at="2026-07-17T09:00:00Z",
        since="2026-07-16T09:00:00Z",
        commits=(
            {
                "revision": "abc123",
                "message": "Make retries deterministic",
                "public_url": "https://github.com/example/tenkai/commit/abc123",
                "changed_files": ["src/retry.py"],
                "patches": [{"path": "src/retry.py", "patch": "+bounded"}],
                "checks": [{"name": "test", "status": "completed", "conclusion": "success"}],
                "documents": [],
            },
        ),
        omissions=(),
        content_hash="a" * 64,
    )


def candidate_response(*, topic: str = "Deterministic retries", revision: str = "abc123") -> str:
    return json.dumps(
        {
            "candidate": {
                "revision": revision,
                "topic": topic,
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


def test_governed_selection_returns_one_bundled_candidate_and_receipt() -> None:
    gateway = FakeChiseiGateway(candidate_response())

    result = select_candidate(gateway, bundle(), (), namespace="sandbox")

    assert result.candidate is not None
    assert result.candidate.revision == "abc123"
    assert result.operation_id == "operation-1"
    assert result.receipt_complete is True
    assert gateway.plan_requests[0].input.namespace == "sandbox"
    spec = json.loads(gateway.plan_requests[0].input.spec)
    assert spec["recent_topics"] == []
    assert spec["evidence_bundle"]["content_hash"] == "a" * 64
    assert gateway.receipt_requests[0].operation_id == "operation-1"


def test_explicit_no_candidate_is_a_valid_result() -> None:
    gateway = FakeChiseiGateway(
        json.dumps({"candidate": None, "reason": "No commit passes every eligibility rule."})
    )

    result = select_candidate(gateway, bundle(), ())

    assert result.candidate is None
    assert result.reason == "No commit passes every eligibility rule."


def test_repeat_topic_is_rejected_even_if_model_selects_it() -> None:
    gateway = FakeChiseiGateway(candidate_response(topic="Deterministic-retries!"))

    result = select_candidate(gateway, bundle(), ("deterministic retries",))

    assert result.candidate is None
    assert result.reason == "repeat topic rejected: Deterministic-retries!"


def test_candidate_must_reference_evidence_bundle() -> None:
    gateway = FakeChiseiGateway(candidate_response(revision="outside456"))

    with pytest.raises(SelectionError, match="outside the evidence bundle"):
        select_candidate(gateway, bundle(), ())

    assert gateway.receipt_requests == []


def test_no_candidate_requires_explicit_null_candidate_field() -> None:
    gateway = FakeChiseiGateway(json.dumps({"reason": "Nothing eligible."}))

    with pytest.raises(SelectionError, match="missing candidate"):
        select_candidate(gateway, bundle(), ())


def test_source_evidence_identity_ignores_mutable_check_state() -> None:
    original = bundle()
    changed_commit = dict(original.commits[0])
    changed_commit["checks"] = [{"name": "test", "status": "completed", "conclusion": "failure"}]
    changed = replace(original, commits=(changed_commit,))

    assert commit_evidence_hash(original, "abc123") == commit_evidence_hash(changed, "abc123")
