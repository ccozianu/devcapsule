---
status: confirmed
severity: minor
target: 0.9
owner: maintenance
opened: 2026-08-03
requirements: [R-ENV-001, R-FRAMEWORK-001]
---

# Observation: PyCharm Recommends Its Native Launcher

Date opened: 2026-08-03

Status note (pre-vocabulary, kept as evidence): observed in external dogfood; low-priority V1 review

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

## Disposition, 2026-09-25

Owner ruling during 0.2.14 acceptance: deferred beyond 0.2.14 and marked
minor; no functional failure was reported on any 0.2.14 candidate.

## Triage, 2026-10-04: confirmed, in scope for the 0.9 series

Owner ruling: a minimal change plus an end-to-end test, scheduled for 0.9,
the series expected to host V1's betas and candidates. What the triage
established, read from the source at `17532fd` and from the PyCharm
installed in this repository's own capsule (build 262.8665.369):

- **There is no recorded reason for the script.** The path was carried
  into the component template by the 2026-08-07 layout refactor from the
  Docker4PyCharm era; "intentionally encoded" records the fact, not a
  design. It lives in three places: the `launcher` key of the PyCharm
  runtime template (`components/pycharm.py`), the chmod and symlink in the
  image build (`launch/pycharm/_image_build.py`), and the archive probe in
  `materialization.py`.
- **The runtime's only coupling to the launcher** is one environment
  variable: the JetBrains adapter writes a properties file and sets
  `PYCHARM_PROPERTIES` to its path; the script maps that to
  `-Didea.properties.file`. The native binary honours the same
  product-prefixed `_PROPERTIES`, `_VM_OPTIONS` and `_JDK` variables; the
  `_PROPERTIES` lookup is present in the installed binary.
- **What the script does that DevCapsule does not use**: the JRE search
  through `PYCHARM_JDK`, the bundled runtime, `JAVA_HOME` and the path. The
  bundled runtime is what ships; nothing else is set.
- Both launchers are present in the installed archive, `bin/pycharm`
  (about one megabyte, ELF) and `bin/pycharm.sh` (28 kilobytes). This
  build's `product-info.json` carries no `launcherPath` key, so the
  derivation proposed in step 1 above cannot assume it; probe for the
  binary and fall back to the script.

**Minimal change.** Switch the three places to `bin/pycharm`, with the probe
accepting either file; the template digest changes the formation identity,
which is intended. Then the end-to-end proof: the opt-in IDE smoke test
(`nox -s ide-smoke`) launches each surface in a fresh project and proves
from the outside that the IDE comes alive, and it must keep passing under
the native process, plus the foreground, signal, exit-status and
container-removal checks of the review above. The warning disappearing is
the visible sign; the smoke row passing is the acceptance.

The same per-product choice arises for IntelliJ IDEA in the
`component-catalog` work targeted at 0.2.16; whoever generalizes the
template there should keep the `launcher` key per product rather than
assume one JetBrains filename.
