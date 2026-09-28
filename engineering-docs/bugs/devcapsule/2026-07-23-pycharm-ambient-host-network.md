---
status: retired
severity: untriaged
target: none
owner: maintenance
opened: 2026-07-23
closed: 2026-09-22
requirements: [R-SCOPE-001, R-DOCKER-001, R-FRAMEWORK-001, R-PRODUCT-002]
---

# Bug: PyCharm Run-Image Network And Docker-Option Parity

## Current scope (2026-09-22)

Owner-selected resolution: **retire the public `pycharm run` command** rather
than extend its networking options. At the owner's direction, mark this bug
retired before implementing removal: its legacy option-parity requirements
will not be implemented. Removal and verification are the current maintenance
task; this disposition alone is not evidence that released RC0 lacks the command.
Preserve the shared launcher used by normal `project run`, update references
to the old command, and verify the retired invocation cannot launch a container.
The capability inventory and future migrate/drop decisions
are preserved in the
[V1-blocking work item](../../work-orders/2026-09-22-legacy-launch-capability-disposition.md).
Those future product decisions do not require preserving the legacy entrypoint.

### Removal Evidence — 2026-09-22

Removal is implemented on `release-0.2.14`: `PycharmRunCommand` and its three
CLI-only option translators are deleted. PyCharm help lists only `build` and
`check-runtime`; old run invocations return an actionable usage error before
launch or state preparation. Normal `project run` still calls the shared
launcher with explicit configured choices. Diagnostics and current usage
documentation no longer recommend the removed launch command.

115 focused CLI/project/launcher checks passed. The full `nox -s build` passed:
1,046 tests, 18 deselected, one existing xfail and the quarantined claim-test
XPASS; mypy over 167 files, source/PEX smokes and nine packaged integration
checks. Log: `/tmp/maintenance-retire-pycharm-run-build.log`. Direct checks of
the built local PEX rejected bare, `--help` and legacy image/DinD invocations
with the retirement message and created no checkout state. Source regression
tests also assert no launcher or subprocess call occurs.

The validated artifact is `devcapsule-src/dist/devcapsule-local.pex`; the gate
skipped revision-bearing packaging because the checkout carries edits. Main
integration and RC1 or later remain pending. Published RC0 is unchanged and
still contains the legacy command. No new Docker/GUI acceptance is claimed.

The owner retired `project run-image` and chose diagnostic
`project run --print-command` using the ordinary configured launch. The maintenance
patch removes the former command rather than adding its previously proposed parity
options. That decision supersedes the run-image-specific remedies and close criteria
below; retain them as historical evidence.

Before removal, the legacy `pycharm run` path inherits
`PycharmRunOptions.network_mode = "host"`. Normal `project run` supplies the reviewed
network choice explicitly. Removing run-image therefore resolves its command-specific
exposure but does not prove the shared legacy default safe. The selected
retirement supersedes adding a legacy network option; no Docker-daemon
acceptance is claimed by the diagnostic-output tests.

Date opened: 2026-07-23

Status note (pre-vocabulary, kept as evidence): reopened; open pending an explicit network option and broader
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
