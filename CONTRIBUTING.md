# Contributing to Hibiki

Hibiki welcomes focused bug fixes, tests, documentation improvements, and
changes that preserve its accepted product boundary. It is a deliberately
narrow, pre-1.0 project, so an issue or design discussion is recommended before
large changes.

## Before you start

Read these sources in order:

1. [`VISION.md`](VISION.md) for the product promise and non-goals.
2. [`docs/decisions/`](docs/decisions/README.md) for accepted architecture and
   safety decisions.
3. [`docs/architecture.md`](docs/architecture.md) for system and data ownership.
4. [`PLAN.md`](PLAN.md) for implemented scope and remaining external work.

If a proposal changes product ownership, publication safety, evidence
admission, or learning semantics, first propose a new ADR or an explicit
amendment to the affected ADR. Do not hide a boundary change inside an
implementation pull request.

## Choose the right contribution path

- **Bug or documentation error:** open an issue with reproduction steps or a
  link to the inaccurate section, then send a focused pull request.
- **Small implementation improvement:** explain the user-visible outcome and
  keep the change to one vertical slice.
- **New behavior or dependency:** discuss it before implementation and identify
  which ADRs it affects.
- **Security issue:** follow [`SECURITY.md`](SECURITY.md); do not disclose
  sensitive details in a public issue.

## Development setup

Prerequisites are Python 3.12 or newer, `uv`, and Git. Runtime services are not
needed for the test suite.

```sh
git clone https://github.com/Sannrox/hibiki.git
cd hibiki
uv sync --locked
```

Run the CLI help without configuring external services:

```sh
uv run hibiki --help
```

Most runtime commands require the non-secret variables documented in
[`.env.example`](.env.example). Hibiki does not load that file automatically.

## Tests and quality checks

Before opening a pull request, run the full deterministic suite:

```sh
uv run pytest
uv run ruff check .
uv run python scripts/generate_contracts.py --check
```

Tests must use fake process and gRPC boundaries. They must not require network
access, a running Sekai/Chisei service, BirdClaw credentials, or an X account.
CI forces `HIBIKI_ALLOW_LIVE_WRITES=false` regardless of repository settings.

Prefer tests that prove externally visible invariants: idempotency, exact-text
approval, bounded evidence, complete lineage, and fail-closed behavior.

## Generated contracts

`src/hibiki/contracts/` is generated from the protobuf files in `proto/` and is
committed. Do not edit generated files manually. To refresh from a sibling
Sekai/Chisei checkout:

```sh
uv run python scripts/generate_contracts.py --update-from ../sekai-chisei/proto
```

Include and review both the protobuf changes and regenerated bindings in the
same pull request. The generation check must be clean afterward.

## Documentation standards

- Keep commands, arguments, JSON stdin shapes, and side effects in
  [`docs/cli-reference.md`](docs/cli-reference.md) synchronized with
  `src/hibiki/cli.py`.
- Keep the end-to-end sequence in [`docs/workflow.md`](docs/workflow.md)
  synchronized with lifecycle changes.
- Put durable product and safety decisions in ADRs, not only in the README.
- Record non-obvious operational discoveries in
  [`docs/learnings/`](docs/learnings/INDEX.md) and update its index.
- Make factual claims traceable to code, tests, an ADR, or another repository
  artifact. Mark planned behavior as planned.
- Use relative links for repository documentation and check new links locally.

## Pull request checklist

- [ ] The change has one clear outcome and no unrelated cleanup.
- [ ] Existing ADR boundaries are preserved, or an explicit amendment is
      included.
- [ ] New behavior has deterministic tests, including failure paths.
- [ ] No secrets, tokens, analytics exports, or imported private material are
      present.
- [ ] Documentation and examples match the implemented CLI.
- [ ] The full local check suite passes.
- [ ] No test or CI path can perform a live external-account write.

## Repository layout

```text
docs/decisions/   Accepted architecture decision records
docs/learnings/   Operational lessons worth retaining
proto/            Vendored public Sekai/Chisei protobuf contracts
scripts/          Contract-generation and BirdClaw install helpers
src/hibiki/       CLI and workflow modules
tests/            Deterministic tests over fake boundaries
```

By participating, contributors agree to follow the
[`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).
