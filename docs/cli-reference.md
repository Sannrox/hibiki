# CLI reference

Hibiki uses a small, stable command dispatcher intended for automation.

```text
hibiki <command> [arguments]
```

Run `uv run hibiki --help` for the compact machine-readable usage response.

## Process contract

- Exactly one compact JSON object is written to stdout, followed by a newline.
- Human-readable diagnostics are written to stderr.
- Commands that accept a request body read exactly one JSON object from stdin.
- Unknown commands and invalid arguments return exit code `2`.
- Workflow, configuration, or dependency failures return exit code `1`.
- Successful commands return `0`, except a completed `validate` operation also
  returns `1` when the proposed text is factually invalid.

Consumers should branch on both the process exit code and the JSON `ok` field.
They should treat undocumented response fields as unstable before 1.0.

## Commands

| Command | Arguments | Stdin | Main side effect |
| --- | --- | --- | --- |
| `config` | none | none | None |
| `health` | optional `--timeout SECONDS` | none | Dependency probes |
| `schema` | none | none | Registers Sekai contracts |
| `recommend` | none | none | Reads GitHub; records selection |
| `draft` | `SOURCE_ID` | none | Records proposal |
| `validate` | `PROPOSAL_ID` | `{"final_text":"…"}` | May update proposal |
| `approve` | `PROPOSAL_ID` | `{"final_text_hash":"…"}` | Records exact-text approval |
| `publish` | `PROPOSAL_ID` | none | May publish to X |
| `collect` | `PUBLICATION_ID 24h\|7d` | none | Reads X; submits evidence |
| `classify` | `PUBLICATION_ID` | none | Records classifications |
| `confirm` | `REPLY_SUBMISSION_ID CATEGORY` | none | Records operator decision |
| `outcome` | `PUBLICATION_ID 24h\|7d` | none | Records/reports outcome |
| `hypothesize` | `PUBLICATION_ID` | none | May record hypotheses |
| `strategy` | none | none | Evaluates recommendation gates |
| `hypothesis-status` | `HYPOTHESIS_ID STATUS` | none | Updates hypothesis status |

### `config`

Validates all runtime variables and returns their non-secret normalized values.
It never contacts dependencies. All configured identifiers are included in the
response, so do not treat stdout as private merely because Hibiki stores no
credentials.

```sh
uv run hibiki config
```

### `health`

Checks the `gh` executable plus the Sekai and Chisei gRPC health services.
Default timeout is 3 seconds; accepted values are greater than zero and at most
60 seconds.

```sh
uv run hibiki health
uv run hibiki health --timeout 10
```

### `schema`

Idempotently registers the five record types, scoped evidence producer, and
versioned evidence schemas. Incompatible existing definitions fail visibly.

```sh
uv run hibiki schema
```

### `recommend`

Discovers public commits and asks Chisei to choose one eligible source or no
candidate. A response with `"candidate": null` and `"ok": true` is expected
when none qualifies.

```sh
uv run hibiki recommend
```

### `draft SOURCE_ID`

Reloads the selected source revision and records one generated proposal.

```sh
uv run hibiki draft 'hibiki.source:hibiki:OWNER/REPOSITORY@REVISION'
```

### `validate PROPOSAL_ID`

Requires stdin to contain exactly one non-empty string field named
`final_text`. Extra fields are rejected. Supported text is persisted;
unsupported text is not.

```sh
printf '%s\n' '{"final_text":"Exact edited post text"}' | \
  uv run hibiki validate 'hibiki.proposal:hibiki:OWNER/REPOSITORY@REVISION'
```

### `approve PROPOSAL_ID`

Requires stdin to contain exactly one non-empty string field named
`final_text_hash`. The value must match the current successfully validated
proposal text.

```sh
printf '%s\n' '{"final_text_hash":"SHA256_FROM_VALIDATE"}' | \
  uv run hibiki approve 'hibiki.proposal:hibiki:OWNER/REPOSITORY@REVISION'
```

### `publish PROPOSAL_ID`

Publishes the approved text through BirdClaw only when all publication gates
pass. The explicit environment guard must be enabled on the live invocation.

```sh
HIBIKI_ALLOW_LIVE_WRITES=true \
  uv run hibiki publish 'hibiki.proposal:hibiki:OWNER/REPOSITORY@REVISION'
```

Never wrap this command in an unconditional retry loop. Reinvoking it after an
uncertain result is safe only because the Hibiki publication workflow first
reconciles authored history.

### `collect PUBLICATION_ID WINDOW`

Collects one completed `24h` or `7d` window. The command reads X through
BirdClaw and writes admitted evidence and raw outcome data to Sekai.

```sh
uv run hibiki collect 'hibiki.publication:hibiki:OWNER/REPOSITORY@REVISION' 24h
uv run hibiki collect 'hibiki.publication:hibiki:OWNER/REPOSITORY@REVISION' 7d
```

### `classify PUBLICATION_ID`

Classifies submitted replies and reports whether each result was automatically
accepted or requires confirmation.

```sh
uv run hibiki classify 'hibiki.publication:hibiki:OWNER/REPOSITORY@REVISION'
```

### `confirm REPLY_SUBMISSION_ID CATEGORY`

Records an operator confirmation or correction. Accepted categories are:

- `potential_user`
- `potential_tester_or_contributor`
- `substantive_technical_discussion`
- `general_reaction`
- `irrelevant_or_low_signal`

```sh
uv run hibiki confirm 'REPLY_SUBMISSION_ID' substantive_technical_discussion
```

An invalid category reaches workflow validation and returns a structured
failure.

### `outcome PUBLICATION_ID WINDOW`

Builds a preliminary `24h` or final `7d` report after its exact complete
snapshot and required reply decisions exist.

```sh
uv run hibiki outcome 'hibiki.publication:hibiki:OWNER/REPOSITORY@REVISION' 7d
```

### `hypothesize PUBLICATION_ID`

Surfaces hypotheses when at least three comparable final outcomes exist.

```sh
uv run hibiki hypothesize 'hibiki.publication:hibiki:OWNER/REPOSITORY@REVISION'
```

### `strategy`

Evaluates accepted hypotheses against the eight-post, two-period strategy
gate. The response distinguishes actionable recommendations from gated ones.

```sh
uv run hibiki strategy
```

### `hypothesis-status HYPOTHESIS_ID STATUS`

Records an explicit operator decision. `STATUS` must be `accepted`, `rejected`,
or `retired`.

```sh
uv run hibiki hypothesis-status 'HYPOTHESIS_EXTERNAL_ID' accepted
```

## Environment variables

| Variable | Validation |
| --- | --- |
| `HIBIKI_NAMESPACE` | Lowercase namespace identifier; default `hibiki` |
| `HIBIKI_TENKAI_REPOSITORY` | Required `OWNER/REPOSITORY` |
| `HIBIKI_BIRDCLAW_ACCOUNT` | Required, non-empty, no whitespace |
| `HIBIKI_CHISEI_TARGET` | Required `HOST:PORT` or `unix:///absolute/path` |
| `HIBIKI_ALLOW_LIVE_WRITES` | `true/false`, `1/0`, `yes/no`, or `on/off`; default false |

When a conventional truthy `CI` variable is present, Hibiki forces live writes
off regardless of `HIBIKI_ALLOW_LIVE_WRITES`.
