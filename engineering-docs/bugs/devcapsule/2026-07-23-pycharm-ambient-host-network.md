# Bug: PyCharm Run-Image Network And Docker-Option Parity

Date opened: 2026-07-23

Status: reopened; open pending an explicit network option and broader
`run-image` Docker-option parity

Requirements: R-SCOPE-001, R-DOCKER-001, R-FRAMEWORK-001, root R-PRODUCT-002

## Symptom

Removing PyCharm's ambient host networking also removed the only way the
PyCharm dogfood launch could use host networking. `devcapsule run-image IMAGE`
does not expose an explicit network choice, even though `--network host` is
essential for the current dogfood environment.

More broadly, `devcapsule run-image IMAGE` is not yet runtime-equivalent to the
previous `devcapsule pycharm run --image IMAGE` path. Several Docker runtime
choices supported by the configuration-specific command cannot be selected on
the expert compatibility path.

## Evidence

Docker-daemon inspection originally confirmed `NetworkMode=host` even though
the `run-image` command did not contain a network option. On 2026-07-24 the
unconditional launcher argument was removed, but `run-image` gained no
replacement `--network` option.

The current `run-image` surface has `--docker-daemon [none|host-socket]` and
`--development-sudo`. The transitional PyCharm run surface additionally has:

- `--docker-socket` for a non-default host daemon socket;
- `--docker-in-docker` / `--dind`;
- `--debug-native`;
- `--writable-root`;
- repeatable `--docker-arg` values for expert Docker-run control.

The PyCharm launcher can consume those choices, but `run-image` cannot express
them. Neither PyCharm surface currently has a proper explicit run-network
option. The uncommitted dogfood workaround restored the launcher's historical
unconditional `--network host`, proving the immediate need but also restoring
the ambient-host-network defect until a real option is implemented.

## Expected Behavior

The safe default is Docker bridge networking. Host networking is available to
an operator who selects it explicitly on the command line or records it in
developer-owned checkout configuration. A committed project may recommend it
but cannot authorize it.

The expert `run-image` path should expose broad Docker-specific control. It
should make unusual or risky choices visible rather than maintaining a broad
forbidden-option list, while still applying restrictive workstation policy.

## Actual Behavior

The implementation currently has two bad states: without the dogfood
workaround, required host networking cannot be selected; with the workaround,
host networking is ambient and cannot be distinguished from an intentional
operator choice. Other expert Docker runtime choices are also lost when moving
from `pycharm run` to `run-image`.

## Root Cause

The Python launcher retained the historical PyCharm prototype's unconditional
host-network setting while runtime authorization was being refactored. The
subsequent fix removed the default at the shared launcher layer before the
expert command had a shared runtime-options model capable of passing an
explicit replacement and the other existing Docker choices.

## Fix Progress

On 2026-07-24 the unconditional `--network=host` argument was removed from the
shared PyCharm launcher, and an end-to-end planning test asserted bridge-like
default behavior. That was only half of the required fix: the explicit
host-network choice was not added to `run-image`. The user restored the legacy
launcher argument ad hoc to keep dogfood usable.

The bug is therefore reopened. Keep it open while the workaround is present
and until explicit network selection plus the accepted expert Docker-option
surface are implemented and validated.

## Proposed Fix Direction

- Replace the restored unconditional `--network host` workaround with a shared
  network-mode value whose safe default is `bridge`.
- Allow developer-owned checkout configuration and explicit command-line
  options to select `host`.
- Let committed configuration recommend, but not activate, host networking.
- Include the effective network mode in sanitized runtime-plan output.
- Make `run-image` accept an explicit `--network MODE` choice, including
  `--network host` for the current dogfood launch.
- Define and implement the accepted `run-image` parity surface for custom host
  Docker sockets, Docker-in-Docker, native debugging, writable root, and raw
  repeatable Docker arguments. Prefer the shared runtime-options model already
  planned by the Codium parity bug over another command-specific translation.
- Preserve expert custom Docker arguments for `run-image`, subject only to
  structural plan validation and restrictive workstation policy.

## Verification Target

1. Automated: both PyCharm launch paths default to bridge networking.
2. Automated: explicit `run-image` and checkout-owned host-network selections emit
   `--network=host`.
3. Automated: a committed recommendation alone does not enable host networking.
4. Automated: accepted Docker modes and expert arguments produce the same
   launcher plan through `run-image` as through the legacy PyCharm surface.
5. Manual: inspect a default and explicitly host-networked dogfood container,
   including the Docker access and development options used for dogfood.

## Close Criteria

Close when host networking is absent by default, remains available through an
explicit developer-owned choice, `run-image` retains the accepted Docker-run
capabilities of the previous PyCharm path, both launch paths share the behavior,
and the automated plus Docker-daemon inspection targets pass.
