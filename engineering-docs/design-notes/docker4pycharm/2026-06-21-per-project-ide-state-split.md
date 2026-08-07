# Decision: Per-Project IDE State Split

Date: 2026-06-21

Status: implemented, manually validated on 2026-06-22; amended on 2026-06-24 for config lock handling

## Context

The user found that launching the same image against a different host project,
while reusing the same plugin directory and the same previous state directory,
could make PyCharm show stale Project view contents from the earlier project.

The likely trigger is a combination of two facts:

- JetBrains IDE global settings live in the configuration directory and are
  meant to apply across projects.
- Project, recent-workspace, cache, and window state are also persisted by the
  IDE, and the old launcher made every mounted host project appear as the same
  `/project` path inside the container.

## Decision

Split the launcher storage model:

- `--global-settings` maps to `/ide-global-settings` and backs the isolated
  IDE home plus the default shared JetBrains config root.
- `--shared-config` keeps `idea.config.path` at
  `<global-settings>/config`, which preserves current settings continuity but
  supports only one live PyCharm process at a time because JetBrains locks this
  config directory.
- `--project-config` maps `idea.config.path` to `<project-state>/config`, which
  is intended for concurrent sessions against different projects.
- `--ide-config DIR` maps `idea.config.path` to an explicit config directory.
- `--plugins` remains shared at `/ide-plugins`.
- `--project-state` maps to `/ide-project-state` and backs
  `idea.system.path`, logs, and XDG cache state.
- The default in-container project path is now `/workspace/<project-id>` instead
  of `/project`, where `<project-id>` is derived from the resolved host project
  path.

`--state` remains as a legacy alias for `--global-settings` so an existing
working PyCharm configuration can keep using the old default directory:

```text
~/.local/share/pycharm-docker/state
```

## Consequences

Existing shared settings, plugin preferences, AI login state, SSH known-hosts,
and similar IDE-local home files should continue to persist through the shared
global settings root.

Different host projects should receive separate system/cache/log/workspace state
by default and should appear to PyCharm under distinct container paths.

Some project code or scripts may have assumed the mounted project path was
always `/project`. Those cases can use `--project-mount`, but reusing the same
mount path for unrelated projects can reintroduce stale JetBrains workspace
state.

## Verification

Static checks completed:

```bash
shellcheck docker4pycharm/run-pycharm-container.sh docker4pycharm/entrypoint.sh
bash -n docker4pycharm/run-pycharm-container.sh docker4pycharm/entrypoint.sh
./docker4pycharm/run-pycharm-container.sh --help
docker run --rm --network host --read-only --workdir /workspace/test \
  --mount type=bind,src=/tmp,dst=/workspace/test \
  busybox:latest sh -c 'pwd; test -d /workspace/test'
```

Manual validation completed on 2026-06-22:

1. Launch the DockerForIDEIsolation project with shared `--global-settings` and
   shared `--plugins`.
2. Launch a separate ordinary Python project with the same shared settings and
   plugins, allowing the default per-project state and mount path.
3. Confirm the Project view, open files, and recent workspace state correspond
   to the current mounted project, while global IDE settings and plugins remain
   available.

## Reopen If

Reopen if PyCharm still shows stale Project view contents when two different
host projects use the same shared global settings and plugins but default
per-project state and mount paths.
