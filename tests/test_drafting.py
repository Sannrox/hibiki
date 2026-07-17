from __future__ import annotations

import json

import pytest

from hibiki.discovery import discover_public_revision
from hibiki.drafting import DraftingError, generate_draft
from tests.fakes import FakeChiseiGateway
from tests.test_discovery import fixture_runner


def draft_response(*, path: str = "src/retry.py") -> str:
    draft = "I made retries deterministic by giving each attempt a stable identity."
    return json.dumps(
        {
            "draft": draft,
            "reasoning": "The implementation exposes a reusable retry invariant.",
            "claims": [
                {
                    "text": draft,
                    "source_references": [{"revision": "abc123", "path": path}],
                }
            ],
        }
    )


def test_governed_draft_returns_claims_bounded_to_selected_evidence() -> None:
    bundle = discover_public_revision(fixture_runner(), "example/tenkai", "abc123")
    gateway = FakeChiseiGateway(draft_response())

    result = generate_draft(gateway, bundle)

    assert result.draft.startswith("I made retries deterministic")
    assert result.claims[0].source_references[0].path == "src/retry.py"
    assert result.receipt_complete is True
    request = gateway.plan_requests[0].input
    assert request.task_type == "standalone_post_drafting"
    assert json.loads(request.spec)["evidence_bundle"]["commits"][0]["revision"] == "abc123"


def test_governed_draft_rejects_reference_outside_selected_evidence() -> None:
    bundle = discover_public_revision(fixture_runner(), "example/tenkai", "abc123")

    with pytest.raises(DraftingError, match="outside the evidence bundle"):
        generate_draft(FakeChiseiGateway(draft_response(path="private/notes.md")), bundle)


def test_governed_draft_rejects_omitted_changed_file_as_evidence() -> None:
    bundle = discover_public_revision(fixture_runner(), "example/tenkai", "abc123")

    with pytest.raises(DraftingError, match="outside the evidence bundle"):
        generate_draft(FakeChiseiGateway(draft_response(path="uv.lock")), bundle)
