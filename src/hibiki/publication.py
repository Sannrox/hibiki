from __future__ import annotations

import json
import subprocess
from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace

from hibiki.boundaries import ProcessResult, ProcessRunner
from hibiki.proposals import ProposalWorkflowError, proposal_lock, require_current_approval
from hibiki.records import CausalRepositories, ProposalRecord, PublicationRecord
from hibiki.sekai import SekaiGateway

BIRDCLAW_TIMEOUT_SECONDS = 30.0


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
        if proposal.status == "published":
            if publication is None or publication.status != "posted":
                raise PublicationWorkflowError(
                    "published proposal has no completed publication record"
                )
            _require_matching_intent(publication, proposal, proposal.decision_ref)
            return PublicationResult(proposal, publication, True)
        try:
            approval_id = require_current_approval(sekai, proposal, proposal.draft)
        except ProposalWorkflowError as error:
            raise PublicationWorkflowError(str(error)) from error

        if publication is not None:
            _require_matching_intent(publication, proposal, approval_id)
            if publication.status == "posted":
                proposal = _mark_proposal_published(repositories, proposal)
                return PublicationResult(proposal, publication, True)
            if publication.status in {"intent", "uncertain"}:
                return _reconcile_prior_attempt(
                    process_runner,
                    repositories,
                    proposal,
                    publication,
                    account,
                )

        intent = PublicationRecord(
            namespace=namespace,
            stable_id=proposal.stable_id,
            proposal_external_id=proposal.external_id,
            final_text=proposal.draft,
            status="intent",
            approval_id=approval_id,
        )
        intent = repositories.publications.put(intent)
        request = {
            "account": account,
            "client_reference": intent.external_id,
            "text": intent.final_text,
        }
        try:
            response = _run_json(
                process_runner,
                ("birdclaw", "post", "--json"),
                request,
            )
        except (OSError, subprocess.TimeoutExpired, PublicationWorkflowError) as error:
            repositories.publications.put(replace(intent, status="uncertain"))
            raise PublicationWorkflowError(
                "BirdClaw publication outcome is uncertain; reconcile before retrying"
            ) from error
        if response.get("accepted") is not True:
            repositories.publications.put(replace(intent, status="uncertain"))
            raise PublicationWorkflowError(
                "BirdClaw did not acknowledge publication; outcome is uncertain"
            )

        return _read_back_new_post(
            process_runner,
            repositories,
            proposal,
            intent,
            account,
        )


def _reconcile_prior_attempt(
    process_runner: ProcessRunner,
    repositories: CausalRepositories,
    proposal: ProposalRecord,
    publication: PublicationRecord,
    account: str,
) -> PublicationResult:
    post_id = _find_authored_post(process_runner, account, publication.external_id)
    if post_id is None:
        repositories.publications.put(replace(publication, status="failed"))
        raise PublicationWorkflowError(
            "prior publication attempt was reconciled with no authored post; retry is now safe"
        )
    posted = repositories.publications.put(
        replace(publication, status="posted", post_id=post_id)
    )
    proposal = _mark_proposal_published(repositories, proposal)
    return PublicationResult(proposal, posted, True)


def _read_back_new_post(
    process_runner: ProcessRunner,
    repositories: CausalRepositories,
    proposal: ProposalRecord,
    publication: PublicationRecord,
    account: str,
) -> PublicationResult:
    try:
        post_id = _find_authored_post(process_runner, account, publication.external_id)
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
    account: str,
    client_reference: str,
) -> str | None:
    response = _run_json(
        process_runner,
        ("birdclaw", "authored-posts", "--json"),
        {"account": account, "client_reference": client_reference},
    )
    posts = response.get("posts")
    if not isinstance(posts, list):
        raise PublicationWorkflowError("BirdClaw authored-posts response must contain posts")
    matches: list[str] = []
    for post in posts:
        if not isinstance(post, dict) or post.get("client_reference") != client_reference:
            continue
        post_id = post.get("post_id")
        if not isinstance(post_id, str) or not post_id.strip():
            raise PublicationWorkflowError("BirdClaw authored post has no post_id")
        matches.append(post_id)
    if len(matches) > 1:
        raise PublicationWorkflowError("BirdClaw returned duplicate authored posts for one intent")
    return matches[0] if matches else None


def _run_json(
    process_runner: ProcessRunner,
    argv: tuple[str, ...],
    request: Mapping[str, object],
) -> dict[str, object]:
    result = process_runner.run(
        argv,
        BIRDCLAW_TIMEOUT_SECONDS,
        input_text=json.dumps(request, separators=(",", ":"), sort_keys=True),
    )
    _require_success(result, argv[1])
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise PublicationWorkflowError(f"BirdClaw {argv[1]} returned invalid JSON") from error
    if not isinstance(payload, dict):
        raise PublicationWorkflowError(f"BirdClaw {argv[1]} must return one JSON object")
    return payload


def _require_success(result: ProcessResult, command: str) -> None:
    if result.returncode == 0:
        return
    detail = result.stderr.strip() or f"exit status {result.returncode}"
    raise PublicationWorkflowError(f"BirdClaw {command} failed: {detail}")


def _require_matching_intent(
    publication: PublicationRecord,
    proposal: ProposalRecord,
    approval_id: str,
) -> None:
    if (
        publication.proposal_external_id != proposal.external_id
        or publication.final_text != proposal.draft
        or publication.approval_id != approval_id
    ):
        raise PublicationWorkflowError(
            "stored publication intent does not match the approved proposal"
        )


def _mark_proposal_published(
    repositories: CausalRepositories,
    proposal: ProposalRecord,
) -> ProposalRecord:
    if proposal.status == "published":
        return proposal
    return repositories.proposals.put(proposal.with_status("published"))
