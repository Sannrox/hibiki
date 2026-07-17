from __future__ import annotations

import json

import pytest

from hibiki.discovery import discover_public_revision
from hibiki.validation import ClaimValidationError, inventory_claims, validate_claims
from tests.fakes import FakeChiseiGateway
from tests.test_discovery import fixture_runner

FINAL_TEXT = "I made retries deterministic by giving each attempt a stable identity."


def validation_response(
    *,
    supported: bool = True,
    claim: str = FINAL_TEXT,
    undeclared_claims: tuple[str, ...] = (),
) -> str:
    return json.dumps(
        {
            "valid": supported and not undeclared_claims,
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
            "undeclared_claims": list(undeclared_claims),
        }
    )


def inventory_response(*claims: str) -> str:
    return json.dumps({"claims": list(claims or (FINAL_TEXT,))})


def test_claim_validation_returns_strict_supported_verdict() -> None:
    bundle = discover_public_revision(fixture_runner(), "example/tenkai", "abc123")

    result = validate_claims(
        FakeChiseiGateway(validation_response()),
        FINAL_TEXT,
        bundle,
        expected_claims=(FINAL_TEXT,),
    )

    assert result.valid is True
    assert result.claims[0].text == FINAL_TEXT
    assert result.claims[0].source_references[0].path == "src/retry.py"


def test_claim_inventory_returns_verbatim_unique_claims() -> None:
    result = inventory_claims(
        FakeChiseiGateway(inventory_response()),
        FINAL_TEXT,
        discover_public_revision(fixture_runner(), "example/tenkai", "abc123"),
    )

    assert result.claims == (FINAL_TEXT,)


def test_claim_validation_rejects_claim_absent_from_final_text() -> None:
    bundle = discover_public_revision(fixture_runner(), "example/tenkai", "abc123")

    with pytest.raises(ClaimValidationError, match="appear verbatim"):
        validate_claims(
            FakeChiseiGateway(validation_response(claim="An unrelated assertion.")),
            FINAL_TEXT,
            bundle,
            expected_claims=(FINAL_TEXT,),
        )


def test_claim_validation_rejects_omitted_expected_claim() -> None:
    text = FINAL_TEXT + " It also guarantees zero failures."
    with pytest.raises(ClaimValidationError, match="omitted or added"):
        validate_claims(
            FakeChiseiGateway(validation_response()),
            text,
            discover_public_revision(fixture_runner(), "example/tenkai", "abc123"),
            expected_claims=(FINAL_TEXT, "It also guarantees zero failures."),
        )


def test_claim_validation_fails_closed_on_undeclared_factual_claim() -> None:
    extra_claim = "It also guarantees zero failures."
    result = validate_claims(
        FakeChiseiGateway(validation_response(undeclared_claims=(extra_claim,))),
        FINAL_TEXT + " " + extra_claim,
        discover_public_revision(fixture_runner(), "example/tenkai", "abc123"),
        expected_claims=(FINAL_TEXT,),
    )

    assert result.valid is False
    assert result.undeclared_claims == (extra_claim,)
