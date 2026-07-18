# Getting started

This guide gets a development checkout to a safe, read-only recommendation.
It does not publish to X.

## Decide whether Hibiki fits

Hibiki currently assumes all of the following:

- one operator;
- public commits from one configured Tenkai GitHub repository;
- Sekai and Chisei available through their native gRPC services;
- BirdClaw as the only X transport; and
- an external workflow, eventually Onmyoji, for scheduling and operator
  interaction.

It is not a generic GitHub-to-social CLI, hosted service, or standalone app.
Changing those assumptions is product work and requires an ADR amendment.

## 1. Install the development checkout

Install Python 3.12 or newer, [`uv`](https://docs.astral.sh/uv/), Git, and
[`gh`](https://cli.github.com/). Then:

```sh
git clone https://github.com/Sannrox/hibiki.git
cd hibiki
uv sync --locked
uv run hibiki --help
```

The package is not currently published to PyPI. `uv sync --locked` installs the
checkout and its locked development dependencies into a local environment.

## 2. Prepare external services

You need a deployment exposing both the `sekai.SekaiService` and
`chisei.ChiseiService` gRPC health services and native APIs. Hibiki vendors the
compatible public protobuf contracts in `proto/`.

Authenticate `gh` and verify that it can read the configured public repository:

```sh
gh auth status
gh repo view OWNER/REPOSITORY
```

BirdClaw is not needed for recommendation or drafting. Install and authenticate
it before publication or evidence collection. The helper supports Homebrew on
macOS and falls back to npm:

```sh
./scripts/install_birdclaw.sh
```

Hibiki stores none of these credentials.

## 3. Configure non-secret identifiers

Copy the example and replace every placeholder:

```sh
cp .env.example .env
```

| Variable | Required | Meaning |
| --- | --- | --- |
| `HIBIKI_NAMESPACE` | No | Sekai namespace; defaults to `hibiki` |
| `HIBIKI_TENKAI_REPOSITORY` | Yes | Public source as `OWNER/REPOSITORY` |
| `HIBIKI_BIRDCLAW_ACCOUNT` | Yes | Account name known to BirdClaw |
| `HIBIKI_CHISEI_TARGET` | Yes | `HOST:PORT` or `unix:///absolute/path` |
| `HIBIKI_ALLOW_LIVE_WRITES` | No | Explicit publication guard; defaults to `false` |

`.env` is ignored by Git, but it should contain identifiers only. Hibiki does
not load dotenv files, so export the values in the process that invokes it:

```sh
set -a
. ./.env
set +a
```

## 4. Verify the environment

`config` validates and prints only Hibiki's non-secret settings. `health`
checks `gh` and both gRPC health endpoints. Neither command writes externally.

```sh
uv run hibiki config
uv run hibiki health --timeout 5
```

Both commands emit one JSON object on stdout. A nonzero exit code and stderr
diagnostic indicate failure. The health timeout must be greater than zero and
at most 60 seconds.

## 5. Register contracts

This is the first persistent operation. It idempotently registers five Hibiki
causal record types, the scoped evidence producer, and two versioned evidence
schemas in Sekai:

```sh
uv run hibiki schema
```

An existing incompatible definition fails visibly instead of being silently
overwritten.

## 6. Request a recommendation

The first model-backed operation discovers public default-branch commits,
builds bounded evidence, performs a local sensitive-data preflight, and asks
Chisei to select at most one eligible story:

```sh
uv run hibiki recommend
```

A successful command can legitimately return `"candidate": null` when no
commit passes the product criteria. That is not an error and must not be
converted into a forced draft.

At this point the safe first run is complete. Continue with the
[workflow guide](workflow.md) for drafting, approval, publication, observation,
and learning.

## Troubleshooting

### Configuration fails before checks run

All three identifiers—repository, BirdClaw account, and gRPC target—are
required even for commands that do not immediately use BirdClaw. Check `.env`
placeholders and confirm that the variables were exported into the current
shell.

### `health` reports `gh` unavailable

Run `gh --version` and `gh auth status`. Hibiki invokes the executable from the
current `PATH`.

### A gRPC service is unavailable

Confirm the target scheme. TCP targets use `HOST:PORT`; Unix sockets use three
slashes before the absolute path, for example
`unix:///var/run/sekai-chisei.sock`.

### Live writes remain disabled

That is the default. Do not enable them during setup. Publication requires a
validated and approved proposal and an explicit guard on that invocation. CI
always disables the guard, even when the environment says otherwise.
