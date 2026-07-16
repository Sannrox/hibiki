# ADR 004: Evidence, evaluation, and learning

## Status

Accepted.

## Decision

Hibiki owns one scoped BirdClaw evidence producer. It is restricted to the
`hibiki` namespace, the configured BirdClaw source instance,
`hibiki.publication` targets, bounded payloads, and two versioned schemas:

- `social.post_snapshot` contains the raw BirdClaw post statistics for a 24-hour
  or seven-day window: impressions, likes, replies, reposts, and quotes.
- `social.reply` contains a reply identifier, parent post identifier, author
  reference, text, public metrics, and collection timestamp.

BirdClaw's generated digest does not enter the funnel. It is a second model's
interpretation rather than source evidence. Account and follower snapshots are
also outside v0.

Chisei classifies replies as potential user, potential tester or contributor,
substantive technical discussion, general reaction, or irrelevant/low-signal.
The operator confirms the first 25 classifications. Thereafter Chisei may
accept high-confidence classifications while escalating ambiguous cases and
periodically sampling automatic results for drift.

The 24-hour snapshot is preliminary. The seven-day snapshot is the final
outcome used for learning. Chisei may surface a hypothesis after three
comparable posts but may recommend a strategy change only after eight
comparable posts and reproduction across two separate periods. It never
silently changes the writing voice or drafting strategy.
