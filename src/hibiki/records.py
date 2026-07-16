from __future__ import annotations

import hashlib
import json
import time
import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace
from typing import ClassVar, Protocol, Self

import grpc

from hibiki.contracts import sekai_pb2
from hibiki.sekai import SekaiGateway

OBJECT_ID_NAMESPACE = uuid.UUID("ee807fe9-667f-41d3-a4c2-fadc9aa36049")


class RecordValidationError(ValueError):
    """Raised when a causal record or its stored representation is invalid."""


class RecordConflictError(RuntimeError):
    """Raised when a stable external ID belongs to another kind or namespace."""


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _content_hash(properties: Mapping[str, str]) -> str:
    return sha256_text(_canonical_json(properties))


def _require_nonempty(**values: str) -> None:
    empty = [name for name, value in values.items() if not value.strip()]
    if empty:
        raise RecordValidationError(f"record fields must not be empty: {', '.join(empty)}")


def _require_choice(name: str, value: str, choices: frozenset[str]) -> None:
    if value not in choices:
        raise RecordValidationError(f"{name} must be one of: {', '.join(sorted(choices))}")


class CausalRecord(Protocol):
    KIND: ClassVar[str]
    namespace: str
    stable_id: str

    @property
    def external_id(self) -> str: ...

    @property
    def content_hash(self) -> str: ...

    def to_properties(self) -> dict[str, str]: ...

    @classmethod
    def from_properties(
        cls, namespace: str, stable_id: str, properties: Mapping[str, str]
    ) -> Self: ...


class _Record:
    KIND: ClassVar[str]
    namespace: str
    stable_id: str

    @property
    def external_id(self) -> str:
        return _external_id(self.KIND, self.namespace, self.stable_id)

    def _payload(self) -> dict[str, str]:
        raise NotImplementedError

    @property
    def content_hash(self) -> str:
        return _content_hash(self._payload())

    def to_properties(self) -> dict[str, str]:
        payload = self._payload()
        payload["content_hash"] = _content_hash(payload)
        return payload


def _external_id(kind: str, namespace: str, stable_id: str) -> str:
    return f"{kind}:{namespace}:{stable_id}"


@dataclass(frozen=True, slots=True, kw_only=True)
class SourceRecord(_Record):
    KIND: ClassVar[str] = "hibiki.source"

    namespace: str = "hibiki"
    stable_id: str
    repository: str
    revision: str
    public_url: str
    evidence_hash: str

    def __post_init__(self) -> None:
        _require_nonempty(
            namespace=self.namespace,
            stable_id=self.stable_id,
            repository=self.repository,
            revision=self.revision,
            public_url=self.public_url,
            evidence_hash=self.evidence_hash,
        )

    def _payload(self) -> dict[str, str]:
        return {
            "repository": self.repository,
            "revision": self.revision,
            "public_url": self.public_url,
            "evidence_hash": self.evidence_hash,
        }

    @classmethod
    def from_properties(
        cls, namespace: str, stable_id: str, properties: Mapping[str, str]
    ) -> SourceRecord:
        return cls(
            namespace=namespace,
            stable_id=stable_id,
            repository=properties.get("repository", ""),
            revision=properties.get("revision", ""),
            public_url=properties.get("public_url", ""),
            evidence_hash=properties.get("evidence_hash", ""),
        )


PROPOSAL_STATUSES = frozenset({"drafted", "approved", "rejected", "invalidated", "published"})


@dataclass(frozen=True, slots=True, kw_only=True)
class ProposalRecord(_Record):
    KIND: ClassVar[str] = "hibiki.proposal"

    namespace: str = "hibiki"
    stable_id: str
    source_external_id: str
    evidence_hash: str
    draft: str
    status: str = "drafted"
    decision_ref: str = ""
    operation_id: str = ""

    def __post_init__(self) -> None:
        _require_nonempty(
            namespace=self.namespace,
            stable_id=self.stable_id,
            source_external_id=self.source_external_id,
            evidence_hash=self.evidence_hash,
            draft=self.draft,
        )
        _require_choice("status", self.status, PROPOSAL_STATUSES)

    @property
    def draft_hash(self) -> str:
        return sha256_text(self.draft)

    def with_status(self, status: str) -> ProposalRecord:
        return replace(self, status=status)

    def _payload(self) -> dict[str, str]:
        return {
            "source_external_id": self.source_external_id,
            "evidence_hash": self.evidence_hash,
            "draft": self.draft,
            "draft_hash": self.draft_hash,
            "status": self.status,
            "decision_ref": self.decision_ref,
            "operation_id": self.operation_id,
        }

    @classmethod
    def from_properties(
        cls, namespace: str, stable_id: str, properties: Mapping[str, str]
    ) -> ProposalRecord:
        record = cls(
            namespace=namespace,
            stable_id=stable_id,
            source_external_id=properties.get("source_external_id", ""),
            evidence_hash=properties.get("evidence_hash", ""),
            draft=properties.get("draft", ""),
            status=properties.get("status", ""),
            decision_ref=properties.get("decision_ref", ""),
            operation_id=properties.get("operation_id", ""),
        )
        if properties.get("draft_hash") != record.draft_hash:
            raise RecordValidationError("stored proposal draft_hash does not match its draft")
        return record


PUBLICATION_STATUSES = frozenset({"intent", "posted", "uncertain", "failed"})


@dataclass(frozen=True, slots=True, kw_only=True)
class PublicationRecord(_Record):
    KIND: ClassVar[str] = "hibiki.publication"

    namespace: str = "hibiki"
    stable_id: str
    proposal_external_id: str
    final_text: str
    status: str = "intent"
    approval_id: str = ""
    approval_expires_at: str = ""
    post_id: str = ""

    def __post_init__(self) -> None:
        _require_nonempty(
            namespace=self.namespace,
            stable_id=self.stable_id,
            proposal_external_id=self.proposal_external_id,
            final_text=self.final_text,
        )
        _require_choice("status", self.status, PUBLICATION_STATUSES)

    @property
    def final_text_hash(self) -> str:
        return sha256_text(self.final_text)

    def _payload(self) -> dict[str, str]:
        return {
            "proposal_external_id": self.proposal_external_id,
            "final_text": self.final_text,
            "final_text_hash": self.final_text_hash,
            "status": self.status,
            "approval_id": self.approval_id,
            "approval_expires_at": self.approval_expires_at,
            "post_id": self.post_id,
        }

    @classmethod
    def from_properties(
        cls, namespace: str, stable_id: str, properties: Mapping[str, str]
    ) -> PublicationRecord:
        record = cls(
            namespace=namespace,
            stable_id=stable_id,
            proposal_external_id=properties.get("proposal_external_id", ""),
            final_text=properties.get("final_text", ""),
            status=properties.get("status", ""),
            approval_id=properties.get("approval_id", ""),
            approval_expires_at=properties.get("approval_expires_at", ""),
            post_id=properties.get("post_id", ""),
        )
        if properties.get("final_text_hash") != record.final_text_hash:
            raise RecordValidationError(
                "stored publication final_text_hash does not match its text"
            )
        return record


OUTCOME_WINDOWS = frozenset({"24h", "7d"})


@dataclass(frozen=True, slots=True, kw_only=True)
class OutcomeRecord(_Record):
    KIND: ClassVar[str] = "hibiki.outcome"

    namespace: str = "hibiki"
    stable_id: str
    publication_external_id: str
    window: str
    observed_at: int
    metrics: Mapping[str, int]
    qualified_replies: int

    def __post_init__(self) -> None:
        _require_nonempty(
            namespace=self.namespace,
            stable_id=self.stable_id,
            publication_external_id=self.publication_external_id,
        )
        _require_choice("window", self.window, OUTCOME_WINDOWS)
        if self.observed_at < 0:
            raise RecordValidationError("observed_at must not be negative")
        if self.qualified_replies < 0:
            raise RecordValidationError("qualified_replies must not be negative")
        if any(
            not isinstance(name, str) or not name or not isinstance(value, int) or value < 0
            for name, value in self.metrics.items()
        ):
            raise RecordValidationError("metrics must map non-empty names to non-negative integers")

    def _payload(self) -> dict[str, str]:
        return {
            "publication_external_id": self.publication_external_id,
            "window": self.window,
            "observed_at": str(self.observed_at),
            "metrics": _canonical_json(dict(self.metrics)),
            "qualified_replies": str(self.qualified_replies),
        }

    @classmethod
    def from_properties(
        cls, namespace: str, stable_id: str, properties: Mapping[str, str]
    ) -> OutcomeRecord:
        try:
            metrics = json.loads(properties.get("metrics", ""))
            observed_at = int(properties.get("observed_at", ""))
            qualified_replies = int(properties.get("qualified_replies", ""))
        except (TypeError, ValueError, json.JSONDecodeError) as error:
            raise RecordValidationError(
                "stored outcome contains invalid numeric or metrics data"
            ) from error
        if not isinstance(metrics, dict):
            raise RecordValidationError("stored outcome metrics must be a JSON object")
        return cls(
            namespace=namespace,
            stable_id=stable_id,
            publication_external_id=properties.get("publication_external_id", ""),
            window=properties.get("window", ""),
            observed_at=observed_at,
            metrics=metrics,
            qualified_replies=qualified_replies,
        )


HYPOTHESIS_STATUSES = frozenset({"surfaced", "accepted", "rejected", "retired"})


@dataclass(frozen=True, slots=True, kw_only=True)
class HypothesisRecord(_Record):
    KIND: ClassVar[str] = "hibiki.hypothesis"

    namespace: str = "hibiki"
    stable_id: str
    statement: str
    evidence_external_ids: tuple[str, ...]
    status: str = "surfaced"

    def __post_init__(self) -> None:
        _require_nonempty(
            namespace=self.namespace, stable_id=self.stable_id, statement=self.statement
        )
        _require_choice("status", self.status, HYPOTHESIS_STATUSES)
        if not self.evidence_external_ids or any(not value for value in self.evidence_external_ids):
            raise RecordValidationError("evidence_external_ids must contain non-empty references")

    def _payload(self) -> dict[str, str]:
        return {
            "statement": self.statement,
            "status": self.status,
            "evidence_external_ids": _canonical_json(list(self.evidence_external_ids)),
        }

    @classmethod
    def from_properties(
        cls, namespace: str, stable_id: str, properties: Mapping[str, str]
    ) -> HypothesisRecord:
        try:
            evidence = json.loads(properties.get("evidence_external_ids", ""))
        except json.JSONDecodeError as error:
            raise RecordValidationError("stored hypothesis evidence is not valid JSON") from error
        if not isinstance(evidence, list) or any(not isinstance(value, str) for value in evidence):
            raise RecordValidationError("stored hypothesis evidence must be a JSON string list")
        return cls(
            namespace=namespace,
            stable_id=stable_id,
            statement=properties.get("statement", ""),
            evidence_external_ids=tuple(evidence),
            status=properties.get("status", ""),
        )


class RecordRepository[RecordT: CausalRecord]:
    def __init__(
        self,
        gateway: SekaiGateway,
        namespace: str,
        record_type: type[RecordT],
        *,
        clock_ms: Callable[[], int] | None = None,
    ) -> None:
        self._gateway = gateway
        self._namespace = namespace
        self._record_type = record_type
        self._clock_ms = clock_ms or (lambda: time.time_ns() // 1_000_000)

    def get(self, stable_id: str) -> RecordT | None:
        external_id = _external_id(self._record_type.KIND, self._namespace, stable_id)
        stored = self._gateway.find_by_external_id(external_id)
        if stored is None:
            return None
        return self._decode(stored)

    def put(self, record: RecordT) -> RecordT:
        if not isinstance(record, self._record_type):
            raise TypeError(f"repository accepts only {self._record_type.__name__}")
        if record.namespace != self._namespace:
            raise RecordConflictError(
                f"record namespace {record.namespace!r} does not match repository "
                f"namespace {self._namespace!r}"
            )

        properties = record.to_properties()
        stored = self._gateway.find_by_external_id(record.external_id)
        if stored is not None:
            return self._reconcile(record, properties, stored)

        now = self._clock_ms()
        object_ = sekai_pb2.Object(
            id=str(uuid.uuid5(OBJECT_ID_NAMESPACE, record.external_id)),
            kind=self._record_type.KIND,
            name=record.stable_id,
            namespace=self._namespace,
            external_id=record.external_id,
            properties=properties,
            created=now,
            updated=now,
        )
        try:
            created = self._gateway.create_object(object_)
        except grpc.RpcError as error:
            if error.code() not in {
                grpc.StatusCode.ALREADY_EXISTS,
                grpc.StatusCode.DEADLINE_EXCEEDED,
                grpc.StatusCode.INTERNAL,
                grpc.StatusCode.UNAVAILABLE,
                grpc.StatusCode.UNKNOWN,
            }:
                raise
            stored = self._gateway.find_by_external_id(record.external_id)
            if stored is None:
                raise
            return self._reconcile(record, properties, stored)
        return self._decode(created)

    def _reconcile(
        self,
        record: RecordT,
        properties: Mapping[str, str],
        stored: sekai_pb2.Object,
    ) -> RecordT:
        self._check_owner(stored)
        if stored.properties.get("content_hash") == record.content_hash:
            return self._decode(stored)
        object_ = sekai_pb2.Object(
            id=stored.id,
            kind=self._record_type.KIND,
            name=record.stable_id,
            namespace=self._namespace,
            external_id=record.external_id,
            properties=properties,
            created=stored.created,
            updated=self._clock_ms(),
        )
        return self._decode(self._gateway.update_object(object_))

    def _check_owner(self, stored: sekai_pb2.Object) -> None:
        if stored.kind != self._record_type.KIND or stored.namespace != self._namespace:
            raise RecordConflictError(
                f"external ID {stored.external_id!r} belongs to "
                f"{stored.namespace}/{stored.kind}, not {self._namespace}/{self._record_type.KIND}"
            )

    def _decode(self, stored: sekai_pb2.Object) -> RecordT:
        self._check_owner(stored)
        prefix = f"{self._record_type.KIND}:{self._namespace}:"
        if not stored.external_id.startswith(prefix) or stored.external_id == prefix:
            raise RecordValidationError(f"invalid external ID for {self._record_type.KIND}")
        stable_id = stored.external_id.removeprefix(prefix)
        record = self._record_type.from_properties(self._namespace, stable_id, stored.properties)
        if stored.properties.get("content_hash") != record.content_hash:
            raise RecordValidationError(
                f"stored {self._record_type.KIND} content_hash does not match its properties"
            )
        return record


class SourceRepository(RecordRepository[SourceRecord]):
    def __init__(
        self, gateway: SekaiGateway, namespace: str, *, clock_ms: Callable[[], int] | None = None
    ) -> None:
        super().__init__(gateway, namespace, SourceRecord, clock_ms=clock_ms)


class ProposalRepository(RecordRepository[ProposalRecord]):
    def __init__(
        self, gateway: SekaiGateway, namespace: str, *, clock_ms: Callable[[], int] | None = None
    ) -> None:
        super().__init__(gateway, namespace, ProposalRecord, clock_ms=clock_ms)


class PublicationRepository(RecordRepository[PublicationRecord]):
    def __init__(
        self, gateway: SekaiGateway, namespace: str, *, clock_ms: Callable[[], int] | None = None
    ) -> None:
        super().__init__(gateway, namespace, PublicationRecord, clock_ms=clock_ms)


class OutcomeRepository(RecordRepository[OutcomeRecord]):
    def __init__(
        self, gateway: SekaiGateway, namespace: str, *, clock_ms: Callable[[], int] | None = None
    ) -> None:
        super().__init__(gateway, namespace, OutcomeRecord, clock_ms=clock_ms)


class HypothesisRepository(RecordRepository[HypothesisRecord]):
    def __init__(
        self, gateway: SekaiGateway, namespace: str, *, clock_ms: Callable[[], int] | None = None
    ) -> None:
        super().__init__(gateway, namespace, HypothesisRecord, clock_ms=clock_ms)


@dataclass(frozen=True, slots=True)
class CausalRepositories:
    sources: SourceRepository
    proposals: ProposalRepository
    publications: PublicationRepository
    outcomes: OutcomeRepository
    hypotheses: HypothesisRepository

    @classmethod
    def create(
        cls,
        gateway: SekaiGateway,
        namespace: str,
        *,
        clock_ms: Callable[[], int] | None = None,
    ) -> CausalRepositories:
        return cls(
            sources=SourceRepository(gateway, namespace, clock_ms=clock_ms),
            proposals=ProposalRepository(gateway, namespace, clock_ms=clock_ms),
            publications=PublicationRepository(gateway, namespace, clock_ms=clock_ms),
            outcomes=OutcomeRepository(gateway, namespace, clock_ms=clock_ms),
            hypotheses=HypothesisRepository(gateway, namespace, clock_ms=clock_ms),
        )
