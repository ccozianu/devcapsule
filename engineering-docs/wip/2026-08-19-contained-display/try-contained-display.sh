#!/usr/bin/env bash
# Try the contained display from the current source branch, side by side with
# the legacy host X11 passthrough. Contained is the default; passthrough is the
# opt-in `host-x11` authorization (contained-display design note, T6/T7).
#
# Steps are separate subcommands so the interactive ones can be run one at a
# time from a desktop session with a browser:
#
#   try-contained-display.sh build      # PEX from this source + local recipe-8 base
#   try-contained-display.sh select     # authorize that base for the checkout, resolve
#   try-contained-display.sh contained  # project run: the capsule's own desktop (default)
#   try-contained-display.sh x11        # project run --authorize host-x11 true (legacy)
#   try-contained-display.sh verify     # while a run is up: mounts, ports, processes
#   try-contained-display.sh revert     # re-authorize the lock's published base
#
# Environment: PROJECT (default: this repository), BUILD_NETWORK (default:
# host — the Docker bridge has no DNS on some hosts), CONTAINER (default:
# devcapsule-display-try), NOX (default: nox on PATH, else python3 -m nox).
#
# Every path is relative to this script's own directory, so the script works
# from any checkout location, inside or outside a capsule. Needs: bash, git,
# docker, nox (pip/pipx install nox), and a desktop browser for the runs.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SRC="$REPO/devcapsule-src"
PEX="$SRC/dist/devcapsule-local.pex"
PROJECT="${PROJECT:-$REPO}"
BUILD_NETWORK="${BUILD_NETWORK:-host}"
CONTAINER="${CONTAINER:-devcapsule-display-try}"
TAG="devcapsule-base:display-$(git -C "$REPO" rev-parse --short HEAD)"
LOCK="$PROJECT/.devcapsule/devcapsule.linux-amd64.lock"

say() { printf '\n=== %s\n' "$*"; }

run_nox() {
    if [ -n "${NOX:-}" ]; then $NOX "$@"
    elif command -v nox >/dev/null 2>&1; then nox "$@"
    elif python3 -c 'import nox' >/dev/null 2>&1; then python3 -m nox "$@"
    else
        echo "nox is not installed; run 'pipx install nox' (or 'pip install nox') or set NOX=/path/to/nox" >&2
        exit 1
    fi
}

cmd_build() {
    say "Building the launcher/runtime PEX from this source"
    (cd "$SRC" && run_nox -s pex)
    say "Building a local recipe-8 base: $TAG (network: $BUILD_NETWORK)"
    "$PEX" images build --type base --tag "$TAG" --pex "$PEX" --allow-local-source --network "$BUILD_NETWORK"
    say "Base labels (expect: display=contained, recipe-version=8)"
    docker image inspect "$TAG" --format \
        'display={{index .Config.Labels "devcapsule.base.display"}} recipe-version={{index .Config.Labels "devcapsule.base.recipe-version"}}'
}

cmd_select() {
    say "Authorizing the local base for the checkout at $PROJECT and resolving"
    "$PEX" project --path "$PROJECT" config authorize base-image "$TAG"
    "$PEX" project --path "$PROJECT" config resolve
    "$PEX" project --path "$PROJECT" config list | grep -E 'base-image|host-x11' || true
}

cmd_contained() {
    say "Default run: contained desktop. Watch for 'Display: contained desktop' and the noVNC URL."
    say "Closing the browser tab does not end the session; closing the IDE or Ctrl-C does."
    "$PEX" project --path "$PROJECT" run --name "$CONTAINER"
}

cmd_x11() {
    say "Opt-in run: legacy host X11 passthrough. Watch for the credential-exposure statement."
    "$PEX" project --path "$PROJECT" run --name "$CONTAINER" --authorize host-x11 true
}

cmd_verify() {
    say "Mounts (contained: no /tmp/.X11-unix, a /run/devcapsule-display-token; x11: the reverse)"
    docker inspect "$CONTAINER" --format '{{range .Mounts}}{{.Destination}}{{"\n"}}{{end}}' | grep -E 'X11|display-token' || echo "(none of the display mounts present)"
    say "Environment crossing in (contained: no DISPLAY/XAUTHORITY from the host)"
    docker inspect "$CONTAINER" --format '{{range .Config.Env}}{{println .}}{{end}}' | grep -E '^(DISPLAY|XAUTHORITY)=' || echo "(no DISPLAY/XAUTHORITY passed from the host)"
    say "Published ports (contained under bridge networking: one 127.0.0.1 port -> 6080)"
    docker port "$CONTAINER" || true
    say "Process tree under the supervisor (contained: Xvnc, openbox, websockify, then the IDE)"
    docker exec "$CONTAINER" sh -c 'ps -eo pid,ppid,user,comm | awk "NR==1 || \$2==1"'
    say "Display transport recorded in the run manifest"
    docker exec "$CONTAINER" python3 -c 'import json;print(json.load(open("/etc/devcapsule/runtime-plan.json")).get("display"))'
}

cmd_revert() {
    # The [base] table's reference line, read without depending on a Python.
    locked="$(awk -F'"' '/^\[base\]/{f=1;next} /^\[/{f=0} f && /^reference[ \t]*=/{print $2; exit}' "$LOCK")"
    [ -n "$locked" ] || { echo "no base.reference found in $LOCK" >&2; exit 1; }
    say "Re-authorizing the lock's published base: $locked"
    "$PEX" project --path "$PROJECT" config authorize base-image "$locked"
    "$PEX" project --path "$PROJECT" config resolve
}

case "${1:-}" in
    build) cmd_build ;;
    select) cmd_select ;;
    contained) cmd_contained ;;
    x11) cmd_x11 ;;
    verify) cmd_verify ;;
    revert) cmd_revert ;;
    *) sed -n '2,22p' "${BASH_SOURCE[0]}"; exit 2 ;;
esac
