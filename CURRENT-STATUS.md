# Current Status

DevCapsule uses `workflow-type = "multiple-streams"`. On `main`, this file is
the compact registry of workstreams that have begun but not ended. Detailed
state belongs in each linked workstream handoff.

## Open Workstreams

| Mnemonic | Started | Goal | State | Branch association | Handoff |
|---|---|---|---|---|---|
| `workflow-improvements` | 2026-08-09 | Improve the multiple-stream workflow from concrete dogfood findings during the recursive E2E cycle | open-idle per the 2026-08-29 ruling; `WORKFLOW.md` frozen until a release candidate; seven intake items await its resume | `workflow-improvements/v1` | [workstream status](engineering-docs/wip/2026-08-09-workflow-improvements/CURRENT-STATUS.md) |
| `project-management` | 2026-08-09 | Maintain project-wide priorities, sequencing, dependencies, and lifecycle coordination | active; permanent coordination | `project-management/coordination` | [workstream status](engineering-docs/wip/2026-08-09-project-management/CURRENT-STATUS.md) |
| `sample-projects` | 2026-08-14 | Provide realistic sample projects as submodules that demonstrate ordinary adopter development inside DevCapsule | paused 2026-08-21 after adding human-authorized workstream-change rules; labeled fixtures are next | `sample-projects/fastapi-webapp` | [workstream status](engineering-docs/wip/2026-08-14-sample-projects/CURRENT-STATUS.md) |
| `contained-display` | 2026-08-19 | Own the capsule supervisor core (container entry process, supervised children, explicit session end, headless mode) and the capsule's own display environment, closing the host-session credential exposure — supervisor first, display as its first consumer | open; not yet started; supervisor core assigned 2026-08-30, see intake | `contained-display/`; no branch yet | [workstream status](engineering-docs/wip/2026-08-19-contained-display/CURRENT-STATUS.md) |

Paused and blocked workstreams remain open until they conclude successfully or
unsuccessfully. The one exception is `project-management`, which every
multiple-stream project reserves and keeps open for as long as the mode lasts;
see *The Reserved `project-management` Workstream* in `WORKFLOW.md`.

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

`project-management` was opened on 2026-08-09 as a one-off permanent workstream
before the workflow defined one. On 2026-08-16 `workflow-improvements` made it
the general rule: every multiple-stream project reserves exactly one
`project-management` workstream, created when the mode is initialized or
adopted. This repository's instance is therefore no longer an exception in
substance. It keeps one narrow adoption exception: this repository adopted
`multiple-streams` on 2026-08-08 and created the reserved workstream on
2026-08-09, so its immutable start date is one day later than initialization.

Other local or remote branch refs that predate this transition are inactive
legacy refs, not implicitly open workstreams. Do not resume work on one until
`main` first registers a workstream and its branch association under the new
protocol.

## Shared Constraints

- Keep host filesystem, credentials, Docker, devices, and networking exposure
  explicit and preserve `R-SCOPE-001`, `R-DOCKER-001`, and `R-PRODUCT-002`.
- Release sequencing: the v026 series and v0.2.7 (the new CLI, under the
  unified release identity decided 2026-08-26) are released; `recursive-e2e`
  concluded 2026-08-27 with its remaining items dissolved into the
  project-management coordination backlog. The contained-display release
  target is open under the unified versioning. See the
  [portfolio checkpoint](engineering-docs/wip/2026-08-09-project-management/2026-08-16-portfolio-checkpoint.md)
  and the [V1 scope ledger](engineering-docs/wip/2026-08-09-project-management/v1-scope-ledger.md).
- Bases stay agent-neutral per `D-0005`: no ambient agent CLI is installed and
  no agent credential or state directory is mounted by default. Agent CLIs are
  optional components that materialize per developer after explicit
  authorization. Base agent-absence checks remain correct and apply to every
  agent, including selected ones.
- V1 curates three agent components and lets the developer choose: Claude Code,
  OpenAI Codex, and Google Antigravity CLI. Selected 2026-08-16; see the
  [V1 scope ledger](engineering-docs/wip/2026-08-09-project-management/v1-scope-ledger.md).
  This is the deliberate selection `D-0005` anticipated, not a change to it.
- Gemini CLI is not a selected component. Do not install, configure, mount state
  for, or advertise it. This is a product-boundary choice; `D-0005` verified on
  2026-08-02 that Google had not deprecated it.
- Root `docs/` contains current user-facing documentation only. Workstream
  drafts stay beneath the selected engineering WIP directory.
- No workstream holds exclusive editing rights over any file. A workstream may
  edit any file its task genuinely requires. Exclusivity applies only where a
  documented locking protocol exists and is actually used for that file; no
  such protocol exists yet, so none may be inferred from a file's subject,
  directory, or the workstream that created it. Established 2026-08-15; see the
  [portfolio checkpoint](engineering-docs/wip/2026-08-09-project-management/2026-08-15-portfolio-checkpoint.md)
  and the [coordination backlog](engineering-docs/wip/2026-08-09-project-management/coordination-backlog.md).
