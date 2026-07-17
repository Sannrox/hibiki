from __future__ import annotations

import pytest

from hibiki.contracts import sekai_pb2
from hibiki.schema import HIBIKI_SCHEMA_TYPES, SchemaConflictError, register_schema_types
from tests.fakes import FakeSekaiGateway


def test_registers_all_hibiki_types_once() -> None:
    gateway = FakeSekaiGateway()

    first = register_schema_types(gateway)
    second = register_schema_types(gateway)

    expected_kinds = tuple(object_type.kind for object_type in HIBIKI_SCHEMA_TYPES)
    assert first.created == expected_kinds
    assert first.updated == ()
    assert first.unchanged == ()
    assert second.created == ()
    assert second.updated == ()
    assert second.unchanged == expected_kinds
    assert gateway.schema_creates == list(expected_kinds)


def test_refuses_to_replace_a_conflicting_accepted_schema() -> None:
    gateway = FakeSekaiGateway(
        schema_types={
            "hibiki.hypothesis": sekai_pb2.ObjectType(
                kind="hibiki.hypothesis", description="unexpected definition"
            )
        }
    )

    with pytest.raises(SchemaConflictError, match=r"hibiki\.hypothesis"):
        register_schema_types(gateway)

    assert gateway.schema_creates == []


def test_adds_optional_reconciliation_fields_to_the_legacy_publication_schema() -> None:
    schemas = {object_type.kind: object_type for object_type in HIBIKI_SCHEMA_TYPES}
    legacy_publication = sekai_pb2.ObjectType()
    legacy_publication.CopyFrom(schemas["hibiki.publication"])
    retained = [
        property_
        for property_ in legacy_publication.properties
        if property_.name not in {"target_account", "attempted_at"}
    ]
    del legacy_publication.properties[:]
    legacy_publication.properties.extend(retained)
    gateway = FakeSekaiGateway(schema_types=schemas | {"hibiki.publication": legacy_publication})

    result = register_schema_types(gateway)

    assert result.created == ()
    assert result.updated == ("hibiki.publication",)
    assert result.unchanged == (
        "hibiki.source",
        "hibiki.proposal",
        "hibiki.outcome",
        "hibiki.hypothesis",
    )
    assert gateway.schema_creates == ["hibiki.publication"]


def test_relaxes_intermediate_required_reconciliation_fields() -> None:
    schemas = {object_type.kind: object_type for object_type in HIBIKI_SCHEMA_TYPES}
    intermediate = sekai_pb2.ObjectType()
    intermediate.CopyFrom(schemas["hibiki.publication"])
    for property_ in intermediate.properties:
        if property_.name in {"target_account", "attempted_at", "approval_id"}:
            property_.required = True
    gateway = FakeSekaiGateway(schema_types=schemas | {"hibiki.publication": intermediate})

    result = register_schema_types(gateway)

    assert result.updated == ("hibiki.publication",)
    assert gateway.schema_types["hibiki.publication"] == schemas["hibiki.publication"]


def test_schema_properties_encode_retry_and_causal_identity() -> None:
    schemas = {object_type.kind: object_type for object_type in HIBIKI_SCHEMA_TYPES}

    for object_type in schemas.values():
        properties = {property_.name: property_ for property_ in object_type.properties}
        assert properties["content_hash"].required is True

    proposal_properties = {
        property_.name: property_ for property_ in schemas["hibiki.proposal"].properties
    }
    publication_properties = {
        property_.name: property_ for property_ in schemas["hibiki.publication"].properties
    }
    assert proposal_properties["source_external_id"].required is True
    assert publication_properties["proposal_external_id"].required is True
    assert publication_properties["target_account"].required is False
    assert publication_properties["attempted_at"].required is False
    assert publication_properties["approval_id"].required is False
