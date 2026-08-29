# DevCapsule Requirements Overview

This file is the overview and index for `devcapsule` implementation
requirements. Read it first for scope, status, and current priorities. The
canonical detailed record for each subproject requirement lives under:

```text
engineering-docs/requirements/devcapsule/
```

This subproject keeps the existing implementation requirement IDs and status
vocabulary so historical traceability remains intact while the documentation
model matches the root requirement structure.

## Scope

`devcapsule` is the active Python CLI/framework subproject. These requirements
describe the active implementation scope: user-facing CLI behavior, packaging,
runtime planning, build behavior, validation expectations, and the current V1
(`python_mvp`) target.

Historical PyCharm MVP context remains useful and is still referenced by some
requirements, but `docker4pycharm/` is now the reference baseline rather than
the active implementation surface.

## Requirement Types

This subproject distinguishes:

- high-level goals: scope-setting or architecture-setting requirements judged
  against accumulated evidence;
- concrete requirements: testable behaviors, constraints, or deliverables,
  even when some validation remains manual.

## Status Values

- `proposed`: captured, but not yet accepted as a project requirement.
- `accepted`: accepted, but not yet implemented.
- `implemented`: code or docs exist, but validation is incomplete.
- `repo-validated`: static checks, smoke tests, or automated checks passed.
- `manually validated`: the user or agent validated behavior in the running
  product.
- `deferred`: accepted direction, but intentionally outside the current target.
- `rejected`: considered and intentionally not pursued.

## Priority Bands

- `MVP`: required for the first useful Dockerized PyCharm workflow.
- `current stabilization`: required before closing the active V1 /
  `python_mvp` stabilization pass.
- `later`: useful, but not required for the current target.

## Current Requirement Snapshot

Already met or substantially in place:

- PyCharm container runtime baseline and persistent state model.
- Explicit host filesystem and Docker-capability boundaries.
- Development tooling baseline, Git identity flow, and concurrent-project
  handling for the validated PyCharm baseline.
- Configuration-first CLI, source install path, PEX distribution path, and the
  shared Python command/framework base.
- Documentation/process rules for user-visible behavior and durable project
  memory.

Still open for the active V1 target:

- `R-PYTHON-MVP-003` — accepted V1 scope still needs to be fully closed.
- `R-IMAGE-BUILD-001` — the Python-native composable image-build path is still
  the main open architectural requirement.

Explicitly later or deferred:

- `R-DOCS-001` — generated documentation index from frontmatter metadata.

The implementation-agnostic requirement for copied per-IDE profile prototypes
is indexed by the root `REQUIREMENTS.md`; its implementation target remains to
be assigned.

## Requirement Index

### Historical Baseline And Runtime Constraints

- `R-ENV-001` — [Dockerized PyCharm Runtime](../engineering-docs/requirements/devcapsule/r-env-001-dockerized-pycharm-runtime.md)
- `R-STATE-001` — [Persistent IDE State And Plugins](../engineering-docs/requirements/devcapsule/r-state-001-persistent-ide-state-and-plugins.md)
- `R-SCOPE-001` — [Explicit Host Filesystem Exposure](../engineering-docs/requirements/devcapsule/r-scope-001-explicit-host-filesystem-exposure.md)
- `R-DEV-001` — [Useful Development Tooling Baseline](../engineering-docs/requirements/devcapsule/r-dev-001-useful-development-tooling-baseline.md)
- `R-GIT-001` — [Git Identity And Credentials Without Host Credential Mounts](../engineering-docs/requirements/devcapsule/r-git-001-git-identity-and-credentials-without-host-credential-mounts.md)
- `R-DOCKER-001` — [Explicit Docker Capability Profiles](../engineering-docs/requirements/devcapsule/r-docker-001-explicit-docker-capability-profiles.md)
- `R-PROJECT-001` — [Per-Project IDE Runtime State](../engineering-docs/requirements/devcapsule/r-project-001-per-project-ide-runtime-state.md)
- `R-CONC-001` — [Concurrent Project Sessions](../engineering-docs/requirements/devcapsule/r-conc-001-concurrent-project-sessions.md)

### Process And Documentation

- `R-PROC-001` — [Durable Human/Agent Project Memory](../engineering-docs/requirements/devcapsule/r-proc-001-durable-human-agent-project-memory.md)
- `R-DOCS-001` — [Generated Documentation Index](../engineering-docs/requirements/devcapsule/r-docs-001-generated-documentation-index.md)
- `R-DOCS-002` — [User-Level Documentation Coevolves With User-Visible Behavior](../engineering-docs/requirements/devcapsule/r-docs-002-user-level-documentation-coevolves-with-user-visible-behavior.md)

### Active Python CLI And V1 Scope

- `R-IDE-CONFIG-001` — [Capability-First End-User CLI Model](../engineering-docs/requirements/devcapsule/r-ide-config-001-configuration-first-end-user-cli-model.md)
- `R-PYTHON-MVP-001` — [Source Checkout Install And Run](../engineering-docs/requirements/devcapsule/r-python-mvp-001-source-checkout-install-and-run.md)
- `R-PYTHON-MVP-002` — [Single-File Python CLI Artifact](../engineering-docs/requirements/devcapsule/r-python-mvp-002-single-file-python-cli-artifact.md)
- `R-PYTHON-MVP-003` — [Python MVP Feature Scope](../engineering-docs/requirements/devcapsule/r-python-mvp-003-python-mvp-feature-scope.md)
- `R-IMAGE-BUILD-001` — [Python-Native Composable Image Building](../engineering-docs/requirements/devcapsule/r-image-build-001-python-native-composable-image-building.md)
- `R-FRAMEWORK-001` — [Shared Python DevCapsule Orchestration](../engineering-docs/requirements/devcapsule/r-framework-001-shared-python-docker4ide-orchestration.md)
- `R-COMPAT-001` — [Client Upgrades Require No User Action For Existing Projects](../engineering-docs/requirements/devcapsule/r-compat-001-client-upgrades-require-no-user-action.md)

## Maintenance Rules

- Read `devcapsule-src/REQUIREMENTS.md` first for orientation.
- Open only the detailed requirement files relevant to the current task.
- Keep this file concise: overview, grouping, status framing, and links.
- Keep canonical detail in `engineering-docs/requirements/devcapsule/`.
