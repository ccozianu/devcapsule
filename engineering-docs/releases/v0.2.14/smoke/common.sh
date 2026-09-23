#!/usr/bin/env bash
# Sourced by the host steps. All mutable DevCapsule state belongs to this run.
set -euo pipefail
umask 077
RC0_SHA=2a425a39d2ed5319d1945dd91e34f693c299fa2c53acdf70a205024eea45d513
smoke_load() {
    [[ $# == 2 ]] || { echo 'Expected RUN_DIRECTORY CASE' >&2; exit 2; }
    SMOKE_ROOT=$(cd -- "$1" && pwd -P)
    [[ $(cat "$SMOKE_ROOT/.rc0-smoke" 2>/dev/null) == v0.2.14-rc0 ]] || {
        echo 'Use the run directory created by 00-prepare.sh.' >&2; exit 2;
    }
    SMOKE_CASE=$2
    case "$SMOKE_CASE" in fresh|tictactoe|trading|fastapi) ;; *) echo 'Unknown case' >&2; exit 2;; esac
    SMOKE_PROJECT="$SMOKE_ROOT/projects/$SMOKE_CASE"
    SMOKE_PEX="$SMOKE_ROOT/bin/devcapsule.pex"
    echo "$RC0_SHA  $SMOKE_PEX" | sha256sum --check --status
    export XDG_CONFIG_HOME="$SMOKE_ROOT/xdg/config"
    export XDG_STATE_HOME="$SMOKE_ROOT/xdg/state"
    export XDG_DATA_HOME="$SMOKE_ROOT/xdg/data"
    export XDG_CACHE_HOME="$SMOKE_ROOT/xdg/cache"
    unset DEVCAPSULE_RUNTIME_PEX
    local suffix
    suffix=$(printf '%s' "$SMOKE_ROOT" | sha256sum)
    SMOKE_CONTAINER="rc0-$SMOKE_CASE-${suffix:0:12}"
}
dc() { "$SMOKE_PEX" project --path "$SMOKE_PROJECT" "$@"; }
# Preserve the interactive terminal: log argv/exit, not login or desktop tokens.
step() {
    local result=0
    printf '%s ' "$(date -u +%FT%TZ)" >> "$SMOKE_ROOT/evidence/commands.log"
    printf '%q ' "$@" >> "$SMOKE_ROOT/evidence/commands.log"
    printf '\n' >> "$SMOKE_ROOT/evidence/commands.log"
    "$@" || result=$?
    printf 'exit=%s\n' "$result" >> "$SMOKE_ROOT/evidence/commands.log"
    return "$result"
}
