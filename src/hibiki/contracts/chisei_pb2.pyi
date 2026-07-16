from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BudgetUsage(_message.Message):
    __slots__ = ("user_id", "tokens_used", "max_tokens", "period_type", "period_start")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    TOKENS_USED_FIELD_NUMBER: _ClassVar[int]
    MAX_TOKENS_FIELD_NUMBER: _ClassVar[int]
    PERIOD_TYPE_FIELD_NUMBER: _ClassVar[int]
    PERIOD_START_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    tokens_used: int
    max_tokens: int
    period_type: str
    period_start: int
    def __init__(self, user_id: _Optional[str] = ..., tokens_used: _Optional[int] = ..., max_tokens: _Optional[int] = ..., period_type: _Optional[str] = ..., period_start: _Optional[int] = ...) -> None: ...

class PolicyResolution(_message.Message):
    __slots__ = ("runtime", "model", "eval_regressed", "eval_regression_reason", "data_class", "route_bias", "policy_scope", "policy_version", "fallback_models")
    RUNTIME_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    EVAL_REGRESSED_FIELD_NUMBER: _ClassVar[int]
    EVAL_REGRESSION_REASON_FIELD_NUMBER: _ClassVar[int]
    DATA_CLASS_FIELD_NUMBER: _ClassVar[int]
    ROUTE_BIAS_FIELD_NUMBER: _ClassVar[int]
    POLICY_SCOPE_FIELD_NUMBER: _ClassVar[int]
    POLICY_VERSION_FIELD_NUMBER: _ClassVar[int]
    FALLBACK_MODELS_FIELD_NUMBER: _ClassVar[int]
    runtime: str
    model: str
    eval_regressed: bool
    eval_regression_reason: str
    data_class: str
    route_bias: str
    policy_scope: str
    policy_version: str
    fallback_models: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, runtime: _Optional[str] = ..., model: _Optional[str] = ..., eval_regressed: _Optional[bool] = ..., eval_regression_reason: _Optional[str] = ..., data_class: _Optional[str] = ..., route_bias: _Optional[str] = ..., policy_scope: _Optional[str] = ..., policy_version: _Optional[str] = ..., fallback_models: _Optional[_Iterable[str]] = ...) -> None: ...

class PortfolioPoint(_message.Message):
    __slots__ = ("model", "quality_score", "cost_usd_micros", "sample_count", "updated_at")
    MODEL_FIELD_NUMBER: _ClassVar[int]
    QUALITY_SCORE_FIELD_NUMBER: _ClassVar[int]
    COST_USD_MICROS_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_COUNT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    model: str
    quality_score: float
    cost_usd_micros: int
    sample_count: int
    updated_at: int
    def __init__(self, model: _Optional[str] = ..., quality_score: _Optional[float] = ..., cost_usd_micros: _Optional[int] = ..., sample_count: _Optional[int] = ..., updated_at: _Optional[int] = ...) -> None: ...

class PortfolioObjective(_message.Message):
    __slots__ = ("namespace", "mode", "budget_usd_micros", "quality_bar", "min_samples", "updated_at")
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    BUDGET_USD_MICROS_FIELD_NUMBER: _ClassVar[int]
    QUALITY_BAR_FIELD_NUMBER: _ClassVar[int]
    MIN_SAMPLES_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    namespace: str
    mode: str
    budget_usd_micros: int
    quality_bar: float
    min_samples: int
    updated_at: int
    def __init__(self, namespace: _Optional[str] = ..., mode: _Optional[str] = ..., budget_usd_micros: _Optional[int] = ..., quality_bar: _Optional[float] = ..., min_samples: _Optional[int] = ..., updated_at: _Optional[int] = ...) -> None: ...

class PortfolioTaskDemand(_message.Message):
    __slots__ = ("task_class", "expected_calls", "quality_bar", "has_quality_bar")
    TASK_CLASS_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_CALLS_FIELD_NUMBER: _ClassVar[int]
    QUALITY_BAR_FIELD_NUMBER: _ClassVar[int]
    HAS_QUALITY_BAR_FIELD_NUMBER: _ClassVar[int]
    task_class: str
    expected_calls: int
    quality_bar: float
    has_quality_bar: bool
    def __init__(self, task_class: _Optional[str] = ..., expected_calls: _Optional[int] = ..., quality_bar: _Optional[float] = ..., has_quality_bar: _Optional[bool] = ...) -> None: ...

class PortfolioAllocation(_message.Message):
    __slots__ = ("task_class", "model", "quality_score", "cost_per_call_usd_micros", "expected_calls")
    TASK_CLASS_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    QUALITY_SCORE_FIELD_NUMBER: _ClassVar[int]
    COST_PER_CALL_USD_MICROS_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_CALLS_FIELD_NUMBER: _ClassVar[int]
    task_class: str
    model: str
    quality_score: float
    cost_per_call_usd_micros: int
    expected_calls: int
    def __init__(self, task_class: _Optional[str] = ..., model: _Optional[str] = ..., quality_score: _Optional[float] = ..., cost_per_call_usd_micros: _Optional[int] = ..., expected_calls: _Optional[int] = ...) -> None: ...

class PipelineRequest(_message.Message):
    __slots__ = ("request_id", "namespace", "spec", "model", "runtime", "task_type", "priority", "task_class")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    SPEC_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    RUNTIME_FIELD_NUMBER: _ClassVar[int]
    TASK_TYPE_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    TASK_CLASS_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    namespace: str
    spec: str
    model: str
    runtime: str
    task_type: str
    priority: int
    task_class: str
    def __init__(self, request_id: _Optional[str] = ..., namespace: _Optional[str] = ..., spec: _Optional[str] = ..., model: _Optional[str] = ..., runtime: _Optional[str] = ..., task_type: _Optional[str] = ..., priority: _Optional[int] = ..., task_class: _Optional[str] = ...) -> None: ...

class StepDecision(_message.Message):
    __slots__ = ("step", "action", "reasoning", "confidence", "suggestion", "value")
    STEP_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    REASONING_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    SUGGESTION_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    step: str
    action: str
    reasoning: str
    confidence: float
    suggestion: str
    value: str
    def __init__(self, step: _Optional[str] = ..., action: _Optional[str] = ..., reasoning: _Optional[str] = ..., confidence: _Optional[float] = ..., suggestion: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class PipelineRunResult(_message.Message):
    __slots__ = ("request_id", "steps", "timestamp", "prepared_spec", "evidence_references", "memory_references")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    STEPS_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    PREPARED_SPEC_FIELD_NUMBER: _ClassVar[int]
    EVIDENCE_REFERENCES_FIELD_NUMBER: _ClassVar[int]
    MEMORY_REFERENCES_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    steps: _containers.RepeatedCompositeFieldContainer[StepDecision]
    timestamp: int
    prepared_spec: str
    evidence_references: _containers.RepeatedCompositeFieldContainer[ContextEvidenceReference]
    memory_references: _containers.RepeatedCompositeFieldContainer[MemoryContextReference]
    def __init__(self, request_id: _Optional[str] = ..., steps: _Optional[_Iterable[_Union[StepDecision, _Mapping]]] = ..., timestamp: _Optional[int] = ..., prepared_spec: _Optional[str] = ..., evidence_references: _Optional[_Iterable[_Union[ContextEvidenceReference, _Mapping]]] = ..., memory_references: _Optional[_Iterable[_Union[MemoryContextReference, _Mapping]]] = ...) -> None: ...

class MemoryContextReference(_message.Message):
    __slots__ = ("memory_id", "memory_version", "classification", "confidence_bps", "applicability", "evidence_operation_ids", "content_digest")
    MEMORY_ID_FIELD_NUMBER: _ClassVar[int]
    MEMORY_VERSION_FIELD_NUMBER: _ClassVar[int]
    CLASSIFICATION_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_BPS_FIELD_NUMBER: _ClassVar[int]
    APPLICABILITY_FIELD_NUMBER: _ClassVar[int]
    EVIDENCE_OPERATION_IDS_FIELD_NUMBER: _ClassVar[int]
    CONTENT_DIGEST_FIELD_NUMBER: _ClassVar[int]
    memory_id: str
    memory_version: int
    classification: str
    confidence_bps: int
    applicability: str
    evidence_operation_ids: _containers.RepeatedScalarFieldContainer[str]
    content_digest: str
    def __init__(self, memory_id: _Optional[str] = ..., memory_version: _Optional[int] = ..., classification: _Optional[str] = ..., confidence_bps: _Optional[int] = ..., applicability: _Optional[str] = ..., evidence_operation_ids: _Optional[_Iterable[str]] = ..., content_digest: _Optional[str] = ...) -> None: ...

class ContextEvidenceReference(_message.Message):
    __slots__ = ("submission_id", "source_type", "source_instance", "source_version", "source_sequence", "evidence_type", "schema_id", "schema_version", "content_digest", "observed_at_ms", "classification", "projection_version", "disclosed_fields")
    SUBMISSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_INSTANCE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_VERSION_FIELD_NUMBER: _ClassVar[int]
    SOURCE_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    EVIDENCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_ID_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_VERSION_FIELD_NUMBER: _ClassVar[int]
    CONTENT_DIGEST_FIELD_NUMBER: _ClassVar[int]
    OBSERVED_AT_MS_FIELD_NUMBER: _ClassVar[int]
    CLASSIFICATION_FIELD_NUMBER: _ClassVar[int]
    PROJECTION_VERSION_FIELD_NUMBER: _ClassVar[int]
    DISCLOSED_FIELDS_FIELD_NUMBER: _ClassVar[int]
    submission_id: str
    source_type: str
    source_instance: str
    source_version: str
    source_sequence: int
    evidence_type: str
    schema_id: str
    schema_version: str
    content_digest: str
    observed_at_ms: int
    classification: str
    projection_version: str
    disclosed_fields: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, submission_id: _Optional[str] = ..., source_type: _Optional[str] = ..., source_instance: _Optional[str] = ..., source_version: _Optional[str] = ..., source_sequence: _Optional[int] = ..., evidence_type: _Optional[str] = ..., schema_id: _Optional[str] = ..., schema_version: _Optional[str] = ..., content_digest: _Optional[str] = ..., observed_at_ms: _Optional[int] = ..., classification: _Optional[str] = ..., projection_version: _Optional[str] = ..., disclosed_fields: _Optional[_Iterable[str]] = ...) -> None: ...

class ChatMessage(_message.Message):
    __slots__ = ("role", "content", "tool_call_id", "tool_calls")
    ROLE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    TOOL_CALL_ID_FIELD_NUMBER: _ClassVar[int]
    TOOL_CALLS_FIELD_NUMBER: _ClassVar[int]
    role: str
    content: str
    tool_call_id: str
    tool_calls: _containers.RepeatedCompositeFieldContainer[ToolCall]
    def __init__(self, role: _Optional[str] = ..., content: _Optional[str] = ..., tool_call_id: _Optional[str] = ..., tool_calls: _Optional[_Iterable[_Union[ToolCall, _Mapping]]] = ...) -> None: ...

class ToolCall(_message.Message):
    __slots__ = ("id", "name", "args_json")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ARGS_JSON_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    args_json: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., args_json: _Optional[str] = ...) -> None: ...

class ToolDef(_message.Message):
    __slots__ = ("name", "description", "input_schema_json")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    INPUT_SCHEMA_JSON_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    input_schema_json: str
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., input_schema_json: _Optional[str] = ...) -> None: ...

class ReviewPolicy(_message.Message):
    __slots__ = ("confidence_threshold", "max_cycles", "model")
    CONFIDENCE_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    MAX_CYCLES_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    confidence_threshold: float
    max_cycles: int
    model: str
    def __init__(self, confidence_threshold: _Optional[float] = ..., max_cycles: _Optional[int] = ..., model: _Optional[str] = ...) -> None: ...

class BudgetVerdict(_message.Message):
    __slots__ = ("allowed", "usage", "reason")
    ALLOWED_FIELD_NUMBER: _ClassVar[int]
    USAGE_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    allowed: bool
    usage: BudgetUsage
    reason: str
    def __init__(self, allowed: _Optional[bool] = ..., usage: _Optional[_Union[BudgetUsage, _Mapping]] = ..., reason: _Optional[str] = ...) -> None: ...

class ExecutionInput(_message.Message):
    __slots__ = ("request_id", "namespace", "spec", "preferred_model", "preferred_runtime", "task_type", "priority", "user_id", "estimated_tokens", "messages", "tools", "system", "max_tokens", "task_class")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    SPEC_FIELD_NUMBER: _ClassVar[int]
    PREFERRED_MODEL_FIELD_NUMBER: _ClassVar[int]
    PREFERRED_RUNTIME_FIELD_NUMBER: _ClassVar[int]
    TASK_TYPE_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    ESTIMATED_TOKENS_FIELD_NUMBER: _ClassVar[int]
    MESSAGES_FIELD_NUMBER: _ClassVar[int]
    TOOLS_FIELD_NUMBER: _ClassVar[int]
    SYSTEM_FIELD_NUMBER: _ClassVar[int]
    MAX_TOKENS_FIELD_NUMBER: _ClassVar[int]
    TASK_CLASS_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    namespace: str
    spec: str
    preferred_model: str
    preferred_runtime: str
    task_type: str
    priority: int
    user_id: str
    estimated_tokens: int
    messages: _containers.RepeatedCompositeFieldContainer[ChatMessage]
    tools: _containers.RepeatedCompositeFieldContainer[ToolDef]
    system: str
    max_tokens: int
    task_class: str
    def __init__(self, request_id: _Optional[str] = ..., namespace: _Optional[str] = ..., spec: _Optional[str] = ..., preferred_model: _Optional[str] = ..., preferred_runtime: _Optional[str] = ..., task_type: _Optional[str] = ..., priority: _Optional[int] = ..., user_id: _Optional[str] = ..., estimated_tokens: _Optional[int] = ..., messages: _Optional[_Iterable[_Union[ChatMessage, _Mapping]]] = ..., tools: _Optional[_Iterable[_Union[ToolDef, _Mapping]]] = ..., system: _Optional[str] = ..., max_tokens: _Optional[int] = ..., task_class: _Optional[str] = ...) -> None: ...

class ExecutionPlan(_message.Message):
    __slots__ = ("plan_id", "input", "resolved_runtime", "resolved_model", "enriched_spec", "prepared_system", "prepared_messages", "tools", "budget", "steps", "review_policy", "risk_score", "low_success_namespace", "executable", "warnings", "max_tokens", "created_at", "affinity_namespaces", "eval_regressed", "eval_regression_reason", "sampled", "sample_rate", "sample_reason", "egress_decisions", "task_class", "evidence_references", "memory_references", "planning_actor")
    PLAN_ID_FIELD_NUMBER: _ClassVar[int]
    INPUT_FIELD_NUMBER: _ClassVar[int]
    RESOLVED_RUNTIME_FIELD_NUMBER: _ClassVar[int]
    RESOLVED_MODEL_FIELD_NUMBER: _ClassVar[int]
    ENRICHED_SPEC_FIELD_NUMBER: _ClassVar[int]
    PREPARED_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    PREPARED_MESSAGES_FIELD_NUMBER: _ClassVar[int]
    TOOLS_FIELD_NUMBER: _ClassVar[int]
    BUDGET_FIELD_NUMBER: _ClassVar[int]
    STEPS_FIELD_NUMBER: _ClassVar[int]
    REVIEW_POLICY_FIELD_NUMBER: _ClassVar[int]
    RISK_SCORE_FIELD_NUMBER: _ClassVar[int]
    LOW_SUCCESS_NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    EXECUTABLE_FIELD_NUMBER: _ClassVar[int]
    WARNINGS_FIELD_NUMBER: _ClassVar[int]
    MAX_TOKENS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    AFFINITY_NAMESPACES_FIELD_NUMBER: _ClassVar[int]
    EVAL_REGRESSED_FIELD_NUMBER: _ClassVar[int]
    EVAL_REGRESSION_REASON_FIELD_NUMBER: _ClassVar[int]
    SAMPLED_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_RATE_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_REASON_FIELD_NUMBER: _ClassVar[int]
    EGRESS_DECISIONS_FIELD_NUMBER: _ClassVar[int]
    TASK_CLASS_FIELD_NUMBER: _ClassVar[int]
    EVIDENCE_REFERENCES_FIELD_NUMBER: _ClassVar[int]
    MEMORY_REFERENCES_FIELD_NUMBER: _ClassVar[int]
    PLANNING_ACTOR_FIELD_NUMBER: _ClassVar[int]
    plan_id: str
    input: ExecutionInput
    resolved_runtime: str
    resolved_model: str
    enriched_spec: str
    prepared_system: str
    prepared_messages: _containers.RepeatedCompositeFieldContainer[ChatMessage]
    tools: _containers.RepeatedCompositeFieldContainer[ToolDef]
    budget: BudgetVerdict
    steps: _containers.RepeatedCompositeFieldContainer[StepDecision]
    review_policy: ReviewPolicy
    risk_score: float
    low_success_namespace: bool
    executable: bool
    warnings: _containers.RepeatedScalarFieldContainer[str]
    max_tokens: int
    created_at: int
    affinity_namespaces: _containers.RepeatedScalarFieldContainer[str]
    eval_regressed: bool
    eval_regression_reason: str
    sampled: bool
    sample_rate: float
    sample_reason: str
    egress_decisions: _containers.RepeatedCompositeFieldContainer[EgressDecision]
    task_class: str
    evidence_references: _containers.RepeatedCompositeFieldContainer[ContextEvidenceReference]
    memory_references: _containers.RepeatedCompositeFieldContainer[MemoryContextReference]
    planning_actor: str
    def __init__(self, plan_id: _Optional[str] = ..., input: _Optional[_Union[ExecutionInput, _Mapping]] = ..., resolved_runtime: _Optional[str] = ..., resolved_model: _Optional[str] = ..., enriched_spec: _Optional[str] = ..., prepared_system: _Optional[str] = ..., prepared_messages: _Optional[_Iterable[_Union[ChatMessage, _Mapping]]] = ..., tools: _Optional[_Iterable[_Union[ToolDef, _Mapping]]] = ..., budget: _Optional[_Union[BudgetVerdict, _Mapping]] = ..., steps: _Optional[_Iterable[_Union[StepDecision, _Mapping]]] = ..., review_policy: _Optional[_Union[ReviewPolicy, _Mapping]] = ..., risk_score: _Optional[float] = ..., low_success_namespace: _Optional[bool] = ..., executable: _Optional[bool] = ..., warnings: _Optional[_Iterable[str]] = ..., max_tokens: _Optional[int] = ..., created_at: _Optional[int] = ..., affinity_namespaces: _Optional[_Iterable[str]] = ..., eval_regressed: _Optional[bool] = ..., eval_regression_reason: _Optional[str] = ..., sampled: _Optional[bool] = ..., sample_rate: _Optional[float] = ..., sample_reason: _Optional[str] = ..., egress_decisions: _Optional[_Iterable[_Union[EgressDecision, _Mapping]]] = ..., task_class: _Optional[str] = ..., evidence_references: _Optional[_Iterable[_Union[ContextEvidenceReference, _Mapping]]] = ..., memory_references: _Optional[_Iterable[_Union[MemoryContextReference, _Mapping]]] = ..., planning_actor: _Optional[str] = ...) -> None: ...

class EgressDecision(_message.Message):
    __slots__ = ("provider", "external", "included", "redacted", "reasons")
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    EXTERNAL_FIELD_NUMBER: _ClassVar[int]
    INCLUDED_FIELD_NUMBER: _ClassVar[int]
    REDACTED_FIELD_NUMBER: _ClassVar[int]
    REASONS_FIELD_NUMBER: _ClassVar[int]
    provider: str
    external: bool
    included: _containers.RepeatedScalarFieldContainer[str]
    redacted: _containers.RepeatedScalarFieldContainer[str]
    reasons: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, provider: _Optional[str] = ..., external: _Optional[bool] = ..., included: _Optional[_Iterable[str]] = ..., redacted: _Optional[_Iterable[str]] = ..., reasons: _Optional[_Iterable[str]] = ...) -> None: ...

class PlannedChatResponse(_message.Message):
    __slots__ = ("content", "tool_calls", "input_tokens", "output_tokens", "stop_reason", "provider")
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    TOOL_CALLS_FIELD_NUMBER: _ClassVar[int]
    INPUT_TOKENS_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_TOKENS_FIELD_NUMBER: _ClassVar[int]
    STOP_REASON_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    content: str
    tool_calls: _containers.RepeatedCompositeFieldContainer[ToolCall]
    input_tokens: int
    output_tokens: int
    stop_reason: str
    provider: str
    def __init__(self, content: _Optional[str] = ..., tool_calls: _Optional[_Iterable[_Union[ToolCall, _Mapping]]] = ..., input_tokens: _Optional[int] = ..., output_tokens: _Optional[int] = ..., stop_reason: _Optional[str] = ..., provider: _Optional[str] = ...) -> None: ...

class AffinityResult(_message.Message):
    __slots__ = ("namespaces", "best_model", "low_success")
    NAMESPACES_FIELD_NUMBER: _ClassVar[int]
    BEST_MODEL_FIELD_NUMBER: _ClassVar[int]
    LOW_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    namespaces: _containers.RepeatedScalarFieldContainer[str]
    best_model: str
    low_success: bool
    def __init__(self, namespaces: _Optional[_Iterable[str]] = ..., best_model: _Optional[str] = ..., low_success: _Optional[bool] = ...) -> None: ...

class EvalAssertion(_message.Message):
    __slots__ = ("type", "value")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    type: str
    value: str
    def __init__(self, type: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class EvalCase(_message.Message):
    __slots__ = ("id", "name", "namespace", "spec", "assertions")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    SPEC_FIELD_NUMBER: _ClassVar[int]
    ASSERTIONS_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    namespace: str
    spec: str
    assertions: _containers.RepeatedCompositeFieldContainer[EvalAssertion]
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., namespace: _Optional[str] = ..., spec: _Optional[str] = ..., assertions: _Optional[_Iterable[_Union[EvalAssertion, _Mapping]]] = ...) -> None: ...

class EvalSuite(_message.Message):
    __slots__ = ("id", "name", "description", "cases")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CASES_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    cases: _containers.RepeatedCompositeFieldContainer[EvalCase]
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., cases: _Optional[_Iterable[_Union[EvalCase, _Mapping]]] = ...) -> None: ...

class CaseResult(_message.Message):
    __slots__ = ("case_id", "passed", "status", "result", "score", "reason", "elapsed")
    CASE_ID_FIELD_NUMBER: _ClassVar[int]
    PASSED_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    ELAPSED_FIELD_NUMBER: _ClassVar[int]
    case_id: str
    passed: bool
    status: str
    result: str
    score: int
    reason: str
    elapsed: int
    def __init__(self, case_id: _Optional[str] = ..., passed: _Optional[bool] = ..., status: _Optional[str] = ..., result: _Optional[str] = ..., score: _Optional[int] = ..., reason: _Optional[str] = ..., elapsed: _Optional[int] = ...) -> None: ...

class EvalRun(_message.Message):
    __slots__ = ("id", "suite_id", "config_ref", "results", "timestamp")
    ID_FIELD_NUMBER: _ClassVar[int]
    SUITE_ID_FIELD_NUMBER: _ClassVar[int]
    CONFIG_REF_FIELD_NUMBER: _ClassVar[int]
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    id: str
    suite_id: str
    config_ref: str
    results: _containers.RepeatedCompositeFieldContainer[CaseResult]
    timestamp: int
    def __init__(self, id: _Optional[str] = ..., suite_id: _Optional[str] = ..., config_ref: _Optional[str] = ..., results: _Optional[_Iterable[_Union[CaseResult, _Mapping]]] = ..., timestamp: _Optional[int] = ...) -> None: ...

class GateDecision(_message.Message):
    __slots__ = ("verdict", "reason", "baseline_score", "candidate_score")
    VERDICT_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    BASELINE_SCORE_FIELD_NUMBER: _ClassVar[int]
    CANDIDATE_SCORE_FIELD_NUMBER: _ClassVar[int]
    verdict: str
    reason: str
    baseline_score: float
    candidate_score: float
    def __init__(self, verdict: _Optional[str] = ..., reason: _Optional[str] = ..., baseline_score: _Optional[float] = ..., candidate_score: _Optional[float] = ...) -> None: ...

class EvalVarianceCase(_message.Message):
    __slots__ = ("case_id", "run_count", "pass_rate", "mean_score", "min_score", "max_score", "std_dev")
    CASE_ID_FIELD_NUMBER: _ClassVar[int]
    RUN_COUNT_FIELD_NUMBER: _ClassVar[int]
    PASS_RATE_FIELD_NUMBER: _ClassVar[int]
    MEAN_SCORE_FIELD_NUMBER: _ClassVar[int]
    MIN_SCORE_FIELD_NUMBER: _ClassVar[int]
    MAX_SCORE_FIELD_NUMBER: _ClassVar[int]
    STD_DEV_FIELD_NUMBER: _ClassVar[int]
    case_id: str
    run_count: int
    pass_rate: float
    mean_score: float
    min_score: float
    max_score: float
    std_dev: float
    def __init__(self, case_id: _Optional[str] = ..., run_count: _Optional[int] = ..., pass_rate: _Optional[float] = ..., mean_score: _Optional[float] = ..., min_score: _Optional[float] = ..., max_score: _Optional[float] = ..., std_dev: _Optional[float] = ...) -> None: ...

class EvalVariance(_message.Message):
    __slots__ = ("suite_id", "config_ref", "run_count", "mean_score", "std_dev", "min_score", "max_score", "cases")
    SUITE_ID_FIELD_NUMBER: _ClassVar[int]
    CONFIG_REF_FIELD_NUMBER: _ClassVar[int]
    RUN_COUNT_FIELD_NUMBER: _ClassVar[int]
    MEAN_SCORE_FIELD_NUMBER: _ClassVar[int]
    STD_DEV_FIELD_NUMBER: _ClassVar[int]
    MIN_SCORE_FIELD_NUMBER: _ClassVar[int]
    MAX_SCORE_FIELD_NUMBER: _ClassVar[int]
    CASES_FIELD_NUMBER: _ClassVar[int]
    suite_id: str
    config_ref: str
    run_count: int
    mean_score: float
    std_dev: float
    min_score: float
    max_score: float
    cases: _containers.RepeatedCompositeFieldContainer[EvalVarianceCase]
    def __init__(self, suite_id: _Optional[str] = ..., config_ref: _Optional[str] = ..., run_count: _Optional[int] = ..., mean_score: _Optional[float] = ..., std_dev: _Optional[float] = ..., min_score: _Optional[float] = ..., max_score: _Optional[float] = ..., cases: _Optional[_Iterable[_Union[EvalVarianceCase, _Mapping]]] = ...) -> None: ...

class EvalModelVariance(_message.Message):
    __slots__ = ("model_id", "variance")
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    VARIANCE_FIELD_NUMBER: _ClassVar[int]
    model_id: str
    variance: EvalVariance
    def __init__(self, model_id: _Optional[str] = ..., variance: _Optional[_Union[EvalVariance, _Mapping]] = ...) -> None: ...

class EvalModelComparison(_message.Message):
    __slots__ = ("suite_id", "models")
    SUITE_ID_FIELD_NUMBER: _ClassVar[int]
    MODELS_FIELD_NUMBER: _ClassVar[int]
    suite_id: str
    models: _containers.RepeatedCompositeFieldContainer[EvalModelVariance]
    def __init__(self, suite_id: _Optional[str] = ..., models: _Optional[_Iterable[_Union[EvalModelVariance, _Mapping]]] = ...) -> None: ...

class EvalIteration(_message.Message):
    __slots__ = ("id", "run_id", "suite_id", "changed_file", "diff_hash", "parent_iteration_id", "baseline_run_id", "candidate_run_id", "delta", "regressed", "created")
    ID_FIELD_NUMBER: _ClassVar[int]
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    SUITE_ID_FIELD_NUMBER: _ClassVar[int]
    CHANGED_FILE_FIELD_NUMBER: _ClassVar[int]
    DIFF_HASH_FIELD_NUMBER: _ClassVar[int]
    PARENT_ITERATION_ID_FIELD_NUMBER: _ClassVar[int]
    BASELINE_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    CANDIDATE_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    DELTA_FIELD_NUMBER: _ClassVar[int]
    REGRESSED_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    run_id: str
    suite_id: str
    changed_file: str
    diff_hash: str
    parent_iteration_id: str
    baseline_run_id: str
    candidate_run_id: str
    delta: float
    regressed: bool
    created: int
    def __init__(self, id: _Optional[str] = ..., run_id: _Optional[str] = ..., suite_id: _Optional[str] = ..., changed_file: _Optional[str] = ..., diff_hash: _Optional[str] = ..., parent_iteration_id: _Optional[str] = ..., baseline_run_id: _Optional[str] = ..., candidate_run_id: _Optional[str] = ..., delta: _Optional[float] = ..., regressed: _Optional[bool] = ..., created: _Optional[int] = ...) -> None: ...

class EvolveRecommendation(_message.Message):
    __slots__ = ("action", "reason")
    ACTION_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    action: str
    reason: str
    def __init__(self, action: _Optional[str] = ..., reason: _Optional[str] = ...) -> None: ...

class EvolveSuggestion(_message.Message):
    __slots__ = ("message", "confidence", "category")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    message: str
    confidence: float
    category: str
    def __init__(self, message: _Optional[str] = ..., confidence: _Optional[float] = ..., category: _Optional[str] = ...) -> None: ...

class EvolvePattern(_message.Message):
    __slots__ = ("pattern", "occurrences", "success_rate", "category")
    PATTERN_FIELD_NUMBER: _ClassVar[int]
    OCCURRENCES_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_RATE_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    pattern: str
    occurrences: int
    success_rate: float
    category: str
    def __init__(self, pattern: _Optional[str] = ..., occurrences: _Optional[int] = ..., success_rate: _Optional[float] = ..., category: _Optional[str] = ...) -> None: ...

class EvolveVarianceWindow(_message.Message):
    __slots__ = ("window", "total", "succeeded", "success_rate")
    WINDOW_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    SUCCEEDED_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_RATE_FIELD_NUMBER: _ClassVar[int]
    window: str
    total: int
    succeeded: int
    success_rate: float
    def __init__(self, window: _Optional[str] = ..., total: _Optional[int] = ..., succeeded: _Optional[int] = ..., success_rate: _Optional[float] = ...) -> None: ...

class EvolvePatternVariance(_message.Message):
    __slots__ = ("pattern", "sample_size", "mean_success_rate", "std_dev", "ci_95_lower", "ci_95_upper", "risk_flag", "trend", "windows")
    PATTERN_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_SIZE_FIELD_NUMBER: _ClassVar[int]
    MEAN_SUCCESS_RATE_FIELD_NUMBER: _ClassVar[int]
    STD_DEV_FIELD_NUMBER: _ClassVar[int]
    CI_95_LOWER_FIELD_NUMBER: _ClassVar[int]
    CI_95_UPPER_FIELD_NUMBER: _ClassVar[int]
    RISK_FLAG_FIELD_NUMBER: _ClassVar[int]
    TREND_FIELD_NUMBER: _ClassVar[int]
    WINDOWS_FIELD_NUMBER: _ClassVar[int]
    pattern: str
    sample_size: int
    mean_success_rate: float
    std_dev: float
    ci_95_lower: float
    ci_95_upper: float
    risk_flag: bool
    trend: str
    windows: _containers.RepeatedCompositeFieldContainer[EvolveVarianceWindow]
    def __init__(self, pattern: _Optional[str] = ..., sample_size: _Optional[int] = ..., mean_success_rate: _Optional[float] = ..., std_dev: _Optional[float] = ..., ci_95_lower: _Optional[float] = ..., ci_95_upper: _Optional[float] = ..., risk_flag: _Optional[bool] = ..., trend: _Optional[str] = ..., windows: _Optional[_Iterable[_Union[EvolveVarianceWindow, _Mapping]]] = ...) -> None: ...

class EvolveVarianceReport(_message.Message):
    __slots__ = ("patterns", "insights")
    PATTERNS_FIELD_NUMBER: _ClassVar[int]
    INSIGHTS_FIELD_NUMBER: _ClassVar[int]
    patterns: _containers.RepeatedCompositeFieldContainer[EvolvePatternVariance]
    insights: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, patterns: _Optional[_Iterable[_Union[EvolvePatternVariance, _Mapping]]] = ..., insights: _Optional[_Iterable[str]] = ...) -> None: ...

class EvolveReport(_message.Message):
    __slots__ = ("total_tasks", "succeeded", "failed", "success_rate", "patterns")
    TOTAL_TASKS_FIELD_NUMBER: _ClassVar[int]
    SUCCEEDED_FIELD_NUMBER: _ClassVar[int]
    FAILED_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_RATE_FIELD_NUMBER: _ClassVar[int]
    PATTERNS_FIELD_NUMBER: _ClassVar[int]
    total_tasks: int
    succeeded: int
    failed: int
    success_rate: float
    patterns: _containers.RepeatedCompositeFieldContainer[EvolvePattern]
    def __init__(self, total_tasks: _Optional[int] = ..., succeeded: _Optional[int] = ..., failed: _Optional[int] = ..., success_rate: _Optional[float] = ..., patterns: _Optional[_Iterable[_Union[EvolvePattern, _Mapping]]] = ...) -> None: ...

class EvolveTemplate(_message.Message):
    __slots__ = ("id", "name", "content", "created")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    content: str
    created: int
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., content: _Optional[str] = ..., created: _Optional[int] = ...) -> None: ...

class EvolveAbGroup(_message.Message):
    __slots__ = ("total", "succeeded", "success_rate")
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    SUCCEEDED_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_RATE_FIELD_NUMBER: _ClassVar[int]
    total: int
    succeeded: int
    success_rate: float
    def __init__(self, total: _Optional[int] = ..., succeeded: _Optional[int] = ..., success_rate: _Optional[float] = ...) -> None: ...

class EvolveAbReport(_message.Message):
    __slots__ = ("enhanced", "non_enhanced")
    ENHANCED_FIELD_NUMBER: _ClassVar[int]
    NON_ENHANCED_FIELD_NUMBER: _ClassVar[int]
    enhanced: EvolveAbGroup
    non_enhanced: EvolveAbGroup
    def __init__(self, enhanced: _Optional[_Union[EvolveAbGroup, _Mapping]] = ..., non_enhanced: _Optional[_Union[EvolveAbGroup, _Mapping]] = ...) -> None: ...

class CheckBudgetRequest(_message.Message):
    __slots__ = ("user_id", "estimated_tokens", "subject", "project", "agent", "key_id", "work_unit", "metric", "task_class", "mid_task", "local_free_available")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    ESTIMATED_TOKENS_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    AGENT_FIELD_NUMBER: _ClassVar[int]
    KEY_ID_FIELD_NUMBER: _ClassVar[int]
    WORK_UNIT_FIELD_NUMBER: _ClassVar[int]
    METRIC_FIELD_NUMBER: _ClassVar[int]
    TASK_CLASS_FIELD_NUMBER: _ClassVar[int]
    MID_TASK_FIELD_NUMBER: _ClassVar[int]
    LOCAL_FREE_AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    estimated_tokens: int
    subject: str
    project: str
    agent: str
    key_id: str
    work_unit: str
    metric: str
    task_class: str
    mid_task: bool
    local_free_available: bool
    def __init__(self, user_id: _Optional[str] = ..., estimated_tokens: _Optional[int] = ..., subject: _Optional[str] = ..., project: _Optional[str] = ..., agent: _Optional[str] = ..., key_id: _Optional[str] = ..., work_unit: _Optional[str] = ..., metric: _Optional[str] = ..., task_class: _Optional[str] = ..., mid_task: _Optional[bool] = ..., local_free_available: _Optional[bool] = ...) -> None: ...

class CheckBudgetResponse(_message.Message):
    __slots__ = ("allowed", "usage", "route_bias", "degradation_level", "warning")
    ALLOWED_FIELD_NUMBER: _ClassVar[int]
    USAGE_FIELD_NUMBER: _ClassVar[int]
    ROUTE_BIAS_FIELD_NUMBER: _ClassVar[int]
    DEGRADATION_LEVEL_FIELD_NUMBER: _ClassVar[int]
    WARNING_FIELD_NUMBER: _ClassVar[int]
    allowed: bool
    usage: BudgetUsage
    route_bias: str
    degradation_level: str
    warning: bool
    def __init__(self, allowed: _Optional[bool] = ..., usage: _Optional[_Union[BudgetUsage, _Mapping]] = ..., route_bias: _Optional[str] = ..., degradation_level: _Optional[str] = ..., warning: _Optional[bool] = ...) -> None: ...

class RecordUsageRequest(_message.Message):
    __slots__ = ("user_id", "tokens_used", "subject", "project", "agent", "key_id", "work_unit", "metric", "idempotency_key")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    TOKENS_USED_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    AGENT_FIELD_NUMBER: _ClassVar[int]
    KEY_ID_FIELD_NUMBER: _ClassVar[int]
    WORK_UNIT_FIELD_NUMBER: _ClassVar[int]
    METRIC_FIELD_NUMBER: _ClassVar[int]
    IDEMPOTENCY_KEY_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    tokens_used: int
    subject: str
    project: str
    agent: str
    key_id: str
    work_unit: str
    metric: str
    idempotency_key: str
    def __init__(self, user_id: _Optional[str] = ..., tokens_used: _Optional[int] = ..., subject: _Optional[str] = ..., project: _Optional[str] = ..., agent: _Optional[str] = ..., key_id: _Optional[str] = ..., work_unit: _Optional[str] = ..., metric: _Optional[str] = ..., idempotency_key: _Optional[str] = ...) -> None: ...

class RecordUsageResponse(_message.Message):
    __slots__ = ("usage",)
    USAGE_FIELD_NUMBER: _ClassVar[int]
    usage: BudgetUsage
    def __init__(self, usage: _Optional[_Union[BudgetUsage, _Mapping]] = ...) -> None: ...

class SetBudgetLimitRequest(_message.Message):
    __slots__ = ("user_id", "max_tokens", "period_type", "subject", "project", "agent", "key_id", "work_unit", "metric")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    MAX_TOKENS_FIELD_NUMBER: _ClassVar[int]
    PERIOD_TYPE_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    AGENT_FIELD_NUMBER: _ClassVar[int]
    KEY_ID_FIELD_NUMBER: _ClassVar[int]
    WORK_UNIT_FIELD_NUMBER: _ClassVar[int]
    METRIC_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    max_tokens: int
    period_type: str
    subject: str
    project: str
    agent: str
    key_id: str
    work_unit: str
    metric: str
    def __init__(self, user_id: _Optional[str] = ..., max_tokens: _Optional[int] = ..., period_type: _Optional[str] = ..., subject: _Optional[str] = ..., project: _Optional[str] = ..., agent: _Optional[str] = ..., key_id: _Optional[str] = ..., work_unit: _Optional[str] = ..., metric: _Optional[str] = ...) -> None: ...

class SetBudgetLimitResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RecordPortfolioObservationRequest(_message.Message):
    __slots__ = ("namespace", "task_class", "model", "quality_score", "cost_usd_micros", "sample_count", "updated_at")
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    TASK_CLASS_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    QUALITY_SCORE_FIELD_NUMBER: _ClassVar[int]
    COST_USD_MICROS_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_COUNT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    namespace: str
    task_class: str
    model: str
    quality_score: float
    cost_usd_micros: int
    sample_count: int
    updated_at: int
    def __init__(self, namespace: _Optional[str] = ..., task_class: _Optional[str] = ..., model: _Optional[str] = ..., quality_score: _Optional[float] = ..., cost_usd_micros: _Optional[int] = ..., sample_count: _Optional[int] = ..., updated_at: _Optional[int] = ...) -> None: ...

class RecordPortfolioObservationResponse(_message.Message):
    __slots__ = ("frontier",)
    FRONTIER_FIELD_NUMBER: _ClassVar[int]
    frontier: _containers.RepeatedCompositeFieldContainer[PortfolioPoint]
    def __init__(self, frontier: _Optional[_Iterable[_Union[PortfolioPoint, _Mapping]]] = ...) -> None: ...

class GetPortfolioFrontierRequest(_message.Message):
    __slots__ = ("namespace", "task_class")
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    TASK_CLASS_FIELD_NUMBER: _ClassVar[int]
    namespace: str
    task_class: str
    def __init__(self, namespace: _Optional[str] = ..., task_class: _Optional[str] = ...) -> None: ...

class GetPortfolioFrontierResponse(_message.Message):
    __slots__ = ("frontier",)
    FRONTIER_FIELD_NUMBER: _ClassVar[int]
    frontier: _containers.RepeatedCompositeFieldContainer[PortfolioPoint]
    def __init__(self, frontier: _Optional[_Iterable[_Union[PortfolioPoint, _Mapping]]] = ...) -> None: ...

class SetPortfolioObjectiveRequest(_message.Message):
    __slots__ = ("objective",)
    OBJECTIVE_FIELD_NUMBER: _ClassVar[int]
    objective: PortfolioObjective
    def __init__(self, objective: _Optional[_Union[PortfolioObjective, _Mapping]] = ...) -> None: ...

class SetPortfolioObjectiveResponse(_message.Message):
    __slots__ = ("objective",)
    OBJECTIVE_FIELD_NUMBER: _ClassVar[int]
    objective: PortfolioObjective
    def __init__(self, objective: _Optional[_Union[PortfolioObjective, _Mapping]] = ...) -> None: ...

class AllocatePortfolioRequest(_message.Message):
    __slots__ = ("namespace", "demands")
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    DEMANDS_FIELD_NUMBER: _ClassVar[int]
    namespace: str
    demands: _containers.RepeatedCompositeFieldContainer[PortfolioTaskDemand]
    def __init__(self, namespace: _Optional[str] = ..., demands: _Optional[_Iterable[_Union[PortfolioTaskDemand, _Mapping]]] = ...) -> None: ...

class AllocatePortfolioResponse(_message.Message):
    __slots__ = ("objective", "allocations", "total_cost_usd_micros", "total_value")
    OBJECTIVE_FIELD_NUMBER: _ClassVar[int]
    ALLOCATIONS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COST_USD_MICROS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_VALUE_FIELD_NUMBER: _ClassVar[int]
    objective: PortfolioObjective
    allocations: _containers.RepeatedCompositeFieldContainer[PortfolioAllocation]
    total_cost_usd_micros: int
    total_value: float
    def __init__(self, objective: _Optional[_Union[PortfolioObjective, _Mapping]] = ..., allocations: _Optional[_Iterable[_Union[PortfolioAllocation, _Mapping]]] = ..., total_cost_usd_micros: _Optional[int] = ..., total_value: _Optional[float] = ...) -> None: ...

class SetNamespacePolicyRequest(_message.Message):
    __slots__ = ("namespace", "allowed_runtimes", "allowed_models", "default_runtime", "default_model", "data_class")
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    ALLOWED_RUNTIMES_FIELD_NUMBER: _ClassVar[int]
    ALLOWED_MODELS_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_RUNTIME_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_MODEL_FIELD_NUMBER: _ClassVar[int]
    DATA_CLASS_FIELD_NUMBER: _ClassVar[int]
    namespace: str
    allowed_runtimes: _containers.RepeatedScalarFieldContainer[str]
    allowed_models: _containers.RepeatedScalarFieldContainer[str]
    default_runtime: str
    default_model: str
    data_class: str
    def __init__(self, namespace: _Optional[str] = ..., allowed_runtimes: _Optional[_Iterable[str]] = ..., allowed_models: _Optional[_Iterable[str]] = ..., default_runtime: _Optional[str] = ..., default_model: _Optional[str] = ..., data_class: _Optional[str] = ...) -> None: ...

class SetNamespacePolicyResponse(_message.Message):
    __slots__ = ("resolution",)
    RESOLUTION_FIELD_NUMBER: _ClassVar[int]
    resolution: PolicyResolution
    def __init__(self, resolution: _Optional[_Union[PolicyResolution, _Mapping]] = ...) -> None: ...

class ResolvePolicyRequest(_message.Message):
    __slots__ = ("namespace", "preferred_runtime", "preferred_model", "subject", "project", "agent", "key_id", "task_class", "user_id", "expected_calls", "budget_route_bias")
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    PREFERRED_RUNTIME_FIELD_NUMBER: _ClassVar[int]
    PREFERRED_MODEL_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    AGENT_FIELD_NUMBER: _ClassVar[int]
    KEY_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_CLASS_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_CALLS_FIELD_NUMBER: _ClassVar[int]
    BUDGET_ROUTE_BIAS_FIELD_NUMBER: _ClassVar[int]
    namespace: str
    preferred_runtime: str
    preferred_model: str
    subject: str
    project: str
    agent: str
    key_id: str
    task_class: str
    user_id: str
    expected_calls: int
    budget_route_bias: str
    def __init__(self, namespace: _Optional[str] = ..., preferred_runtime: _Optional[str] = ..., preferred_model: _Optional[str] = ..., subject: _Optional[str] = ..., project: _Optional[str] = ..., agent: _Optional[str] = ..., key_id: _Optional[str] = ..., task_class: _Optional[str] = ..., user_id: _Optional[str] = ..., expected_calls: _Optional[int] = ..., budget_route_bias: _Optional[str] = ...) -> None: ...

class ResolvePolicyResponse(_message.Message):
    __slots__ = ("resolution",)
    RESOLUTION_FIELD_NUMBER: _ClassVar[int]
    resolution: PolicyResolution
    def __init__(self, resolution: _Optional[_Union[PolicyResolution, _Mapping]] = ...) -> None: ...

class CheckEgressRequest(_message.Message):
    __slots__ = ("namespace", "payload", "provider", "task_class")
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    TASK_CLASS_FIELD_NUMBER: _ClassVar[int]
    namespace: str
    payload: str
    provider: str
    task_class: str
    def __init__(self, namespace: _Optional[str] = ..., payload: _Optional[str] = ..., provider: _Optional[str] = ..., task_class: _Optional[str] = ...) -> None: ...

class CheckEgressResponse(_message.Message):
    __slots__ = ("allowed", "findings", "policy_version")
    ALLOWED_FIELD_NUMBER: _ClassVar[int]
    FINDINGS_FIELD_NUMBER: _ClassVar[int]
    POLICY_VERSION_FIELD_NUMBER: _ClassVar[int]
    allowed: bool
    findings: _containers.RepeatedCompositeFieldContainer[EgressDecision]
    policy_version: str
    def __init__(self, allowed: _Optional[bool] = ..., findings: _Optional[_Iterable[_Union[EgressDecision, _Mapping]]] = ..., policy_version: _Optional[str] = ...) -> None: ...

class RunPipelineRequest(_message.Message):
    __slots__ = ("request",)
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    request: PipelineRequest
    def __init__(self, request: _Optional[_Union[PipelineRequest, _Mapping]] = ...) -> None: ...

class RunPipelineResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: PipelineRunResult
    def __init__(self, result: _Optional[_Union[PipelineRunResult, _Mapping]] = ...) -> None: ...

class ListPipelineRunsRequest(_message.Message):
    __slots__ = ("limit",)
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    limit: int
    def __init__(self, limit: _Optional[int] = ...) -> None: ...

class ListPipelineRunsResponse(_message.Message):
    __slots__ = ("runs",)
    RUNS_FIELD_NUMBER: _ClassVar[int]
    runs: _containers.RepeatedCompositeFieldContainer[PipelineRunResult]
    def __init__(self, runs: _Optional[_Iterable[_Union[PipelineRunResult, _Mapping]]] = ...) -> None: ...

class SampleObservation(_message.Message):
    __slots__ = ("request_id", "namespace", "spec", "resolved_model", "output_content", "sample_reason", "input_tokens", "output_tokens", "stop_reason", "timestamp", "task_class", "cost_usd_micros")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    SPEC_FIELD_NUMBER: _ClassVar[int]
    RESOLVED_MODEL_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_CONTENT_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_REASON_FIELD_NUMBER: _ClassVar[int]
    INPUT_TOKENS_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_TOKENS_FIELD_NUMBER: _ClassVar[int]
    STOP_REASON_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TASK_CLASS_FIELD_NUMBER: _ClassVar[int]
    COST_USD_MICROS_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    namespace: str
    spec: str
    resolved_model: str
    output_content: str
    sample_reason: str
    input_tokens: int
    output_tokens: int
    stop_reason: str
    timestamp: int
    task_class: str
    cost_usd_micros: int
    def __init__(self, request_id: _Optional[str] = ..., namespace: _Optional[str] = ..., spec: _Optional[str] = ..., resolved_model: _Optional[str] = ..., output_content: _Optional[str] = ..., sample_reason: _Optional[str] = ..., input_tokens: _Optional[int] = ..., output_tokens: _Optional[int] = ..., stop_reason: _Optional[str] = ..., timestamp: _Optional[int] = ..., task_class: _Optional[str] = ..., cost_usd_micros: _Optional[int] = ...) -> None: ...

class RecordSampleObservationRequest(_message.Message):
    __slots__ = ("observation",)
    OBSERVATION_FIELD_NUMBER: _ClassVar[int]
    observation: SampleObservation
    def __init__(self, observation: _Optional[_Union[SampleObservation, _Mapping]] = ...) -> None: ...

class RecordSampleObservationResponse(_message.Message):
    __slots__ = ("recorded",)
    RECORDED_FIELD_NUMBER: _ClassVar[int]
    recorded: bool
    def __init__(self, recorded: _Optional[bool] = ...) -> None: ...

class GatewayAuditEvent(_message.Message):
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

class RecordGatewayAuditRequest(_message.Message):
    __slots__ = ("event",)
    EVENT_FIELD_NUMBER: _ClassVar[int]
    event: GatewayAuditEvent
    def __init__(self, event: _Optional[_Union[GatewayAuditEvent, _Mapping]] = ...) -> None: ...

class RecordGatewayAuditResponse(_message.Message):
    __slots__ = ("event",)
    EVENT_FIELD_NUMBER: _ClassVar[int]
    event: GatewayAuditEvent
    def __init__(self, event: _Optional[_Union[GatewayAuditEvent, _Mapping]] = ...) -> None: ...

class PlanExecutionRequest(_message.Message):
    __slots__ = ("input",)
    INPUT_FIELD_NUMBER: _ClassVar[int]
    input: ExecutionInput
    def __init__(self, input: _Optional[_Union[ExecutionInput, _Mapping]] = ...) -> None: ...

class PlanExecutionResponse(_message.Message):
    __slots__ = ("plan",)
    PLAN_FIELD_NUMBER: _ClassVar[int]
    plan: ExecutionPlan
    def __init__(self, plan: _Optional[_Union[ExecutionPlan, _Mapping]] = ...) -> None: ...

class ExecutePlanRequest(_message.Message):
    __slots__ = ("plan",)
    PLAN_FIELD_NUMBER: _ClassVar[int]
    plan: ExecutionPlan
    def __init__(self, plan: _Optional[_Union[ExecutionPlan, _Mapping]] = ...) -> None: ...

class ExecutePlanResponse(_message.Message):
    __slots__ = ("response", "executed_at")
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    EXECUTED_AT_FIELD_NUMBER: _ClassVar[int]
    response: PlannedChatResponse
    executed_at: int
    def __init__(self, response: _Optional[_Union[PlannedChatResponse, _Mapping]] = ..., executed_at: _Optional[int] = ...) -> None: ...

class ExecutePlanStreamEvent(_message.Message):
    __slots__ = ("content_delta", "response", "done", "executed_at")
    CONTENT_DELTA_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    DONE_FIELD_NUMBER: _ClassVar[int]
    EXECUTED_AT_FIELD_NUMBER: _ClassVar[int]
    content_delta: str
    response: PlannedChatResponse
    done: bool
    executed_at: int
    def __init__(self, content_delta: _Optional[str] = ..., response: _Optional[_Union[PlannedChatResponse, _Mapping]] = ..., done: _Optional[bool] = ..., executed_at: _Optional[int] = ...) -> None: ...

class OperationEvidenceReference(_message.Message):
    __slots__ = ("kind", "reference", "content_hash", "disclosed_fields", "omitted", "omission_reason")
    KIND_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_HASH_FIELD_NUMBER: _ClassVar[int]
    DISCLOSED_FIELDS_FIELD_NUMBER: _ClassVar[int]
    OMITTED_FIELD_NUMBER: _ClassVar[int]
    OMISSION_REASON_FIELD_NUMBER: _ClassVar[int]
    kind: str
    reference: str
    content_hash: str
    disclosed_fields: _containers.RepeatedScalarFieldContainer[str]
    omitted: bool
    omission_reason: str
    def __init__(self, kind: _Optional[str] = ..., reference: _Optional[str] = ..., content_hash: _Optional[str] = ..., disclosed_fields: _Optional[_Iterable[str]] = ..., omitted: _Optional[bool] = ..., omission_reason: _Optional[str] = ...) -> None: ...

class ReportOperationEventRequest(_message.Message):
    __slots__ = ("operation_id", "event_id", "parent_event_id", "timestamp_ms", "kind", "attributes", "references")
    class AttributesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    OPERATION_ID_FIELD_NUMBER: _ClassVar[int]
    EVENT_ID_FIELD_NUMBER: _ClassVar[int]
    PARENT_EVENT_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_MS_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    REFERENCES_FIELD_NUMBER: _ClassVar[int]
    operation_id: str
    event_id: str
    parent_event_id: str
    timestamp_ms: int
    kind: str
    attributes: _containers.ScalarMap[str, str]
    references: _containers.RepeatedCompositeFieldContainer[OperationEvidenceReference]
    def __init__(self, operation_id: _Optional[str] = ..., event_id: _Optional[str] = ..., parent_event_id: _Optional[str] = ..., timestamp_ms: _Optional[int] = ..., kind: _Optional[str] = ..., attributes: _Optional[_Mapping[str, str]] = ..., references: _Optional[_Iterable[_Union[OperationEvidenceReference, _Mapping]]] = ...) -> None: ...

class ReportOperationEventResponse(_message.Message):
    __slots__ = ("event_id", "recorded", "complete", "missing_surfaces")
    EVENT_ID_FIELD_NUMBER: _ClassVar[int]
    RECORDED_FIELD_NUMBER: _ClassVar[int]
    COMPLETE_FIELD_NUMBER: _ClassVar[int]
    MISSING_SURFACES_FIELD_NUMBER: _ClassVar[int]
    event_id: str
    recorded: bool
    complete: bool
    missing_surfaces: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, event_id: _Optional[str] = ..., recorded: _Optional[bool] = ..., complete: _Optional[bool] = ..., missing_surfaces: _Optional[_Iterable[str]] = ...) -> None: ...

class AuthorizeOperationReporterRequest(_message.Message):
    __slots__ = ("operation_id", "principal", "event_kinds")
    OPERATION_ID_FIELD_NUMBER: _ClassVar[int]
    PRINCIPAL_FIELD_NUMBER: _ClassVar[int]
    EVENT_KINDS_FIELD_NUMBER: _ClassVar[int]
    operation_id: str
    principal: str
    event_kinds: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, operation_id: _Optional[str] = ..., principal: _Optional[str] = ..., event_kinds: _Optional[_Iterable[str]] = ...) -> None: ...

class AuthorizeOperationReporterResponse(_message.Message):
    __slots__ = ("authorized", "changed")
    AUTHORIZED_FIELD_NUMBER: _ClassVar[int]
    CHANGED_FIELD_NUMBER: _ClassVar[int]
    authorized: bool
    changed: bool
    def __init__(self, authorized: _Optional[bool] = ..., changed: _Optional[bool] = ...) -> None: ...

class GetOperationReceiptRequest(_message.Message):
    __slots__ = ("operation_id", "request_id", "caller_scope", "attempt")
    OPERATION_ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    CALLER_SCOPE_FIELD_NUMBER: _ClassVar[int]
    ATTEMPT_FIELD_NUMBER: _ClassVar[int]
    operation_id: str
    request_id: str
    caller_scope: str
    attempt: int
    def __init__(self, operation_id: _Optional[str] = ..., request_id: _Optional[str] = ..., caller_scope: _Optional[str] = ..., attempt: _Optional[int] = ...) -> None: ...

class ReserveGatewayRequestAliasRequest(_message.Message):
    __slots__ = ("caller_scope", "request_alias", "request_id", "operation_id")
    CALLER_SCOPE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ALIAS_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    OPERATION_ID_FIELD_NUMBER: _ClassVar[int]
    caller_scope: str
    request_alias: str
    request_id: str
    operation_id: str
    def __init__(self, caller_scope: _Optional[str] = ..., request_alias: _Optional[str] = ..., request_id: _Optional[str] = ..., operation_id: _Optional[str] = ...) -> None: ...

class ReserveGatewayRequestAliasResponse(_message.Message):
    __slots__ = ("reserved",)
    RESERVED_FIELD_NUMBER: _ClassVar[int]
    reserved: bool
    def __init__(self, reserved: _Optional[bool] = ...) -> None: ...

class ClaimGatewayRequestAliasDispatchRequest(_message.Message):
    __slots__ = ("caller_scope", "request_alias", "request_id", "operation_id", "dispatch_token")
    CALLER_SCOPE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ALIAS_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    OPERATION_ID_FIELD_NUMBER: _ClassVar[int]
    DISPATCH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    caller_scope: str
    request_alias: str
    request_id: str
    operation_id: str
    dispatch_token: str
    def __init__(self, caller_scope: _Optional[str] = ..., request_alias: _Optional[str] = ..., request_id: _Optional[str] = ..., operation_id: _Optional[str] = ..., dispatch_token: _Optional[str] = ...) -> None: ...

class ClaimGatewayRequestAliasDispatchResponse(_message.Message):
    __slots__ = ("claimed",)
    CLAIMED_FIELD_NUMBER: _ClassVar[int]
    claimed: bool
    def __init__(self, claimed: _Optional[bool] = ...) -> None: ...

class GetOperationReceiptResponse(_message.Message):
    __slots__ = ("receipt_json", "complete", "missing_surfaces")
    RECEIPT_JSON_FIELD_NUMBER: _ClassVar[int]
    COMPLETE_FIELD_NUMBER: _ClassVar[int]
    MISSING_SURFACES_FIELD_NUMBER: _ClassVar[int]
    receipt_json: str
    complete: bool
    missing_surfaces: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, receipt_json: _Optional[str] = ..., complete: _Optional[bool] = ..., missing_surfaces: _Optional[_Iterable[str]] = ...) -> None: ...

class GetAffinityRequest(_message.Message):
    __slots__ = ("namespace",)
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    namespace: str
    def __init__(self, namespace: _Optional[str] = ...) -> None: ...

class GetAffinityResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: AffinityResult
    def __init__(self, result: _Optional[_Union[AffinityResult, _Mapping]] = ...) -> None: ...

class CreateEvalSuiteRequest(_message.Message):
    __slots__ = ("suite",)
    SUITE_FIELD_NUMBER: _ClassVar[int]
    suite: EvalSuite
    def __init__(self, suite: _Optional[_Union[EvalSuite, _Mapping]] = ...) -> None: ...

class CreateEvalSuiteResponse(_message.Message):
    __slots__ = ("suite",)
    SUITE_FIELD_NUMBER: _ClassVar[int]
    suite: EvalSuite
    def __init__(self, suite: _Optional[_Union[EvalSuite, _Mapping]] = ...) -> None: ...

class ListEvalSuitesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListEvalSuitesResponse(_message.Message):
    __slots__ = ("suites",)
    SUITES_FIELD_NUMBER: _ClassVar[int]
    suites: _containers.RepeatedCompositeFieldContainer[EvalSuite]
    def __init__(self, suites: _Optional[_Iterable[_Union[EvalSuite, _Mapping]]] = ...) -> None: ...

class GetEvalSuiteRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetEvalSuiteResponse(_message.Message):
    __slots__ = ("suite",)
    SUITE_FIELD_NUMBER: _ClassVar[int]
    suite: EvalSuite
    def __init__(self, suite: _Optional[_Union[EvalSuite, _Mapping]] = ...) -> None: ...

class CreateEvalRunRequest(_message.Message):
    __slots__ = ("run", "changed_file", "diff_hash")
    RUN_FIELD_NUMBER: _ClassVar[int]
    CHANGED_FILE_FIELD_NUMBER: _ClassVar[int]
    DIFF_HASH_FIELD_NUMBER: _ClassVar[int]
    run: EvalRun
    changed_file: str
    diff_hash: str
    def __init__(self, run: _Optional[_Union[EvalRun, _Mapping]] = ..., changed_file: _Optional[str] = ..., diff_hash: _Optional[str] = ...) -> None: ...

class CreateEvalRunResponse(_message.Message):
    __slots__ = ("run",)
    RUN_FIELD_NUMBER: _ClassVar[int]
    run: EvalRun
    def __init__(self, run: _Optional[_Union[EvalRun, _Mapping]] = ...) -> None: ...

class GetEvalRunRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetEvalRunResponse(_message.Message):
    __slots__ = ("run",)
    RUN_FIELD_NUMBER: _ClassVar[int]
    run: EvalRun
    def __init__(self, run: _Optional[_Union[EvalRun, _Mapping]] = ...) -> None: ...

class ListEvalRunsRequest(_message.Message):
    __slots__ = ("suite_id",)
    SUITE_ID_FIELD_NUMBER: _ClassVar[int]
    suite_id: str
    def __init__(self, suite_id: _Optional[str] = ...) -> None: ...

class ListEvalRunsResponse(_message.Message):
    __slots__ = ("runs",)
    RUNS_FIELD_NUMBER: _ClassVar[int]
    runs: _containers.RepeatedCompositeFieldContainer[EvalRun]
    def __init__(self, runs: _Optional[_Iterable[_Union[EvalRun, _Mapping]]] = ...) -> None: ...

class TrackEvalIterationRequest(_message.Message):
    __slots__ = ("suite_id", "run_id", "changed_file", "diff_hash")
    SUITE_ID_FIELD_NUMBER: _ClassVar[int]
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    CHANGED_FILE_FIELD_NUMBER: _ClassVar[int]
    DIFF_HASH_FIELD_NUMBER: _ClassVar[int]
    suite_id: str
    run_id: str
    changed_file: str
    diff_hash: str
    def __init__(self, suite_id: _Optional[str] = ..., run_id: _Optional[str] = ..., changed_file: _Optional[str] = ..., diff_hash: _Optional[str] = ...) -> None: ...

class TrackEvalIterationResponse(_message.Message):
    __slots__ = ("iteration",)
    ITERATION_FIELD_NUMBER: _ClassVar[int]
    iteration: EvalIteration
    def __init__(self, iteration: _Optional[_Union[EvalIteration, _Mapping]] = ...) -> None: ...

class GetLatestEvalIterationRequest(_message.Message):
    __slots__ = ("changed_file",)
    CHANGED_FILE_FIELD_NUMBER: _ClassVar[int]
    changed_file: str
    def __init__(self, changed_file: _Optional[str] = ...) -> None: ...

class GetLatestEvalIterationResponse(_message.Message):
    __slots__ = ("iteration",)
    ITERATION_FIELD_NUMBER: _ClassVar[int]
    iteration: EvalIteration
    def __init__(self, iteration: _Optional[_Union[EvalIteration, _Mapping]] = ...) -> None: ...

class ListEvalIterationsRequest(_message.Message):
    __slots__ = ("suite_id", "changed_file")
    SUITE_ID_FIELD_NUMBER: _ClassVar[int]
    CHANGED_FILE_FIELD_NUMBER: _ClassVar[int]
    suite_id: str
    changed_file: str
    def __init__(self, suite_id: _Optional[str] = ..., changed_file: _Optional[str] = ...) -> None: ...

class ListEvalIterationsResponse(_message.Message):
    __slots__ = ("iterations",)
    ITERATIONS_FIELD_NUMBER: _ClassVar[int]
    iterations: _containers.RepeatedCompositeFieldContainer[EvalIteration]
    def __init__(self, iterations: _Optional[_Iterable[_Union[EvalIteration, _Mapping]]] = ...) -> None: ...

class CompareRunsRequest(_message.Message):
    __slots__ = ("baseline_id", "candidate_id")
    BASELINE_ID_FIELD_NUMBER: _ClassVar[int]
    CANDIDATE_ID_FIELD_NUMBER: _ClassVar[int]
    baseline_id: str
    candidate_id: str
    def __init__(self, baseline_id: _Optional[str] = ..., candidate_id: _Optional[str] = ...) -> None: ...

class CompareRunsResponse(_message.Message):
    __slots__ = ("decision",)
    DECISION_FIELD_NUMBER: _ClassVar[int]
    decision: GateDecision
    def __init__(self, decision: _Optional[_Union[GateDecision, _Mapping]] = ...) -> None: ...

class GetEvidenceContextGateRequest(_message.Message):
    __slots__ = ("namespace", "evidence_type", "source_type")
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    EVIDENCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    namespace: str
    evidence_type: str
    source_type: str
    def __init__(self, namespace: _Optional[str] = ..., evidence_type: _Optional[str] = ..., source_type: _Optional[str] = ...) -> None: ...

class EvidenceContextGate(_message.Message):
    __slots__ = ("evidence_type", "profile_key", "allowed", "verdict", "reason", "iteration_id", "baseline_run_id", "candidate_run_id", "expected_baseline_config_ref", "expected_candidate_config_ref", "source_type")
    EVIDENCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PROFILE_KEY_FIELD_NUMBER: _ClassVar[int]
    ALLOWED_FIELD_NUMBER: _ClassVar[int]
    VERDICT_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    ITERATION_ID_FIELD_NUMBER: _ClassVar[int]
    BASELINE_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    CANDIDATE_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_BASELINE_CONFIG_REF_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_CANDIDATE_CONFIG_REF_FIELD_NUMBER: _ClassVar[int]
    SOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    evidence_type: str
    profile_key: str
    allowed: bool
    verdict: str
    reason: str
    iteration_id: str
    baseline_run_id: str
    candidate_run_id: str
    expected_baseline_config_ref: str
    expected_candidate_config_ref: str
    source_type: str
    def __init__(self, evidence_type: _Optional[str] = ..., profile_key: _Optional[str] = ..., allowed: _Optional[bool] = ..., verdict: _Optional[str] = ..., reason: _Optional[str] = ..., iteration_id: _Optional[str] = ..., baseline_run_id: _Optional[str] = ..., candidate_run_id: _Optional[str] = ..., expected_baseline_config_ref: _Optional[str] = ..., expected_candidate_config_ref: _Optional[str] = ..., source_type: _Optional[str] = ...) -> None: ...

class GetEvidenceContextGateResponse(_message.Message):
    __slots__ = ("gate",)
    GATE_FIELD_NUMBER: _ClassVar[int]
    gate: EvidenceContextGate
    def __init__(self, gate: _Optional[_Union[EvidenceContextGate, _Mapping]] = ...) -> None: ...

class EvalVarianceRequest(_message.Message):
    __slots__ = ("suite_id", "config_ref")
    SUITE_ID_FIELD_NUMBER: _ClassVar[int]
    CONFIG_REF_FIELD_NUMBER: _ClassVar[int]
    suite_id: str
    config_ref: str
    def __init__(self, suite_id: _Optional[str] = ..., config_ref: _Optional[str] = ...) -> None: ...

class EvalVarianceResponse(_message.Message):
    __slots__ = ("variance",)
    VARIANCE_FIELD_NUMBER: _ClassVar[int]
    variance: EvalVariance
    def __init__(self, variance: _Optional[_Union[EvalVariance, _Mapping]] = ...) -> None: ...

class EvalModelCompareRequest(_message.Message):
    __slots__ = ("suite_id",)
    SUITE_ID_FIELD_NUMBER: _ClassVar[int]
    suite_id: str
    def __init__(self, suite_id: _Optional[str] = ...) -> None: ...

class EvalModelCompareResponse(_message.Message):
    __slots__ = ("comparison",)
    COMPARISON_FIELD_NUMBER: _ClassVar[int]
    comparison: EvalModelComparison
    def __init__(self, comparison: _Optional[_Union[EvalModelComparison, _Mapping]] = ...) -> None: ...

class EvolveSuggestRequest(_message.Message):
    __slots__ = ("request_id",)
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    def __init__(self, request_id: _Optional[str] = ...) -> None: ...

class EvolveSuggestResponse(_message.Message):
    __slots__ = ("suggestions",)
    SUGGESTIONS_FIELD_NUMBER: _ClassVar[int]
    suggestions: _containers.RepeatedCompositeFieldContainer[EvolveSuggestion]
    def __init__(self, suggestions: _Optional[_Iterable[_Union[EvolveSuggestion, _Mapping]]] = ...) -> None: ...

class EvolveEnhanceRequest(_message.Message):
    __slots__ = ("request_id", "spec")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    SPEC_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    spec: str
    def __init__(self, request_id: _Optional[str] = ..., spec: _Optional[str] = ...) -> None: ...

class EvolveEnhanceResponse(_message.Message):
    __slots__ = ("enhanced_spec", "modified")
    ENHANCED_SPEC_FIELD_NUMBER: _ClassVar[int]
    MODIFIED_FIELD_NUMBER: _ClassVar[int]
    enhanced_spec: str
    modified: bool
    def __init__(self, enhanced_spec: _Optional[str] = ..., modified: _Optional[bool] = ...) -> None: ...

class EvolveRecommendRequest(_message.Message):
    __slots__ = ("request_id",)
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    def __init__(self, request_id: _Optional[str] = ...) -> None: ...

class EvolveRecommendResponse(_message.Message):
    __slots__ = ("recommendation",)
    RECOMMENDATION_FIELD_NUMBER: _ClassVar[int]
    recommendation: EvolveRecommendation
    def __init__(self, recommendation: _Optional[_Union[EvolveRecommendation, _Mapping]] = ...) -> None: ...

class EvolveReportRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class EvolveReportResponse(_message.Message):
    __slots__ = ("report",)
    REPORT_FIELD_NUMBER: _ClassVar[int]
    report: EvolveReport
    def __init__(self, report: _Optional[_Union[EvolveReport, _Mapping]] = ...) -> None: ...

class EvolvePatternsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class EvolvePatternsResponse(_message.Message):
    __slots__ = ("patterns",)
    PATTERNS_FIELD_NUMBER: _ClassVar[int]
    patterns: _containers.RepeatedCompositeFieldContainer[EvolvePattern]
    def __init__(self, patterns: _Optional[_Iterable[_Union[EvolvePattern, _Mapping]]] = ...) -> None: ...

class EvolveVarianceRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class EvolveVarianceResponse(_message.Message):
    __slots__ = ("report",)
    REPORT_FIELD_NUMBER: _ClassVar[int]
    report: EvolveVarianceReport
    def __init__(self, report: _Optional[_Union[EvolveVarianceReport, _Mapping]] = ...) -> None: ...

class EvolveAbResultsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class EvolveAbResultsResponse(_message.Message):
    __slots__ = ("report",)
    REPORT_FIELD_NUMBER: _ClassVar[int]
    report: EvolveAbReport
    def __init__(self, report: _Optional[_Union[EvolveAbReport, _Mapping]] = ...) -> None: ...

class EvolveTemplatesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class EvolveTemplatesResponse(_message.Message):
    __slots__ = ("templates",)
    TEMPLATES_FIELD_NUMBER: _ClassVar[int]
    templates: _containers.RepeatedCompositeFieldContainer[EvolveTemplate]
    def __init__(self, templates: _Optional[_Iterable[_Union[EvolveTemplate, _Mapping]]] = ...) -> None: ...
