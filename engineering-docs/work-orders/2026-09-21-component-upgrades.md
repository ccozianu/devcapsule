# Work Order: Component Upgrades And Recoverable Version Sets

Prepared with the product owner on 2026-09-21 for execution in
`component-upgrades`, branch `ws-component-upgrades/v1`. This is the
fresh-session task contract; the preceding conversation is not required.
The intended release is v0.2.14, subject to project-management's release
sequencing. This order does not authorize cutting a release.

## Outcome And Owner Direction

Make it practical to respond to an agent's update notice through DevCapsule.
Today the owner postpones Codex's repeated notices because the update belongs
at the DevCapsule environment level, not in an ad hoc npm installation inside
a running capsule. Deliver a discoverable path to inspect available upgrades,
try a chosen version set, and return to a locally known-good version set.

Codex is the first real data point. Nothing in generic discovery, selection,
validation, activation, history, or rollback logic may special-case its name.
Its distribution details belong in its component definition or channel adapter.

The owner's settled product choices are:

- Use **version sets** consistently. A version set identifies the exact
  platform, base and selected component versions, with immutable artifact
  identities sufficient to reproduce the environment.
- Components declare distribution channels as part of their definitions.
  A channel is a resource, such as a URL or code adapter, that can report the
  status of a version and the existence of upgrades. This is technically
  optional but omission should encounter useful contributor-facing friction.
- Developers may deliberately select version sets DevCapsule has not yet
  validated. Missing validation is not an absolute prohibition on trying one.
- User-decided updates belong in developer-owned user configuration, scoped
  to the checkout. They do not silently rewrite the project's committed
  recommendation or lock.
- Tooling should recommend the optional contribution path: after successful
  use, prepare a reviewable upstream proposal. The developer decides whether
  to send a PR. Local experimentation must be useful without contributing.
- Easy rollback is part of the feature. Unit tests must prove return to a
  known-good version set, not merely that snapshot files can be written.

The owner wants an independently executed feature and code implementation,
reviewed at the end. Choose routine design, schema, CLI wording and code
structure within this order without repeated approval requests. Surface a
contradictory product contract or a consequential scope expansion while it is
still cheap to resolve. Do not expand this into an unrelated redesign.

## User Journey To Deliver

Start from a normal host terminal in the project checkout. Fit the existing
CLI's noun/verb model; command spellings discussed in chat were illustrative.
Provide coherent help and a short practical user guide covering this journey:

1. Inspect the effective version set and its origin: project recommendation
   or local selection. Check the selected components' distribution channels.
   Show current versions, available candidates and any reported withdrawn or
   unsupported status. Distinguish current metadata from an unavailable check.
2. Preview a candidate version set before changing anything. Show the diff,
   provenance of validation evidence, dependency-driven changes, required
   downloads, activation timing and recovery option. Selecting one component
   preserves unrelated versions unless declared constraints require a change.
3. Explicitly choose a candidate, including an unvalidated one. Prepare it
   without changing the currently running session. A successful preparation
   selects it for the next ordinary launch. Failed preparation leaves the
   existing usable choice intact and explains the next action.
4. Launch normally and associate successful use with the exact set launched.
   Keep project configuration, credentials, login state and user work intact.
5. Inspect locally known-good choices and select the previous working set
   through an easy rollback operation. The following ordinary launch must
   actually use that set. Explain when there is no known-good predecessor.
6. Explicitly return to following the project's recommendation by removing
   the local selection. If upstream changed while a local selection existed,
   show divergence and offer deliberate reconciliation; never quietly mix a
   new upstream baseline into the developer's selected set.
7. After successful use, offer to prepare an upstream recommendation change
   with the version-set diff and appropriately qualified evidence. The output
   must be a reviewable patch/change the developer can turn into a PR. Do not
   automatically commit, publish a PR or merge on the developer's behalf.

Reminders must respect the original pain: useful, dismissible and remembered,
not a new prompt on every launch. A deferred or dismissed candidate should
stay quiet according to a documented policy. A genuinely new candidate can
be surfaced. Normal launch and offline use must not require a successful
online update check. Do not claim to suppress vendor-owned prompts unless
that behavior is actually implemented; rewriting vendor prompt settings is
outside this slice.

## Version-Set And Distribution Contracts

Keep three facts separate in both data and presentation: upstream availability
and version status, DevCapsule validation evidence, and this developer's
successful use. A local zero-exit launch does not establish upstream validation
or test every capability. Preserve D-0007's accumulated verified edges and
declared couplings; do not require a manually enumerated row for every possible
combination or label every composition as directly tested.

Allow explicitly unvalidated sets while enforcing structural compatibility,
platform support, acquisition integrity and declared dependency/coupling
constraints. Resolve moving channel labels to exact artifact identities before
activation. A channel check cannot silently replace an existing selected set.
Do not execute arbitrary downloaded code as update metadata; code channels use
the existing trust boundary for installed component implementations.

Choose a small typed channel contract that can express version identity,
status, available candidates, platform applicability and acquisition metadata
or a reference to the existing acquisition contract. Reuse existing component
acquisition rather than adding a second installation engine. Channel failures
need actionable diagnostics; unavailable metadata is not evidence that the
installed version is current or invalid.

Make channel omission explicit during component definition/contribution
validation, with a documented reason or opt-out and an intelligible limitation
when checking that component. Existing definitions and configurations must
continue working. Optional metadata must not become a surprise migration
requirement for users of older projects.

Keep the complete effective set reproducible across project recommendation
changes. User configuration owns the choice; generated resolution and state
may hold derived data, prepared artifacts and history. Establish the actual
schema after tracing the existing ownership contracts. Merely persisting an
override that floats against changing project defaults is insufficient.

## Recovery Invariants

- Capture the exact launched inputs before launching. If configuration changes
  while that session runs, its completion must not certify the changed files
  as the set that succeeded. Preserve the accepted success trigger unless an
  explicit product decision changes it.
- A successful predecessor remains available while a successor is prepared
  and tried. A failed or interrupted candidate never becomes known-good merely
  because it was selected or materialized.
- Retain the previous exact local artifacts/environment needed for ordinary
  rollback, so a vendor removing an old download does not defeat recovery.
  If required local artifacts are missing, report the limitation and any
  possible exact reacquisition without destroying the current usable state.
- Rollback changes software selection while respecting current permissions.
  It must never resurrect a revoked host-resource authorization from an old
  configuration snapshot. Maintain the current explicit host boundaries.
- Preserve credential/login and project state. Downgrading executables cannot
  promise to undo agent-owned state/schema migrations; document that limit.
  Do not implement wholesale automatic restoration of personal state.
- Preserve recoverability on failures between preparation and activation and
  during repeated rollback. A backup of a failed/current candidate is not a
  known-good generation. Existing history should remain understandable.

Serialized configuration access remains the existing owner precondition.
Do not invent a broad locking/concurrency project; account specifically for
an old session completing after a new version set was prepared.

## Baseline Evidence And Required Reading

Preparation was based on `origin/main` at `e4a96dc`, after PRs #117 and #120
integrated the maintenance fixes and blog/handoff. Re-read changed contracts
on resume rather than assuming that revision is still current.

DevCapsule provides reproducible development environments through project
configuration, developer-owned checkout settings and explicit host consent.
The developer brief and detailed requirements govern this feature as they do
existing configuration and launch behavior. Start with the mandatory root
startup documents and this workstream's status/intake, then read:

- [Capability-first CLI decision](../decisions/product/d-0001-capability-first-cli-model.md).
- [Resolution and guided run](../decisions/product/d-0004-configuration-resolution-and-guided-run.md).
- [Agent-neutral optional components](../decisions/product/d-0005-agent-neutral-base-and-optional-agent-components.md).
- [Accumulated verification model](../decisions/product/d-0007-resolution-matrix-model-and-interface.md).
- [Known-good configuration history](../decisions/product/d-0008-known-good-configuration-history.md).
- [Identical runtime delivery](../decisions/product/d-0009-launcher-delivers-identical-runtime.md).
- [Upgrade compatibility requirement](../requirements/devcapsule/r-compat-001-client-upgrades-require-no-user-action.md).
- [Explicit host boundaries](../requirements/product/r-product-002-explicit-host-boundaries.md).
- [Maintenance configuration contract](../wip/2026-09-18-maintenance/configuration-contract.md),
  [correctness map](../wip/2026-09-18-maintenance/configuration-correctness.md),
  and [upgrade recovery contract](../wip/2026-09-18-maintenance/upgrade-recovery-contract.md).

Read implementation to settle specific questions. Initial navigation points:
`devcapsule-src/devcapsule/components/interface.py`, `resolution_matrix.py`,
`configuration/operations.py`, `configuration/resolution.py`,
`configuration/history.py`, and `commands/project.py`.

D-0008 currently snapshots checkout and resolved TOML after a successful
`project run`; it explicitly leaves guided restore for later. Those snapshots
are not a self-contained copy of the project platform lock. The run command
currently reads configuration files after the launcher returns, which needs
attention when a newer choice can be prepared during an older session.

Seven targeted existing tests passed during the discussion: six in
`tests/configuration/test_history.py` and
`tests/test_project_commands.py::test_project_run_records_known_good_configuration_only_on_success`.
They establish snapshot behavior and its success trigger, not operational
version-set rollback. Do not report the requested recovery proof as already
present. The preparation gate passed 917 tests, one existing xfail,
18 deselected, mypy and nine packaging tests; no feature code was changed.

Record the owner's local-selection refinement in the canonical requirements
and decision machinery during implementation. Preserve accepted decision
history; do not silently rewrite an old decision to imply it always said this.

## Validation And Reviewable Finish

Implement proportionate tests against the contracts above. Required evidence:

- A real Codex distribution adapter plus a synthetic unrelated component using
  the same generic path; no Codex-specific control flow in the generic engine.
- Deterministic channel tests for omission, unavailable/malformed metadata,
  exact pinning, status/validation distinction and relevant platform handling.
- Production configuration/CLI paths for project recommendation, local choice,
  upstream divergence, explicit follow-project-again and upstream proposal.
  Personal upgrades leave committed project recommendations unchanged.
- Start with a successfully launched set A, select and attempt B, then roll
  back and prove ordinary resolution/launch consumes A's exact identities.
  Cover failed B, interrupted preparation, repeated rollback, missing artifacts,
  and an old session completing after a newer selection. Use controlled external
  boundaries; do not test only a helper written to mirror the new implementation.
- Revoked host authorization stays revoked after rollback. Credential/project
  state is preserved. Earlier released configuration fixtures still work.
- Reminder dismissal/defer behavior and offline ordinary launch remain usable.
- Run the relevant focused checks and the repository's `nox -s build` gate.
  Stop broadening tests once concrete concerns are resolved.

Demonstrate the documented user journey through the ordinary CLI, including
one bounded real component upgrade and rollback where the authorized test
environment permits. Plan that check from a concrete uncertainty; do not launch
containers or alter the owner's everyday environment merely to explore. Report
fixtures, observed behavior and any unperformed acceptance check separately.
Self-authored tests alone are not proof of a satisfying upgrade experience.

Deliver feature/code, current user documentation and contributor instructions
for declaring a channel, a concise validation record, known limitations and
reproduction/review commands. Push the working branch and give the owner the
reviewable result; the owner opens and merges the GitHub PR. No direct-main
integration, release tagging or remote publication is authorized here.

## Scope Boundary And Fresh Start

This slice delivers component upgrades using Codex first. It does not deliver
DevCapsule launcher self-update, base/IDE upgrade delivery, an in-capsule
host-control broker, a universal package manager, background automatic
application, vendor prompt rewriting or personal-account/state migration.
Platform/base identities still belong in version sets for reproducibility.
The maintenance bug-triage proposal remains paused; do not take it over.

This session only prepares and publishes the registration and work order.
Implementation starts in the fresh session on `ws-component-upgrades/v1`.
Read Open Threads, fetch/synchronize as repository policy permits, take mail,
and begin by tracing the local-selection and recovery contracts into a small
implementation plan. Carry the agreed slice through reviewable completion;
no additional product scoping round is required to begin.
