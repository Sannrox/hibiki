from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import grpc

from hibiki.contracts import sekai_pb2, sekai_pb2_grpc

DEFAULT_PRINCIPAL = "local"


class SekaiGateway(Protocol):
    def list_schema_types(self) -> tuple[sekai_pb2.ObjectType, ...]: ...

    def create_schema_type(self, object_type: sekai_pb2.ObjectType) -> sekai_pb2.ObjectType: ...

    def find_by_external_id(self, external_id: str) -> sekai_pb2.Object | None: ...

    def create_object(self, object_: sekai_pb2.Object) -> sekai_pb2.Object: ...

    def update_object(self, object_: sekai_pb2.Object) -> sekai_pb2.Object: ...

    def record_decision(self, decision: sekai_pb2.Decision) -> sekai_pb2.Decision: ...

    def list_decisions(
        self, *, actor: str, action: str, limit: int
    ) -> tuple[sekai_pb2.Decision, ...]: ...


@dataclass(frozen=True, slots=True)
class NativeSekaiGateway:
    target: str
    timeout: float = 3.0
    principal: str = DEFAULT_PRINCIPAL

    @property
    def _metadata(self) -> tuple[tuple[str, str], ...]:
        return (("x-principal", self.principal),)

    def list_schema_types(self) -> tuple[sekai_pb2.ObjectType, ...]:
        with grpc.insecure_channel(self.target) as channel:
            response = sekai_pb2_grpc.SekaiServiceStub(channel).ListSchemaTypes(
                sekai_pb2.ListSchemaTypesRequest(),
                timeout=self.timeout,
                metadata=self._metadata,
            )
        return tuple(response.types)

    def create_schema_type(self, object_type: sekai_pb2.ObjectType) -> sekai_pb2.ObjectType:
        with grpc.insecure_channel(self.target) as channel:
            response = sekai_pb2_grpc.SekaiServiceStub(channel).CreateSchemaType(
                sekai_pb2.CreateSchemaTypeRequest(type=object_type),
                timeout=self.timeout,
                metadata=self._metadata,
            )
        return response.type

    def find_by_external_id(self, external_id: str) -> sekai_pb2.Object | None:
        try:
            with grpc.insecure_channel(self.target) as channel:
                response = sekai_pb2_grpc.SekaiServiceStub(channel).FindByExternalId(
                    sekai_pb2.FindByExternalIdRequest(external_id=external_id),
                    timeout=self.timeout,
                    metadata=self._metadata,
                )
        except grpc.RpcError as error:
            if error.code() == grpc.StatusCode.NOT_FOUND:
                return None
            raise
        return response.object

    def create_object(self, object_: sekai_pb2.Object) -> sekai_pb2.Object:
        with grpc.insecure_channel(self.target) as channel:
            response = sekai_pb2_grpc.SekaiServiceStub(channel).CreateObject(
                sekai_pb2.CreateObjectRequest(object=object_),
                timeout=self.timeout,
                metadata=self._metadata,
            )
        return response.object

    def update_object(self, object_: sekai_pb2.Object) -> sekai_pb2.Object:
        with grpc.insecure_channel(self.target) as channel:
            response = sekai_pb2_grpc.SekaiServiceStub(channel).UpdateObject(
                sekai_pb2.UpdateObjectRequest(object=object_),
                timeout=self.timeout,
                metadata=self._metadata,
            )
        return response.object

    def record_decision(self, decision: sekai_pb2.Decision) -> sekai_pb2.Decision:
        with grpc.insecure_channel(self.target) as channel:
            response = sekai_pb2_grpc.SekaiServiceStub(channel).RecordDecision(
                sekai_pb2.RecordDecisionRequest(decision=decision),
                timeout=self.timeout,
                metadata=self._metadata,
            )
        return response.decision

    def list_decisions(
        self, *, actor: str, action: str, limit: int
    ) -> tuple[sekai_pb2.Decision, ...]:
        with grpc.insecure_channel(self.target) as channel:
            response = sekai_pb2_grpc.SekaiServiceStub(channel).ListDecisions(
                sekai_pb2.ListDecisionsRequest(actor=actor, action=action, limit=limit),
                timeout=self.timeout,
                metadata=self._metadata,
            )
        return tuple(response.decisions)
