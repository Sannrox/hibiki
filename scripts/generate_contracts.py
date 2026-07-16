#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

from grpc_tools import protoc

ROOT = Path(__file__).resolve().parents[1]
PROTO_DIR = ROOT / "proto"
OUTPUT_DIR = ROOT / "src" / "hibiki" / "contracts"
MANIFEST = PROTO_DIR / "manifest.json"
CONTRACTS = ("chisei.proto", "sekai.proto")
GENERATED_SUFFIXES = ("_pb2.py", "_pb2_grpc.py", "_pb2.pyi")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate reproducible Python gRPC bindings")
    parser.add_argument("--check", action="store_true", help="fail if bindings are stale")
    parser.add_argument(
        "--update-from",
        type=Path,
        metavar="PROTO_DIR",
        help="refresh vendored public contracts before generating",
    )
    arguments = parser.parse_args(argv)

    if arguments.check and arguments.update_from:
        parser.error("--check and --update-from cannot be combined")
    if arguments.update_from:
        update_contracts(arguments.update_from)

    validate_manifest()
    if arguments.check:
        return check_generated()
    generate(PROTO_DIR, OUTPUT_DIR)
    return 0


def update_contracts(source_dir: Path) -> None:
    for name in CONTRACTS:
        source = source_dir / name
        if not source.is_file():
            raise SystemExit(f"missing source contract: {source}")
        shutil.copyfile(source, PROTO_DIR / name)
    write_manifest()


def write_manifest() -> None:
    existing = json.loads(MANIFEST.read_text())
    payload = {
        "source": existing["source"],
        "contracts": {name: digest(PROTO_DIR / name) for name in CONTRACTS},
    }
    MANIFEST.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def validate_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text())
    expected = manifest.get("contracts", {})
    mismatches = [name for name in CONTRACTS if expected.get(name) != digest(PROTO_DIR / name)]
    if mismatches:
        joined = ", ".join(mismatches)
        raise SystemExit(f"contract manifest mismatch: {joined}; use --update-from")


def check_generated() -> int:
    with tempfile.TemporaryDirectory(prefix="hibiki-contracts-") as temporary:
        candidate = Path(temporary)
        generate(PROTO_DIR, candidate)
        stale = []
        for name in generated_names():
            committed = OUTPUT_DIR / name
            generated = candidate / name
            if not committed.is_file() or committed.read_bytes() != generated.read_bytes():
                stale.append(name)
        if stale:
            print(f"generated bindings are stale: {', '.join(stale)}", file=sys.stderr)
            return 1
    print("generated bindings are current")
    return 0


def generate(proto_dir: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    arguments = [
        "grpc_tools.protoc",
        f"-I{proto_dir}",
        f"--python_out={output_dir}",
        f"--pyi_out={output_dir}",
        f"--grpc_python_out={output_dir}",
        *(str(proto_dir / name) for name in CONTRACTS),
    ]
    result = protoc.main(arguments)
    if result != 0:
        raise SystemExit(result)
    for name in CONTRACTS:
        grpc_file = output_dir / name.replace(".proto", "_pb2_grpc.py")
        module = name.replace(".proto", "_pb2")
        content = grpc_file.read_text()
        content = content.replace(f"import {module} as", f"from . import {module} as")
        grpc_file.write_text(content)


def generated_names() -> tuple[str, ...]:
    return tuple(
        name.replace(".proto", suffix) for name in CONTRACTS for suffix in GENERATED_SUFFIXES
    )


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
