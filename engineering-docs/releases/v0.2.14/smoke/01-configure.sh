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
    options+=(--need frontend-ide --need node --name 'RC0 first session' --slug rc0-first-session --creator mailto:smoke@example.invalid)
fi
if [[ ${3:-} == --regenerate ]]; then options+=(--regenerate); fi
# Fixed test policy: base execution and the pinned samples' declared downloads;
# no host Docker/network/sudo/browser/X11 exposure. No personal login is supplied.
if [[ $SMOKE_CASE != fresh ]]; then
    options+=(--authorize network none)
    needs=$(python3 - "$SMOKE_PROJECT/.devcapsule/devcapsule.toml" <<'PYTHON'
import sys, tomllib
from pathlib import Path
print("\n".join(tomllib.loads(Path(sys.argv[1]).read_text())["capabilities"]["need"]))
PYTHON
)
    if grep -Fxq 'claude-code-agent' <<< "$needs"; then
        options+=(--authorize claude-code-download true)
    fi
    if grep -Fxq 'antigravity-agent' <<< "$needs"; then
        options+=(--authorize antigravity-download true)
    fi
fi
step dc init "${options[@]}" --authorize base-image default \
    --authorize docker-daemon none \
    --authorize development-sudo false --authorize host-browser false \
    --authorize host-x11 false < /dev/null
step dc config list
step dc config resolve
if [[ $SMOKE_CASE != fresh ]]; then
    git -C "$SMOKE_PROJECT" diff -- .devcapsule > "$SMOKE_ROOT/evidence/$SMOKE_CASE-config.diff"
fi
echo 'Configuration complete. Follow stories.md: ordinary first launch precedes preview.'
