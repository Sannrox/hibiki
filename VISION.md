# Vision

## Problem

Interesting engineering work often remains buried in commits, plans, and
private notes. Generic writing assistants can generate polished text, but they
do not know whether a claim is grounded in completed work or whether a content
strategy produced meaningful reach.

## Product promise

Hibiki helps one operator select a true story from their work, shape it into a
post worth reading, and learn from the post's measured outcome without turning
their account into automated content.

## Intended loop

```text
source artifact -> candidate story -> approved draft -> published post
       ^                                          |
       |                                          v
 governed learning <- evaluated outcome <- observed metrics
```

## Principles

- Ground every factual claim in an inspectable source.
- Keep publication under explicit human control.
- Optimize for meaningful reach and conversation, not raw interaction counts.
- Treat content advice as a hypothesis until repeated outcomes support it.
- Keep private source material local and disclose what leaves the machine.
- Prefer a small tool the operator uses weekly over a broad social platform.

## Non-goals

- Social-network automation or account management
- Autonomous replies or engagement farming
- Multi-user campaign management
- Paid-ad optimization
- Competitor surveillance
- Support for multiple social networks in the first version

## MVP

Onmyoji periodically invokes Hibiki during a bounded randomized window. Hibiki
discovers public Tenkai commits through `gh`, asks Chisei to select one eligible
story, and returns one grounded standalone draft. The operator may edit it;
Chisei validates the final claims, and explicit hash-bound approval permits
BirdClaw publication. BirdClaw post statistics and replies enter Sekai through
the evidence funnel for governed classification and later learning.

The primary outcome is relevant technical conversation that can lead to early
Tenkai users, testers, and collaborators. Raw impressions remain diagnostic.
