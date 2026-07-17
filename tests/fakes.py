from __future__ import annotations

from dataclasses import dataclass, field

from hibiki.boundaries import ProbeResult, ProcessResult
from hibiki.contracts import chisei_pb2, sekai_pb2


@dataclass
class FakeProcessRunner:
    result: ProcessResult = field(
        default_factory=lambda: ProcessResult(0, "gh version 2.76.0\n", "")
    )
    calls: list[tuple[tuple[str, ...], float]] = field(default_factory=list)

    def run(self, argv: tuple[str, ...], timeout: float) -> ProcessResult:
        self.calls.append((argv, timeout))
        return self.result


@dataclass
class FakeGrpcHealthProbe:
    results: dict[str, ProbeResult] = field(default_factory=dict)
    calls: list[tuple[str, str, float]] = field(default_factory=list)

    def check(self, target: str, service: str, timeout: float) -> ProbeResult:
        self.calls.append((target, service, timeout))
        return self.results.get(service, ProbeResult(True, "SERVING"))


@dataclass
class FakeChiseiGateway:
    content: str | tuple[str, ...]
    plan_id: str = "operation-1"
    provider: str = "local"
    model: str = "fixture-model"
    receipt_json: str = '{"operation_id":"operation-1"}'
    receipt_complete: bool = True
    missing_surfaces: tuple[str, ...] = ()
    plan_requests: list[chisei_pb2.PlanExecutionRequest] = field(default_factory=list)
    executed_plans: list[str] = field(default_factory=list)
    receipt_requests: list[chisei_pb2.GetOperationReceiptRequest] = field(default_factory=list)

    def plan_execution(self, request: chisei_pb2.PlanExecutionRequest) -> chisei_pb2.ExecutionPlan:
        copied = chisei_pb2.PlanExecutionRequest()
        copied.CopyFrom(request)
        self.plan_requests.append(copied)
        return chisei_pb2.ExecutionPlan(
            plan_id=self.plan_id,
            input=request.input,
            resolved_model=self.model,
            executable=True,
            budget=chisei_pb2.BudgetVerdict(allowed=True),
        )

    def execute_plan(self, plan: chisei_pb2.ExecutionPlan) -> chisei_pb2.ExecutePlanResponse:
        self.executed_plans.append(plan.plan_id)
        content = (
            self.content[len(self.executed_plans) - 1]
            if isinstance(self.content, tuple)
            else self.content
        )
        return chisei_pb2.ExecutePlanResponse(
            response=chisei_pb2.PlannedChatResponse(
                content=content,
                provider=self.provider,
            ),
            executed_at=1_750_000_000_000,
        )

    def get_operation_receipt(
        self, request: chisei_pb2.GetOperationReceiptRequest
    ) -> chisei_pb2.GetOperationReceiptResponse:
        copied = chisei_pb2.GetOperationReceiptRequest()
        copied.CopyFrom(request)
        self.receipt_requests.append(copied)
        return chisei_pb2.GetOperationReceiptResponse(
            receipt_json=self.receipt_json,
            complete=self.receipt_complete,
            missing_surfaces=self.missing_surfaces,
        )


@dataclass
class FakeSekaiGateway:
    schema_types: dict[str, sekai_pb2.ObjectType] = field(default_factory=dict)
    objects: dict[str, sekai_pb2.Object] = field(default_factory=dict)
    schema_creates: list[str] = field(default_factory=list)
    object_creates: list[str] = field(default_factory=list)
    object_updates: list[str] = field(default_factory=list)
    decisions: dict[str, sekai_pb2.Decision] = field(default_factory=dict)
    evidence_producers: list[sekai_pb2.EvidenceProducerCapability] = field(default_factory=list)
    evidence_schemas: list[sekai_pb2.EvidenceSchemaDefinition] = field(default_factory=list)
    evidence_envelopes: list[sekai_pb2.EvidenceEnvelope] = field(default_factory=list)
    evidence_results: list[sekai_pb2.EvidenceSubmissionResult] = field(default_factory=list)

    def list_schema_types(self) -> tuple[sekai_pb2.ObjectType, ...]:
        return tuple(self.schema_types.values())

    def create_schema_type(self, object_type: sekai_pb2.ObjectType) -> sekai_pb2.ObjectType:
        stored = sekai_pb2.ObjectType()
        stored.CopyFrom(object_type)
        self.schema_types[stored.kind] = stored
        self.schema_creates.append(stored.kind)
        return stored

    def find_by_external_id(self, external_id: str) -> sekai_pb2.Object | None:
        for object_ in self.objects.values():
            if object_.external_id == external_id:
                found = sekai_pb2.Object()
                found.CopyFrom(object_)
                return found
        return None

    def create_object(self, object_: sekai_pb2.Object) -> sekai_pb2.Object:
        if object_.id in self.objects:
            raise ValueError(f"duplicate object id: {object_.id}")
        stored = sekai_pb2.Object()
        stored.CopyFrom(object_)
        self.objects[stored.id] = stored
        self.object_creates.append(stored.external_id)
        return stored

    def update_object(self, object_: sekai_pb2.Object) -> sekai_pb2.Object:
        if object_.id not in self.objects:
            raise ValueError(f"unknown object id: {object_.id}")
        stored = sekai_pb2.Object()
        stored.CopyFrom(object_)
        self.objects[stored.id] = stored
        self.object_updates.append(stored.external_id)
        return stored

    def record_decision(self, decision: sekai_pb2.Decision) -> sekai_pb2.Decision:
        stored = sekai_pb2.Decision()
        stored.CopyFrom(decision)
        self.decisions[stored.id] = stored
        return stored

    def list_decisions(
        self, *, actor: str, action: str, limit: int, after: int = 0
    ) -> tuple[sekai_pb2.Decision, ...]:
        matches = [
            decision
            for decision in self.decisions.values()
            if (not actor or decision.actor == actor)
            and (not action or decision.action == action)
            and decision.timestamp > after
        ]
        return tuple(sorted(matches, key=lambda decision: decision.timestamp)[:limit])

    def register_evidence_producer(self, capability: sekai_pb2.EvidenceProducerCapability) -> None:
        stored = sekai_pb2.EvidenceProducerCapability()
        stored.CopyFrom(capability)
        self.evidence_producers.append(stored)

    def register_evidence_schema(self, definition: sekai_pb2.EvidenceSchemaDefinition) -> None:
        stored = sekai_pb2.EvidenceSchemaDefinition()
        stored.CopyFrom(definition)
        self.evidence_schemas.append(stored)

    def submit_evidence(
        self, envelope: sekai_pb2.EvidenceEnvelope
    ) -> sekai_pb2.EvidenceSubmissionResult:
        stored = sekai_pb2.EvidenceEnvelope()
        stored.CopyFrom(envelope)
        self.evidence_envelopes.append(stored)
        result = sekai_pb2.EvidenceSubmissionResult(
            submission=sekai_pb2.EvidenceSubmissionRecord(
                id=f"evidence-{len(self.evidence_envelopes)}",
                producer_identity=envelope.producer_identity,
                source_type=envelope.source_type,
                source_instance=envelope.source_instance,
                source_record_id=envelope.source_record_id,
                source_version=envelope.source_version,
                source_sequence=envelope.source_sequence,
                namespace=envelope.namespace,
                target_external_id=envelope.target_external_id,
                target_kind=envelope.target_kind,
                evidence_type=envelope.evidence_type,
                schema_id=envelope.schema_id,
                schema_version=envelope.schema_version,
                content_digest=envelope.content_digest,
                lifecycle_state="available",
            ),
            admitted=True,
            projected=True,
        )
        self.evidence_results.append(result)
        return result

    def list_evidence_submissions(
        self,
        *,
        producer_identity: str,
        target_external_id: str,
        evidence_type: str,
        limit: int,
    ) -> tuple[sekai_pb2.EvidenceSubmissionRecord, ...]:
        matches = [
            result.submission
            for result in self.evidence_results
            if result.submission.producer_identity == producer_identity
            and result.submission.target_external_id == target_external_id
            and result.submission.evidence_type == evidence_type
        ]
        return tuple(matches[:limit])

    def get_evidence_submission(self, submission_id: str) -> sekai_pb2.EvidenceSubmissionRecord:
        for result in self.evidence_results:
            if result.submission.id == submission_id:
                stored = sekai_pb2.EvidenceSubmissionRecord()
                stored.CopyFrom(result.submission)
                return stored
        raise KeyError(submission_id)
