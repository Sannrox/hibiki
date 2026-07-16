from __future__ import annotations

import io
import json
import subprocess

from hibiki.boundaries import ProbeResult, ProcessResult
from hibiki.cli import run
from tests.fakes import FakeGrpcHealthProbe, FakeProcessRunner, FakeSekaiGateway


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
) -> tuple[int, dict[str, object], str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    exit_code = run(
        argv,
        environ=environment() if environ is None else environ,
        stdout=stdout,
        stderr=stderr,
        process_runner=process_runner or FakeProcessRunner(),
        grpc_probe=grpc_probe or FakeGrpcHealthProbe(),
        sekai_gateway=sekai_gateway,
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
    assert second_payload["unchanged"] == first_payload["created"]
    assert first_diagnostics == second_diagnostics == ""
