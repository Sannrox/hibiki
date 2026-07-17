from __future__ import annotations

import io
import json
import subprocess

import pytest

from hibiki.boundaries import ProbeResult, ProcessResult
from hibiki.cli import run
from hibiki.contracts import sekai_pb2
from tests.fakes import (
    FakeChiseiGateway,
    FakeGrpcHealthProbe,
    FakeProcessRunner,
    FakeSekaiGateway,
)
from tests.test_discovery import fixture_runner


def environment() -> dict[str, str]:
    return {
        "HIBIKI_TENKAI_REPOSITORY": "example/tenkai",
        "HIBIKI_BIRDCLAW_ACCOUNT": "builder",
        "HIBIKI_CHISEI_TARGET": "127.0.0.1:50051",
    }


def invoke(
    argv: list[str],
    *,
    environ: dict[str, str] | None = None,
    process_runner: FakeProcessRunner | None = None,
    grpc_probe: FakeGrpcHealthProbe | None = None,
    sekai_gateway: FakeSekaiGateway | None = None,
    chisei_gateway: FakeChiseiGateway | None = None,
    stdin_payload: object | None = None,
) -> tuple[int, dict[str, object], str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    exit_code = run(
        argv,
        environ=environment() if environ is None else environ,
        stdout=stdout,
        stderr=stderr,
        stdin=io.StringIO("" if stdin_payload is None else json.dumps(stdin_payload)),
        process_runner=process_runner or FakeProcessRunner(),
        grpc_probe=grpc_probe or FakeGrpcHealthProbe(),
        sekai_gateway=sekai_gateway,
        chisei_gateway=chisei_gateway,
    )
    return exit_code, json.loads(stdout.getvalue()), stderr.getvalue()


def test_health_reports_dependencies_through_fake_boundaries() -> None:
    process_runner = FakeProcessRunner()
    grpc_probe = FakeGrpcHealthProbe()

    exit_code, payload, diagnostics = invoke(
        ["health", "--timeout", "1.5"],
        process_runner=process_runner,
        grpc_probe=grpc_probe,
    )

    assert exit_code == 0
    assert payload["ok"] is True
    assert diagnostics == ""
    assert process_runner.calls == [(("gh", "--version"), 1.5)]
    assert grpc_probe.calls == [
        ("127.0.0.1:50051", "sekai.SekaiService", 1.5),
        ("127.0.0.1:50051", "chisei.ChiseiService", 1.5),
    ]


def test_health_failure_stays_structured_and_uses_stderr_for_diagnostics() -> None:
    process_runner = FakeProcessRunner(ProcessResult(1, "", "gh unavailable"))
    grpc_probe = FakeGrpcHealthProbe(
        {"chisei.ChiseiService": ProbeResult(False, "UNAVAILABLE: connection refused")}
    )

    exit_code, payload, diagnostics = invoke(
        ["health"], process_runner=process_runner, grpc_probe=grpc_probe
    )

    assert exit_code == 1
    assert payload["ok"] is False
    checks = {check["name"]: check for check in payload["checks"]}
    assert checks["gh"]["detail"] == "gh unavailable"
    assert checks["chisei"]["ok"] is False
    assert diagnostics == "hibiki: one or more health checks failed\n"


def test_process_timeout_becomes_a_failed_health_check() -> None:
    class TimeoutRunner(FakeProcessRunner):
        def run(self, argv: tuple[str, ...], timeout: float) -> ProcessResult:
            raise subprocess.TimeoutExpired(argv, timeout)

    exit_code, payload, diagnostics = invoke(["health"], process_runner=TimeoutRunner())

    assert exit_code == 1
    checks = {check["name"]: check for check in payload["checks"]}
    assert checks["gh"]["ok"] is False
    assert "timed out" in checks["gh"]["detail"]
    assert diagnostics == "hibiki: one or more health checks failed\n"


def test_invalid_configuration_does_not_touch_dependencies() -> None:
    process_runner = FakeProcessRunner()
    grpc_probe = FakeGrpcHealthProbe()

    exit_code, payload, diagnostics = invoke(
        ["health"], environ={}, process_runner=process_runner, grpc_probe=grpc_probe
    )

    assert exit_code == 1
    assert payload["ok"] is False
    assert process_runner.calls == []
    assert grpc_probe.calls == []
    assert "HIBIKI_TENKAI_REPOSITORY is required" in diagnostics


def test_config_reports_only_non_secret_settings() -> None:
    exit_code, payload, diagnostics = invoke(["config"])

    assert exit_code == 0
    assert payload == {
        "command": "config",
        "ok": True,
        "configuration": {
            "allow_live_writes": False,
            "birdclaw_account": "builder",
            "chisei_target": "127.0.0.1:50051",
            "namespace": "hibiki",
            "tenkai_repository": "example/tenkai",
        },
    }
    assert diagnostics == ""


def test_usage_errors_are_json_on_stdout() -> None:
    exit_code, payload, diagnostics = invoke(["unknown"])

    assert exit_code == 2
    assert payload["error"]["code"] == "usage"
    assert diagnostics.startswith("hibiki: unknown command")


def test_schema_command_reports_created_and_unchanged_types() -> None:
    gateway = FakeSekaiGateway()

    first_code, first_payload, first_diagnostics = invoke(["schema"], sekai_gateway=gateway)
    second_code, second_payload, second_diagnostics = invoke(["schema"], sekai_gateway=gateway)

    assert first_code == second_code == 0
    assert first_payload["ok"] is True
    assert first_payload["created"] == [
        "hibiki.source",
        "hibiki.proposal",
        "hibiki.publication",
        "hibiki.outcome",
        "hibiki.hypothesis",
    ]
    assert second_payload["created"] == []
    assert first_payload["updated"] == second_payload["updated"] == []
    assert second_payload["unchanged"] == first_payload["created"]
    assert first_diagnostics == second_diagnostics == ""


def test_recommend_command_returns_grounded_candidate_and_receipt_status() -> None:
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
    chisei = FakeChiseiGateway(
        json.dumps(
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
    )

    exit_code, payload, diagnostics = invoke(
        ["recommend"],
        process_runner=fixture_runner(),  # type: ignore[arg-type]
        sekai_gateway=sekai,
        chisei_gateway=chisei,
    )

    assert exit_code == 0
    assert payload["candidate"]["revision"] == "abc123"
    assert payload["candidate"]["public_url"].endswith("/commit/abc123")
    assert payload["operation_receipt"] == {"complete": True, "missing_surfaces": []}
    assert diagnostics == ""


def test_draft_command_returns_proposal_claims_and_source_references() -> None:
    runner = fixture_runner()
    from hibiki.discovery import discover_public_revision
    from hibiki.records import CausalRepositories, SourceRecord
    from hibiki.selection import commit_evidence_hash
    from tests.test_drafting import draft_response
    from tests.test_validation import validation_response

    bundle = discover_public_revision(runner, "example/tenkai", "abc123")
    sekai = FakeSekaiGateway()
    source = CausalRepositories.create(sekai, "hibiki").sources.put(
        SourceRecord(
            stable_id="example/tenkai@abc123",
            repository="example/tenkai",
            revision="abc123",
            public_url="https://github.com/example/tenkai/commit/abc123",
            evidence_hash=commit_evidence_hash(bundle, "abc123"),
        )
    )

    exit_code, payload, diagnostics = invoke(
        ["draft", source.external_id],
        process_runner=fixture_runner(),  # type: ignore[arg-type]
        sekai_gateway=sekai,
        chisei_gateway=FakeChiseiGateway((draft_response(), validation_response())),
    )

    assert exit_code == 0
    assert payload["proposal_external_id"].startswith("hibiki.proposal:hibiki:")
    assert payload["claims"][0]["source_references"] == [
        {"revision": "abc123", "path": "src/retry.py"}
    ]
    assert payload["source_references"] == payload["claims"][0]["source_references"]
    assert diagnostics == ""


def test_validate_and_approve_commands_bind_exact_edited_text_hash() -> None:
    from hibiki.discovery import discover_public_revision
    from hibiki.proposals import draft_source
    from hibiki.records import CausalRepositories, SourceRecord
    from hibiki.selection import commit_evidence_hash
    from tests.test_drafting import draft_response
    from tests.test_validation import inventory_response, validation_response

    bundle = discover_public_revision(fixture_runner(), "example/tenkai", "abc123")
    sekai = FakeSekaiGateway()
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
    edited_text = "I made retries deterministic with a stable identity for each attempt."

    validate_code, validate_payload, validate_diagnostics = invoke(
        ["validate", drafted.proposal.external_id],
        process_runner=fixture_runner(),  # type: ignore[arg-type]
        sekai_gateway=sekai,
        chisei_gateway=FakeChiseiGateway(
            (inventory_response(edited_text), validation_response(claim=edited_text))
        ),
        stdin_payload={"final_text": edited_text},
    )
    approve_code, approve_payload, approve_diagnostics = invoke(
        ["approve", drafted.proposal.external_id],
        sekai_gateway=sekai,
        stdin_payload={"final_text_hash": validate_payload["final_text_hash"]},
    )

    assert validate_code == approve_code == 0
    assert validate_payload["status"] == "drafted"
    assert approve_payload["status"] == "approved"
    assert approve_payload["final_text_hash"] == validate_payload["final_text_hash"]
    assert validate_diagnostics == approve_diagnostics == ""


def test_publish_command_returns_read_back_post_identifier() -> None:
    from tests.test_publication import (
        BirdClawRunner,
        _approved_proposal,
        _authored_post,
        _result,
        _sync_result,
    )

    sekai = FakeSekaiGateway()
    proposal = _approved_proposal(sekai)
    runner = BirdClawRunner(
        [
            _result({"ok": True, "tweetId": "tweet_local"}),
            _sync_result([_authored_post(proposal, "1900000000000000000")]),
        ]
    )

    exit_code, payload, diagnostics = invoke(
        ["publish", proposal.external_id],
        environ=environment() | {"HIBIKI_ALLOW_LIVE_WRITES": "true"},
        process_runner=runner,  # type: ignore[arg-type]
        sekai_gateway=sekai,
    )

    assert exit_code == 0
    assert payload["proposal_status"] == "published"
    assert payload["publication_status"] == "posted"
    assert payload["post_id"] == "1900000000000000000"
    assert payload["target_account"] == "builder"
    assert payload["reconciled"] is False
    assert diagnostics == ""


def test_publish_command_is_write_disabled_in_ci() -> None:
    from tests.test_publication import BirdClawRunner, _approved_proposal

    sekai = FakeSekaiGateway()
    proposal = _approved_proposal(sekai)
    runner = BirdClawRunner([])

    exit_code, payload, diagnostics = invoke(
        ["publish", proposal.external_id],
        environ=environment()
        | {"HIBIKI_ALLOW_LIVE_WRITES": "true", "CI": "true"},
        process_runner=runner,  # type: ignore[arg-type]
        sekai_gateway=sekai,
    )

    assert exit_code == 1
    assert payload["error"]["code"] == "publication_failed"
    assert "live publication is disabled" in payload["error"]["message"]
    assert runner.calls == []
    assert "publication failed" in diagnostics


def test_publish_reconciliation_emits_structured_error_when_birdclaw_is_missing() -> None:
    from hibiki.publication import PublicationWorkflowError
    from tests.test_publication import (
        BirdClawRunner,
        _approved_proposal,
        _publish,
        _result,
    )

    class MissingBirdClawRunner:
        def run(self, argv: tuple[str, ...], timeout: float) -> ProcessResult:
            raise FileNotFoundError("birdclaw")

    sekai = FakeSekaiGateway()
    proposal = _approved_proposal(sekai)
    with pytest.raises(PublicationWorkflowError):
        _publish(
            BirdClawRunner([_result({}, returncode=4, stderr="connection lost")]),
            sekai,
            proposal,
        )

    exit_code, payload, diagnostics = invoke(
        ["publish", proposal.external_id],
        environ=environment() | {"HIBIKI_ALLOW_LIVE_WRITES": "true"},
        process_runner=MissingBirdClawRunner(),  # type: ignore[arg-type]
        sekai_gateway=sekai,
    )

    assert exit_code == 1
    assert payload["error"]["code"] == "publication_failed"
    assert "could not start" in payload["error"]["message"]
    assert "publication failed" in diagnostics
