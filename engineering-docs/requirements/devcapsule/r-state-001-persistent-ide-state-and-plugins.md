---
id: R-STATE-001
title: Persistent IDE State And Plugins
type: requirement
kind: concrete-requirement
status: implemented
priority: MVP
source_of_truth: repo
verification:
  - doc-review
  - manual
external_refs: []
---

# R-STATE-001: Persistent IDE State And Plugins

## Statement

PyCharm settings, IDE-local home state, and installed plugins must persist
outside the image across container runs and rebuilds. Shared state must be
separated from lock-bearing or project-specific runtime state when required by
the IDE vendor.

## Implementation

- `docker4pycharm/run-pycharm-container.sh`
- `docker4pycharm/entrypoint.sh`
- `docker4pycharm/README.md`

## Verification

- Manual validation depends on the specific state path and launch mode
- Shared `idea.config.path` concurrency is explicitly not required

## Related

- `engineering-docs/design-notes/docker4pycharm/2026-06-21-per-project-ide-state-split.md`
- `engineering-docs/bugs/docker4pycharm/2026-06-24-concurrent-projects-shared-global-settings-lock.md`
