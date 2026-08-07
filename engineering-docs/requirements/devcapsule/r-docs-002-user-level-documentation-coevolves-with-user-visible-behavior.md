---
id: R-DOCS-002
title: User-Level Documentation Coevolves With User-Visible Behavior
type: requirement
kind: concrete-requirement
status: implemented
priority: current stabilization
source_of_truth: repo
verification:
  - doc-review
external_refs: []
---

# R-DOCS-002: User-Level Documentation Coevolves With User-Visible Behavior

## Statement

Any change to user-visible behavior must update the relevant user-level
documentation in the same change.

## Implementation

- User-level documentation protocol in `WORKFLOW.md`
- `devcapsule-src/README.md`
- root `README.md`

## Verification

- Review the relevant requirement overview, user README, and root handoff
  together before closing user-visible changes

## Related

- `R-PROC-001`
- `R-PYTHON-MVP-003`
