# Contributing

Hibiki is a small, deliberately narrow tool. Contributions are welcome when
they respect the accepted product boundary.

## Ground rules

- Read [`VISION.md`](VISION.md) and the ADRs in
  [`docs/decisions/`](docs/decisions/README.md) before proposing changes.
  The ADRs are the current boundary; changes to product ownership, safety,
  or learning semantics require an explicit ADR amendment first.
- Never add a code path that publishes to X or mutates an external account
  without explicit hash-bound approval and the live-write guard.
- Keep secrets, tokens, analytics exports, and imported private material out
  of version control.
- Keep factual claims in generated content traceable to source artifacts.
- Prefer narrow vertical slices and deterministic tests over fakes; tests
  must never require network access or a live Sekai/Chisei instance.

## Development setup

```sh
uv sync
```

Before opening a pull request, run the full deterministic check suite:

```sh
uv run pytest
uv run ruff check .
uv run python scripts/generate_contracts.py --check
```

## Generated contracts

`src/hibiki/contracts/` is generated from the vendored protobuf files in
`proto/` and committed. Do not edit the generated files by hand. To refresh
from a sibling Sekai/Chisei checkout:

```sh
uv run python scripts/generate_contracts.py --update-from ../sekai-chisei/proto
```

Review both the proto diff and the regenerated bindings in the same change.

## Documentation

- Keep [`README.md`](README.md) in sync with the CLI: every command in
  `src/hibiki/cli.py` must be documented, and examples must match the real
  argument names.
- Record non-obvious operational discoveries in
  [`docs/learnings/`](docs/learnings/INDEX.md) and add a row to its index.

## Reporting issues

Open a GitHub issue. For anything security-sensitive (for example a path
that could leak private material or bypass the approval gate), avoid public
details in the initial report and say so in the issue title.
