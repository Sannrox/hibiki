from __future__ import annotations

import subprocess
from dataclasses import asdict, dataclass

from hibiki.boundaries import GrpcHealthProbe, ProbeResult, ProcessRunner
from hibiki.config import Settings


@dataclass(frozen=True, slots=True)
class Check:
    name: str
    ok: bool
    detail: str


def run_health_checks(
    settings: Settings,
    process_runner: ProcessRunner,
    grpc_probe: GrpcHealthProbe,
    timeout: float,
) -> list[Check]:
    checks = [Check("configuration", True, "valid")]
    checks.append(_gh_check(process_runner, timeout))
    checks.append(_grpc_check(grpc_probe, settings, "sekai.SekaiService", "sekai", timeout))
    checks.append(_grpc_check(grpc_probe, settings, "chisei.ChiseiService", "chisei", timeout))
    return checks


def serialize_checks(checks: list[Check]) -> list[dict[str, str | bool]]:
    return [asdict(check) for check in checks]


def _gh_check(process_runner: ProcessRunner, timeout: float) -> Check:
    try:
        result = process_runner.run(("gh", "--version"), timeout)
    except (OSError, TimeoutError, subprocess.TimeoutExpired) as error:
        return Check("gh", False, str(error))
    if result.returncode != 0:
        detail = result.stderr.strip() or f"exited with status {result.returncode}"
        return Check("gh", False, detail)
    first_line = result.stdout.partition("\n")[0].strip()
    return Check("gh", True, first_line or "available")


def _grpc_check(
    grpc_probe: GrpcHealthProbe,
    settings: Settings,
    service: str,
    name: str,
    timeout: float,
) -> Check:
    result: ProbeResult = grpc_probe.check(settings.chisei_target, service, timeout)
    return Check(name, result.ok, result.detail)
