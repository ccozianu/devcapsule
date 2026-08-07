# Decision: Default JetBrains GL To Mesa Software Rendering

Date: 2026-06-22

Status: implemented and manually validated for the current v0 image

## Context

The Dockerized PyCharm runtime again logged:

```text
MESA: error: Failed to query drm device.
glx: failed to create dri3 screen
failed to load driver: iris
org.jetbrains.skiko.RenderException: Cannot create OpenGL context
```

The earlier missing-library issue was already fixed: the image has Mesa/OpenGL
packages installed and `libskiko-linux-x64.so` resolves `libGL.so.1`.

The current warning class comes from Mesa attempting a hardware DRI path inside
the container. The default runtime does not mount host `/dev/dri` devices, so
that probe is expected to fail or fall back.

## Decision

Default the launcher, entrypoint, and image environment to Mesa software GL:

```text
LIBGL_ALWAYS_SOFTWARE=1
MESA_LOADER_DRIVER_OVERRIDE=llvmpipe
LIBGL_DRI3_DISABLE=1
```

Expose launcher overrides through:

```text
PYCHARM_LIBGL_ALWAYS_SOFTWARE
PYCHARM_MESA_LOADER_DRIVER_OVERRIDE
PYCHARM_LIBGL_DRI3_DISABLE
```

Add `docker4ide-check-runtime-deps` to future images and keep the same
helper available in the repository as `docker4pycharm/check-runtime-deps.sh`.

## Verification

Completed static/live checks in the current container:

```bash
dpkg -l libgl1 libglx-mesa0 libgl1-mesa-dri mesa-utils
ldd /opt/pycharm/lib/skiko-awt-runtime-all/libskiko-linux-x64.so | rg -i 'not found|libGL'
glxinfo -B
LIBGL_ALWAYS_SOFTWARE=1 MESA_LOADER_DRIVER_OVERRIDE=llvmpipe LIBGL_DRI3_DISABLE=1 glxinfo -B
```

Observed result:

- The Mesa packages are installed.
- `libGL.so.1` resolves for Skiko.
- Plain `glxinfo -B` reproduces the `drm` / `dri3` / `iris` warning path.
- The software-GL environment removes those warnings and reports Mesa
  `llvmpipe`.

Original manual validation plan:

- Relaunch PyCharm through the updated launcher or rebuilt image.
- Run `docker4ide-check-runtime-deps` in the launched container.
- Open Markdown preview and confirm the IDE stays responsive.
- Inspect `/ide-project-state/log` for absence of the OpenGL warning signatures
  during normal preview use.

Manual validation update on 2026-06-22:

- The user reported that `Failed to query drm device` appears to have
  disappeared in the latest image.
- At that point, logs still included `[SKIKO] warn: Fallback to next API`
  followed by `org.jetbrains.skiko.RenderException: Cannot create OpenGL
  context`.
- At that point, the Mesa hardware-probe warning was treated as improved, while
  the remaining Skiko OpenGL context failure stayed active until the follow-up
  validation below.

Follow-up manual validation update on 2026-06-22:

- After the fresh image was tested again, the user reported that everything
  looks OK now.
- Treat the default Mesa software-GL path, Markdown preview behavior, and the
  related Skiko/OpenGL logging as accepted for the current v0 image.
- The active Skiko/OpenGL context failure item has been removed from the root
  README handoff. Retrospective note:
  `completed-tasks/2026-06-22-mesa-skiko-markdown-validation.md`.

Deferred GPU passthrough note:

- Do not use NVIDIA or `/dev/dri` passthrough as the next rendering fix.
- Preserve GPU passthrough for a later explicit developer-workload profile,
  especially for Python ML projects on hosts with NVIDIA hardware.
- Treat that future profile as a documented host-exposure relaxation, not as
  part of the v0 default rendering path.
- The first GPU profile should assume NVIDIA because the current motivating
  host has an NVIDIA GA107M / GeForce RTX 3050 Mobile and Python ML workloads
  are a more compelling use case than IDE rendering.

## Consequences

The default remains compatible with the isolation model because no additional
host GPU devices are mounted.

Rendering is software-based, so graphics-heavy IDE surfaces may be slower than
hardware acceleration. That is acceptable for the v0 default because PyCharm is
currently X11-forwarded and the priority is stable, reproducible behavior with
limited host exposure.

## Reopen If

Reopen if Markdown preview becomes blank or unresponsive again, if Skiko or
Markdown preview again logs OpenGL context failures under the default launcher
path, if a future change removes the Mesa software-GL defaults, or if the
project decides to add explicit GPU device passthrough.
