#!/usr/bin/env bash
# Run from the PROJECT ROOT in the actual IDE terminal, never on the host.
set -euo pipefail
umask 077
[[ $# == 1 && -d .rc0-smoke ]] || { echo "Usage, from project root: bash .rc0-smoke/04-inside.sh CASE" >&2; exit 2; }
[[ -f /.dockerenv ]] || { echo 'Run this inside the DevCapsule IDE terminal.' >&2; exit 2; }
case "$1" in fresh|tictactoe|trading|fastapi) ;; *) echo 'Unknown case' >&2; exit 2;; esac
# pipefail propagates a failing install/test despite tee; runs keep separate logs.
exec > >(tee ".rc0-smoke/workload-$(date -u +%Y%m%dT%H%M%SZ).log") 2>&1
case "$1" in
    fresh)
        node --version
        npm --version
        # Created by the human in the IDE; do not fabricate the edit/save evidence.
        test -f hello.js
        [[ $(node hello.js) == 'Hello, RC0!' ]]
        ;;
    tictactoe)
        node --version
        npm --version
        npm ci
        npm test
        npm run build
        ;;
    trading)
        python3 --version
        python3 -m venv .venv
        .venv/bin/python -m pip install -e .
        # The sample's own test session uses unittest, with no model/network calls.
        .venv/bin/python -m unittest discover -s tests -v
        ;;
    fastapi)
        python3 --version
        node --version
        npm --version
        psql --version
        python3 -m venv .venv
        .venv/bin/python -m pip install -r backend/requirements-dev.txt
        (cd backend && ../.venv/bin/python -m pytest)
        (cd frontend && npm ci && npm run build)
        ;;
esac
echo 'PASS: in-capsule workload. GUI, agent and resume observations are separate.'
