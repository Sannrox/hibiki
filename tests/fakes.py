from __future__ import annotations

from dataclasses import dataclass, field

from hibiki.boundaries import ProbeResult, ProcessResult


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
