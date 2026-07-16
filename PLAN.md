# Implementation plan

The plan is ordered by contract risk. Each phase must remain independently
testable and must not add a live X write before Phase 5.

## Phase 1: Python CLI and contract generation

- Initialize the `uv` package and a small command dispatcher.
- Generate Python bindings from Sekai and Chisei public protobuf contracts.
- Add JSON stdout and diagnostic stderr conventions.
- Add configuration for namespace, Tenkai repository, BirdClaw account,
  Chisei target, and the live-write guard without storing credentials.
- Add fake process and gRPC boundaries for deterministic tests.

Definition of done: the CLI can report dependency/configuration health against
fakes, and generated bindings are reproducible and compatibility-checked.

## Phase 2: Namespace and causal records

- Register the five `hibiki` schema types idempotently.
- Implement source, proposal, publication-intent, outcome, and hypothesis
  repositories over Sekai gRPC.
- Make retries idempotent through stable external identifiers and content
  hashes.

Definition of done: a fake proposal lifecycle round-trips through Sekai without
GitHub, model, or BirdClaw access.

## Phase 3: Public source discovery and recommendation

- Invoke `gh` for Tenkai default-branch commits since the last successful scan.
- Build the bounded evidence bundle and run local sensitive-data preflight.
- Fetch check results and relevant changed documentation.
- Ask Chisei through `PlanExecution`/`ExecutePlan` to apply eligibility and
  ranking rules, returning either one candidate or no candidate.
- Record the selection decision and operation receipt.

Definition of done: fixtures prove public-only discovery, bounded context,
explicit no-candidate behavior, and repeat-topic rejection.

## Phase 4: Draft, edit, validation, and approval

- Generate one standalone draft from the selected evidence.
- Return draft, reasoning, claims, and source references as JSON for Onmyoji.
- Accept an edited final text and revalidate every factual claim through
  Chisei.
- Record approval against the exact final-text hash and invalidate it on edits.

Definition of done: unsupported claims and stale approvals cannot reach a
publication intent.

## Phase 5: Approval-gated BirdClaw publication

- Record the durable publication intent before an external write.
- Require both hash-bound approval and the explicit live-write environment
  guard.
- Invoke BirdClaw through a narrow JSON subprocess contract.
- Read back and record the X post identifier.
- Reconcile uncertain outcomes before permitting any retry.

Definition of done: all tests remain write-disabled; one explicitly approved
live smoke test can publish exactly once and records complete lineage.

## Phase 6: BirdClaw evidence funnel

- Register the scoped producer and two evidence schemas.
- Collect and submit 24-hour and seven-day `social.post_snapshot` envelopes.
- Collect replies and submit idempotent `social.reply` envelopes.
- Preserve BirdClaw as source of truth and reject generated digest input.

Definition of done: duplicate collection does not duplicate evidence, and each
submission projects onto the correct publication.

## Phase 7: Classification and outcome reporting

- Classify replies through governed native Chisei execution.
- Require confirmation for the first 25 replies and persist corrections as
  evaluation evidence.
- Return the 24-hour preliminary and seven-day final outcome to Onmyoji.
- Enable high-confidence automatic classification only after calibration.

Definition of done: the final report distinguishes qualified replies from raw
engagement and exposes the complete source-to-outcome lineage.

## Phase 8: Governed learning

- Surface hypotheses after three comparable posts.
- Enforce eight-post and two-period gates for strategy recommendations.
- Record acceptance, rejection, and retirement without silently changing
  drafting behavior.

Definition of done: deterministic fixtures prove that insufficient or
single-period evidence cannot alter the recommended strategy.

## External Onmyoji work

Onmyoji needs a reusable automation capable of invoking the JSON CLI, honoring
the 09:00–20:00 randomized proposal window and rolling-frequency limits,
presenting the proposal and evidence, collecting edits and approval, and
showing outcome/classification questions. Hibiki must not implement a second
scheduler or chat interface while that integration is pending.
