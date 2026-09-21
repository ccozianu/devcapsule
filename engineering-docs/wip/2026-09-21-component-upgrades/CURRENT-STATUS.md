# Workstream Current Status: Component Upgrades

Mnemonic: `component-upgrades`

Start date: 2026-09-21

State: integrating; runtime introspection correction validated, awaiting owner review and PR delivery

Definition read: WORKFLOW.md@ee9065a1b3ab, WORKFLOW-LOCAL.md@488eed5a6c05

Integration target: `main`

Delivery method: pull request; agent pushes, owner opens and merges on GitHub

Branch association: `ws-component-upgrades/v1`

Branch prefix: `ws-component-upgrades/`

Requirements: `R-UPGRADE-001`, `R-PRODUCT-001`, `R-PRODUCT-002`, `R-COMPAT-001`

## Goal

Deliver discoverable component upgrades with developer-owned, reproducible
version sets and operational rollback, using Codex as the first generic-channel
consumer. Intended for v0.2.14; project-management owns release sequencing.

## Current State

The owner-approved runtime correction is implemented. Ordinary launch supplies
a read-only configuration directory and an immutable session snapshot. Inside
the capsule, `versions show` distinguishes running software from the current
next-launch selection, and `config list` reads recorded settings without host
path validation or recovery writes. Mutation/state-dependent commands point to
the launcher. Older capsules need a relaunch to receive the mounts. The mount
uses the selected record's existing parent directory; sibling checkout records
can be readable under that shared layout, as documented. The contract-first
navigation rule is in WORKFLOW-LOCAL.md.

The original work order and the owner's review refinement are implemented.
Security/end-of-support notices now elicit decisions during interactive launch
through the existing Elicitor: review/upgrade, later, keep or stop. Confirmed
selection is used by that launch, with separate acquisition consent, accurate
success history and the existing recovery path. Daily best-effort checks use
cached offline fallback; noninteractive launch never checks or prompts.
The final focused suite and full repository gate pass. `project versions`
provides inspection, channel checks, exact previews, preparation/selection,
successful-use history, rollback, following the project again, proposal export,
and remembered reminders. Codex uses the typed npm channel; generic orchestration
also passes the unrelated widget and licensed-widget journeys.

Local selection is a complete checkout-owned version set. Ordinary configuration
and launch consume it without mixing in later project lock changes. Preparation
uses the existing acquisition/materialization engine; activation is recoverable.
Zero-exit history captures inputs before launch. Rollback preserves current host
permissions, personal state and exact software identities, including moved local
base tags. Candidate acquisition consent is explicit and cannot grant host access.

D-0010 records the owner's work-order decision and R-UPGRADE-001 the contract.
User/contributor instructions and permanent validation evidence are indexed below.
No release, mainline push or PR creation is part of this work order.

Session synchronization: fetched remote main remains `e4a96dc`, already contained
in the branch, with unchanged mainline workflow definitions. No synchronization was needed.
The local workflow was then updated with the owner's navigation rule; the generic
definition and declared workflow version were not changed.
Run workflow commands from the repository root: from `devcapsule-src` they report
state relative to that directory, which initially appeared misleadingly empty.
Re-running at root confirmed the published handoff. Final mail take found no mail;
there are no open bugs owned by this workstream.

## Planned Next Step

Owner reviews the pushed feature, including runtime introspection and the critical-upgrade launch UX, and
opens its PR against `main`. Address review findings on this branch. Once the PR is otherwise ready to merge, perform the
workflow finishing/archive changes and required checks, then the owner merges.
Verify remote main contains the finished tree before declaring the workstream
complete. Do not resume maintenance or cut a release.

## Validation And External State

Final gate after runtime introspection: `nox -s build` — 1,009 tests passed, 18 host-sensitive tests deselected,
one existing xfail; mypy, source smoke, PEX construction and nine packaged tests.
The channel/upgrade suite now contains 91 passing cases, including production
terminal elicitation and runtime inspection with controlled external boundaries.
No new real Docker/account acceptance is claimed for the prompting refinement. Earlier released-input fixtures
remain passing. Whitespace and new documentation links passed; the root index's
pre-existing absent five-in-a-row sample README remains unrelated.

Real ordinary-CLI fixture: Codex **0.153.4 → 0.155.1 → 0.153.4**, unchanged
project lock, successful proposal export and `git apply --check`, and explicit
return to following the recommendation. The tiny fixture IDE ran `codex --version`;
no account or interactive IDE acceptance is claimed. Exact PEX identity and the
boundary between that run and final source refinements are in the validation record.

The isolated `devcapsule-src/dist/component-upgrades-smoke/` tree retains about
654 MiB of artifacts/state and sanitized evidence. Its two canonical images are
retained; no fixture container remains running. The pinned existing base and the
owner's everyday checkout, accounts and previous environments were not changed.
A separate real Docker probe verified packaged runtime inspection, live atomic
replacement, mutation refusal and kernel-enforced read-only configuration.
The evidence and exact tested PEX are retained at
`devcapsule-src/dist/runtime-configuration-smoke-2/`; its container was removed.
No everyday configuration was mounted. The initial failed probe directory was
removed after correcting its non-executable tmpfs. No uncommitted work is
intentionally left. Git push is available; owner GitHub
PR creation/merge remains the delivery arrangement.

## Open Threads

### Awaiting The Human

Owner feature/code/UX review and GitHub PR opening/merge. The implementation
uses explicit component-channel notices. The optional question about adding an
independent security feed received no answer; the stated default confines this
slice to channel notices. A separate feed can be scoped later if desired. Authenticated agent use
and full interactive IDE acceptance remain outside the bounded executable probe.
Project-management owns the complete v0.2.14 scope and release sequence.

### Weighed And Unresolved

No design question blocks review. npm deprecation is the implemented support
signal; security notices are typed adapter data, with no independent vulnerability
feed or claim of complete security coverage. Retention has no automatic pruning; manual
removal of both artifacts and images can defeat offline recovery. Vendor state
migrations are not reversible by executable rollback. Serialized configuration
access remains required; the journal is not a general locking or power-loss
solution. Other components explicitly explain their missing distribution channels.

### Deliberately Not Preserved

No chat transcript was requested. The work order, canonical decision, requirements,
and validation record preserve the contract and evidence. Fixture account state
was never created; transient display tokens are redacted from the retained log.

## Workstream Document Index

- [Work order](../../work-orders/2026-09-21-component-upgrades.md): scope and finish criteria.
- [User guide](../../../docs/guides/component-upgrades.md): ordinary CLI journey and limits.
- [D-0010](../../decisions/product/d-0010-developer-owned-version-sets.md): owner decision and historical refinements.
- [R-UPGRADE-001](../../requirements/product/r-upgrade-001-component-version-sets.md): canonical contract.
- [Channel/implementation contract](../../implementation-notes/devcapsule/2026-09-21-component-distribution-channels.md): contributor interface and ownership/recovery mechanisms.
- [Validation record](../../implementation-notes/devcapsule/2026-09-21-component-upgrades-validation.md): observed real run, tests, limits and reproduction.
- [Intake dispositions](intake-dispositions.md): received-work decisions.
- [Intake instructions](intake/README.md): mail delivery.
