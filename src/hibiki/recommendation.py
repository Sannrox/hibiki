from __future__ import annotations

import json
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass

from hibiki.boundaries import ProcessRunner
from hibiki.chisei import ChiseiGateway
from hibiki.contracts import sekai_pb2
from hibiki.discovery import DiscoveryLimits, discover_public_sources
from hibiki.records import CausalRepositories, SourceRecord
from hibiki.sekai import OWN_DECISION_ACTOR, SekaiGateway
from hibiki.selection import Candidate, commit_evidence_hash, select_candidate

DECISION_ID_NAMESPACE = uuid.UUID("78fb1003-480c-4448-9dbc-71cc65449ac9")


@dataclass(frozen=True, slots=True)
class Recommendation:
    candidate: Candidate | None
    reason: str
    source: SourceRecord | None
    decision_id: str
    operation_id: str
    receipt_complete: bool
    missing_surfaces: tuple[str, ...]
    scanned_at: str


def recommend_source(
    process_runner: ProcessRunner,
    sekai: SekaiGateway,
    chisei: ChiseiGateway,
    repository: str,
    namespace: str,
    *,
    limits: DiscoveryLimits | None = None,
    clock_ms: Callable[[], int] | None = None,
) -> Recommendation:
    now_ms = (clock_ms or (lambda: time.time_ns() // 1_000_000))()
    decisions = sekai.list_decisions(
        actor=OWN_DECISION_ACTOR, action="hibiki.source_scan", limit=100
    )
    successful_scans = [
        decision
        for decision in decisions
        if decision.target_id == repository
        and decision.outcome == "success"
        and decision.evidence.get("scanned_at")
    ]
    since = (
        max(successful_scans, key=lambda decision: decision.timestamp).evidence["scanned_at"]
        if successful_scans
        else None
    )
    selection_decisions = sekai.list_decisions(
        actor=OWN_DECISION_ACTOR, action="hibiki.source_selection", limit=100
    )
    topic_decisions = [
        decision
        for decision in selection_decisions
        if decision.evidence.get("repository") == repository
        and decision.outcome == "selected"
        and decision.evidence.get("topic")
    ]
    recent_topics = tuple(
        decision.evidence["topic"]
        for decision in sorted(topic_decisions, key=lambda decision: decision.timestamp)[-10:]
    )

    bundle = discover_public_sources(
        process_runner,
        repository,
        since=since,
        limits=limits,
    )
    selection = select_candidate(chisei, bundle, recent_topics, namespace=namespace)
    source: SourceRecord | None = None
    target_id = repository
    evidence = {
        "bundle_hash": bundle.content_hash,
        "repository": repository,
        "operation_id": selection.operation_id,
        "provider": selection.provider,
        "model": selection.model,
        "receipt_json": selection.receipt_json,
        "receipt_complete": str(selection.receipt_complete).lower(),
        "missing_surfaces": json.dumps(list(selection.missing_surfaces), separators=(",", ":")),
    }
    outcome = "no_candidate"
    if selection.candidate is not None:
        candidate = selection.candidate
        evidence_hash = commit_evidence_hash(bundle, candidate.revision)
        source = CausalRepositories.create(sekai, namespace, clock_ms=lambda: now_ms).sources.put(
            SourceRecord(
                namespace=namespace,
                stable_id=f"{repository}@{candidate.revision}",
                repository=repository,
                revision=candidate.revision,
                public_url=f"https://github.com/{repository}/commit/{candidate.revision}",
                evidence_hash=evidence_hash,
            )
        )
        target_id = source.external_id
        outcome = "selected"
        evidence.update(
            {
                "revision": candidate.revision,
                "topic": candidate.topic,
                "source_evidence_hash": evidence_hash,
                "scores": json.dumps(candidate.scores, separators=(",", ":"), sort_keys=True),
            }
        )
    decision_id = _stable_decision_id(namespace, "selection", bundle.content_hash)
    sekai.record_decision(
        sekai_pb2.Decision(
            id=decision_id,
            timestamp=now_ms,
            actor="hibiki",
            action="hibiki.source_selection",
            reason=selection.reason,
            evidence=evidence,
            target_id=target_id,
            outcome=outcome,
        )
    )
    sekai.record_decision(
        sekai_pb2.Decision(
            id=_stable_decision_id(namespace, "scan", bundle.content_hash),
            timestamp=now_ms,
            actor="hibiki",
            action="hibiki.source_scan",
            reason="public default-branch scan and governed selection completed",
            evidence={
                "bundle_hash": bundle.content_hash,
                "repository": repository,
                "scanned_at": bundle.scanned_at,
                "commit_count": str(len(bundle.commits)),
                "selection_decision_id": decision_id,
            },
            target_id=repository,
            outcome="success",
        )
    )
    return Recommendation(
        candidate=selection.candidate,
        reason=selection.reason,
        source=source,
        decision_id=decision_id,
        operation_id=selection.operation_id,
        receipt_complete=selection.receipt_complete,
        missing_surfaces=selection.missing_surfaces,
        scanned_at=bundle.scanned_at,
    )


def _stable_decision_id(namespace: str, kind: str, bundle_hash: str) -> str:
    return str(uuid.uuid5(DECISION_ID_NAMESPACE, f"{namespace}:{kind}:{bundle_hash}"))
