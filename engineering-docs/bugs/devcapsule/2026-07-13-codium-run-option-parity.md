# Bug: Codium Run Lacks Shared Developer Runtime Options

Date opened: 2026-07-13

Status: accepted parity gap; first shared state-layout slice implemented, broader parity still pending

Requirements: R-PYTHON-MVP-003, R-FRAMEWORK-001, R-SCOPE-001, R-DOCKER-001

## Symptom

`devcapsule codium_with_claude run` exposes a much smaller runtime surface
than `devcapsule pycharm run`. Developers using VSCodium cannot select the
same explicit state profiles, project mount layout, Git transport, Docker
capability, native debugging, sudo, or writable-root behaviors.

The command name in this record is `codium_with_claude`; references to
`codium_with_code` in the initial report are treated as a typo.

## Current Common Options

Both commands currently expose:

- `--project`, `-p`
- `--profile`
- `--image`
- `--name`
- `--state` (`pycharm` also calls this `--global-settings`)
- `--project-state`
- `--project-state-root`
- `--project-mount`
- `--docker-arg`

Codium alone currently exposes `--debug-shell`.

On 2026-07-13, Codium gained an opt-in `--network MODE` option as an early
debugging slice. It applies to both normal and `--debug-shell` launches;
`--network host` explicitly relaxes network isolation. Broader option parity
remains pending.

On 2026-07-15, Codium gained a first shared runtime-layout slice backed by a
common planner module used by both PyCharm and Codium. That slice added shared
support for `--profile`, `--project-state-root`, and `--project-mount` while
preserving Codium's existing default in-container project path.

## Options Present Only On PyCharm Run

The following list includes aliases because they are part of the public
command surface:

1. State and filesystem layout:
   - `--global-settings` as the descriptive alias of `--state`
   - `--config-mode [shared|project|custom]`
   - `--ide-config`
   - `--project-config`
   - `--shared-config`
   - `--plugins`
2. Git identity and credentials:
   - `--ssh-agent`
   - `--git-user-name`
   - `--git-user-email`
   - `--git-identity-from-host`
   - `--no-git-identity-from-host`
   - `--git-token-file`, `--github-token-file`
   - `--git-token-env`, `--github-token-env`
   - `--git-token-user`, `--github-user`
   - `--git-token-host`
3. Docker capability profiles:
   - `--docker`, `--host-docker`
   - `--docker-socket`
   - `--docker-in-docker`, `--dind`
   - `--no-docker`
4. Development and isolation profiles:
   - `--debug-native`
   - `--dev-sudo`, `--sudo`
   - `--writable-root`
5. PyCharm-specific behavior:
   - `--ignore-config-lock`

## Are These Options Useful To Codium Developers?

Most are useful, but they fall into three different categories.

### Directly Useful As Shared Framework Capabilities

- `--profile`: developers need named persistent settings/credential profiles
  independently of IDE choice.
- `--project-state-root`: useful for keeping generated state outside source
  trees and mirroring project layouts consistently.
- `--project-mount`: useful when tools, scripts, or documentation require a
  stable container path.
- All Git identity, SSH-agent, and scoped HTTPS-token options: Git workflows
  inside VSCodium and Claude Code need the same deliberate credential model.
- Docker modes and `--docker-socket`: containerized development and agents may
  need host Docker, isolated Docker-in-Docker, or an explicit no-Docker mode.
- `--debug-native`: equally useful for `strace`, debuggers, profilers, and
  native extensions.
- `--dev-sudo` and `--writable-root`: useful for deliberate development
  sessions that need package installation or system mutation.

These should be implemented by shared runtime planning rather than duplicated
from the PyCharm launcher.

### Useful With Codium-Specific Semantics

- `--plugins` should become an IDE-neutral or Codium-specific extensions path,
  such as `--extensions`, while retaining explicit persistence.
- `--global-settings` is clearer than the generic `--state`, but the framework
  should settle one consistent public naming model.
- Config placement is relevant because VSCodium has user data, extensions,
  cache, and singleton/runtime state. However, PyCharm's exact
  `shared|project|custom` model must not be assumed to match Electron locking
  and concurrency behavior. Codium needs its own evidence-based state split.
- `--project-config` and `--shared-config` should exist only if the resulting
  Codium modes are meaningful; they should not survive merely as PyCharm
  compatibility aliases.

### Not Directly Portable

- `--ignore-config-lock` handles an IDEA-family `.lock` preflight and should
  remain PyCharm-specific. If VSCodium singleton locks cause a real conflict,
  add a Codium-specific check and recovery message based on observed behavior
  rather than reusing this switch.

## Expected Behavior

Configurations should expose a consistent core set of developer runtime
capabilities where the behavior and security boundary are IDE-independent.
Configuration-specific options should cover only real vendor differences.
Users should not lose Git, Docker, debugging, sudo, state-layout, or project
mount controls merely because they selected VSCodium instead of PyCharm.

## Actual Behavior

The Codium launcher directly assembles a minimal `docker run` command. The
PyCharm launcher independently owns substantially richer state resolution,
credential preparation, Docker modes, and development profiles. There is no
shared run-planning layer for the Codium configuration to consume.

## Security And Compatibility Constraints

- Keep every added host mount, socket, credential, capability, device, and
  writable-root relaxation explicit and documented.
- Do not silently give Codium host Docker access because the historical
  PyCharm configuration defaults to it. The default must be chosen and
  documented deliberately.
- Preserve the narrow Git-token host allowlist and temporary-file cleanup
  behavior.
- Do not mount the host home, `.ssh`, `.gitconfig`, or credential directories
  as a shortcut.
- Do not encode PyCharm environment-variable names or IDEA lock assumptions in
  shared framework components.
- Keep source-install and PEX command behavior equivalent.

## Proposed Implementation Direction

1. Define a shared runtime options/configuration model for:
   project planning, profile/state roots, host identity, X11, Git transport,
   Docker capability mode, debugging, sudo, writable root, and advanced Docker
   arguments.
2. Extract tested Docker-argument and temporary-runtime-file planning from the
   PyCharm launcher into IDE-neutral modules without changing accepted PyCharm
   behavior.
3. Adapt both PyCharm and Codium launchers to the shared model.
4. Add Codium-specific extension, user-data, cache, and singleton-state
   planning based on concurrent-launch experiments.
5. Add options incrementally with help, conflict validation, isolation
   documentation, and focused command-plan tests.

Raw `--docker-arg` remains an advanced escape hatch, not an adequate public
replacement for safe, validated capability options.

## Verification Target

1. Add a parameterized parity test that identifies the intended shared option
   set across both commands.
2. Add focused tests for every new mount, environment value, capability, and
   option conflict.
3. Verify default Codium launch arguments do not gain ambient host access.
4. Verify explicit Git, Docker, debug, sudo, and state profiles on a host.
5. Confirm concurrent Codium sessions with the chosen state split.
6. Run `cd devcapsule-src && python -m nox -s build` and smoke-test the PEX
   command surface.

## Close Criteria

Close this bug when the accepted shared capability set is available to Codium,
IDE-specific exclusions are documented, automated planning/CLI tests pass,
and the security-sensitive profiles have been manually validated. A smaller
first slice may close a child task, but should not close this parity bug while
material shared developer capabilities remain unavailable.
