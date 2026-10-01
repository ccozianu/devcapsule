#!/usr/bin/env bash
# Ad hoc documented remedies, using exactly the same candidate and local state.
set -euo pipefail
HERE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
source "$HERE/common.sh"
[[ $# -ge 3 ]] || { echo "Usage: $0 RUN_DIRECTORY CASE PROJECT_SUBCOMMAND [ARGS...]" >&2; exit 2; }
smoke_load "$1" "$2"
shift 2
step dc "$@"
