from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import grpc

from hibiki import channels
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

    def register_evidence_producer(
        self, capability: sekai_pb2.EvidenceProducerCapability
    ) -> None: ...

    def register_evidence_schema(self, definition: sekai_pb2.EvidenceSchemaDefinition) -> None: ...

    def submit_evidence(
        self, envelope: sekai_pb2.EvidenceEnvelope
    ) -> sekai_pb2.EvidenceSubmissionResult: ...

    def list_evidence_submissions(
        self,
        *,
        producer_identity: str,
        target_external_id: str,
        evidence_type: str,
        limit: int,
    ) -> tuple[sekai_pb2.EvidenceSubmissionRecord, ...]: ...

    def get_evidence_submission(self, submission_id: str) -> sekai_pb2.EvidenceSubmissionRecord: ...

    def list_objects_by_kind(
        self, *, kind: str, namespace: str, limit: int
    ) -> tuple[sekai_pb2.Object, ...]: ...


@dataclass(frozen=True, slots=True)
class NativeSekaiGateway:
    target: str
    timeout: float = 3.0
    principal: str = DEFAULT_PRINCIPAL

    @property
    def _metadata(self) -> tuple[tuple[str, str], ...]:
        return (("x-principal", self.principal),)

    def list_schema_types(self) -> tuple[sekai_pb2.ObjectType, ...]:
        with channels.insecure_channel(self.target) as channel:
            response = sekai_pb2_grpc.SekaiServiceStub(channel).ListSchemaTypes(
                sekai_pb2.ListSchemaTypesRequest(),
                timeout=self.timeout,
                metadata=self._metadata,
            )
        return tuple(response.types)

    def create_schema_type(self, object_type: sekai_pb2.ObjectType) -> sekai_pb2.ObjectType:
        with channels.insecure_channel(self.target) as channel:
            response = sekai_pb2_grpc.SekaiServiceStub(channel).CreateSchemaType(
                sekai_pb2.CreateSchemaTypeRequest(type=object_type),
                timeout=self.timeout,
                metadata=self._metadata,
            )
        return response.type

    def find_by_external_id(self, external_id: str) -> sekai_pb2.Object | None:
        try:
            with channels.insecure_channel(self.target) as channel:
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
        with channels.insecure_channel(self.target) as channel:
            response = sekai_pb2_grpc.SekaiServiceStub(channel).CreateObject(
                sekai_pb2.CreateObjectRequest(object=object_),
                timeout=self.timeout,
                metadata=self._metadata,
            )
        return response.object

    def update_object(self, object_: sekai_pb2.Object) -> sekai_pb2.Object:
        with channels.insecure_channel(self.target) as channel:
            response = sekai_pb2_grpc.SekaiServiceStub(channel).UpdateObject(
                sekai_pb2.UpdateObjectRequest(object=object_),
                timeout=self.timeout,
                metadata=self._metadata,
            )
        return response.object

    def record_decision(self, decision: sekai_pb2.Decision) -> sekai_pb2.Decision:
        with channels.insecure_channel(self.target) as channel:
            response = sekai_pb2_grpc.SekaiServiceStub(channel).RecordDecision(
                sekai_pb2.RecordDecisionRequest(decision=decision),
                timeout=self.timeout,
                metadata=self._metadata,
            )
        return response.decision

    def list_decisions(
        self, *, actor: str, action: str, limit: int
    ) -> tuple[sekai_pb2.Decision, ...]:
        with channels.insecure_channel(self.target) as channel:
            response = sekai_pb2_grpc.SekaiServiceStub(channel).ListDecisions(
                sekai_pb2.ListDecisionsRequest(actor=actor, action=action, limit=limit),
                timeout=self.timeout,
                metadata=self._metadata,
            )
        return tuple(response.decisions)

    def register_evidence_producer(self, capability: sekai_pb2.EvidenceProducerCapability) -> None:
        with channels.insecure_channel(self.target) as channel:
            sekai_pb2_grpc.SekaiServiceStub(channel).RegisterEvidenceProducer(
                sekai_pb2.RegisterEvidenceProducerRequest(capability=capability),
                timeout=self.timeout,
                metadata=self._metadata,
            )

    def register_evidence_schema(self, definition: sekai_pb2.EvidenceSchemaDefinition) -> None:
        with channels.insecure_channel(self.target) as channel:
            sekai_pb2_grpc.SekaiServiceStub(channel).RegisterEvidenceSchema(
                sekai_pb2.RegisterEvidenceSchemaRequest(definition=definition),
                timeout=self.timeout,
                metadata=self._metadata,
            )

    def submit_evidence(
        self, envelope: sekai_pb2.EvidenceEnvelope
    ) -> sekai_pb2.EvidenceSubmissionResult:
        with channels.insecure_channel(self.target) as channel:
            response = sekai_pb2_grpc.SekaiServiceStub(channel).SubmitEvidence(
                sekai_pb2.SubmitEvidenceRequest(envelope=envelope),
                timeout=self.timeout,
                metadata=(("x-principal", envelope.producer_identity),),
            )
        return response.result

    def list_evidence_submissions(
        self,
        *,
        producer_identity: str,
        target_external_id: str,
        evidence_type: str,
        limit: int,
    ) -> tuple[sekai_pb2.EvidenceSubmissionRecord, ...]:
        with channels.insecure_channel(self.target) as channel:
            response = sekai_pb2_grpc.SekaiServiceStub(channel).ListEvidenceSubmissions(
                sekai_pb2.ListEvidenceSubmissionsRequest(
                    producer_identity=producer_identity,
                    target_external_id=target_external_id,
                    evidence_type=evidence_type,
                    limit=limit,
                ),
                timeout=self.timeout,
                metadata=(("x-principal", producer_identity),),
            )
        return tuple(response.submissions)

    def get_evidence_submission(self, submission_id: str) -> sekai_pb2.EvidenceSubmissionRecord:
        with channels.insecure_channel(self.target) as channel:
            response = sekai_pb2_grpc.SekaiServiceStub(channel).GetEvidenceSubmission(
                sekai_pb2.GetEvidenceSubmissionRequest(submission_id=submission_id),
                timeout=self.timeout,
                metadata=self._metadata,
            )
        return response.submission

    def list_objects_by_kind(
        self, *, kind: str, namespace: str, limit: int
    ) -> tuple[sekai_pb2.Object, ...]:
        with channels.insecure_channel(self.target) as channel:
            response = sekai_pb2_grpc.SekaiServiceStub(channel).ListObjects(
                sekai_pb2.ListObjectsRequest(
                    filter=sekai_pb2.ListFilter(kind=kind, namespace=namespace, limit=limit)
                ),
                timeout=self.timeout,
                metadata=self._metadata,
            )
        return tuple(response.objects)
