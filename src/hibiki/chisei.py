from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import grpc

from hibiki.contracts import chisei_pb2, chisei_pb2_grpc


class ChiseiGateway(Protocol):
    def plan_execution(
        self, request: chisei_pb2.PlanExecutionRequest
    ) -> chisei_pb2.ExecutionPlan: ...

    def execute_plan(self, plan: chisei_pb2.ExecutionPlan) -> chisei_pb2.ExecutePlanResponse: ...

    def get_operation_receipt(
        self, request: chisei_pb2.GetOperationReceiptRequest
    ) -> chisei_pb2.GetOperationReceiptResponse: ...


@dataclass(frozen=True, slots=True)
class NativeChiseiGateway:
    target: str
    timeout: float = 30.0

    def plan_execution(self, request: chisei_pb2.PlanExecutionRequest) -> chisei_pb2.ExecutionPlan:
        with grpc.insecure_channel(self.target) as channel:
            response = chisei_pb2_grpc.ChiseiServiceStub(channel).PlanExecution(
                request, timeout=self.timeout
            )
        return response.plan

    def execute_plan(self, plan: chisei_pb2.ExecutionPlan) -> chisei_pb2.ExecutePlanResponse:
        with grpc.insecure_channel(self.target) as channel:
            return chisei_pb2_grpc.ChiseiServiceStub(channel).ExecutePlan(
                chisei_pb2.ExecutePlanRequest(plan=plan), timeout=self.timeout
            )

    def get_operation_receipt(
        self, request: chisei_pb2.GetOperationReceiptRequest
    ) -> chisei_pb2.GetOperationReceiptResponse:
        with grpc.insecure_channel(self.target) as channel:
            return chisei_pb2_grpc.ChiseiServiceStub(channel).GetOperationReceipt(
                request, timeout=self.timeout
            )
