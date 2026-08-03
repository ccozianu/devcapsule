# Observation: PyCharm Recommends Its Native Launcher

Date opened: 2026-08-03

Status: observed in external dogfood; low-priority V1 review

Requirements: R-ENV-001, R-FRAMEWORK-001

## Observation

The v021-backed PyCharm 2026.2.0.1 environment reports:

```text
The IDE seems to be launched with a script launcher ('bin/pycharm.sh').
Please consider switching to a native launcher ('bin/pycharm') for better
experience.
```

This is caused by DevCapsule's current component template. Materialization
explicitly requires `bin/pycharm.sh`, and the generic JetBrains adapter launches
the configured script in the foreground.

## Evidence

The pinned PyCharm archive supports the recommended alternative:

- `product-info.json` declares `"launcherPath": "bin/pycharm"`;
- `bin/pycharm` exists as an executable x86-64 ELF binary; and
- `bin/pycharm.sh` exists as the shell launcher currently selected by
  DevCapsule.

The current source and tests intentionally encode `bin/pycharm.sh`; this is not
a missing-file or packaging failure.

## Current Assessment

The vendor recommendation is reasonable, but changing the executable belongs
in the component/runtime contract rather than as an untested string edit. The
native launcher must preserve DevCapsule's foreground process ownership under
`tini`, project argument handling, environment and properties delivery, exit
status, restart behavior, and automatic container removal.

No functional failure beyond the warning has been reported, so this remains a
minor review item rather than an immediate V1 blocker.

## Proposed Review

1. Derive or validate the launcher against the pinned archive's
   `product-info.json` instead of assuming a universal JetBrains filename.
2. Change the PyCharm component template to `bin/pycharm` and ensure the
   template digest changes the canonical formation identity. The existing
   archive already carries the binary, so this should not require a new base.
3. Verify that the native process stays foreground-attached below `tini`,
   receives termination signals, returns meaningful status, and keeps the
   container alive for the IDE session.
4. Exercise IDE restart, ordinary window close, project-path launch, runtime
   properties, X11, JCEF preview, plugins, and a second persistent launch.
5. Update fixture archives and source/PEX/Docker E2E checks to represent the
   native launcher contract.
6. Confirm the warning disappears without adding a shell wrapper or command
   override that defeats the purpose of the native launcher.

## Close Criteria

Close when the native launcher is selected through validated component
metadata, formation identity reflects the change, automated lifecycle tests
pass, external dogfood confirms normal launch/restart/exit behavior, and the
JetBrains warning is absent.

Retire without implementation if controlled testing shows a concrete native
launcher incompatibility with DevCapsule's foreground container lifecycle and
the retained script behavior is documented. Reopen if the script launcher
causes a functional problem rather than only a recommendation.
