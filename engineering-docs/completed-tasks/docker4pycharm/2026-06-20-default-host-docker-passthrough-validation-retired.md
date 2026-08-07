# Completed Task: Default Host Docker Passthrough Validation Retired

Date: 2026-06-20

Status: removed from active v0 tracking.

## Original Task

Relaunch the image from the host and validate that `docker info` reaches the
host daemon in the default launcher mode.

## Done Means

- The default Docker mode is documented as host Docker daemon passthrough.
- The active task list no longer asks future agents to repeat this validation
  unless the default Docker path changes.
- The implementation note records how default Docker access is expected to
  behave.

## Verification

This was retired by user direction during v0 stabilization. The documented
developer-facing behavior remains:

```text
docker ps inside PyCharm == docker ps on the host
```

## Environment Provenance

- Project: `docker4pycharm` v0/MVP.
- Date retired: 2026-06-20.
- Runtime mode: default `DOCKER_MODE=host`.
- Docker socket path in container: `/run/host-docker.sock`.
- `DOCKER_HOST`: `unix:///run/host-docker.sock`.

## Retrospective Notes

Default host Docker passthrough is a deliberate MVP productivity exception. It
gives tools inside PyCharm/Codex broad control over host Docker state, so it
must remain explicit in the docs and launcher warnings.

## Reopen If

- A later image, launcher, or entrypoint change affects the default Docker path.
- The default mode stops mounting the host Docker socket as documented.
- The project changes its default Docker capability policy.
