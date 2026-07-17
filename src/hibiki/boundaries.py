from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import Protocol

import grpc
from grpc_health.v1 import health_pb2, health_pb2_grpc


@dataclass(frozen=True, slots=True)
class ProcessResult:
    returncode: int
    stdout: str
    stderr: str


class ProcessRunner(Protocol):
    def run(self, argv: tuple[str, ...], timeout: float) -> ProcessResult: ...


class SubprocessRunner:
    def run(self, argv: tuple[str, ...], timeout: float) -> ProcessResult:
        completed = subprocess.run(
            argv,
            capture_output=True,
            check=False,
            text=True,
            timeout=timeout,
        )
        return ProcessResult(completed.returncode, completed.stdout, completed.stderr)


@dataclass(frozen=True, slots=True)
class ProbeResult:
    ok: bool
    detail: str


class GrpcHealthProbe(Protocol):
    def check(self, target: str, service: str, timeout: float) -> ProbeResult: ...


class NativeGrpcHealthProbe:
    def check(self, target: str, service: str, timeout: float) -> ProbeResult:
        try:
            with grpc.insecure_channel(target) as channel:
                stub = health_pb2_grpc.HealthStub(channel)
                request = health_pb2.HealthCheckRequest(service=service)
                response = stub.Check(request, timeout=timeout)
        except grpc.RpcError as error:
            code = error.code().name if error.code() is not None else "UNKNOWN"
            detail = error.details() or "gRPC health check failed"
            return ProbeResult(False, f"{code}: {detail}")

        status_name = health_pb2.HealthCheckResponse.ServingStatus.Name(response.status)
        return ProbeResult(response.status == health_pb2.HealthCheckResponse.SERVING, status_name)
