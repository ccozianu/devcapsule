# Workstream Current Status: Component Upgrades

Mnemonic: `component-upgrades`

Start date: 2026-09-21

State: paused; checkpoint merged and first hosted publication verified; V1 operational follow-up retained

Definition read: WORKFLOW.md@a1002b6f5e67, WORKFLOW-LOCAL.md@ed70f3147563

Integration target: `main`

Delivery method: pull request; agent pushes, owner opens and merges on GitHub

Branch association: `ws-component-upgrades/v1`

Branch prefix: `ws-component-upgrades/`

Requirements: `R-UPGRADE-001`, `R-UPGRADE-002`, `R-PRODUCT-001`, `R-PRODUCT-002`, `R-COMPAT-001`

## Goal

Deliver discoverable component upgrades with developer-owned, reproducible
version sets and operational rollback, using Codex as the first generic-channel
consumer. Intended for v0.2.14; project-management owns release sequencing.

## Current State

Owner requested publication of the current slice and a user/developer write-up.
The component freshness guide explains vendor sources, interpretation, user
actions, client/backend responsibilities and today's operational limits.
R-UPGRADE-002 captures accepted V1 follow-up: 48-hour observation freshness,
persistent vendor-failure handling, independent monitoring, verified notification
delivery and failure drills. These are not implemented or newly imposed release
gates. The workstream remains open for this follow-up after checkpoint integration.
Portfolio sequencing request delivered to project-management through coordination
mail as `2026-09-21-component-upgrades-v1-status-reliability.md` at `a0ffbec8cdcf`.

The owner reiterated that all GitHub integration beyond SSH Git operations is
theirs through the UI. WORKFLOW-LOCAL.md now explicitly prohibits probing gh or
using API/connector integration even when available. Before this correction the
agent made read-only GitHub API inquiries; it created no PR or hosted publication.
Subsequent delivery follows SSH branch push and owner UI handoff.

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
Owner merged PR #122 at `fa44a2f`; first hosted publication is commit `c23ed99`
on `component-status`. Public feed and README were fetched and verified against
that commit on 2026-09-21. The source policy currently contains no diagnoses.

The original version-set journey, critical prompts and read-only runtime
introspection remain implemented; earlier evidence is in the validation record.
The full gate exposed three launcher tests reading this restarted dogfood
capsule's ambient context. Their fixtures now use their own temporary working
directory; production runtime dispatch and mounts are unchanged.

Session synchronization: fetched `origin/main` at `9bf2711`, verified it contains
`29fe42a`, and fast-forwarded this workstream through `git rebase origin/main`.
The updated workflow definition adds brief/claim operations; read and applied.
Mail and owned open bug queues were empty. Workflow commands run from the root.

## Planned Next Step

Scope the R-UPGRADE-002 operational slice with the owner: independent monitor
and alert routes, incident ownership, thresholds and supported adapter inventory.
The current checkpoint is on main and its public endpoint passed client acceptance.
Do not archive while accepted follow-up remains, begin external service setup
without those decisions, or resume maintenance automatically.

## Validation And External State

First hosted publication acceptance, 2026-09-21 around 21:50 UTC:
- Owner-supplied artifact URL returned HTTP 403 because its signed access expired
  at 21:36:13 UTC. The ZIP itself could not be inspected or compared; its signed
  URL is deliberately not retained.
- Both public raw files returned HTTP 200 and byte-matched `origin/component-status`
  at `c23ed99`. Feed SHA-256:
  `afe4cb969bf826413ab39fd1f693c5789621058d04cf65d8e8b6fab904da211f`.
- Format 1 parsed with the production `StatusFeed` parser and was current.
  Generated 2026-09-21 20:50:57 UTC; expiry 2026-09-24 20:50:57 UTC.
  Source revision `fa44a2f` is the merged checkpoint and an ancestor of main.
- All six expected Linux amd64 probes were `ok`, had zero consecutive failures
  and matching check/last-success times. PyCharm advertised 2026.2.3; PostgreSQL
  reported supported major 16, latest minor 16.15 and EOL 2028-11-09 without
  inventing an installed minor or upgrade candidate. Maintained diagnoses are empty.
- Production `CompatibilityLookup` fetched, parsed and cached the real public
  feed in a temporary directory and correctly returned no matching diagnosis.
  No simulated incident was published and no installed client configuration changed.
- The generated README was inspected as Markdown. Browser rendering was not
  independently verified. This proves current publication/client consumption,
  not future schedule reliability, alert delivery or the V1 48-hour objective.


Hosted-acceptance record checkpoint: required `nox -s build` passed after main
synchronization (1,035 tests, 18 deselected, one existing xfail, mypy and nine
packaged tests); `/tmp/component-status-hosted-acceptance-build.log`. Only status
records changed. These records travel with the next deliverable; no records-only
PR is needed.

Documentation/rules checkpoint gate: `nox -s build` passed again (1,033 tests,
18 deselected, one existing xfail; mypy 165 files and nine packaged tests).
Log: `/tmp/component-freshness-docs-build.log`. Local documentation links and
whitespace checked; only the previously recorded unrelated missing sample README
in the root index remains. No production code changed in this checkpoint.
The dirty-tree build produced the local validation PEX, not a revision-stamped
release artifact. Mail was empty before handoff.

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

Older clients predating fallback support need one normal CLI upgrade. Authenticated
agent/interactive IDE acceptance and release sequencing remain with the owner.
The V1 monitor/provider, notification routes, operational owner and alert timing
need owner decisions before external services are configured.

### Weighed And Unresolved

GitHub-rendered branch page avoids coupling status to the existing Pages sites.
Current probes do not certify every old adapter; maintained diagnoses retain
explicit old IDs and review deadlines. No independent vulnerability feed,
additional installation adapter or "upgrade all" command is claimed here.
The current 72-hour metadata expiry is not a 48-hour freshness guarantee.
Probe failures do not fail the action; no independent monitor or verified email
route exists. R-UPGRADE-002 preserves the intended operational work explicitly.
Vendor state migrations and manually deleted recovery resources retain earlier
rollback limitations. No product decision blocks review.

### Deliberately Not Preserved

No chat transcript or accounts were created. Contracts, operator instructions and
validation records retain the decisions. Earlier local previews remain observations; the hosted acceptance above is
separate deployed-service evidence. The expired signed artifact URL is not retained.

## Workstream Document Index

- [Freshness explanation](../../../docs/guides/component-freshness.md): user/developer signals, actions and current limits.
- [R-UPGRADE-002](../../requirements/product/r-upgrade-002-status-operational-reliability.md): accepted V1 operational follow-up.
- [Status service](../../../component-status/README.md): v1 contract, publication and maintenance operations.
- [Work order](../../work-orders/2026-09-21-component-upgrades.md): scope and finish criteria.
- [User guide](../../../docs/guides/component-upgrades.md): ordinary CLI journey and limits.
- [D-0010](../../decisions/product/d-0010-developer-owned-version-sets.md): owner decision and historical refinements.
- [R-UPGRADE-001](../../requirements/product/r-upgrade-001-component-version-sets.md): canonical contract.
- [Channel/implementation contract](../../implementation-notes/devcapsule/2026-09-21-component-distribution-channels.md): contributor interface and ownership/recovery mechanisms.
- [Validation record](../../implementation-notes/devcapsule/2026-09-21-component-upgrades-validation.md): observed real run, tests, limits and reproduction.
- [Intake dispositions](intake-dispositions.md): received-work decisions.
- [Intake instructions](intake/README.md): mail delivery.
