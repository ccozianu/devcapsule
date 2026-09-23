#!/usr/bin/env bash
set -euo pipefail
HERE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
source "$HERE/common.sh"
smoke_load "$@"
echo "Open the printed desktop URL; run bash .rc0-smoke/04-inside.sh $SMOKE_CASE in the IDE terminal."
echo 'Exit through the IDE menu. Re-run this same host command later for the resume check.'
step dc run --no-update-check --name "$SMOKE_CONTAINER"
if docker container inspect "$SMOKE_CONTAINER" >/dev/null 2>&1; then
    echo "FAIL: $SMOKE_CONTAINER remains after foreground launch returned." >&2; exit 1
fi
echo 'Launcher exited successfully and the container is gone. Record the observed GUI result separately.'
