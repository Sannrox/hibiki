from __future__ import annotations

import base64
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime

import pytest

from hibiki.boundaries import ProcessResult
from hibiki.discovery import (
    DiscoveryError,
    DiscoveryLimits,
    SensitiveDataError,
    discover_public_revision,
    discover_public_sources,
)


@dataclass
class FixtureRunner:
    responses: dict[tuple[str, ...], ProcessResult]
    calls: list[tuple[tuple[str, ...], float]] = field(default_factory=list)

    def run(self, argv: tuple[str, ...], timeout: float) -> ProcessResult:
        self.calls.append((argv, timeout))
        return self.responses[argv]


def result(payload: object) -> ProcessResult:
    return ProcessResult(0, json.dumps(payload), "")


def fixture_runner(*, visibility: str = "public", patch: str = "+bounded change") -> FixtureRunner:
    repository = "example/tenkai"
    revision = "abc123"
    document = "\n".join(
        (
            base64.b64encode(b"# Public design\n").decode()[:10],
            base64.b64encode(b"# Public design\n").decode()[10:],
        )
    )
    return FixtureRunner(
        {
            ("gh", "api", f"repos/{repository}"): result(
                {
                    "private": visibility != "public",
                    "visibility": visibility,
                    "default_branch": "main",
                }
            ),
            (
                "gh",
                "api",
                "--method",
                "GET",
                f"repos/{repository}/commits",
                "-f",
                "sha=main",
                "-f",
                "per_page=20",
                "-f",
                "since=2026-07-16T09:00:00Z",
            ): result([{"sha": revision}]),
            (
                "gh",
                "api",
                "--method",
                "GET",
                f"repos/{repository}/commits/{revision}",
                "-f",
                "per_page=100",
                "-f",
                "page=1",
            ): result(
                {
                    "sha": revision,
                    "html_url": f"https://github.com/{repository}/commit/{revision}",
                    "commit": {"message": "Make retries deterministic"},
                    "files": [
                        {"filename": "src/retry.py", "patch": patch},
                        {"filename": "docs/retries.md", "patch": "+documented"},
                        {"filename": "uv.lock", "patch": "+generated"},
                        {"filename": "assets/diagram.png"},
                    ],
                }
            ),
            ("gh", "api", f"repos/{repository}/commits/{revision}/check-runs"): result(
                {
                    "check_runs": [
                        {
                            "name": "test",
                            "status": "completed",
                            "conclusion": "success",
                            "html_url": "https://github.com/example/tenkai/actions/runs/1",
                        }
                    ]
                }
            ),
            (
                "gh",
                "api",
                "--method",
                "GET",
                f"repos/{repository}/contents/docs/retries.md",
                "-f",
                f"ref={revision}",
            ): result({"encoding": "base64", "content": document}),
        }
    )


def test_discovers_only_public_bounded_evidence_with_checks_and_documents() -> None:
    runner = fixture_runner()

    bundle = discover_public_sources(
        runner,
        "example/tenkai",
        since="2026-07-16T09:00:00Z",
        scanned_at=datetime(2026, 7, 17, 9, tzinfo=UTC),
    )

    assert bundle.repository == "example/tenkai"
    assert bundle.default_branch == "main"
    assert bundle.scanned_at == "2026-07-17T09:00:00Z"
    assert len(bundle.content_hash) == 64
    commit = bundle.commits[0]
    assert commit["revision"] == "abc123"
    assert commit["patches"] == [
        {"path": "src/retry.py", "patch": "+bounded change"},
        {"path": "docs/retries.md", "patch": "+documented"},
    ]
    assert commit["checks"][0]["conclusion"] == "success"
    assert commit["documents"] == [{"path": "docs/retries.md", "content": "# Public design\n"}]
    assert {entry["reason"] for entry in bundle.omissions} == {
        "generated",
        "binary_or_unavailable",
    }


def test_reloads_one_selected_public_revision_without_commit_listing() -> None:
    runner = fixture_runner()

    bundle = discover_public_revision(
        runner,
        "example/tenkai",
        "abc123",
        scanned_at=datetime(2026, 7, 17, 10, tzinfo=UTC),
    )

    assert bundle.since is None
    assert [commit["revision"] for commit in bundle.commits] == ["abc123"]
    assert not any(call[0][-1] == "repos/example/tenkai/commits" for call in runner.calls)


def test_rejects_repository_that_is_not_confirmed_public() -> None:
    runner = fixture_runner(visibility="private")

    with pytest.raises(DiscoveryError, match="not confirmed public"):
        discover_public_sources(runner, "example/tenkai", since="2026-07-16T09:00:00Z")

    assert len(runner.calls) == 1


def test_sensitive_data_preflight_runs_before_bundle_can_leave_the_machine() -> None:
    runner = fixture_runner(patch="+token = 'ghp_abcdefghijklmnopqrstuvwxyz123456'")

    with pytest.raises(SensitiveDataError, match="GitHub token"):
        discover_public_sources(runner, "example/tenkai", since="2026-07-16T09:00:00Z")


def test_visible_bundle_ceiling_fails_instead_of_sending_oversized_context() -> None:
    runner = fixture_runner(patch="+" + ("x" * 1000))

    with pytest.raises(DiscoveryError, match=r"bounded evidence is .* limit is 100 bytes"):
        discover_public_sources(
            runner,
            "example/tenkai",
            since="2026-07-16T09:00:00Z",
            limits=DiscoveryLimits(max_bundle_bytes=100),
        )


def test_file_limit_cannot_exceed_github_page_size() -> None:
    with pytest.raises(ValueError, match="100-file page limit"):
        discover_public_sources(
            fixture_runner(),
            "example/tenkai",
            limits=DiscoveryLimits(max_files_per_commit=101),
        )
