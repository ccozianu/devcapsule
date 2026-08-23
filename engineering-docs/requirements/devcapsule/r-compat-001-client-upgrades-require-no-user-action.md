---
id: R-COMPAT-001
title: Client Upgrades Require No User Action For Existing Projects
type: requirement
kind: concrete-requirement
status: accepted
priority: current stabilization
source_of_truth: repo
verification:
  - tests
  - manual
external_refs: []
---

# R-COMPAT-001: Client Upgrades Require No User Action For Existing Projects

## Statement

Installing a newer DevCapsule client must require no user action for a project,
checkout, or platform lock created by an earlier client. Ordinary work
continues across the upgrade.

A release that cannot honor this must name the exception, its justification,
and its migration instruction in that release's notes. Such an exception is
justified once, for one release, and does not generalize.

**Corollary.** Staleness, refusal, or reconfiguration triggered by a change in
the client — rather than by a change made by the user or by the project — is a
defect. This holds whether the trigger is a version gate, a digest comparison,
a new required field, or a changed default.

The requirement is stated as an outcome for the user, not as a mechanism.
Whether compatibility is achieved by reading older artifacts directly, by
migrating them in place, or by tolerating unknown fields is an implementation
choice, and different artifacts may resolve it differently.

## Rationale

Accepted by the product owner on 2026-08-23: a user who downloads a tooling
upgrade expects nothing to be required of them for the upgraded tool to work
with a project created by an earlier version. Anything else is a user
nuisance, and it is a nuisance delivered at the worst moment — the user did not
ask for it, did not change anything, and has no context for the failure.

This requirement is the general form of a concrete failure. The
`lock.manifest-digest` staleness check fired on an ordinary, intentional,
user-made configuration change and blocked every command that loads a project,
including `project config list`, whose purpose is to explain the state the user
is stuck in. That specific defect belongs to the first-run experience work; the
general property belongs here, because the same shape can arrive from any
release.

## Implementation

Not implemented. Verified on 2026-08-23 against the current tree:

- Four artifacts carry a format version, and every gate is exact equality
  against a single accepted value, with no accepted predecessor and no
  migration path:

  | Artifact | Field | Gate |
  | --- | --- | --- |
  | Project manifest | `devcapsule-schema-version` | `project_configuration.py:134` |
  | Platform lock | `devcapsule-lock-format-version` | `project_configuration.py:771` |
  | Checkout record | `devcapsule-checkout-schema-version` | `project_configuration.py:695` |
  | Generated resolution | `devcapsule-resolved-schema-version` | `commands/project.py:742` |

- No migration or compatibility-shim code exists for any of the four. The first
  release that increments any of these numbers is therefore a breaking release
  by construction, and the tool ships no way forward for the user.

- `canonical_digest()` (`project_configuration.py:591`) hashes the entire
  parsed manifest, and that digest is recorded in every committed platform
  lock. Nothing injects defaults before digesting, so a pure client upgrade
  does not currently invalidate a lock on its own. But any release that asks
  projects to declare a new manifest field invalidates every existing lock, and
  the remedy the failure prints is `project lock`, which cannot author a V1
  lock.

## Verification

- An automated compatibility fixture: run the current client against project,
  lock, and checkout artifacts produced by the previously released client, and
  require ordinary commands to succeed with no user action. Documentation
  review alone cannot verify this requirement — the failure mode is behavioral
  and appears only across a version boundary.
- The fixture's stored artifacts are versioned inputs and are not regenerated
  by the current client, which would defeat their purpose.
- Manual product-owner validation on a real upgrade of an existing project.

## Related

- `R-DOCS-002` — user-level documentation coevolves with user-visible behavior;
  a justified exception under this requirement is user-visible.
- `D-0004` — configuration resolution and guided run; the staleness model this
  requirement constrains.
- First-run experience work in `engineering-docs/design-notes/devcapsule/v1-user-experience.md`.
