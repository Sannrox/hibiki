# Twitter text parser needs an explicit Python 3.14 compatibility dependency

## What happened
`twitter-text-parser` 3.0.0 installed but initially failed during import in Hibiki's Python 3.14 environment.

## Root cause
The package imports `pkg_resources`, which is available only when a compatible Setuptools release is installed.

## Rule
Pin `setuptools>=80,<81` with `twitter-text-parser==3.0.0` and suppress only its known deprecation warning. Treat the parser's bundled TLD list as stale: use `linkify-it-py` to find explicit HTTP(S) URL boundaries, then conservatively apply X's fixed URL weight to any URL the parser still counts literally. Do not maintain a custom URL scanner.
