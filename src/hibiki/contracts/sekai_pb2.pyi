from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Object(_message.Message):
    __slots__ = ("id", "kind", "name", "namespace", "external_id", "properties", "created", "updated")
    class PropertiesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    EXTERNAL_ID_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    kind: str
    name: str
    namespace: str
    external_id: str
    properties: _containers.ScalarMap[str, str]
    created: int
    updated: int
    def __init__(self, id: _Optional[str] = ..., kind: _Optional[str] = ..., name: _Optional[str] = ..., namespace: _Optional[str] = ..., external_id: _Optional[str] = ..., properties: _Optional[_Mapping[str, str]] = ..., created: _Optional[int] = ..., updated: _Optional[int] = ...) -> None: ...

class Link(_message.Message):
    __slots__ = ("id", "from_id", "to_id", "relation", "created")
    ID_FIELD_NUMBER: _ClassVar[int]
    FROM_ID_FIELD_NUMBER: _ClassVar[int]
    TO_ID_FIELD_NUMBER: _ClassVar[int]
    RELATION_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    from_id: str
    to_id: str
    relation: str
    created: int
    def __init__(self, id: _Optional[str] = ..., from_id: _Optional[str] = ..., to_id: _Optional[str] = ..., relation: _Optional[str] = ..., created: _Optional[int] = ...) -> None: ...

class ListFilter(_message.Message):
    __slots__ = ("kind", "name", "namespace", "property_filters", "limit", "offset", "order_by", "descending", "interface_filter")
    KIND_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    PROPERTY_FILTERS_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    ORDER_BY_FIELD_NUMBER: _ClassVar[int]
    DESCENDING_FIELD_NUMBER: _ClassVar[int]
    INTERFACE_FILTER_FIELD_NUMBER: _ClassVar[int]
    kind: str
    name: str
    namespace: str
    property_filters: _containers.RepeatedCompositeFieldContainer[PropertyFilter]
    limit: int
    offset: int
    order_by: str
    descending: bool
    interface_filter: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, kind: _Optional[str] = ..., name: _Optional[str] = ..., namespace: _Optional[str] = ..., property_filters: _Optional[_Iterable[_Union[PropertyFilter, _Mapping]]] = ..., limit: _Optional[int] = ..., offset: _Optional[int] = ..., order_by: _Optional[str] = ..., descending: _Optional[bool] = ..., interface_filter: _Optional[_Iterable[str]] = ...) -> None: ...

class PropertyFilter(_message.Message):
    __slots__ = ("key", "op", "value")
    KEY_FIELD_NUMBER: _ClassVar[int]
    OP_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: str
    op: str
    value: str
    def __init__(self, key: _Optional[str] = ..., op: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class GraphQuery(_message.Message):
    __slots__ = ("start_id", "start_external_id", "relations", "direction", "max_depth", "kind_filter", "property_filter", "interface_filter")
    class PropertyFilterEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    START_ID_FIELD_NUMBER: _ClassVar[int]
    START_EXTERNAL_ID_FIELD_NUMBER: _ClassVar[int]
    RELATIONS_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    MAX_DEPTH_FIELD_NUMBER: _ClassVar[int]
    KIND_FILTER_FIELD_NUMBER: _ClassVar[int]
    PROPERTY_FILTER_FIELD_NUMBER: _ClassVar[int]
    INTERFACE_FILTER_FIELD_NUMBER: _ClassVar[int]
    start_id: str
    start_external_id: str
    relations: _containers.RepeatedScalarFieldContainer[str]
    direction: str
    max_depth: int
    kind_filter: _containers.RepeatedScalarFieldContainer[str]
    property_filter: _containers.ScalarMap[str, str]
    interface_filter: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, start_id: _Optional[str] = ..., start_external_id: _Optional[str] = ..., relations: _Optional[_Iterable[str]] = ..., direction: _Optional[str] = ..., max_depth: _Optional[int] = ..., kind_filter: _Optional[_Iterable[str]] = ..., property_filter: _Optional[_Mapping[str, str]] = ..., interface_filter: _Optional[_Iterable[str]] = ...) -> None: ...

class GraphResult(_message.Message):
    __slots__ = ("objects", "links")
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    LINKS_FIELD_NUMBER: _ClassVar[int]
    objects: _containers.RepeatedCompositeFieldContainer[Object]
    links: _containers.RepeatedCompositeFieldContainer[Link]
    def __init__(self, objects: _Optional[_Iterable[_Union[Object, _Mapping]]] = ..., links: _Optional[_Iterable[_Union[Link, _Mapping]]] = ...) -> None: ...

class ObjectType(_message.Message):
    __slots__ = ("kind", "description", "properties", "is_builtin", "implements")
    KIND_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    IS_BUILTIN_FIELD_NUMBER: _ClassVar[int]
    IMPLEMENTS_FIELD_NUMBER: _ClassVar[int]
    kind: str
    description: str
    properties: _containers.RepeatedCompositeFieldContainer[PropertyDef]
    is_builtin: bool
    implements: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, kind: _Optional[str] = ..., description: _Optional[str] = ..., properties: _Optional[_Iterable[_Union[PropertyDef, _Mapping]]] = ..., is_builtin: _Optional[bool] = ..., implements: _Optional[_Iterable[str]] = ...) -> None: ...

class InterfaceDef(_message.Message):
    __slots__ = ("name", "description", "properties", "is_builtin")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    IS_BUILTIN_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    properties: _containers.RepeatedCompositeFieldContainer[PropertyDef]
    is_builtin: bool
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., properties: _Optional[_Iterable[_Union[PropertyDef, _Mapping]]] = ..., is_builtin: _Optional[bool] = ...) -> None: ...

class PropertyDef(_message.Message):
    __slots__ = ("name", "type", "required", "description", "enum_values", "link_kind", "compute_expr", "classification", "struct_fields")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ENUM_VALUES_FIELD_NUMBER: _ClassVar[int]
    LINK_KIND_FIELD_NUMBER: _ClassVar[int]
    COMPUTE_EXPR_FIELD_NUMBER: _ClassVar[int]
    CLASSIFICATION_FIELD_NUMBER: _ClassVar[int]
    STRUCT_FIELDS_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: str
    required: bool
    description: str
    enum_values: _containers.RepeatedScalarFieldContainer[str]
    link_kind: str
    compute_expr: str
    classification: str
    struct_fields: _containers.RepeatedCompositeFieldContainer[StructFieldDef]
    def __init__(self, name: _Optional[str] = ..., type: _Optional[str] = ..., required: _Optional[bool] = ..., description: _Optional[str] = ..., enum_values: _Optional[_Iterable[str]] = ..., link_kind: _Optional[str] = ..., compute_expr: _Optional[str] = ..., classification: _Optional[str] = ..., struct_fields: _Optional[_Iterable[_Union[StructFieldDef, _Mapping]]] = ...) -> None: ...

class StructFieldDef(_message.Message):
    __slots__ = ("name", "type", "required", "description", "enum_values")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ENUM_VALUES_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: str
    required: bool
    description: str
    enum_values: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, name: _Optional[str] = ..., type: _Optional[str] = ..., required: _Optional[bool] = ..., description: _Optional[str] = ..., enum_values: _Optional[_Iterable[str]] = ...) -> None: ...

class Function(_message.Message):
    __slots__ = ("name", "description", "params", "pipeline", "created")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    PIPELINE_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    params: _containers.RepeatedCompositeFieldContainer[FuncParam]
    pipeline: _containers.RepeatedCompositeFieldContainer[PipelineStep]
    created: int
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., params: _Optional[_Iterable[_Union[FuncParam, _Mapping]]] = ..., pipeline: _Optional[_Iterable[_Union[PipelineStep, _Mapping]]] = ..., created: _Optional[int] = ...) -> None: ...

class FuncParam(_message.Message):
    __slots__ = ("name", "type", "required")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: str
    required: bool
    def __init__(self, name: _Optional[str] = ..., type: _Optional[str] = ..., required: _Optional[bool] = ...) -> None: ...

class PipelineStep(_message.Message):
    __slots__ = ("op", "kind", "property", "value", "relation", "dir", "func", "field")
    OP_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    PROPERTY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    RELATION_FIELD_NUMBER: _ClassVar[int]
    DIR_FIELD_NUMBER: _ClassVar[int]
    FUNC_FIELD_NUMBER: _ClassVar[int]
    FIELD_FIELD_NUMBER: _ClassVar[int]
    AS_FIELD_NUMBER: _ClassVar[int]
    op: str
    kind: str
    property: str
    value: str
    relation: str
    dir: str
    func: str
    field: str
    def __init__(self, op: _Optional[str] = ..., kind: _Optional[str] = ..., property: _Optional[str] = ..., value: _Optional[str] = ..., relation: _Optional[str] = ..., dir: _Optional[str] = ..., func: _Optional[str] = ..., field: _Optional[str] = ..., **kwargs) -> None: ...

class FunctionResult(_message.Message):
    __slots__ = ("objects", "aggregates")
    class AggregatesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    AGGREGATES_FIELD_NUMBER: _ClassVar[int]
    objects: _containers.RepeatedCompositeFieldContainer[Object]
    aggregates: _containers.ScalarMap[str, str]
    def __init__(self, objects: _Optional[_Iterable[_Union[Object, _Mapping]]] = ..., aggregates: _Optional[_Mapping[str, str]] = ...) -> None: ...

class Dataset(_message.Message):
    __slots__ = ("id", "name", "columns", "object_id", "created")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    COLUMNS_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    columns: _containers.RepeatedCompositeFieldContainer[ColumnDef]
    object_id: str
    created: int
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., columns: _Optional[_Iterable[_Union[ColumnDef, _Mapping]]] = ..., object_id: _Optional[str] = ..., created: _Optional[int] = ...) -> None: ...

class ColumnDef(_message.Message):
    __slots__ = ("name", "type", "classification")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    CLASSIFICATION_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: str
    classification: str
    def __init__(self, name: _Optional[str] = ..., type: _Optional[str] = ..., classification: _Optional[str] = ...) -> None: ...

class RowFilter(_message.Message):
    __slots__ = ("column", "op", "value")
    COLUMN_FIELD_NUMBER: _ClassVar[int]
    OP_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    column: str
    op: str
    value: str
    def __init__(self, column: _Optional[str] = ..., op: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class RowQuery(_message.Message):
    __slots__ = ("filters", "columns", "limit", "offset")
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    COLUMNS_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    filters: _containers.RepeatedCompositeFieldContainer[RowFilter]
    columns: _containers.RepeatedScalarFieldContainer[str]
    limit: int
    offset: int
    def __init__(self, filters: _Optional[_Iterable[_Union[RowFilter, _Mapping]]] = ..., columns: _Optional[_Iterable[str]] = ..., limit: _Optional[int] = ..., offset: _Optional[int] = ...) -> None: ...

class VirtualTable(_message.Message):
    __slots__ = ("id", "name", "dataset_id", "filters", "columns", "created")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    COLUMNS_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    dataset_id: str
    filters: _containers.RepeatedCompositeFieldContainer[RowFilter]
    columns: _containers.RepeatedScalarFieldContainer[str]
    created: int
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., dataset_id: _Optional[str] = ..., filters: _Optional[_Iterable[_Union[RowFilter, _Mapping]]] = ..., columns: _Optional[_Iterable[str]] = ..., created: _Optional[int] = ...) -> None: ...

class Grant(_message.Message):
    __slots__ = ("id", "object_id", "principal", "role", "created")
    ID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    PRINCIPAL_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    object_id: str
    principal: str
    role: str
    created: int
    def __init__(self, id: _Optional[str] = ..., object_id: _Optional[str] = ..., principal: _Optional[str] = ..., role: _Optional[str] = ..., created: _Optional[int] = ...) -> None: ...

class Decision(_message.Message):
    __slots__ = ("id", "timestamp", "actor", "action", "reason", "evidence", "target_id", "outcome")
    class EvidenceEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    ACTOR_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    EVIDENCE_FIELD_NUMBER: _ClassVar[int]
    TARGET_ID_FIELD_NUMBER: _ClassVar[int]
    OUTCOME_FIELD_NUMBER: _ClassVar[int]
    id: str
    timestamp: int
    actor: str
    action: str
    reason: str
    evidence: _containers.ScalarMap[str, str]
    target_id: str
    outcome: str
    def __init__(self, id: _Optional[str] = ..., timestamp: _Optional[int] = ..., actor: _Optional[str] = ..., action: _Optional[str] = ..., reason: _Optional[str] = ..., evidence: _Optional[_Mapping[str, str]] = ..., target_id: _Optional[str] = ..., outcome: _Optional[str] = ...) -> None: ...

class ObjectChange(_message.Message):
    __slots__ = ("id", "object_id", "field", "old_value", "new_value", "changed_by", "timestamp")
    ID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    FIELD_FIELD_NUMBER: _ClassVar[int]
    OLD_VALUE_FIELD_NUMBER: _ClassVar[int]
    NEW_VALUE_FIELD_NUMBER: _ClassVar[int]
    CHANGED_BY_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    id: str
    object_id: str
    field: str
    old_value: str
    new_value: str
    changed_by: str
    timestamp: int
    def __init__(self, id: _Optional[str] = ..., object_id: _Optional[str] = ..., field: _Optional[str] = ..., old_value: _Optional[str] = ..., new_value: _Optional[str] = ..., changed_by: _Optional[str] = ..., timestamp: _Optional[int] = ...) -> None: ...

class ActionRequest(_message.Message):
    __slots__ = ("action", "params", "actor")
    class ParamsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ACTION_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    ACTOR_FIELD_NUMBER: _ClassVar[int]
    action: str
    params: _containers.ScalarMap[str, str]
    actor: str
    def __init__(self, action: _Optional[str] = ..., params: _Optional[_Mapping[str, str]] = ..., actor: _Optional[str] = ...) -> None: ...

class ActionResult(_message.Message):
    __slots__ = ("action", "message", "dry_run", "planned_ops", "decision", "approval_id")
    ACTION_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    DRY_RUN_FIELD_NUMBER: _ClassVar[int]
    PLANNED_OPS_FIELD_NUMBER: _ClassVar[int]
    DECISION_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_ID_FIELD_NUMBER: _ClassVar[int]
    action: str
    message: str
    dry_run: bool
    planned_ops: _containers.RepeatedScalarFieldContainer[str]
    decision: str
    approval_id: str
    def __init__(self, action: _Optional[str] = ..., message: _Optional[str] = ..., dry_run: _Optional[bool] = ..., planned_ops: _Optional[_Iterable[str]] = ..., decision: _Optional[str] = ..., approval_id: _Optional[str] = ...) -> None: ...

class ActionParamDef(_message.Message):
    __slots__ = ("name", "type", "required", "enum_values")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_FIELD_NUMBER: _ClassVar[int]
    ENUM_VALUES_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: str
    required: bool
    enum_values: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, name: _Optional[str] = ..., type: _Optional[str] = ..., required: _Optional[bool] = ..., enum_values: _Optional[_Iterable[str]] = ...) -> None: ...

class ActionOp(_message.Message):
    __slots__ = ("op", "property", "value_from", "relation")
    OP_FIELD_NUMBER: _ClassVar[int]
    PROPERTY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FROM_FIELD_NUMBER: _ClassVar[int]
    RELATION_FIELD_NUMBER: _ClassVar[int]
    op: str
    property: str
    value_from: str
    relation: str
    def __init__(self, op: _Optional[str] = ..., property: _Optional[str] = ..., value_from: _Optional[str] = ..., relation: _Optional[str] = ...) -> None: ...

class ActionTypeDef(_message.Message):
    __slots__ = ("name", "description", "params", "ops", "target_kind", "created")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    OPS_FIELD_NUMBER: _ClassVar[int]
    TARGET_KIND_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    params: _containers.RepeatedCompositeFieldContainer[ActionParamDef]
    ops: _containers.RepeatedCompositeFieldContainer[ActionOp]
    target_kind: str
    created: int
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., params: _Optional[_Iterable[_Union[ActionParamDef, _Mapping]]] = ..., ops: _Optional[_Iterable[_Union[ActionOp, _Mapping]]] = ..., target_kind: _Optional[str] = ..., created: _Optional[int] = ...) -> None: ...

class LineageNode(_message.Message):
    __slots__ = ("object", "role", "ephemeral")
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    EPHEMERAL_FIELD_NUMBER: _ClassVar[int]
    object: Object
    role: str
    ephemeral: bool
    def __init__(self, object: _Optional[_Union[Object, _Mapping]] = ..., role: _Optional[str] = ..., ephemeral: _Optional[bool] = ...) -> None: ...

class LineageEdge(_message.Message):
    __slots__ = ("to", "relation")
    FROM_FIELD_NUMBER: _ClassVar[int]
    TO_FIELD_NUMBER: _ClassVar[int]
    RELATION_FIELD_NUMBER: _ClassVar[int]
    to: str
    relation: str
    def __init__(self, to: _Optional[str] = ..., relation: _Optional[str] = ..., **kwargs) -> None: ...

class LineageResult(_message.Message):
    __slots__ = ("nodes", "edges", "truncated")
    NODES_FIELD_NUMBER: _ClassVar[int]
    EDGES_FIELD_NUMBER: _ClassVar[int]
    TRUNCATED_FIELD_NUMBER: _ClassVar[int]
    nodes: _containers.RepeatedCompositeFieldContainer[LineageNode]
    edges: _containers.RepeatedCompositeFieldContainer[LineageEdge]
    truncated: bool
    def __init__(self, nodes: _Optional[_Iterable[_Union[LineageNode, _Mapping]]] = ..., edges: _Optional[_Iterable[_Union[LineageEdge, _Mapping]]] = ..., truncated: _Optional[bool] = ...) -> None: ...

class CreateObjectRequest(_message.Message):
    __slots__ = ("object",)
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    object: Object
    def __init__(self, object: _Optional[_Union[Object, _Mapping]] = ...) -> None: ...

class CreateObjectResponse(_message.Message):
    __slots__ = ("object",)
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    object: Object
    def __init__(self, object: _Optional[_Union[Object, _Mapping]] = ...) -> None: ...

class GetObjectRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetObjectResponse(_message.Message):
    __slots__ = ("object",)
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    object: Object
    def __init__(self, object: _Optional[_Union[Object, _Mapping]] = ...) -> None: ...

class UpdateObjectRequest(_message.Message):
    __slots__ = ("object",)
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    object: Object
    def __init__(self, object: _Optional[_Union[Object, _Mapping]] = ...) -> None: ...

class UpdateObjectResponse(_message.Message):
    __slots__ = ("object",)
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    object: Object
    def __init__(self, object: _Optional[_Union[Object, _Mapping]] = ...) -> None: ...

class DeleteObjectRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteObjectResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListObjectsRequest(_message.Message):
    __slots__ = ("filter",)
    FILTER_FIELD_NUMBER: _ClassVar[int]
    filter: ListFilter
    def __init__(self, filter: _Optional[_Union[ListFilter, _Mapping]] = ...) -> None: ...

class ListObjectsResponse(_message.Message):
    __slots__ = ("objects", "total")
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    objects: _containers.RepeatedCompositeFieldContainer[Object]
    total: int
    def __init__(self, objects: _Optional[_Iterable[_Union[Object, _Mapping]]] = ..., total: _Optional[int] = ...) -> None: ...

class FindByExternalIdRequest(_message.Message):
    __slots__ = ("external_id",)
    EXTERNAL_ID_FIELD_NUMBER: _ClassVar[int]
    external_id: str
    def __init__(self, external_id: _Optional[str] = ...) -> None: ...

class FindByPropertyRequest(_message.Message):
    __slots__ = ("kind", "key", "value")
    KIND_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    kind: str
    key: str
    value: str
    def __init__(self, kind: _Optional[str] = ..., key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class ObjectSet(_message.Message):
    __slots__ = ("id", "name", "description", "filter", "owner_principal", "created")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    OWNER_PRINCIPAL_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    filter: ListFilter
    owner_principal: str
    created: int
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., filter: _Optional[_Union[ListFilter, _Mapping]] = ..., owner_principal: _Optional[str] = ..., created: _Optional[int] = ...) -> None: ...

class CreateObjectSetRequest(_message.Message):
    __slots__ = ("object_set",)
    OBJECT_SET_FIELD_NUMBER: _ClassVar[int]
    object_set: ObjectSet
    def __init__(self, object_set: _Optional[_Union[ObjectSet, _Mapping]] = ...) -> None: ...

class CreateObjectSetResponse(_message.Message):
    __slots__ = ("object_set",)
    OBJECT_SET_FIELD_NUMBER: _ClassVar[int]
    object_set: ObjectSet
    def __init__(self, object_set: _Optional[_Union[ObjectSet, _Mapping]] = ...) -> None: ...

class ListObjectSetsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListObjectSetsResponse(_message.Message):
    __slots__ = ("object_sets",)
    OBJECT_SETS_FIELD_NUMBER: _ClassVar[int]
    object_sets: _containers.RepeatedCompositeFieldContainer[ObjectSet]
    def __init__(self, object_sets: _Optional[_Iterable[_Union[ObjectSet, _Mapping]]] = ...) -> None: ...

class DeleteObjectSetRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteObjectSetResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ResolveObjectSetRequest(_message.Message):
    __slots__ = ("id", "limit", "offset")
    ID_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    id: str
    limit: int
    offset: int
    def __init__(self, id: _Optional[str] = ..., limit: _Optional[int] = ..., offset: _Optional[int] = ...) -> None: ...

class CreateLinkRequest(_message.Message):
    __slots__ = ("link",)
    LINK_FIELD_NUMBER: _ClassVar[int]
    link: Link
    def __init__(self, link: _Optional[_Union[Link, _Mapping]] = ...) -> None: ...

class CreateLinkResponse(_message.Message):
    __slots__ = ("link",)
    LINK_FIELD_NUMBER: _ClassVar[int]
    link: Link
    def __init__(self, link: _Optional[_Union[Link, _Mapping]] = ...) -> None: ...

class DeleteLinkRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteLinkResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetLinksRequest(_message.Message):
    __slots__ = ("object_id", "relation", "direction")
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    RELATION_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    object_id: str
    relation: str
    direction: str
    def __init__(self, object_id: _Optional[str] = ..., relation: _Optional[str] = ..., direction: _Optional[str] = ...) -> None: ...

class GetLinksResponse(_message.Message):
    __slots__ = ("links",)
    LINKS_FIELD_NUMBER: _ClassVar[int]
    links: _containers.RepeatedCompositeFieldContainer[Link]
    def __init__(self, links: _Optional[_Iterable[_Union[Link, _Mapping]]] = ...) -> None: ...

class GetLinkedObjectsRequest(_message.Message):
    __slots__ = ("object_id", "relation", "direction")
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    RELATION_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    object_id: str
    relation: str
    direction: str
    def __init__(self, object_id: _Optional[str] = ..., relation: _Optional[str] = ..., direction: _Optional[str] = ...) -> None: ...

class GetLinkedObjectsResponse(_message.Message):
    __slots__ = ("objects",)
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    objects: _containers.RepeatedCompositeFieldContainer[Object]
    def __init__(self, objects: _Optional[_Iterable[_Union[Object, _Mapping]]] = ...) -> None: ...

class TraverseRequest(_message.Message):
    __slots__ = ("query",)
    QUERY_FIELD_NUMBER: _ClassVar[int]
    query: GraphQuery
    def __init__(self, query: _Optional[_Union[GraphQuery, _Mapping]] = ...) -> None: ...

class TraverseResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: GraphResult
    def __init__(self, result: _Optional[_Union[GraphResult, _Mapping]] = ...) -> None: ...

class ContextRoot(_message.Message):
    __slots__ = ("object_id", "external_id", "link_id")
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    EXTERNAL_ID_FIELD_NUMBER: _ClassVar[int]
    LINK_ID_FIELD_NUMBER: _ClassVar[int]
    object_id: str
    external_id: str
    link_id: str
    def __init__(self, object_id: _Optional[str] = ..., external_id: _Optional[str] = ..., link_id: _Optional[str] = ...) -> None: ...

class RetrieveContextRequest(_message.Message):
    __slots__ = ("roots", "relations", "direction", "max_depth", "max_objects", "max_links", "kind_filter")
    ROOTS_FIELD_NUMBER: _ClassVar[int]
    RELATIONS_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    MAX_DEPTH_FIELD_NUMBER: _ClassVar[int]
    MAX_OBJECTS_FIELD_NUMBER: _ClassVar[int]
    MAX_LINKS_FIELD_NUMBER: _ClassVar[int]
    KIND_FILTER_FIELD_NUMBER: _ClassVar[int]
    roots: _containers.RepeatedCompositeFieldContainer[ContextRoot]
    relations: _containers.RepeatedScalarFieldContainer[str]
    direction: str
    max_depth: int
    max_objects: int
    max_links: int
    kind_filter: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, roots: _Optional[_Iterable[_Union[ContextRoot, _Mapping]]] = ..., relations: _Optional[_Iterable[str]] = ..., direction: _Optional[str] = ..., max_depth: _Optional[int] = ..., max_objects: _Optional[int] = ..., max_links: _Optional[int] = ..., kind_filter: _Optional[_Iterable[str]] = ...) -> None: ...

class ContextCandidate(_message.Message):
    __slots__ = ("object", "depth", "via_relation", "affinity")
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    DEPTH_FIELD_NUMBER: _ClassVar[int]
    VIA_RELATION_FIELD_NUMBER: _ClassVar[int]
    AFFINITY_FIELD_NUMBER: _ClassVar[int]
    object: Object
    depth: int
    via_relation: str
    affinity: float
    def __init__(self, object: _Optional[_Union[Object, _Mapping]] = ..., depth: _Optional[int] = ..., via_relation: _Optional[str] = ..., affinity: _Optional[float] = ...) -> None: ...

class RetrieveContextResponse(_message.Message):
    __slots__ = ("candidates", "links", "truncated", "unresolved_roots", "denied_objects", "truncated_objects", "truncated_links")
    CANDIDATES_FIELD_NUMBER: _ClassVar[int]
    LINKS_FIELD_NUMBER: _ClassVar[int]
    TRUNCATED_FIELD_NUMBER: _ClassVar[int]
    UNRESOLVED_ROOTS_FIELD_NUMBER: _ClassVar[int]
    DENIED_OBJECTS_FIELD_NUMBER: _ClassVar[int]
    TRUNCATED_OBJECTS_FIELD_NUMBER: _ClassVar[int]
    TRUNCATED_LINKS_FIELD_NUMBER: _ClassVar[int]
    candidates: _containers.RepeatedCompositeFieldContainer[ContextCandidate]
    links: _containers.RepeatedCompositeFieldContainer[Link]
    truncated: bool
    unresolved_roots: int
    denied_objects: int
    truncated_objects: int
    truncated_links: int
    def __init__(self, candidates: _Optional[_Iterable[_Union[ContextCandidate, _Mapping]]] = ..., links: _Optional[_Iterable[_Union[Link, _Mapping]]] = ..., truncated: _Optional[bool] = ..., unresolved_roots: _Optional[int] = ..., denied_objects: _Optional[int] = ..., truncated_objects: _Optional[int] = ..., truncated_links: _Optional[int] = ...) -> None: ...

class ListSchemaTypesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListSchemaTypesResponse(_message.Message):
    __slots__ = ("types",)
    TYPES_FIELD_NUMBER: _ClassVar[int]
    types: _containers.RepeatedCompositeFieldContainer[ObjectType]
    def __init__(self, types: _Optional[_Iterable[_Union[ObjectType, _Mapping]]] = ...) -> None: ...

class CreateSchemaTypeRequest(_message.Message):
    __slots__ = ("type",)
    TYPE_FIELD_NUMBER: _ClassVar[int]
    type: ObjectType
    def __init__(self, type: _Optional[_Union[ObjectType, _Mapping]] = ...) -> None: ...

class CreateSchemaTypeResponse(_message.Message):
    __slots__ = ("type",)
    TYPE_FIELD_NUMBER: _ClassVar[int]
    type: ObjectType
    def __init__(self, type: _Optional[_Union[ObjectType, _Mapping]] = ...) -> None: ...

class DeleteSchemaTypeRequest(_message.Message):
    __slots__ = ("kind",)
    KIND_FIELD_NUMBER: _ClassVar[int]
    kind: str
    def __init__(self, kind: _Optional[str] = ...) -> None: ...

class DeleteSchemaTypeResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListInterfacesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListInterfacesResponse(_message.Message):
    __slots__ = ("interfaces",)
    INTERFACES_FIELD_NUMBER: _ClassVar[int]
    interfaces: _containers.RepeatedCompositeFieldContainer[InterfaceDef]
    def __init__(self, interfaces: _Optional[_Iterable[_Union[InterfaceDef, _Mapping]]] = ...) -> None: ...

class CreateInterfaceRequest(_message.Message):
    __slots__ = ("interface",)
    INTERFACE_FIELD_NUMBER: _ClassVar[int]
    interface: InterfaceDef
    def __init__(self, interface: _Optional[_Union[InterfaceDef, _Mapping]] = ...) -> None: ...

class CreateInterfaceResponse(_message.Message):
    __slots__ = ("interface",)
    INTERFACE_FIELD_NUMBER: _ClassVar[int]
    interface: InterfaceDef
    def __init__(self, interface: _Optional[_Union[InterfaceDef, _Mapping]] = ...) -> None: ...

class DeleteInterfaceRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class DeleteInterfaceResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ExecuteFunctionRequest(_message.Message):
    __slots__ = ("name", "params")
    class ParamsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    name: str
    params: _containers.ScalarMap[str, str]
    def __init__(self, name: _Optional[str] = ..., params: _Optional[_Mapping[str, str]] = ...) -> None: ...

class ExecuteFunctionResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: FunctionResult
    def __init__(self, result: _Optional[_Union[FunctionResult, _Mapping]] = ...) -> None: ...

class CreateFunctionRequest(_message.Message):
    __slots__ = ("function",)
    FUNCTION_FIELD_NUMBER: _ClassVar[int]
    function: Function
    def __init__(self, function: _Optional[_Union[Function, _Mapping]] = ...) -> None: ...

class CreateFunctionResponse(_message.Message):
    __slots__ = ("function",)
    FUNCTION_FIELD_NUMBER: _ClassVar[int]
    function: Function
    def __init__(self, function: _Optional[_Union[Function, _Mapping]] = ...) -> None: ...

class ListFunctionsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListFunctionsResponse(_message.Message):
    __slots__ = ("functions",)
    FUNCTIONS_FIELD_NUMBER: _ClassVar[int]
    functions: _containers.RepeatedCompositeFieldContainer[Function]
    def __init__(self, functions: _Optional[_Iterable[_Union[Function, _Mapping]]] = ...) -> None: ...

class CreateDatasetRequest(_message.Message):
    __slots__ = ("dataset",)
    DATASET_FIELD_NUMBER: _ClassVar[int]
    dataset: Dataset
    def __init__(self, dataset: _Optional[_Union[Dataset, _Mapping]] = ...) -> None: ...

class CreateDatasetResponse(_message.Message):
    __slots__ = ("dataset",)
    DATASET_FIELD_NUMBER: _ClassVar[int]
    dataset: Dataset
    def __init__(self, dataset: _Optional[_Union[Dataset, _Mapping]] = ...) -> None: ...

class UpdateDatasetRequest(_message.Message):
    __slots__ = ("dataset",)
    DATASET_FIELD_NUMBER: _ClassVar[int]
    dataset: Dataset
    def __init__(self, dataset: _Optional[_Union[Dataset, _Mapping]] = ...) -> None: ...

class UpdateDatasetResponse(_message.Message):
    __slots__ = ("dataset",)
    DATASET_FIELD_NUMBER: _ClassVar[int]
    dataset: Dataset
    def __init__(self, dataset: _Optional[_Union[Dataset, _Mapping]] = ...) -> None: ...

class ListDatasetsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListDatasetsResponse(_message.Message):
    __slots__ = ("datasets",)
    DATASETS_FIELD_NUMBER: _ClassVar[int]
    datasets: _containers.RepeatedCompositeFieldContainer[Dataset]
    def __init__(self, datasets: _Optional[_Iterable[_Union[Dataset, _Mapping]]] = ...) -> None: ...

class AppendRowsRequest(_message.Message):
    __slots__ = ("dataset_id", "rows")
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    ROWS_FIELD_NUMBER: _ClassVar[int]
    dataset_id: str
    rows: _containers.RepeatedCompositeFieldContainer[Row]
    def __init__(self, dataset_id: _Optional[str] = ..., rows: _Optional[_Iterable[_Union[Row, _Mapping]]] = ...) -> None: ...

class Row(_message.Message):
    __slots__ = ("values",)
    class ValuesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.ScalarMap[str, str]
    def __init__(self, values: _Optional[_Mapping[str, str]] = ...) -> None: ...

class AppendRowsResponse(_message.Message):
    __slots__ = ("count",)
    COUNT_FIELD_NUMBER: _ClassVar[int]
    count: int
    def __init__(self, count: _Optional[int] = ...) -> None: ...

class QueryRowsRequest(_message.Message):
    __slots__ = ("dataset_id", "query")
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    dataset_id: str
    query: RowQuery
    def __init__(self, dataset_id: _Optional[str] = ..., query: _Optional[_Union[RowQuery, _Mapping]] = ...) -> None: ...

class QueryRowsResponse(_message.Message):
    __slots__ = ("rows",)
    ROWS_FIELD_NUMBER: _ClassVar[int]
    rows: _containers.RepeatedCompositeFieldContainer[Row]
    def __init__(self, rows: _Optional[_Iterable[_Union[Row, _Mapping]]] = ...) -> None: ...

class CreateVirtualTableRequest(_message.Message):
    __slots__ = ("table",)
    TABLE_FIELD_NUMBER: _ClassVar[int]
    table: VirtualTable
    def __init__(self, table: _Optional[_Union[VirtualTable, _Mapping]] = ...) -> None: ...

class CreateVirtualTableResponse(_message.Message):
    __slots__ = ("table",)
    TABLE_FIELD_NUMBER: _ClassVar[int]
    table: VirtualTable
    def __init__(self, table: _Optional[_Union[VirtualTable, _Mapping]] = ...) -> None: ...

class ListVirtualTablesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListVirtualTablesResponse(_message.Message):
    __slots__ = ("tables",)
    TABLES_FIELD_NUMBER: _ClassVar[int]
    tables: _containers.RepeatedCompositeFieldContainer[VirtualTable]
    def __init__(self, tables: _Optional[_Iterable[_Union[VirtualTable, _Mapping]]] = ...) -> None: ...

class CreateGrantRequest(_message.Message):
    __slots__ = ("grant",)
    GRANT_FIELD_NUMBER: _ClassVar[int]
    grant: Grant
    def __init__(self, grant: _Optional[_Union[Grant, _Mapping]] = ...) -> None: ...

class CreateGrantResponse(_message.Message):
    __slots__ = ("grant",)
    GRANT_FIELD_NUMBER: _ClassVar[int]
    grant: Grant
    def __init__(self, grant: _Optional[_Union[Grant, _Mapping]] = ...) -> None: ...

class DeleteGrantRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteGrantResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListGrantsRequest(_message.Message):
    __slots__ = ("object_id",)
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    object_id: str
    def __init__(self, object_id: _Optional[str] = ...) -> None: ...

class ListGrantsResponse(_message.Message):
    __slots__ = ("grants",)
    GRANTS_FIELD_NUMBER: _ClassVar[int]
    grants: _containers.RepeatedCompositeFieldContainer[Grant]
    def __init__(self, grants: _Optional[_Iterable[_Union[Grant, _Mapping]]] = ...) -> None: ...

class CheckAccessRequest(_message.Message):
    __slots__ = ("object_id", "principals")
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    PRINCIPALS_FIELD_NUMBER: _ClassVar[int]
    object_id: str
    principals: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, object_id: _Optional[str] = ..., principals: _Optional[_Iterable[str]] = ...) -> None: ...

class CheckAccessResponse(_message.Message):
    __slots__ = ("allowed",)
    ALLOWED_FIELD_NUMBER: _ClassVar[int]
    allowed: bool
    def __init__(self, allowed: _Optional[bool] = ...) -> None: ...

class RecordDecisionRequest(_message.Message):
    __slots__ = ("decision",)
    DECISION_FIELD_NUMBER: _ClassVar[int]
    decision: Decision
    def __init__(self, decision: _Optional[_Union[Decision, _Mapping]] = ...) -> None: ...

class RecordDecisionResponse(_message.Message):
    __slots__ = ("decision",)
    DECISION_FIELD_NUMBER: _ClassVar[int]
    decision: Decision
    def __init__(self, decision: _Optional[_Union[Decision, _Mapping]] = ...) -> None: ...

class ListDecisionsRequest(_message.Message):
    __slots__ = ("actor", "action", "after", "limit")
    ACTOR_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    AFTER_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    actor: str
    action: str
    after: int
    limit: int
    def __init__(self, actor: _Optional[str] = ..., action: _Optional[str] = ..., after: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class ListDecisionsResponse(_message.Message):
    __slots__ = ("decisions",)
    DECISIONS_FIELD_NUMBER: _ClassVar[int]
    decisions: _containers.RepeatedCompositeFieldContainer[Decision]
    def __init__(self, decisions: _Optional[_Iterable[_Union[Decision, _Mapping]]] = ...) -> None: ...

class ListObjectChangesRequest(_message.Message):
    __slots__ = ("object_id", "limit", "offset")
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    object_id: str
    limit: int
    offset: int
    def __init__(self, object_id: _Optional[str] = ..., limit: _Optional[int] = ..., offset: _Optional[int] = ...) -> None: ...

class ListObjectChangesResponse(_message.Message):
    __slots__ = ("changes",)
    CHANGES_FIELD_NUMBER: _ClassVar[int]
    changes: _containers.RepeatedCompositeFieldContainer[ObjectChange]
    def __init__(self, changes: _Optional[_Iterable[_Union[ObjectChange, _Mapping]]] = ...) -> None: ...

class PolicyAttestation(_message.Message):
    __slots__ = ("id", "decision_id", "policy_kind", "policy_scope", "policy_version", "policy_snapshot", "inputs", "decision", "content_hash", "created")
    class InputsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    DECISION_ID_FIELD_NUMBER: _ClassVar[int]
    POLICY_KIND_FIELD_NUMBER: _ClassVar[int]
    POLICY_SCOPE_FIELD_NUMBER: _ClassVar[int]
    POLICY_VERSION_FIELD_NUMBER: _ClassVar[int]
    POLICY_SNAPSHOT_FIELD_NUMBER: _ClassVar[int]
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    DECISION_FIELD_NUMBER: _ClassVar[int]
    CONTENT_HASH_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    decision_id: str
    policy_kind: str
    policy_scope: str
    policy_version: str
    policy_snapshot: str
    inputs: _containers.ScalarMap[str, str]
    decision: str
    content_hash: str
    created: int
    def __init__(self, id: _Optional[str] = ..., decision_id: _Optional[str] = ..., policy_kind: _Optional[str] = ..., policy_scope: _Optional[str] = ..., policy_version: _Optional[str] = ..., policy_snapshot: _Optional[str] = ..., inputs: _Optional[_Mapping[str, str]] = ..., decision: _Optional[str] = ..., content_hash: _Optional[str] = ..., created: _Optional[int] = ...) -> None: ...

class GetAttestationRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetAttestationResponse(_message.Message):
    __slots__ = ("attestation",)
    ATTESTATION_FIELD_NUMBER: _ClassVar[int]
    attestation: PolicyAttestation
    def __init__(self, attestation: _Optional[_Union[PolicyAttestation, _Mapping]] = ...) -> None: ...

class ListAttestationsRequest(_message.Message):
    __slots__ = ("decision_id", "policy_scope", "limit", "offset")
    DECISION_ID_FIELD_NUMBER: _ClassVar[int]
    POLICY_SCOPE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    decision_id: str
    policy_scope: str
    limit: int
    offset: int
    def __init__(self, decision_id: _Optional[str] = ..., policy_scope: _Optional[str] = ..., limit: _Optional[int] = ..., offset: _Optional[int] = ...) -> None: ...

class ListAttestationsResponse(_message.Message):
    __slots__ = ("attestations",)
    ATTESTATIONS_FIELD_NUMBER: _ClassVar[int]
    attestations: _containers.RepeatedCompositeFieldContainer[PolicyAttestation]
    def __init__(self, attestations: _Optional[_Iterable[_Union[PolicyAttestation, _Mapping]]] = ...) -> None: ...

class VerifyAttestationRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class VerifyAttestationResponse(_message.Message):
    __slots__ = ("ok", "found", "hash_ok", "replay_ok", "replayed_decision", "decision_linked", "error")
    OK_FIELD_NUMBER: _ClassVar[int]
    FOUND_FIELD_NUMBER: _ClassVar[int]
    HASH_OK_FIELD_NUMBER: _ClassVar[int]
    REPLAY_OK_FIELD_NUMBER: _ClassVar[int]
    REPLAYED_DECISION_FIELD_NUMBER: _ClassVar[int]
    DECISION_LINKED_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    ok: bool
    found: bool
    hash_ok: bool
    replay_ok: bool
    replayed_decision: str
    decision_linked: bool
    error: str
    def __init__(self, ok: _Optional[bool] = ..., found: _Optional[bool] = ..., hash_ok: _Optional[bool] = ..., replay_ok: _Optional[bool] = ..., replayed_decision: _Optional[str] = ..., decision_linked: _Optional[bool] = ..., error: _Optional[str] = ...) -> None: ...

class VerifyAuditLedgerRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class VerifyAuditLedgerResponse(_message.Message):
    __slots__ = ("ok", "entries_checked", "first_bad_seq", "error", "anchor_seq", "head_seq", "head_hash")
    OK_FIELD_NUMBER: _ClassVar[int]
    ENTRIES_CHECKED_FIELD_NUMBER: _ClassVar[int]
    FIRST_BAD_SEQ_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    ANCHOR_SEQ_FIELD_NUMBER: _ClassVar[int]
    HEAD_SEQ_FIELD_NUMBER: _ClassVar[int]
    HEAD_HASH_FIELD_NUMBER: _ClassVar[int]
    ok: bool
    entries_checked: int
    first_bad_seq: int
    error: str
    anchor_seq: int
    head_seq: int
    head_hash: str
    def __init__(self, ok: _Optional[bool] = ..., entries_checked: _Optional[int] = ..., first_bad_seq: _Optional[int] = ..., error: _Optional[str] = ..., anchor_seq: _Optional[int] = ..., head_seq: _Optional[int] = ..., head_hash: _Optional[str] = ...) -> None: ...

class AssuranceRecord(_message.Message):
    __slots__ = ("decision", "attestation", "verification")
    DECISION_FIELD_NUMBER: _ClassVar[int]
    ATTESTATION_FIELD_NUMBER: _ClassVar[int]
    VERIFICATION_FIELD_NUMBER: _ClassVar[int]
    decision: Decision
    attestation: PolicyAttestation
    verification: VerifyAttestationResponse
    def __init__(self, decision: _Optional[_Union[Decision, _Mapping]] = ..., attestation: _Optional[_Union[PolicyAttestation, _Mapping]] = ..., verification: _Optional[_Union[VerifyAttestationResponse, _Mapping]] = ...) -> None: ...

class ExportAssuranceRequest(_message.Message):
    __slots__ = ("action", "policy_scope", "after", "limit")
    ACTION_FIELD_NUMBER: _ClassVar[int]
    POLICY_SCOPE_FIELD_NUMBER: _ClassVar[int]
    AFTER_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    action: str
    policy_scope: str
    after: int
    limit: int
    def __init__(self, action: _Optional[str] = ..., policy_scope: _Optional[str] = ..., after: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class ExportAssuranceResponse(_message.Message):
    __slots__ = ("records", "ledger")
    RECORDS_FIELD_NUMBER: _ClassVar[int]
    LEDGER_FIELD_NUMBER: _ClassVar[int]
    records: _containers.RepeatedCompositeFieldContainer[AssuranceRecord]
    ledger: VerifyAuditLedgerResponse
    def __init__(self, records: _Optional[_Iterable[_Union[AssuranceRecord, _Mapping]]] = ..., ledger: _Optional[_Union[VerifyAuditLedgerResponse, _Mapping]] = ...) -> None: ...

class CreateActionTypeRequest(_message.Message):
    __slots__ = ("action_type",)
    ACTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    action_type: ActionTypeDef
    def __init__(self, action_type: _Optional[_Union[ActionTypeDef, _Mapping]] = ...) -> None: ...

class CreateActionTypeResponse(_message.Message):
    __slots__ = ("action_type",)
    ACTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    action_type: ActionTypeDef
    def __init__(self, action_type: _Optional[_Union[ActionTypeDef, _Mapping]] = ...) -> None: ...

class ListActionTypesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListActionTypesResponse(_message.Message):
    __slots__ = ("action_types",)
    ACTION_TYPES_FIELD_NUMBER: _ClassVar[int]
    action_types: _containers.RepeatedCompositeFieldContainer[ActionTypeDef]
    def __init__(self, action_types: _Optional[_Iterable[_Union[ActionTypeDef, _Mapping]]] = ...) -> None: ...

class DeleteActionTypeRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class DeleteActionTypeResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ExecuteActionRequest(_message.Message):
    __slots__ = ("request", "dry_run")
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    DRY_RUN_FIELD_NUMBER: _ClassVar[int]
    request: ActionRequest
    dry_run: bool
    def __init__(self, request: _Optional[_Union[ActionRequest, _Mapping]] = ..., dry_run: _Optional[bool] = ...) -> None: ...

class ExecuteActionResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: ActionResult
    def __init__(self, result: _Optional[_Union[ActionResult, _Mapping]] = ...) -> None: ...

class ActionPolicy(_message.Message):
    __slots__ = ("scope", "default_decision", "action_overrides", "risk_overrides", "max_mutations_per_work_unit", "max_deletes_per_work_unit")
    class ActionOverridesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class RiskOverridesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    SCOPE_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_DECISION_FIELD_NUMBER: _ClassVar[int]
    ACTION_OVERRIDES_FIELD_NUMBER: _ClassVar[int]
    RISK_OVERRIDES_FIELD_NUMBER: _ClassVar[int]
    MAX_MUTATIONS_PER_WORK_UNIT_FIELD_NUMBER: _ClassVar[int]
    MAX_DELETES_PER_WORK_UNIT_FIELD_NUMBER: _ClassVar[int]
    scope: str
    default_decision: str
    action_overrides: _containers.ScalarMap[str, str]
    risk_overrides: _containers.ScalarMap[str, str]
    max_mutations_per_work_unit: int
    max_deletes_per_work_unit: int
    def __init__(self, scope: _Optional[str] = ..., default_decision: _Optional[str] = ..., action_overrides: _Optional[_Mapping[str, str]] = ..., risk_overrides: _Optional[_Mapping[str, str]] = ..., max_mutations_per_work_unit: _Optional[int] = ..., max_deletes_per_work_unit: _Optional[int] = ...) -> None: ...

class SetActionPolicyRequest(_message.Message):
    __slots__ = ("policy",)
    POLICY_FIELD_NUMBER: _ClassVar[int]
    policy: ActionPolicy
    def __init__(self, policy: _Optional[_Union[ActionPolicy, _Mapping]] = ...) -> None: ...

class SetActionPolicyResponse(_message.Message):
    __slots__ = ("policy",)
    POLICY_FIELD_NUMBER: _ClassVar[int]
    policy: ActionPolicy
    def __init__(self, policy: _Optional[_Union[ActionPolicy, _Mapping]] = ...) -> None: ...

class GetActionPolicyRequest(_message.Message):
    __slots__ = ("scope",)
    SCOPE_FIELD_NUMBER: _ClassVar[int]
    scope: str
    def __init__(self, scope: _Optional[str] = ...) -> None: ...

class GetActionPolicyResponse(_message.Message):
    __slots__ = ("policy",)
    POLICY_FIELD_NUMBER: _ClassVar[int]
    policy: ActionPolicy
    def __init__(self, policy: _Optional[_Union[ActionPolicy, _Mapping]] = ...) -> None: ...

class ListActionPoliciesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListActionPoliciesResponse(_message.Message):
    __slots__ = ("policies",)
    POLICIES_FIELD_NUMBER: _ClassVar[int]
    policies: _containers.RepeatedCompositeFieldContainer[ActionPolicy]
    def __init__(self, policies: _Optional[_Iterable[_Union[ActionPolicy, _Mapping]]] = ...) -> None: ...

class ActionApproval(_message.Message):
    __slots__ = ("id", "status", "actor", "action", "params", "work_unit", "policy_scope", "risk_class", "target_id", "created", "updated", "decided_by", "outcome")
    class ParamsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ACTOR_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    WORK_UNIT_FIELD_NUMBER: _ClassVar[int]
    POLICY_SCOPE_FIELD_NUMBER: _ClassVar[int]
    RISK_CLASS_FIELD_NUMBER: _ClassVar[int]
    TARGET_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    DECIDED_BY_FIELD_NUMBER: _ClassVar[int]
    OUTCOME_FIELD_NUMBER: _ClassVar[int]
    id: str
    status: str
    actor: str
    action: str
    params: _containers.ScalarMap[str, str]
    work_unit: str
    policy_scope: str
    risk_class: str
    target_id: str
    created: int
    updated: int
    decided_by: str
    outcome: str
    def __init__(self, id: _Optional[str] = ..., status: _Optional[str] = ..., actor: _Optional[str] = ..., action: _Optional[str] = ..., params: _Optional[_Mapping[str, str]] = ..., work_unit: _Optional[str] = ..., policy_scope: _Optional[str] = ..., risk_class: _Optional[str] = ..., target_id: _Optional[str] = ..., created: _Optional[int] = ..., updated: _Optional[int] = ..., decided_by: _Optional[str] = ..., outcome: _Optional[str] = ...) -> None: ...

class ApproveActionRequest(_message.Message):
    __slots__ = ("approval_id",)
    APPROVAL_ID_FIELD_NUMBER: _ClassVar[int]
    approval_id: str
    def __init__(self, approval_id: _Optional[str] = ...) -> None: ...

class ApproveActionResponse(_message.Message):
    __slots__ = ("result", "approval")
    RESULT_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_FIELD_NUMBER: _ClassVar[int]
    result: ActionResult
    approval: ActionApproval
    def __init__(self, result: _Optional[_Union[ActionResult, _Mapping]] = ..., approval: _Optional[_Union[ActionApproval, _Mapping]] = ...) -> None: ...

class DenyActionRequest(_message.Message):
    __slots__ = ("approval_id", "reason")
    APPROVAL_ID_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    approval_id: str
    reason: str
    def __init__(self, approval_id: _Optional[str] = ..., reason: _Optional[str] = ...) -> None: ...

class DenyActionResponse(_message.Message):
    __slots__ = ("approval",)
    APPROVAL_FIELD_NUMBER: _ClassVar[int]
    approval: ActionApproval
    def __init__(self, approval: _Optional[_Union[ActionApproval, _Mapping]] = ...) -> None: ...

class ListPendingApprovalsRequest(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: str
    def __init__(self, status: _Optional[str] = ...) -> None: ...

class ListPendingApprovalsResponse(_message.Message):
    __slots__ = ("approvals",)
    APPROVALS_FIELD_NUMBER: _ClassVar[int]
    approvals: _containers.RepeatedCompositeFieldContainer[ActionApproval]
    def __init__(self, approvals: _Optional[_Iterable[_Union[ActionApproval, _Mapping]]] = ...) -> None: ...

class GetLineageRequest(_message.Message):
    __slots__ = ("object_id", "max_nodes")
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    MAX_NODES_FIELD_NUMBER: _ClassVar[int]
    object_id: str
    max_nodes: int
    def __init__(self, object_id: _Optional[str] = ..., max_nodes: _Optional[int] = ...) -> None: ...

class GetLineageResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: LineageResult
    def __init__(self, result: _Optional[_Union[LineageResult, _Mapping]] = ...) -> None: ...

class ContentionScope(_message.Message):
    __slots__ = ("id", "name", "parent_scope_id", "max_concurrency", "admission_policy", "heartbeat_ttl_seconds", "timeout_seconds", "owner_principal", "created", "updated")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PARENT_SCOPE_ID_FIELD_NUMBER: _ClassVar[int]
    MAX_CONCURRENCY_FIELD_NUMBER: _ClassVar[int]
    ADMISSION_POLICY_FIELD_NUMBER: _ClassVar[int]
    HEARTBEAT_TTL_SECONDS_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_SECONDS_FIELD_NUMBER: _ClassVar[int]
    OWNER_PRINCIPAL_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    parent_scope_id: str
    max_concurrency: int
    admission_policy: str
    heartbeat_ttl_seconds: int
    timeout_seconds: int
    owner_principal: str
    created: int
    updated: int
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., parent_scope_id: _Optional[str] = ..., max_concurrency: _Optional[int] = ..., admission_policy: _Optional[str] = ..., heartbeat_ttl_seconds: _Optional[int] = ..., timeout_seconds: _Optional[int] = ..., owner_principal: _Optional[str] = ..., created: _Optional[int] = ..., updated: _Optional[int] = ...) -> None: ...

class WorkUnit(_message.Message):
    __slots__ = ("id", "kind", "actor", "target_object_id", "status", "requested_spec", "scope_id", "priority", "timeout_seconds", "heartbeat_ttl_seconds", "created_at", "admitted_at", "started_at", "finished_at", "last_heartbeat_at", "failure_reason", "cancel_reason", "owner_principal", "creator_principal", "idempotency_key", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    ACTOR_FIELD_NUMBER: _ClassVar[int]
    TARGET_OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    REQUESTED_SPEC_FIELD_NUMBER: _ClassVar[int]
    SCOPE_ID_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_SECONDS_FIELD_NUMBER: _ClassVar[int]
    HEARTBEAT_TTL_SECONDS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    ADMITTED_AT_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    LAST_HEARTBEAT_AT_FIELD_NUMBER: _ClassVar[int]
    FAILURE_REASON_FIELD_NUMBER: _ClassVar[int]
    CANCEL_REASON_FIELD_NUMBER: _ClassVar[int]
    OWNER_PRINCIPAL_FIELD_NUMBER: _ClassVar[int]
    CREATOR_PRINCIPAL_FIELD_NUMBER: _ClassVar[int]
    IDEMPOTENCY_KEY_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    kind: str
    actor: str
    target_object_id: str
    status: str
    requested_spec: str
    scope_id: str
    priority: int
    timeout_seconds: int
    heartbeat_ttl_seconds: int
    created_at: int
    admitted_at: int
    started_at: int
    finished_at: int
    last_heartbeat_at: int
    failure_reason: str
    cancel_reason: str
    owner_principal: str
    creator_principal: str
    idempotency_key: str
    updated_at: int
    def __init__(self, id: _Optional[str] = ..., kind: _Optional[str] = ..., actor: _Optional[str] = ..., target_object_id: _Optional[str] = ..., status: _Optional[str] = ..., requested_spec: _Optional[str] = ..., scope_id: _Optional[str] = ..., priority: _Optional[int] = ..., timeout_seconds: _Optional[int] = ..., heartbeat_ttl_seconds: _Optional[int] = ..., created_at: _Optional[int] = ..., admitted_at: _Optional[int] = ..., started_at: _Optional[int] = ..., finished_at: _Optional[int] = ..., last_heartbeat_at: _Optional[int] = ..., failure_reason: _Optional[str] = ..., cancel_reason: _Optional[str] = ..., owner_principal: _Optional[str] = ..., creator_principal: _Optional[str] = ..., idempotency_key: _Optional[str] = ..., updated_at: _Optional[int] = ...) -> None: ...

class Reservation(_message.Message):
    __slots__ = ("id", "work_unit_id", "scope_id", "status", "lease_owner", "leased_at", "expires_at", "released_at", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    WORK_UNIT_ID_FIELD_NUMBER: _ClassVar[int]
    SCOPE_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LEASE_OWNER_FIELD_NUMBER: _ClassVar[int]
    LEASED_AT_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    RELEASED_AT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    work_unit_id: str
    scope_id: str
    status: str
    lease_owner: str
    leased_at: int
    expires_at: int
    released_at: int
    created_at: int
    def __init__(self, id: _Optional[str] = ..., work_unit_id: _Optional[str] = ..., scope_id: _Optional[str] = ..., status: _Optional[str] = ..., lease_owner: _Optional[str] = ..., leased_at: _Optional[int] = ..., expires_at: _Optional[int] = ..., released_at: _Optional[int] = ..., created_at: _Optional[int] = ...) -> None: ...

class RunEvent(_message.Message):
    __slots__ = ("id", "work_unit_id", "event_type", "message", "evidence", "created_at")
    class EvidenceEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    WORK_UNIT_ID_FIELD_NUMBER: _ClassVar[int]
    EVENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    EVIDENCE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    work_unit_id: str
    event_type: str
    message: str
    evidence: _containers.ScalarMap[str, str]
    created_at: int
    def __init__(self, id: _Optional[str] = ..., work_unit_id: _Optional[str] = ..., event_type: _Optional[str] = ..., message: _Optional[str] = ..., evidence: _Optional[_Mapping[str, str]] = ..., created_at: _Optional[int] = ...) -> None: ...

class WorkUnitFilter(_message.Message):
    __slots__ = ("status", "actor", "scope_id", "target_object_id", "owner_principal", "limit", "offset", "statuses", "created_after", "updated_after", "creator_principal", "page_token")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ACTOR_FIELD_NUMBER: _ClassVar[int]
    SCOPE_ID_FIELD_NUMBER: _ClassVar[int]
    TARGET_OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    OWNER_PRINCIPAL_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    STATUSES_FIELD_NUMBER: _ClassVar[int]
    CREATED_AFTER_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AFTER_FIELD_NUMBER: _ClassVar[int]
    CREATOR_PRINCIPAL_FIELD_NUMBER: _ClassVar[int]
    PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    status: str
    actor: str
    scope_id: str
    target_object_id: str
    owner_principal: str
    limit: int
    offset: int
    statuses: _containers.RepeatedScalarFieldContainer[str]
    created_after: int
    updated_after: int
    creator_principal: str
    page_token: str
    def __init__(self, status: _Optional[str] = ..., actor: _Optional[str] = ..., scope_id: _Optional[str] = ..., target_object_id: _Optional[str] = ..., owner_principal: _Optional[str] = ..., limit: _Optional[int] = ..., offset: _Optional[int] = ..., statuses: _Optional[_Iterable[str]] = ..., created_after: _Optional[int] = ..., updated_after: _Optional[int] = ..., creator_principal: _Optional[str] = ..., page_token: _Optional[str] = ...) -> None: ...

class ScopeBlockage(_message.Message):
    __slots__ = ("scope_id", "scope_name", "reason", "pending_count", "active_count")
    SCOPE_ID_FIELD_NUMBER: _ClassVar[int]
    SCOPE_NAME_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    PENDING_COUNT_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_COUNT_FIELD_NUMBER: _ClassVar[int]
    scope_id: str
    scope_name: str
    reason: str
    pending_count: int
    active_count: int
    def __init__(self, scope_id: _Optional[str] = ..., scope_name: _Optional[str] = ..., reason: _Optional[str] = ..., pending_count: _Optional[int] = ..., active_count: _Optional[int] = ...) -> None: ...

class CoordinationSnapshot(_message.Message):
    __slots__ = ("pending_count", "running_count", "stale_count", "active_reservation_count", "oldest_pending_age_ms", "blocked_scopes", "oldest_running_age_ms", "stale_reservation_count")
    PENDING_COUNT_FIELD_NUMBER: _ClassVar[int]
    RUNNING_COUNT_FIELD_NUMBER: _ClassVar[int]
    STALE_COUNT_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_RESERVATION_COUNT_FIELD_NUMBER: _ClassVar[int]
    OLDEST_PENDING_AGE_MS_FIELD_NUMBER: _ClassVar[int]
    BLOCKED_SCOPES_FIELD_NUMBER: _ClassVar[int]
    OLDEST_RUNNING_AGE_MS_FIELD_NUMBER: _ClassVar[int]
    STALE_RESERVATION_COUNT_FIELD_NUMBER: _ClassVar[int]
    pending_count: int
    running_count: int
    stale_count: int
    active_reservation_count: int
    oldest_pending_age_ms: int
    blocked_scopes: _containers.RepeatedCompositeFieldContainer[ScopeBlockage]
    oldest_running_age_ms: int
    stale_reservation_count: int
    def __init__(self, pending_count: _Optional[int] = ..., running_count: _Optional[int] = ..., stale_count: _Optional[int] = ..., active_reservation_count: _Optional[int] = ..., oldest_pending_age_ms: _Optional[int] = ..., blocked_scopes: _Optional[_Iterable[_Union[ScopeBlockage, _Mapping]]] = ..., oldest_running_age_ms: _Optional[int] = ..., stale_reservation_count: _Optional[int] = ...) -> None: ...

class CreateContentionScopeRequest(_message.Message):
    __slots__ = ("scope", "request_id")
    SCOPE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    scope: ContentionScope
    request_id: str
    def __init__(self, scope: _Optional[_Union[ContentionScope, _Mapping]] = ..., request_id: _Optional[str] = ...) -> None: ...

class CreateContentionScopeResponse(_message.Message):
    __slots__ = ("scope",)
    SCOPE_FIELD_NUMBER: _ClassVar[int]
    scope: ContentionScope
    def __init__(self, scope: _Optional[_Union[ContentionScope, _Mapping]] = ...) -> None: ...

class UpdateContentionScopeRequest(_message.Message):
    __slots__ = ("scope", "request_id")
    SCOPE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    scope: ContentionScope
    request_id: str
    def __init__(self, scope: _Optional[_Union[ContentionScope, _Mapping]] = ..., request_id: _Optional[str] = ...) -> None: ...

class UpdateContentionScopeResponse(_message.Message):
    __slots__ = ("scope",)
    SCOPE_FIELD_NUMBER: _ClassVar[int]
    scope: ContentionScope
    def __init__(self, scope: _Optional[_Union[ContentionScope, _Mapping]] = ...) -> None: ...

class GetContentionScopeRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetContentionScopeResponse(_message.Message):
    __slots__ = ("scope",)
    SCOPE_FIELD_NUMBER: _ClassVar[int]
    scope: ContentionScope
    def __init__(self, scope: _Optional[_Union[ContentionScope, _Mapping]] = ...) -> None: ...

class ListContentionScopesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListContentionScopesResponse(_message.Message):
    __slots__ = ("scopes",)
    SCOPES_FIELD_NUMBER: _ClassVar[int]
    scopes: _containers.RepeatedCompositeFieldContainer[ContentionScope]
    def __init__(self, scopes: _Optional[_Iterable[_Union[ContentionScope, _Mapping]]] = ...) -> None: ...

class CreateWorkUnitRequest(_message.Message):
    __slots__ = ("work_unit", "request_id")
    WORK_UNIT_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    work_unit: WorkUnit
    request_id: str
    def __init__(self, work_unit: _Optional[_Union[WorkUnit, _Mapping]] = ..., request_id: _Optional[str] = ...) -> None: ...

class CreateWorkUnitResponse(_message.Message):
    __slots__ = ("work_unit",)
    WORK_UNIT_FIELD_NUMBER: _ClassVar[int]
    work_unit: WorkUnit
    def __init__(self, work_unit: _Optional[_Union[WorkUnit, _Mapping]] = ...) -> None: ...

class GetWorkUnitRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetWorkUnitResponse(_message.Message):
    __slots__ = ("work_unit",)
    WORK_UNIT_FIELD_NUMBER: _ClassVar[int]
    work_unit: WorkUnit
    def __init__(self, work_unit: _Optional[_Union[WorkUnit, _Mapping]] = ...) -> None: ...

class ListWorkUnitsRequest(_message.Message):
    __slots__ = ("filter",)
    FILTER_FIELD_NUMBER: _ClassVar[int]
    filter: WorkUnitFilter
    def __init__(self, filter: _Optional[_Union[WorkUnitFilter, _Mapping]] = ...) -> None: ...

class ListWorkUnitsResponse(_message.Message):
    __slots__ = ("work_units", "next_page_token")
    WORK_UNITS_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    work_units: _containers.RepeatedCompositeFieldContainer[WorkUnit]
    next_page_token: str
    def __init__(self, work_units: _Optional[_Iterable[_Union[WorkUnit, _Mapping]]] = ..., next_page_token: _Optional[str] = ...) -> None: ...

class TryAdmitWorkUnitRequest(_message.Message):
    __slots__ = ("work_unit_id", "request_id")
    WORK_UNIT_ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    work_unit_id: str
    request_id: str
    def __init__(self, work_unit_id: _Optional[str] = ..., request_id: _Optional[str] = ...) -> None: ...

class TryAdmitWorkUnitResponse(_message.Message):
    __slots__ = ("admitted", "queue_position", "reason", "work_unit", "reservations")
    ADMITTED_FIELD_NUMBER: _ClassVar[int]
    QUEUE_POSITION_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    WORK_UNIT_FIELD_NUMBER: _ClassVar[int]
    RESERVATIONS_FIELD_NUMBER: _ClassVar[int]
    admitted: bool
    queue_position: int
    reason: str
    work_unit: WorkUnit
    reservations: _containers.RepeatedCompositeFieldContainer[Reservation]
    def __init__(self, admitted: _Optional[bool] = ..., queue_position: _Optional[int] = ..., reason: _Optional[str] = ..., work_unit: _Optional[_Union[WorkUnit, _Mapping]] = ..., reservations: _Optional[_Iterable[_Union[Reservation, _Mapping]]] = ...) -> None: ...

class HeartbeatWorkUnitRequest(_message.Message):
    __slots__ = ("work_unit_id", "request_id")
    WORK_UNIT_ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    work_unit_id: str
    request_id: str
    def __init__(self, work_unit_id: _Optional[str] = ..., request_id: _Optional[str] = ...) -> None: ...

class HeartbeatWorkUnitResponse(_message.Message):
    __slots__ = ("work_unit",)
    WORK_UNIT_FIELD_NUMBER: _ClassVar[int]
    work_unit: WorkUnit
    def __init__(self, work_unit: _Optional[_Union[WorkUnit, _Mapping]] = ...) -> None: ...

class CompleteWorkUnitRequest(_message.Message):
    __slots__ = ("work_unit_id", "request_id")
    WORK_UNIT_ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    work_unit_id: str
    request_id: str
    def __init__(self, work_unit_id: _Optional[str] = ..., request_id: _Optional[str] = ...) -> None: ...

class CompleteWorkUnitResponse(_message.Message):
    __slots__ = ("work_unit",)
    WORK_UNIT_FIELD_NUMBER: _ClassVar[int]
    work_unit: WorkUnit
    def __init__(self, work_unit: _Optional[_Union[WorkUnit, _Mapping]] = ...) -> None: ...

class FailWorkUnitRequest(_message.Message):
    __slots__ = ("work_unit_id", "failure_reason", "request_id")
    WORK_UNIT_ID_FIELD_NUMBER: _ClassVar[int]
    FAILURE_REASON_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    work_unit_id: str
    failure_reason: str
    request_id: str
    def __init__(self, work_unit_id: _Optional[str] = ..., failure_reason: _Optional[str] = ..., request_id: _Optional[str] = ...) -> None: ...

class FailWorkUnitResponse(_message.Message):
    __slots__ = ("work_unit",)
    WORK_UNIT_FIELD_NUMBER: _ClassVar[int]
    work_unit: WorkUnit
    def __init__(self, work_unit: _Optional[_Union[WorkUnit, _Mapping]] = ...) -> None: ...

class CancelWorkUnitRequest(_message.Message):
    __slots__ = ("work_unit_id", "cancel_reason", "request_id")
    WORK_UNIT_ID_FIELD_NUMBER: _ClassVar[int]
    CANCEL_REASON_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    work_unit_id: str
    cancel_reason: str
    request_id: str
    def __init__(self, work_unit_id: _Optional[str] = ..., cancel_reason: _Optional[str] = ..., request_id: _Optional[str] = ...) -> None: ...

class CancelWorkUnitResponse(_message.Message):
    __slots__ = ("work_unit",)
    WORK_UNIT_FIELD_NUMBER: _ClassVar[int]
    work_unit: WorkUnit
    def __init__(self, work_unit: _Optional[_Union[WorkUnit, _Mapping]] = ...) -> None: ...

class ReleaseReservationRequest(_message.Message):
    __slots__ = ("work_unit_id", "request_id")
    WORK_UNIT_ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    work_unit_id: str
    request_id: str
    def __init__(self, work_unit_id: _Optional[str] = ..., request_id: _Optional[str] = ...) -> None: ...

class ReleaseReservationResponse(_message.Message):
    __slots__ = ("released",)
    RELEASED_FIELD_NUMBER: _ClassVar[int]
    released: int
    def __init__(self, released: _Optional[int] = ...) -> None: ...

class ListReservationsRequest(_message.Message):
    __slots__ = ("work_unit_id", "scope_id", "status")
    WORK_UNIT_ID_FIELD_NUMBER: _ClassVar[int]
    SCOPE_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    work_unit_id: str
    scope_id: str
    status: str
    def __init__(self, work_unit_id: _Optional[str] = ..., scope_id: _Optional[str] = ..., status: _Optional[str] = ...) -> None: ...

class ListReservationsResponse(_message.Message):
    __slots__ = ("reservations",)
    RESERVATIONS_FIELD_NUMBER: _ClassVar[int]
    reservations: _containers.RepeatedCompositeFieldContainer[Reservation]
    def __init__(self, reservations: _Optional[_Iterable[_Union[Reservation, _Mapping]]] = ...) -> None: ...

class ListRunEventsRequest(_message.Message):
    __slots__ = ("work_unit_id", "limit", "after", "event_types", "page_token")
    WORK_UNIT_ID_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    AFTER_FIELD_NUMBER: _ClassVar[int]
    EVENT_TYPES_FIELD_NUMBER: _ClassVar[int]
    PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    work_unit_id: str
    limit: int
    after: int
    event_types: _containers.RepeatedScalarFieldContainer[str]
    page_token: str
    def __init__(self, work_unit_id: _Optional[str] = ..., limit: _Optional[int] = ..., after: _Optional[int] = ..., event_types: _Optional[_Iterable[str]] = ..., page_token: _Optional[str] = ...) -> None: ...

class ListRunEventsResponse(_message.Message):
    __slots__ = ("events", "next_page_token")
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    events: _containers.RepeatedCompositeFieldContainer[RunEvent]
    next_page_token: str
    def __init__(self, events: _Optional[_Iterable[_Union[RunEvent, _Mapping]]] = ..., next_page_token: _Optional[str] = ...) -> None: ...

class ReconciliationDetail(_message.Message):
    __slots__ = ("work_unit_id", "reservation_id", "reason", "action")
    WORK_UNIT_ID_FIELD_NUMBER: _ClassVar[int]
    RESERVATION_ID_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    work_unit_id: str
    reservation_id: str
    reason: str
    action: str
    def __init__(self, work_unit_id: _Optional[str] = ..., reservation_id: _Optional[str] = ..., reason: _Optional[str] = ..., action: _Optional[str] = ...) -> None: ...

class ReconcileWorkUnitsRequest(_message.Message):
    __slots__ = ("dry_run", "work_unit_id", "scope_id", "limit")
    DRY_RUN_FIELD_NUMBER: _ClassVar[int]
    WORK_UNIT_ID_FIELD_NUMBER: _ClassVar[int]
    SCOPE_ID_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    dry_run: bool
    work_unit_id: str
    scope_id: str
    limit: int
    def __init__(self, dry_run: _Optional[bool] = ..., work_unit_id: _Optional[str] = ..., scope_id: _Optional[str] = ..., limit: _Optional[int] = ...) -> None: ...

class ReconcileWorkUnitsResponse(_message.Message):
    __slots__ = ("work_units_reconciled", "reservations_released", "details")
    WORK_UNITS_RECONCILED_FIELD_NUMBER: _ClassVar[int]
    RESERVATIONS_RELEASED_FIELD_NUMBER: _ClassVar[int]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    work_units_reconciled: int
    reservations_released: int
    details: _containers.RepeatedCompositeFieldContainer[ReconciliationDetail]
    def __init__(self, work_units_reconciled: _Optional[int] = ..., reservations_released: _Optional[int] = ..., details: _Optional[_Iterable[_Union[ReconciliationDetail, _Mapping]]] = ...) -> None: ...

class GetCoordinationSnapshotRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetCoordinationSnapshotResponse(_message.Message):
    __slots__ = ("snapshot",)
    SNAPSHOT_FIELD_NUMBER: _ClassVar[int]
    snapshot: CoordinationSnapshot
    def __init__(self, snapshot: _Optional[_Union[CoordinationSnapshot, _Mapping]] = ...) -> None: ...

class CredentialRecord(_message.Message):
    __slots__ = ("id", "principal", "status", "created", "rotated_at", "revoked_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    PRINCIPAL_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    ROTATED_AT_FIELD_NUMBER: _ClassVar[int]
    REVOKED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    principal: str
    status: str
    created: int
    rotated_at: int
    revoked_at: int
    def __init__(self, id: _Optional[str] = ..., principal: _Optional[str] = ..., status: _Optional[str] = ..., created: _Optional[int] = ..., rotated_at: _Optional[int] = ..., revoked_at: _Optional[int] = ...) -> None: ...

class CreateCredentialRequest(_message.Message):
    __slots__ = ("principal",)
    PRINCIPAL_FIELD_NUMBER: _ClassVar[int]
    principal: str
    def __init__(self, principal: _Optional[str] = ...) -> None: ...

class CreateCredentialResponse(_message.Message):
    __slots__ = ("token", "credential")
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    CREDENTIAL_FIELD_NUMBER: _ClassVar[int]
    token: str
    credential: CredentialRecord
    def __init__(self, token: _Optional[str] = ..., credential: _Optional[_Union[CredentialRecord, _Mapping]] = ...) -> None: ...

class RotateCredentialRequest(_message.Message):
    __slots__ = ("principal",)
    PRINCIPAL_FIELD_NUMBER: _ClassVar[int]
    principal: str
    def __init__(self, principal: _Optional[str] = ...) -> None: ...

class RotateCredentialResponse(_message.Message):
    __slots__ = ("token", "credential")
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    CREDENTIAL_FIELD_NUMBER: _ClassVar[int]
    token: str
    credential: CredentialRecord
    def __init__(self, token: _Optional[str] = ..., credential: _Optional[_Union[CredentialRecord, _Mapping]] = ...) -> None: ...

class RevokeCredentialRequest(_message.Message):
    __slots__ = ("principal",)
    PRINCIPAL_FIELD_NUMBER: _ClassVar[int]
    principal: str
    def __init__(self, principal: _Optional[str] = ...) -> None: ...

class RevokeCredentialResponse(_message.Message):
    __slots__ = ("credential",)
    CREDENTIAL_FIELD_NUMBER: _ClassVar[int]
    credential: CredentialRecord
    def __init__(self, credential: _Optional[_Union[CredentialRecord, _Mapping]] = ...) -> None: ...

class ListCredentialsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListCredentialsResponse(_message.Message):
    __slots__ = ("credentials",)
    CREDENTIALS_FIELD_NUMBER: _ClassVar[int]
    credentials: _containers.RepeatedCompositeFieldContainer[CredentialRecord]
    def __init__(self, credentials: _Optional[_Iterable[_Union[CredentialRecord, _Mapping]]] = ...) -> None: ...

class GetProvenanceReportRequest(_message.Message):
    __slots__ = ("work_unit_id",)
    WORK_UNIT_ID_FIELD_NUMBER: _ClassVar[int]
    work_unit_id: str
    def __init__(self, work_unit_id: _Optional[str] = ...) -> None: ...

class GetProvenanceReportResponse(_message.Message):
    __slots__ = ("report",)
    REPORT_FIELD_NUMBER: _ClassVar[int]
    report: str
    def __init__(self, report: _Optional[str] = ...) -> None: ...

class EvidenceRelationship(_message.Message):
    __slots__ = ("relation", "target_source_record_id", "target_source_type", "target_source_instance")
    RELATION_FIELD_NUMBER: _ClassVar[int]
    TARGET_SOURCE_RECORD_ID_FIELD_NUMBER: _ClassVar[int]
    TARGET_SOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    TARGET_SOURCE_INSTANCE_FIELD_NUMBER: _ClassVar[int]
    relation: str
    target_source_record_id: str
    target_source_type: str
    target_source_instance: str
    def __init__(self, relation: _Optional[str] = ..., target_source_record_id: _Optional[str] = ..., target_source_type: _Optional[str] = ..., target_source_instance: _Optional[str] = ...) -> None: ...

class EvidenceCausality(_message.Message):
    __slots__ = ("operation_id", "parent_operation_id", "attempt_id", "model_call_id", "subject_references", "trace_context")
    class TraceContextEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    OPERATION_ID_FIELD_NUMBER: _ClassVar[int]
    PARENT_OPERATION_ID_FIELD_NUMBER: _ClassVar[int]
    ATTEMPT_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_CALL_ID_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_REFERENCES_FIELD_NUMBER: _ClassVar[int]
    TRACE_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    operation_id: str
    parent_operation_id: str
    attempt_id: str
    model_call_id: str
    subject_references: _containers.RepeatedScalarFieldContainer[str]
    trace_context: _containers.ScalarMap[str, str]
    def __init__(self, operation_id: _Optional[str] = ..., parent_operation_id: _Optional[str] = ..., attempt_id: _Optional[str] = ..., model_call_id: _Optional[str] = ..., subject_references: _Optional[_Iterable[str]] = ..., trace_context: _Optional[_Mapping[str, str]] = ...) -> None: ...

class EvidenceEnvelope(_message.Message):
    __slots__ = ("contract_version", "source_type", "source_instance", "source_record_id", "source_version", "source_sequence", "namespace", "target_external_id", "target_kind", "evidence_type", "signal", "schema_id", "schema_version", "schema_compatibility", "observed_at_ms", "collected_at_ms", "expires_at_ms", "content_json", "relationships", "producer_identity", "confidence_bps", "classification", "provenance", "idempotency_key", "content_digest", "intent", "causality")
    class ProvenanceEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    CONTRACT_VERSION_FIELD_NUMBER: _ClassVar[int]
    SOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_INSTANCE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_RECORD_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_VERSION_FIELD_NUMBER: _ClassVar[int]
    SOURCE_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    TARGET_EXTERNAL_ID_FIELD_NUMBER: _ClassVar[int]
    TARGET_KIND_FIELD_NUMBER: _ClassVar[int]
    EVIDENCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_ID_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_VERSION_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_COMPATIBILITY_FIELD_NUMBER: _ClassVar[int]
    OBSERVED_AT_MS_FIELD_NUMBER: _ClassVar[int]
    COLLECTED_AT_MS_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_MS_FIELD_NUMBER: _ClassVar[int]
    CONTENT_JSON_FIELD_NUMBER: _ClassVar[int]
    RELATIONSHIPS_FIELD_NUMBER: _ClassVar[int]
    PRODUCER_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_BPS_FIELD_NUMBER: _ClassVar[int]
    CLASSIFICATION_FIELD_NUMBER: _ClassVar[int]
    PROVENANCE_FIELD_NUMBER: _ClassVar[int]
    IDEMPOTENCY_KEY_FIELD_NUMBER: _ClassVar[int]
    CONTENT_DIGEST_FIELD_NUMBER: _ClassVar[int]
    INTENT_FIELD_NUMBER: _ClassVar[int]
    CAUSALITY_FIELD_NUMBER: _ClassVar[int]
    contract_version: str
    source_type: str
    source_instance: str
    source_record_id: str
    source_version: str
    source_sequence: int
    namespace: str
    target_external_id: str
    target_kind: str
    evidence_type: str
    signal: str
    schema_id: str
    schema_version: str
    schema_compatibility: str
    observed_at_ms: int
    collected_at_ms: int
    expires_at_ms: int
    content_json: bytes
    relationships: _containers.RepeatedCompositeFieldContainer[EvidenceRelationship]
    producer_identity: str
    confidence_bps: int
    classification: str
    provenance: _containers.ScalarMap[str, str]
    idempotency_key: str
    content_digest: str
    intent: str
    causality: EvidenceCausality
    def __init__(self, contract_version: _Optional[str] = ..., source_type: _Optional[str] = ..., source_instance: _Optional[str] = ..., source_record_id: _Optional[str] = ..., source_version: _Optional[str] = ..., source_sequence: _Optional[int] = ..., namespace: _Optional[str] = ..., target_external_id: _Optional[str] = ..., target_kind: _Optional[str] = ..., evidence_type: _Optional[str] = ..., signal: _Optional[str] = ..., schema_id: _Optional[str] = ..., schema_version: _Optional[str] = ..., schema_compatibility: _Optional[str] = ..., observed_at_ms: _Optional[int] = ..., collected_at_ms: _Optional[int] = ..., expires_at_ms: _Optional[int] = ..., content_json: _Optional[bytes] = ..., relationships: _Optional[_Iterable[_Union[EvidenceRelationship, _Mapping]]] = ..., producer_identity: _Optional[str] = ..., confidence_bps: _Optional[int] = ..., classification: _Optional[str] = ..., provenance: _Optional[_Mapping[str, str]] = ..., idempotency_key: _Optional[str] = ..., content_digest: _Optional[str] = ..., intent: _Optional[str] = ..., causality: _Optional[_Union[EvidenceCausality, _Mapping]] = ...) -> None: ...

class EvidenceProducerCapability(_message.Message):
    __slots__ = ("producer_identity", "config_version", "source_instances", "namespaces", "evidence_types", "target_kinds", "classification_ceiling", "allowed_intents", "allow_operation_attachment", "replay_window_ms", "max_clock_skew_ms", "max_payload_bytes", "max_relationships", "rate_limit_per_minute", "revoked", "max_retained_submissions", "source_types")
    PRODUCER_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    CONFIG_VERSION_FIELD_NUMBER: _ClassVar[int]
    SOURCE_INSTANCES_FIELD_NUMBER: _ClassVar[int]
    NAMESPACES_FIELD_NUMBER: _ClassVar[int]
    EVIDENCE_TYPES_FIELD_NUMBER: _ClassVar[int]
    TARGET_KINDS_FIELD_NUMBER: _ClassVar[int]
    CLASSIFICATION_CEILING_FIELD_NUMBER: _ClassVar[int]
    ALLOWED_INTENTS_FIELD_NUMBER: _ClassVar[int]
    ALLOW_OPERATION_ATTACHMENT_FIELD_NUMBER: _ClassVar[int]
    REPLAY_WINDOW_MS_FIELD_NUMBER: _ClassVar[int]
    MAX_CLOCK_SKEW_MS_FIELD_NUMBER: _ClassVar[int]
    MAX_PAYLOAD_BYTES_FIELD_NUMBER: _ClassVar[int]
    MAX_RELATIONSHIPS_FIELD_NUMBER: _ClassVar[int]
    RATE_LIMIT_PER_MINUTE_FIELD_NUMBER: _ClassVar[int]
    REVOKED_FIELD_NUMBER: _ClassVar[int]
    MAX_RETAINED_SUBMISSIONS_FIELD_NUMBER: _ClassVar[int]
    SOURCE_TYPES_FIELD_NUMBER: _ClassVar[int]
    producer_identity: str
    config_version: int
    source_instances: _containers.RepeatedScalarFieldContainer[str]
    namespaces: _containers.RepeatedScalarFieldContainer[str]
    evidence_types: _containers.RepeatedScalarFieldContainer[str]
    target_kinds: _containers.RepeatedScalarFieldContainer[str]
    classification_ceiling: str
    allowed_intents: _containers.RepeatedScalarFieldContainer[str]
    allow_operation_attachment: bool
    replay_window_ms: int
    max_clock_skew_ms: int
    max_payload_bytes: int
    max_relationships: int
    rate_limit_per_minute: int
    revoked: bool
    max_retained_submissions: int
    source_types: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, producer_identity: _Optional[str] = ..., config_version: _Optional[int] = ..., source_instances: _Optional[_Iterable[str]] = ..., namespaces: _Optional[_Iterable[str]] = ..., evidence_types: _Optional[_Iterable[str]] = ..., target_kinds: _Optional[_Iterable[str]] = ..., classification_ceiling: _Optional[str] = ..., allowed_intents: _Optional[_Iterable[str]] = ..., allow_operation_attachment: _Optional[bool] = ..., replay_window_ms: _Optional[int] = ..., max_clock_skew_ms: _Optional[int] = ..., max_payload_bytes: _Optional[int] = ..., max_relationships: _Optional[int] = ..., rate_limit_per_minute: _Optional[int] = ..., revoked: _Optional[bool] = ..., max_retained_submissions: _Optional[int] = ..., source_types: _Optional[_Iterable[str]] = ...) -> None: ...

class EvidenceSchemaDefinition(_message.Message):
    __slots__ = ("schema_id", "schema_version", "evidence_type", "compatible_versions")
    SCHEMA_ID_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_VERSION_FIELD_NUMBER: _ClassVar[int]
    EVIDENCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    COMPATIBLE_VERSIONS_FIELD_NUMBER: _ClassVar[int]
    schema_id: str
    schema_version: str
    evidence_type: str
    compatible_versions: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, schema_id: _Optional[str] = ..., schema_version: _Optional[str] = ..., evidence_type: _Optional[str] = ..., compatible_versions: _Optional[_Iterable[str]] = ...) -> None: ...

class EvidenceSubmissionRecord(_message.Message):
    __slots__ = ("id", "producer_identity", "source_type", "source_instance", "source_record_id", "source_version", "source_sequence", "namespace", "target_external_id", "target_kind", "evidence_type", "schema_id", "schema_version", "content_digest", "classification", "intent", "lifecycle_state", "rejection_code", "rejection_summary", "observed_at_ms", "collected_at_ms", "expires_at_ms", "received_at_ms", "updated_at_ms")
    ID_FIELD_NUMBER: _ClassVar[int]
    PRODUCER_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    SOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_INSTANCE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_RECORD_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_VERSION_FIELD_NUMBER: _ClassVar[int]
    SOURCE_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    TARGET_EXTERNAL_ID_FIELD_NUMBER: _ClassVar[int]
    TARGET_KIND_FIELD_NUMBER: _ClassVar[int]
    EVIDENCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_ID_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_VERSION_FIELD_NUMBER: _ClassVar[int]
    CONTENT_DIGEST_FIELD_NUMBER: _ClassVar[int]
    CLASSIFICATION_FIELD_NUMBER: _ClassVar[int]
    INTENT_FIELD_NUMBER: _ClassVar[int]
    LIFECYCLE_STATE_FIELD_NUMBER: _ClassVar[int]
    REJECTION_CODE_FIELD_NUMBER: _ClassVar[int]
    REJECTION_SUMMARY_FIELD_NUMBER: _ClassVar[int]
    OBSERVED_AT_MS_FIELD_NUMBER: _ClassVar[int]
    COLLECTED_AT_MS_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_MS_FIELD_NUMBER: _ClassVar[int]
    RECEIVED_AT_MS_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_MS_FIELD_NUMBER: _ClassVar[int]
    id: str
    producer_identity: str
    source_type: str
    source_instance: str
    source_record_id: str
    source_version: str
    source_sequence: int
    namespace: str
    target_external_id: str
    target_kind: str
    evidence_type: str
    schema_id: str
    schema_version: str
    content_digest: str
    classification: str
    intent: str
    lifecycle_state: str
    rejection_code: str
    rejection_summary: str
    observed_at_ms: int
    collected_at_ms: int
    expires_at_ms: int
    received_at_ms: int
    updated_at_ms: int
    def __init__(self, id: _Optional[str] = ..., producer_identity: _Optional[str] = ..., source_type: _Optional[str] = ..., source_instance: _Optional[str] = ..., source_record_id: _Optional[str] = ..., source_version: _Optional[str] = ..., source_sequence: _Optional[int] = ..., namespace: _Optional[str] = ..., target_external_id: _Optional[str] = ..., target_kind: _Optional[str] = ..., evidence_type: _Optional[str] = ..., schema_id: _Optional[str] = ..., schema_version: _Optional[str] = ..., content_digest: _Optional[str] = ..., classification: _Optional[str] = ..., intent: _Optional[str] = ..., lifecycle_state: _Optional[str] = ..., rejection_code: _Optional[str] = ..., rejection_summary: _Optional[str] = ..., observed_at_ms: _Optional[int] = ..., collected_at_ms: _Optional[int] = ..., expires_at_ms: _Optional[int] = ..., received_at_ms: _Optional[int] = ..., updated_at_ms: _Optional[int] = ...) -> None: ...

class EvidenceSubmissionResult(_message.Message):
    __slots__ = ("submission", "admitted", "deduplicated", "projected")
    SUBMISSION_FIELD_NUMBER: _ClassVar[int]
    ADMITTED_FIELD_NUMBER: _ClassVar[int]
    DEDUPLICATED_FIELD_NUMBER: _ClassVar[int]
    PROJECTED_FIELD_NUMBER: _ClassVar[int]
    submission: EvidenceSubmissionRecord
    admitted: bool
    deduplicated: bool
    projected: bool
    def __init__(self, submission: _Optional[_Union[EvidenceSubmissionRecord, _Mapping]] = ..., admitted: _Optional[bool] = ..., deduplicated: _Optional[bool] = ..., projected: _Optional[bool] = ...) -> None: ...

class RegisterEvidenceProducerRequest(_message.Message):
    __slots__ = ("capability",)
    CAPABILITY_FIELD_NUMBER: _ClassVar[int]
    capability: EvidenceProducerCapability
    def __init__(self, capability: _Optional[_Union[EvidenceProducerCapability, _Mapping]] = ...) -> None: ...

class RegisterEvidenceProducerResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RegisterEvidenceSchemaRequest(_message.Message):
    __slots__ = ("definition",)
    DEFINITION_FIELD_NUMBER: _ClassVar[int]
    definition: EvidenceSchemaDefinition
    def __init__(self, definition: _Optional[_Union[EvidenceSchemaDefinition, _Mapping]] = ...) -> None: ...

class RegisterEvidenceSchemaResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SubmitEvidenceRequest(_message.Message):
    __slots__ = ("envelope",)
    ENVELOPE_FIELD_NUMBER: _ClassVar[int]
    envelope: EvidenceEnvelope
    def __init__(self, envelope: _Optional[_Union[EvidenceEnvelope, _Mapping]] = ...) -> None: ...

class SubmitEvidenceResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: EvidenceSubmissionResult
    def __init__(self, result: _Optional[_Union[EvidenceSubmissionResult, _Mapping]] = ...) -> None: ...

class SubmitEvidenceBatchRequest(_message.Message):
    __slots__ = ("envelopes",)
    ENVELOPES_FIELD_NUMBER: _ClassVar[int]
    envelopes: _containers.RepeatedCompositeFieldContainer[EvidenceEnvelope]
    def __init__(self, envelopes: _Optional[_Iterable[_Union[EvidenceEnvelope, _Mapping]]] = ...) -> None: ...

class SubmitEvidenceBatchResponse(_message.Message):
    __slots__ = ("results",)
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[EvidenceSubmissionResult]
    def __init__(self, results: _Optional[_Iterable[_Union[EvidenceSubmissionResult, _Mapping]]] = ...) -> None: ...

class GetEvidenceSubmissionRequest(_message.Message):
    __slots__ = ("submission_id",)
    SUBMISSION_ID_FIELD_NUMBER: _ClassVar[int]
    submission_id: str
    def __init__(self, submission_id: _Optional[str] = ...) -> None: ...

class GetEvidenceSubmissionResponse(_message.Message):
    __slots__ = ("submission", "lifecycle_history")
    SUBMISSION_FIELD_NUMBER: _ClassVar[int]
    LIFECYCLE_HISTORY_FIELD_NUMBER: _ClassVar[int]
    submission: EvidenceSubmissionRecord
    lifecycle_history: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, submission: _Optional[_Union[EvidenceSubmissionRecord, _Mapping]] = ..., lifecycle_history: _Optional[_Iterable[str]] = ...) -> None: ...

class ListEvidenceSubmissionsRequest(_message.Message):
    __slots__ = ("producer_identity", "source_instance", "namespace", "lifecycle_state", "target_external_id", "evidence_type", "limit", "offset")
    PRODUCER_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    SOURCE_INSTANCE_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    LIFECYCLE_STATE_FIELD_NUMBER: _ClassVar[int]
    TARGET_EXTERNAL_ID_FIELD_NUMBER: _ClassVar[int]
    EVIDENCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    producer_identity: str
    source_instance: str
    namespace: str
    lifecycle_state: str
    target_external_id: str
    evidence_type: str
    limit: int
    offset: int
    def __init__(self, producer_identity: _Optional[str] = ..., source_instance: _Optional[str] = ..., namespace: _Optional[str] = ..., lifecycle_state: _Optional[str] = ..., target_external_id: _Optional[str] = ..., evidence_type: _Optional[str] = ..., limit: _Optional[int] = ..., offset: _Optional[int] = ...) -> None: ...

class ListEvidenceSubmissionsResponse(_message.Message):
    __slots__ = ("submissions",)
    SUBMISSIONS_FIELD_NUMBER: _ClassVar[int]
    submissions: _containers.RepeatedCompositeFieldContainer[EvidenceSubmissionRecord]
    def __init__(self, submissions: _Optional[_Iterable[_Union[EvidenceSubmissionRecord, _Mapping]]] = ...) -> None: ...

class ReplayEvidenceSubmissionRequest(_message.Message):
    __slots__ = ("submission_id",)
    SUBMISSION_ID_FIELD_NUMBER: _ClassVar[int]
    submission_id: str
    def __init__(self, submission_id: _Optional[str] = ...) -> None: ...

class ReplayEvidenceSubmissionResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: EvidenceSubmissionResult
    def __init__(self, result: _Optional[_Union[EvidenceSubmissionResult, _Mapping]] = ...) -> None: ...

class RetractEvidenceRequest(_message.Message):
    __slots__ = ("submission_id", "source_version", "source_sequence", "idempotency_key", "observed_at_ms")
    SUBMISSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_VERSION_FIELD_NUMBER: _ClassVar[int]
    SOURCE_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    IDEMPOTENCY_KEY_FIELD_NUMBER: _ClassVar[int]
    OBSERVED_AT_MS_FIELD_NUMBER: _ClassVar[int]
    submission_id: str
    source_version: str
    source_sequence: int
    idempotency_key: str
    observed_at_ms: int
    def __init__(self, submission_id: _Optional[str] = ..., source_version: _Optional[str] = ..., source_sequence: _Optional[int] = ..., idempotency_key: _Optional[str] = ..., observed_at_ms: _Optional[int] = ...) -> None: ...

class RetractEvidenceResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: EvidenceSubmissionResult
    def __init__(self, result: _Optional[_Union[EvidenceSubmissionResult, _Mapping]] = ...) -> None: ...

class MarkEvidenceStaleRequest(_message.Message):
    __slots__ = ("submission_id", "source_version", "source_sequence", "idempotency_key", "observed_at_ms")
    SUBMISSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_VERSION_FIELD_NUMBER: _ClassVar[int]
    SOURCE_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    IDEMPOTENCY_KEY_FIELD_NUMBER: _ClassVar[int]
    OBSERVED_AT_MS_FIELD_NUMBER: _ClassVar[int]
    submission_id: str
    source_version: str
    source_sequence: int
    idempotency_key: str
    observed_at_ms: int
    def __init__(self, submission_id: _Optional[str] = ..., source_version: _Optional[str] = ..., source_sequence: _Optional[int] = ..., idempotency_key: _Optional[str] = ..., observed_at_ms: _Optional[int] = ...) -> None: ...

class MarkEvidenceStaleResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: EvidenceSubmissionResult
    def __init__(self, result: _Optional[_Union[EvidenceSubmissionResult, _Mapping]] = ...) -> None: ...
