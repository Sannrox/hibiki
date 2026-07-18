# Security policy

Hibiki handles public source material and can publish to an external account.
A report is security-sensitive when it could, for example:

- bypass exact-text approval or the live-write guard;
- cause duplicate or unintended X publication;
- expose credentials, private source material, or analytics data;
- admit untrusted evidence outside the scoped Hibiki producer; or
- make a supposedly deterministic test perform a live external write.

## Supported versions

Hibiki is pre-1.0 and has no released support branches. Security fixes target
the current `main` branch. Older commits and forks are not maintained by this
project.

## Report a vulnerability

Use GitHub's private vulnerability reporting form:

<https://github.com/Sannrox/hibiki/security/advisories/new>

Include the affected commit, impact, reproduction steps, and any suggested
mitigation. Do not include credentials, private source content, or live account
tokens. If private vulnerability reporting is unavailable, open a minimal
public issue requesting a private contact channel, without exploit details.

The project currently makes no guaranteed response-time commitment. The
maintainer will acknowledge the report, validate it, coordinate a fix, and
credit the reporter if desired and safe to do so. Please allow time for a fix
before public disclosure.

## Safe research expectations

- Use repositories, accounts, and data you own or have permission to test.
- Keep `HIBIKI_ALLOW_LIVE_WRITES=false` unless an authorized live test
  explicitly requires publication.
- Do not test against another person's X account or production deployment.
- Stop if testing could expose private material or create an unreconciled
  external write.

Operational safety behavior is documented in
[`docs/architecture.md`](docs/architecture.md#trust-boundaries-and-failure-behavior)
and the accepted [ADRs](docs/decisions/README.md).
