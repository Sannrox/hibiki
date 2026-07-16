# ADR 002: Runtime and system boundaries

## Status

Accepted.

## Decision

Hibiki is a headless Python CLI managed with `uv`. It has no independent UI,
daemon, scheduler, or local database. Commands emit machine-readable JSON on
stdout and diagnostics on stderr so Onmyoji can invoke them safely.

System ownership is:

- `gh` owns access to public GitHub data and is the only Tenkai commit source.
- Onmyoji owns automation, presentation, operator interaction, and escalation.
- BirdClaw owns X authentication, publication, synchronization, and complete
  local X history.
- Sekai owns Hibiki's durable causal records under namespace `hibiki`.
- Chisei owns selection, drafting, claim validation, reply classification,
  policy, model routing, evaluation, and governed learning.
- Hibiki coordinates those systems without copying their responsibilities.

Hibiki uses native Sekai and Chisei gRPC services through generated Python
bindings. It does not use the OpenAI-compatible gateway. `PlanExecution` and
`ExecutePlan` govern model work; typed Sekai objects record state;
`SubmitEvidence` admits BirdClaw observations.

The minimal ontology is:

- `hibiki.source`
- `hibiki.proposal`
- `hibiki.publication`
- `hibiki.outcome`
- `hibiki.hypothesis`

Sekai stores references, hashes, decisions, drafts, approvals, publications,
outcomes, and hypotheses. Git remains the source for complete diffs and
BirdClaw remains the source for complete X history and media.

Hibiki stores no credentials. `gh`, BirdClaw, and the existing Chisei
environment or secret-reference mechanism retain their own authentication.
