# Design decisions

The initial design interview is complete. These ADRs are the implementation
boundary:

1. [Product and audience contract](001-product-and-audience.md)
2. [Runtime and system boundaries](002-runtime-and-boundaries.md)
3. [Automation, approval, and publication](003-automation-and-publication.md)
4. [Evidence, evaluation, and learning](004-evidence-and-learning.md)

Changes to these decisions require an explicit ADR amendment. Implementation
details that do not alter the boundaries may be decided in `PLAN.md` steps.

## Reading and changing decisions

ADRs are normative. The guides in [`docs/`](../README.md) explain the accepted
design but do not override it. When code, a guide, and an accepted ADR disagree
on product ownership, safety, or learning semantics, stop and resolve the
conflict explicitly.

To propose a change:

1. copy the existing ADR structure and assign the next sequence number;
2. mark the new ADR `Proposed` and identify which accepted decisions it
   supersedes or amends;
3. describe the decision, its safety implications, and migration impact; and
4. change implementation and user documentation only after the decision is
   accepted.

Purely explanatory corrections that preserve the decision do not require a
new ADR.
