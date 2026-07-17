from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from hibiki.contracts import chisei_pb2, chisei_pb2_grpc, sekai_pb2, sekai_pb2_grpc

ROOT = Path(__file__).resolve().parents[1]


def test_public_contracts_expose_required_native_services() -> None:
    chisei_methods = chisei_pb2.DESCRIPTOR.services_by_name["ChiseiService"].methods_by_name
    sekai_methods = sekai_pb2.DESCRIPTOR.services_by_name["SekaiService"].methods_by_name
    assert "PlanExecution" in chisei_methods
    assert "ExecutePlan" in chisei_methods
    assert "SubmitEvidence" in sekai_methods
    assert hasattr(chisei_pb2_grpc, "ChiseiServiceStub")
    assert hasattr(sekai_pb2_grpc, "SekaiServiceStub")


def test_generated_bindings_are_reproducible() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/generate_contracts.py", "--check"],
        cwd=ROOT,
        capture_output=True,
        check=False,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert completed.stdout == "generated bindings are current\n"


def test_list_objects_request_uses_list_filter() -> None:
    request = sekai_pb2.ListObjectsRequest(
        filter=sekai_pb2.ListFilter(kind="hibiki.outcome", namespace="hibiki", limit=100)
    )
    assert request.filter.kind == "hibiki.outcome"
    assert request.filter.namespace == "hibiki"
    assert request.filter.limit == 100
