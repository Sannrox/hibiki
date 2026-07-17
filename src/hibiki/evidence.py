from __future__ import annotations

import hashlib
import json
import subprocess
import time
import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime

import grpc

from hibiki.boundaries import ProcessRunner
from hibiki.contracts import sekai_pb2
from hibiki.publication import _authored_snowflake_window
from hibiki.records import CausalRepositories, PublicationRecord
from hibiki.sekai import SekaiGateway

PRODUCER_IDENTITY = "hibiki:birdclaw"
SOURCE_TYPE = "birdclaw"
SNAPSHOT_TYPE = "social.post_snapshot"
REPLY_TYPE = "social.reply"
SCHEMA_VERSION = "1.0.0"
CONTRACT_VERSION = "sekai.evidence/v1"
MAX_CONTENT_BYTES = 64 * 1024
MAX_REPLIES = 500
BIRDCLAW_TIMEOUT_SECONDS = 60.0
WINDOW_MILLISECONDS = {"24h": 24 * 60 * 60 * 1000, "7d": 7 * 24 * 60 * 60 * 1000}
WINDOW_TOLERANCE_MILLISECONDS = {
    "24h": 6 * 60 * 60 * 1000,
    "7d": 24 * 60 * 60 * 1000,
}
REGISTRATION_ACTION = "hibiki.evidence_contract_registered"
MAX_REGISTRATION_VERSION_ATTEMPTS = 100
METRIC_FIELDS = {
    "impressions": "impression_count",
    "likes": "like_count",
    "replies": "reply_count",
    "reposts": "retweet_count",
    "quotes": "quote_count",
}


class EvidenceWorkflowError(RuntimeError):
    """Raised when BirdClaw evidence cannot be safely admitted to Sekai."""


@dataclass(frozen=True, slots=True)
class EvidenceRegistrationResult:
    producer_identity: str
    evidence_types: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CollectionResult:
    publication_external_id: str
    post_id: str
    window: str
    snapshot_submission_id: str
    snapshot_deduplicated: bool
    reply_submission_ids: tuple[str, ...]
    replies_deduplicated: int


def register_evidence_contracts(
    gateway: SekaiGateway, namespace: str, source_instance: str
) -> EvidenceRegistrationResult:
    registrations = tuple(
        decision
        for decision in gateway.list_decisions(
            actor="hibiki", action=REGISTRATION_ACTION, limit=100
        )
        if decision.target_id == PRODUCER_IDENTITY and decision.outcome == "success"
    )
    previous_versions = []
    for decision in registrations:
        try:
            version = int(decision.evidence.get("config_version", ""))
        except ValueError as error:
            raise EvidenceWorkflowError(
                "stored evidence producer registration is invalid"
            ) from error
        if version <= 0:
            raise EvidenceWorkflowError("stored evidence producer registration is invalid")
        previous_versions.append(version)
    requested_version = max(previous_versions, default=0) + 1
    capability = sekai_pb2.EvidenceProducerCapability(
        producer_identity=PRODUCER_IDENTITY,
        config_version=requested_version,
        source_types=(SOURCE_TYPE,),
        source_instances=(source_instance,),
        namespaces=(namespace,),
        evidence_types=(SNAPSHOT_TYPE, REPLY_TYPE),
        target_kinds=(PublicationRecord.KIND,),
        classification_ceiling="public",
        allowed_intents=("upsert",),
        allow_operation_attachment=False,
        replay_window_ms=30 * 24 * 60 * 60 * 1000,
        max_clock_skew_ms=5 * 60 * 1000,
        max_payload_bytes=MAX_CONTENT_BYTES,
        max_relationships=8,
        rate_limit_per_minute=600,
        max_retained_submissions=100_000,
    )
    config_version = _register_producer(gateway, capability)
    fingerprint_input = sekai_pb2.EvidenceProducerCapability()
    fingerprint_input.CopyFrom(capability)
    fingerprint_input.config_version = 0
    fingerprint = hashlib.sha256(
        fingerprint_input.SerializeToString(deterministic=True)
    ).hexdigest()
    gateway.record_decision(
        sekai_pb2.Decision(
            id=str(
                uuid.uuid5(
                    uuid.NAMESPACE_URL,
                    f"{PRODUCER_IDENTITY}:{config_version}:{fingerprint}",
                )
            ),
            timestamp=time.time_ns() // 1_000_000,
            actor="hibiki",
            action=REGISTRATION_ACTION,
            reason="Reconciled the scoped BirdClaw evidence producer capability.",
            evidence={
                "config_version": str(config_version),
                "fingerprint": fingerprint,
                "namespace": namespace,
                "source_instance": source_instance,
            },
            target_id=PRODUCER_IDENTITY,
            outcome="success",
        )
    )
    for evidence_type in (SNAPSHOT_TYPE, REPLY_TYPE):
        gateway.register_evidence_schema(
            sekai_pb2.EvidenceSchemaDefinition(
                schema_id=evidence_type,
                schema_version=SCHEMA_VERSION,
                evidence_type=evidence_type,
            )
        )
    return EvidenceRegistrationResult(PRODUCER_IDENTITY, (SNAPSHOT_TYPE, REPLY_TYPE))


def collect_publication_evidence(
    process_runner: ProcessRunner,
    sekai: SekaiGateway,
    publication_external_id: str,
    account: str,
    namespace: str,
    window: str,
    *,
    clock_ms: Callable[[], int] | None = None,
) -> CollectionResult:
    if window not in WINDOW_MILLISECONDS:
        raise EvidenceWorkflowError("collection window must be 24h or 7d")
    repositories = CausalRepositories.create(sekai, namespace, clock_ms=clock_ms)
    publication = repositories.publications.get_external(publication_external_id)
    if publication is None:
        raise EvidenceWorkflowError(f"publication not found: {publication_external_id}")
    if publication.status != "posted" or not publication.post_id:
        raise EvidenceWorkflowError("evidence collection requires a posted publication")
    if publication.target_account != account:
        raise EvidenceWorkflowError("publication belongs to a different BirdClaw account")

    now_ms = (clock_ms or (lambda: time.time_ns() // 1_000_000))()
    if now_ms < publication.attempted_at + WINDOW_MILLISECONDS[window]:
        raise EvidenceWorkflowError(f"{window} evidence window has not elapsed")

    existing_snapshots = _list_submissions(sekai, publication.external_id, SNAPSHOT_TYPE)
    snapshot = next(
        (
            item
            for item in existing_snapshots
            if item.source_record_id == publication.post_id and item.source_version == window
        ),
        None,
    )
    existing_replies = _list_submissions(sekai, publication.external_id, REPLY_TYPE)
    if now_ms > (
        publication.attempted_at
        + WINDOW_MILLISECONDS[window]
        + WINDOW_TOLERANCE_MILLISECONDS[window]
    ):
        if snapshot is None:
            raise EvidenceWorkflowError(f"{window} evidence window has expired")
        return CollectionResult(
            publication.external_id,
            publication.post_id,
            window,
            snapshot.id,
            True,
            (),
            len(existing_replies),
        )
    snapshot_deduplicated = snapshot is not None
    pending: list[sekai_pb2.EvidenceEnvelope] = []
    snapshot_envelope: sekai_pb2.EvidenceEnvelope | None = None
    if snapshot is None:
        post = _collect_post(process_runner, publication)
        content = {
            "post_id": publication.post_id,
            "window": window,
            "metrics": _metrics(post.get("public_metrics"), require_all=True),
        }
        snapshot_envelope = _build_envelope(
            publication,
            account,
            source_record_id=publication.post_id,
            source_version=window,
            source_sequence=1 if window == "24h" else 2,
            evidence_type=SNAPSHOT_TYPE,
            signal="other",
            observed_at_ms=now_ms,
            collected_at_ms=now_ms,
            content=content,
            idempotency_key=f"birdclaw:{account}:post:{publication.post_id}:{window}",
        )

    existing_reply_ids = {item.source_record_id: item for item in existing_replies}
    reply_submission_ids: list[str] = []
    replies_deduplicated = 0
    for reply, authors in _collect_replies(process_runner, publication):
        reply_id = _required_string(reply, "id", "reply")
        if reply_id in existing_reply_ids:
            replies_deduplicated += 1
            continue
        parent_id = _reply_parent(reply)
        author_id = _required_string(reply, "author_id", "reply")
        author = authors.get(author_id, {})
        author_reference = author.get("username") if isinstance(author, dict) else None
        if not isinstance(author_reference, str) or not author_reference.strip():
            author_reference = author_id
        created_at = _timestamp_ms(_required_string(reply, "created_at", "reply"))
        content = {
            "reply_id": reply_id,
            "parent_post_id": parent_id,
            "author_reference": author_reference,
            "text": _required_string(reply, "text", "reply"),
            "public_metrics": _metrics(reply.get("public_metrics")),
            "collected_at_ms": now_ms,
        }
        pending.append(
            _build_envelope(
                publication,
                account,
                source_record_id=reply_id,
                source_version="1",
                source_sequence=1,
                evidence_type=REPLY_TYPE,
                signal="other",
                observed_at_ms=created_at,
                collected_at_ms=now_ms,
                content=content,
                idempotency_key=f"birdclaw:{account}:reply:{reply_id}",
            )
        )

    # The snapshot is the durable completion marker. Submitting it last means
    # its presence proves every reply discovered in this complete sync was
    # already projected, even though Sekai's v1 batch RPC is not atomic.
    if snapshot_envelope is not None:
        pending.append(snapshot_envelope)

    submitted_by_type: dict[str, list[sekai_pb2.EvidenceSubmissionRecord]] = {}
    for envelope in pending:
        submitted = _submit(sekai, envelope)
        submitted_by_type.setdefault(envelope.evidence_type, []).append(submitted)
    if snapshot is None:
        snapshot = submitted_by_type[SNAPSHOT_TYPE][0]
    reply_submission_ids.extend(
        item.id for item in submitted_by_type.get(REPLY_TYPE, ())
    )
    return CollectionResult(
        publication.external_id,
        publication.post_id,
        window,
        snapshot.id,
        snapshot_deduplicated,
        tuple(reply_submission_ids),
        replies_deduplicated,
    )


def _register_producer(
    gateway: SekaiGateway, capability: sekai_pb2.EvidenceProducerCapability
) -> int:
    first_version = capability.config_version
    for config_version in range(
        first_version, first_version + MAX_REGISTRATION_VERSION_ATTEMPTS
    ):
        capability.config_version = config_version
        try:
            gateway.register_evidence_producer(capability)
        except grpc.RpcError as error:
            if error.code() == grpc.StatusCode.INVALID_ARGUMENT and (
                error.details() and "config version must increase" in error.details()
            ):
                continue
            raise
        return config_version
    raise EvidenceWorkflowError(
        "could not negotiate the evidence producer config version; "
        "inspect the Sekai producer registration"
    )


def _list_submissions(
    sekai: SekaiGateway, target_external_id: str, evidence_type: str
) -> tuple[sekai_pb2.EvidenceSubmissionRecord, ...]:
    return sekai.list_evidence_submissions(
        producer_identity=PRODUCER_IDENTITY,
        target_external_id=target_external_id,
        evidence_type=evidence_type,
        limit=MAX_REPLIES + 2,
    )


def _collect_post(
    process_runner: ProcessRunner, publication: PublicationRecord
) -> dict[str, object]:
    since_id, until_id = _authored_snowflake_window(publication.attempted_at)
    response = _run_birdclaw(
        process_runner,
        (
            "birdclaw",
            "sync",
            "authored",
            "--account",
            publication.target_account,
            "--mode",
            "xurl",
            "--limit",
            "100",
            "--since-id",
            since_id,
            "--until-id",
            until_id,
            "--json",
        ),
        "authored post snapshot",
    )
    data, _ = _payload_data(response, "authored post snapshot")
    matches = [item for item in data if item.get("id") == publication.post_id]
    if len(matches) != 1:
        raise EvidenceWorkflowError("BirdClaw did not return exactly one published post")
    return matches[0]


def _collect_replies(
    process_runner: ProcessRunner, publication: PublicationRecord
) -> tuple[tuple[dict[str, object], Mapping[str, dict[str, object]]], ...]:
    start_time = datetime.fromtimestamp(publication.attempted_at / 1000, UTC).isoformat().replace(
        "+00:00", "Z"
    )
    response = _run_birdclaw(
        process_runner,
        (
            "birdclaw",
            "sync",
            "mentions",
            "--account",
            publication.target_account,
            "--mode",
            "xurl",
            "--limit",
            "100",
            "--max-pages",
            "5",
            "--start-time",
            start_time,
            "--refresh",
            "--json",
        ),
        "reply collection",
    )
    data, includes = _payload_data(response, "reply collection")
    author_items = includes.get("users", []) if isinstance(includes, dict) else []
    if not isinstance(author_items, list):
        raise EvidenceWorkflowError("BirdClaw reply collection returned invalid authors")
    authors = {
        item["id"]: item
        for item in author_items
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    replies = tuple(
        (item, authors)
        for item in data
        if item.get("id") != publication.post_id
        and item.get("conversation_id") == publication.post_id
        and _has_reply_parent(item)
    )
    if len(replies) > MAX_REPLIES:
        raise EvidenceWorkflowError(f"reply collection exceeds the {MAX_REPLIES}-reply limit")
    return replies


def _run_birdclaw(
    process_runner: ProcessRunner, argv: tuple[str, ...], operation: str
) -> dict[str, object]:
    try:
        result = process_runner.run(argv, BIRDCLAW_TIMEOUT_SECONDS)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise EvidenceWorkflowError(f"BirdClaw {operation} failed: {error}") from error
    try:
        response = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise EvidenceWorkflowError(f"BirdClaw {operation} returned invalid JSON") from error
    if (
        result.returncode != 0
        or not isinstance(response, dict)
        or response.get("ok") is not True
        or response.get("partial") is not False
    ):
        detail = result.stderr.strip() or "incomplete result"
        raise EvidenceWorkflowError(f"BirdClaw {operation} failed: {detail}")
    return response


def _payload_data(
    response: Mapping[str, object], operation: str
) -> tuple[list[dict[str, object]], Mapping[str, object]]:
    payload = response.get("payload")
    if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
        raise EvidenceWorkflowError(f"BirdClaw {operation} returned no tweet payload")
    if any(not isinstance(item, dict) for item in payload["data"]):
        raise EvidenceWorkflowError(f"BirdClaw {operation} returned an invalid tweet")
    includes = payload.get("includes", {})
    if not isinstance(includes, dict):
        raise EvidenceWorkflowError(f"BirdClaw {operation} returned invalid includes")
    return payload["data"], includes


def _metrics(raw: object, *, require_all: bool = False) -> dict[str, int]:
    if not isinstance(raw, dict):
        raise EvidenceWorkflowError("BirdClaw tweet has no public metrics")
    metrics: dict[str, int] = {}
    for output_name, source_name in METRIC_FIELDS.items():
        if source_name not in raw:
            if require_all:
                raise EvidenceWorkflowError(f"BirdClaw post metric {source_name} is missing")
            continue
        value = raw[source_name]
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise EvidenceWorkflowError(f"BirdClaw metric {source_name} is invalid")
        metrics[output_name] = value
    return metrics


def _has_reply_parent(tweet: Mapping[str, object]) -> bool:
    references = tweet.get("referenced_tweets")
    return isinstance(references, list) and any(
        isinstance(item, dict) and item.get("type") == "replied_to" for item in references
    )


def _reply_parent(tweet: Mapping[str, object]) -> str:
    references = tweet.get("referenced_tweets")
    if isinstance(references, list):
        parents = [
            item.get("id")
            for item in references
            if isinstance(item, dict) and item.get("type") == "replied_to"
        ]
        if len(parents) == 1 and isinstance(parents[0], str) and parents[0].strip():
            return parents[0]
    raise EvidenceWorkflowError("BirdClaw reply has no unique parent post identifier")


def _required_string(item: Mapping[str, object], field: str, kind: str) -> str:
    value = item.get(field)
    if not isinstance(value, str) or not value.strip():
        raise EvidenceWorkflowError(f"BirdClaw {kind} has no {field}")
    return value


def _timestamp_ms(value: str) -> int:
    try:
        return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp() * 1000)
    except ValueError as error:
        raise EvidenceWorkflowError("BirdClaw reply has an invalid created_at") from error


def _build_envelope(
    publication: PublicationRecord,
    account: str,
    *,
    source_record_id: str,
    source_version: str,
    source_sequence: int,
    evidence_type: str,
    signal: str,
    observed_at_ms: int,
    collected_at_ms: int,
    content: Mapping[str, object],
    idempotency_key: str,
) -> sekai_pb2.EvidenceEnvelope:
    content_json = json.dumps(
        content, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode()
    if len(content_json) > MAX_CONTENT_BYTES:
        raise EvidenceWorkflowError("evidence content exceeds the registered payload limit")
    content_digest = hashlib.sha256(content_json).hexdigest()
    return sekai_pb2.EvidenceEnvelope(
        contract_version=CONTRACT_VERSION,
        source_type=SOURCE_TYPE,
        source_instance=account,
        source_record_id=source_record_id,
        source_version=source_version,
        source_sequence=source_sequence,
        namespace=publication.namespace,
        target_external_id=publication.external_id,
        target_kind=PublicationRecord.KIND,
        evidence_type=evidence_type,
        signal=signal,
        schema_id=evidence_type,
        schema_version=SCHEMA_VERSION,
        schema_compatibility="exact",
        observed_at_ms=observed_at_ms,
        collected_at_ms=collected_at_ms,
        content_json=content_json,
        producer_identity=PRODUCER_IDENTITY,
        confidence_bps=10_000,
        classification="public",
        provenance={"transport": "birdclaw", "account": account},
        idempotency_key=idempotency_key,
        content_digest=content_digest,
        intent="upsert",
        causality=sekai_pb2.EvidenceCausality(
            subject_references=(publication.post_id, publication.proposal_external_id)
        ),
    )


def _submit(
    sekai: SekaiGateway, envelope: sekai_pb2.EvidenceEnvelope
) -> sekai_pb2.EvidenceSubmissionRecord:
    result = sekai.submit_evidence(envelope)
    if not result.admitted or not result.projected or not result.submission.id:
        code = result.submission.rejection_code or "not_projected"
        summary = result.submission.rejection_summary or "Sekai did not project the evidence"
        raise EvidenceWorkflowError(f"Sekai rejected evidence ({code}): {summary}")
    return result.submission
