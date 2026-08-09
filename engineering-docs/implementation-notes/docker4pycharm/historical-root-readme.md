# DockerForIDEIsolation

Historical note: this file is the former repository-root README preserved under
`docker4pycharm/` for PyCharm prototype context. It contains old implementation
details and handoff history. For current project-wide guidance, read
`../README.md`; for active Python framework usage, read `../docker4ides/README.md`.

This repository is a continuation point for the Docker/PyCharm isolation work bootstrapped from a ChatGPT design session. It is intended to be read by both a human developer and a future AI development agent working inside a containerized IDE.

The long-term goal is to create a line of reproducible, batteries-included development environments that combine:

1. Best-of-breed IDEs for the target development domain.
2. Best-of-breed AI assistants and coding agents.
3. Reproducibility, portability, and isolation.

The user experience target is a fast, low-friction human-to-agent loop. A user should not need extensive local setup before working, and the AI agent should have enough tools and environmental completeness to make meaningful progress without stopping every few minutes for permission or missing dependency setup. At the same time, the environment should constrain host exposure so a capable AI agent can operate aggressively inside the development environment without casually reaching into unrelated host state.

This project is also an experiment in documenting a practical human/AI development workflow. The repository should become the durable knowledge base for the project: important decisions, current state, handoffs, and next steps should be persisted in project files. Human attention should be reserved for direction, intuition, product judgment, and creativity. Agent/model pairs should be given narrow, well-documented targets so context stays small and the quality of the AI work stays high.

## Current Repository Shape

This repository now has two deliberately different subprojects:

- `docker4ides/` is the active Python CLI and framework. New code development
  should happen here. The current public command model is configuration-first:
  `docker4ides CONFIGURATION ACTION [options]`, for example
  `docker4ides pycharm run ...`.
- `docker4pycharm/` is the historical PyCharm shell implementation and
  reference baseline. It records the original working Docker/X11 PyCharm MVP
  and remains useful for comparison and operational notes, but it is not the
  place for new framework development.

The rest of this root README intentionally preserves the historical PyCharm
prototype rationale because that prototype is the source of many accepted
requirements. When deciding where to implement new behavior, use `docker4ides/`
unless the task is explicitly to maintain or compare against the old
`docker4pycharm/` reference.

## Historical PyCharm Prototype Summary

The user requested a Docker environment whose main goal is to run PyCharm in isolation without degrading the expected IDE experience. The environment should allow future installation of AI-related PyCharm plugins, including ChatGPT/Codex and possibly Claude-related tooling in later revisions. The environment is expected to run from a normal Linux developer workstation under X11, launched from `xterm` or a similar terminal. The assumed host baseline is a common Linux distribution newer than Ubuntu 22.04, with systemd newer than 249.x if systemd functionality is ever needed.

The key requirements were:

- Run PyCharm isolated in Docker, but preserve normal IDE features as much as practical.
- Start the environment with a simple command, either `docker start ...` or a suitably parameterized Bash/Python launcher.
- Keep PyCharm configuration and plugins outside the Docker image so user settings and installed plugins persist across runs.
- Map one project directory into the container and launch PyCharm directly against that project.
- Do not mount arbitrary host directories into the container. Other than the project directory, the IDE state directory, and the plugins directory, avoid exposing host directories to PyCharm.
- Include the usual Linux development/debugging tools inside the image: `ssh`, `git`, `netcat`, `nslookup`, `strace`, and other bread-and-butter development utilities.
- Support GitHub fetch/push workflows without baking credentials into the image. The first revision supports SSH agent forwarding and an optional HTTPS token mounted as a temporary secret file.
- Accept PyCharm either as a `.tar.gz` distribution or as an already-unpacked folder supplied to the image build script.

The first implementation generated the following files, which live under the
historical/reference `docker4pycharm/` subproject:

```text
docker4pycharm/
  Dockerfile
  build-image.sh
  run-pycharm-container.sh
  entrypoint.sh
  README.md
```

This root `README.md` is intentionally broader than `docker4pycharm/README.md`.
It records design rationale and project continuation notes so a future
development agent does not lose context. Current user-facing Python framework
usage belongs in `docker4ides/README.md`.

## Important design decision: `docker run` wrapper instead of pure `docker start`

The user mentioned `docker start ...` as an acceptable target. The first implementation uses a launcher script around `docker run` instead.

Reason: project path, X11 authorization file, SSH agent socket, optional GitHub token, user/group mapping, and temporary runtime files are all per-invocation inputs. These are naturally container-creation options, not restart options. A pre-created container started with `docker start` would make these inputs awkward or stale.

The wrapper still gives the user a stable start command:

```bash
./docker4pycharm/run-pycharm-container.sh --project /path/to/project --ssh-agent
```

A future revision may add a convenience top-level command such as `./run-ide pycharm --project ...`, but it should preserve the per-run mount and credential model.

## Current architecture

### Image

The image is built from `ubuntu:24.04`. The supplied PyCharm distribution is normalized into the Docker build context as `pycharm/` and copied into:

```text
/opt/pycharm
```

The image symlinks PyCharm to:

```text
/usr/local/bin/pycharm
```

The default entrypoint is:

```text
/usr/bin/tini -- /usr/local/bin/entrypoint.sh
```

### Runtime mounts

The launcher mounts only the required host resources by default:

```text
/workspace/<project-id> -> selected host project directory, read/write
/ide-global-settings    -> shared IDE-local home and default config root, read/write
/ide-config             -> selected PyCharm idea.config.path, read/write
/ide-project-state      -> per-project PyCharm caches/logs/workspace state, read/write
/ide-plugins            -> persistent PyCharm plugins root, read/write
/tmp/.X11-unix          -> host X11 socket directory, read-only
/tmp/.docker.xauth      -> temporary generated Xauthority file, read-only
/etc/passwd             -> temporary generated passwd file, read-only
/etc/group              -> temporary generated group file, read-only
/run/host-docker.sock   -> host Docker daemon socket, default Docker mode
```

Optional mounts:

```text
/run/host-ssh-agent.sock      -> host SSH agent socket, only with --ssh-agent
/run/secrets/git-token        -> temporary HTTPS Git token file, only with --git-token-file or --git-token-env
```

The default persistent host locations are:

```text
~/.local/share/pycharm-docker/state
~/.local/share/pycharm-docker/state/config
~/.local/share/pycharm-docker/project-state/<project-id>
~/.local/share/pycharm-docker/plugins
```

These can be overridden with:

```bash
--global-settings /some/shared/settings/dir
--ide-config /some/config/dir
--project-state /some/per-project/state/dir
--plugins /some/plugins/dir
```

`--state` remains as a legacy alias for `--global-settings`.
`--project-config` stores JetBrains config under the per-project state root
instead of the shared global settings root, which is the preferred mode for
running two different projects concurrently.

### PyCharm state redirection

The container entrypoint creates an `idea.properties` file at runtime and sets `PYCHARM_PROPERTIES` so PyCharm uses externalized state paths:

```properties
idea.config.path=/ide-config
idea.system.path=/ide-project-state/system
idea.plugins.path=/ide-plugins
idea.log.path=/ide-project-state/log
```

The container also sets:

```text
HOME=/ide-global-settings/home
XDG_CONFIG_HOME=/ide-global-settings/home/.config
XDG_CACHE_HOME=/ide-project-state/home/.cache
XDG_DATA_HOME=/ide-global-settings/home/.local/share
```

This gives PyCharm, Git, SSH, shell tools, and plugins a writable home-like
location without mounting the host home directory. Shared IDE-local home state
persists across projects, while caches, logs, and volatile project workspace
state are namespaced per host project by default. JetBrains config defaults to
the shared global settings root for continuity, but `--project-config` moves it
under per-project state to avoid JetBrains config-directory locks when running
multiple projects concurrently.

### PyCharm launch behavior

PyCharm is launched with the selected project mounted at a stable per-project
container path and that path passed as the command-line argument:

```bash
/opt/pycharm/bin/pycharm.sh /workspace/<project-id>
```

This avoids making different host projects all look like the same `/project`
directory to JetBrains project/recent-workspace state. The mount path can be
overridden with `--project-mount`, but the default should be preferred unless a
specific integration requires a fixed container path.

### GUI model

Revision 0 uses X11 forwarding through the host X socket:

```text
/tmp/.X11-unix
```

The launcher creates a temporary Xauthority file using `xauth nlist` and `xauth nmerge`, then mounts it into the container as `/tmp/.docker.xauth`.

If PyCharm cannot connect to the display because no Xauthority cookie was copied, the wrapper warns that the user may need to allow the local user explicitly, for example:

```bash
xhost +SI:localuser:$(id -un)
```

This is a pragmatic development-workstation choice, not a perfect GUI security boundary. Future revisions may evaluate `xpra`, VNC, Waypipe, a nested X server, or a dedicated untrusted X session.

### Security posture

The default launcher profile now uses Docker-outside-of-Docker for developer
convenience: it mounts the host Docker daemon socket into the IDE container at
`/run/host-docker.sock` and sets `DOCKER_HOST=unix:///run/host-docker.sock`.
The container still runs PyCharm as the mapped non-root user, keeps the
read-only root filesystem, drops capabilities, and sets
`no-new-privileges`, but the Docker socket is a major security exception. Any
tool inside PyCharm/Codex that can run Docker commands can control host Docker
images, containers, networks, and bind mounts.

The image includes `sudo` for development work, but sudo elevation is not
enabled in the default profile because `no-new-privileges`, dropped
capabilities, and a read-only root filesystem intentionally prevent setuid
privilege escalation. Use `--dev-sudo` or `--sudo` when the IDE-side user needs
passwordless sudo for package installs or similar container-local development
tasks. That mode is explicit, prints a warning, implies `--writable-root`, and
keeps the default Docker container capabilities in host-Docker and no-Docker
modes.

The strict launcher profile, available with `--no-docker`, keeps the original
constrained posture and does not mount any Docker socket:

- `--read-only` root filesystem by default.
- Writable `tmpfs` mounts for `/tmp`, `/run`, and `/var/tmp`.
- `--cap-drop ALL` by default.
- `--security-opt no-new-privileges`.
- Private IPC namespace.
- PID limit.
- No host `$HOME` mount.
- No host `~/.ssh` mount.
- No system package-cache or language-environment mounts from the host.
- No Docker daemon access.

The project directory is mounted read/write because normal IDE operation
requires editing project files. Shared PyCharm settings and IDE-local home files
are stored under `/ide-global-settings`, project-specific caches and logs are
stored under `/ide-project-state`, and plugins are stored under `/ide-plugins`.

For isolated Docker state, the launcher also supports explicit true
Docker-in-Docker:

```bash
./docker4pycharm/run-pycharm-container.sh \
  --project /repo \
  --docker-in-docker
```

This starts the outer IDE container with `--privileged`, a writable root
filesystem, and an inner `dockerd`. When this mode is active, the launcher
prints a large stderr warning. Because the outer PyCharm container uses host
networking, the inner daemon is started without bridge/iptables management; use
`--network host` for inner Docker builds that need network access.

### Native-debugging exception

Native debugging and some `strace` workflows require extra privileges. The launcher supports:

```bash
./docker4pycharm/run-pycharm-container.sh --project /repo --debug-native
```

This adds:

```text
--cap-add SYS_PTRACE
--security-opt seccomp=unconfined
```

Use this only when needed for native debugging, non-child process tracing, or similar development work.

### Git identity and credential model

The launcher avoids mounting host `~/.gitconfig`, host `~/.ssh`, or host
credential directories. Git author identity can be passed explicitly:

```bash
./docker4pycharm/run-pycharm-container.sh \
  --project /repo \
  --git-user-name "Your Name" \
  --git-user-email you@example.com
```

Or the launcher can read only the host's global `user.name` and `user.email`
values and pass those into the container:

```bash
./docker4pycharm/run-pycharm-container.sh \
  --project /repo \
  --git-identity-from-host
```

By default, the launcher now tries to read only the host global Git
`user.name` and `user.email` strings and pass them into the isolated IDE home.
This avoids accidental commits with the auto-generated container identity
without mounting host `~/.gitconfig`. Use `--no-git-identity-from-host` to
disable that automatic lookup for a session, or pass `--git-user-name` and
`--git-user-email` to set explicit values.

When identity values are supplied or auto-detected, the entrypoint writes them
to the isolated IDE home Git config under
`/ide-global-settings/home/.gitconfig`.

Preferred SSH workflow:

```bash
ssh-add -l
./docker4pycharm/run-pycharm-container.sh --project /repo --ssh-agent
```

The container gets only the forwarded SSH agent socket. SSH known-hosts are
stored in `/ide-global-settings/home/.ssh/known_hosts`, not on the host home
directory.

Optional HTTPS token workflow:

```bash
export GITHUB_TOKEN=ghp_...
./docker4pycharm/run-pycharm-container.sh \
  --project /repo \
  --git-token-env GITHUB_TOKEN
```

The wrapper writes the environment variable value to a temporary file, mounts
that file read-only at `/run/secrets/git-token`, and configures `GIT_ASKPASS`
inside the container. This avoids persisting the token in the Docker image and
avoids placing it directly in a long-lived Docker environment variable. The
askpass helper only releases the token for the configured host list, which
defaults to `github.com`.

A token file can also be supplied directly:

```bash
./docker4pycharm/run-pycharm-container.sh \
  --project /repo \
  --git-token-file /path/to/token-file
```

The legacy `--github-token-env`, `--github-token-file`, and `--github-user`
flags remain as aliases for the Git token options.

## Installed tool baseline

Revision 0 installs common development and debugging utilities including:

```text
ca-certificates curl wget git openssh-client gnupg2 xauth
build-essential make cmake pkg-config gcc g++ gdb lldb
python3 python-is-python3 python3-pip python3-venv python3-dev
netcat-openbsd dnsutils iproute2 iputils-ping traceroute
procps psmisc lsof strace tcpdump socat telnet whois file
jq ripgrep fd-find fzf shellcheck tree less vim-tiny nano sudo
libpq5 libpq-dev
tini
docker.io docker-buildx docker-compose-v2 gosu
```

It also installs X11/GTK/font libraries needed by JetBrains IDEs:

```text
libx11-6 libxext6 libxrender1 libxtst6 libxi6 libxrandr2 libxss1 libxkbfile1
libgtk-3-0 libnss3 libnspr4 libasound2t64 libfontconfig1 libfreetype6
libdbus-1-3 xdg-utils fonts-dejavu fonts-liberation
libgl1 libglx-mesa0 libgl1-mesa-dri mesa-utils
```

Because the default isolation model does not mount host `/dev/dri` render
devices, the launcher and entrypoint default Mesa to software GL with
`LIBGL_ALWAYS_SOFTWARE=1`, `MESA_LOADER_DRIVER_OVERRIDE=llvmpipe`, and
`LIBGL_DRI3_DISABLE=1`. This avoids the noisy hardware-DRI probe path that logs
`Failed to query drm device`, `failed to create dri3 screen`, and
`failed to load driver: iris` while preserving the no-extra-device-mount
posture.

## Build and run quickstart

From the repository root:

```bash
cd docker4pycharm

./build-image.sh \
  --pycharm /path/to/pycharm-professional-or-community.tar.gz
```

Or with an unpacked PyCharm directory:

```bash
cd docker4pycharm

./build-image.sh \
  --pycharm /path/to/unpacked/pycharm
```

Run PyCharm on a project:

```bash
./docker4pycharm/run-pycharm-container.sh \
  --project /path/to/project \
  --ssh-agent \
  --git-identity-from-host
```

By default, Docker commands inside PyCharm/Codex connect to the host Docker
daemon through the host Docker socket. To launch with a separate inner Docker
daemon instead:

```bash
./docker4pycharm/run-pycharm-container.sh \
  --project /path/to/project \
  --ssh-agent \
  --git-identity-from-host \
  --docker-in-docker
```

To launch a higher-isolation session without Docker access:

```bash
./docker4pycharm/run-pycharm-container.sh \
  --project /path/to/project \
  --ssh-agent \
  --git-identity-from-host \
  --no-docker
```

Use a custom image name:

```bash
./docker4pycharm/build-image.sh \
  --pycharm /path/to/pycharm.tar.gz \
  --image docker4pycharm:dev

./docker4pycharm/run-pycharm-container.sh \
  --image docker4pycharm:dev \
  --project /path/to/project \
  --ssh-agent \
  --git-identity-from-host
```

## AI plugin direction

The near-term ChatGPT/Codex integration path for PyCharm is documented
separately in `docs/guides/docker4pycharm-ai-plugin-and-chatgpt-setup.md`.

As of the documentation checked on 2026-06-18, the recommended path is:

1. Use PyCharm/JetBrains IDE version 2025.3 or newer for Codex in JetBrains AI Chat.
2. Install or update the JetBrains AI Assistant plugin.
3. Open the JetBrains AI Chat/widget.
4. Authenticate using the user’s ChatGPT account.
5. Select Codex from the agent picker in AI Chat.

This is preferable to installing a random third-party “ChatGPT” plugin, because the JetBrains/OpenAI-supported path integrates Codex into JetBrains AI Chat and supports ChatGPT account sign-in.

Potential container-specific issue: account login flows may open a browser or localhost callback. Because PyCharm is running inside Docker, the login flow should be tested early. If browser handoff fails, likely mitigation paths include:

- Use the “copy URL” or manual sign-in option if the plugin offers one.
- Temporarily pass through a host browser via `xdg-open` bridging in a future launcher revision.
- Use an OpenAI API key or JetBrains AI subscription authentication path if ChatGPT-account OAuth proves awkward inside the container.
- Consider a launcher option for host networking only during sign-in, if strictly necessary and documented.

Do not add such relaxations silently. Treat them as explicit, auditable options.

## Future development backlog

Suggested next work items:

1. Continue active framework development in `docker4ides/`, using
   `docker4pycharm/` only as the historical PyCharm reference baseline and
   operational comparison target.
2. Consider a top-level wrapper only if it clarifies active `docker4ides`
   usage without adding a second command model.
3. Add automated shell linting and smoke tests for the launcher scripts.
4. Add a minimal X11 smoke test command such as `xeyes` or `xclock` in a diagnostic mode, if an appropriate package is installed.
5. Add a `--project-readonly` mode for code review or browsing use cases.
6. Add a `--network none` mode for high-isolation sessions, plus documented exceptions for Git/AI plugin workflows.
7. Add a separate `--login-relaxed` or similar mode only if AI plugin OAuth requires additional browser/network handling.
8. Consider rootless Docker or Podman compatibility.
9. Consider Wayland-native and `xpra`/VNC alternatives to direct X11 socket sharing.
10. Add a per-IDE settings profile mechanism so a user can maintain a global
    PyCharm/Python preference set and use it to seed the initial config for a
    new containerized PyCharm project without sharing the same live
    lock-bearing JetBrains config directory.
11. Add a mechanism for passing additional trusted CA certificates or corporate proxy settings without mounting host-wide directories.
12. Add clear documentation for Claude-related plugins in a later revision, after verifying the current recommended PyCharm integration path.
13. Manually validate the host UID/GID mapping and `--dev-sudo` behavior from a
    second non-default host user account. The launcher intentionally uses the
    current host launcher user's actual `id -u:id -g` and does not assume UID
    1000; this follow-up is useful coverage but is not a v0 stabilization
    blocker after the primary mapped-user validation.
14. After the post-MVP refactoring, manually validate GitHub SSH remotes with
    `--ssh-agent` and HTTPS remotes with `--git-token-env` / `--git-token-file`.
    This is useful but no longer a v0/MVP blocker because the user can push from
    outside the isolated IDE environment.
15. Refine `index.md` into a generated documentation index backed by
    frontmatter metadata in each markdown file. The intended direction is that
    each `.md` file declares stable tags, category, status, and/or audience in
    frontmatter, then a repository-side script regenerates `index.md` and checks
    that the manual documentation map has not drifted. This remains a later
    documentation-tooling task; until then, agents must update `index.md`
    manually when markdown files are added, deleted, renamed, or moved.

The post-MVP refactoring direction is documented in
`engineering-docs/design-notes/docker4pycharm/future-agent-refactoring-brief.md`.
Read it before planning work that generalizes this repository beyond the
current `docker4pycharm` prototype.

The human/agent iteration workflow is documented in `WORKFLOW.md`. The
requirements register is documented in `REQUIREMENTS.md`. For using the current
PyCharm v0 image on an ordinary Python project, see
`engineering-docs/implementation-notes/docker4pycharm/using-v0-for-real-python-projects.md`.

## Guidance for future AI development agents

When continuing this project inside the bootstrapped IDE:

- Read `WORKFLOW.md` before changing the project handoff or active task list.
- Read `REQUIREMENTS.md` before changing behavior, validation scope, or
  prioritization.
- Treat the repository files as the project knowledge base. Persist important requirements, decisions, current state, and handoff notes in versioned files rather than relying on conversation memory.
- Keep context focused. Prefer narrow, explicit work targets and update the handoff when the active target changes.
- Preserve the human role as project director and quality owner: ask for decisions where product judgment, code-quality judgment, risk tolerance, overall project-quality acceptance, or prioritization is genuinely needed, but do not push routine implementation bookkeeping back to the user.
- Preserve the core isolation principle: do not mount host directories beyond the explicitly selected project, IDE state, IDE plugins, and narrowly scoped runtime/credential resources.
- Prefer explicit launcher options over broad default access, except for the
  revised MVP requirement that Docker capability should be available by default
  to the IDE-side agent through the host Docker socket.
- Treat Docker capability as a deliberate MVP productivity exception. The
  default is host Docker socket passthrough; true Docker-in-Docker is an
  explicit `--docker-in-docker` option; `--no-docker` is the clear opt-out.
- Do not mount host `~/.ssh`; use SSH agent forwarding or explicit secret files.
- Do not persist API keys or OAuth tokens into the image.
- Treat AI plugin authentication as a first-class integration test.
- Make security relaxations opt-in, visible in command-line flags, and documented.
- Treat `docker4ides/` as the active development subproject.
- Keep `docker4pycharm/README.md` focused on historical/reference PyCharm
  operational usage.
- Keep this root `README.md` focused on project-wide context, design rationale, and future direction.

## Reference links checked during bootstrap

These links were used to validate the current PyCharm/OpenAI/JetBrains assumptions. Re-check them before making future authentication or plugin recommendations, because IDE plugin behavior and subscription rules can change.

- OpenAI Codex IDE extension documentation: https://developers.openai.com/codex/ide
- JetBrains blog: Codex is integrated into JetBrains IDEs: https://blog.jetbrains.com/ai/2026/01/codex-in-jetbrains-ides/
- JetBrains AI Assistant installation guide: https://www.jetbrains.com/help/ai-assistant/installation-guide-ai-assistant.html
- JetBrains AI Assistant Marketplace page: https://plugins.jetbrains.com/plugin/22282-jetbrains-ai-assistant

## Current state and next step

This section is the project handoff point. Future agents should update it when completing a stage, changing the project state materially, or ending a session.

Current stage: `docker4pycharm` v0/MVP checkpoint complete; `docker4ides`
Python MVP is the active post-MVP refactoring stage.

Repository shape: `docker4ides/` is the active Python CLI/framework subproject
for new code, packaging, configuration protocol work, tests, and current user
documentation. `docker4pycharm/` is the historical PyCharm shell
implementation and reference baseline for the original working MVP.

Current stage goal / exit criteria: finish the V1 / `python_mvp` surface by
preserving the working PyCharm MVP, completing Python `docker4ides pycharm run`
parity without depending on `docker4pycharm` bootstrap crutches for the
implemented Python run path, providing usable PEX/source-install paths, adding
acceptable user documentation for exposed V1 functionality, making the
`docker4ides` Python project itself embody a good-enough current engineering
process, and building plus testing at least one additional IDE-plus-agent
combination: VS Code plus Claude. The VS Code plus Claude proof point should
show that the framework works beyond PyCharm and provide a concrete model for
future users to create their own configuration. The engineering-process
criterion should remain lightweight, but V1 should close obvious gaps such as
not reporting or gating on test coverage.

Current status: PyCharm can run inside the Docker container, open the selected
project, and the AI/Codex/ChatGPT plugin path has worked from inside that IDE
environment. The user accepted the current v0 state as MVP on 2026-06-30 after
local Git identity edge-case validation was completed. Retrospective note:
`engineering-docs/completed-tasks/docker4pycharm/2026-06-30-pycharm-v0-mvp-checkpoint.md`.

Latest stabilization update: `docker4pycharm/run-pycharm-container.sh` now
defaults to host Docker daemon passthrough for developer convenience. The
launcher mounts the host Docker socket at `/run/host-docker.sock`, sets
`DOCKER_HOST=unix:///run/host-docker.sock`, and adds the host socket group ID as
a supplemental group for the mapped IDE user. True Docker-in-Docker remains
available only as the explicit `--docker-in-docker` / `--dind` mode, which
starts the outer IDE container with `--privileged`, a writable root filesystem,
and an inner `dockerd`. Use `--no-docker` or `DOCKER_MODE=none` for the
higher-isolation no-Docker profile. Legacy `DOCKER_IN_DOCKER=1` still selects
DinD, and `DOCKER_IN_DOCKER=0` selects no-Docker, for compatibility with the
previous launcher behavior. The image package baseline now includes
`shellcheck` so future sessions can lint launcher scripts after rebuilding the
image.

Explicit Docker-in-Docker validation update: on 2026-06-20, the latest built VM
was tested manually and Docker-in-Docker worked as expected. Do not reopen the
explicit DinD validation item unless a later image or launcher change regresses
it. Retrospective note:
`engineering-docs/completed-tasks/docker4pycharm/2026-06-20-explicit-docker-in-docker-validation.md`.

Default host Docker validation update: on 2026-06-20, the default host Docker
passthrough validation item was removed from the active v0 stabilization list.
Do not reopen it unless a later image or launcher change affects the default
Docker path. Retrospective note:
`engineering-docs/completed-tasks/docker4pycharm/2026-06-20-default-host-docker-passthrough-validation-retired.md`.

Retired issue note: the earlier PyCharm Markdown preview blank/hang issue is no
longer reproduced in the current iterations, so it has been removed from the
active stabilization task list. Historical symptoms and log signatures are
preserved in
`engineering-docs/completed-tasks/docker4pycharm/2026-06-20-markdown-preview-skiko-opengl-hang-retired.md`
in case it returns.

Process documentation update: the current human/agent iteration loop is now
captured in `WORKFLOW.md`, including the human role in code-quality judgment
and overall project-quality acceptance. Accepted requirements now live in
`REQUIREMENTS.md` with stable IDs, priority, status, implementation references,
validation references, and related task or bug links. Active tasks and bug
records should cite requirement IDs when they materially implement, validate,
change, defer, or reinterpret a requirement. Guidance for reusing the current
`pycharm-isolated:codex-debug-v004` image on an ordinary Python project is in
`engineering-docs/implementation-notes/docker4pycharm/using-v0-for-real-python-projects.md`.
The image build now includes a reusable bootstrap template at
`/usr/local/share/docker4ide/vibe-coding-process.md` so a future agent can
apply the process to a newly mounted project without manual copy/paste by the
user. The process now includes `engineering-docs/bugs/` for durable bug
reports with reproduction steps, evidence, hypotheses, verification targets,
close criteria, and affected requirements. Closed or retired tasks now move to
`engineering-docs/completed-tasks/docker4pycharm/`, while active tasks keep
explicit requirement IDs, done criteria, verification, and reopen conditions.
Documentation index update: `index.md` now lists all repository markdown
documentation using relative links grouped by category. `AGENTS.md` now
requires future agents to update `index.md` whenever a `.md` file is added,
deleted, renamed, or moved.

Python-project UX update: on 2026-06-24, feedback from using the image in a
separate test Python project was folded into the checked-in image and launcher.
The image package baseline now includes `python-is-python3`, `file`, `sudo`, and
PostgreSQL `libpq` client development/runtime packages for Psycopg source-build
compatibility, while still avoiding bundled database services. The image also
adds `docker4ide-bootstrap-project`, an idempotent helper that creates
`AGENTS.md`, `REQUIREMENTS.md`, a README handoff section,
`engineering-docs/implementation-notes/`, `engineering-docs/bugs/`, and basic Python
`.gitignore` entries in a mounted project. The launcher now defaults to
auto-importing only host global
Git author identity strings when available and adds
`--no-git-identity-from-host` as the opt-out. Implementation note:
`engineering-docs/design-notes/docker4pycharm/2026-06-24-python-project-ux-defaults.md`.
Repository-side validation passed for this change: Bash syntax checks,
ShellCheck, `git diff --check`, launcher `--help`, and scratch-project
idempotence checks for `docker4ide-bootstrap-project`. Manual validation on
2026-06-28 confirmed the latest development baseline is good in the rebuilt
image. Git identity auto-import, opt-out behavior, and remote credential
transport remain tracked under the separate R-GIT-001 validation item.

Development sudo profile update: on 2026-06-24, the Dockerfile was updated to
install `sudo`, and the launcher gained explicit `--dev-sudo` / `--sudo`
support. That profile adds the mapped IDE user to a runtime-only `ide-sudo`
group with passwordless sudo, implies a writable root filesystem, and avoids
the default `no-new-privileges` / `--cap-drop ALL` restrictions so
container-local package installs can work. The default host-Docker and
no-Docker profiles still keep sudo escalation disabled. Implementation note:
`engineering-docs/design-notes/docker4pycharm/2026-06-24-development-sudo-profile.md`.
Repository-side validation passed for this change: Bash syntax checks,
ShellCheck, `git diff --check`, launcher `--help`, and fake-Docker argument
checks for default versus `--dev-sudo` profile flags. Manual validation on
2026-06-28 initially found an account-validation failure; the wrapper now
generates and mounts a synthetic `/etc/shadow` only for `--dev-sudo`, and the
user confirmed `sudo -n ls` works in the launched container. Retrospective note:
`engineering-docs/completed-tasks/docker4pycharm/2026-06-28-dev-sudo-account-validation.md`.

Concurrent shared-config limitation update: on 2026-06-24, manual testing
found that two different projects cannot run concurrently when they share the
same JetBrains `idea.config.path`; PyCharm/IDEA-family IDEs lock that config
directory while an IDE process is running. This is now treated as a documented
IDE limitation rather than an unresolved requirement to make one live config
directory concurrent. Limitation record:
`engineering-docs/bugs/docker4pycharm/2026-06-24-concurrent-projects-shared-global-settings-lock.md`.

Concurrent-project config update: the launcher now mounts JetBrains config at
`/ide-config` and adds `--project-config`, which maps `idea.config.path` to
`<project-state>/config` for concurrent sessions. The default remains shared
config at `<global-settings>/config` for backward compatibility and settings
continuity. In shared/custom config modes, the launcher fails early if
`.lock` already exists and suggests `--project-config`; `--ignore-config-lock`
is available for an intentionally stale-lock recovery attempt. Repository-side
checks passed:
script syntax, ShellCheck, `git diff --check`, launcher `--help`, entrypoint
`IDE_CONFIG_PATH` property generation, shared-config lock preflight, and
`--project-config` path selection using a fake Docker executable. Full GUI
validation of a second live project with `--project-config` remains useful, but
is no longer a blocker for closing the current task.

Deferred settings-profile note: the user may later want a global settings
profile per IDE or IDE family, for example Python/PyCharm, that seeds the
initial settings for a new per-project config directory. That would preserve
common preferences such as notebook execution behavior without requiring
unrelated or concurrent projects to share the same lock-bearing live
`idea.config.path`. Requirement: `R-SETTINGS-001`.

Per-project IDE state update: on 2026-06-21, the launcher was changed to split
shared IDE configuration from volatile per-project state. The old default
`~/.local/share/pycharm-docker/state` is now treated as the shared
`--global-settings` root and remains available through the legacy `--state`
alias. Plugins remain shared through `--plugins`. Per-project caches, logs, and
workspace state now default to
`~/.local/share/pycharm-docker/project-state/<project-id>`, and projects are
mounted inside the container at `/workspace/<project-id>` instead of all sharing
the same `/project` path. This is intended to avoid stale JetBrains Project view
or open-file state when the same PyCharm setup is reused across unrelated host
projects. Implementation note:
`engineering-docs/design-notes/docker4pycharm/2026-06-21-per-project-ide-state-split.md`.

Per-project IDE state manual validation update: on 2026-06-22, the user
manually launched this repository and a separate ordinary Python project with
the same shared global settings and plugins while using the default per-project
state and mount paths. The Project view, open-file state, and recent workspace
state behaved as intended for the current mounted project. Do not reopen this
unless stale Project view contents, open files, or project-window state from one
host project appear when opening a different host project with default
per-project state.

Bootstrap process template validation update: on 2026-06-20,
`pycharm-isolated:codex-debug-v004` was confirmed as the running image for this
agent session, and `/usr/local/share/docker4ide/vibe-coding-process.md` was
confirmed present and close enough to `WORKFLOW.md` to serve as the reusable
bootstrap process instructions. This was an improvement over the previously
referenced `pycharm-isolated:codex-debug-v003` image. Do not reopen this unless
a later image removes the template or the template drifts materially from the
current workflow. Retrospective note:
`engineering-docs/completed-tasks/docker4pycharm/2026-06-20-bootstrap-process-template-v004-validation.md`.

Build networking remains configurable in `docker4pycharm/build-image.sh`. The
default build network is Docker's normal `default` mode, while
firewall-constrained hosts can opt into host networking with `--network host` or
`DOCKER_BUILD_NETWORK=host`.

Mesa/OpenGL runtime update: on 2026-06-22, the image and launcher were updated
to make the current working Mesa path explicit. The Dockerfile includes
`libgl1`, `libglx-mesa0`, `libgl1-mesa-dri`, and `mesa-utils`; the launcher and
entrypoint default JetBrains/Skiko rendering to Mesa `llvmpipe` software GL
without mounting host `/dev/dri`; and the image includes
`docker4ide-check-runtime-deps` for repeatable checks. This addresses the
`drm` / `dri3` / `iris` warning class separately from the earlier missing
`libGL.so.1` dependency failure.

Mesa/OpenGL manual validation update: on 2026-06-22, after the fresh image was
tested again, the user reported that everything looks OK now. Treat the
software-GL path, Markdown preview behavior, and related Skiko/OpenGL logging as
manually validated for the current v0 image. Do not reopen the Skiko/OpenGL
context item unless Markdown preview again becomes blank/unresponsive or the
logs again show active `Cannot create OpenGL context` failures under the default
launcher path. Retrospective note:
`engineering-docs/completed-tasks/docker4pycharm/2026-06-22-mesa-skiko-markdown-validation.md`.

Deferred GPU passthrough note: do not use NVIDIA or `/dev/dri` passthrough as
the next rendering fix. Preserve GPU passthrough for a later explicit
developer-workload profile, especially for Python ML projects on hosts with
NVIDIA hardware. That future option should assume NVIDIA first, be documented as
a host-exposure relaxation, and remain separate from the v0 default software-GL
rendering path.

Checkpoint update: on 2026-06-22, the repository state was prepared for manual
validation against the next image build. Changed items included the per-project
IDE state split, explicit Mesa software-GL defaults, and the framework-named
`docker4ide-check-runtime-deps` helper. Script syntax, ShellCheck, whitespace
checks, and the repository-local runtime helper passed in the then-running
container. The follow-up fresh PyCharm launch has now been manually accepted by
the user for the current v0 stabilization pass.

Post-MVP refactoring context:
`engineering-docs/design-notes/docker4pycharm/future-agent-refactoring-brief.md`
describes the intended move from one-off PyCharm scripts toward a
profile-driven Python `docker4ide` framework with shared runtime orchestration,
IDE-family adapters, and product-specific profiles.

Product positioning update: `docs/product/working-backwards-press-release.md` now
captures a working-backwards v1 product narrative for Docker4IDE as
one-command environment rehydration plus repo-local project memory
rehydration. `docs/index.html` is a self-contained GitHub Pages-friendly
version of the same story, and `docs/product/linkedin-announcement.md` contains draft
LinkedIn announcement copy with a placeholder GitHub Pages URL.

0.2 positioning draft update: `docs/product/draft-pitch.md` captures the early
post-MVP pitch direction around batteries-included developer workspaces,
explicit host-access boundaries, AI-agent readiness, the tailor-with-torn-pants
motif, and naming concerns around `mycodespace.ai` versus GitHub Codespaces.

When resuming the project, read these files in order:

1. `README.md` for project-wide requirements, architecture, and backlog.
2. `index.md` for the grouped index of all markdown documentation.
3. `REQUIREMENTS.md` for accepted requirements, priority, status, and
   traceability to implementation and validation.
4. `WORKFLOW.md` for the human/agent iteration process, requirements hygiene,
   and task-list hygiene.
5. `docker4ides/README.md` for the active Python CLI/framework user
   documentation.
6. `docker4pycharm/README.md` for the historical/reference PyCharm container
   build/run workflow.
7. `engineering-docs/implementation-notes/docker4pycharm/debugging.md` for the handoff from the debugging session that made the current image work.
8. `docs/guides/docker4pycharm-ai-plugin-and-chatgpt-setup.md` for the
   human-facing PyCharm AI plugin and ChatGPT subscription setup notes.
9. `engineering-docs/design-notes/docker4pycharm/future-agent-refactoring-brief.md`
   before planning post-MVP refactoring beyond the current PyCharm target.
10. `docs/product/working-backwards-press-release.md` before changing v1 product
   positioning, onboarding goals, or open-source launch messaging.
11. `engineering-docs/implementation-notes/docker4pycharm/using-v0-for-real-python-projects.md` before applying this workflow to a normal Python project with the current v0 image.
12. `engineering-docs/bugs/docker4pycharm/` for active bug records,
   especially before changing launcher state or runtime behavior.
13. `engineering-docs/design-notes/docker4pycharm/2026-06-21-per-project-ide-state-split.md`
   before changing PyCharm state, settings, or project mount behavior.
14. `engineering-docs/design-notes/docker4pycharm/2026-06-22-git-identity-and-credentials.md`
   before changing Git identity, SSH-agent, or HTTPS token credential behavior.
15. `engineering-docs/design-notes/docker4pycharm/2026-06-22-mesa-software-gl-default.md`
   before changing Mesa/OpenGL, Skiko, Markdown preview, or GPU passthrough behavior.
16. `engineering-docs/completed-tasks/docker4pycharm/` only when a retired
   issue recurs, when doing retrospective work, or when comparing current
   behavior against a completed task.

Immediate engineering priority: preserve the working PyCharm MVP while
extracting reusable pieces into the active Python `docker4ides` framework. The
existing `docker4pycharm` shell scripts remain the historical/reference PyCharm
baseline while shared runtime orchestration, configuration protocol, and
IDE-family behavior move into Python.

Active docs cleanup note: `/project` is no longer the default mounted project
path for PyCharm v0. The current launcher intentionally mounts projects at
`/workspace/<project-id>` by default to avoid stale JetBrains project-window
state; use `--project-mount` only when a tool truly needs a fixed in-container
path. Treat active instructions that require `/project/README.md` as stale
fixed-path assumptions to remove or replace with repository-relative
`README.md` guidance. Historical debugging notes and future framework sketches
may still mention `/project` when describing older behavior or conceptual
targets.

Session close update for 2026-06-24: repository-side work has been completed
for the latest Python-project UX defaults, concurrent config handling, stale
`/project/README.md` instruction cleanup, and the explicit development sudo
profile. The next validation pass should use a freshly rebuilt image and a
launched PyCharm/Codex container to confirm these changes show up in the image
before marking them manually validated.

Manual validation update for 2026-06-28: the user started verifying the rebuilt
image for R-DEV-001. The latest development baseline is currently good except
for the explicit `--dev-sudo` path. Launching with `--dev-sudo` reaches the
container, but `sudo -n true` fails with:

```text
sudo: account validation failure, is your account locked?
sudo: a password is required
```

Treat this as the top next task. Record:
`engineering-docs/completed-tasks/docker4pycharm/2026-06-28-dev-sudo-account-validation.md`.

Follow-up fix update for 2026-06-28: `run-pycharm-container.sh` now
generates and mounts a synthetic `/etc/shadow` only for `--dev-sudo`, alongside
the existing synthetic `/etc/passwd` and `/etc/group`. The mapped IDE user still
uses the host launcher user's actual `id -u:id -g`; the launcher does not
assume UID 1000. Syntax, ShellCheck, and fake-Docker argument checks passed.
The user manually confirmed `sudo -n ls` works in the launched container. A
manual retest from a different non-default host user account is deferred for
later and is not a current v0 blocker.

Git remote credential validation deferral for 2026-06-28: the user decided
GitHub SSH remote validation with `--ssh-agent` and HTTPS remote validation with
`--git-token-env` / `--git-token-file` should not block v0/MVP. For the current
MVP, pushing from outside the isolated IDE environment is acceptable, though less
than ideal. Revisit this after the post-MVP refactoring. Retrospective note:
`engineering-docs/completed-tasks/docker4pycharm/2026-06-28-git-remote-validation-deferred.md`.

Local Git identity validation closeout for 2026-06-30: R-GIT-001 local identity
behavior is manually validated for the current v0 launcher. The user confirmed
the default host global Git `user.name` and `user.email` import path, explicit
`--git-user-name` / `--git-user-email` flags, intentional opt-out with
`--no-git-identity-from-host`, and explicit missing-host-identity warning with
`--git-identity-from-host`. Reopen only if commits fall back to the container
auto-generated identity, opt-out still imports host identity, or missing
identity fails unclearly. GitHub SSH/HTTPS remote validation remains deferred
until after the post-MVP refactoring. Retrospective note:
`engineering-docs/completed-tasks/docker4pycharm/2026-06-30-local-git-identity-edge-validation.md`.

Initial Python refactor slice for 2026-07-03: the user chose the pluralized
package/CLI name `docker4ides`. A new Python project now lives under
`docker4ides/` with `pyproject.toml`, pip/pip-compile dependency files,
`python -m docker4ides`, the `docker4ides` console script, and a first command
tree:

```text
docker4ides run pycharm ...
docker4ides build pycharm ...
docker4ides check runtime pycharm ...
docker4ides bootstrap project ...
```

The build, check, and bootstrap commands still use compatibility delegation
until they are translated. The run path should not be treated as a permanent
argument-forwarding facade; the refactoring goal is to translate the launcher
behavior from Bash into maintainable Python runtime planning and execution.
Repository-side verification passed in a temporary venv with
`python -m pytest docker4ides`, top-level CLI help, and PyCharm run/build
leaf-help delegation smoke checks.

PyCharm run translation update for 2026-07-05: `docker4ides run pycharm` now
uses translated Python launcher code instead of forwarding its arguments to
`docker4pycharm/run-pycharm-container.sh`. The new
`docker4ides/docker4ides/project.py` module mirrors the current shell behavior
for basename sanitization, SHA-256-based project namespace calculation, default
`/workspace/<project-id>` mount generation, and reserved in-container
project-mount rejection. The new `docker4ides/docker4ides/pycharm.py` module
parses the PyCharm run options, plans project/global/config/plugin state paths,
handles Docker mode selection, creates temporary Xauthority/passwd/group/shadow
and token files, generates Docker run arguments, and invokes `docker run`
directly. The old shell launcher remains available as a manually callable
compatibility script while parity is validated. Verification passed from
`docker4ides/` with `.venv/bin/python -m pytest` and
`.venv/bin/python -m docker4ides run pycharm --help`; the root shell wrapper
help also passed with `docker4pycharm/run-pycharm-container.sh --help`.

Typer CLI refactor update for 2026-07-05: the Python CLI no longer uses a
hand-rolled dispatcher in `docker4ides/docker4ides/cli.py`, and the translated
PyCharm run path no longer has a second internal `argparse` parser. The public
command tree is now implemented with Typer/Click subcommands, with build,
runtime-check, and bootstrap compatibility commands still forwarding unknown
arguments to their existing scripts. PyCharm config selection is now explicit:
use `--config-mode shared|project|custom`; `--project-config` and
`--shared-config` remain compatibility shorthands, but conflicting combinations
such as `--config-mode shared --ide-config ...` are rejected instead of being
resolved by Bash-style option order.

Dependency polish update for 2026-07-07: `docker4ides/pyproject.toml` is now
the source of truth for Python runtime and contributor dependencies. Python
3.12+ is required, `python -m pip install -e ./docker4ides` is the source
checkout install path, and `python -m pip install -e "./docker4ides[dev]"`
installs contributor tooling. The pinned `requirements.txt` and
`dev-requirements.txt` files are regenerated from `pyproject.toml` and no
longer depend on duplicate `.in` inputs.

Python CLI ergonomics update for 2026-07-07: the current refactor stage is now
framed as preserving `docker4pycharm/` scripts as the stable compatibility and
reference surface while making `python -m docker4ides` easier for day-to-day
use and contributor testing. `docker4ides run pycharm` now defaults `--project`
to the current directory, accepts `--profile NAME` for repeated shared settings
and plugin roots under `~/.config/docker-pycharm-NAME/`, and accepts
`--project-state-root DIR` for mirrored per-project state trees. Verification
passed from `docker4ides/` with `.venv/bin/python -m pytest` and
`.venv/bin/python -m docker4ides run pycharm --help`.

Python MVP distribution goal update for 2026-07-07: Python MVP should include
an end-user path that does not require creating a virtual environment or
understanding editable installs. The accepted initial direction is a
single-file Python executable archive, likely `dist/docker4ides.pex`, built
from package metadata and the pinned dependency set, while keeping the builder
tooling out of runtime dependencies. Requirement: R-PYTHON-MVP-002.

Python MVP PEX artifact update for 2026-07-07: `docker4ides/scripts/build-pex.sh`
now builds `docker4ides/dist/docker4ides.pex` from the local package and pinned
runtime lock file. `pex` is part of contributor/build dependencies, not runtime
dependencies, and `docker4ides/dist/` remains ignored. Repository-side
validation passed from a fresh temporary venv using the locked contributor
setup, then `PYTHON=<tmp-venv>/bin/python docker4ides/scripts/build-pex.sh`,
`python3.12 docker4ides/dist/docker4ides.pex --help`, and
`python3.12 docker4ides/dist/docker4ides.pex run pycharm --help`.

Python MVP build gate update for 2026-07-08: `docker4ides/noxfile.py` now
defines the Python-native project build gate. From `docker4ides/`, `nox -s
build` installs the locked contributor dependencies, installs `docker4ides`
editable with `--no-deps`, compiles Python sources, checks shell script syntax,
runs pytest, smoke-tests the Python CLI and shell wrapper help, builds the PEX
artifact, and smoke-tests the PEX CLI. Repository-side validation passed with
`cd docker4ides && .venv/bin/python -m nox -s build`.

Python MVP PEX host smoke update for 2026-07-08: the user confirmed the
PyCharm run path works through `docker4ides/dist/docker4ides.pex` on the
Ubuntu 22.04 host. Treat R-PYTHON-MVP-002 as manually validated unless a
later PEX launch diverges materially from the known shell launch behavior.

Python MVP V1 scope update for 2026-07-08: R-PYTHON-MVP-003 now records the
accepted V1 (`python_mvp`) feature boundary, explicit deferrals, done criteria,
and likely implementation order. V1 should finish PyCharm Python launcher
parity, packaging, acceptable user docs, focused non-GUI regression coverage,
lightweight engineering-process hygiene for `docker4ides` itself, and at least
one additional IDE-plus-agent proof point: VS Code plus Claude. Broader
multi-IDE profile loading, IDE-family adapters beyond the V1 proof point,
extension workflows, formal release automation, alternate GUI transports,
GPU/device profiles, and previously deferred GitHub remote push validation
remain post-V1 work.

Click-based CLI cleanup update for 2026-07-08: the user added
`engineering-docs/design-notes/devcapsule/click-based-cli-parsing-brief.md` as the target
direction for human-readable CLI parsing. `docker4ides` now uses class-backed
Click commands discovered from `docker4ides/docker4ides/commands/` instead of a
central Typer command registry. The public command tree is preserved, including
`docker4ides run pycharm`, shell-backed compatibility commands, and the hidden
`bootstrap-project` alias. Optional external plugin entry points from the brief
are intentionally deferred until after V1. Since Typer is no longer imported,
it was removed from runtime dependencies and the lock files were regenerated.
Validation passed from `docker4ides/` with `.venv/bin/python -m pytest`,
`.venv/bin/python -m docker4ides --help`,
`.venv/bin/python -m docker4ides run pycharm --help`, compatibility help
forwarding checks, and `.venv/bin/python -m nox -s build`.

Configuration-first CLI update for 2026-07-08: the accepted primary command
shape is now the configuration alias first, then the action, for example:

```text
docker4ides pycharm run ...
docker4ides pycharm build ...
docker4ides pycharm check-runtime
```

The same shape applies to the PEX artifact, for example:

```text
python3.12 docker4ides/dist/docker4ides.pex pycharm run --help
```

This is not only a cosmetic command-order change. The Click-facing `commands`
package is now intended to stay a small command-tree adapter, while
per-configuration packages under `docker4ides/docker4ides/configurations/`
own the IDE-specific interface and implementation. For PyCharm, the public
module interface is `docker4ides.configurations.pycharm.PycharmConfiguration`;
that object builds the `pycharm run`, `pycharm build`, and
`pycharm check-runtime` Click commands. The private translated launcher now lives in
`docker4ides/docker4ides/configurations/pycharm/_launcher.py`. A tested
`vscode_with_claude` configuration module is registered as the next proof-point
alias with explicit not-yet-implemented `run` and `build` commands. Verification
passed from `docker4ides/` with `.venv/bin/python -m pytest` and
`.venv/bin/python -m nox -s build`.

PyCharm module-boundary cleanup for 2026-07-09: following the
configuration-first CLI work, the PyCharm command files were collapsed so
`docker4ides/docker4ides/commands/pycharm.py` is the only PyCharm adapter in
the command tree. The previous almost-empty
`commands/pycharm/run.py`, `commands/pycharm/build.py`, and
`commands/pycharm/check_runtime.py` files were removed, along with the
noun-first `commands/run`, `commands/build`, and `commands/check` compatibility
groups. The Python CLI now supports only the configuration-first command shape.
The bulk of PyCharm knowledge is now packaged under
`docker4ides/docker4ides/configurations/pycharm/`, with public names exposed
from `__init__.py`, `PycharmConfiguration` implemented in `configuration.py`,
and private implementation details kept in `_launcher.py`.
Verification passed from `docker4ides/` with `.venv/bin/python -m pytest` and
`.venv/bin/python -m nox -s build`.

Command adapter cleanup for 2026-07-09: the same module-boundary cleanup was
applied to Bootstrap and VS Code plus Claude. `commands/bootstrap.py` is now the
single Bootstrap command adapter, and the hidden `bootstrap-project` alias was
removed. `commands/vscode_with_claude.py` is now the single VS Code plus Claude
command adapter. Its proof-point configuration identity and explicit
not-yet-implemented `run` / `build` behavior are owned by
`docker4ides.configurations.vscode_with_claude.VscodeWithClaudeConfiguration`.
The current command adapter tree is intentionally small: generic command
helpers plus one file per public top-level command. Verification passed from
`docker4ides/` with `.venv/bin/python -m pytest` and
`.venv/bin/python -m nox -s build`.

User-facing configuration model update for 2026-07-09: requirements and user
documentation now describe the intended end-user shape as
`docker4ides CONFIGURATION ACTION [options]`. `R-IDE-CONFIG-001` records this
configuration-first CLI model and explicitly rejects noun-first paths such as
`docker4ides run pycharm`. `R-DOCS-002` and `WORKFLOW.md` now define the
user-level documentation protocol: user-visible behavior changes must update
requirements, relevant user docs, and handoff notes together. `docker4ides/README.md`
now explains what an end user should be able to do with IDE configurations:
discover configurations, build/update supported configuration images, run a
configuration against a project, pass configuration-specific options without
exposing unrelated host state, and use the same command shape from source and
PEX paths.

Top-level documentation cleanup for 2026-07-09: the root markdown files now
state the repository split explicitly. `docker4ides/` is documented as the
active Python CLI/framework subproject, while `docker4pycharm/` is documented
as the historical PyCharm reference baseline. `index.md` groups the active and
historical subprojects separately, `WORKFLOW.md` records the rule for future
doc changes, `REQUIREMENTS.md` explains how old PyCharm MVP requirements relate
to current `docker4ides` work,
`docs/guides/docker4pycharm-ai-plugin-and-chatgpt-setup.md` is framed as
PyCharm plugin setup for the reference baseline, and
`engineering-docs/design-notes/docker4pycharm/future-agent-refactoring-brief.md`
carries a status note pointing back to the current README handoff and
`docker4ides` docs.

Current and next work:

Current task:

1. Continue the Python V1 hardening on the new configuration-first command
   surface: audit `docker4ides pycharm run` parity against the shell launcher
   and add focused tests for any missing run-planning or Docker-argument
   behavior, verify the Python implementation no longer depends on
   `docker4pycharm` bootstrap crutches for supported run behavior, plus minor
   cleanup after the latest Python CLI code changes.
   Requirements: R-PYTHON-MVP-003, R-FRAMEWORK-001, R-SCOPE-001.
   Context: the V1 feature boundary is now settled. The next useful work is to
   make sure the translated Python run path covers the accepted PyCharm V1
   surface without silently changing host exposure, and to get the recent code
   into a clean enough shape for the human quality owner to decide, with agent
   consultation, that the project can move forward. This cleanup should also
   identify and address lightweight process gaps in the `docker4ides` Python
   project itself, including the current lack of test coverage reporting or
   gating.
   Done means: the audit records any parity gaps, missing tests are added for
   option conflicts/path planning/security modes/Docker arguments, minor
   cleanup from the latest code changes is complete, supported PyCharm run
   behavior is implemented in the Python codebase rather than delegated to
   `docker4pycharm` bootstrap scripts or other compatibility crutches, any
   obvious V1 engineering-process gaps such as coverage reporting/gating are
   closed or explicitly documented as deferred, small parity fixes stay within
   the documented V1 scope, and the human has accepted the code as shapely
   enough to proceed.
   Verification: run `cd docker4ides && python -m nox -s build`; review
   generated Docker arguments and docs together for any changed mount,
   credential, device, or Docker access behavior.
   Reopen if: Python `pycharm run` diverges from the shell reference for a
   supported V1 option, or a host exposure change lands without matching docs.

Next task:

1. Define the small shared Python protocol for IDE configurations based on the
   documented end-user model, then make PyCharm and VS Code plus Claude conform
   to it before implementing VS Code plus Claude behavior.

Standing stabilization rule:

1. Keep any isolation relaxation explicit and documented.
   Requirements: R-SCOPE-001, R-DOCKER-001.
   Done means: any change that broadens host exposure is represented by a clear
   launcher option/default, README text, and implementation note.
   Verification: review Docker/run arguments and docs together before closing
   each stabilization change.
   Reopen if: a change adds host access, credentials, networking, devices, or
   filesystem mounts without matching documentation.
