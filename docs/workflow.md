# Workflow guide

This guide follows one post through Hibiki's complete lifecycle. Complete the
[getting-started guide](getting-started.md) first. Commands assume the required
environment variables are already exported.

Identifiers used between stages are stable Sekai external IDs shaped like
`hibiki.<type>:hibiki:OWNER/REPOSITORY@REVISION`. Use returned identifiers when
the response includes them. The current `publish` response is the exception:
it returns the post ID and statuses but not the publication external ID, so the
publication ID retains the proposal suffix and uses the
`hibiki.publication:` type prefix.

## Lifecycle

```text
schema
  |
  v
recommend -> draft -> validate -> approve -> publish
                                              |
                                              v
collect -> classify -> confirm -> outcome -> hypothesize -> strategy
```

`publish` is the only command in this sequence that can write to X. `collect`
reads X through BirdClaw; most other stages persist records or decisions in
Sekai.

## 1. Register schemas

Run once for a deployment and safely repeat after upgrades:

```sh
uv run hibiki schema
```

The command registers the five causal record types, scoped BirdClaw evidence
producer, and two evidence schemas. It fails if a pre-existing definition has
drifted incompatibly.

## 2. Recommend a source

```sh
uv run hibiki recommend
```

Hibiki discovers public default-branch commits since the last successful scan,
constructs bounded evidence, performs a local sensitive-data preflight, and
asks Chisei to select one eligible source. It records the decision even when
there is no candidate.

If `candidate` is `null`, stop this lifecycle. No candidate is a valid result;
do not choose an ineligible commit manually to force progress.

Save `candidate.source_external_id` from the JSON response.

## 3. Draft one post

```sh
uv run hibiki draft 'SOURCE_EXTERNAL_ID'
```

Hibiki reloads the exact public revision, checks the evidence hash, asks Chisei
for one standalone draft, and persists a proposal. The result includes the
draft, reasoning, factual claims, source references, and operation receipt.

Save `proposal_external_id`. Inspect the draft and evidence before editing.

## 4. Validate the final text

`validate` accepts exactly one JSON object on stdin:

```sh
printf '%s\n' '{"final_text":"Exact edited post text"}' | \
  uv run hibiki validate 'PROPOSAL_EXTERNAL_ID'
```

Chisei inventories and validates the final claims against the same source
evidence. Supported text is persisted in `drafted` state. Unsupported text is
not persisted, returns a nonzero exit code, and invalidates prior approval.

Save `final_text_hash` only from a successful validation response.

## 5. Approve the exact text

Approval is a separate operator action. Present the exact validated text and
its evidence before running:

```sh
printf '%s\n' '{"final_text_hash":"HASH_FROM_VALIDATE"}' | \
  uv run hibiki approve 'PROPOSAL_EXTERNAL_ID'
```

The hash must match the current proposal text. Any later edit requires another
successful validation and approval.

## 6. Publish with an explicit live-write guard

This command can create a real X post. Confirm the target BirdClaw account and
approved text before enabling the guard for this invocation:

```sh
HIBIKI_ALLOW_LIVE_WRITES=true \
  uv run hibiki publish 'PROPOSAL_EXTERNAL_ID'
```

Hibiki records durable intent before invoking BirdClaw, then reads authored
history back and persists the post ID. If the external outcome is uncertain,
do not manually retry or publish outside Hibiki. Reinvoke the same command so
its reconciliation path can determine whether the post already exists.

The initial publication surface is a standard post whose X-weighted text is at
most 280 characters. CI always disables live writes.

The current response does not echo the publication external ID. For subsequent
stages, replace the leading `hibiki.proposal:` in the proposal ID with
`hibiki.publication:` and preserve the complete suffix. The result is called
`PUBLICATION_EXTERNAL_ID` below. This follows the stable identifier contract,
but the missing response field is a pre-1.0 CLI usability limitation.

## 7. Collect fixed-window observations

After each window has elapsed, collect raw post statistics and replies:

```sh
uv run hibiki collect 'PUBLICATION_EXTERNAL_ID' 24h
uv run hibiki collect 'PUBLICATION_EXTERNAL_ID' 7d
```

The 24-hour command must run no more than six hours after its boundary. The
seven-day command has a one-day tolerance. These limits prevent late cumulative
metrics from being labelled as fixed-window observations.

Collection is read-only with respect to X. It accepts only complete raw
BirdClaw sync payloads, projects each envelope onto the publication, and
deduplicates repeated snapshot and reply submissions. BirdClaw's generated
digest is never invoked or admitted as evidence.

## 8. Classify and confirm replies

```sh
uv run hibiki classify 'PUBLICATION_EXTERNAL_ID'
```

Classifications use one of these categories:

- `potential_user`
- `potential_tester_or_contributor`
- `substantive_technical_discussion`
- `general_reaction`
- `irrelevant_or_low_signal`

The first 25 classifications require operator confirmation. Confirm or correct
each returned `submission_id`:

```sh
uv run hibiki confirm 'REPLY_SUBMISSION_ID' potential_user
```

Corrections become evaluation decisions. High-confidence automatic acceptance
is possible only after the calibration gate is met; ambiguous results continue
to require operator review.

## 9. Build outcome reports

After required confirmations are complete:

```sh
uv run hibiki outcome 'PUBLICATION_EXTERNAL_ID' 24h
uv run hibiki outcome 'PUBLICATION_EXTERNAL_ID' 7d
```

The 24-hour result is preliminary and the seven-day result is final. Outcome
JSON separates raw engagement metrics from `qualified_replies` and includes
source, proposal, publication, evidence, classification, and outcome lineage.

## 10. Govern learning

Once enough comparable seven-day outcomes exist, surface hypotheses:

```sh
uv run hibiki hypothesize 'PUBLICATION_EXTERNAL_ID'
```

Three comparable posts are required before Chisei may surface a hypothesis.
Evaluate strategy only when the dataset may support it:

```sh
uv run hibiki strategy
```

Recommendations remain gated until at least eight comparable posts cover two
separate periods. Record the operator's explicit decision for a hypothesis:

```sh
uv run hibiki hypothesis-status 'HYPOTHESIS_EXTERNAL_ID' accepted
uv run hibiki hypothesis-status 'HYPOTHESIS_EXTERNAL_ID' rejected
uv run hibiki hypothesis-status 'HYPOTHESIS_EXTERNAL_ID' retired
```

These statuses govern learning records; they do not silently rewrite the
drafting strategy or voice.

## Automation notes

Onmyoji is intended to enforce the randomized proposal window and rolling
frequency limits from [ADR 003](decisions/003-automation-and-publication.md),
present evidence, collect edits and approval, and surface classification work.
That integration is external and pending. Do not add an internal scheduler to
Hibiki as a workaround without first amending the accepted architecture.
