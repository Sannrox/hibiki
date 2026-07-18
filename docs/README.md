# Hibiki documentation

This index separates product decisions from user instructions and
implementation history. If two documents conflict, an accepted architecture
decision record (ADR) takes precedence over descriptive guides.

## Start here

| You want to… | Read |
| --- | --- |
| Understand the problem and product boundary | [`VISION.md`](../VISION.md) |
| Evaluate whether Hibiki is usable for you | [Getting started](getting-started.md) |
| Run one post through the lifecycle | [Workflow guide](workflow.md) |
| Look up a command or input contract | [CLI reference](cli-reference.md) |
| Understand ownership and trust boundaries | [Architecture](architecture.md) |
| Contribute code or documentation | [`CONTRIBUTING.md`](../CONTRIBUTING.md) |
| Report a vulnerability | [`SECURITY.md`](../SECURITY.md) |

## Source-of-truth hierarchy

1. [Accepted ADRs](decisions/README.md) define product ownership, safety, and
   learning semantics.
2. Code and deterministic tests define currently implemented behavior within
   those boundaries.
3. The [implementation plan](../PLAN.md) records completed phases and pending
   external work.
4. Guides explain how to use the implementation; they do not override ADRs.
5. [Learnings](learnings/INDEX.md) retain narrow operational discoveries.

Planned behavior should be labelled as planned. A guide must not describe an
external integration as available merely because the core CLI supports it.

## Maintainer map

- Product contract: [`VISION.md`](../VISION.md)
- Product and safety decisions: [`docs/decisions/`](decisions/README.md)
- Installation and first run: [`docs/getting-started.md`](getting-started.md)
- Lifecycle examples: [`docs/workflow.md`](workflow.md)
- CLI surface: [`docs/cli-reference.md`](cli-reference.md)
- System boundaries: [`docs/architecture.md`](architecture.md)
- Contribution process: [`CONTRIBUTING.md`](../CONTRIBUTING.md)
- Operational discoveries: [`docs/learnings/`](learnings/INDEX.md)

When the CLI changes, update the CLI reference and any affected workflow
example in the same pull request.
