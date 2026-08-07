---
id: R-DEV-001
title: Useful Development Tooling Baseline
type: requirement
kind: concrete-requirement
status: manually validated
priority: MVP
source_of_truth: repo
verification:
  - manual
  - repo-review
external_refs: []
---

# R-DEV-001: Useful Development Tooling Baseline

## Statement

The image must include common Linux development and debugging tools so IDE-side
agents can make progress without repeatedly stopping for missing basic
dependencies. Tools such as `sudo` must be enabled only through explicit
development profiles.

## Implementation

- `docker4pycharm/Dockerfile`
- `docker4pycharm/run-pycharm-container.sh`
- `docker4pycharm/check-runtime-deps.sh`

## Verification

- Repository-side helper checks recorded in root `README.md`
- User manually accepted the rebuilt development baseline on 2026-06-28

## Related

- `engineering-docs/design-notes/docker4pycharm/2026-06-24-python-project-ux-defaults.md`
- `engineering-docs/design-notes/docker4pycharm/2026-06-24-development-sudo-profile.md`
