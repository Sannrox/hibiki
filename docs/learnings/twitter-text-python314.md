# Twitter text parser is incompatible with Python 3.14

## What happened
`twitter-text-parser` 3.0.0 installed but failed during import in Hibiki's Python 3.14 environment.

## Root cause
The package imports `pkg_resources`, which is no longer available in the locked runtime.

## Rule
Keep X text validation dependency-free unless a parser is verified against Hibiki's current Python runtime.
