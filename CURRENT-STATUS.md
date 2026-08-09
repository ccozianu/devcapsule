# Current Status

DevCapsule uses `workflow-type = "multiple-streams"`. On `main`, this file is
the compact registry of workstreams that have begun but not ended. Detailed
state belongs in each linked workstream handoff.

## Open Workstreams

| Mnemonic | Goal | State | Branch association | Handoff |
|---|---|---|---|---|
| `multi-workflow` | Establish and adopt the optional multiple-stream workflow | integrating; documentation complete, main integration pending | no conforming branch; bootstrap work occurred on the recursive branch before adoption | [workstream status](engineering-docs/wip/multi-workflow/CURRENT-STATUS.md) |
| `recursive-e2e` | Build and launch a successor DevCapsule from inside the accepted dogfood environment | paused after Stage 3 | `milestone/recursive-dogfood-e2e` (adoption exception); future branches use `recursive-e2e/` | [workstream status](engineering-docs/wip/recursive-e2e/CURRENT-STATUS.md) |

Paused and blocked workstreams remain open until they conclude successfully or
unsuccessfully.

## Coordination Baseline

The canonical public repository is
`https://github.com/ccozianu/devcapsule`. This repository adopted the
multiple-stream workflow while the recursive E2E branch already existed and
while local `main` had diverged. The existing branch is therefore the one
documented naming and registration exception.

The commit containing this transition must be integrated into `main` before a
new workstream is registered or forked. Later workstreams must be registered on
current `main` first and use their mnemonic as the branch prefix.

Other local or remote branch refs that predate this transition are inactive
legacy refs, not implicitly open workstreams. Do not resume work on one until
`main` first registers a workstream and its branch association under the new
protocol.

The workflow documentation is complete, but the
[`multi-workflow` handoff](engineering-docs/wip/multi-workflow/CURRENT-STATUS.md)
remains open until this transition is integrated into `main` and archived
through the successful-completion procedure.

## Shared Constraints

- Keep host filesystem, credentials, Docker, devices, and networking exposure
  explicit and preserve `R-SCOPE-001`, `R-DOCKER-001`, and `R-PRODUCT-002`.
- DevCapsule does not support Gemini CLI. Do not install, configure, mount
  state for, or advertise it; absence checks are permitted.
- Root `docs/` contains current user-facing documentation only. Workstream
  drafts stay beneath the selected engineering WIP directory.
