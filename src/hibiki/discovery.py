from __future__ import annotations

import base64
import hashlib
import json
import re
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from hibiki.boundaries import ProcessRunner


class DiscoveryError(RuntimeError):
    """Raised when public source discovery cannot complete safely."""


class SensitiveDataError(DiscoveryError):
    """Raised when the local evidence preflight finds sensitive material."""


# Bounded evidence has to survive two independent limits: our own byte cap and
# the served model's context window. The byte cap is the one we control, so it
# is sized to fit inside the smaller of the two. Chisei does not report the
# resolved model's context window on the execution plan, so the derivation is
# stated here rather than negotiated at runtime; a deployment on a larger model
# raises it by passing its own DiscoveryLimits.
MODEL_CONTEXT_TOKENS = 16_384
# The largest response reservation any Hibiki call site makes (drafting and
# claim validation both ask for 1_500).
RESPONSE_TOKEN_RESERVE = 1_500
# System prompt, task framing, response schema, and Chisei's spec enrichment.
PROMPT_OVERHEAD_TOKEN_RESERVE = 1_400
# Minified JSON carrying diffs measured ~3.3 bytes per token against the
# deployed tokenizer; 2.6 leaves margin for punctuation- or unicode-dense
# evidence that tokenizes worse than the sample.
EVIDENCE_BYTES_PER_TOKEN = 2.6

MAX_BUNDLE_BYTES = int(
    (MODEL_CONTEXT_TOKENS - RESPONSE_TOKEN_RESERVE - PROMPT_OVERHEAD_TOKEN_RESERVE)
    * EVIDENCE_BYTES_PER_TOKEN
)


@dataclass(frozen=True, slots=True)
class DiscoveryLimits:
    max_commits: int = 20
    max_files_per_commit: int = 100
    max_bundle_bytes: int = MAX_BUNDLE_BYTES
    # Held well below the bundle cap so no single file can crowd out every other
    # piece of evidence in a one-commit bundle. Documents get the larger share:
    # they are the prose drafting actually quotes, where a patch mainly has to
    # show that a change happened.
    max_patch_bytes: int = 8_000
    max_document_bytes: int = 12_000
    timeout: float = 15.0


@dataclass(frozen=True, slots=True)
class EvidenceBundle:
    repository: str
    default_branch: str
    scanned_at: str
    since: str | None
    commits: tuple[dict[str, Any], ...]
    omissions: tuple[dict[str, str], ...]
    content_hash: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "repository": self.repository,
            "default_branch": self.default_branch,
            "scanned_at": self.scanned_at,
            "since": self.since,
            "commits": list(self.commits),
            "omissions": list(self.omissions),
            "content_hash": self.content_hash,
        }


_SECRET_PATTERNS = (
    ("private key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("GitHub token", re.compile(r"\bgh[opusr]_[A-Za-z0-9_]{20,}\b")),
    ("OpenAI key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("AWS access key", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    (
        "credential assignment",
        re.compile(
            r"(?i)\b(?:api[_-]?key|password|secret|token)\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{16,}"
        ),
    ),
    ("local home path", re.compile(r"/(?:Users|home)/[^/\s]+/")),
)

_GENERATED_PATH_PATTERNS = (
    re.compile(r"(?:^|/)(?:dist|build|vendor|node_modules)/"),
    re.compile(r"(?:^|/).*_pb2(?:_grpc)?\.py$"),
    re.compile(r"(?:^|/).*\.min\.(?:css|js)$"),
    re.compile(r"(?:^|/)(?:uv\.lock|package-lock\.json|pnpm-lock\.yaml|yarn\.lock)$"),
)


def discover_public_sources(
    runner: ProcessRunner,
    repository: str,
    *,
    since: str | None = None,
    limits: DiscoveryLimits | None = None,
    scanned_at: datetime | None = None,
) -> EvidenceBundle:
    limits = limits or DiscoveryLimits()
    _validate_limits(limits)
    if since is not None:
        _parse_timestamp(since, "since")
    scan_time = (scanned_at or datetime.now(UTC)).astimezone(UTC)
    scanned_at_text = scan_time.isoformat().replace("+00:00", "Z")

    metadata = _gh_json(runner, ("gh", "api", f"repos/{repository}"), limits.timeout)
    if not isinstance(metadata, dict):
        raise DiscoveryError("GitHub repository metadata must be a JSON object")
    if metadata.get("private") is not False or metadata.get("visibility") != "public":
        raise DiscoveryError(f"repository {repository!r} is not confirmed public")
    default_branch = _required_string(metadata, "default_branch", "repository metadata")

    argv = [
        "gh",
        "api",
        "--method",
        "GET",
        f"repos/{repository}/commits",
        "-f",
        f"sha={default_branch}",
        "-f",
        f"per_page={limits.max_commits}",
    ]
    if since is not None:
        argv.extend(("-f", f"since={since}"))
    summaries = _gh_json(runner, tuple(argv), limits.timeout)
    if not isinstance(summaries, list):
        raise DiscoveryError("GitHub commit listing must be a JSON array")

    omissions: list[dict[str, str]] = []
    commits: list[dict[str, Any]] = []

    def _bundle_size(candidate_commits: list[dict[str, Any]]) -> int:
        return len(
            _canonical_json(
                {
                    "repository": repository,
                    "default_branch": default_branch,
                    "scanned_at": scanned_at_text,
                    "since": since,
                    "commits": candidate_commits,
                    "omissions": omissions,
                }
            ).encode()
        )

    for summary in summaries[: limits.max_commits]:
        if not isinstance(summary, dict):
            raise DiscoveryError("GitHub commit listing contains a non-object entry")
        revision = _required_string(summary, "sha", "commit listing")
        detail = _gh_json(
            runner,
            (
                "gh",
                "api",
                "--method",
                "GET",
                f"repos/{repository}/commits/{revision}",
                "-f",
                f"per_page={limits.max_files_per_commit}",
                "-f",
                "page=1",
            ),
            limits.timeout,
        )
        checks = _gh_json(
            runner,
            ("gh", "api", f"repos/{repository}/commits/{revision}/check-runs"),
            limits.timeout,
        )
        # Newest-first: keep admitting commits until one would exceed the
        # bounded-evidence budget, then omit it and continue trying smaller
        # later commits. The byte cap is the safety invariant, so it governs
        # how many commits are eligible rather than a fixed count.
        omissions_mark = len(omissions)
        commit = _build_commit(repository, revision, detail, checks, runner, limits, omissions)
        if _bundle_size([*commits, commit]) > limits.max_bundle_bytes:
            del omissions[omissions_mark:]
            omissions.append(
                {"revision": revision, "path": "*", "reason": "bundle_budget_exceeded"}
            )
            continue
        commits.append(commit)

    payload = {
        "repository": repository,
        "default_branch": default_branch,
        "scanned_at": scanned_at_text,
        "since": since,
        "commits": commits,
        "omissions": omissions,
    }
    _sensitive_preflight(payload)
    encoded = _canonical_json(payload).encode()
    if len(encoded) > limits.max_bundle_bytes:
        raise DiscoveryError(
            f"bounded evidence is {len(encoded)} bytes; limit is {limits.max_bundle_bytes} bytes"
        )
    return EvidenceBundle(
        repository=repository,
        default_branch=default_branch,
        scanned_at=scanned_at_text,
        since=since,
        commits=tuple(commits),
        omissions=tuple(omissions),
        content_hash=hashlib.sha256(encoded).hexdigest(),
    )


def discover_public_revision(
    runner: ProcessRunner,
    repository: str,
    revision: str,
    *,
    limits: DiscoveryLimits | None = None,
    scanned_at: datetime | None = None,
) -> EvidenceBundle:
    """Reload one immutable public revision for drafting or claim validation."""
    limits = limits or DiscoveryLimits()
    _validate_limits(limits)
    scan_time = (scanned_at or datetime.now(UTC)).astimezone(UTC)
    scanned_at_text = scan_time.isoformat().replace("+00:00", "Z")

    metadata = _gh_json(runner, ("gh", "api", f"repos/{repository}"), limits.timeout)
    if not isinstance(metadata, dict):
        raise DiscoveryError("GitHub repository metadata must be a JSON object")
    if metadata.get("private") is not False or metadata.get("visibility") != "public":
        raise DiscoveryError(f"repository {repository!r} is not confirmed public")
    default_branch = _required_string(metadata, "default_branch", "repository metadata")

    omissions: list[dict[str, str]] = []
    detail = _gh_json(
        runner,
        (
            "gh",
            "api",
            "--method",
            "GET",
            f"repos/{repository}/commits/{revision}",
            "-f",
            f"per_page={limits.max_files_per_commit}",
            "-f",
            "page=1",
        ),
        limits.timeout,
    )
    checks = _gh_json(
        runner,
        ("gh", "api", f"repos/{repository}/commits/{revision}/check-runs"),
        limits.timeout,
    )
    commit = _build_commit(repository, revision, detail, checks, runner, limits, omissions)

    def _payload(current: dict[str, Any]) -> dict[str, Any]:
        return {
            "repository": repository,
            "default_branch": default_branch,
            "scanned_at": scanned_at_text,
            "since": None,
            "commits": [current],
            "omissions": omissions,
        }

    # A single revision is the whole bundle here, so there is no later commit to
    # fall back to: shedding the largest attachments keeps the revision usable
    # instead of failing drafting outright on a wide commit.
    commit = _shed_to_budget(commit, revision, _payload, limits, omissions)
    payload = _payload(commit)
    _sensitive_preflight(payload)
    encoded = _canonical_json(payload).encode()
    if len(encoded) > limits.max_bundle_bytes:
        raise DiscoveryError(
            f"bounded evidence is {len(encoded)} bytes; limit is {limits.max_bundle_bytes} bytes"
        )
    return EvidenceBundle(
        repository=repository,
        default_branch=default_branch,
        scanned_at=scanned_at_text,
        since=None,
        commits=(commit,),
        omissions=tuple(omissions),
        content_hash=hashlib.sha256(encoded).hexdigest(),
    )


def _build_commit(
    repository: str,
    revision: str,
    detail: object,
    checks: object,
    runner: ProcessRunner,
    limits: DiscoveryLimits,
    omissions: list[dict[str, str]],
) -> dict[str, Any]:
    if not isinstance(detail, dict):
        raise DiscoveryError(f"commit {revision} detail must be a JSON object")
    commit = detail.get("commit")
    files = detail.get("files")
    if not isinstance(commit, dict) or not isinstance(files, list):
        raise DiscoveryError(f"commit {revision} detail is missing commit or files")
    if len(files) >= limits.max_files_per_commit:
        omissions.append(
            {
                "revision": revision,
                "path": "*",
                "reason": f"file_list_limited_to_{limits.max_files_per_commit}",
            }
        )
    message = _required_string(commit, "message", f"commit {revision}")
    html_url = _required_string(detail, "html_url", f"commit {revision}")
    if html_url != f"https://github.com/{repository}/commit/{revision}":
        raise DiscoveryError(f"commit {revision} has an unexpected public URL")

    changed_files: list[str] = []
    patches: list[dict[str, str]] = []
    documents: list[dict[str, str]] = []
    for file_ in files:
        if not isinstance(file_, dict):
            raise DiscoveryError(f"commit {revision} contains invalid file metadata")
        path = _required_string(file_, "filename", f"commit {revision} file")
        changed_files.append(path)
        patch = file_.get("patch")
        if _is_generated(path):
            omissions.append({"revision": revision, "path": path, "reason": "generated"})
            continue
        if not isinstance(patch, str):
            omissions.append(
                {"revision": revision, "path": path, "reason": "binary_or_unavailable"}
            )
            continue
        patch_bytes = patch.encode()
        if len(patch_bytes) > limits.max_patch_bytes:
            patch = patch_bytes[: limits.max_patch_bytes].decode(errors="ignore")
            omissions.append({"revision": revision, "path": path, "reason": "patch_truncated"})
        patches.append({"path": path, "patch": patch})
        if _is_document(path):
            document = _fetch_document(runner, repository, revision, path, limits)
            if document is None:
                omissions.append({"revision": revision, "path": path, "reason": "document_deleted"})
            else:
                # Truncate rather than discard, matching patch handling above. A
                # report one byte over the cap still carries its methodology and
                # headline results, and dropping it whole leaves drafting with
                # nothing concrete to ground a claim in.
                document_bytes = document.encode()
                if len(document_bytes) > limits.max_document_bytes:
                    document = document_bytes[: limits.max_document_bytes].decode(errors="ignore")
                    omissions.append(
                        {"revision": revision, "path": path, "reason": "document_truncated"}
                    )
                documents.append({"path": path, "content": document})

    return {
        "revision": revision,
        "message": message,
        "public_url": html_url,
        "changed_files": changed_files,
        "patches": patches,
        "checks": _normalize_checks(checks, revision),
        "documents": documents,
    }


def _shed_to_budget(
    commit: dict[str, Any],
    revision: str,
    payload: Callable[[dict[str, Any]], dict[str, Any]],
    limits: DiscoveryLimits,
    omissions: list[dict[str, str]],
) -> dict[str, Any]:
    """Drop the largest patches, then documents, until the payload fits the cap.

    Patches go first: a post quotes the prose a commit ships, while a patch
    mainly has to show that a change happened. Shedding purely by size would
    discard a long design document ahead of several small diffs and leave
    drafting with nothing concrete to say. Within a kind, largest-first keeps the
    most distinct pieces of evidence per byte, and ties break on path so the
    surviving commit — and therefore its evidence hash — is reproducible across
    scans.
    """
    commit = {**commit, "patches": list(commit["patches"]), "documents": list(commit["documents"])}
    while len(_canonical_json(payload(commit)).encode()) > limits.max_bundle_bytes:
        for kind in ("patches", "documents"):
            candidates = [
                (len(_canonical_json(entry).encode()), entry["path"], index)
                for index, entry in enumerate(commit[kind])
            ]
            if candidates:
                break
        if not candidates:
            return commit
        _, path, index = max(candidates, key=lambda item: (item[0], item[1]))
        del commit[kind][index]
        omissions.append({"revision": revision, "path": path, "reason": "bundle_budget_exceeded"})
    return commit


def _fetch_document(
    runner: ProcessRunner,
    repository: str,
    revision: str,
    path: str,
    limits: DiscoveryLimits,
) -> str | None:
    response = _gh_json(
        runner,
        (
            "gh",
            "api",
            "--method",
            "GET",
            f"repos/{repository}/contents/{path}",
            "-f",
            f"ref={revision}",
        ),
        limits.timeout,
        allow_not_found=True,
    )
    if response is None:
        return None
    if not isinstance(response, dict) or response.get("encoding") != "base64":
        raise DiscoveryError(f"changed document {path!r} is not base64 file content")
    content = response.get("content")
    if not isinstance(content, str):
        raise DiscoveryError(f"changed document {path!r} has no content")
    try:
        normalized_content = "".join(content.split())
        decoded = base64.b64decode(normalized_content, validate=True)
    except ValueError as error:
        raise DiscoveryError(f"changed document {path!r} has invalid base64 content") from error
    try:
        return decoded.decode()
    except UnicodeDecodeError as error:
        raise DiscoveryError(f"changed document {path!r} is not UTF-8 text") from error


def _normalize_checks(checks: object, revision: str) -> list[dict[str, str]]:
    if not isinstance(checks, dict) or not isinstance(checks.get("check_runs"), list):
        raise DiscoveryError(f"check results for {revision} are invalid")
    normalized: list[dict[str, str]] = []
    for check in checks["check_runs"]:
        if not isinstance(check, dict):
            raise DiscoveryError(f"check results for {revision} contain a non-object entry")
        normalized.append(
            {
                "name": _required_string(check, "name", f"check result for {revision}"),
                "status": _required_string(check, "status", f"check result for {revision}"),
                "conclusion": str(check.get("conclusion") or ""),
                "url": str(check.get("html_url") or ""),
            }
        )
    return normalized


def _gh_json(
    runner: ProcessRunner,
    argv: tuple[str, ...],
    timeout: float,
    *,
    allow_not_found: bool = False,
) -> object:
    try:
        result = runner.run(argv, timeout)
    except (OSError, TimeoutError, subprocess.TimeoutExpired) as error:
        raise DiscoveryError(f"gh invocation failed: {error}") from error
    if result.returncode != 0:
        if allow_not_found and result.returncode == 1 and "HTTP 404" in result.stderr:
            return None
        detail = result.stderr.strip() or f"exit status {result.returncode}"
        raise DiscoveryError(f"gh invocation failed: {detail}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise DiscoveryError("gh returned invalid JSON") from error


def _sensitive_preflight(payload: object) -> None:
    text = _canonical_json(payload)
    findings = [name for name, pattern in _SECRET_PATTERNS if pattern.search(text)]
    if findings:
        raise SensitiveDataError(
            "local sensitive-data preflight rejected evidence: " + ", ".join(findings)
        )


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _required_string(value: dict[str, Any], key: str, context: str) -> str:
    field = value.get(key)
    if not isinstance(field, str) or not field:
        raise DiscoveryError(f"{context} is missing {key}")
    return field


def _is_generated(path: str) -> bool:
    return any(pattern.search(path) for pattern in _GENERATED_PATH_PATTERNS)


def _is_document(path: str) -> bool:
    lowered = path.lower()
    return lowered.endswith((".md", ".mdx", ".rst")) or lowered.startswith("docs/")


def _parse_timestamp(value: str, name: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise DiscoveryError(f"{name} must be an ISO-8601 timestamp") from error
    if parsed.tzinfo is None:
        raise DiscoveryError(f"{name} must include a timezone")
    return parsed


def _validate_limits(limits: DiscoveryLimits) -> None:
    if (
        min(
            limits.max_commits,
            limits.max_files_per_commit,
            limits.max_bundle_bytes,
            limits.max_patch_bytes,
            limits.max_document_bytes,
        )
        <= 0
        or limits.timeout <= 0
    ):
        raise ValueError("discovery limits must be positive")
    if limits.max_files_per_commit > 100:
        raise ValueError("max_files_per_commit must not exceed GitHub's 100-file page limit")
