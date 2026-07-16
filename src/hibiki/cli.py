from __future__ import annotations

import json
import os
import sys
from collections.abc import Mapping, Sequence
from typing import TextIO

import grpc

from hibiki.boundaries import (
    GrpcHealthProbe,
    NativeGrpcHealthProbe,
    ProcessRunner,
    SubprocessRunner,
)
from hibiki.config import ConfigurationError, Settings
from hibiki.health import Check, run_health_checks, serialize_checks
from hibiki.schema import SchemaConflictError, register_schema_types
from hibiki.sekai import NativeSekaiGateway, SekaiGateway

USAGE = "usage: hibiki <health|config|schema> [--timeout SECONDS]"


def run(
    argv: Sequence[str],
    *,
    environ: Mapping[str, str],
    stdout: TextIO,
    stderr: TextIO,
    process_runner: ProcessRunner,
    grpc_probe: GrpcHealthProbe,
    sekai_gateway: SekaiGateway | None = None,
) -> int:
    if not argv or argv[0] in {"-h", "--help"}:
        _emit(stdout, {"ok": True, "usage": USAGE})
        return 0

    command = argv[0]
    try:
        timeout = _parse_timeout(argv[1:]) if command == "health" else None
    except ValueError as error:
        return _usage_error(stdout, stderr, str(error))

    if command not in {"health", "config", "schema"}:
        return _usage_error(stdout, stderr, f"unknown command: {command}")
    if command in {"config", "schema"} and len(argv) != 1:
        return _usage_error(stdout, stderr, f"{command} does not accept arguments")

    try:
        settings = Settings.from_environ(environ)
    except ConfigurationError as error:
        checks = [Check("configuration", False, str(error))]
        if command == "health":
            checks.extend(
                [
                    Check("gh", False, "not checked: configuration invalid"),
                    Check("sekai", False, "not checked: configuration invalid"),
                    Check("chisei", False, "not checked: configuration invalid"),
                ]
            )
            _emit(stdout, {"command": command, "ok": False, "checks": serialize_checks(checks)})
        else:
            _emit_error(stdout, command, "invalid_configuration", str(error))
        print(f"hibiki: {error}", file=stderr)
        return 1

    if command == "config":
        _emit(stdout, {"command": command, "ok": True, "configuration": settings.public_dict()})
        return 0

    if command == "schema":
        gateway = sekai_gateway or NativeSekaiGateway(settings.chisei_target)
        try:
            result = register_schema_types(gateway)
        except (SchemaConflictError, grpc.RpcError) as error:
            _emit_error(stdout, command, "schema_registration_failed", str(error))
            print(f"hibiki: schema registration failed: {error}", file=stderr)
            return 1
        _emit(
            stdout,
            {
                "command": command,
                "ok": True,
                "created": result.created,
                "unchanged": result.unchanged,
            },
        )
        return 0

    checks = run_health_checks(settings, process_runner, grpc_probe, timeout or 3.0)
    ok = all(check.ok for check in checks)
    _emit(stdout, {"command": command, "ok": ok, "checks": serialize_checks(checks)})
    if not ok:
        print("hibiki: one or more health checks failed", file=stderr)
    return 0 if ok else 1


def main(argv: Sequence[str] | None = None) -> int:
    return run(
        list(sys.argv[1:] if argv is None else argv),
        environ=os.environ,
        stdout=sys.stdout,
        stderr=sys.stderr,
        process_runner=SubprocessRunner(),
        grpc_probe=NativeGrpcHealthProbe(),
    )


def _parse_timeout(arguments: Sequence[str]) -> float:
    if not arguments:
        return 3.0
    if len(arguments) != 2 or arguments[0] != "--timeout":
        raise ValueError("health accepts only --timeout SECONDS")
    try:
        timeout = float(arguments[1])
    except ValueError as error:
        raise ValueError("timeout must be a number") from error
    if not 0 < timeout <= 60:
        raise ValueError("timeout must be greater than 0 and at most 60 seconds")
    return timeout


def _usage_error(stdout: TextIO, stderr: TextIO, message: str) -> int:
    _emit_error(stdout, "dispatch", "usage", message)
    print(f"hibiki: {message}; {USAGE}", file=stderr)
    return 2


def _emit_error(stdout: TextIO, command: str, code: str, message: str) -> None:
    _emit(stdout, {"command": command, "ok": False, "error": {"code": code, "message": message}})


def _emit(stdout: TextIO, payload: object) -> None:
    json.dump(payload, stdout, sort_keys=True, separators=(",", ":"))
    stdout.write("\n")
