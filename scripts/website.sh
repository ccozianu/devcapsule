#!/usr/bin/env bash
# The parent owns content and invokes its pinned presentation project.
set -euo pipefail
parent_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
website_root="$parent_root/website"
if [[ ! -f "$website_root/package.json" ]]; then
  echo 'Initialize the website submodule: git submodule update --init website' >&2
  exit 1
fi
export CONTENT_DIR="$parent_root"
case "${1:-preview}" in
  install) npm --prefix "$website_root" ci ;;
  preview) npm --prefix "$website_root" run dev ;;
  build) npm --prefix "$website_root" run build && npm --prefix "$website_root" run check ;;
  check) npm --prefix "$website_root" test && npm --prefix "$website_root" run check ;;
  *) echo 'Usage: scripts/website.sh [install|preview|build|check]' >&2; exit 2 ;;
esac
