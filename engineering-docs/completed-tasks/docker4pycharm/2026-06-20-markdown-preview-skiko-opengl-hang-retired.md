# Completed Task: Markdown Preview Skiko/OpenGL Hang Retired

Date: 2026-06-20

Status: retired because it is not currently reproduced in the latest
iterations.

## Original Task

Investigate and fix the PyCharm Markdown preview blank/hang issue before
broader refactoring, while preserving the working AI/Codex path.

## Done Means

- The issue no longer appears in current use.
- The active v0 task list no longer tells future agents to investigate it by
  default.
- Historical symptoms and log signatures are preserved for comparison if it
  returns.

## Verification

The user reported that the issue appears to have disappeared in current
iterations.

## Environment Provenance

- Project: `docker4pycharm` v0/MVP.
- Original capture date: 2026-06-19.
- Retired date: 2026-06-20.
- Runtime context: containerized PyCharm under X11.

## Original Symptom

Opening a preview window for an `.md` file inside the containerized PyCharm
instance showed a blank preview. If the preview was not closed quickly enough,
the whole PyCharm GUI could become unresponsive.

This was disruptive because the repository relies heavily on Markdown handoff
documents.

## Captured Log Signatures

Captured during repeated interaction inside the containerized PyCharm
environment:

```text
MESA: error: Failed to query drm device.
glx: failed to create dri3 screen
failed to load driver: iris
[SKIKO] warn: Fallback to next API
org.jetbrains.skiko.RenderException: Cannot create OpenGL context
MarkdownPreviewFileEditor: panel is null, cannot update preview
```

## Original Hypothesis

The failure appeared related to GPU/OpenGL context creation for the JetBrains
Markdown preview / Skiko rendering path, not merely to the earlier missing
`libGL.so.1` package issue.

Candidate mitigations considered at the time:

- Force a software rendering path for JetBrains/Skiko/Markdown preview.
- Expose a narrow DRI/render device explicitly.
- Adjust Mesa environment variables.
- Disable or change the problematic Markdown preview rendering mode.

Any future mitigation should preserve the working AI/Codex path and keep host
exposure explicit in the launcher and docs.

## Reopen If

- Markdown preview again renders blank in the containerized PyCharm instance.
- The PyCharm GUI becomes unresponsive after opening Markdown preview.
- Logs again show `MESA`, `dri3`, `iris`, `Cannot create OpenGL context`,
  `SKIKO`, or `MarkdownPreviewFileEditor` errors around preview rendering.
