#!/usr/bin/env bash
set -euo pipefail
HERE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
source "$HERE/common.sh"
[[ $# == 2 || ( $# == 3 && $3 == --regenerate ) ]] || {
    echo "Usage: $0 RUN_DIRECTORY fresh|tictactoe|trading|fastapi [--regenerate]" >&2; exit 2;
}
smoke_load "$1" "$2"
options=()
if [[ $SMOKE_CASE == fresh ]]; then
    options+=(--need frontend-ide --need node --name 'RC0 first session' --slug rc0-first-session)
fi
if [[ ${3:-} == --regenerate ]]; then options+=(--regenerate); fi
# Keep elicitations visible. No blanket approval, forced resolution or host-X11 fallback.
step dc init "${options[@]}" --authorize host-x11 false
step dc config list
step dc config resolve
if [[ $SMOKE_CASE != fresh ]]; then
    git -C "$SMOKE_PROJECT" diff -- .devcapsule > "$SMOKE_ROOT/evidence/$SMOKE_CASE-config.diff"
fi
echo 'Configuration complete. Continue with 02-preview.sh; this is not an IDE acceptance result.'
