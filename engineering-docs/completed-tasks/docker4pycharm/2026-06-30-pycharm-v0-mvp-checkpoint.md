# PyCharm V0 MVP Checkpoint

Date: 2026-06-30

Requirements:

- R-ENV-001
- R-STATE-001
- R-SCOPE-001
- R-DEV-001
- R-GIT-001
- R-DOCKER-001
- R-PROJECT-001
- R-CONC-001
- R-PROC-001

Status: accepted by the user as MVP

## Summary

The user accepted the current `docker4pycharm` v0 state as the MVP checkpoint.
The remaining local Git identity edge-case validation was completed immediately
before this checkpoint, including opt-out behavior and explicit missing-host
identity warnings.

The current MVP includes:

- Dockerized PyCharm launch through the existing shell wrapper.
- Persistent PyCharm state, per-project runtime state, and plugins outside the
  image.
- Per-project default mount paths under `/workspace/<project-id>`.
- Default host Docker socket passthrough as an explicit productivity exception,
  with true Docker-in-Docker and no-Docker profiles still available.
- Mesa software OpenGL defaults for the v0 X11 GUI path.
- Common development tooling and explicit `--dev-sudo` support.
- Local Git author identity handling without mounting host `~/.gitconfig`.
- Repo-local human/agent process documentation and bootstrap support.

GitHub SSH and HTTPS remote credential validation remains deferred until after
the post-MVP refactoring.

## Next Direction

Begin the post-MVP refactor described in
`engineering-docs/design-notes/docker4pycharm/future-agent-refactoring-brief.md`:
move reusable launcher/runtime behavior into a Python `docker4ide` framework
while preserving the current PyCharm MVP wrapper path.

## Reopen If

Reopen the MVP checkpoint only if the current PyCharm wrapper no longer starts
the IDE successfully for the documented v0 profiles, or if a refactor changes
the default mount/security posture without matching documentation and
validation.
