# Current Status

DevCapsule uses `workflow-type = "multiple-streams"`. On `main`, this file is
the compact registry of workstreams that have begun but not ended. Detailed
state belongs in each linked workstream handoff.

## Open Workstreams

| Mnemonic | Started | Goal | State | Branch association | Handoff |
|---|---|---|---|---|---|
| `recursive-e2e` | 2026-08-06 | Build and launch a successor DevCapsule from inside the accepted dogfood environment | active; Stage 4 ready to begin | `recursive-e2e/stage-4`; the initial milestone branch is a historical adoption exception | [workstream status](engineering-docs/wip/2026-08-06-recursive-e2e/CURRENT-STATUS.md) |
| `workflow-improvements` | 2026-08-09 | Improve the multiple-stream workflow from concrete dogfood findings during the recursive E2E cycle | active; intake ready | `workflow-improvements/intake` | [workstream status](engineering-docs/wip/2026-08-09-workflow-improvements/CURRENT-STATUS.md) |
| `project-management` | 2026-08-09 | Maintain project-wide priorities, sequencing, dependencies, and lifecycle coordination | active; permanent coordination | `project-management/coordination` | [workstream status](engineering-docs/wip/2026-08-09-project-management/CURRENT-STATUS.md) |
| `sample-projects` | 2026-08-14 | Provide realistic sample projects as submodules that demonstrate ordinary adopter development inside DevCapsule | active; first sample in progress | `sample-projects/fastapi-webapp` | [workstream status](engineering-docs/wip/2026-08-14-sample-projects/CURRENT-STATUS.md) |

Paused and blocked workstreams remain open until they conclude successfully or
unsuccessfully.

## Coordination Baseline

The canonical public repository is
`https://github.com/ccozianu/devcapsule`. This repository adopted the
multiple-stream workflow while the recursive E2E branch already existed and
while local `main` had diverged. The existing branch is therefore the one
documented naming and registration exception.

The workflow transition reached `main` through
[`PR #8`](https://github.com/ccozianu/devcapsule/pull/8) at merge revision
`b648623`; its date-prefixed layout and checkout-selection refinements reached
`main` through [`PR #9`](https://github.com/ccozianu/devcapsule/pull/9) at merge
revision `ed30a58`. Later workstreams must be registered on current `main`
first, use their mnemonic as the branch prefix, and use an immutable
ISO-start-date and mnemonic directory name for WIP and archive records.

Other local or remote branch refs that predate this transition are inactive
legacy refs, not implicitly open workstreams. Do not resume work on one until
`main` first registers a workstream and its branch association under the new
protocol.

## Shared Constraints

- Keep host filesystem, credentials, Docker, devices, and networking exposure
  explicit and preserve `R-SCOPE-001`, `R-DOCKER-001`, and `R-PRODUCT-002`.
- DevCapsule does not support Gemini CLI. Do not install, configure, mount
  state for, or advertise it; absence checks are permitted.
- Root `docs/` contains current user-facing documentation only. Workstream
  drafts stay beneath the selected engineering WIP directory.
