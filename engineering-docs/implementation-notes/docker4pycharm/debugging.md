# Debugging Notes: DockerForIDEIsolation / docker4pycharm

Recommended repository location:

```text
/project/engineering-docs/implementation-notes/docker4pycharm/debugging.md
```

This file is a handoff for the development agent running inside PyCharm/Codex inside the Dockerized IDE environment.

It captures the debugging work performed after the initial v0 `docker4pycharm` bootstrap, including what broke, what was changed or proposed, what appears fixed, and what remains to be validated or committed.

---

## Current Status

The Dockerized PyCharm environment now successfully reaches the AI/Codex/ChatGPT plugin path.

Confirmed by the user:

```text
Able to talk to the ChatGPT/Codex instance from inside PyCharm running inside the Docker container.
```

This means the broad architecture works:

```text
Host Linux desktop
  -> Docker container
    -> PyCharm GUI under X11
      -> AI/Codex/ChatGPT plugin
        -> outbound network/API access
```

The current running environment may include file changes and persistent IDE/container state changes made outside the IDE-side agent's current local view. The IDE-side agent should inspect the repository and compare against this document before assuming the repo already contains all fixes.

---

## Important Context for the IDE-Side Agent

The current IDE-side agent may be running inside the initial v0 container or a
close descendant of it.

Debugging was performed externally from a browser-based ChatGPT/Codex session.

Latest launcher update: the checked-in image and launcher now support Docker
from inside PyCharm. The default mode connects the IDE container to the host
Docker daemon through `/run/host-docker.sock`, while keeping PyCharm as the
mapped non-root IDE user. True Docker-in-Docker is still available as explicit
`--docker-in-docker` / `--dind`; in that mode the launcher starts the outer IDE
container with `--privileged`, and the entrypoint starts an inner `dockerd`
before dropping PyCharm back to the mapped IDE user. Disable Docker access with
`--no-docker` or `DOCKER_MODE=none`.

The inner daemon is intentionally started with bridge/iptables management
disabled because the outer PyCharm container uses host networking. For inner
builds that need network access, pass `--network host` to `build-image.sh`.

Important bootstrap limitation: an agent running in an older already-launched
container still may not have the current Docker mode until the PyCharm container
is relaunched through the updated launcher. Explicit DinD also requires the host
image to include the updated Dockerfile packages.

Therefore:

- Some repository files may already have been edited outside this session.
- Some persistent state may have changed outside Git.
- Some changes may have been applied manually to `Dockerfile`, launcher script, `entrypoint.sh`, or persistent IDE settings.
- The local IDE-side view may be incomplete until files are inspected.
- Non-file state must be reconstructed from this document.
- Build validation may require one more human host-side image rebuild before the
  IDE-side agent can validate Docker commands internally.

The user specifically wanted this document to prevent loss of context.

---

## Historical: Markdown Preview Blank / IDE GUI Hang

Status on 2026-06-20: this is no longer reproduced in the latest iterations and
has been removed from the active stabilization task list. The comparison note
for future recurrence lives in
`engineering-docs/completed-tasks/docker4pycharm/2026-06-20-markdown-preview-skiko-opengl-hang-retired.md`.

### Symptom

The user observed several times that opening a preview window for an `.md` file
inside the containerized PyCharm instance shows a blank preview. If the preview
is not closed quickly enough, the whole PyCharm GUI can become unresponsive.

This is a top-priority stabilization issue because this repository relies
heavily on Markdown handoff documents, and the behavior can interrupt the
human-to-agent loop.

### Captured Logs

Captured on 2026-06-19 during repeated interaction inside the containerized
PyCharm environment:

```text
2026-06-19 23:05:10,349 [ 363248]   WARN - #c.i.i.s.e.FeatureUsageData - Collectors should not reuse platform keys: current_file
MESA: error: Failed to query drm device.
glx: failed to create dri3 screen
failed to load driver: iris
[SKIKO] warn: Fallback to next API
org.jetbrains.skiko.RenderException: Cannot create OpenGL context
MESA: error: Failed to query drm device.
MESA: error: Failed to query drm device.
MESA: error: Failed to query drm device.
MESA: error: Failed to query drm device.
MESA: error: Failed to query drm device.
MESA: error: Failed to query drm device.
MESA: error: Failed to query drm device.
MESA: error: Failed to query drm device.
MESA: error: Failed to query drm device.
MESA: error: Failed to query drm device.
MESA: error: Failed to query drm device.
MESA: error: Failed to query drm device.
MESA: error: Failed to query drm device.
MESA: error: Failed to query drm device.
MESA: error: Failed to query drm device.
2026-06-19 23:08:47,699 [ 580598]   WARN - #org.intellij.plugins.markdown.ui.preview.MarkdownPreviewFileEditor$Companion - MarkdownPreviewFileEditor: panel is null, cannot update preview
MESA: error: Failed to query drm device.
MESA: error: Failed to query drm device.
MESA: error: Failed to query drm device.
MESA: error: Failed to query drm device.
2026-06-19 23:09:47,073 [ 639972]   WARN - #org.intellij.plugins.markdown.ui.preview.MarkdownPreviewFileEditor$Companion - MarkdownPreviewFileEditor: panel is null, cannot update preview
```

### Initial Hypothesis

This appears related to GPU/OpenGL context creation for the JetBrains Markdown
preview/Skiko rendering path, not merely the earlier missing `libGL.so.1`
package issue. The image now includes Mesa/OpenGL runtime libraries, but the
runtime still cannot query a DRM device and Mesa attempts to load the `iris`
driver before Skiko reports that it cannot create an OpenGL context.

The next agent should investigate whether the right mitigation is to force a
software rendering path for JetBrains/Skiko/Markdown preview, expose a narrow
DRI/render device explicitly, adjust Mesa environment variables, or disable the
problematic preview rendering mode. Any change must preserve the working
AI/Codex path and remain explicit in the launcher/docs.

### 2026-06-22 Runtime Update

The image dependency side is now separate from the runtime rendering path:

- `libgl1`, `libglx-mesa0`, `libgl1-mesa-dri`, and `mesa-utils` are present in
  the Dockerfile package list.
- `ldd /opt/pycharm/lib/skiko-awt-runtime-all/libskiko-linux-x64.so` resolves
  `libGL.so.1`; the earlier missing-library failure is not the current issue.
- Running `glxinfo -B` without Mesa overrides reproduces the noisy
  `Failed to query drm device`, `failed to create dri3 screen`, and
  `failed to load driver: iris` path.
- Running with `LIBGL_ALWAYS_SOFTWARE=1`,
  `MESA_LOADER_DRIVER_OVERRIDE=llvmpipe`, and `LIBGL_DRI3_DISABLE=1` removes
  that noise while still producing a Mesa `llvmpipe` OpenGL context.

The launcher, entrypoint, and Dockerfile now default to that software GL path.
This keeps the current no-`/dev/dri` isolation posture. If hardware GL is later
needed, add it as an explicit launcher option with documented device passthrough
rather than quietly mounting host GPU devices.

### 2026-06-22 Manual Validation Status

After the fresh image was tested again, the user reported that everything looks
OK now. Treat the Markdown preview / Skiko OpenGL context investigation as
closed for the current v0 image. Reopen only if Markdown preview becomes blank
or unresponsive again, or if logs again show active `Cannot create OpenGL
context` failures under the default launcher path.

Retrospective note:
`engineering-docs/completed-tasks/docker4pycharm/2026-06-22-mesa-skiko-markdown-validation.md`.

### Historical Validation Checklist

- Open this repository in the containerized PyCharm instance.
- Open a Markdown file such as `README.md`.
- Open the Markdown preview and leave it open long enough to reproduce or rule
  out the GUI freeze.
- Run `docker4ide-check-runtime-deps` inside the launched container.
- Check PyCharm logs for `MESA`, `dri3`, `iris`, `Cannot create OpenGL context`,
  `SKIKO`, and `MarkdownPreviewFileEditor`.
- Test candidate mitigations one at a time and document both the launcher/image
  change and the observed PyCharm behavior.

---

## Initial Project Goal

The project is intended to run IDEs in Docker with a tight host exposure policy.

The first target is PyCharm.

Core goals:

- Run PyCharm isolated in Docker.
- Preserve most IDE functionality.
- Support future AI plugins such as Claude, Codex, OpenAI, or JetBrains AI Assistant.
- Keep IDE configuration and plugins persistent outside the image.
- Mount exactly one project directory into the container.
- Avoid mounting host `$HOME`, `~/.ssh`, `~/.gitconfig`, or other broad host directories.
- Provide common Linux development/debugging tools inside the container.
- Support GitHub access through explicit credential transport such as SSH agent forwarding or token secret mounting.
- Run from a common Linux/X11 developer environment.
- Prefer a scriptable launcher over a hand-maintained `docker start` container where dynamic mounts are needed.

---

## Initial v0 Architecture

The initial generated files were:

```text
docker4pycharm/
  Dockerfile
  build-image.sh
  run-pycharm-container.sh
  entrypoint.sh
  README.md
```

The project root also later received documentation files:

```text
README.md
docs/guides/docker4pycharm-ai-plugin-and-chatgpt-setup.md
engineering-docs/design-notes/docker4pycharm/future-agent-refactoring-brief.md
```

The intended persistent host-side state roots were:

```text
~/.local/share/pycharm-docker/state
~/.local/share/pycharm-docker/plugins
```

Inside the container:

```text
/project
/ide-state
/ide-plugins
```

JetBrains path overrides were configured through an `idea.properties` file:

```properties
idea.config.path=/ide-state/config
idea.system.path=/ide-state/system
idea.plugins.path=/ide-plugins
idea.log.path=/ide-state/log
```

The container HOME was intended to be local to the persistent IDE state, e.g.:

```text
HOME=/ide-state/home
```

Default mount policy:

```text
Allowed:
  /project
  /ide-state
  /ide-plugins
  X11 socket/auth
  optional SSH agent socket
  optional temporary secret files

Forbidden by default:
  host $HOME
  ~/.ssh
  ~/.gitconfig
  /var/run/docker.sock
  arbitrary host roots
```

---

## Build-Time Network Failure

### Symptom

On the user's laptop, the Docker image build failed because `apt-get` and other outbound network calls inside the build could not reach the outside world.

The suspected cause was a host Linux firewall/network configuration issue that broke the default Docker build network path.

### Fix / Workaround

Use host networking during Docker build.

For classic Docker build:

```bash
docker build --network=host -t docker4ide/pycharm .
```

For Buildx:

```bash
docker buildx build --network=host -t docker4ide/pycharm --load .
```

If BuildKit/buildx rejects host networking due to missing privileged entitlement:

```bash
docker buildx build \
  --network=host \
  --allow network.host \
  -t docker4ide/pycharm \
  --load \
  .
```

### Suggested Script Patch

Add a configurable build-network option to `build-image.sh`.

Example pattern:

```bash
DOCKER_BUILD_NETWORK="${DOCKER_BUILD_NETWORK:-default}"

docker build \
  --network="${DOCKER_BUILD_NETWORK}" \
  -t "${IMAGE_TAG}" \
  .
```

Usage:

```bash
DOCKER_BUILD_NETWORK=host ./build-image.sh --pycharm /path/to/pycharm.tar.gz
```

### Current Script Status

`docker4pycharm/build-image.sh` now supports both:

```bash
DOCKER_BUILD_NETWORK=host ./build-image.sh --pycharm /path/to/pycharm.tar.gz
./build-image.sh --network host --pycharm /path/to/pycharm.tar.gz
```

The default build network is `default`; host networking is no longer hard-coded.
When `host` is selected, the script also passes the BuildKit entitlement:

```bash
--allow network.host
```

### Remaining Validation

Rebuild once on the user's laptop with the normal default network and, if that
still fails, rebuild with:

```bash
./build-image.sh --network host --pycharm /path/to/pycharm.tar.gz
```

Acceptance criteria:

- Default behavior uses Docker's normal build network.
- Host networking can be enabled explicitly.
- Buildx usage is documented if/when used.
- The option is mentioned in README/debugging docs.

---

## AI Plugin First Failure: Duplicate JetBrains ML Features

### Symptom

API key configuration succeeded. The test connection button showed success with a green check.

But sending a message from the chat window produced no GUI output and logged this stack trace:

```text
SEVERE - #c.i.m.i.c.i.c.ControlModel - com.jetbrains.mlapi.feature.FeatureSelector@... has produced duplicate features:
  {postprocessing_before_filter_model.analyze_time=[
    Int64FeatureHolder(int64Value=1, signature=postprocessing_before_filter_model.analyze_time(Int64)),
    Int64FeatureHolder(int64Value=0, signature=postprocessing_before_filter_model.analyze_time(Int64))
  ]}

java.lang.IllegalArgumentException: com.jetbrains.mlapi.feature.FeatureSelector@... has produced duplicate features
  at com.jetbrains.mlapi.feature.FeatureSelector.removeRedundantFeatures(FeatureSelector.kt:73)
  at com.jetbrains.mlapi.feature.FeatureSelector.selectFeatureList(FeatureSelector.kt:15)
  at com.jetbrains.mlapi.feature.FeatureProvider.provideFeatures(FeatureProvider.kt:49)
  at com.intellij.fullLine.controlModel.MLApiControlModel.predict$suspendImpl(MLApiControlModel.kt:44)
  at com.intellij.fullLine.controlModel.MLApiControlModel.predict(MLApiControlModel.kt)
```

### Diagnosis

This looked less like an API-key/network issue and more like a JetBrains IDE/plugin runtime problem.

The significant packages were:

```text
com.intellij.fullLine.controlModel.MLApiControlModel
com.jetbrains.mlapi.feature.FeatureSelector
postprocessing_before_filter_model.analyze_time
```

Hypothesis:

- The failing path was JetBrains Full Line / inline completion / ML feature selection.
- The IDE-side ML feature selector produced duplicate feature keys with conflicting values.
- This may have been triggered by a plugin interaction, stale IDE state, or a bug in bundled Full Line Code Completion / AI Assistant integration.
- It was probably not caused by provider authentication, because API-key test already succeeded.

### Recommended Workaround

Disable JetBrains Full Line Code Completion / inline completion features.

Possible places to inspect:

```text
Settings
  -> Editor
  -> General
  -> Inline Completion
```

and:

```text
Settings
  -> Plugins
  -> Installed
  -> Full Line Code Completion
```

Potentially disable overlapping completion/AI plugins during debugging:

```text
GitHub Copilot
Continue
Tabnine
Codeium
Claude-specific plugin
JetBrains Full Line Code Completion
JetBrains AI inline completion / next edit suggestions
```

Then restart the IDE.

### Current Status

After subsequent restart and fixes, the user reports successful connection from inside PyCharm, so this may be resolved, bypassed, or masked by later fixes.

### Next Task

The IDE-side agent should check:

- Whether Full Line Code Completion is enabled.
- Whether any settings were changed in persistent IDE state.
- Whether the duplicate-feature error still appears in the latest logs.

If it is still present but non-fatal, document it as a known issue.

---

## Restart Failure: Missing `libGL.so.1`

### Symptom

After restarting the IDE, the log showed:

```text
error: XDG_RUNTIME_DIR is invalid or not set in the environment.
[warning][cds] Archived non-system classes are disabled because the java.system.class.loader property is specified

(java:6): dbind-WARNING **: Couldn't connect to accessibility bus:
Failed to connect to socket /run/user/1000/at-spi/bus_1: No such file or directory

WARN - #c.i.p.instanceContainer - InstanceNotOverridableException: ...
WARN - #c.i.m.l.t.AIAssistantTelemetryExporterKt - No Langfuse auth string found.

SEVERE - #kotlinx.coroutines.CoroutineScope - Failed to preload Skiko
java.lang.UnsatisfiedLinkError:
/opt/pycharm/lib/skiko-awt-runtime-all/libskiko-linux-x64.so:
libGL.so.1: cannot open shared object file: No such file or directory
```

### Diagnosis

The actionable failure was:

```text
libGL.so.1: cannot open shared object file: No such file or directory
```

This means the image was missing OpenGL/Mesa runtime libraries required by JetBrains' Skiko/Skia UI components.

The missing native library plausibly explained why the AI/chat UI could fail or silently render nothing.

### Dockerfile Fix

Add OpenGL/Mesa runtime packages to the GUI dependency block.

Recommended Ubuntu/Debian packages:

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglx-mesa0 \
    libgl1-mesa-dri \
    mesa-utils \
 && rm -rf /var/lib/apt/lists/*
```

Broader GUI dependency set suggested:

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglx-mesa0 \
    libgl1-mesa-dri \
    mesa-utils \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxtst6 \
    libxi6 \
    libxrandr2 \
    libxss1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon-x11-0 \
    libgtk-3-0 \
    libnss3 \
    libatspi2.0-0 \
 && rm -rf /var/lib/apt/lists/*
```

Audio package name depends on base OS:

```text
Ubuntu 24.04:
  libasound2t64

Ubuntu 22.04 / some Debian variants:
  libasound2
```

### Verification Command

Inside the container or a shell in the built image:

```bash
ldd /opt/pycharm/lib/skiko-awt-runtime-all/libskiko-linux-x64.so | grep -i "not found\|libGL"
```

Before fix, expected:

```text
libGL.so.1 => not found
```

After fix, `libGL.so.1` should resolve to a valid path.

Alternative package check:

```bash
dpkg -S /usr/lib/x86_64-linux-gnu/libGL.so.1 2>/dev/null || find /usr/lib -name 'libGL.so.1*'
```

### Current Status

After the OpenGL/Mesa issue was addressed and the IDE restarted, the user confirmed that the AI connection works.

### Next Task

Inspect the Dockerfile and confirm that the Mesa/OpenGL packages are committed.

If not present, add them.

Then rebuild and run:

```bash
ldd /opt/pycharm/lib/skiko-awt-runtime-all/libskiko-linux-x64.so | grep -i "not found\|libGL"
```

Acceptance criteria:

- No `libGL.so.1 => not found`.
- No `Failed to preload Skiko` severe error.
- AI/Codex chat UI remains functional after a clean container restart.

---

## Runtime Warning: `XDG_RUNTIME_DIR`

### Symptom

Log showed:

```text
error: XDG_RUNTIME_DIR is invalid or not set in the environment.
```

### Diagnosis

Expected in many containers because there is no normal systemd user session.

May be non-fatal, but modern GUI libraries and Electron/GTK/JetBrains components expect a valid runtime dir.

### Suggested `entrypoint.sh` Fix

Add:

```bash
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/tmp/runtime-${USER:-ideuser}}"
mkdir -p "$XDG_RUNTIME_DIR"
chmod 700 "$XDG_RUNTIME_DIR"
```

Alternative if `/run` is tmpfs and writable:

```bash
export XDG_RUNTIME_DIR=/run/user/1000
mkdir -p "$XDG_RUNTIME_DIR"
chmod 700 "$XDG_RUNTIME_DIR"
```

The `/tmp` option is simpler and fits the existing read-only-root + tmpfs design.

### Next Task

Inspect `entrypoint.sh`.

If not present, add the `XDG_RUNTIME_DIR` setup.

Acceptance criteria:

- The warning disappears or is reduced.
- `$XDG_RUNTIME_DIR` exists and is writable inside the container.
- Permissions are `0700`.

Validation:

```bash
echo "$XDG_RUNTIME_DIR"
ls -ld "$XDG_RUNTIME_DIR"
test -w "$XDG_RUNTIME_DIR"
```

---

## Runtime Warning: Accessibility Bus / `dbind`

### Symptom

Log showed:

```text
dbind-WARNING **: Couldn't connect to accessibility bus:
Failed to connect to socket /run/user/1000/at-spi/bus_1: No such file or directory
```

### Diagnosis

GTK accessibility integration could not find a session accessibility bus.

Usually non-fatal unless accessibility/screen-reader integration is required.

### Suggested Fix / Suppression

In `entrypoint.sh`, add:

```bash
export NO_AT_BRIDGE="${NO_AT_BRIDGE:-1}"
```

This suppresses accessibility bridge attempts.

### Next Task

Add this to `entrypoint.sh` if not already present.

Acceptance criteria:

- Warning disappears or is reduced.
- IDE still starts.
- No impact on AI chat or normal IDE behavior.

---

## Warnings Deprioritized for Now

The following warnings were seen but are not currently considered root causes.

### JVM CDS Warning

```text
Archived non-system classes are disabled because the java.system.class.loader property is specified
```

Likely benign JetBrains JVM/classloader behavior.

### Langfuse Warning

```text
No Langfuse auth string found.
```

Likely telemetry/exporter-related, not a core provider failure.

### Java Unsafe Warning

```text
WARNING: sun.misc.Unsafe::allocateMemory has been called by io.netty...
```

Future-deprecation warning from Netty/JVM; noisy but likely non-fatal.

### JetBrains Instance Override Warnings

```text
InstanceNotOverridableException: Override failed for ...
```

Possibly internal JetBrains plugin/service warnings. Defer unless symptoms persist.

---

## Current Working Hypothesis

The main blocking issue after restart was missing GUI/native runtime dependencies, specifically `libGL.so.1`.

Once OpenGL/Mesa runtime libraries were added, the JetBrains Skiko preload issue should have been resolved, enabling the AI chat UI to work.

Secondary cleanup items:

- Set `XDG_RUNTIME_DIR`.
- Suppress accessibility bus warning if accessibility integration is not needed.
- Confirm Full Line Code Completion is not still causing duplicate-feature crashes.
- Document the build-time `--network=host` workaround.

---

## Commands to Preserve

### Build With Host Networking

```bash
docker build --network=host -t docker4ide/pycharm .
```

or:

```bash
docker buildx build --network=host --allow network.host -t docker4ide/pycharm --load .
```

### Build Through Script With Environment Variable

```bash
DOCKER_BUILD_NETWORK=host ./build-image.sh --pycharm /path/to/pycharm.tar.gz
```

### Verify Skiko Native Dependencies

```bash
ldd /opt/pycharm/lib/skiko-awt-runtime-all/libskiko-linux-x64.so | grep -i "not found\|libGL"
```

### Verify Runtime Directory

```bash
echo "$XDG_RUNTIME_DIR"
ls -ld "$XDG_RUNTIME_DIR"
test -w "$XDG_RUNTIME_DIR"
```

### Verify Important Writable Paths

```bash
test -w /ide-state
test -w /ide-state/config
test -w /ide-state/system
test -w /ide-state/log
test -w /ide-plugins
test -w "$HOME"
```

### Expected HOME

```bash
echo "$HOME"
```

Expected:

```text
/ide-state/home
```

---

## Files to Inspect Next

The IDE-side agent should inspect at least:

```text
docker4pycharm/Dockerfile
docker4pycharm/build-image.sh
docker4pycharm/run-pycharm-container.sh
docker4pycharm/entrypoint.sh
README.md
docs/guides/docker4pycharm-ai-plugin-and-chatgpt-setup.md
engineering-docs/design-notes/docker4pycharm/future-agent-refactoring-brief.md
```

Potential new file location:

```text
engineering-docs/implementation-notes/docker4pycharm/debugging.md
```

---

## Concrete Next Tasks

### Task 1: Commit Missing Runtime Dependencies

Inspect `docker4pycharm/Dockerfile`.

Ensure the GUI dependency block contains:

```text
libgl1
libglx-mesa0
libgl1-mesa-dri
mesa-utils
```

Also ensure the broader X11/GTK dependencies remain present.

### Task 2: Add Runtime Environment Setup

Inspect `docker4pycharm/entrypoint.sh`.

Ensure it contains:

```bash
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/tmp/runtime-${USER:-ideuser}}"
mkdir -p "$XDG_RUNTIME_DIR"
chmod 700 "$XDG_RUNTIME_DIR"

export NO_AT_BRIDGE="${NO_AT_BRIDGE:-1}"
```

### Task 3: Add Build Network Option

Inspect `docker4pycharm/build-image.sh`.

Add support for:

```bash
DOCKER_BUILD_NETWORK=host
```

and preferably:

```bash
--network host
```

### Task 4: Add Verification Target or Script

Consider adding a helper:

```bash
docker4pycharm/check-runtime-deps.sh
```

Suggested checks:

```bash
ldd /opt/pycharm/lib/skiko-awt-runtime-all/libskiko-linux-x64.so | grep -i "not found"
echo "$XDG_RUNTIME_DIR"
test -w "$XDG_RUNTIME_DIR"
test -w /ide-state
test -w /ide-plugins
```

### Task 5: Update Documentation

Update `docker4pycharm/README.md` and/or root `README.md` with:

- `--network=host` build workaround.
- Missing `libGL.so.1` diagnosis.
- `XDG_RUNTIME_DIR` container setup.
- AI plugin debugging notes.
- Recommended check commands.

### Task 6: Check AI Plugin Persistent State

From inside PyCharm, check:

- Which AI plugin is installed.
- Whether it is JetBrains AI Assistant, Codex, OpenAI ChatGPT extension/plugin, Claude plugin, or another provider.
- Whether Full Line Code Completion is enabled.
- Whether the duplicate-feature error still appears in logs.

### Task 7: Preserve Current Working Configuration

Because the user has a now-working configuration, avoid destructive changes to persistent state.

Before resetting state, back up:

```bash
~/.local/share/pycharm-docker/state
~/.local/share/pycharm-docker/plugins
```

or the actual state/plugin paths configured by the launcher.

---

## Known Good Milestone

A working milestone has been reached when:

```text
PyCharm starts inside Docker.
The project opens.
The AI/Codex/ChatGPT plugin can send and receive messages.
The build can complete on the user's laptop using host networking if needed.
Skiko no longer fails to load due to missing libGL.so.1.
The runtime environment defines a valid XDG_RUNTIME_DIR.
```

This milestone should be captured in Git once the corresponding Dockerfile and script changes are verified.

---

## Do Not Regress

Do not solve these issues by weakening isolation unnecessarily.

Avoid in the strict `--no-docker` profile:

```text
Mounting host $HOME
Mounting ~/.ssh
Mounting ~/.gitconfig
Mounting /var/run/docker.sock
Disabling read-only root without a reason
Baking secrets into the image
Baking user IDE state into the image
```

The default MVP profile now mounts the host Docker socket. This keeps the
outer IDE container non-root, read-only, and capability-dropped, but it gives
IDE-side tools broad control over host Docker state. True Docker-in-Docker is
an explicit exception that runs the outer IDE container with `--privileged` and
a writable root filesystem. Do not re-enable inner Docker bridge/iptables
management while the outer container uses host networking.

Acceptable targeted changes:

```text
Add required GUI runtime libraries.
Add XDG_RUNTIME_DIR setup.
Mount explicit X11 transport/auth.
Forward SSH agent only when requested.
Mount token secrets only as temporary files.
Use --network=host only for build when explicitly requested.
```

---

## Suggested Commit Message

If the Dockerfile/script fixes are applied, a good commit message would be:

```text
Fix PyCharm container GUI deps and build networking escape hatch

- Add Mesa/OpenGL libraries required by JetBrains Skiko runtime
- Initialize XDG_RUNTIME_DIR in the container entrypoint
- Suppress accessibility bus warnings with NO_AT_BRIDGE
- Add configurable Docker build network mode for firewall-constrained hosts
- Document AI plugin debugging and runtime dependency checks
```

---

## Final Note for the IDE-Side Agent

The system now works at least once end-to-end for AI chat from inside the Dockerized PyCharm instance.

Your job is not to redesign from scratch.

Your first job is to inspect the repository, identify which of these fixes are already present, make missing fixes explicit in files, and preserve the working configuration while improving reproducibility.
