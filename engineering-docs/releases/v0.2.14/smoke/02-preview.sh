#!/usr/bin/env bash
set -euo pipefail
HERE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
source "$HERE/common.sh"
smoke_load "$@"
if container_exists; then
    echo 'This case already has a container. End its IDE session before the preview.' >&2; exit 2
fi
# This can download components and build the derived image. It is not a dry run.
step dc run --no-update-check --name "$SMOKE_CONTAINER" --print-command \
    > "$SMOKE_ROOT/evidence/$SMOKE_CASE-command.txt" \
    2> "$SMOKE_ROOT/evidence/$SMOKE_CASE-preparation.log"
[[ -s "$SMOKE_ROOT/evidence/$SMOKE_CASE-command.txt" ]]
if container_exists; then
    echo 'FAIL: preview left the named project container behind.' >&2; exit 1
fi
echo 'Preview completed without a named project container. Review command.txt and preparation.log.'
echo 'Do not execute the printed command: its transient paths may already have been removed.'
