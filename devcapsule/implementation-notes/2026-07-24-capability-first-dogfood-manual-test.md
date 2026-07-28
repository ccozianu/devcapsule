# Manual Test: Capability-First PyCharm Dogfood Transition

Date prepared: 2026-07-24

Status: positive capability-first launch validated on 2026-07-26; network and
negative-authorization acceptance remain open because the dogfood image still
uses the ambient host-network workaround

Requirements: R-IDE-CONFIG-001, R-STATE-001, R-SCOPE-001, R-DOCKER-001,
R-FRAMEWORK-001

## Purpose

Validate the first transition from the established `run-image` dogfood command
to the committed `.devcapsule/` declaration, developer-owned checkout input,
generated local resolution, and `devcapsule run`.

This procedure adopts the existing directories in place. It does not copy,
move, or delete the old PyCharm state. The established `run-image` command
remains the fallback.

## Expected Environment

Run the preparation and launch commands on the host, outside the current
DevCapsule container. The expected host values are:

```bash
export MONOREPO_ROOT="${MONOREPO_ROOT:?Set this to the private host monorepo root}"
export HOST_PROJECT_ROOT="${HOST_PROJECT_ROOT:?Set this to the DevCapsule checkout}"
export PROJECT_STATE="${PROJECT_STATE:?Set this to the checkout's existing state directory}"
export PROJECT="$HOST_PROJECT_ROOT"
export LEGACY_STATE="$HOME/.config/docker-pycharm-codex/state"
export LEGACY_PLUGINS="$HOME/.config/docker-pycharm-codex/plugins"
export DEVCAPSULE="$PROJECT/devcapsule/dist/devcapsule.pex"
```

The repository build gate generated that PEX from the current source. Do not
use `/dist/devcapsule.pex` for this test unless it has separately been replaced
with the newly built artifact.

## 1. Preflight On The Host

Open a fresh host terminal and run:

```bash
set -u

test -d "$PROJECT/.devcapsule"
test -f "$PROJECT/.devcapsule/devcapsule.toml"
test -f "$PROJECT/.devcapsule/devcapsule.linux-amd64.lock"
test -f "$DEVCAPSULE"
test -d "$LEGACY_STATE/home"
test -d "$LEGACY_STATE/config"
test -d "$LEGACY_PLUGINS"
test -d "$PROJECT_STATE/system"
test -d "$PROJECT_STATE/log"
test -d "$PROJECT_STATE/home/.cache"
docker image inspect mycodespace.ai/pycharm:debug-v018 >/dev/null

python3.12 "$DEVCAPSULE" --help | sed -n '/Commands:/,$p'
```

Expected: every `test` and `docker image inspect` exits successfully. The help
output lists `init`, `lock`, `config`, `state`, and `run`.

If the host cannot execute the PEX directly, continue invoking it as
`python3.12 "$DEVCAPSULE"`. The examples below use a Bash array so the spelling
stays consistent:

```bash
DC=(python3.12 "$DEVCAPSULE")
```

## 2. Recreate `.devcapsule/` With `init` And `lock`

The WIP branch already contains the intended committed `.devcapsule/`
directory. Move it aside so this test exercises the bootstrap command that a
project uses before those generated project files are committed:

```bash
export COMMITTED_DEVCAPSULE="$PROJECT/.devcapsule.committed-wip-backup"
export GENERATED_DEVCAPSULE="$PROJECT/.devcapsule.generated-manual-test"

test ! -e "$COMMITTED_DEVCAPSULE"
test ! -e "$GENERATED_DEVCAPSULE"
mv "$PROJECT/.devcapsule" "$COMMITTED_DEVCAPSULE"
```

Do not run `git add`, `git commit`, or a destructive Git cleanup while the
tracked directory is parked under the backup name.

Initialize the existing checkout and generate its first dogfood lock:

```bash
"${DC[@]}" init "$PROJECT" \
  --name DevCapsule \
  --slug devcapsule \
  --creator https://github.com/ccozianu \
  --project-mount /workspace/301e4208ef81-ChatGPT_Codex \
  --need python \
  --need python-ide \
  --need docker-cli \
  --need gemini

"${DC[@]}" lock \
  --project "$PROJECT" \
  --image mycodespace.ai/pycharm:debug-v018
```

Expected: `init` creates `.devcapsule/devcapsule.toml`; `lock` creates the
current-platform `devcapsule.linux-amd64.lock`. Neither command modifies the
parked committed backup.

Inspect the generated inputs:

```bash
sed -n '1,200p' "$PROJECT/.devcapsule/devcapsule.toml"
sed -n '1,200p' "$PROJECT/.devcapsule/devcapsule.linux-amd64.lock"
```

Confirm before continuing:

- the capabilities are `docker-cli`, `gemini`, `python`, and `python-ide`;
- the container project mount is
  `/workspace/301e4208ef81-ChatGPT_Codex`;
- the lock selects `mycodespace.ai/pycharm:debug-v018`;
- neither generated file grants Docker-daemon or sudo access.

The parked WIP manifest contains an additional project-authored Docker
recommendation. `init` does not currently synthesize recommendations, and
their absence does not change the runtime result because committed
recommendations cannot grant host access.

Now verify create-only safety against the newly initialized project:

```bash
before=$(sha256sum "$PROJECT/.devcapsule/devcapsule.toml")
"${DC[@]}" init "$PROJECT" --creator https://github.com/ccozianu --need python
status=$?
after=$(sha256sum "$PROJECT/.devcapsule/devcapsule.toml")
printf 'init status: %s\nbefore: %s\nafter:  %s\n' "$status" "$before" "$after"
```

Expected: `init` exits with status 2, explains that the project is already
initialized, and the before/after hashes match.

## 3. Adopt Existing State In Place

Run each command from the host:

```bash
"${DC[@]}" state adopt home \
  --from "$LEGACY_STATE/home" --project "$PROJECT"
"${DC[@]}" state adopt pycharm/config \
  --from "$LEGACY_STATE/config" --project "$PROJECT"
"${DC[@]}" state adopt pycharm/plugins \
  --from "$LEGACY_PLUGINS" --project "$PROJECT"
"${DC[@]}" state adopt pycharm/system \
  --from "$PROJECT_STATE/system" --project "$PROJECT"
"${DC[@]}" state adopt pycharm/log \
  --from "$PROJECT_STATE/log" --project "$PROJECT"
"${DC[@]}" state adopt pycharm/cache \
  --from "$PROJECT_STATE/home/.cache" --project "$PROJECT"
```

Expected: each command reports `Adopted SLOT: PATH`. Existing directory
contents remain in place.

Locate and inspect the developer-owned checkout file:

```bash
find "$HOME/.config/devcapsule/projects" -name devcapsule.checkout.toml -print
CHECKOUT_FILE=$(find "$HOME/.config/devcapsule/projects" \
  -name devcapsule.checkout.toml -print -quit)
test -n "$CHECKOUT_FILE"
stat -c '%a %n' "$CHECKOUT_FILE"
sed -n '1,240p' "$CHECKOUT_FILE"
```

Expected:

- mode is `600`;
- `[checkout].path` is the canonical host checkout path;
- `[state.adopted]` contains exactly the six intended mappings;
- no tokens, passwords, or other credential values appear in the file;
- `[host]` is absent unless it was added previously by the developer.

## 4. Generate And Inspect Local Resolution

```bash
"${DC[@]}" config resolve --project "$PROJECT"

RESOLVED_FILE=$(find "$HOME/.config/devcapsule/projects" \
  -name devcapsule.resolved.toml -print -quit)
test -n "$RESOLVED_FILE"
stat -c '%a %n' "$RESOLVED_FILE"
sed -n '1,260p' "$RESOLVED_FILE"
```

Expected:

- resolution succeeds against `devcapsule.linux-amd64.lock`;
- mode is `600`;
- `[sources]` contains manifest, lock, and checkout digests;
- `[runtime]` selects `mycodespace.ai/pycharm:debug-v018`, `pycharm`, and the
  established `/workspace/301e4208ef81-ChatGPT_Codex` mount;
- the six adopted paths match the checkout input;
- the committed Docker recommendation has not turned into a `[host]`
  authorization.

## 5. Launch From Host Terminal A

Use the explicit run-once Docker and sudo authorizations:

```bash
"${DC[@]}" run \
  --project "$PROJECT" \
  --docker-daemon host-socket \
  --development-sudo \
  --name devcapsule-dogfood-v1
```

Expected initial console evidence:

- the storage summary names the six adopted host paths;
- the container project path is
  `/workspace/301e4208ef81-ChatGPT_Codex`;
- PyCharm opens and the command remains foreground-attached while the IDE is
  running.

Inside PyCharm, check:

1. The DevCapsule project opens at the established path.
2. Existing IDE settings and plugins are present.
3. Existing agent state under the adopted persistent home is available.
4. The project interpreter or virtual environment references are not broken by
   a changed project mount.
5. `docker version` works in the IDE terminal.
6. `sudo -n true && echo sudo-ok` prints `sudo-ok` in the IDE terminal.

Do not close PyCharm until the live-container inspection below is complete.

## 6. Inspect From Host Terminal B While PyCharm Is Open

```bash
docker inspect devcapsule-dogfood-v1 \
  --format 'network={{.HostConfig.NetworkMode}} autoremove={{.HostConfig.AutoRemove}} restart={{.HostConfig.RestartPolicy.Name}} user={{.Config.User}}'

docker inspect devcapsule-dogfood-v1 \
  --format '{{range .Mounts}}{{println .Source "->" .Destination}}{{end}}'

docker top devcapsule-dogfood-v1 -eo pid,ppid,user,args
```

Expected:

- `network=default` or `network=bridge`, never `network=host`;
- `autoremove=true` and no restart policy;
- project, home, config, plugins, system, log, cache, and Docker-socket mounts
  have the intended destinations;
- the container user remains unprivileged rather than root;
- PyCharm remains beneath the container's foreground lifecycle rather than
  being detached from it.

Also confirm the explicit permissions from inside the IDE terminal:

```bash
id
printf 'HOME=%s\n' "$HOME"
pwd
docker info --format '{{.ServerVersion}}'
sudo -n id
```

Expected: `HOME=/home/devcapsule`, the working directory is the established
project mount, Docker reaches the host daemon, and sudo succeeds only because
this launch explicitly requested it.

## 7. Lifecycle Check

Close PyCharm normally. Terminal A should return with the IDE/container exit
status. Then run on the host:

```bash
if docker container inspect devcapsule-dogfood-v1 >/dev/null 2>&1; then
  echo 'FAIL: container still exists'
else
  echo 'PASS: foreground exit removed the container'
fi
```

Expected: `PASS`.

Launch once more with the same command and verify that settings, plugins, and
agent state still persist. This second launch is the most useful check that the
new configuration records, rather than accidental first-run state, drive the
environment.

## 8. Negative Authorization Check

After the positive test, launch without Docker or sudo authorization:

```bash
"${DC[@]}" run \
  --project "$PROJECT" \
  --name devcapsule-dogfood-safe-default
```

While it is open, confirm in the IDE terminal:

```bash
if docker info >/dev/null 2>&1; then echo 'FAIL: ambient Docker access'; else echo 'PASS: Docker denied'; fi
if sudo -n true >/dev/null 2>&1; then echo 'FAIL: ambient sudo'; else echo 'PASS: sudo denied'; fi
```

Expected: both print `PASS`. Close PyCharm and confirm the container is
automatically removed.

## Failure Capture

If a launch fails, preserve these outputs before changing configuration:

```bash
"${DC[@]}" config resolve --project "$PROJECT"
sed -n '1,260p' "$CHECKOUT_FILE"
sed -n '1,260p' "$RESOLVED_FILE"
docker image inspect mycodespace.ai/pycharm:debug-v018 \
  --format '{{json .Config.Labels}}'
docker ps -a --no-trunc --filter name=devcapsule-dogfood
```

If the container still exists, also capture:

```bash
docker inspect CONTAINER_NAME
docker logs CONTAINER_NAME
```

Do not paste credential-bearing IDE files or the contents of the persistent
home into an issue or chat transcript.

## Rollback

The old state directories were only referenced, not modified structurally or
moved. To stop using the new local configuration, close the new container and
move the two generated records aside:

```bash
mkdir -p "$HOME/.config/devcapsule/manual-test-backup"
mv "$CHECKOUT_FILE" "$HOME/.config/devcapsule/manual-test-backup/"
mv "$RESOLVED_FILE" "$HOME/.config/devcapsule/manual-test-backup/"
```

Then use the previously validated `run-image` command. Do not delete any of the
legacy state directories.

Restore the tracked WIP declaration after either a successful test or a
rollback. Preserve the generated version temporarily for comparison:

```bash
test -d "$COMMITTED_DEVCAPSULE"
mv "$PROJECT/.devcapsule" "$GENERATED_DEVCAPSULE"
mv "$COMMITTED_DEVCAPSULE" "$PROJECT/.devcapsule"
git -C "$PROJECT" status --short
```

Expected: the tracked `.devcapsule/` files are restored and Git no longer
reports them deleted. The generated comparison directory is untracked and can
be removed after any useful comparison:

```bash
diff -ru "$PROJECT/.devcapsule" "$GENERATED_DEVCAPSULE" || true
rm -rf "$GENERATED_DEVCAPSULE"
```

If the developer-owned checkout record was retained after a successful test,
restoring the committed manifest changes its source digest relative to the
generated local resolution. Refresh that resolution before a later launch:

```bash
"${DC[@]}" config resolve --project "$PROJECT"
```

Skip that command after the rollback above moved the checkout record aside;
state must be adopted again before resolution in that case.

## Acceptance Record

Report these results back to the agent:

```text
Preflight and resolution: PASS / FAIL
Fresh `devcapsule init` and `lock`: PASS / FAIL
Create-only refusal preserves manifest: PASS / FAIL
PyCharm opens established project: PASS / FAIL
Existing settings/plugins/agent state: PASS / FAIL
Docker access with explicit option: PASS / FAIL
Development sudo with explicit option: PASS / FAIL
Default network is bridge, not host: PASS / FAIL
No ambient Docker/sudo without options: PASS / FAIL
Foreground exit and auto-remove: PASS / FAIL
Second-launch persistence: PASS / FAIL
Unexpected prompts or regressions:
Relevant non-secret output:
```

On success, this record can be converted into a completed-task validation note
and the README handoff can advance to immutable lock resolution and persistent
host-choice commands.
