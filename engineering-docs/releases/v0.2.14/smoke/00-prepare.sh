#!/usr/bin/env bash
# Downloads only; no containers, package installs or existing checkout changes.
set -euo pipefail
umask 077
HERE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
source "$HERE/common.sh"
SMOKE_CHECK_DOCKER=1
if [[ ${1:-} == --cli-only ]]; then SMOKE_CHECK_DOCKER=0; shift; fi
[[ $# == 1 || $# == 2 ]] || { echo "Usage: $0 [--cli-only] NEW_RUN_DIRECTORY [RC0_PEX]" >&2; exit 2; }
[[ $(uname -sm) == 'Linux x86_64' ]] || { echo 'Requires Linux x86_64 (including WSL2).' >&2; exit 2; }
for tool in git curl sha256sum; do command -v "$tool" >/dev/null; done
if [[ $SMOKE_CHECK_DOCKER == 1 ]]; then
    docker info >/dev/null
    docker buildx version
fi
mkdir -- "$1"  # Deliberately refuse to overwrite or resume an existing run.
SMOKE_ROOT=$(cd -- "$1" && pwd -P)
mkdir -p "$SMOKE_ROOT"/{bin,projects/fresh,evidence,xdg}
if [[ $# == 2 ]]; then
    cp -- "$2" "$SMOKE_ROOT/bin/devcapsule.pex"
else
    curl --fail --location --retry 3 --output "$SMOKE_ROOT/bin/devcapsule.pex" \
        https://github.com/ccozianu/devcapsule/releases/download/v0.2.14-rc0/devcapsule.pex
fi
echo "$RC0_SHA  $SMOKE_ROOT/bin/devcapsule.pex" | sha256sum --check
chmod 700 "$SMOKE_ROOT/bin/devcapsule.pex"
# Isolate the executable's cache even for the identity probe.
XDG_CACHE_HOME="$SMOKE_ROOT/xdg/cache" "$SMOKE_ROOT/bin/devcapsule.pex" version --json > "$SMOKE_ROOT/evidence/version.json"
uname -sm > "$SMOKE_ROOT/evidence/platform.txt"
if [[ $SMOKE_CHECK_DOCKER == 1 ]]; then
    docker version --format '{{.Server.Version}}' >> "$SMOKE_ROOT/evidence/platform.txt"
else
    echo 'Docker not checked: CLI-only preparation.' >> "$SMOKE_ROOT/evidence/platform.txt"
fi
while read -r name repository revision; do
    git clone --quiet --no-checkout "https://github.com/ccozianu/$repository.git" "$SMOKE_ROOT/projects/$name"
    git -C "$SMOKE_ROOT/projects/$name" checkout --quiet --detach "$revision"
    [[ $(git -C "$SMOKE_ROOT/projects/$name" rev-parse HEAD) == "$revision" ]]
    printf '%s %s %s\n' "$name" "$repository" "$revision" >> "$SMOKE_ROOT/evidence/projects.txt"
    mkdir -p "$SMOKE_ROOT/evidence/$name-original"
    cp -a "$SMOKE_ROOT/projects/$name/.devcapsule" "$SMOKE_ROOT/evidence/$name-original/"
done <<'PROJECTS'
tictactoe devcapsule-sample-typescript-tictactoe f1e2e6febf98b3058f4d35c209d06844c6c14dc4
trading devcapsule-sample-trading-research 687d245eba9ff461ddf6013aac7d80718ebc831f
fastapi devcapsule-sample-fastapi-webbapp 31c86c4a5f7d73e5864fd3d9311ee26243140fbe
PROJECTS
for name in fresh tictactoe trading fastapi; do
    mkdir "$SMOKE_ROOT/projects/$name/.rc0-smoke"
    cp "$HERE/04-inside.sh" "$SMOKE_ROOT/projects/$name/.rc0-smoke/"
done
cp "$HERE/results-template.md" "$SMOKE_ROOT/evidence/results.md"
printf 'v0.2.14-rc0\n' > "$SMOKE_ROOT/.rc0-smoke"
echo "Prepared $SMOKE_ROOT. Follow README.md; record observations in evidence/results.md."
