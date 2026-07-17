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
    inputs: list[str | None] = field(default_factory=list)

    def run(
        self,
        argv: tuple[str, ...],
        timeout: float,
        *,
        input_text: str | None = None,
    ) -> ProcessResult:
        self.calls.append((argv, timeout))
        self.inputs.append(input_text)
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
        self, *, actor: str, action: str, limit: int
    ) -> tuple[sekai_pb2.Decision, ...]:
        matches = [
            decision
            for decision in self.decisions.values()
            if (not actor or decision.actor == actor) and (not action or decision.action == action)
        ]
        return tuple(sorted(matches, key=lambda decision: decision.timestamp, reverse=True)[:limit])
