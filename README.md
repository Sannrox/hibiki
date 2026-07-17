# Hibiki

Hibiki (`響き`, "resonance") turns real project work into grounded posts on X
and learns, from observed outcomes, which stories resonate with the intended
audience.

It is a headless, approval-gated coordinator: every factual claim traces back
to an inspectable source commit, every publication requires explicit
hash-bound human approval, and every outcome is measured and fed back into
governed learning. Hibiki is not an engagement bot. It will not auto-reply,
follow or unfollow accounts, scrape competitors, manufacture claims, or
publish without approval.

## How it works

```text
source artifact -> candidate story -> approved draft -> published post
       ^                                          |
       |                                          v
 governed learning <- evaluated outcome <- observed metrics
```

Hibiki coordinates a small ecosystem of systems, each with a single
responsibility:

| System   | Role |
| -------- | ---- |
| Tenkai   | The project whose public commits are the only source material |
| `gh`     | Sole access path to public GitHub data |
| Chisei   | Governs model work: selection, drafting, claim validation, reply classification, learning |
| Sekai    | Durable causal record store (namespace `hibiki`) |
| BirdClaw | Sole X transport: authentication, publication, post history |
| Onmyoji  | External automation and operator-facing workflow; invokes this CLI |

Hibiki itself has no UI, daemon, scheduler, or local database. Every command
writes one JSON object to stdout and reserves stderr for diagnostics, so an
automation layer can invoke it safely. The full boundary is recorded in
[`docs/decisions/`](docs/decisions/README.md).

## Status

All eight implementation phases in [`PLAN.md`](PLAN.md) are complete: the CLI
covers discovery through governed learning. The Onmyoji integration that
schedules and presents proposals is external and tracked separately.

## Requirements

- Python >= 3.12 and [`uv`](https://docs.astral.sh/uv/)
- `gh`, authenticated for public GitHub reads
- A running Sekai/Chisei environment reachable over gRPC
- [BirdClaw](https://github.com/steipete/birdclaw), installed and
  authenticated for the configured X account (only needed for live
  publication and collection; `scripts/install_birdclaw.sh` installs the CLI)

## Configuration

Copy the non-secret identifiers from [`.env.example`](.env.example) into the
invoking environment:

| Variable | Meaning |
| -------- | ------- |
| `HIBIKI_NAMESPACE` | Sekai namespace (default `hibiki`) |
| `HIBIKI_TENKAI_REPOSITORY` | Source repository as `OWNER/REPOSITORY` |
| `HIBIKI_BIRDCLAW_ACCOUNT` | BirdClaw account name for publication |
| `HIBIKI_CHISEI_TARGET` | gRPC target, `HOST:PORT` or `unix:///abs/path` |
| `HIBIKI_ALLOW_LIVE_WRITES` | Live X writes guard, defaults to `false` |

Authentication belongs to `gh`, BirdClaw, and the Sekai/Chisei environment;
Hibiki does not accept credential settings. CI always forces live writes off,
even if the guard is set to true.

Check configuration and reachable dependencies without performing writes:

```sh
uv run hibiki config
uv run hibiki health          # accepts --timeout SECONDS
```

## Workflow

The commands below follow one post through its full lifecycle. Identifiers
are stable Sekai external ids of the form
`hibiki.<type>:hibiki:OWNER/REPOSITORY@REVISION`.

### 1. Register schemas (once, idempotent)

Register the five accepted Hibiki causal record types, the scoped BirdClaw
evidence producer, and the two versioned evidence schemas in Sekai. The
command fails visibly if an existing definition has drifted:

```sh
uv run hibiki schema
```

### 2. Recommend a source

Discover new public default-branch commits since the last successful scan and
ask Chisei to return one eligible source or an explicit no-candidate result.
A local sensitive-data preflight runs before any model execution, and the
selection decision and Chisei operation receipt are recorded in Sekai:

```sh
uv run hibiki recommend
```

### 3. Draft

Generate one standalone draft from a selected source. Hibiki reloads the
exact public revision, verifies its evidence hash, and returns the draft,
reasoning, claims, and source references while persisting the proposal:

```sh
uv run hibiki draft 'hibiki.source:hibiki:OWNER/REPOSITORY@REVISION'
```

### 4. Validate edits

Submit edited text as JSON on stdin for an independent factual-claim
inventory and validation. A valid edit replaces the proposal text in
`drafted` state; unsupported text is not persisted and invalidates any prior
approval:

```sh
printf '%s\n' '{"final_text":"Exact edited post text"}' | \
  uv run hibiki validate 'hibiki.proposal:hibiki:OWNER/REPOSITORY@REVISION'
```

### 5. Approve

After presenting that exact validated text to the operator, bind explicit
approval to its returned SHA-256 hash. Any later edit invalidates the
approval:

```sh
printf '%s\n' '{"final_text_hash":"SHA256_FROM_VALIDATE"}' | \
  uv run hibiki approve 'hibiki.proposal:hibiki:OWNER/REPOSITORY@REVISION'
```

### 6. Publish

Publish only after inspecting the approved text and explicitly enabling live
writes for that invocation. BirdClaw must already be installed and
authenticated for the configured account:

```sh
HIBIKI_ALLOW_LIVE_WRITES=true \
  uv run hibiki publish 'hibiki.proposal:hibiki:OWNER/REPOSITORY@REVISION'
```

Hibiki records a durable intent before invoking `birdclaw compose post`, then
reads authored history back through BirdClaw and stores the X post
identifier. If the command outcome is uncertain, the next invocation
reconciles authored history before any retry; it never posts blindly. The
initial safe publication surface is limited to standard posts with X-weighted
text at or below 280.

### 7. Collect metrics

After the publication reaches its 24-hour or seven-day observation window,
collect raw post statistics and replies from BirdClaw and submit them through
Sekai's evidence funnel:

```sh
uv run hibiki collect 'hibiki.publication:hibiki:OWNER/REPOSITORY@REVISION' 24h
uv run hibiki collect 'hibiki.publication:hibiki:OWNER/REPOSITORY@REVISION' 7d
```

Collection is read-only with respect to X. Hibiki accepts only complete raw
BirdClaw sync payloads, projects every envelope onto the publication record,
and reuses prior snapshot and reply submissions on repeated collection. The
24-hour observation must run within six hours of its boundary; the seven-day
observation has a one-day tolerance, so late cumulative metrics cannot be
mislabelled as fixed-window results. BirdClaw's generated digest is never
invoked or admitted as source evidence.

### 8. Classify replies

Classify collected replies through Chisei's governed native execution. The
first 25 classifications always require operator confirmation; corrections
are retained as evaluation decisions. Automatic classification is enabled
only after those confirmations reach 90% accuracy, and still requires at
least 90% confidence:

```sh
uv run hibiki classify 'hibiki.publication:hibiki:OWNER/REPOSITORY@REVISION'
uv run hibiki confirm REPLY_SUBMISSION_ID potential_user
```

The accepted categories are `potential_user`,
`potential_tester_or_contributor`, `substantive_technical_discussion`,
`general_reaction`, and `irrelevant_or_low_signal`.

### 9. Report outcomes

After required confirmations are complete, return the 24-hour preliminary or
seven-day final outcome:

```sh
uv run hibiki outcome 'hibiki.publication:hibiki:OWNER/REPOSITORY@REVISION' 24h
uv run hibiki outcome 'hibiki.publication:hibiki:OWNER/REPOSITORY@REVISION' 7d
```

Outcome JSON keeps raw engagement metrics separate from the primary
`qualified_replies` count and includes the complete source, proposal,
publication, evidence-submission, and outcome lineage.

### 10. Governed learning

Surface hypotheses once at least three comparable posts have completed
seven-day outcomes, evaluate strategy recommendations behind the eight-post
and two-period gates, and record explicit operator decisions. Learning never
silently changes drafting behavior:

```sh
uv run hibiki hypothesize 'hibiki.publication:hibiki:OWNER/REPOSITORY@REVISION'
uv run hibiki strategy
uv run hibiki hypothesis-status HYPOTHESIS_ID accepted|rejected|retired
```

## Development

Install the locked development environment and run the deterministic checks:

```sh
uv sync
uv run pytest
uv run ruff check .
uv run python scripts/generate_contracts.py --check
```

All tests run against fakes; no test performs a live X write or requires a
running Sekai/Chisei instance.

Hibiki vendors the public `sekai.proto` and `chisei.proto` contracts and
commits their generated Python bindings. Refresh them from a sibling
Sekai/Chisei checkout, then review the resulting source and generated diff:

```sh
uv run python scripts/generate_contracts.py --update-from ../sekai-chisei/proto
```

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for conventions and
[`AGENTS.md`](AGENTS.md) for the rules automated contributors must follow.

## Project layout

```text
docs/decisions/   Accepted ADRs; the product and safety boundary
docs/learnings/   Operational learnings worth keeping
proto/            Vendored public Sekai/Chisei protobuf contracts
scripts/          Contract generation and BirdClaw install helpers
src/hibiki/       CLI and workflow modules
tests/            Deterministic tests over fakes
```

Further reading: [`VISION.md`](VISION.md) for the problem and principles,
[`PLAN.md`](PLAN.md) for the phased implementation record.

## License

[MIT](LICENSE)
