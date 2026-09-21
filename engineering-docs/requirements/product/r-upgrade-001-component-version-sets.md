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

## Authority And Scope

[D-0010](../../decisions/product/d-0010-developer-owned-version-sets.md) records
the owner's direction. The [work order](../../work-orders/2026-09-21-component-upgrades.md)
sets the first slice: Codex through the generic channel contract, without base
or IDE upgrade delivery, launcher self-update or account/state migrations.
R-PRODUCT-002 and R-COMPAT-001 continue to govern host access and old inputs.

## Verification

- `tests/test_version_sets.py` drives production commands through configuration,
  acquisition, materialization and controlled external Docker/GUI boundaries,
  for Codex and an unrelated component. It verifies exact ordinary launch inputs,
  failed/interrupted preparation, repeated recovery, artifact loss, upstream
  divergence, proposal export, remembered reminders and current permissions.
- `tests/test_distribution_channels.py` covers metadata admission, omission,
  platform handling, exact pinning and integrity through the acquisition engine.
- Existing released-input fixtures remain in the configuration and release
  compatibility suites.
- [Host evidence and its practical limits](../../implementation-notes/devcapsule/2026-09-21-component-upgrades-validation.md) record the observed Codex upgrade and rollback; passing self-authored tests is not product-owner acceptance.
