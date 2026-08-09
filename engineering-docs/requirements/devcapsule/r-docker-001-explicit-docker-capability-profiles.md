---
id: R-DOCKER-001
title: Explicit Docker Capability Profiles
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

# R-DOCKER-001: Explicit Docker Capability Profiles

## Statement

Docker capability inside the IDE must be deliberate and documented: default
host Docker socket passthrough for productivity, explicit Docker-in-Docker when
isolated Docker state is needed, and explicit no-Docker mode for higher
isolation.

## Implementation

- `docker4pycharm/run-pycharm-container.sh`
- `docker4pycharm/README.md`
- root `README.md`

## Verification

- Completed-task records for explicit Docker-in-Docker validation and retired
  default passthrough validation

## Related

- `engineering-docs/design-notes/docker4pycharm/docker-in-docker-implementation-choice.md`
