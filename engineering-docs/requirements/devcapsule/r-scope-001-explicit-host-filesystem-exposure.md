---
id: R-SCOPE-001
title: Explicit Host Filesystem Exposure
type: requirement
kind: concrete-requirement
status: implemented
priority: MVP
source_of_truth: repo
verification:
  - implementation-review
  - doc-review
external_refs: []
---

# R-SCOPE-001: Explicit Host Filesystem Exposure

## Statement

The IDE container must not mount arbitrary host directories. Host filesystem
exposure should be limited to the selected project, IDE state, plugins, and
narrowly scoped runtime or credential resources.

## Implementation

- `docker4pycharm/run-pycharm-container.sh`
- root `README.md`
- `docker4pycharm/README.md`

## Verification

- Review launcher Docker arguments and docs together when changing mounts

## Related

- Root `R-PRODUCT-002`
