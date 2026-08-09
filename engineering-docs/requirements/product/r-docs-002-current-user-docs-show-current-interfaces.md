---
id: R-DOCS-002
title: Current User Docs Show Current Interfaces
type: requirement
kind: concrete-requirement
status: accepted
priority: current
source_of_truth: repo
verification:
  - doc-review
  - manual-review
external_refs: []
---

# R-DOCS-002: Current User Docs Show Current Interfaces

## Statement

Current user-facing documentation must show the supported interface for the
active implementation and must not require readers to infer whether an old
command shape or historical note still applies.

## Why This Exists

Users should not have to reverse-engineer the current supported path from
historical material.

## Verification

This is a concrete requirement. It is satisfied when active user docs point to
supported commands and current behavior only, while historical notes remain
clearly historical.

Verification evidence may include:

- active user docs point to supported commands only;
- intentionally unsupported or historical command paths are absent from current
  instructions;
- historical notes are clearly separated from current usage docs.

## Related

- `R-DOCS-001`
- `R-PRODUCT-002`
