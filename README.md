# Hibiki

[![CI](https://github.com/Sannrox/hibiki/actions/workflows/ci.yml/badge.svg)](https://github.com/Sannrox/hibiki/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Hibiki (`響き`, “resonance”) turns real project work into grounded posts on X,
then learns from measured outcomes which stories create relevant technical
conversation.

It is a headless, approval-gated coordinator. Every factual claim traces to a
public source commit, every publication requires approval of the exact text,
and learning remains visible to the operator. Hibiki does not auto-reply,
manage followers, scrape competitors, invent claims, or publish autonomously.

> [!IMPORTANT]
> Hibiki is experimental, pre-1.0 software built for one operator and the
> Tenkai ecosystem. It is not currently a standalone social-media tool: a
> usable deployment also needs Sekai, Chisei, BirdClaw, and an external
> operator workflow. See [Project status](#project-status) before installing.

## Why Hibiki?

Most writing assistants optimize the text while ignoring whether its claims
are true or whether the advice improved anything. Hibiki treats publication as
an evidence-backed workflow:

```text
public commit -> selected story -> validated draft -> approved post
      ^                                              |
      |                                              v
 governed learning <- evaluated outcome <- observed metrics
```

Its primary success signal is a qualified technical reply from a potential
user, tester, contributor, or peer—not impressions alone. The product contract
and non-goals live in [`VISION.md`](VISION.md).

## Safety model

- **Public, bounded evidence:** only public default-branch Tenkai commits are
  eligible; the full repository is never sent to a model.
- **Claim validation:** edited text is checked against the source evidence
  before it can be approved.
- **Exact-text approval:** approval is bound to the final SHA-256 text hash;
  editing the text invalidates it.
- **Fail-closed publication:** live writes require a durable intent, valid
  approval, and `HIBIKI_ALLOW_LIVE_WRITES=true`. CI overrides the guard to
  `false`.
- **No blind retries:** an uncertain BirdClaw response is reconciled against
  authored-post history before another attempt.
- **Governed learning:** recommendations need enough comparable outcomes and
  never silently alter the drafting strategy.

These are product invariants, not optional deployment advice. The accepted
[architecture decision records](docs/decisions/README.md) define them in full.

## Project status

The repository implements the CLI workflow from source recommendation through
governed learning, with deterministic tests over fake process and gRPC
boundaries. The external Onmyoji integration that schedules and presents
operator work is not part of this repository and is still pending.

This means Hibiki is suitable for development, review, and integration work,
but it is not a turnkey end-user application. There is no hosted service, UI,
daemon, scheduler, local database, or published package installation path.

## Install from source

Prerequisites:

- Python 3.12 or newer and [`uv`](https://docs.astral.sh/uv/)
- [`gh`](https://cli.github.com/), authenticated for public GitHub reads
- a running Sekai and Chisei deployment reachable over gRPC
- [BirdClaw](https://github.com/steipete/birdclaw), authenticated for the
  configured X account when publishing or collecting observations

```sh
git clone https://github.com/Sannrox/hibiki.git
cd hibiki
uv sync --locked
cp .env.example .env
```

Edit `.env`, load those non-secret values into the invoking environment, then
verify configuration and dependencies:

```sh
set -a
. ./.env
set +a
uv run hibiki config
uv run hibiki health
```

Hibiki does not read `.env` itself. Your shell, process manager, or automation
layer must provide the variables. Do not put credentials in `.env`; `gh`,
BirdClaw, and the Sekai/Chisei environment own authentication.

Continue with the [getting-started guide](docs/getting-started.md) to register
schemas and run a safe first recommendation.

## CLI at a glance

Every command emits one machine-readable JSON object on stdout and reserves
stderr for diagnostics.

| Stage | Commands | External effect |
| --- | --- | --- |
| Inspect | `config`, `health` | Read-only |
| Initialize | `schema` | Registers Sekai types and evidence contracts |
| Create | `recommend`, `draft`, `validate`, `approve` | Writes causal records; no X write |
| Publish | `publish` | Can write to X only when all safety gates pass |
| Observe | `collect`, `classify`, `confirm`, `outcome` | Reads X; writes evidence and decisions |
| Learn | `hypothesize`, `strategy`, `hypothesis-status` | Writes governed hypotheses and decisions |

See the [workflow guide](docs/workflow.md) for the end-to-end sequence and the
[CLI reference](docs/cli-reference.md) for arguments, stdin contracts, and
side effects.

## Architecture

Hibiki coordinates systems without copying their responsibilities:

| System | Responsibility |
| --- | --- |
| Tenkai | Project whose public commits are the v0 source material |
| `gh` | Sole access path to public GitHub data |
| Chisei | Model execution, claim validation, classification, and learning |
| Sekai | Durable causal records under the `hibiki` namespace |
| BirdClaw | X authentication, publication, synchronization, and post history |
| Onmyoji | Scheduling, presentation, operator interaction, and escalation |

Read the [architecture guide](docs/architecture.md) for data ownership,
trust boundaries, and failure behavior.

## Contributing

Run the same deterministic checks as CI:

```sh
uv sync --locked
uv run pytest
uv run ruff check .
uv run python scripts/generate_contracts.py --check
```

Start with [`CONTRIBUTING.md`](CONTRIBUTING.md). Product ownership, safety, or
learning changes require an ADR amendment before implementation. Report
security-sensitive issues through [`SECURITY.md`](SECURITY.md), not a public
issue containing exploit details.

## Documentation

The [documentation index](docs/README.md) routes users, operators,
contributors, and reviewers to the relevant material. In particular:

- [`VISION.md`](VISION.md) — problem, promise, principles, and non-goals
- [`docs/decisions/`](docs/decisions/README.md) — accepted product boundaries
- [`PLAN.md`](PLAN.md) — implementation record and remaining external work
- [`docs/learnings/`](docs/learnings/INDEX.md) — retained operational lessons

## License

Hibiki is available under the [MIT License](LICENSE).
