# Workstream Current Status: Component Upgrades

Mnemonic: `component-upgrades`

Start date: 2026-09-21

State: integrating; discovery and compatibility service validated, awaiting owner PR review and delivery

Definition read: WORKFLOW.md@ee9065a1b3ab, WORKFLOW-LOCAL.md@2103fb7c230c

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

Owner extension implemented: all six curated components have read-only vendor
update discovery. Codex retains installation/selection; discovery-only candidates
are not offered as installable. PostgreSQL major-only base locks report upstream
support/latest minor without inventing an installed minor or missing update.

Failed checks consult a versioned DevCapsule compatibility feed, matching adapter,
CLI version and platform locally. Maintained diagnoses identify released fixes or
known issue/workaround links. Feed and diagnosis expiry, unknown metadata and
unavailable service/cache remain explicit. Last-successful checks and existing
notices survive failure; software selection and offline launch remain intact.

The scheduled/main-change/manual GitHub Action generates the feed and a
GitHub-rendered status page on the dedicated `component-status` branch. The
backend records observations separately from authored diagnoses and never invents
an incident or renews its review date. No website Pages deployment is changed.
The first live publication waits for owner PR merge; no remote status branch was
created in this session. The source policy currently contains no diagnoses.

The original version-set journey, critical prompts and read-only runtime
introspection remain implemented; earlier evidence is in the validation record.
The full gate exposed three launcher tests reading this restarted dogfood
capsule's ambient context. Their fixtures now use their own temporary working
directory; production runtime dispatch and mounts are unchanged.

Session synchronization: fetched `origin/main` remains `e4a96dc`, already in this
branch. No synchronization needed. Mail and owned open bug queues were empty.
Workflow commands run from the repository root, not `devcapsule-src`.

## Planned Next Step

Owner reviews the pushed extension and opens the feature PR against `main`. After merge, inspect the first
**Component update status** action, public raw feed and rendered status page;
GitHub token/branch policy and public-endpoint client acceptance remain external
checks. No release or direct-main integration is authorized. Before workstream
closure, complete archive/finishing work and verify remote main contains the tree.
Do not resume maintenance automatically.

## Validation And External State

Latest gate for compatibility service: `nox -s build` passed 1,033 tests,
18 host-sensitive cases deselected, one existing xfail, mypy on 165 files,
source/PEX smoke and nine packaged tests. Focused suite: 115 passed. Six live
metadata probes passed without executable downloads. The workflow publication
shell passed against a local bare remote, including successive fast-forward
updates and unchanged main. Logs: `/tmp/component-status-build.log`,
`/tmp/component-status-focused.log`; generated local metadata/page preview at
`/tmp/devcapsule-component-status-preview/`. No hosted deployment was performed.

Previous checkpoint evidence:

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

Owner PR review/opening/merge and first hosted publication acceptance. Older
clients predating fallback support need one normal CLI upgrade. Authenticated
agent/interactive IDE acceptance and release sequencing remain with the owner.

### Weighed And Unresolved

GitHub-rendered branch page avoids coupling status to the existing Pages sites.
Current probes do not certify every old adapter; maintained diagnoses retain
explicit old IDs and review deadlines. No independent vulnerability feed,
additional installation adapter or "upgrade all" command is claimed here.
Vendor state migrations and manually deleted recovery resources retain earlier
rollback limitations. No product decision blocks review.

### Deliberately Not Preserved

No chat transcript or accounts were created. Contracts, operator instructions and
validation records retain the decisions. Local metadata previews are observations,
not deployed service evidence.

## Workstream Document Index

- [Status service](../../../component-status/README.md): v1 contract, publication and maintenance operations.
- [Work order](../../work-orders/2026-09-21-component-upgrades.md): scope and finish criteria.
- [User guide](../../../docs/guides/component-upgrades.md): ordinary CLI journey and limits.
- [D-0010](../../decisions/product/d-0010-developer-owned-version-sets.md): owner decision and historical refinements.
- [R-UPGRADE-001](../../requirements/product/r-upgrade-001-component-version-sets.md): canonical contract.
- [Channel/implementation contract](../../implementation-notes/devcapsule/2026-09-21-component-distribution-channels.md): contributor interface and ownership/recovery mechanisms.
- [Validation record](../../implementation-notes/devcapsule/2026-09-21-component-upgrades-validation.md): observed real run, tests, limits and reproduction.
- [Intake dispositions](intake-dispositions.md): received-work decisions.
- [Intake instructions](intake/README.md): mail delivery.
