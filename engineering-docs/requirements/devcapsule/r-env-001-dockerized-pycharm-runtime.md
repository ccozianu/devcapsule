---
id: R-ENV-001
title: Dockerized PyCharm Runtime
type: requirement
kind: concrete-requirement
status: manually validated
priority: MVP
source_of_truth: repo
verification:
  - manual
external_refs: []
---

# R-ENV-001: Dockerized PyCharm Runtime

## Statement

PyCharm must run inside a Docker container while preserving enough of the
normal IDE experience for real development work.

## Implementation

- `docker4pycharm/Dockerfile`
- `docker4pycharm/run-pycharm-container.sh`
- `docker4pycharm/entrypoint.sh`

## Verification

- Current-state notes in root `README.md`
- `engineering-docs/implementation-notes/docker4pycharm/debugging.md`

## Related

- `docker4pycharm/README.md`
