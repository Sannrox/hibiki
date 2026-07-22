from __future__ import annotations

import base64
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime

import pytest

from hibiki.boundaries import ProcessResult
from hibiki.discovery import (
    EVIDENCE_BYTES_PER_TOKEN,
    MODEL_CONTEXT_TOKENS,
    PROMPT_OVERHEAD_TOKEN_RESERVE,
    RESPONSE_TOKEN_RESERVE,
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


def fixture_runner(
    *,
    visibility: str = "public",
    patch: str = "+bounded change",
    document_text: bytes = b"# Public design\n",
) -> FixtureRunner:
    repository = "example/tenkai"
    revision = "abc123"
    document = "\n".join(
        (
            base64.b64encode(document_text).decode()[:10],
            base64.b64encode(document_text).decode()[10:],
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


def test_oversized_document_is_truncated_rather_than_dropped() -> None:
    runner = fixture_runner()

    bundle = discover_public_sources(
        runner,
        "example/tenkai",
        since="2026-07-16T09:00:00Z",
        limits=DiscoveryLimits(max_document_bytes=4),
    )

    # Dropping the document whole would leave drafting with nothing to quote, so
    # the leading bytes survive and the truncation is recorded.
    assert len(bundle.commits) == 1
    assert bundle.commits[0]["documents"] == [{"path": "docs/retries.md", "content": "# Pu"}]
    assert "document_truncated" in {entry["reason"] for entry in bundle.omissions}


def test_commit_exceeding_bundle_budget_is_omitted_instead_of_aborting() -> None:
    runner = fixture_runner(patch="+" + ("x" * 4000))

    bundle = discover_public_sources(
        runner,
        "example/tenkai",
        since="2026-07-16T09:00:00Z",
        limits=DiscoveryLimits(max_bundle_bytes=1500),
    )

    # A commit that would overflow the budget is dropped, not fatal.
    assert bundle.commits == ()
    assert {entry["reason"] for entry in bundle.omissions} == {"bundle_budget_exceeded"}


def test_selected_revision_sheds_attachments_instead_of_aborting() -> None:
    runner = fixture_runner(patch="+" + ("x" * 4000))

    bundle = discover_public_revision(
        runner,
        "example/tenkai",
        "abc123",
        limits=DiscoveryLimits(max_bundle_bytes=1500),
    )

    # Drafting has no later commit to fall back to, so the revision survives with
    # its largest attachment shed rather than failing outright, and shedding stops
    # as soon as the payload fits instead of stripping every remaining patch.
    commit = bundle.commits[0]
    assert commit["revision"] == "abc123"
    assert commit["patches"] == [{"path": "docs/retries.md", "patch": "+documented"}]
    assert commit["documents"] == [{"path": "docs/retries.md", "content": "# Public design\n"}]
    # The full changed-file list stays, so the shed patch is still attributable.
    assert "src/retry.py" in commit["changed_files"]
    assert {"revision": "abc123", "path": "src/retry.py", "reason": "bundle_budget_exceeded"} in (
        bundle.omissions
    )


def test_shedding_sacrifices_patches_before_the_documents_a_post_quotes() -> None:
    # The report is the single largest item in the bundle (~2.4 kB against a
    # ~0.4 kB patch), so shedding purely by size would discard it first and
    # leave drafting with nothing concrete to quote.
    report = b"# Benchmark report\n" + b"result row\n" * 200
    runner = fixture_runner(patch="+" + ("x" * 400), document_text=report)

    bundle = discover_public_revision(
        runner,
        "example/tenkai",
        "abc123",
        limits=DiscoveryLimits(max_bundle_bytes=3_400, max_document_bytes=100_000),
    )

    # The smaller patch is sacrificed; the larger report survives intact.
    commit = bundle.commits[0]
    assert commit["documents"] == [{"path": "docs/retries.md", "content": report.decode()}]
    assert [entry["path"] for entry in commit["patches"]] == ["docs/retries.md"]
    assert {"revision": "abc123", "path": "src/retry.py", "reason": "bundle_budget_exceeded"} in (
        bundle.omissions
    )


def test_default_bundle_cap_leaves_room_for_the_model_context() -> None:
    limits = DiscoveryLimits()
    # The cap only protects the request if the evidence plus the reserved
    # response still fit the context window the served model actually has.
    worst_case_prompt_tokens = limits.max_bundle_bytes / EVIDENCE_BYTES_PER_TOKEN
    assert (
        worst_case_prompt_tokens + RESPONSE_TOKEN_RESERVE + PROMPT_OVERHEAD_TOKEN_RESERVE
        <= MODEL_CONTEXT_TOKENS
    )
    # No single file may consume the whole bundle.
    assert max(limits.max_patch_bytes, limits.max_document_bytes) < limits.max_bundle_bytes / 2


def test_file_limit_cannot_exceed_github_page_size() -> None:
    with pytest.raises(ValueError, match="100-file page limit"):
        discover_public_sources(
            fixture_runner(),
            "example/tenkai",
            limits=DiscoveryLimits(max_files_per_commit=101),
        )
