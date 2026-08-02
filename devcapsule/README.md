# DevCapsule Python CLI

`devcapsule` is the Python command layer for the post-MVP refactor. It uses
Click for the public command tree and option parsing, with class-backed built-in
commands discovered from `devcapsule.commands`. The primary command shape is
configuration-first, for example `devcapsule pycharm run`. The `commands`
package is deliberately a thin CLI adapter; IDE-specific knowledge belongs in
configuration packages such as `devcapsule.configurations.pycharm`. The
PyCharm run path is being translated from the validated
`docker4pycharm/run-pycharm-container.sh` Bash launcher into maintainable Python
runtime planning and Docker invocation code.

Read [devcapsule/REQUIREMENTS.md](REQUIREMENTS.md) first for the subproject
requirement overview. The canonical detailed records for those requirements live
under `devcapsule/docs/requirements/`.

## User Setup

```bash
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ./devcapsule

python -m devcapsule --help
```

## Development Setup

Nox is the preferred developer cycle. By default this repository reuses Nox's
managed virtual environments between runs, so repeated commands avoid starting
from a completely fresh venv unless explicitly requested.

Run these commands from a Python environment where Nox is installed.

```bash
cd devcapsule

python -m nox -s tests   # Python compile checks plus pytest
python -m nox -s syntax  # Python compile checks plus shell syntax checks
python -m nox -s typecheck  # mypy for package, tests, and noxfile.py
python -m nox -s smoke   # source CLI and shell-wrapper help smoke tests
python -m nox -s pex     # build the PEX artifact and smoke-test it
python -m nox -s build   # full local gate
```

The `tests` session is the Nox way to run pytest for this project. It installs
the locked contributor dependencies into the managed Nox venv, installs
`devcapsule` editable with `--no-deps`, runs Python compile checks, then runs
`python -m pytest devcapsule`.

The `typecheck` session runs `mypy` across the `devcapsule` Python package,
tests, and `noxfile.py`.

The `build` session is the default Nox session, so these are equivalent:

```bash
cd devcapsule
python -m nox
python -m nox -s build
```

Run a clean-slate build when dependency or environment reuse could hide a
problem:

```bash
cd devcapsule
python -m nox --no-reuse-existing-virtualenvs -s build
```

If you want to discard all cached Nox environments before a clean build:

```bash
cd devcapsule
rm -rf .nox
python -m nox -s build
```

The manual virtualenv workflow is still supported when directly inspecting a
developer environment:

```bash
python3.12 -m venv .venv-dev
. .venv-dev/bin/activate
python -m pip install --upgrade pip
python -m pip install -r dev-requirements.txt
python -m pip install -e . --no-deps

python -m pytest devcapsule
```

The Nox build session installs the locked contributor dependencies, installs
`devcapsule` editable with `--no-deps`, compiles Python files, checks shell
script syntax, runs `mypy`, runs tests, smoke-tests the Python CLI and shell
wrapper help, builds the PEX artifact, and smoke-tests the PEX CLI.

`pyproject.toml` is the source of truth for Python runtime and development
dependencies. The pinned `requirements.txt` and `dev-requirements.txt` files
are reproducibility artifacts. Contributors should use the locked setup above;
the direct `python -m pip install -e "./devcapsule[dev]"` path remains useful
for quick local checks when exact dependency reproducibility is not needed.

Regenerate lock files after editing dependencies in `pyproject.toml`:

```bash
cd devcapsule
python -m piptools compile --strip-extras pyproject.toml --output-file requirements.txt
python -m piptools compile --strip-extras --extra dev pyproject.toml --output-file dev-requirements.txt
```

## End-User Artifact

Build a single-file PEX archive from a contributor environment:

```bash
cd devcapsule
scripts/build-pex.sh
```

For normal development, prefer the project build gate:

```bash
python -m nox -s pex
```

If the contributor environment is not activated, point the script at it:

```bash
PYTHON=/path/to/venv/bin/python devcapsule/scripts/build-pex.sh
```

Run the artifact with Python 3.12+:

```bash
python3.12 devcapsule/dist/devcapsule.pex --help
python3.12 devcapsule/dist/devcapsule.pex pycharm run --help
python3.12 devcapsule/dist/devcapsule.pex pycharm build --help
```

The archive contains the Python CLI, runtime dependencies, and the legacy
PyCharm build/runtime helper assets still needed by the current delegated
`pycharm build`, `pycharm check-runtime`, and `bootstrap project` commands.

The PEX build embeds `/tmp/devcapsule-pex-root` as its default runtime
extraction/cache root so it does not depend on IDE project-state cache
directories being writable. If the launch environment explicitly sets
`PEX_ROOT`, that value still controls PEX before DevCapsule starts; point it
at a writable directory or unset it if PEX warns about an unwritable cache.

## Commands

### Managed local images

List only V1 DevCapsule-managed images from the local Docker image store:

```bash
devcapsule images list
devcapsule images list --include-legacy
```

The default view requires the managed-image metadata labels and does not infer
ownership from a repository or tag prefix. `--include-legacy` also shows older
images carrying the transitional `devcapsule.configuration` label. Listing is
read-only and performs no registry access.

Build the JetBrains-free DevCapsule base:

```bash
# From a source/editable installation, identify the PEX to embed.
devcapsule images build \
  --type base \
  --tag devcapsule-base:debug-v019 \
  --pex dist/devcapsule.pex \
  --source-revision "$(git rev-parse HEAD)" \
  --network host

# When invoked from a PEX, that PEX is embedded by default.
python3.12 dist/devcapsule.pex images build \
  --type base \
  --tag devcapsule-base:debug-v019 \
  --source-revision "$(git rev-parse HEAD)"

# WIP: build the NVIDIA CUDA development variant for specialized validation.
python3.12 dist/devcapsule.pex images build \
  --type base \
  --recipe nvidia-cuda-devel \
  --tag devcapsule-base:cuda-v019 \
  --source-revision "$(git rev-parse HEAD)"
```

`--recipe` accepts `ubuntu-24.04` or `nvidia-cuda-devel`. The default
`ubuntu-24.04` recipe uses `ubuntu:24.04` and installs the established
DevCapsule developer utilities. The WIP `nvidia-cuda-devel` recipe uses
`nvidia/cuda:12.8.1-devel-ubuntu24.04` and installs the same utilities on top
of the CUDA compiler/runtime development baseline. It emits a WIP warning and
remains blocked for V1 release until the specialized NVIDIA host E2E task is
complete.

#### What is in the base, and where to audit it

TL;DR: the default base starts from Ubuntu 24.04 and adds a broad Python and
native-development workstation baseline. It contains Python 3.12 and headers,
Git and OpenSSH, GCC/G++ plus Make/CMake/pkg-config, GDB/LLDB/strace, common
shell/process/filesystem/network diagnostics, Docker CLI/buildx/Compose and
daemon binaries, X11/GTK/audio/font/Mesa runtime libraries, `tini`, `gosu`, and
the `sudo` binary. It also installs the pinned language-tooling baseline—Node.js
`v22.23.1` and its bundled npm—and embeds the selected
DevCapsule PEX at `/opt/devcapsule/bin/devcapsule.pex`.

The repository-owned Python build plan is the inspectable source of truth:

- [`devcapsule/base_image.py`](devcapsule/base_image.py) defines the curated
  `ubuntu-24.04` and WIP `nvidia-cuda-devel` recipes, root images, managed-image
  labels, embedded PEX, and generic entrypoint/CMD.
- [`devcapsule/configurations/pycharm/_image_build.py`](devcapsule/configurations/pycharm/_image_build.py)
  currently owns `BASE_APT_PACKAGES`, the exact Ubuntu package list shared by
  the Python-owned base planner. Despite that transitional module location,
  the base remains JetBrains-free.
- [`devcapsule/image_tooling.py`](devcapsule/image_tooling.py) pins and verifies
  the Node.js/npm runtime.
- [`devcapsule/image_build.py`](devcapsule/image_build.py) shows how those
  components become the generated Dockerfile/build context and are executed
  through Docker buildx.
- [`devcapsule/container_runtime/`](devcapsule/container_runtime/) is the
  generic runtime embedded in the PEX and invoked when a completed environment
  is launched.

The base does **not** contain an IDE or vendor archive, project source,
developer state, credentials, host mounts, host authorization, license/EULA
acceptance, or an ambient AI-agent CLI. Installing Docker and `sudo` binaries
grants no Docker-daemon or sudo access. Materialization adds the
checksum-verified IDE/component; the
developer-owned runtime resolution separately controls project/state mounts,
networking, devices, Docker access, privilege, and secrets.

`--from IMAGE` overrides the selected recipe's root image. The builder reuses
that root image when it is already local and otherwise allows Docker to obtain
the reference.
`--network` accepts `default`, `host`, or `none` and is forwarded to Docker
buildx. Host mode is an explicit build-time isolation relaxation and adds the
BuildKit `network.host` entitlement; it does not configure the network of later
runtime containers.
The resulting image carries the V1 managed marker, metadata version, base kind,
canonical name, recipe name/status/version, PEX digest, and source revision
labels. `images build --type base` is the sole supported base-build command;
there is no compatibility `build-base` alias.

Build the lock-selected local environment after creating a fresh checkout
resolution:

```bash
devcapsule project --path /path/to/checkout config resolve
devcapsule images build \
  --type environment \
  --project /path/to/checkout \
  --alias devcapsule-local-pycharm:debug-v019
```

The platform lock must select a DevCapsule base plus a
`local-materialization` PyCharm component with an exact version, variant,
download URL, SHA-256, and supported materialization recipe. A locked base
must use a digest-pinned reference or record its expected immutable local image
ID. `--base IMAGE` is an explicit development override; it never rewrites the
lock or resolution.

This repository's current Linux dogfood lock uses published digest
`docker.io/mycodespaceai/devcapsule-base@sha256:637f646a9de962cb399025c2bf3817b08e242d2a4416b49a202cf06763852feb`.
The associated `ubuntu-24.04-v019` tag is only a dogfood discovery tag;
official V1 artifacts will use semantic release versions and committed locks
will continue to use immutable digests.

That immutable v019 image predates agent-neutral base recipe version 2 and
still contains Gemini CLI. It remains usable only as the already-validated
dogfood bridge. A newly built and published recipe-v2 base must replace the
committed digest before the dogfood lock and V1 release candidate satisfy the
current no-ambient-agent contract.

The command obtains the selected base when it is not local, verifies that it
is a managed metadata-v1 base for the locked platform, and downloads the
locked JetBrains archive into `$XDG_CACHE_HOME/devcapsule` (normally
`~/.cache/devcapsule`). Artifact acquisition and formation are protected by
per-identity locks. The archive is checksum-verified and unpacked only into a
temporary build context.

The canonical output name is
`devcapsule-local-pycharm:<formation-identity-prefix>`. Existing canonical
images are reused only after their stored canonical descriptor, full digest,
base identity, recipe, and component metadata all match. A conflicting tag
fails with cleanup guidance instead of being overwritten. `--alias` adds an
extra local debugging tag without changing the formation identity.

Environment images contain the generic PyCharm component template, but no
project source, checkout state, credentials, host authorization, or
checkout-specific runtime plan. This command never launches a container.
The template declares that PyCharm uses the persistent home and home-relative
XDG roots, and owns its exceptional config, plugins, system, log, and cache
slots with their lifecycle and storage semantics. Components that keep state
entirely under standard `HOME`/XDG locations declare no custom slots; shared
runtime planning contains no agent- or IDE-named state field.
Automatic materialization and external runtime-plan delivery from `project
run` remain the next integration slice; use `project run-image` only for
deliberate interim inspection of a locally built checkpoint.

### Capability-first dogfood path

The first capability-first slice supports a locally built PyCharm image. New
projects can create a declaration and current-platform dogfood lock with:

```bash
devcapsule project --path . init --creator https://github.com/example \
  --need python --need python-ide --need docker-cli
devcapsule project lock --image mycodespace.ai/pycharm:debug-v018
```

`project init` is create-only and leaves an existing `.devcapsule/` untouched.
Adopt the six existing dogfood state directories once, then generate the local
developer-owned resolution:

```bash
devcapsule project state adopt home --from ~/.config/docker-pycharm-codex/state/home
devcapsule project state adopt pycharm/config --from ~/.config/docker-pycharm-codex/state/config
devcapsule project state adopt pycharm/plugins --from ~/.config/docker-pycharm-codex/plugins
devcapsule project state adopt pycharm/system --from /path/to/project-state/system
devcapsule project state adopt pycharm/log --from /path/to/project-state/log
devcapsule project state adopt pycharm/cache --from /path/to/project-state/home/.cache
devcapsule project config resolve
```

Normal launch then uses the committed manifest and platform lock plus that
checkout-local resolution:

```bash
devcapsule project run --docker-daemon host-socket --development-sudo
```

Those two host relaxations are run-once choices and are not granted by the
committed Docker recommendation. They can be recorded manually in the
developer-owned checkout file's `[host]` table for this initial slice. The
PyCharm runtime now uses Docker bridge networking unless an expert path adds a
different explicit Docker choice.

This is intentionally a dogfood bridge, not the complete V1 resolver: `lock`
currently pins a local image tag supplied with `--image`; immutable image
digest resolution and general curated capability selection remain follow-up
work.

Registered checkout records can be listed without scanning source trees:

```bash
devcapsule project list
```

Use `devcapsule project --path /path/to/checkout SUBCOMMAND` when operating
outside a checkout. Otherwise project commands discover the nearest
`.devcapsule/devcapsule.toml` upward from the current directory.

DevCapsule uses a configuration-first command model:

```text
devcapsule CONFIGURATION ACTION [options]
```

`CONFIGURATION` names an IDE-plus-agent environment. `pycharm` and
`codium_with_claude` are implemented configurations. The active public-default
image builds bundle pinned Node.js/npm but no ambient AI-agent CLI.
`codium_with_claude` remains a transitional proof-point name and is distinct
from the registered,
unimplemented `vscode_with_claude` placeholder.

End users should be able to:

- discover available configurations with `devcapsule --help`;
- build or update a configuration image when that configuration supports
  `build`;
- run a configuration against a selected project with `run`;
- pass configuration-specific options without exposing unrelated host state;
- use the same command shape from source installs and from the PEX artifact.

```bash
python -m devcapsule --help
devcapsule pycharm run --project /path/to/project
devcapsule pycharm run
devcapsule pycharm run --project /path/to/project --config-mode project
devcapsule pycharm run --profile codex --project-state-root /path/to/workspace/.state
devcapsule project --path /path/to/project run-image pycharm-isolated:latest
devcapsule pycharm build --pycharm /path/to/pycharm.tar.gz
devcapsule pycharm check-runtime
devcapsule vscode_with_claude --help
devcapsule codium_with_claude build
devcapsule codium_with_claude build --ide-archive /path/to/VSCodium-linux-x64.tar.gz
devcapsule codium_with_claude run --project /path/to/project
devcapsule codium_with_claude run --project /path/to/project --profile codex
devcapsule codium_with_claude run --project /path/to/project --project-state-root /path/to/workspace/.state
devcapsule codium_with_claude run --project /path/to/project --project-mount /workspace/project
devcapsule codium_with_claude run --project /path/to/project --debug-shell
devcapsule codium_with_claude run --project /path/to/project --network host
devcapsule bootstrap project --project /path/to/project
```

`pycharm build` and `codium_with_claude build` use Ubuntu 24.04 and install
Python plus a pinned Node.js archive under `/opt/node/node-{version}`, expose
that runtime through `/opt/node/current` and `/usr/local/bin`. The Codium image also installs
VSCodium plus `xterm` for basic X11 validation and `strace` for process-level
diagnostics. Update the pinned versions in source when intentionally advancing
the public-default tooling baseline. Use
`--image`, `--base-image`,
`--network`, and repeatable `--extra-apt-package` options to customize a build.
Pass `--ide-archive PATH` to install VSCodium from a local `.tar.gz` (or other
tar format recognized by Python) containing an executable `bin/codium`. In
that mode the build does not configure or contact the VSCodium apt repository;
the archive is installed under `/opt/codium`. The pinned Node.js archive and
checksum file are still fetched during the image build from their configured
upstream source.

`codium_with_claude run` currently targets Linux X11. It mounts the selected
project at `/workspace/project` by default, a persistent VSCodium/Claude home
(by default `~/.config/devcapsule/codium-with-claude`) at
`/ide-global-settings`, a project-local state directory (by default
`.devcapsule/codium-state`) at `/ide-project-state`, and the host X11 socket
read-only. `--profile NAME` moves the shared global state under
`~/.config/devcapsule-codium-with-claude-NAME/state`. `--project-state-root
DIR` mirrors per-project state outside the source tree, and `--project-mount`
overrides the in-container project path explicitly. It passes `DISPLAY` and
uses ordinary Docker bridge networking so VSCodium and Claude Code can reach
their services. It does not mount the Docker socket, SSH agent, host home,
devices, or other credentials by default. Claude authentication written under
its container home persists in the explicit global state directory. No
agent-specific host credential/state directory is mounted automatically.
Use `--debug-shell` to run interactive Bash through the normal image
entrypoint with the same project, state, and X11 mounts instead of starting
VSCodium.
Use `--network MODE` to select an explicit Docker network mode for either the
normal IDE or `--debug-shell` path. The default remains Docker bridge
networking. `--network host` is useful for host-bound development services and
debugging, but shares the host network namespace and therefore weakens network
isolation.
Normal launches execute VSCodium's Electron binary directly so it remains the
foreground container process. They do not use the `bin/codium` CLI wrapper,
which detaches the GUI and exits before the IDE session ends.

The local-archive build path restores root ownership and mode `4755` on
VSCodium's Chromium sandbox helper after safe archive extraction strips the
setuid bit. This path and foreground launching were manually validated on
2026-07-13. Do not adopt `--no-sandbox` as a normal workaround. The evidence
and validation record are documented in
`implementation-notes/completed-tasks/2026-07-13-vscodium-sandbox-and-foreground-launch.md`.

Known parity gap: `codium_with_claude run` now shares `--profile`,
`--project-state-root`, and `--project-mount` with the common runtime-layout
model, but it still lacks many of the Git credential, Docker capability,
debugging, sudo, and additional filesystem options available from
`pycharm run`. The intended shared versus IDE-specific behavior is tracked in
`implementation-notes/bugs/2026-07-13-codium-run-option-parity.md`.

`pycharm run` defaults `--project` to the current directory. Its default
persistent home is checkout-scoped beneath `$XDG_DATA_HOME/devcapsule/` and is
mounted at `/home/devcapsule`; standard IDE, agent, and shell state beneath
`HOME` naturally persists there. `--home DIR` or `DEVCAPSULE_HOME_DIR`
selects a developer-owned alternative. The developer's actual host home is
never mounted as the container home.

PyCharm config and plugins are durable component state. PyCharm system data and
tool caches use `$XDG_CACHE_HOME/devcapsule/`, while logs use
`$XDG_STATE_HOME/devcapsule/`. For the current dogfood migration, existing
`--global-settings`, `--plugins`, and `--project-state` values are adopted in
place: their `home`, `config`, `plugins`, `system`, `log`, and `home/.cache`
subdirectories are mounted independently at the new container destinations.

`run-image IMAGE` is the expert, lock-independent PyCharm-compatible image path
for construction and diagnosis. It passes `--pull=never` to Docker, so a
missing local image fails instead of pulling or resolving another image. It
defaults to no Docker-daemon access. Use
`--docker-daemon host-socket` and `--development-sudo` only as explicit
run-once relaxations. The broader capability-first state-management CLI remains
under development.

The first dogfood validation intentionally supplies the existing directories
once, before the planned `state adopt` command persists those mappings:

```bash
./dist/devcapsule.pex project --path "$HOST_PROJECT_ROOT" \
  run-image mycodespace.ai/pycharm:debug-v018 \
  --global-settings ~/.config/docker-pycharm-codex/state/ \
  --plugins ~/.config/docker-pycharm-codex/plugins \
  --project-mount /workspace/301e4208ef81-ChatGPT_Codex \
  --project-state "$PROJECT_STATE" \
  --docker-daemon host-socket \
  --development-sudo
```

The explicit project mount preserves the absolute path already stored in the
adopted PyCharm workspace and interpreter configuration. Omitting it during
this migration makes saved paths such as
`/workspace/301e4208ef81-ChatGPT_Codex/.venv/bin/python` appear missing.

Unsupported command shapes such as top-level `devcapsule run`,
`devcapsule run-image`, `devcapsule config`, `devcapsule state`, and
`devcapsule lock`, as well as `devcapsule build pycharm` and
`devcapsule bootstrap-project`, are intentionally not part of the Python CLI.
