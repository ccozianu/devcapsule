---
status: fixed
severity: minor
target: 0.3.0
owner: maintenance
opened: 2026-09-26
requirements: [R-PRODUCT-001]
---

# Inside a capsule, `project <unknown>` is refused as launcher-only instead of as unknown

The owner, inside a running capsule and in the project directory, tried to
install the workflow with `devcapsule project --path $PWD bootstrap`. The
answer was that the command needs launcher-owned configuration and must run
outside the capsule, with a remedy command that repeats the same spelling.
Run outside, that spelling fails as an unknown subcommand. The real command,
`devcapsule bootstrap project`, is not under the `project` group, has no
launcher guard, and installs the files inside the capsule; the owner had no
way to learn that from the message.

## Environment

- Owner: shipped launcher `v0.2.14` inside a 0.2.14 capsule, project mounted
  at `/workspace/chessclub-website`.
- Reproduced with the development CLI at `74bc4aa` inside this dogfood
  capsule, which has no launch-context file: the same command yields the
  other guard message, "This capsule has no launcher configuration mount",
  again before the subcommand is validated.

## Reproduction

```text
$ devcapsule project --path $PWD bootstrap
devcapsule: This command needs launcher-owned configuration or state. Inside this capsule that
configuration is read-only. Run outside the capsule: devcapsule project --path /home/costin/.../chessclub-website bootstrap
```

Outside the capsule, `devcapsule project bootstrap` is rejected by argparse
as an invalid choice. Inside the capsule, `devcapsule bootstrap --project
$PWD` runs and installs the workflow files (probe on a scratch directory,
2026-09-26).

## Cause

`ProjectCommand.make_context` in
`devcapsule-src/devcapsule/commands/project.py` calls
`runtime_configuration.require_launcher` on the raw token list before argparse
has validated the subcommand: any first token that is not in its small
read-only allowlist triggers the guard. The guard's remedy echoes the tokens
verbatim, so an invalid command is reported as a valid one that merely needs
the launcher.

## Expected

An unknown `project` subcommand is reported as unknown, with the group's
choices, inside and outside a capsule alike. The launcher guard applies only
to subcommands that exist. Nice to have: the unknown-subcommand message for
`bootstrap` points at `devcapsule bootstrap project`.

## Verification target

A test in `devcapsule-src/tests/test_project_commands.py` that runs
`project --path <root> bootstrap` with a patched launch context present and
asserts the invalid-choice error rather than the launcher message; and the
owner's rerun inside a capsule.

## Close criteria

Status `closed` when the test passes on `main` and the owner confirms the
message inside a capsule with a release that carries the fix.

## Release disposition (owner, 2026-09-27)

The owner explicitly accepts this limitation for 0.2.15. Keep the defect
open and outside that release's gate; a later target remains unassigned.
The owner's broader report that project subcommands fail inside the capsule
regardless of working directory is preserved as reported, not established
by the narrower reproduction above.

The same decision adds `project info` and persistent `/opt/xtras` to 0.2.15;
see the [accepted work order](../../work-orders/2026-09-27-project-environment-discovery.md).
`project info` must work inside the capsule, including outside the project
directory. The deferral does not excuse failure of that new command.

## Owner ruling, 2026-10-01

Targeted at 0.2.16 together with the
[in-capsule inspection record](2026-09-24-runtime-configuration-inspection-fails.md),
whose ruling of the same date covers this: the `project` group validates
the subcommand first, resolves the capsule's project automatically, and
reaches the launcher guard only for a valid mutating command. The owner's
broader report of 2026-09-27, that project subcommands fail inside the
capsule regardless of directory, is now established on v0.2.15 and
recorded there with its three causes; this record keeps the
argparse-before-guard half. Recorded by `project-management`.

## Fix, 2026-10-05, on `ws-maintenance/post-0.2.15`

Fixed with the [inspection record](2026-09-24-runtime-configuration-inspection-fails.md),
whose fix section has the design: the `project` group resolves the
subcommand without side effects (`Group.resolve`) before applying any
capsule policy, so an unknown name reaches the ordinary "unknown command"
error with the group's choices, inside and outside a capsule. Verified by
`test_runtime_unknown_subcommand_is_unknown_not_launcher_only` and by
`project --path $PWD bootstrap` inside this repository's capsule. The
nice-to-have pointer from `bootstrap` to `devcapsule bootstrap project` is
not implemented. Closes on the owner's rerun with a 0.3.0 candidate.
