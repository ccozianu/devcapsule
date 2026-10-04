---
status: fixed
severity: major
target: 0.2.16
owner: component-catalog
opened: 2026-10-04
requirements: [R-PRODUCT-001, R-PRODUCT-002]
---

# Unreleased Playwright in the shared lock prevents released launchers opening the checkout

The owner reports that ordinary `devcapsule project run` fails with:

```text
devcapsule: no V1 runtime template is available for component 'playwright'
```

The shared development checkout should remain launchable with the released
CLI. The host executable's exact path and version have been requested but are
not yet established. The command named `devcapsule0` inside the current capsule
reports `0.2.16.dev0`, source `unknown`; it does not identify the owner's host
launcher.

## Cause

Commit `ada153c00637ab6561b7f4a13ea33321fb17b8ab` added both
`browser-automation` to `.devcapsule/devcapsule.toml` and `components.playwright`
to the committed Linux lock. Playwright support exists in the development
catalog but not in final v0.2.15's catalog. Its runtime-template selection
rejects that lock. The matrix version is informational; changing that number
cannot give an older executable a new component implementation.

Git establishes the introducing change, but not whether the original lock
was written through a CLI command or a file-editing tool. The fault is the
unsupported shared bootstrap dependency regardless of the writing mechanism.
The development-executable E2E passed because it had Playwright support;
that evidence never covered the owner's released launcher.

The existing repository compatibility guard covered runtime-effect vocabulary
only, following the [September manifest incident](2026-09-24-released-launchers-reject-repository-manifest.md).
It did not cover capability needs or locked runtime-template IDs.

## Repair and prevention

- Restore the exact manifest and lock from `ada153c^` as a pair. Their diff
  removes only the added Playwright need/component and restores the associated
  generated digest/provenance. Existing component versions stay unchanged.
- Keep Playwright's implementation, resolution fixtures and disposable E2E
  selections. Testing a component does not make it a bootstrap prerequisite.
- Add the local [checkout compatibility rule](../../../WORKFLOW-LOCAL.md#keep-the-development-checkout-launchable):
  released-launcher compatibility by default, deliberate launcher selection,
  generated locks, validation against the consumer, and an owner-agreed
  bootstrap path before requiring a development launcher.
- Extend `tests/test_repository_manifest_compatibility.py` with frozen
  capability and component vocabularies from final v0.2.15, commit
  `a15ff8b58f4af93845c17eaca22f9c9d29c8e000`. Do not derive these guards from
  the current development catalog.

## Evidence and remaining verification

The two new guards failed on the original pair, explicitly naming
`browser-automation` and `playwright`; after restoration, all 43 focused
compatibility/resolution tests passed.

An isolated export of the v0.2.15 Python package (loaded with the checkout's
Python interpreter and dependencies) reproduced the exact catalog error on
the original lock and rejected the original need. On the restored pair it
accepted the manifest vocabulary, verified the capability digest, parsed
lock/materialization metadata and constructed the project runtime plan.
Log: `.git/launcher-compat-tagged-source.log`. This is tagged-source evidence,
not a run of the downloaded release executable and not a Docker launch.
No launcher, Docker container, user authorization or persisted IDE state was
changed. Owner confirmation of `project run` with the host executable remains
outstanding; do not close this record on source/gate evidence alone.

Full `nox -s build` passed: 1,152 unit tests, nine packaging checks, mypy,
source/executable smokes and the documentation contract. Log:
`.git/launcher-compat-build.log`; command used
`PYTEST_ADDOPTS=--basetemp=/opt/devcapsule-gate/pytest`. The resumed environment
initially lacked that scratch parent; an alternate `/var/tmp` attempt exhausted
its 1 GB tmpfs. Recreating the documented scratch directory on the large overlay
resolved those setup failures. No product-code change was needed.

## Owner recovery and 0.3 planning follow-up

The owner subsequently reported a successful recovery using an already-built
executable in the shared `dist` folder. Its exact identity is not yet recorded.
This is a different path from the proposed manifest/lock rollback and does not
confirm that rollback on the host. The defect stays fixed pending that check.

The owner wants these lessons addressed for a 0.3 release. Component-catalog
sent `2026-10-04-component-catalog-0-3-launcher-bootstrap-lessons.md` to
project-management on the coordination branch, with proposed compatibility,
safe-transition, independent bootstrap/recovery and cold-restart acceptance
requirements. Scope and sequencing, including the relationship to 0.2.16,
remain decisions for release planning with the owner.
