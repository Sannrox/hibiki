#!/usr/bin/env bash
# Install the BirdClaw CLI (https://github.com/steipete/birdclaw), Hibiki's
# sole X transport in v0. Prefers Homebrew on macOS; falls back to npm.
# Authentication is not handled here: BirdClaw owns its own credentials via
# `xurl` / its local session, per docs/decisions/002-runtime-and-boundaries.md.
set -euo pipefail

if command -v birdclaw >/dev/null 2>&1; then
    echo "birdclaw already installed: $(command -v birdclaw)"
    birdclaw --version 2>/dev/null || true
    exit 0
fi

if command -v brew >/dev/null 2>&1; then
    echo "Installing birdclaw via Homebrew (steipete/tap/birdclaw)..."
    brew install steipete/tap/birdclaw
elif command -v npm >/dev/null 2>&1; then
    echo "Homebrew not found; installing birdclaw globally via npm..."
    npm install -g birdclaw
else
    echo "error: neither brew nor npm is available; install one of them first" >&2
    echo "  Homebrew: https://brew.sh" >&2
    echo "  or from source: https://github.com/steipete/birdclaw#install" >&2
    exit 1
fi

command -v birdclaw >/dev/null 2>&1 || {
    echo "error: installation finished but birdclaw is not on PATH" >&2
    exit 1
}

echo "birdclaw installed: $(command -v birdclaw)"
birdclaw --version 2>/dev/null || true
echo
echo "Next steps: authenticate BirdClaw itself (xurl for live reads/writes)."
echo "Hibiki only needs HIBIKI_BIRDCLAW_ACCOUNT to match a configured account."
