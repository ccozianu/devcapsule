#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/build-pex.sh [options]

Options:
  --output PATH             Output archive. Defaults by source policy.
  --source-revision SHA     Assert and embed this full source commit.
  --source-repository URL   Public HTTPS GitHub repository URL.
  --allow-unpublished-revision
                            Embed clean HEAD without checking that GitHub advertises it.
  --allow-local-source      Permit dirty inputs and disclose unknown revision.

Output policy:
  strict public source     dist/devcapsule.pex
  clean unpublished HEAD  dist/devcapsule.pex
  --allow-local-source     dist/devcapsule-local.pex

Build a single-file DevCapsule PEX archive from the local package and the
pinned runtime dependency lock file.

Environment:
  PYTHON                 Python executable used to run PEX. Default: python
  DOCKER4IDES_PEX_SHEBANG  Shebang embedded in the archive.
                           Default: /usr/bin/env python3.12
  DOCKER4IDES_RUNTIME_PEX_ROOT
                         Runtime extraction/cache root embedded in the archive.
                         Default: /tmp/devcapsule-pex-root
  DEVCAPSULE_SOURCE_REVISION
                         Default value for --source-revision.
  DEVCAPSULE_SOURCE_REPOSITORY
                         Default value for --source-repository.
USAGE
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_dir="$(cd "${script_dir}/.." && pwd)"
output="${project_dir}/dist/devcapsule.pex"
output_explicit=0
source_revision="${DEVCAPSULE_SOURCE_REVISION:-}"
source_repository="${DEVCAPSULE_SOURCE_REPOSITORY:-}"
allow_local_source=0
allow_unpublished_revision=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --output)
      if [[ $# -lt 2 ]]; then
        echo "scripts/build-pex.sh: --output requires a path" >&2
        exit 2
      fi
      output="$2"
      output_explicit=1
      shift 2
      ;;
    --source-revision)
      if [[ $# -lt 2 ]]; then
        echo "scripts/build-pex.sh: --source-revision requires a value" >&2
        exit 2
      fi
      source_revision="$2"
      shift 2
      ;;
    --source-repository)
      if [[ $# -lt 2 ]]; then
        echo "scripts/build-pex.sh: --source-repository requires a value" >&2
        exit 2
      fi
      source_repository="${2%.git}"
      shift 2
      ;;
    --allow-local-source)
      allow_local_source=1
      shift
      ;;
    --allow-unpublished-revision)
      allow_unpublished_revision=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "scripts/build-pex.sh: unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

python_bin="${PYTHON:-python}"
pex_shebang="${DOCKER4IDES_PEX_SHEBANG:-/usr/bin/env python3.12}"
runtime_pex_root="${DOCKER4IDES_RUNTIME_PEX_ROOT:-/tmp/devcapsule-pex-root}"

if [[ ${allow_local_source} -eq 1 && ${output_explicit} -eq 0 ]]; then
  output="${project_dir}/dist/devcapsule-local.pex"
fi
if [[ "${output}" != /* ]]; then
  output="${project_dir}/${output}"
fi

if ! "${python_bin}" -c "import pex" >/dev/null 2>&1; then
  cat >&2 <<EOF
scripts/build-pex.sh: PEX is not installed for ${python_bin}.

Set up contributor dependencies first, or point PYTHON at that environment:
  python -m pip install -r devcapsule/dev-requirements.txt
  python -m pip install -e ./devcapsule --no-deps
  PYTHON=/path/to/venv/bin/python devcapsule/scripts/build-pex.sh
EOF
  exit 1
fi

mkdir -p "$(dirname "${output}")"

repo_root="$(git -C "${project_dir}" rev-parse --show-toplevel 2>/dev/null || true)"
head_revision=""
source_inputs_dirty=1
if [[ -n "${repo_root}" ]]; then
  head_revision="$(git -C "${repo_root}" rev-parse HEAD 2>/dev/null || true)"
  if [[ -z "$(git -C "${repo_root}" status --porcelain -- \
    devcapsule/devcapsule \
    devcapsule/pyproject.toml \
    devcapsule/requirements.txt \
    devcapsule/scripts/build-pex.sh)" ]]; then
    source_inputs_dirty=0
  fi
fi

if [[ ${allow_local_source} -eq 1 && ${allow_unpublished_revision} -eq 1 ]]; then
  echo "scripts/build-pex.sh: --allow-local-source cannot be combined with --allow-unpublished-revision" >&2
  exit 2
elif [[ ${allow_local_source} -eq 1 && -n "${source_revision}" ]]; then
  echo "scripts/build-pex.sh: --allow-local-source cannot be combined with --source-revision" >&2
  exit 2
elif [[ ${allow_local_source} -eq 1 ]]; then
  source_revision="unknown"
elif [[ -z "${source_revision}" ]]; then
  if [[ ${source_inputs_dirty} -eq 0 && -n "${head_revision}" ]]; then
    source_revision="${head_revision}"
  else
    source_revision="unknown"
  fi
elif [[ ${source_inputs_dirty} -ne 0 ]]; then
  echo "scripts/build-pex.sh: cannot assert a source revision with modified PEX inputs" >&2
  exit 1
elif [[ "${source_revision}" != "${head_revision}" ]]; then
  echo "scripts/build-pex.sh: source revision does not match checkout HEAD ${head_revision}" >&2
  exit 1
fi

if [[ -z "${source_repository}" && -n "${repo_root}" ]]; then
  remote="$(git -C "${repo_root}" remote get-url origin 2>/dev/null || true)"
  case "${remote}" in
    git@github.com:*) source_repository="https://github.com/${remote#git@github.com:}" ;;
    ssh://git@github.com/*) source_repository="https://github.com/${remote#ssh://git@github.com/}" ;;
    https://github.com/*) source_repository="${remote}" ;;
  esac
  source_repository="${source_repository%.git}"
fi
source_repository="${source_repository:-unknown}"
source_repository="${source_repository%/}"
source_url="unknown"
if [[ "${source_revision}" != "unknown" && "${source_repository}" != "unknown" ]]; then
  source_url="${source_repository}/commit/${source_revision}"
fi

if [[ ${allow_local_source} -eq 0 ]]; then
  if [[ ${source_inputs_dirty} -ne 0 ]]; then
    echo "scripts/build-pex.sh: public-revision builds require clean PEX inputs" >&2
    exit 1
  fi
  if [[ ! "${source_revision}" =~ ^[0-9a-f]{40,64}$ ]]; then
    echo "scripts/build-pex.sh: public-revision builds require a full hexadecimal commit" >&2
    exit 1
  fi
  if [[ ! "${source_repository}" =~ ^https://github\.com/[^/]+/[^/]+$ ]]; then
    echo "scripts/build-pex.sh: public-revision builds require a public HTTPS GitHub repository" >&2
    exit 1
  fi
  if [[ ${allow_unpublished_revision} -eq 0 ]] && \
    ! git ls-remote "${source_repository}.git" 2>/dev/null | cut -f1 | grep -Fqx "${source_revision}"; then
    echo "scripts/build-pex.sh: source revision is not advertised by the public GitHub repository" >&2
    exit 1
  fi
fi

build_root="$(mktemp -d "${TMPDIR:-/tmp}/devcapsule-pex-build.XXXXXXXX")"
trap 'rm -rf "${build_root}"' EXIT
cp "${project_dir}/pyproject.toml" "${project_dir}/README.md" "${build_root}/"
cp -a "${project_dir}/devcapsule" "${build_root}/devcapsule"
project_version="$("${python_bin}" -c 'import sys, tomllib; print(tomllib.load(open(sys.argv[1], "rb"))["project"]["version"])' "${project_dir}/pyproject.toml")"
"${python_bin}" - \
  "${build_root}/devcapsule/_build_info.json" \
  "${project_version}" \
  "${source_repository}" \
  "${source_revision}" \
  "${source_url}" <<'PY'
import json
from pathlib import Path
import sys

path, version, repository, revision, url = sys.argv[1:]
value = {
    "schema_version": 1,
    "version": version,
    "source_repository": repository,
    "source_revision": revision,
    "source_url": url,
}
Path(path).write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
PY

rm -rf "${project_dir}/build" "${project_dir}/devcapsule.egg-info"
"${python_bin}" -m pex \
  -r "${project_dir}/requirements.txt" \
  "${build_root}" \
  -c devcapsule \
  --python-shebang "${pex_shebang}" \
  --runtime-pex-root "${runtime_pex_root}" \
  -o "${output}"

echo "${output}"
echo "Source revision: ${source_revision}"
echo "Source URL: ${source_url}"
