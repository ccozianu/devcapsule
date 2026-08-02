#!/usr/bin/env bash
# Manual acceptance test for the planned D-0004 V1 configuration experience.
#
# This script intentionally describes target behavior that the transitional CLI
# does not yet fully implement. In particular, it requires config
# set/bind/authorize, persistent host
# authorization, a container memory limit, and the v019 generic Python runtime
# boundary.
#
# Run this script from a host terminal, not from inside a DevCapsule container.
# It creates a new clone and new checkout-specific PyCharm system/log/cache
# directories. It never deletes either checkout or any persistent state.

set -Eeuo pipefail

REPOSITORY_URL=${REPOSITORY_URL:-git@github.com:ccozianu/devcapsule.git}
REPOSITORY_REVISION=${REPOSITORY_REVISION:-main}
NEW_CHECKOUT=${NEW_CHECKOUT:-"$HOME/work/provisional/costin3/myProjects/devcapsule"}
CHECKOUT_NAME=${CHECKOUT_NAME:-costin3-devcapsule}
NEW_STATE_ROOT=${NEW_STATE_ROOT:-"$HOME/work/provisional/costin3/.state/myProjects/devcapsule"}
CONTAINER_NAME=${CONTAINER_NAME:-devcapsule-dogfood-costin3}
MEMORY_LIMIT=${MEMORY_LIMIT:-8GiB}
DOGFOOD_IMAGE=${DOGFOOD_IMAGE:-devcapsule-local-pycharm:debug-v019}
BASE_IMAGE=${BASE_IMAGE:-devcapsule-local-base:v019}
PYTHON_BIN=${PYTHON_BIN:-python3.12}
RUN_BUILD_GATE=${RUN_BUILD_GATE:-1}

SHARED_HOME=${SHARED_HOME:-"$HOME/.config/docker-pycharm-codex/state/home"}
SHARED_PYCHARM_CONFIG=${SHARED_PYCHARM_CONFIG:-"$HOME/.config/docker-pycharm-codex/state/config"}
SHARED_PYCHARM_PLUGINS=${SHARED_PYCHARM_PLUGINS:-"$HOME/.config/docker-pycharm-codex/plugins"}
NEW_PYCHARM_SYSTEM=${NEW_PYCHARM_SYSTEM:-"$NEW_STATE_ROOT/system"}
NEW_PYCHARM_LOG=${NEW_PYCHARM_LOG:-"$NEW_STATE_ROOT/log"}
NEW_PYCHARM_CACHE=${NEW_PYCHARM_CACHE:-"$NEW_STATE_ROOT/home/.cache"}

CONFIG_HOME=${XDG_CONFIG_HOME:-"$HOME/.config"}
CONFIG_ROOT="$CONFIG_HOME/devcapsule"

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || fail "required command is unavailable: $1"
}

echo "V1 second-checkout dogfood test"
echo "  repository:       $REPOSITORY_URL ($REPOSITORY_REVISION)"
echo "  new checkout:     $NEW_CHECKOUT"
echo "  checkout identity: $CHECKOUT_NAME"
echo "  new state root:   $NEW_STATE_ROOT"
echo "  memory limit:     $MEMORY_LIMIT"
echo "  dogfood image:    $DOGFOOD_IMAGE"
echo "  locked base:      $BASE_IMAGE"

require_command git
require_command docker
require_command "$PYTHON_BIN"
require_command sha256sum

test "$HOME" = /home/costin || fail "this laptop-specific test expects HOME=/home/costin; found $HOME"
test ! -e "$NEW_CHECKOUT" || fail "new checkout path already exists: $NEW_CHECKOUT"
test -d "$SHARED_HOME" || fail "missing shared persistent home: $SHARED_HOME"
test -d "$SHARED_PYCHARM_CONFIG" || fail "missing shared PyCharm config: $SHARED_PYCHARM_CONFIG"
test -d "$SHARED_PYCHARM_PLUGINS" || fail "missing shared PyCharm plugins: $SHARED_PYCHARM_PLUGINS"
docker image inspect "$DOGFOOD_IMAGE" >/dev/null || \
  fail "run 'devcapsule images build --type environment --project CHECKOUT --base $BASE_IMAGE --alias $DOGFOOD_IMAGE' first"

IMAGE_INSPECTION=$(mktemp "${TMPDIR:-/tmp}/devcapsule-v019-image.XXXXXX.json")
docker image inspect "$DOGFOOD_IMAGE" >"$IMAGE_INSPECTION"
"$PYTHON_BIN" - "$IMAGE_INSPECTION" <<'PY'
import json
import sys
from pathlib import Path

image = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))[0]
config = image["Config"]
labels = config.get("Labels") or {}
assert labels.get("devcapsule.image.managed") == "true", labels
assert labels.get("devcapsule.metadata.version") == "1", labels
assert config.get("Entrypoint") == [
    "/usr/bin/tini",
    "--",
    "/opt/devcapsule/bin/devcapsule.pex",
    "runtime",
], config.get("Entrypoint")
assert config.get("Cmd") == ["/etc/devcapsule/runtime-plan.json"], config.get("Cmd")
assert labels.get("devcapsule.image.kind") == "materialized", labels
assert labels.get("devcapsule.materialization.identity"), "missing materialization identity"
assert labels.get("devcapsule.materialization.descriptor"), "missing canonical formation descriptor"
assert labels.get("devcapsule.materialization.base-identity"), "missing base identity"
assert labels.get("devcapsule.component.id") == "pycharm", labels
assert labels.get("devcapsule.image.canonical-name"), "missing canonical image name"
assert labels.get("devcapsule.pex.sha256"), "missing embedded PEX identity"
assert labels.get("devcapsule.component.sha256"), "missing component artifact identity"
assert labels.get("devcapsule.component.variant"), "missing component variant"
print("v019 generic image contract: PASS")
PY
rm -f "$IMAGE_INSPECTION"

docker run --rm --network none "$DOGFOOD_IMAGE" --help | \
  grep -F "usage: devcapsule runtime RUNTIME_PLAN.json" >/dev/null
docker run --rm --network none --entrypoint test "$DOGFOOD_IMAGE" \
  -r /etc/devcapsule/component-runtime-template.json
docker run --rm --network none --entrypoint test "$DOGFOOD_IMAGE" \
  ! -e /etc/devcapsule/runtime-plan.json

if docker container inspect devcapsule-dogfood-v1 >/dev/null 2>&1; then
  fail "close the existing devcapsule-dogfood-v1 container before sharing its home/config/plugins"
fi

mkdir -p "$(dirname "$NEW_CHECKOUT")"
git clone "$REPOSITORY_URL" "$NEW_CHECKOUT"
git -C "$NEW_CHECKOUT" checkout "$REPOSITORY_REVISION"

MANIFEST="$NEW_CHECKOUT/.devcapsule/devcapsule.toml"
LOCK="$NEW_CHECKOUT/.devcapsule/devcapsule.linux-amd64.lock"
test -f "$MANIFEST" || fail "clone has no committed DevCapsule manifest"
test -f "$LOCK" || fail "clone has no committed linux-amd64 lock"

readarray -t PROJECT_VALUES < <("$PYTHON_BIN" - "$MANIFEST" "$CONFIG_ROOT" <<'PY'
import sys
import tomllib
from pathlib import Path
from urllib.parse import quote

manifest_path = Path(sys.argv[1])
config_root = Path(sys.argv[2])
with manifest_path.open("rb") as stream:
    manifest = tomllib.load(stream)
project = manifest["project"]
project_directory = (
    config_root
    / "projects"
    / quote(str(project["creator"]), safe="")
    / quote(str(project["slug"]), safe="")
)
print(project_directory)
print(project["mount"])
print(project["creator"])
print(project["slug"])
PY
)

PROJECT_CONFIG_DIRECTORY=${PROJECT_VALUES[0]}
CONTAINER_PROJECT_PATH=${PROJECT_VALUES[1]}
PROJECT_CREATOR=${PROJECT_VALUES[2]}
PROJECT_SLUG=${PROJECT_VALUES[3]}
ORIGINAL_CHECKOUT_RECORD="$PROJECT_CONFIG_DIRECTORY/devcapsule.checkout.toml"
NEW_CHECKOUT_RECORD="$PROJECT_CONFIG_DIRECTORY/checkouts/$CHECKOUT_NAME.checkout.toml"
NEW_RESOLVED_RECORD="$PROJECT_CONFIG_DIRECTORY/checkouts/$CHECKOUT_NAME.resolved.toml"

test -f "$ORIGINAL_CHECKOUT_RECORD" || fail "expected existing default checkout record: $ORIGINAL_CHECKOUT_RECORD"
test ! -e "$NEW_CHECKOUT_RECORD" || fail "named checkout record already exists: $NEW_CHECKOUT_RECORD"
test ! -e "$NEW_RESOLVED_RECORD" || fail "named resolution already exists: $NEW_RESOLVED_RECORD"
ORIGINAL_RECORD_HASH=$(sha256sum "$ORIGINAL_CHECKOUT_RECORD")

LEGACY_LOCK_IMAGE=$("$PYTHON_BIN" - "$LOCK" <<'PY'
import sys
import tomllib
from pathlib import Path

with Path(sys.argv[1]).open("rb") as stream:
    lock = tomllib.load(stream)
print(lock.get("image", {}).get("reference", ""))
PY
)
test -z "$LEGACY_LOCK_IMAGE" || \
  fail "the cloned lock still selects completed image $LEGACY_LOCK_IMAGE instead of formation inputs"

echo "Observed committed project identity: $PROJECT_CREATOR / $PROJECT_SLUG"
echo "Observed container project path: $CONTAINER_PROJECT_PATH"
echo "Existing checkout record (must remain unchanged): $ORIGINAL_CHECKOUT_RECORD"
echo "New checkout record: $NEW_CHECKOUT_RECORD"

if [[ "$RUN_BUILD_GATE" == 1 ]]; then
  (
    cd "$NEW_CHECKOUT/devcapsule"
    "$PYTHON_BIN" -m nox -s build
  )
fi

DEVCAPSULE_PEX="$NEW_CHECKOUT/devcapsule/dist/devcapsule.pex"
test -f "$DEVCAPSULE_PEX" || fail "missing built PEX: $DEVCAPSULE_PEX"
DC=("$PYTHON_BIN" "$DEVCAPSULE_PEX")

mkdir -p "$NEW_PYCHARM_SYSTEM" "$NEW_PYCHARM_LOG" "$NEW_PYCHARM_CACHE"

# This explicit operation is the proposed way to assign a workstation-owned
# name when the same portable project identity already has a default checkout.
# Once registered, the canonical project --path selects this record without
# requiring the name on every later command.
"${DC[@]}" project --path "$NEW_CHECKOUT" checkout register "$CHECKOUT_NAME"

# Ordinary value: the resolved Docker plan should apply this as an 8 GiB hard
# memory limit. This is intentionally not an authorization.
"${DC[@]}" project --path "$NEW_CHECKOUT" config set runtime.memory-limit "$MEMORY_LIMIT"

# Explicitly reuse login/settings/plugin state. The implementation must warn
# that these external directories may contain credentials or personal data.
# The original capsule was required to stop above because this test does not
# claim that these PyCharm locations are safe for concurrent read-write use.
"${DC[@]}" project --path "$NEW_CHECKOUT" config bind home --host-directory "$SHARED_HOME"
"${DC[@]}" project --path "$NEW_CHECKOUT" config bind pycharm/config --host-directory "$SHARED_PYCHARM_CONFIG"
"${DC[@]}" project --path "$NEW_CHECKOUT" config bind pycharm/plugins --host-directory "$SHARED_PYCHARM_PLUGINS"

# Keep lock-bearing, operational, and rebuildable state distinct for the new
# checkout identity.
"${DC[@]}" project --path "$NEW_CHECKOUT" config bind pycharm/system --host-directory "$NEW_PYCHARM_SYSTEM"
"${DC[@]}" project --path "$NEW_CHECKOUT" config bind pycharm/log --host-directory "$NEW_PYCHARM_LOG"
"${DC[@]}" project --path "$NEW_CHECKOUT" config bind pycharm/cache --host-directory "$NEW_PYCHARM_CACHE"

# Match the explicitly requested capabilities of the currently inspected
# dogfood instance. Host networking is a known isolation relaxation, not a
# default. A later bridge-network test should remove this authorization once
# the dogfood workflow no longer needs it.
"${DC[@]}" project --path "$NEW_CHECKOUT" config authorize docker-daemon host-socket
"${DC[@]}" project --path "$NEW_CHECKOUT" config authorize network host
"${DC[@]}" project --path "$NEW_CHECKOUT" config authorize development-sudo true

# Holistic validation must create only the named generated plan. It must not
# acquire an image or launch a container; the explicitly built v019 checkpoint
# is already local here.
"${DC[@]}" project --path "$NEW_CHECKOUT" config resolve

test -f "$NEW_CHECKOUT_RECORD" || fail "configuration did not create the named checkout record"
test -f "$NEW_RESOLVED_RECORD" || fail "resolution did not create the named resolved record"
test "$(stat -c %a "$NEW_CHECKOUT_RECORD")" = 600 || fail "checkout record is not mode 600"
test "$(stat -c %a "$NEW_RESOLVED_RECORD")" = 600 || fail "resolved record is not mode 600"
test "$(sha256sum "$ORIGINAL_CHECKOUT_RECORD")" = "$ORIGINAL_RECORD_HASH" || \
  fail "configuring the new checkout modified the original checkout record"

echo "Named checkout input:"
sed -n '1,260p' "$NEW_CHECKOUT_RECORD"
echo "Named generated resolution:"
sed -n '1,320p' "$NEW_RESOLVED_RECORD"

RUN_LOG=$(mktemp "${TMPDIR:-/tmp}/devcapsule-second-checkout.XXXXXX.log")
echo "Launching $CONTAINER_NAME; console output is also saved at $RUN_LOG"
"${DC[@]}" project --path "$NEW_CHECKOUT" run --name "$CONTAINER_NAME" > >(tee "$RUN_LOG") 2>&1 &
RUN_PID=$!

CONTAINER_READY=0
for _ in {1..90}; do
  if docker container inspect "$CONTAINER_NAME" >/dev/null 2>&1; then
    CONTAINER_READY=1
    break
  fi
  if ! kill -0 "$RUN_PID" >/dev/null 2>&1; then
    wait "$RUN_PID" || true
    fail "DevCapsule exited before the container became inspectable; see $RUN_LOG"
  fi
  sleep 1
done
test "$CONTAINER_READY" = 1 || fail "container did not become inspectable within 90 seconds"

INSPECT_JSON=$(mktemp "${TMPDIR:-/tmp}/devcapsule-second-checkout-inspect.XXXXXX.json")
docker inspect "$CONTAINER_NAME" >"$INSPECT_JSON"

"$PYTHON_BIN" - "$INSPECT_JSON" "$NEW_CHECKOUT" "$CONTAINER_PROJECT_PATH" \
  "$SHARED_HOME" "$SHARED_PYCHARM_CONFIG" "$SHARED_PYCHARM_PLUGINS" \
  "$NEW_PYCHARM_SYSTEM" "$NEW_PYCHARM_LOG" "$NEW_PYCHARM_CACHE" <<'PY'
import json
import sys
from pathlib import Path

(
    inspect_path,
    checkout,
    project_destination,
    shared_home,
    shared_config,
    shared_plugins,
    new_system,
    new_log,
    new_cache,
) = sys.argv[1:]
container = json.loads(Path(inspect_path).read_text(encoding="utf-8"))[0]
host = container["HostConfig"]
config = container["Config"]
mounts = {item["Destination"]: item for item in container["Mounts"]}
environment = dict(item.split("=", 1) for item in config.get("Env", []) if "=" in item)

expected_mounts = {
    project_destination: checkout,
    "/home/devcapsule": shared_home,
    "/ide-config": shared_config,
    "/ide-plugins": shared_plugins,
    "/ide-project-state/system": new_system,
    "/ide-project-state/log": new_log,
    "/home/devcapsule/.cache": new_cache,
}
for destination, source in expected_mounts.items():
    actual = mounts.get(destination)
    assert actual is not None, f"missing mount destination {destination}"
    assert actual["Source"] == source, (destination, actual["Source"], source)
    assert actual["RW"] is True, f"expected read-write mount: {destination}"

docker_socket = mounts.get("/run/host-docker.sock")
assert docker_socket is not None, "host Docker socket is not mounted"
assert host["NetworkMode"] == "host", host["NetworkMode"]
assert host["Privileged"] is False
assert host["AutoRemove"] is True
assert host["Memory"] == 8 * 1024**3, host["Memory"]
assert config["User"] not in ("", "0", "0:0", "root")
assert config["WorkingDir"] == project_destination
assert config["Entrypoint"] == [
    "/usr/bin/tini",
    "--",
    "/opt/devcapsule/bin/devcapsule.pex",
    "runtime",
]
assert environment.get("HOME") == "/home/devcapsule"
assert environment.get("PROJECT_PATH") == project_destination
assert environment.get("DOCKER_HOST") == "unix:///run/host-docker.sock"
assert environment.get("ENABLE_SUDO") == "1"
print("Automated live-container inspection: PASS")
print(f"Container runtime selected by launcher: {host.get('Runtime')}")
PY

rm -f "$INSPECT_JSON"

cat <<'CHECKLIST'

Complete these checks inside the newly opened PyCharm before closing it:

  [ ] The project is the new host clone, not the original checkout.
  [ ] Existing IDE preferences, plugins, and required login state are present.
  [ ] `git status --short` describes the new clone correctly.
  [ ] `docker version` reaches the host daemon.
  [ ] `sudo -n true && echo sudo-ok` prints `sudo-ok`.
  [ ] `/sys/fs/cgroup/memory.max` reports 8589934592 (8 GiB).
  [ ] Normal editing, tests, and one agent interaction work as expected.

Close PyCharm when those checks are complete. The script will then verify the
foreground lifecycle and automatic container removal.
CHECKLIST

wait "$RUN_PID"

if docker container inspect "$CONTAINER_NAME" >/dev/null 2>&1; then
  fail "container still exists after the foreground IDE exited"
fi

test "$(sha256sum "$ORIGINAL_CHECKOUT_RECORD")" = "$ORIGINAL_RECORD_HASH" || \
  fail "the original checkout record changed during launch"

echo "First launch and lifecycle: PASS"
echo "Run log retained for debugging: $RUN_LOG"
echo
echo "Launch once more to verify state continuity, then close PyCharm:"
"${DC[@]}" project --path "$NEW_CHECKOUT" run --name "${CONTAINER_NAME}-restart"

if docker container inspect "${CONTAINER_NAME}-restart" >/dev/null 2>&1; then
  fail "restart container still exists after the foreground IDE exited"
fi

cat <<EOF

Second-checkout dogfood script completed.

Report:
  Clone and full build gate:              PASS
  Distinct named checkout record:         PASS
  Original checkout record unchanged:     PASS
  Per-operation and holistic resolution:  PASS
  Live Docker-plan inspection:            PASS
  Foreground exit and auto-remove:         PASS
  Second-launch persistence:              CONFIRM MANUALLY
  IDE/settings/plugins/login continuity:  CONFIRM MANUALLY
  Docker, sudo, memory, and agent checks:  CONFIRM MANUALLY

Retained resources (not deleted by this script):
  checkout:   $NEW_CHECKOUT
  state:      $NEW_STATE_ROOT
  config:     $NEW_CHECKOUT_RECORD
  resolution: $NEW_RESOLVED_RECORD
  log:        $RUN_LOG
EOF
