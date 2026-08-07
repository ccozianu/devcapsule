---
id: R-PROJECT-001
title: Per-Project IDE Runtime State
type: requirement
kind: concrete-requirement
status: manually validated
priority: MVP
source_of_truth: repo
verification:
  - manual
external_refs: []
---

# R-PROJECT-001: Per-Project IDE Runtime State

## Statement

Volatile project workspace state, caches, logs, and default container project
mount paths must be namespaced per selected host project so opening one project
does not restore stale workspace state from another.

## Implementation

- `docker4pycharm/run-pycharm-container.sh`
- `docker4pycharm/entrypoint.sh`
- `docker4pycharm/README.md`

## Verification

- Manual validation update recorded in root `README.md`

## Related

- `engineering-docs/design-notes/docker4pycharm/2026-06-21-per-project-ide-state-split.md`
