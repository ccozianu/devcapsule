---
id: R-CONC-001
title: Concurrent Project Sessions
type: requirement
kind: concrete-requirement
status: manually validated
priority: current stabilization
source_of_truth: repo
verification:
  - manual
  - smoke-tests
external_refs: []
---

# R-CONC-001: Concurrent Project Sessions

## Statement

Users should be able to run separate projects concurrently when practical. If
IDEA-family config locking prevents shared `idea.config.path` from supporting
concurrent processes, the launcher must fail before Docker startup with a clear
diagnostic and provide a documented per-project config workaround.

## Implementation

- `docker4pycharm/run-pycharm-container.sh`
- `docker4pycharm/entrypoint.sh`
- `docker4pycharm/README.md`

## Verification

- Repository-side lock preflight and path-selection smoke tests
- User accepted the documented IDEA-family limitation on 2026-06-24

## Related

- `engineering-docs/bugs/docker4pycharm/2026-06-24-concurrent-projects-shared-global-settings-lock.md`
