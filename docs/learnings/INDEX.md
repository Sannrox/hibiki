# Learnings

These notes record narrow, verified operational discoveries. They are not
product decisions and cannot override an accepted ADR. Add a note when a
non-obvious dependency or platform behavior is likely to save future debugging
time; keep general contributor guidance in [`CONTRIBUTING.md`](../../CONTRIBUTING.md).

| Learning | Area | Summary |
| --- | --- | --- |
| [twitter-text-python314.md](twitter-text-python314.md) | publication | Pair twitter-text-parser with setuptools 80 on Python 3.14 because it imports pkg_resources. |
