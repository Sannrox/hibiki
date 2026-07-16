from __future__ import annotations

from dataclasses import dataclass, field

from hibiki.boundaries import ProbeResult, ProcessResult
from hibiki.contracts import sekai_pb2


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
class FakeSekaiGateway:
    schema_types: dict[str, sekai_pb2.ObjectType] = field(default_factory=dict)
    objects: dict[str, sekai_pb2.Object] = field(default_factory=dict)
    schema_creates: list[str] = field(default_factory=list)
    object_creates: list[str] = field(default_factory=list)
    object_updates: list[str] = field(default_factory=list)

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
