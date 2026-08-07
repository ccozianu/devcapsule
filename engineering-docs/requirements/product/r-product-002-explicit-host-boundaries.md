---
id: R-PRODUCT-002
title: Explicit Host Boundaries
type: requirement
kind: concrete-requirement
status: accepted
priority: current
source_of_truth: repo
verification:
  - doc-review
  - implementation-review
external_refs: []
---

# R-PRODUCT-002: Explicit Host Boundaries

## Statement

Host exposure must be explicit. Project mounts, IDE state, credentials, Docker
access, devices, networking, and other host integrations must be represented
by documented options or defaults.

## Why This Exists

The product is valuable partly because it makes host exposure visible and
deliberate instead of ambient or accidental.

## Verification

This is a concrete requirement. It is satisfied when implementation and
documentation consistently make host boundary choices explicit.

Verification evidence may include:

- user-facing documentation for each supported host exposure;
- implementation review showing the option or default exists;
- handoff or implementation-note records when isolation is intentionally
  relaxed.

## Related

- `engineering-docs/decisions/product/d-0001-capability-first-cli-model.md`
- `R-PRODUCT-001`
- `R-DOCS-002`
