from __future__ import annotations

import json
import re
import subprocess
import time
import unicodedata
import warnings
from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import timedelta

from linkify_it import LinkifyIt

from hibiki.boundaries import ProcessResult, ProcessRunner
from hibiki.proposals import ProposalWorkflowError, proposal_lock, require_current_approval
from hibiki.records import CausalRepositories, ProposalRecord, PublicationRecord
from hibiki.sekai import SekaiGateway

BIRDCLAW_TIMEOUT_SECONDS = 30.0
AUTHORED_LOOKBACK = timedelta(minutes=5)
X_SNOWFLAKE_EPOCH_MS = 1_288_834_974_657
MAX_SAFE_X_TEXT_WEIGHT = 280
X_SHORT_URL_WEIGHT = 23
PROTOCOL_PATTERN = re.compile(r"https?://", re.IGNORECASE | re.ASCII)


class PublicationWorkflowError(RuntimeError):
    """Raised when publication cannot preserve approval or retry guarantees."""


@dataclass(frozen=True, slots=True)
class PublicationResult:
    proposal: ProposalRecord
    publication: PublicationRecord
    reconciled: bool


def publish_proposal(
    process_runner: ProcessRunner,
    sekai: SekaiGateway,
    proposal_external_id: str,
    account: str,
    namespace: str,
    *,
    allow_live_writes: bool,
    clock_ms: Callable[[], int] | None = None,
) -> PublicationResult:
    if not allow_live_writes:
        raise PublicationWorkflowError(
            "live publication is disabled; set HIBIKI_ALLOW_LIVE_WRITES=true explicitly"
        )
    if not account.strip():
        raise PublicationWorkflowError("BirdClaw account must be a non-empty string")

    with proposal_lock(proposal_external_id):
        repositories = CausalRepositories.create(sekai, namespace, clock_ms=clock_ms)
        proposal = repositories.proposals.get_external(proposal_external_id)
        if proposal is None:
            raise PublicationWorkflowError(f"proposal not found: {proposal_external_id}")
        publication = repositories.publications.get(proposal.stable_id)
        if publication is not None:
            _require_publication_owner(publication, proposal)
            if publication.status == "posted":
                _require_matching_completed_publication(publication, proposal)
                proposal = _mark_proposal_published(repositories, proposal)
                return PublicationResult(proposal, publication, True)
            if publication.status in {"intent", "uncertain"}:
                _require_matching_completed_publication(publication, proposal)
                return _reconcile_prior_attempt(
                    process_runner,
                    repositories,
                    proposal,
                    publication,
                )

        try:
            approval_id = require_current_approval(sekai, proposal, proposal.draft)
        except ProposalWorkflowError as error:
            raise PublicationWorkflowError(str(error)) from error
        if _safe_x_text_weight(proposal.draft) > MAX_SAFE_X_TEXT_WEIGHT:
            raise PublicationWorkflowError(
                "final text exceeds Hibiki's safe 280-character X publication limit"
            )

        now_ms = (clock_ms or (lambda: time.time_ns() // 1_000_000))()
        intent = PublicationRecord(
            namespace=namespace,
            stable_id=proposal.stable_id,
            proposal_external_id=proposal.external_id,
            final_text=proposal.draft,
            target_account=account,
            attempted_at=now_ms,
            status="intent",
            approval_id=approval_id,
        )
        intent = repositories.publications.put(intent)
        try:
            response = _run_json_object(
                process_runner,
                (
                    "birdclaw",
                    "compose",
                    "post",
                    "--account",
                    intent.target_account,
                    intent.final_text,
                    "--json",
                ),
                "compose post",
            )
        except (OSError, subprocess.TimeoutExpired, PublicationWorkflowError) as error:
            repositories.publications.put(replace(intent, status="uncertain"))
            raise PublicationWorkflowError(
                "BirdClaw publication outcome is uncertain; reconcile before retrying"
            ) from error
        if response.get("ok") is not True:
            repositories.publications.put(replace(intent, status="uncertain"))
            raise PublicationWorkflowError(
                "BirdClaw did not acknowledge publication; outcome is uncertain"
            )

        return _read_back_new_post(
            process_runner,
            repositories,
            proposal,
            intent,
        )


def _reconcile_prior_attempt(
    process_runner: ProcessRunner,
    repositories: CausalRepositories,
    proposal: ProposalRecord,
    publication: PublicationRecord,
) -> PublicationResult:
    post_id = _find_authored_post(process_runner, publication)
    if post_id is None:
        repositories.publications.put(replace(publication, status="failed"))
        raise PublicationWorkflowError(
            "prior publication attempt was reconciled with no authored post; retry is now safe"
        )
    posted = repositories.publications.put(
        replace(publication, status="posted", post_id=post_id)
    )
    _require_matching_completed_publication(posted, proposal)
    proposal = _mark_proposal_published(repositories, proposal)
    return PublicationResult(proposal, posted, True)


def _read_back_new_post(
    process_runner: ProcessRunner,
    repositories: CausalRepositories,
    proposal: ProposalRecord,
    publication: PublicationRecord,
) -> PublicationResult:
    try:
        post_id = _find_authored_post(process_runner, publication)
    except (OSError, subprocess.TimeoutExpired, PublicationWorkflowError) as error:
        repositories.publications.put(replace(publication, status="uncertain"))
        raise PublicationWorkflowError(
            "BirdClaw read-back failed; publication outcome is uncertain"
        ) from error
    if post_id is None:
        repositories.publications.put(replace(publication, status="uncertain"))
        raise PublicationWorkflowError(
            "BirdClaw did not return the authored post; publication outcome is uncertain"
        )
    posted = repositories.publications.put(
        replace(publication, status="posted", post_id=post_id)
    )
    proposal = _mark_proposal_published(repositories, proposal)
    return PublicationResult(proposal, posted, False)


def _find_authored_post(
    process_runner: ProcessRunner,
    publication: PublicationRecord,
) -> str | None:
    _require_reconciliation_metadata(publication)
    account = publication.target_account
    since_id, until_id = _authored_snowflake_window(publication.attempted_at)
    response = _run_json_object(
        process_runner,
        (
            "birdclaw",
            "sync",
            "authored",
            "--account",
            account,
            "--mode",
            "xurl",
            "--limit",
            "100",
            "--since-id",
            since_id,
            "--until-id",
            until_id,
            "--json",
        ),
        "sync authored",
    )
    if response.get("ok") is not True or response.get("partial") is not False:
        raise PublicationWorkflowError("BirdClaw authored sync did not exhaust the retry window")
    payload = response.get("payload")
    if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
        raise PublicationWorkflowError("BirdClaw authored sync returned no tweet payload")
    posts = payload["data"]
    matches: list[str] = []
    for post in posts:
        if not isinstance(post, dict):
            raise PublicationWorkflowError("BirdClaw authored sync returned an invalid tweet")
        if _canonical_post_text(post) != publication.final_text:
            continue
        post_id = post.get("id")
        if not isinstance(post_id, str) or not post_id.strip():
            raise PublicationWorkflowError("BirdClaw authored post has no X identifier")
        matches.append(post_id)
    if len(matches) > 1:
        raise PublicationWorkflowError(
            "BirdClaw returned multiple matching authored posts for one intent"
        )
    return matches[0] if matches else None


def _authored_snowflake_window(attempted_at: int) -> tuple[str, str]:
    lookback_ms = int(AUTHORED_LOOKBACK.total_seconds() * 1000)
    lower_ms = max(X_SNOWFLAKE_EPOCH_MS, attempted_at - lookback_ms)
    upper_ms = max(X_SNOWFLAKE_EPOCH_MS, attempted_at + lookback_ms)
    since_id = max(0, ((lower_ms - X_SNOWFLAKE_EPOCH_MS) << 22) - 1)
    until_id = ((upper_ms - X_SNOWFLAKE_EPOCH_MS + 1) << 22)
    return str(since_id), str(until_id)


def _canonical_post_text(post: dict[object, object]) -> str:
    note_tweet = post.get("note_tweet")
    content = note_tweet if isinstance(note_tweet, dict) else post
    text = content.get("text")
    if not isinstance(text, str):
        raise PublicationWorkflowError("BirdClaw authored post has no text")
    entities = content.get("entities")
    if not isinstance(entities, dict):
        return text
    urls = entities.get("urls")
    if not isinstance(urls, list):
        return text
    for item in urls:
        if not isinstance(item, dict):
            continue
        short = item.get("url")
        expanded = item.get("expanded_url") or item.get("expandedUrl")
        if isinstance(short, str) and isinstance(expanded, str):
            text = text.replace(short, expanded)
    return text


def _safe_x_text_weight(text: str) -> int:
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="pkg_resources is deprecated as an API.*",
            category=UserWarning,
        )
        from twitter_text import extract_urls_with_indices, parse_tweet
        from twitter_text.regexp.valid_general_url_path_chars import (
            valid_general_url_path_chars,
        )
        from twitter_text.regexp.valid_url_balanced_parens import (
            valid_url_balanced_parens,
        )
        from twitter_text.regexp.valid_url_path import valid_url_path
        from twitter_text.regexp.valid_url_query_chars import valid_url_query_chars

    weight = int(parse_tweet(text).weightedLength)
    linkable_characters = [
        character if _is_linkable_character(character) else " " for character in text
    ]
    linkifier = LinkifyIt()
    linkified_components = _linkified_url_component_mask(
        text,
        linkifier.match("".join(linkable_characters)) or [],
        valid_url_balanced_parens,
        valid_url_path,
    )
    recognized_ranges = [tuple(item["indices"]) for item in extract_urls_with_indices(text)]
    recognized_urls = _recognized_url_mask(text, recognized_ranges)
    for protocol in PROTOCOL_PATTERN.finditer(text):
        if _needs_x_specific_boundary(
            text,
            protocol.start(),
            recognized_urls,
            (
                linkified_components[protocol.start()] == 1
                and valid_general_url_path_chars.fullmatch(
                    text[protocol.start() - 1]
                )
            )
            or linkified_components[protocol.start()] == 3
            or (
                linkified_components[protocol.start()] == 2
                and valid_url_query_chars.fullmatch(text[protocol.start() - 1])
            ),
        ):
            linkable_characters[protocol.start() - 1] = " "
    linkable_text = "".join(linkable_characters)
    for match in linkifier.match(linkable_text) or []:
        if match.schema not in {"http:", "https:"}:
            continue
        candidate = match.raw
        literal_weight = int(parse_tweet(candidate).weightedLength)
        weight += max(0, X_SHORT_URL_WEIGHT - literal_weight)
    return weight


def _is_linkable_character(character: str) -> bool:
    if character.isascii():
        return True
    return unicodedata.category(character)[0] in {"L", "M", "N"}


def _needs_x_specific_boundary(
    text: str,
    start: int,
    recognized_urls: bytearray,
    inside_linkified_x_url: bool,
) -> bool:
    if start == 0 or recognized_urls[start]:
        return False
    preceding = text[start - 1]
    if inside_linkified_x_url:
        return False
    if preceding.isascii():
        return not preceding.isalnum() and preceding not in "@$#"
    return unicodedata.category(preceding)[0] in {"L", "M", "N"}


def _recognized_url_mask(
    text: str,
    recognized_ranges: list[tuple[int, int]],
) -> bytearray:
    recognized = bytearray(len(text))
    for lower, upper in recognized_ranges:
        recognized[lower:upper] = b"\1" * (upper - lower)
    return recognized


def _linkified_url_component_mask(
    text: str,
    matches: list[object],
    balanced_parens: re.Pattern[str],
    valid_path: re.Pattern[str],
) -> bytearray:
    components = bytearray(len(text))
    for match in matches:
        if match.schema in {"http:", "https:"}:
            query_offset = match.raw.find("?")
            path_end = (
                match.last_index
                if query_offset == -1
                else match.index + query_offset
            )
            components[match.index:path_end] = b"\1" * (path_end - match.index)
            raw_path_end = path_end - match.index
            authority_start = match.raw.find("://") + 3
            path_start = match.raw.find("/", authority_start, raw_path_end)
            if path_start != -1:
                path = match.raw[path_start + 1 : raw_path_end]
                for balanced in balanced_parens.finditer(path):
                    if not _matches_repeated_path_atoms(
                        valid_path,
                        path[: balanced.end()],
                    ):
                        continue
                    lower = match.index + path_start + 1 + balanced.start()
                    upper = match.index + path_start + 1 + balanced.end()
                    components[lower:upper] = b"\3" * (upper - lower)
            components[path_end : match.last_index] = b"\2" * (
                match.last_index - path_end
            )
    return components


def _matches_repeated_path_atoms(pattern: re.Pattern[str], path: str) -> bool:
    cursor = 0
    while cursor < len(path):
        match = pattern.match(path, cursor)
        if match is None or match.end() == cursor:
            return False
        cursor = match.end()
    return True


def _run_json_object(
    process_runner: ProcessRunner,
    argv: tuple[str, ...],
    command: str,
) -> dict[str, object]:
    payload = _run_json(process_runner, argv, command)
    if not isinstance(payload, dict):
        raise PublicationWorkflowError(f"BirdClaw {command} must return one JSON object")
    return payload


def _run_json(
    process_runner: ProcessRunner,
    argv: tuple[str, ...],
    command: str,
) -> object:
    try:
        result = process_runner.run(argv, BIRDCLAW_TIMEOUT_SECONDS)
    except OSError as error:
        raise PublicationWorkflowError(
            f"BirdClaw {command} could not start: {error}"
        ) from error
    except subprocess.TimeoutExpired as error:
        raise PublicationWorkflowError(f"BirdClaw {command} timed out") from error
    _require_success(result, command)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise PublicationWorkflowError(f"BirdClaw {command} returned invalid JSON") from error


def _require_success(result: ProcessResult, command: str) -> None:
    if result.returncode == 0:
        return
    detail = result.stderr.strip() or f"exit status {result.returncode}"
    raise PublicationWorkflowError(f"BirdClaw {command} failed: {detail}")


def _require_publication_owner(
    publication: PublicationRecord,
    proposal: ProposalRecord,
) -> None:
    if publication.proposal_external_id != proposal.external_id:
        raise PublicationWorkflowError("stored publication intent belongs to another proposal")


def _require_reconciliation_metadata(publication: PublicationRecord) -> None:
    if not publication.target_account or publication.attempted_at <= 0:
        raise PublicationWorkflowError(
            "legacy publication intent needs target-account and attempt-time migration"
        )


def _require_matching_completed_publication(
    publication: PublicationRecord,
    proposal: ProposalRecord,
) -> None:
    if (
        publication.final_text != proposal.draft
        or publication.approval_id != proposal.decision_ref
    ):
        raise PublicationWorkflowError(
            "completed publication does not match the proposal's approved text"
        )


def _mark_proposal_published(
    repositories: CausalRepositories,
    proposal: ProposalRecord,
) -> ProposalRecord:
    if proposal.status == "published":
        return proposal
    return repositories.proposals.put(proposal.with_status("published"))
