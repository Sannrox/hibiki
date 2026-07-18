## Outcome

Describe the user-visible or contributor-visible result and why it is needed.

## Evidence

List the code, tests, ADRs, issues, or documentation that support the change.

## Verification

- [ ] `uv run pytest`
- [ ] `uv run ruff check .`
- [ ] `uv run python scripts/generate_contracts.py --check`
- [ ] New behavior includes deterministic success and failure coverage.
- [ ] CLI documentation and examples are synchronized where applicable.
- [ ] No secrets, private source material, account data, or analytics exports are included.
- [ ] No test or CI path can perform a live external-account write.

## Decision boundary

- [ ] This change preserves the accepted ADRs.
- [ ] Or, this change includes an explicit proposed/accepted ADR amendment.
