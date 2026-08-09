# Completed Task: Mesa/Skiko Markdown Preview Validation

Date: 2026-06-22

Status: manually validated

## Original Task

Investigate the remaining Skiko OpenGL context failure after the fresh Mesa
software-GL launch.

## Done Means

Markdown preview remains usable, the IDE stays responsive, and IDE logs no
longer show active `[SKIKO] warn: Fallback to next API` followed by
`org.jetbrains.skiko.RenderException: Cannot create OpenGL context` during
normal preview use under the default launcher path.

## Verification

The user manually tested the latest image again and reported that everything
looks OK now.

Earlier in the same stabilization pass, the Mesa hardware-probe warning
(`Failed to query drm device` / `dri3` / `iris`) had already appeared improved.
The follow-up manual validation closes the remaining Skiko/OpenGL context item
for the current v0 image.

## Environment Provenance

- Date validated: 2026-06-22.
- Target: `docker4pycharm` v0/MVP.
- Rendering path: default Mesa `llvmpipe` software GL.
- Host GPU passthrough: not used.
- Validation source: user manual GUI/log observation after a fresh image test.

## Retrospective Notes

Keep the default software-GL posture. Do not add `/dev/dri`, NVIDIA, or other
GPU passthrough as an IDE-rendering fix for v0. GPU passthrough remains deferred
for a later explicit developer-workload profile, especially Python ML projects
that need NVIDIA/CUDA access.

## Reopen If

Reopen if Markdown preview becomes blank or unresponsive again, if logs again
show active Skiko/OpenGL context failures under the default launcher path, if
software-GL defaults regress, or if a future change makes hardware GPU
passthrough part of the runtime.
