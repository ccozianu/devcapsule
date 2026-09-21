---
id: R-UPGRADE-001
title: Local Component Upgrades And Recoverable Version Sets
type: requirement
kind: concrete-requirement
status: implemented
priority: wanted
source_of_truth: repo
verification: [tests, manual]
external_refs: []
---

# R-UPGRADE-001: Local Component Upgrades And Recoverable Version Sets

## Statement

A developer can discover component candidates, preview an exact version set,
prepare and explicitly select it locally, and return to a locally known-good
set through the ordinary launch path. Selection preserves platform, immutable
base, unrelated components, recipe and artifact identities across later project
recommendation changes. Personal upgrades never implicitly edit the committed
project recommendation.

Upstream availability/status, DevCapsule validation provenance and local
successful use are separate facts. Explicitly unvalidated selection is allowed;
structural compatibility, platform/dependency constraints, acquisition consent
and artifact integrity remain enforced. Components declare a channel or explain
why checks are unavailable. Offline launches need no online update check.
Reminders can be deferred/dismissed and remember that choice.

Owner refinement, 2026-09-21: when a component channel explicitly reports a
security or end-of-support notice affecting the selected version, ordinary
interactive launch elicits the developer's decision. Offer an exact preview and
confirmed upgrade for that launch, a remembered deferral/dismissal, and stopping
launch. Confirmation discloses validation gaps; changed acquisition consent is
separate. Failed preparation preserves the usable selection and asks before
continuing. A notice without a replacement still offers a decision.

Discovery must not require the developer to run a separate command first:
interactive launch attempts a daily refresh, with an explicit skip option and
cached fallback. Noninteractive launch neither prompts nor upgrades and performs
no automatic channel request. A failed refresh does not clear known notices or
claim the installed version is current. Applicability, source and check time
remain visible. Routine reminders do not duplicate a critical decision; new
notices can surface despite an older routine dismissal. The initial implementation
consumes typed notices from installed channel adapters; an independent security
feed is not included. Version age and availability alone are not security facts.

Preparation and activation preserve the prior usable choice on failure. Only
zero-exit ordinary launches establish known-good use, from inputs captured before
launch. An old session finishing after a newer selection cannot certify the
newer selection. Exact recovery resources are retained; missing resources are
explained without destroying the current choice. Rollback preserves current
host permissions and personal/project state. It does not promise reversal of
vendor state migrations.

Following the project recommendation again and exporting a reviewable upstream
proposal are explicit operations. Export qualifies local-use evidence and does
not commit, publish or open a PR.

Owner refinement after dogfood inspection, 2026-09-21: the CLI distinguishes
launcher and runtime contexts. The launcher supplies a read-only configuration
directory mount with the selected checkout identity and host/runtime path mapping.
Runtime `versions show` reports the immutable running-session set separately from
the live next-launch selection; `config list` reads recorded configuration without
host filesystem validation or recovery writes. Mutations and operations requiring
launcher-owned state give an actionable launcher command. Old capsules lacking the
mount receive relaunch guidance rather than raw missing-XDG-file errors. Nested
launchers remain usable for other projects. The shared record-directory exposure
is documented under R-PRODUCT-002.

## Authority And Scope

Owner extension, 2026-09-21: vendor discovery covers all curated components even
when upgrade delivery is not implemented. Vendor interfaces are maintained
integrations, not promises of stable third-party APIs. DevCapsule owns a stable,
versioned compatibility feed and human status page, published by a scheduled
GitHub Action independently of CLI releases. A failed vendor check may consult
that feed for a diagnosis applicable to the installed adapter, CLI and platform:
released CLI fix, known issue/workarounds, or no known diagnosis. Discovery
failure does not establish installed-component health. Metadata never installs
code, changes channels or selects software. Feed and diagnosis freshness remain
explicit; stale/unavailable/malformed guidance cannot become a current upgrade
recommendation. Preserve last successful local checks and offline launches.
Backend observations and maintained diagnoses are separate. An isolated probe
failure never automatically creates an upgrade recommendation. The feed contract
must remain available to old clients across future schema changes. This extends
the original discovery scope, not the base/IDE installation scope.

[D-0010](../../decisions/product/d-0010-developer-owned-version-sets.md) records
the owner's direction. The [work order](../../work-orders/2026-09-21-component-upgrades.md)
sets the first slice: Codex through the generic channel contract, without base
or IDE upgrade delivery, launcher self-update or account/state migrations.
R-PRODUCT-002 and R-COMPAT-001 continue to govern host access and old inputs.

## Verification

- `tests/test_component_status.py` covers adapter/CLI/platform matching, unknown
  schemas, invalid metadata, freshness, offline cache, vendor signals and partial
  backend failures. `tests/test_version_sets.py` verifies the ordinary CLI
  fallback preserves software selection and prior successful-check evidence.
- [Status service contract and operations](../../../component-status/README.md)
  defines publication, schema compatibility and maintained diagnosis review.

- `tests/test_version_sets.py` drives production commands through configuration,
  acquisition, materialization and controlled external Docker/GUI boundaries,
  for Codex and an unrelated component. It verifies exact ordinary launch inputs,
  failed/interrupted preparation, repeated recovery, artifact loss, upstream
  divergence, proposal export, remembered reminders and current permissions.
- The same suite exercises terminal decisions through the shared `Elicitor`,
  automatic discovery, same-launch selection and recovery, failed preparation,
  declined consent, EOF, no replacement, offline fallback and noninteractive use.
- `tests/test_distribution_channels.py` covers metadata admission, omission,
  platform handling, exact pinning and integrity through the acquisition engine.
- Existing released-input fixtures remain in the configuration and release
  compatibility suites.
- [Host evidence and its practical limits](../../implementation-notes/devcapsule/2026-09-21-component-upgrades-validation.md) record the observed Codex upgrade and rollback; passing self-authored tests is not product-owner acceptance.
