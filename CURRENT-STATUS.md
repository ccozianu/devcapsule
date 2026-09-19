# Current Status

DevCapsule uses `workflow-type = "multiple-streams"`. On `main`, this file is
the compact workstream list of workstreams that have begun but not ended. Detailed
state belongs in each linked workstream status file.

## Open Workstreams

| Name | Started | Goal | State | Branch association | Status file |
|---|---|---|---|---|---|
| `workflow-improvements` | 2026-08-09 | Improve the multiple-stream workflow from concrete dogfood findings during the recursive E2E cycle | active 2026-09-18; release rule merged; `maintenance` workstream, bug vocabulary, `ws-` branch vocabulary, workflow declaration, and local workflow merged; glossary and off-`main` mail drafted for owner review; four intake items remain | `ws-workflow-improvements/v1` | [workstream status](engineering-docs/wip/2026-08-09-workflow-improvements/CURRENT-STATUS.md) |
| `project-management` | 2026-08-09 | Maintain project-wide priorities, sequencing, dependencies, and lifecycle coordination | active 2026-09-18 at owner request; synchronized with origin and main; pending coordination decisions and intake remain | `project-management/coordination` | [workstream status](engineering-docs/wip/2026-08-09-project-management/CURRENT-STATUS.md) |
| `maintenance` | 2026-09-18 | Own the defects no open workstream covers, on `main` and on maintained release lines, and drive maintenance releases | active; permanent maintenance; owns 12 open bugs, all untriaged; first task is triage | `ws-maintenance/`; no branch yet | [workstream status](engineering-docs/wip/2026-09-18-maintenance/CURRENT-STATUS.md) |
| `sample-projects` | 2026-08-14 | Provide realistic sample projects as submodules that demonstrate ordinary adopter development inside DevCapsule | paused 2026-08-21 after adding human-authorized workstream-change rules; labeled fixtures are next | `sample-projects/fastapi-webapp` | [workstream status](engineering-docs/wip/2026-08-14-sample-projects/CURRENT-STATUS.md) |
| `contained-display` | 2026-08-19 | Own the capsule supervisor core (container entry process, supervised children, explicit session end, headless mode) and the capsule's own display environment, closing the host-session credential exposure — supervisor first, display as its first consumer | active; **the contained display shipped in v0.2.12 on 2026-09-14** (recipe-9 base, contained desktop by default, X11 passthrough behind `host-x11`); the X11 credential bug is resolved; remaining threads are records and follow-ups (reconnect, WSL2 opener, sample locks) | `contained-display/display-transport`; `contained-display/outbox` | [workstream status](engineering-docs/wip/2026-08-19-contained-display/CURRENT-STATUS.md) |
| `eclipse-surface` | 2026-09-09 | Add the Eclipse IDE (JDT) as a third interactive surface beside PyCharm and VSCodium, as an ordinary catalog component | open 2026-09-09; registered, entry survey recorded, awaiting product-owner scoping | `eclipse-surface/`; no branch yet | [workstream status](engineering-docs/wip/2026-09-09-eclipse-surface/CURRENT-STATUS.md) |
| `component-catalog` | 2026-08-30 | Make IDE surfaces and agent CLIs regular catalog components: a neutral `codium` interactive surface replacing the special-cased `codium_with_claude` path, then the Antigravity CLI as a default-selected, just-in-time-materialized agent component with per-checkout persistent state | active 2026-09-09; owner freezes scope at final smoke slice (PR #65); RC3 graphical successor passed and exited 0; only delivery, v0.2.11 promotion, and closure remain | `component-catalog/antigravity-cli` (current working branch); `component-catalog/outbox` | [workstream status](engineering-docs/wip/2026-08-30-component-catalog/CURRENT-STATUS.md) |
| `user-docs` | 2026-09-12 | Deliver V1 adopter documentation from first useful session through resuming work | paused 2026-09-16 for the website experiment; interim docs and blog integrated; v1 cleanup and OpenCode setup remain | `user-docs/first-session`; `user-docs/outbox` | [workstream status](engineering-docs/wip/2026-09-12-user-docs/CURRENT-STATUS.md) |
| `website` | 2026-09-16 | Deliver the website autonomy experiment: repository-owned landing/docs/blog content, independently developable website submodule, local preview and publishing mechanism | active 2026-09-19; experiment accepted, A−; website implementation backlog handed to submodule under owner exception; retains content/contract-producer tasks, parent integration and blog review | `website/initial-cut`; explicit preparation and backlog-handoff exceptions in status | [workstream status](engineering-docs/wip/2026-09-16-website/CURRENT-STATUS.md) |

Paused and blocked workstreams remain open until they conclude successfully or
unsuccessfully. The two exceptions are `project-management` and `maintenance`,
which every multiple-stream project reserves and keeps open for as long as the
mode lasts; see *The Reserved `project-management` Workstream* and *The
Reserved `maintenance` Workstream* in `WORKFLOW.md`.

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
first, use `ws-<mnemonic>/` as the branch prefix, and use an immutable
ISO-start-date and mnemonic directory name for WIP and archive records.
Branches named under the older `<mnemonic>/` prefix are renamed by their own
workstreams before the next release candidate is tagged, per *Changes* in
`WORKFLOW.md`; after that they are outside the workflow.

`project-management` was opened on 2026-08-09 as a one-off permanent workstream
before the workflow defined one. On 2026-08-16 `workflow-improvements` made it
the general rule: every multiple-stream project reserves exactly one
`project-management` workstream, created when the mode is initialized or
adopted. This repository's instance is therefore no longer an exception in
substance. It keeps one narrow adoption exception: this repository adopted
`multiple-streams` on 2026-08-08 and created the reserved workstream on
2026-08-09, so its immutable start date is one day later than initialization.
`maintenance` was reserved by `workflow-improvements` on 2026-09-18 and
created the same day, under the adoption exception `WORKFLOW.md` defines for
projects that adopted the mode before it existed.

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
