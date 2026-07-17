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
from hibiki.evidence import (
    EvidenceWorkflowError,
    collect_publication_evidence,
    register_evidence_contracts,
)
from hibiki.health import Check, run_health_checks, serialize_checks
from hibiki.learning import (
    LearningWorkflowError,
    evaluate_strategy,
    surface_hypotheses,
    update_hypothesis_status,
)
from hibiki.outcomes import (
    OutcomeWorkflowError,
    ReplyClassification,
    build_outcome_report,
    classify_replies,
    confirm_classification,
)
from hibiki.proposals import (
    ProposalWorkflowError,
    approve_proposal,
    draft_source,
    validate_proposal_edit,
)
from hibiki.publication import PublicationWorkflowError, publish_proposal
from hibiki.recommendation import recommend_source
from hibiki.records import RecordConflictError, RecordValidationError, sha256_text
from hibiki.schema import SchemaConflictError, register_schema_types
from hibiki.sekai import NativeSekaiGateway, SekaiGateway
from hibiki.selection import SelectionError
from hibiki.validation import ClaimValidationError

USAGE = (
    "usage: hibiki <health|config|schema|recommend|draft SOURCE_ID|"
    "validate PROPOSAL_ID|approve PROPOSAL_ID|publish PROPOSAL_ID|"
    "collect PUBLICATION_ID 24h|7d|classify PUBLICATION_ID|"
    "confirm REPLY_SUBMISSION_ID CATEGORY|outcome PUBLICATION_ID 24h|7d|"
    "hypothesize PUBLICATION_ID|strategy|"
    "hypothesis-status HYPOTHESIS_ID STATUS> "
    "[--timeout SECONDS]"
)


def run(
    argv: Sequence[str],
    *,
    environ: Mapping[str, str],
    stdout: TextIO,
    stderr: TextIO,
    stdin: TextIO,
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

    if command not in {
        "health",
        "config",
        "schema",
        "recommend",
        "draft",
        "validate",
        "approve",
        "publish",
        "collect",
        "classify",
        "confirm",
        "outcome",
        "hypothesize",
        "strategy",
        "hypothesis-status",
    }:
        return _usage_error(stdout, stderr, f"unknown command: {command}")
    if command in {"config", "schema", "recommend", "strategy"} and len(argv) != 1:
        return _usage_error(stdout, stderr, f"{command} does not accept arguments")
    if command == "draft" and len(argv) != 2:
        return _usage_error(stdout, stderr, "draft requires SOURCE_ID")
    if command in {"validate", "approve", "publish"} and len(argv) != 2:
        return _usage_error(stdout, stderr, f"{command} requires PROPOSAL_ID")
    if command == "collect" and (len(argv) != 3 or argv[2] not in {"24h", "7d"}):
        return _usage_error(stdout, stderr, "collect requires PUBLICATION_ID and 24h or 7d")
    if command == "classify" and len(argv) != 2:
        return _usage_error(stdout, stderr, "classify requires PUBLICATION_ID")
    if command == "confirm" and len(argv) != 3:
        return _usage_error(stdout, stderr, "confirm requires REPLY_SUBMISSION_ID and CATEGORY")
    if command == "outcome" and (len(argv) != 3 or argv[2] not in {"24h", "7d"}):
        return _usage_error(stdout, stderr, "outcome requires PUBLICATION_ID and 24h or 7d")
    if command == "hypothesize" and len(argv) != 2:
        return _usage_error(stdout, stderr, "hypothesize requires PUBLICATION_ID")
    if command == "hypothesis-status" and (
        len(argv) != 3 or argv[2] not in {"accepted", "rejected", "retired"}
    ):
        return _usage_error(
            stdout, stderr, "hypothesis-status requires HYPOTHESIS_ID and accepted|rejected|retired"
        )

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
            evidence = register_evidence_contracts(
                gateway, settings.namespace, settings.birdclaw_account
            )
        except (SchemaConflictError, EvidenceWorkflowError, grpc.RpcError) as error:
            _emit_error(stdout, command, "schema_registration_failed", str(error))
            print(f"hibiki: schema registration failed: {error}", file=stderr)
            return 1
        _emit(
            stdout,
            {
                "command": command,
                "ok": True,
                "created": result.created,
                "updated": result.updated,
                "unchanged": result.unchanged,
                "evidence_producer": evidence.producer_identity,
                "evidence_schemas": evidence.evidence_types,
            },
        )
        return 0

    if command == "collect":
        sekai = sekai_gateway or NativeSekaiGateway(settings.chisei_target)
        try:
            result = collect_publication_evidence(
                process_runner,
                sekai,
                argv[1],
                settings.birdclaw_account,
                settings.namespace,
                argv[2],
            )
        except (
            EvidenceWorkflowError,
            RecordConflictError,
            RecordValidationError,
            grpc.RpcError,
        ) as error:
            _emit_error(stdout, command, "evidence_collection_failed", str(error))
            print(f"hibiki: evidence collection failed: {error}", file=stderr)
            return 1
        _emit(
            stdout,
            {
                "command": command,
                "ok": True,
                "publication_external_id": result.publication_external_id,
                "post_id": result.post_id,
                "window": result.window,
                "snapshot_submission_id": result.snapshot_submission_id,
                "snapshot_deduplicated": result.snapshot_deduplicated,
                "reply_submission_ids": result.reply_submission_ids,
                "replies_deduplicated": result.replies_deduplicated,
            },
        )
        return 0

    if command == "classify":
        sekai = sekai_gateway or NativeSekaiGateway(settings.chisei_target)
        chisei = chisei_gateway or NativeChiseiGateway(settings.chisei_target)
        try:
            result = classify_replies(sekai, chisei, argv[1], settings.namespace)
        except (OutcomeWorkflowError, RecordValidationError, grpc.RpcError) as error:
            _emit_error(stdout, command, "classification_failed", str(error))
            print(f"hibiki: classification failed: {error}", file=stderr)
            return 1
        _emit(
            stdout,
            {
                "command": command,
                "ok": True,
                "publication_external_id": result.publication_external_id,
                "confirmed_count": result.confirmed_count,
                "calibrated": result.calibrated,
                "classifications": [_classification_dict(item) for item in result.classifications],
            },
        )
        return 0

    if command == "confirm":
        sekai = sekai_gateway or NativeSekaiGateway(settings.chisei_target)
        try:
            result = confirm_classification(sekai, argv[1], argv[2])
        except (OutcomeWorkflowError, grpc.RpcError) as error:
            _emit_error(stdout, command, "confirmation_failed", str(error))
            print(f"hibiki: confirmation failed: {error}", file=stderr)
            return 1
        _emit(
            stdout,
            {
                "command": command,
                "ok": True,
                "submission_id": result.submission_id,
                "predicted_category": result.predicted_category,
                "confirmed_category": result.confirmed_category,
                "corrected": result.corrected,
                "confirmed_count": result.confirmed_count,
                "calibrated": result.calibrated,
            },
        )
        return 0

    if command == "outcome":
        sekai = sekai_gateway or NativeSekaiGateway(settings.chisei_target)
        chisei = chisei_gateway or NativeChiseiGateway(settings.chisei_target)
        try:
            result = build_outcome_report(sekai, chisei, argv[1], argv[2], settings.namespace)
        except (
            OutcomeWorkflowError,
            RecordConflictError,
            RecordValidationError,
            grpc.RpcError,
        ) as error:
            _emit_error(stdout, command, "outcome_reporting_failed", str(error))
            print(f"hibiki: outcome reporting failed: {error}", file=stderr)
            return 1
        _emit(
            stdout,
            {
                "command": command,
                "ok": True,
                "status": result.status,
                "window": result.outcome.window,
                "observed_at": result.outcome.observed_at,
                "metrics": result.outcome.metrics,
                "qualified_replies": result.outcome.qualified_replies,
                "classifications": [_classification_dict(item) for item in result.classifications],
                "lineage": result.lineage,
            },
        )
        return 0

    if command == "hypothesize":
        sekai = sekai_gateway or NativeSekaiGateway(settings.chisei_target)
        chisei = chisei_gateway or NativeChiseiGateway(settings.chisei_target)
        try:
            result = surface_hypotheses(sekai, chisei, argv[1], settings.namespace)
        except (
            LearningWorkflowError,
            RecordConflictError,
            RecordValidationError,
            grpc.RpcError,
        ) as error:
            _emit_error(stdout, command, "hypothesis_surfacing_failed", str(error))
            print(f"hibiki: hypothesis surfacing failed: {error}", file=stderr)
            return 1
        _emit(
            stdout,
            {
                "command": command,
                "ok": True,
                "comparable_posts": result.comparable_posts,
                "operation_id": result.operation_id,
                "hypotheses": [
                    {
                        "stable_id": item.stable_id,
                        "statement": item.statement,
                        "evidence_external_ids": list(item.evidence_external_ids),
                        "status": item.status,
                    }
                    for item in result.hypotheses
                ],
            },
        )
        return 0

    if command == "strategy":
        sekai = sekai_gateway or NativeSekaiGateway(settings.chisei_target)
        chisei = chisei_gateway or NativeChiseiGateway(settings.chisei_target)
        try:
            result = evaluate_strategy(sekai, chisei, settings.namespace)
        except (
            LearningWorkflowError,
            RecordConflictError,
            RecordValidationError,
            grpc.RpcError,
        ) as error:
            _emit_error(stdout, command, "strategy_evaluation_failed", str(error))
            print(f"hibiki: strategy evaluation failed: {error}", file=stderr)
            return 1
        _emit(
            stdout,
            {
                "command": command,
                "ok": True,
                "comparable_posts": result.comparable_posts,
                "periods": result.periods,
                "operation_id": result.operation_id,
                "recommendations": [
                    {
                        "hypothesis_external_id": item.hypothesis_external_id,
                        "statement": item.statement,
                        "recommendation": item.recommendation,
                        "confidence_bps": item.confidence_bps,
                        "posts_evaluated": item.posts_evaluated,
                        "periods_covered": item.periods_covered,
                        "actionable": item.actionable,
                    }
                    for item in result.recommendations
                ],
                "gated_hypotheses": [
                    {
                        "hypothesis_external_id": item.hypothesis_external_id,
                        "statement": item.statement,
                        "reason": item.reason,
                        "posts_evaluated": item.posts_evaluated,
                        "periods_covered": item.periods_covered,
                    }
                    for item in result.gated_hypotheses
                ],
            },
        )
        return 0

    if command == "hypothesis-status":
        sekai = sekai_gateway or NativeSekaiGateway(settings.chisei_target)
        try:
            result = update_hypothesis_status(sekai, argv[1], argv[2], settings.namespace)
        except (
            LearningWorkflowError,
            RecordConflictError,
            RecordValidationError,
            grpc.RpcError,
        ) as error:
            _emit_error(stdout, command, "hypothesis_status_failed", str(error))
            print(f"hibiki: hypothesis status update failed: {error}", file=stderr)
            return 1
        _emit(
            stdout,
            {
                "command": command,
                "ok": True,
                "hypothesis_external_id": result.hypothesis.external_id,
                "previous_status": result.previous_status,
                "new_status": result.new_status,
                "statement": result.hypothesis.statement,
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

    if command == "validate":
        try:
            request = _read_request(stdin, required={"final_text"})
        except ValueError as error:
            return _usage_error(stdout, stderr, str(error))
        sekai = sekai_gateway or NativeSekaiGateway(settings.chisei_target)
        chisei = chisei_gateway or NativeChiseiGateway(settings.chisei_target)
        try:
            result = validate_proposal_edit(
                process_runner,
                sekai,
                chisei,
                argv[1],
                request["final_text"],
                settings.namespace,
            )
        except (
            DiscoveryError,
            ClaimValidationError,
            ProposalWorkflowError,
            RecordConflictError,
            RecordValidationError,
            grpc.RpcError,
        ) as error:
            _emit_error(stdout, command, "validation_failed", str(error))
            print(f"hibiki: validation failed: {error}", file=stderr)
            return 1
        _emit(
            stdout,
            {
                "command": command,
                "ok": result.validation.valid,
                "proposal_external_id": result.proposal.external_id,
                "final_text_hash": sha256_text(request["final_text"]),
                "status": result.proposal.status,
                "persisted": result.persisted,
                "reasoning": result.validation.reasoning,
                "claims": [
                    {
                        "text": claim.text,
                        "supported": claim.supported,
                        "reason": claim.reason,
                        "source_references": [
                            {"revision": reference.revision, "path": reference.path}
                            for reference in claim.source_references
                        ],
                    }
                    for claim in result.validation.claims
                ],
                "undeclared_claims": result.validation.undeclared_claims,
                "validation_decision_id": result.validation_decision_id,
            },
        )
        return 0 if result.validation.valid else 1

    if command == "approve":
        try:
            request = _read_request(stdin, required={"final_text_hash"})
        except ValueError as error:
            return _usage_error(stdout, stderr, str(error))
        sekai = sekai_gateway or NativeSekaiGateway(settings.chisei_target)
        try:
            result = approve_proposal(
                sekai,
                argv[1],
                request["final_text_hash"],
                settings.namespace,
            )
        except (
            ProposalWorkflowError,
            RecordConflictError,
            RecordValidationError,
            grpc.RpcError,
        ) as error:
            _emit_error(stdout, command, "approval_failed", str(error))
            print(f"hibiki: approval failed: {error}", file=stderr)
            return 1
        _emit(
            stdout,
            {
                "command": command,
                "ok": True,
                "proposal_external_id": result.proposal.external_id,
                "final_text_hash": result.proposal.draft_hash,
                "status": result.proposal.status,
                "approval_id": result.approval_id,
                "validation_decision_id": result.validation_decision_id,
            },
        )
        return 0

    if command == "publish":
        sekai = sekai_gateway or NativeSekaiGateway(settings.chisei_target)
        try:
            result = publish_proposal(
                process_runner,
                sekai,
                argv[1],
                settings.birdclaw_account,
                settings.namespace,
                allow_live_writes=settings.allow_live_writes,
            )
        except (
            PublicationWorkflowError,
            RecordConflictError,
            RecordValidationError,
            grpc.RpcError,
        ) as error:
            _emit_error(stdout, command, "publication_failed", str(error))
            print(f"hibiki: publication failed: {error}", file=stderr)
            return 1
        _emit(
            stdout,
            {
                "command": command,
                "ok": True,
                "proposal_external_id": result.proposal.external_id,
                "proposal_status": result.proposal.status,
                "publication_status": result.publication.status,
                "post_id": result.publication.post_id,
                "target_account": result.publication.target_account,
                "attempted_at": result.publication.attempted_at,
                "reconciled": result.reconciled,
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
        stdin=sys.stdin,
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


def _read_request(stdin: TextIO, *, required: set[str]) -> dict[str, str]:
    try:
        payload = json.load(stdin)
    except json.JSONDecodeError as error:
        raise ValueError("command input must be one JSON object on stdin") from error
    if not isinstance(payload, dict) or set(payload) != required:
        raise ValueError(f"command input must contain exactly: {', '.join(sorted(required))}")
    if any(not isinstance(payload[name], str) or not payload[name].strip() for name in required):
        raise ValueError("command input values must be non-empty strings")
    return {name: payload[name] for name in required}


def _classification_dict(item: ReplyClassification) -> dict[str, object]:
    return {
        "submission_id": item.submission_id,
        "reply_id": item.reply_id,
        "category": item.category,
        "confidence_bps": item.confidence_bps,
        "disposition": item.disposition,
        "operation_id": item.operation_id,
    }
