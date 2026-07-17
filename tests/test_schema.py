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
    assert first.unchanged == ()
    assert second.created == ()
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
    assert publication_properties["target_account"].required is True
    assert publication_properties["attempted_at"].required is True
    assert publication_properties["approval_id"].required is True
