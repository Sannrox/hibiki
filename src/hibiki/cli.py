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
from hibiki.chisei import ChiseiGateway, NativeChiseiGateway
from hibiki.config import ConfigurationError, Settings
from hibiki.discovery import DiscoveryError
from hibiki.drafting import DraftingError
from hibiki.health import Check, run_health_checks, serialize_checks
from hibiki.proposals import ProposalWorkflowError, draft_source
from hibiki.recommendation import recommend_source
from hibiki.records import RecordConflictError, RecordValidationError
from hibiki.schema import SchemaConflictError, register_schema_types
from hibiki.sekai import NativeSekaiGateway, SekaiGateway
from hibiki.selection import SelectionError
from hibiki.validation import ClaimValidationError

USAGE = "usage: hibiki <health|config|schema|recommend|draft SOURCE_ID> [--timeout SECONDS]"


def run(
    argv: Sequence[str],
    *,
    environ: Mapping[str, str],
    stdout: TextIO,
    stderr: TextIO,
    process_runner: ProcessRunner,
    grpc_probe: GrpcHealthProbe,
    sekai_gateway: SekaiGateway | None = None,
    chisei_gateway: ChiseiGateway | None = None,
) -> int:
    if not argv or argv[0] in {"-h", "--help"}:
        _emit(stdout, {"ok": True, "usage": USAGE})
        return 0

    command = argv[0]
    try:
        timeout = _parse_timeout(argv[1:]) if command == "health" else None
    except ValueError as error:
        return _usage_error(stdout, stderr, str(error))

    if command not in {"health", "config", "schema", "recommend", "draft"}:
        return _usage_error(stdout, stderr, f"unknown command: {command}")
    if command in {"config", "schema", "recommend"} and len(argv) != 1:
        return _usage_error(stdout, stderr, f"{command} does not accept arguments")
    if command == "draft" and len(argv) != 2:
        return _usage_error(stdout, stderr, "draft requires SOURCE_ID")

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

    if command == "recommend":
        sekai = sekai_gateway or NativeSekaiGateway(settings.chisei_target)
        chisei = chisei_gateway or NativeChiseiGateway(settings.chisei_target)
        try:
            result = recommend_source(
                process_runner,
                sekai,
                chisei,
                settings.tenkai_repository,
                settings.namespace,
            )
        except (
            DiscoveryError,
            SelectionError,
            RecordConflictError,
            RecordValidationError,
            grpc.RpcError,
        ) as error:
            _emit_error(stdout, command, "recommendation_failed", str(error))
            print(f"hibiki: recommendation failed: {error}", file=stderr)
            return 1
        candidate = None
        if result.candidate is not None and result.source is not None:
            candidate = {
                "revision": result.candidate.revision,
                "topic": result.candidate.topic,
                "reason": result.candidate.reason,
                "scores": result.candidate.scores,
                "source_external_id": result.source.external_id,
                "public_url": result.source.public_url,
                "evidence_hash": result.source.evidence_hash,
            }
        _emit(
            stdout,
            {
                "command": command,
                "ok": True,
                "candidate": candidate,
                "reason": result.reason,
                "decision_id": result.decision_id,
                "operation_id": result.operation_id,
                "operation_receipt": {
                    "complete": result.receipt_complete,
                    "missing_surfaces": result.missing_surfaces,
                },
                "scanned_at": result.scanned_at,
            },
        )
        return 0

    if command == "draft":
        sekai = sekai_gateway or NativeSekaiGateway(settings.chisei_target)
        chisei = chisei_gateway or NativeChiseiGateway(settings.chisei_target)
        try:
            result = draft_source(
                process_runner,
                sekai,
                chisei,
                argv[1],
                settings.namespace,
            )
        except (
            DiscoveryError,
            DraftingError,
            ClaimValidationError,
            ProposalWorkflowError,
            RecordConflictError,
            RecordValidationError,
            grpc.RpcError,
        ) as error:
            _emit_error(stdout, command, "draft_failed", str(error))
            print(f"hibiki: draft failed: {error}", file=stderr)
            return 1
        _emit(
            stdout,
            {
                "command": command,
                "ok": True,
                "proposal_external_id": result.proposal.external_id,
                "draft": result.proposal.draft,
                "draft_hash": result.proposal.draft_hash,
                "reasoning": result.reasoning,
                "claims": [
                    {
                        "text": claim.text,
                        "source_references": [
                            {"revision": reference.revision, "path": reference.path}
                            for reference in claim.source_references
                        ],
                    }
                    for claim in result.claims
                ],
                "source_references": [
                    {"revision": reference.revision, "path": reference.path}
                    for reference in result.source_references
                ],
                "operation_id": result.operation_id,
                "operation_receipt": {
                    "complete": result.receipt_complete,
                    "missing_surfaces": result.missing_surfaces,
                },
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
