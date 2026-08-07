# Future Agent Handoff: DevCapsule Refactoring Strategy

This file is intended for the next ChatGPT/Codex development agent working inside the IDE that was bootstrapped by the DevCapsule project.

It summarizes the intended direction after the initial `docker4pycharm` prototype and lays out the strategy for extending the project to IntelliJ IDEA, VS Code, and VSCodium without duplicating implementation logic.

Naming update: on 2026-07-03, the user chose `docker4ides` as the Python
package and CLI name. Older sketches in this document may still say
`docker4ide` when describing the conceptual framework, image names, or
pre-existing helper commands.

Status update: as of 2026-07-09, active implementation work is in the Python
distribution project now named `devcapsule-src/`. The original
`docker4pycharm/` shell implementation is kept as the historical PyCharm
reference baseline. This brief remains useful for strategy and rationale, but
the current task list and exact command shape live in the final handoff section
of `README.md` and the active user documentation in
`devcapsule-src/README.md`.

---

## Project Context

The project goal is to run full desktop IDEs inside Docker containers while preserving the developer experience and minimizing host exposure.

The first prototype targeted PyCharm. It provided:

- A Docker image containing PyCharm and common Linux development/debugging tools.
- A launcher script that starts PyCharm under X11.
- Persistent IDE configuration, system/cache/log state, and plugins outside the image.
- A project directory mounted into the container and opened by the IDE.
- Optional SSH-agent forwarding for GitHub SSH workflows.
- Optional GitHub token transport for HTTPS workflows.
- A restrictive default mount policy:
  - Do not mount the host home directory.
  - Do not mount `~/.ssh`.
  - Do not mount `~/.gitconfig`.
  - The initial prototype did not mount Docker socket or provide
    Docker-in-Docker; the current PyCharm MVP now mounts the host Docker socket
    by default as a developer-convenience exception, keeps true
    Docker-in-Docker as explicit `--docker-in-docker`, and provides
    `--no-docker` as the opt-out.
  - Only mount the project, IDE state, plugin/extension state, X11 transport/auth, and explicitly requested credential transports.
- A read-only root filesystem with writable tmpfs areas for `/tmp`, `/run`, and `/var/tmp`.
- An optional native-debugging mode that enables `SYS_PTRACE` and relaxes seccomp.

MVP correction: the agent runs inside the IDE container, so lack of Docker
access prevented it from rebuilding and testing the very image/launcher it was
editing. The PyCharm prototype now connects to the host Docker daemon by default
for local developer convenience, offers explicit true Docker-in-Docker for
separate Docker state, and keeps `--no-docker` for higher-isolation sessions.

The generated PyCharm-specific implementation files are expected to live in:

```text
docker4pycharm/
```

The repository may later contain other build subfolders for other IDE configurations.

---

## Current High-Level Requirement

Extend the design so the project can support:

```text
PyCharm
IntelliJ IDEA
VS Code
VSCodium
possibly other JetBrains IDEs later
possibly other VS Code-family editors later
```

The key requirement is to avoid maintaining separate, divergent Dockerfiles and launcher scripts for every IDE.

The preferred direction is to refactor the prototype into a small framework with:

- Shared runtime orchestration.
- Shared Docker image layers.
- IDE-family-specific behavior.
- Product-specific declarative profiles.
- Thin compatibility wrappers for convenience.

---

## Key Observation

PyCharm and IntelliJ should not be treated as unrelated targets. They belong to the JetBrains IDE family and share most runtime behavior.

Similarly, VS Code and VSCodium should not be treated as unrelated targets. They belong to the VS Code/Electron editor family and share most runtime behavior.

The project should therefore be organized by **IDE family**, not by one-off scripts.

---

## Proposed Repository Structure

A possible future structure:

```text
DevCapsule/
  README.md
  docs/
    guides/
      docker4pycharm-ai-plugin-and-chatgpt-setup.md
  engineering-docs/
    design-notes/
      docker4pycharm/
        future-agent-refactoring-brief.md

  docker4ide/
    docker4ide.py
    docker4ide/
      __init__.py
      cli.py
      config.py
      image.py
      runtime.py
      mounts.py
      x11.py
      credentials.py
      templates.py

      ide/
        __init__.py
        base.py
        jetbrains.py
        vscode_family.py

    profiles/
      pycharm.yaml
      intellij.yaml
      vscode.yaml
      codium.yaml

    dockerfiles/
      base-dev.Dockerfile
      jetbrains.Dockerfile
      vscode-family.Dockerfile

  docker4pycharm/
    Dockerfile
    build-image.sh
    run-pycharm-container.sh

  docker4intellij/
    profile.yaml

  docker4vscode/
    profile.yaml

  docker4codium/
    profile.yaml

  vendor/
    extensions/
      README.md
```

The existing `docker4pycharm/` folder can remain as a compatibility layer or historical first implementation. Over time, its scripts should call the shared Python launcher rather than duplicating orchestration logic.

---

## Why Python for the Shared Launcher

The initial Bash scripts are suitable for a prototype, but the project will become easier to maintain with a Python orchestration layer.

Python is preferable because it can more cleanly handle:

- Argument parsing.
- Path normalization.
- Profile loading.
- YAML/JSON validation.
- Mount policy generation.
- Docker command construction.
- Secret handling.
- Per-IDE launch templates.
- Extension/plugin install workflows.
- Future testing.
- More precise error messages.
- Cross-distro behavior.

Bash should remain only as a thin convenience wrapper, for example:

```bash
./docker4pycharm/run-pycharm-container.sh --project ~/src/foo --ssh-agent
```

Internally, that wrapper could call:

```bash
python3 ../docker4ide/docker4ide.py run pycharm --project ~/src/foo --ssh-agent
```

---

## Proposed CLI Shape

The shared CLI should feel consistent across all IDEs:

```bash
docker4ide run pycharm  --project ~/src/foo --ssh-agent
docker4ide run intellij --project ~/src/foo --ssh-agent
docker4ide run vscode   --project ~/src/foo --ssh-agent
docker4ide run codium   --project ~/src/foo --ssh-agent
```

Potential build commands:

```bash
docker4ide build pycharm  --ide-archive /path/to/pycharm.tar.gz
docker4ide build intellij --ide-archive /path/to/idea.tar.gz
docker4ide build vscode   --ide-archive /path/to/code.tar.gz
docker4ide build codium   --ide-archive /path/to/codium.tar.gz
```

Potential extension/plugin commands:

```bash
docker4ide extensions list codium
docker4ide extensions install vscode openai.chatgpt
docker4ide extensions install codium ./vendor/extensions/openai-chatgpt.vsix
```

---

## Core Runtime Responsibilities

The shared runtime module should generate and execute the Docker invocation.

Common responsibilities:

```text
Project mount
IDE state mount
Plugin/extension mount
X11 socket mount
Temporary Xauthority handling
Optional SSH-agent forwarding
Optional GitHub token secret
Optional extra secret files
Read-only root filesystem
tmpfs mounts
Container user mapping
Native debugging mode
Network mode
Device passthrough where explicitly required
Explicit NVIDIA GPU workload profile for Python ML projects
Environment variable policy
Container naming
Image tagging
Cleanup of temporary host files
```

The runtime should keep the default security posture conservative.

GPU passthrough should be a deliberate profile-level capability, not a default
GUI/rendering workaround. The first GPU profile should assume NVIDIA hardware
and CUDA-oriented Python ML workflows, require the host NVIDIA container runtime
or equivalent Docker support, and document the resulting host-device exposure.

---

## Mount Policy

Default permitted mounts:

```text
/project
/ide-state
/ide-plugins or /ide-extensions
/tmp/.X11-unix, read-only
temporary Xauthority file, read-only
optional SSH agent socket
optional temporary secret files
```

Default forbidden mounts:

```text
$HOME
~/.ssh
~/.gitconfig
/var/run/docker.sock
/
host package caches
host Python virtual environments
arbitrary host source roots outside the selected project
```

Any additional mount should be explicit and justified.

---

## Credential Strategy

Do not bake credentials into images.

Do not mount host credential directories by default.

Supported credential transports should include:

```text
--ssh-agent
--github-token-env GITHUB_TOKEN
--git-name "User Name"
--git-email "user@example.com"
--secret NAME=ENV_VAR
--secret-file NAME=/path/to/file
```

Recommended behavior:

- SSH workflows should use agent forwarding.
- HTTPS GitHub workflows should use temporary secret-file mounting.
- Git identity can be configured inside the container-local HOME.
- Host `~/.ssh` and `~/.gitconfig` should not be mounted unless a future explicit unsafe/advanced option is added.

---

## Image Layering Strategy

Use shared image layers to avoid duplication.

Recommended image hierarchy:

```text
docker4ide/base-dev
  Ubuntu base
  Common Linux development packages
  Git and SSH client
  Debugging tools
  Networking tools
  X11/GTK/font/runtime dependencies
  Common user setup

docker4ide/jetbrains-base
  base-dev
  JetBrains runtime assumptions
  Shared JetBrains launcher support

docker4ide/pycharm
  jetbrains-base
  PyCharm payload

docker4ide/intellij
  jetbrains-base
  IntelliJ IDEA payload

docker4ide/vscode-family
  base-dev
  Electron/VS Code runtime dependencies
  Shared VS Code-family launcher support

docker4ide/vscode
  vscode-family
  Microsoft VS Code payload

docker4ide/codium
  vscode-family
  VSCodium payload
```

Common tools and libraries should be added only to `base-dev` wherever possible.

---

## Base Development Image Package Set

The first prototype used Ubuntu and installed the usual Linux development/debugging tools.

The shared base should continue to include tools similar to:

```text
git
openssh-client
curl
wget
ca-certificates
build-essential
gcc
g++
make
cmake
pkg-config
gdb
lldb
python3
python3-venv
python3-pip
netcat-openbsd
dnsutils
iproute2
iputils-ping
traceroute
procps
psmisc
lsof
strace
tcpdump
socat
telnet
whois
jq
ripgrep
fd-find
fzf
tree
less
vim-tiny
nano
unzip
zip
tar
xz-utils
fontconfig
X11/GTK/Electron runtime libraries
```

Package names may need per-distribution adjustment if the base image changes.

---

## IDE Family: JetBrains

Targets:

```text
pycharm
intellij
possibly webstorm
possibly clion
possibly rider
```

Shared behavior:

- IDE launched from `/opt/ide/bin/...`.
- Project path passed as `/project`.
- Persistent state defined through JetBrains property overrides.
- Plugins stored outside the image.
- User HOME set to a container-local persistent path such as `/ide-state/home`.

JetBrains path properties:

```properties
idea.config.path=/ide-state/config
idea.system.path=/ide-state/system
idea.plugins.path=/ide-plugins
idea.log.path=/ide-state/log
```

The launcher should inject these through a generated `idea.properties` file and set the appropriate environment variable for the IDE process.

Example launch:

```bash
/opt/ide/bin/pycharm.sh /project
```

or:

```bash
/opt/ide/bin/idea.sh /project
```

---

## JetBrains Profile Examples

PyCharm:

```yaml
id: pycharm
family: jetbrains
display_name: PyCharm
image: docker4ide/pycharm
binary: /opt/ide/bin/pycharm.sh

state:
  root: ~/.local/share/docker4ide/pycharm/state
  plugins: ~/.local/share/docker4ide/pycharm/plugins

jetbrains:
  properties:
    idea.config.path: /ide-state/config
    idea.system.path: /ide-state/system
    idea.plugins.path: /ide-plugins
    idea.log.path: /ide-state/log

launch:
  args:
    - /project

ai:
  preferred_plugin: JetBrains AI Assistant / Codex
```

IntelliJ IDEA:

```yaml
id: intellij
family: jetbrains
display_name: IntelliJ IDEA
image: docker4ide/intellij
binary: /opt/ide/bin/idea.sh

state:
  root: ~/.local/share/docker4ide/intellij/state
  plugins: ~/.local/share/docker4ide/intellij/plugins

jetbrains:
  properties:
    idea.config.path: /ide-state/config
    idea.system.path: /ide-state/system
    idea.plugins.path: /ide-plugins
    idea.log.path: /ide-state/log

launch:
  args:
    - /project

ai:
  preferred_plugin: JetBrains AI Assistant / Codex
```

---

## IDE Family: VS Code / VSCodium

Targets:

```text
vscode
codium
possibly cursor/windsurf later if desired
```

Shared behavior:

- Electron-based GUI under X11 initially.
- Project path passed as `/project`.
- User data stored outside the image.
- Extensions stored outside the image.
- Optional extension installation/bootstrap command.

VS Code-family launch pattern:

```bash
code-or-codium   --no-sandbox   --user-data-dir /ide-state/user-data   --extensions-dir /ide-extensions   /project
```

`--no-sandbox` may be required depending on the container runtime, Electron sandbox behavior, and user namespace configuration. Avoid weakening the sandbox unnecessarily if a cleaner configuration works.

---

## VS Code Profile Example

```yaml
id: vscode
family: vscode
display_name: Visual Studio Code
image: docker4ide/vscode
binary: code

state:
  root: ~/.local/share/docker4ide/vscode/state
  extensions: ~/.local/share/docker4ide/vscode/extensions

launch:
  args:
    - --no-sandbox
    - --user-data-dir=/ide-state/user-data
    - --extensions-dir=/ide-extensions
    - /project

extensions:
  marketplace: microsoft
  preferred_ai_extension: openai.chatgpt

ai:
  preferred_extension: OpenAI ChatGPT / Codex extension
  auth_notes:
    - ChatGPT sign-in may require browser redirect handling from inside the container.
```

---

## VSCodium Profile Example

```yaml
id: codium
family: vscode
display_name: VSCodium
image: docker4ide/codium
binary: codium

state:
  root: ~/.local/share/docker4ide/codium/state
  extensions: ~/.local/share/docker4ide/codium/extensions

launch:
  args:
    - --no-sandbox
    - --user-data-dir=/ide-state/user-data
    - --extensions-dir=/ide-extensions
    - /project

extensions:
  marketplace: open_vsx
  preferred_ai_extension: openai.chatgpt
  fallback_install:
    - vsix

ai:
  preferred_extension: OpenAI ChatGPT / Codex extension if compatible
  auth_notes:
    - VSCodium uses Open VSX by default.
    - Some Microsoft Marketplace extensions may not be directly available.
    - VSIX sideloading should be supported for pinned extensions.
    - ChatGPT/OAuth sign-in is likely the main testing risk.
```

---

## OpenAI / Codex / AI Plugin Notes

Current direction:

- JetBrains IDEs should use JetBrains AI Assistant with Codex support where available.
- VS Code should use OpenAI's VS Code-compatible extension / Codex integration where available.
- VSCodium should be treated as plausible but requiring validation.

Important caveats for the future agent:

1. VS Code is the safest target for official OpenAI extension compatibility.
2. VSCodium may require Open VSX availability or VSIX sideloading.
3. Authentication may be the largest practical issue:
   - ChatGPT browser sign-in from inside a container may not round-trip cleanly.
   - API-key-style authentication is easier to containerize.
   - Host browser redirect handling may require an explicit bridge.
4. Do not assume that a third-party extension named “ChatGPT” is safe or desirable.
5. Prefer official OpenAI or JetBrains-supported integrations.
6. Extension/plugin installation should support pinned versions and checksums.

---

## Extension and Plugin Strategy

JetBrains:

```text
Manual plugin installation first.
Later, optional plugin bootstrap by stable plugin IDs if reliable.
Keep plugins under /ide-plugins.
Do not bake user-installed plugins into the image.
```

VS Code / VSCodium:

```text
Support extension installation as a separate command.
Keep extensions under /ide-extensions.
Support Open VSX for VSCodium.
Support Microsoft Marketplace for VS Code where legally/technically appropriate.
Support local VSIX installation.
Support pinned VSIX checksums under vendor/extensions/.
```

Potential command examples:

```bash
docker4ide extensions install vscode ms-python.python
docker4ide extensions install vscode openai.chatgpt
docker4ide extensions install codium ./vendor/extensions/openai-chatgpt.vsix
```

---

## Security and Threat Model Notes

The project is an isolation helper, not a perfect sandbox.

Important risks:

```text
X11 is not a strong security boundary.
IDE plugins/extensions execute with substantial authority inside the container.
Mounted project files are writable by the IDE.
Credential forwarding must be tightly scoped.
Native debugging mode weakens the container.
Mounting docker.sock would effectively give host-level control.
```

Suggested future documentation section:

```text
Threat model
Known non-goals
Default safe mode
Advanced unsafe options
Credential handling
X11 risks
Extension/plugin supply-chain risks
```

Default stance:

- Minimize host mounts.
- Use read-only root filesystem where practical.
- Keep secrets ephemeral.
- Avoid privileged containers where Docker capability design permits.
- Treat Docker capability as a deliberate MVP exception for agent productivity.
  The current PyCharm default is host Docker socket access; true
  Docker-in-Docker remains an explicit option.
- Make default-on Docker capability explicit and noisy, and provide a clear
  opt-out.

---

## Compatibility Considerations

Initial target environment:

```text
Common Linux developer workstation
X11 session or XWayland under a desktop session
Distributions later than Ubuntu 22.04
systemd later than 249.x if systemd features are later introduced
Docker Engine available to the user
```

Do not assume:

```text
Wayland-only operation
Host home directory access
Host browser integration
Host SSH files
Host Docker socket as the only Docker-capability design
Kubernetes
Rootless Docker working perfectly
```

Possible future improvements:

```text
Wayland support
xpra support
VNC/noVNC support
Nested X server support
Rootless Docker support validation
Podman support
GPU/render acceleration
Host browser OAuth bridge
```

---

## Recommended Development Milestones

### R1: Introduce Shared Python CLI

Goals:

```text
Keep docker4pycharm working.
Introduce docker4ide.py.
Move shared Docker run logic into Python.
Add profiles/pycharm.yaml.
Add profiles/intellij.yaml.
Make docker4pycharm/run-pycharm-container.sh call docker4ide.py internally.
```

Deliverables:

```text
docker4ide/docker4ide.py
docker4ide/profiles/pycharm.yaml
docker4ide/profiles/intellij.yaml
basic schema validation
compatibility wrapper for PyCharm
```

---

### R2: Add IntelliJ

Goals:

```text
Build IntelliJ image using shared JetBrains base.
Launch IntelliJ through the same runtime path as PyCharm.
Validate persistent config/system/plugins/log paths.
Validate project-opening behavior.
Validate Git/SSH behavior.
```

Deliverables:

```text
docker4intellij/profile.yaml
JetBrains base Dockerfile
IntelliJ image build path
IntelliJ run command
```

---

### R3: Add VS Code

Goals:

```text
Add vscode-family.Dockerfile.
Add vscode.yaml.
Validate --user-data-dir persistence.
Validate --extensions-dir persistence.
Validate extension installation.
Validate Git/SSH behavior.
Validate GUI launch.
```

Deliverables:

```text
docker4ide/dockerfiles/vscode-family.Dockerfile
docker4ide/profiles/vscode.yaml
VS Code image build path
VS Code run command
```

---

### R4: Add VSCodium

Goals:

```text
Add codium.yaml.
Build VSCodium image.
Validate Open VSX extension installation.
Validate local VSIX installation.
Test OpenAI/Codex extension compatibility.
Test ChatGPT/OAuth authentication flow.
Document any limitations.
```

Deliverables:

```text
docker4ide/profiles/codium.yaml
VSCodium image build path
VSCodium run command
OpenVSX/VSIX install support
```

---

### R5: Formalize Documentation and Threat Model

Goals:

```text
Document security boundaries.
Document known risks.
Document extension/plugin trust model.
Document OAuth/browser limitations.
Document safe and unsafe flags.
Document per-IDE differences.
```

Deliverables:

```text
README.md update
SECURITY.md
docs/architecture.md
docs/profiles.md
docs/credentials.md
docs/extensions.md
```

---

## Testing Strategy

Add tests around command generation before adding complex runtime behavior.

Useful tests:

```text
profile parsing
profile schema validation
mount generation
forbidden mount rejection
Xauthority temporary file generation
SSH-agent option behavior
GitHub token secret option behavior
JetBrains launch command generation
VS Code-family launch command generation
debug-native flag behavior
read-only root behavior
```

Do not rely only on end-to-end manual GUI tests.

A practical split:

```text
Unit tests:
  Python command/mount/profile logic

Integration tests:
  docker run command starts
  container sees /project
  container sees /ide-state
  git works
  ssh-agent socket exists when enabled

Manual tests:
  GUI launch
  plugin installation
  AI authentication
  debugger behavior
```

---

## Implementation Principles for the Future Agent

1. Preserve the PyCharm baseline.
2. Do not break the existing `docker4pycharm` workflow while refactoring.
3. Move common behavior into Python before adding more IDEs.
4. Use declarative profiles for product-specific differences.
5. Group IDEs by family.
6. Keep images free of user credentials and mutable user state.
7. Keep plugin/extension state outside the image.
8. Treat VSCodium extension availability as a validation task, not an assumption.
9. Make unsafe options explicit.
10. Prefer additive migration over a large rewrite.

---

## Suggested First Task for the IDE Agent

Start with R1.

A good initial implementation task:

```text
Create docker4ide/docker4ide.py and supporting modules that can reproduce the current PyCharm docker run behavior from a pycharm.yaml profile, while keeping docker4pycharm/run-pycharm-container.sh as a compatibility wrapper.
```

Acceptance criteria:

```text
Existing PyCharm workflow still works.
The same project/state/plugin mounts are used.
SSH-agent forwarding still works.
GitHub token secret transport still works.
X11 launch still works.
No additional host directories are mounted.
The generated docker run command can be printed with --dry-run.
```

A useful CLI target:

```bash
python3 docker4ide/docker4ide.py run pycharm   --project ~/src/example   --ssh-agent   --dry-run
```

Then:

```bash
./docker4pycharm/run-pycharm-container.sh   --project ~/src/example   --ssh-agent
```

should internally delegate to the shared CLI.

---

## Final Direction

The future architecture should evolve from:

```text
one-off Docker/PyCharm scripts
```

to:

```text
a small profile-driven Docker IDE isolation framework
```

with the first supported families:

```text
JetBrains
VS Code-family
```

This keeps maintenance manageable, makes the security posture consistent, and allows new IDEs to be added mostly by writing a profile and a small family adapter rather than copying and modifying entire script trees.
