# Hibiki

Hibiki (`響き`, "resonance") is a personal tool for turning real
project work into useful posts on X and learning, from observed outcomes, which
stories resonate with the intended audience.

The initial product boundary is deliberately narrow:

- one operator and one X account;
- source material from public Tenkai commits discovered through `gh`;
- drafts require explicit human approval;
- approved posts are published through BirdClaw;
- BirdClaw is the sole X transport and data source in v0;
- Sekai stores the causal chain from source to outcome;
- Chisei governs claims, privacy, approval, evaluation, and learning.

Hibiki is not an engagement bot. It will not auto-reply, follow or unfollow
accounts, scrape competitors, manufacture claims, or publish without approval.

## Status

Product decisions are accepted. Hibiki is a headless Python CLI managed with
`uv`; Onmyoji owns automation and the human-facing workflow. See
[`docs/decisions/`](docs/decisions/README.md) and [`PLAN.md`](PLAN.md).

## Development

Install the locked development environment and run the deterministic checks:

```sh
uv sync
uv run pytest
uv run ruff check .
uv run python scripts/generate_contracts.py --check
```

Hibiki vendors the public `sekai.proto` and `chisei.proto` contracts and commits
their generated Python bindings. Refresh them from a sibling Sekai/Chisei
checkout, then review the resulting source and generated diff:

```sh
uv run python scripts/generate_contracts.py --update-from ../sekai-chisei/proto
```

## Configuration and health

Copy the non-secret identifiers from `.env.example` into the invoking
environment. Authentication continues to belong to `gh`, BirdClaw, and the
existing Sekai/Chisei environment; Hibiki does not accept credential settings.
Live writes default to disabled.

Every command writes one JSON object to stdout and reserves stderr for operator
diagnostics. Check the configured dependencies without performing writes:

```sh
uv run hibiki config
uv run hibiki health
```

Register the five accepted Hibiki causal record types in Sekai. The command is
idempotent and fails visibly if an existing definition has drifted:

```sh
uv run hibiki schema
```

Discover new public default-branch commits since the last successful scan and
ask Chisei to return one eligible source or an explicit no-candidate result.
The command performs local sensitive-data preflight before model execution and
records the selection decision and Chisei operation receipt in Sekai:

```sh
uv run hibiki recommend
```

Generate one standalone draft from a selected source. Hibiki reloads the exact
public revision, verifies its evidence hash, and returns the draft, reasoning,
claims, and source references while persisting the proposal in Sekai:

```sh
uv run hibiki draft 'hibiki.source:hibiki:OWNER/REPOSITORY@REVISION'
```

Submit edited text as JSON on stdin for an independent factual-claim inventory
and validation. A valid edit replaces the proposal text in `drafted` state;
unsupported text is not persisted and invalidates any prior approval:

```sh
printf '%s\n' '{"final_text":"Exact edited post text"}' | \
  uv run hibiki validate 'hibiki.proposal:hibiki:OWNER/REPOSITORY@REVISION'
```

After presenting that exact validated text to the operator, bind explicit
approval to its returned SHA-256 hash:

```sh
printf '%s\n' '{"final_text_hash":"SHA256_FROM_VALIDATE"}' | \
  uv run hibiki approve 'hibiki.proposal:hibiki:OWNER/REPOSITORY@REVISION'
```
