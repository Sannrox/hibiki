from __future__ import annotations

import json

import pytest

from hibiki.discovery import discover_public_revision
from hibiki.validation import ClaimValidationError, validate_claims
from tests.fakes import FakeChiseiGateway
from tests.test_discovery import fixture_runner

FINAL_TEXT = "I made retries deterministic by giving each attempt a stable identity."


def validation_response(*, supported: bool = True, claim: str = FINAL_TEXT) -> str:
    return json.dumps(
        {
            "valid": supported,
            "reasoning": "The changed retry implementation supports the claim.",
            "claims": [
                {
                    "text": claim,
                    "supported": supported,
                    "reason": "The patch introduces stable retry identity.",
                    "source_references": (
                        [{"revision": "abc123", "path": "src/retry.py"}] if supported else []
                    ),
                }
            ],
        }
    )


def test_claim_validation_returns_strict_supported_verdict() -> None:
    bundle = discover_public_revision(fixture_runner(), "example/tenkai", "abc123")

    result = validate_claims(FakeChiseiGateway(validation_response()), FINAL_TEXT, bundle)

    assert result.valid is True
    assert result.claims[0].text == FINAL_TEXT
    assert result.claims[0].source_references[0].path == "src/retry.py"


def test_claim_validation_rejects_claim_absent_from_final_text() -> None:
    bundle = discover_public_revision(fixture_runner(), "example/tenkai", "abc123")

    with pytest.raises(ClaimValidationError, match="appear verbatim"):
        validate_claims(
            FakeChiseiGateway(validation_response(claim="An unrelated assertion.")),
            FINAL_TEXT,
            bundle,
        )
