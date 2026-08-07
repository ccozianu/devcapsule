#!/usr/bin/env bash
set -euo pipefail

IMAGE="pycharm-isolated:latest"
PYCHARM_SRC=""
BUILD_NETWORK="${DOCKER_BUILD_NETWORK:-default}"

usage() {
  cat <<'USAGE'
Usage:
  ./build-image.sh --pycharm /path/to/pycharm.tar.gz|/path/to/unpacked-pycharm [--image pycharm-isolated:latest] [--network default|host|none|...]

The script normalizes the supplied PyCharm distribution into the Docker build
context as ./pycharm/, then builds the image.

Options:
  --pycharm PATH     PyCharm .tar.gz or unpacked PyCharm directory
  --image IMAGE      Docker image tag. Default: pycharm-isolated:latest
  --network MODE     Docker build network mode. Default: default, or DOCKER_BUILD_NETWORK if set

Set DOCKER_BUILD_NETWORK=host or pass --network host only when the normal Docker
build network cannot reach package repositories from this host.
USAGE
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --pycharm) PYCHARM_SRC="${2:?missing value for --pycharm}"; shift 2 ;;
    --image) IMAGE="${2:?missing value for --image}"; shift 2 ;;
    --network) BUILD_NETWORK="${2:?missing value for --network}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [ -z "$PYCHARM_SRC" ]; then
  echo "Missing --pycharm" >&2
  usage >&2
  exit 2
fi

PYCHARM_SRC="$(readlink -f "$PYCHARM_SRC")"
WORKDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

cp "$WORKDIR/Dockerfile" "$WORKDIR/entrypoint.sh" "$WORKDIR/bootstrap-project.sh" "$WORKDIR/check-runtime-deps.sh" "$TMPDIR/"
mkdir -p "$TMPDIR/image-assets"
cp "$WORKDIR/image-assets/vibe-coding-process.md" "$TMPDIR/image-assets/"
mkdir -p "$TMPDIR/pycharm"

if [ -d "$PYCHARM_SRC" ]; then
  shopt -s dotglob
  cp -a "$PYCHARM_SRC"/* "$TMPDIR/pycharm/"
else
  mkdir -p "$TMPDIR/extract"
  tar -xzf "$PYCHARM_SRC" -C "$TMPDIR/extract"
  TOP="$(find "$TMPDIR/extract" -mindepth 1 -maxdepth 1 -type d | head -n 1)"
  if [ -z "$TOP" ]; then
    echo "Could not find top-level PyCharm directory inside archive" >&2
    exit 1
  fi
  shopt -s dotglob
  cp -a "$TOP"/* "$TMPDIR/pycharm/"
fi

if [ ! -x "$TMPDIR/pycharm/bin/pycharm.sh" ]; then
  echo "The supplied PyCharm source does not contain executable bin/pycharm.sh" >&2
  exit 1
fi

BUILD_ARGS=(
  --network="$BUILD_NETWORK"
  -t "$IMAGE"
)

if [ "$BUILD_NETWORK" = "host" ]; then
  BUILD_ARGS+=(--allow network.host)
fi

docker buildx build "${BUILD_ARGS[@]}" "$TMPDIR"
