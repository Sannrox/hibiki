# Architecture

Hibiki is a headless Python CLI that coordinates existing systems while
retaining as little data and authority as possible. It has no independent UI,
daemon, scheduler, credential store, or local database.

The accepted decisions in [`docs/decisions/`](decisions/README.md) are the
normative architecture. This guide explains their combined effect.

## System context

```text
                    schedules and presents work
                 +-------------------------------+
                 |           Onmyoji             |
                 +---------------+---------------+
                                 |
                                 v
+---------+ public GitHub   +-----+------+ native gRPC +------------------+
| Tenkai  +------ gh ------>|   Hibiki   +------------>| Sekai / Chisei   |
+---------+                 | Python CLI |             | records / models |
                            +-----+------+             +------------------+
                                  |
                                  | constrained subprocess JSON
                                  v
                            +-----+------+
                            | BirdClaw  |<----> X
                            +------------+
```

Commands write one JSON object to stdout and diagnostics to stderr. This is the
automation contract: an invoker can distinguish structured results from human
diagnostics without scraping prose.

## Ownership boundaries

| Component | Owns | Explicitly does not own |
| --- | --- | --- |
| Hibiki | Workflow coordination and invariant enforcement | Scheduling, UI, credentials, model policy, X history |
| `gh` | Access to public GitHub data | Durable Hibiki records |
| Chisei | Selection, drafting, validation, classification, model routing, evaluation, learning | Publication transport |
| Sekai | Typed causal records and admitted evidence | Complete Git diffs or X history |
| BirdClaw | X authentication, writes, synchronization, complete local X history | Content decisions and approval |
| Onmyoji | Timing, presentation, operator interaction, escalation | Hibiki's product and safety rules |

Hibiki uses generated Python bindings for the native Sekai and Chisei gRPC
services. It does not use an OpenAI-compatible gateway. Git remains the source
for complete diffs; BirdClaw remains the source for complete X history.

## Data lifecycle

The minimal Sekai ontology is:

- `hibiki.source` — selected public revision and evidence identity;
- `hibiki.proposal` — draft, validation state, exact text hash, and approval;
- `hibiki.publication` — durable intent and reconciled X post identity;
- `hibiki.outcome` — fixed-window raw metrics and classified replies; and
- `hibiki.hypothesis` — surfaced learning and operator-governed status.

Stable external identifiers and content hashes make repeated operations
idempotent. Sekai stores references, hashes, decisions, and lineage rather than
copying complete source repositories or social history.

BirdClaw observations enter Sekai only through a producer restricted to the
`hibiki` namespace, configured BirdClaw instance, Hibiki publication targets,
bounded payloads, and two schemas:

- `social.post_snapshot` for 24-hour or seven-day raw statistics; and
- `social.reply` for reply text, public metrics, author reference, and
  collection time.

BirdClaw-generated digests and account snapshots are outside the v0 evidence
contract.

## Trust boundaries and failure behavior

### Source and model boundary

The only eligible source is a public commit on the configured repository's
default branch. Evidence contains bounded commit metadata, changed files,
textual patches, checks, and relevant public documentation. Generated and
binary content are excluded. The full repository is never sent to a model.

A local sensitive-data preflight runs before hosted model work. Provider,
model, source hashes, and transmitted fields remain attributable through the
operation record.

### Publication boundary

Publication requires all of these conditions:

1. the edited text passed claim validation;
2. approval matches the exact final-text SHA-256 hash;
3. a durable publication intent exists;
4. `HIBIKI_ALLOW_LIVE_WRITES=true` for that invocation; and
5. BirdClaw read-back identifies the authored post.

Any edit invalidates approval. Text over Hibiki's safe X-weighted 280-character
limit fails before the external write. If BirdClaw's result is uncertain,
Hibiki searches bounded authored history and refuses a blind retry.

### Observation and learning boundary

The 24-hour snapshot is preliminary; the seven-day snapshot is final for
learning. Collection rejects incomplete data, excess replies, oversized
payloads, premature windows, and observations too late to represent the fixed
window accurately.

The operator confirms the first 25 reply classifications. Automation is only
eligible after at least 90% calibration accuracy and still requires at least
90% confidence. Hypotheses require three comparable final outcomes; strategy
recommendations require eight comparable outcomes reproduced across two
periods. A recommendation never silently changes drafting behavior.

### Dependency failures

Hibiki fails closed when `gh`, Sekai, Chisei, or BirdClaw is unavailable. Tests
replace process and gRPC boundaries with fakes. CI categorically disables live
writes.

## Deployment shape

Hibiki is intended to be invoked as a short-lived process by Onmyoji. Until
that external integration exists, an operator can invoke CLI stages manually.
Adding a scheduler, UI, local database, or alternate publication transport to
this repository would change the accepted system boundary and requires an ADR
amendment first.
