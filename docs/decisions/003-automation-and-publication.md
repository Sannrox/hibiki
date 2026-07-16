# ADR 003: Automation, approval, and publication

## Status

Accepted.

## Decision

Onmyoji checks proposal eligibility once per day. A proposal may appear at a
random time between 09:00 and 20:00 Europe/Berlin, no sooner than four days
after the previous proposal, and no more than once in a rolling seven-day
period. Publication timing is never randomized or automated.

The source evidence bundle is bounded to:

- commit message and public URL;
- changed-file list;
- textual patches, excluding generated and binary content;
- GitHub check results; and
- changed or explicitly referenced public documentation.

A recorded size ceiling must fail visibly or truncate with provenance. The full
repository is never sent to a model. Hosted models are allowed for public
Tenkai material after a local secret and sensitive-data preflight. Provider,
model, source hashes, and transmitted fields remain attributable.

Chisei produces one draft. The operator may edit it; the final text is then
revalidated against the evidence bundle. Approval is bound to the exact final
text hash, and any later edit invalidates approval.

Publication requires:

1. a durable Sekai publication intent;
2. a valid, unexpired approval for the final text hash;
3. an explicit environment guard permitting live writes; and
4. a BirdClaw post command followed by read-back of the X post identifier.

The system fails closed when `gh`, Sekai, Chisei, or BirdClaw is unavailable.
An uncertain BirdClaw result is reconciled against authored-post history before
another attempt. It is never retried blindly. Tests and CI categorically
disable live writes.
