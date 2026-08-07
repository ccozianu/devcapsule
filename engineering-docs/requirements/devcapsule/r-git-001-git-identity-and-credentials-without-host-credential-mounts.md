---
id: R-GIT-001
title: Git Identity And Credentials Without Host Credential Mounts
type: requirement
kind: concrete-requirement
status: manually validated
priority: current stabilization
source_of_truth: repo
verification:
  - manual
external_refs: []
---

# R-GIT-001: Git Identity And Credentials Without Host Credential Mounts

## Statement

Git author identity and remote access must work without mounting host
`~/.gitconfig`, host `~/.ssh`, or host credential directories into the
container.

## Implementation

- `docker4pycharm/run-pycharm-container.sh`
- `docker4pycharm/entrypoint.sh`
- `docker4pycharm/README.md`

## Verification

- 2026-06-28 manual validation for host Git identity import and explicit
  overrides
- 2026-06-30 manual validation for missing-host-identity edge cases
- Live GitHub SSH/HTTPS remote validation remains intentionally deferred from
  the v0 stabilization pass

## Related

- `engineering-docs/design-notes/docker4pycharm/2026-06-22-git-identity-and-credentials.md`
- `engineering-docs/completed-tasks/docker4pycharm/2026-06-28-git-remote-validation-deferred.md`
- `engineering-docs/completed-tasks/docker4pycharm/2026-06-30-local-git-identity-edge-validation.md`
