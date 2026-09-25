---
status: confirmed
severity: untriaged
target: v1
owner: component-upgrades
opened: 2026-09-24
requirements: [R-UPGRADE-001, R-PRODUCT-001]
---

# In-capsule configuration inspection fails in the RC1 recursive session

The owner reports that RC1 mostly works, but configuration inspection fails
from both `/opt` and the mounted project. The original terminal transcript
was unavailable; both diagnostics were reproduced independently below.
This is separate from the repaired public-command/PATH defect: `devcapsule0`
is present and running the correct published executable.

## Expected behavior and ownership

Read-only configuration inspection from inside the capsule was part of the
component-upgrades deliverable for 0.2.14. See the
[implemented runtime inspection contract](../../implementation-notes/devcapsule/2026-09-21-component-distribution-channels.md#runtime-inspection).
The component-upgrades workstream therefore owns this bug, including the
recursive launcher parity gap; maintenance filed it during release validation.

`project config list` should report the launcher's recorded configuration
without attempting host-path validation, creating a shadow checkout, or
repairing host records. The owner additionally expects inspection with no
explicit project from a directory such as `/opt` to discover the enclosing
capsule's project. Preserve explicit project selection and nested-project
launcher use when defining that fallback.

Mutating commands such as `config set`, `authorize` and `resolve` remain
launcher operations under the current read-only contract. This report does
not authorize making host configuration writable inside a capsule.

## Exact environment and reproduction

- Published executable: `v0.2.14-rc1`, source `cec7a0c`, SHA-256
  `68c58ec09c1a73e07c3bb1b1f7514341ddddaf645c7fae1ff4ff0763ff6f7689`.
- Retained run: `0edc6f491291f0d5ffa4e31b0238863b`; successor
  `devcapsule-e2e-0edc6f491291f0d5ffa4e31b0238863b-successor`.
- Environment image:
  `sha256:bc387eb69b8457f61f016a0a21485302e3fc14bcbbae977e4a1623b8d5544863`.
- Base: `devcapsule-base:0.2.14-rc1-local`; host networking in the original run.
- Actual project mount: `/workspace/301e4208ef81-ChatGPT_Codex`.

The original successor had already exited with code 0. A disposable CLI-only
container used its exact image, the same project mounted read-only, and its
`PROJECT_PATH`/`DEVCAPSULE_CONTAINER_NAME` values. It ran as UID 1000, with
network disabled, no Docker socket or credentials, and temporary HOME. The
probe did not restart the IDE or alter the checkout/configuration.

| Working directory | Command | Result |
|---|---|---|
| `/opt` | `devcapsule0 project config list` | Exit 2: `No .devcapsule/devcapsule.toml found from /opt; run 'devcapsule project init'.` |
| Project mount | `devcapsule0 project config list` | Exit 2: `This capsule has no launcher configuration mount. Relaunch this project from outside the capsule with the updated DevCapsule launcher, then retry. Its running versions cannot be inferred from the project recommendation.` |

`project versions show` produces the same two failures. Bare `project config`
prints help and exits 0 in both directories; it is not the inspection command.
Exact probe output is retained in `configuration-diagnostics.json` under the
run's persistent-home `e2e-workspaces/` directory.

## Confirmed causes and coverage gap

1. Docker inspection of the original successor proves it lacks both
   `/etc/devcapsule/launch-context.json` and `/etc/devcapsule/checkout`.
   `ProjectRunCommand` passes `LaunchConfiguration.capture(...)` through
   `PycharmRunOptions`; `recursive_successor._resolved_run_options` does not.
   The missing-context diagnostic is intended for old capsules, but here the
   current recursive launch omitted the contract itself. Repeating that launch
   with the same RC1 executable will not repair it.
2. `runtime_configuration.for_project` discovers from the supplied starting
   directory. When no project exists there, it retains that directory and
   compares it to the runtime root; it never selects the capsule project as
   the default. This also affects an ordinary launch with valid context when
   inspection starts outside the project tree.

Existing runtime-inspection tests in `tests/test_version_sets.py` construct
the two mounts from ordinary launch options and invoke commands at the project
root. The recursive inspector validates its generated expected plan, but that
plan itself omits these mounts. Its earlier PASS did not test this user story.

## Verification needed before closure

- Actual ordinary and recursive launches supply the same read-only inspection
  contract; test the launch producer as well as the runtime reader.
- Published-candidate `config list` and `versions show` work from the project,
  its descendants, and `/opt` without an explicit project selection.
- Explicit `--path` and separate/nested projects retain their documented
  meaning; malformed or missing context is diagnosed without inventing state.
- Host-record atomic replacement remains visible through directory mounting;
  reads do not mutate records and unsupported mutations remain refused.
- Relaunch with the fix and validate the owner-facing terminal behavior.

No implementation changes made during intake. Severity and release disposition
await owner triage; no final-release acceptance is inferred from "mostly works."

## Owner observation on v0.2.14-rc3, 2026-09-24

In a capsule launched by an ordinary `project run` with the published rc3:
from `/opt`, `devcapsule0 project config list` fails as recorded above
(cause 2, no fallback to the enclosing capsule's project when the working
directory is outside the project tree); from the project mount under
`/workspace`, it succeeds and shows the project's configuration as
recorded on the host. This narrows the bug: cause 1, the missing
launch-context mounts, belongs to the recursive test launcher only and does
not affect ordinary launches. The user-facing defect is cause 2 alone, and
it is small: discovery should fall back to the capsule's project when no
project is found from the working directory and the runtime context names
one. The recursive launcher's parity gap remains a test-harness fix.

## Disposition, 2026-09-25

Owner ruling: discovery of the configuration inside the capsule from a
directory outside the project, such as `/opt`, is minor and is sent to the
V1 release to decide; it does not hold 0.2.14. The recursive test launcher's
missing mounts remain a test-harness fix on the same record.
