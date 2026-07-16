from __future__ import annotations

from dataclasses import dataclass

from hibiki.contracts import sekai_pb2
from hibiki.sekai import SekaiGateway


class SchemaConflictError(RuntimeError):
    """Raised when Sekai already contains a different definition for a Hibiki kind."""


@dataclass(frozen=True, slots=True)
class RegistrationResult:
    created: tuple[str, ...]
    unchanged: tuple[str, ...]


def _property(
    name: str,
    type_: str = "string",
    *,
    required: bool = False,
    description: str,
    enum_values: tuple[str, ...] = (),
) -> sekai_pb2.PropertyDef:
    return sekai_pb2.PropertyDef(
        name=name,
        type=type_,
        required=required,
        description=description,
        enum_values=enum_values,
        classification="internal",
    )


HIBIKI_SCHEMA_TYPES = (
    sekai_pb2.ObjectType(
        kind="hibiki.source",
        description="A public Tenkai revision and its bounded evidence identity.",
        properties=(
            _property("repository", required=True, description="GitHub OWNER/REPOSITORY."),
            _property("revision", required=True, description="Immutable source revision."),
            _property("public_url", required=True, description="Public source URL."),
            _property("evidence_hash", required=True, description="Bounded evidence SHA-256."),
            _property("content_hash", required=True, description="Canonical record SHA-256."),
        ),
    ),
    sekai_pb2.ObjectType(
        kind="hibiki.proposal",
        description="A grounded post proposal selected from one source record.",
        properties=(
            _property("source_external_id", required=True, description="Causal source reference."),
            _property("evidence_hash", required=True, description="Evidence used for drafting."),
            _property("draft", required=True, description="Proposed standalone post text."),
            _property("draft_hash", required=True, description="Draft text SHA-256."),
            _property(
                "status",
                "enum",
                required=True,
                description="Current proposal lifecycle state.",
                enum_values=("drafted", "approved", "rejected", "invalidated", "published"),
            ),
            _property("decision_ref", description="Selection decision reference."),
            _property("operation_id", description="Governed operation reference."),
            _property("content_hash", required=True, description="Canonical record SHA-256."),
        ),
    ),
    sekai_pb2.ObjectType(
        kind="hibiki.publication",
        description="A durable publication intent and its reconciled result.",
        properties=(
            _property(
                "proposal_external_id", required=True, description="Approved proposal reference."
            ),
            _property("final_text", required=True, description="Exact text intended for X."),
            _property("final_text_hash", required=True, description="Approved text SHA-256."),
            _property(
                "status",
                "enum",
                required=True,
                description="Publication reconciliation state.",
                enum_values=("intent", "posted", "uncertain", "failed"),
            ),
            _property("approval_id", description="Hash-bound approval reference."),
            _property(
                "approval_expires_at", "timestamp", description="Approval expiry when bounded."
            ),
            _property("post_id", description="BirdClaw read-back X post identifier."),
            _property("content_hash", required=True, description="Canonical record SHA-256."),
        ),
    ),
    sekai_pb2.ObjectType(
        kind="hibiki.outcome",
        description="An observed 24-hour or seven-day publication outcome.",
        properties=(
            _property(
                "publication_external_id",
                required=True,
                description="Observed publication reference.",
            ),
            _property(
                "window",
                "enum",
                required=True,
                description="Observation window.",
                enum_values=("24h", "7d"),
            ),
            _property(
                "observed_at", "timestamp", required=True, description="Collection timestamp."
            ),
            _property("metrics", required=True, description="Canonical raw metrics JSON."),
            _property(
                "qualified_replies",
                "int",
                required=True,
                description="Count of replies meeting the primary outcome.",
            ),
            _property("content_hash", required=True, description="Canonical record SHA-256."),
        ),
    ),
    sekai_pb2.ObjectType(
        kind="hibiki.hypothesis",
        description="A governed learning hypothesis backed by comparable outcomes.",
        properties=(
            _property("statement", required=True, description="Testable strategy hypothesis."),
            _property(
                "status",
                "enum",
                required=True,
                description="Governed hypothesis disposition.",
                enum_values=("surfaced", "accepted", "rejected", "retired"),
            ),
            _property(
                "evidence_external_ids",
                required=True,
                description="Canonical JSON list of supporting outcome references.",
            ),
            _property("content_hash", required=True, description="Canonical record SHA-256."),
        ),
    ),
)


def register_schema_types(gateway: SekaiGateway) -> RegistrationResult:
    existing_by_kind = {
        object_type.kind: object_type for object_type in gateway.list_schema_types()
    }

    for desired in HIBIKI_SCHEMA_TYPES:
        existing = existing_by_kind.get(desired.kind)
        if existing is not None and existing != desired:
            raise SchemaConflictError(
                f"Sekai schema type {desired.kind!r} differs from Hibiki's accepted definition"
            )

    created: list[str] = []
    unchanged: list[str] = []

    for desired in HIBIKI_SCHEMA_TYPES:
        existing = existing_by_kind.get(desired.kind)
        if existing is None:
            gateway.create_schema_type(desired)
            created.append(desired.kind)
        else:
            unchanged.append(desired.kind)

    return RegistrationResult(tuple(created), tuple(unchanged))
