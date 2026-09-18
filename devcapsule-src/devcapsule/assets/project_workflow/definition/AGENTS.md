# Agent Instructions

Before starting work, read `README.md`, then read the top-level
`workflow-type` field in `.devcapsule/devcapsule.toml`. Supported values are
`single-stream` and `multiple-streams`; a missing field means `single-stream`.
Treat any other value as invalid.

Read `WORKFLOW.md` for the reusable protocol, starting with its *Vocabulary*,
and `CURRENT-STATUS.md` for this project's live state. In single-stream mode, `CURRENT-STATUS.md` is the active
handoff. In multiple-streams mode, it is the mainline registry: select the one
workstream associated with the user's request and current branch, then read its
`engineering-docs/wip/YYYY-MM-DD-MNEMONIC/CURRENT-STATUS.md` and `intake/`.
Do not mix two workstreams' unfinished state in one checkout.

After reading, tell the user that you understand the project and state the
recorded next step before proceeding. Explicit user direction may reprioritize
that step without erasing it.

Treat `REQUIREMENTS.md` as the requirements overview and index. Read only the
detailed requirement, decision, bug, or specification records needed for the
selected task.

Keep important requirements, decisions, evidence, open questions, current
state, and next steps in repository files rather than only in chat. Update the
selected handoff at meaningful checkpoints and before pausing. In
multiple-streams mode, follow `WORKFLOW.md` for branch routing, synchronization,
intake disposition, outbox publication, and integration. A registry row whose
branch association names a `release-<version>` branch means that workstream is
driving a release: follow *Releases* in `WORKFLOW.md`, and never rebase,
force-push, or cherry-pick release refs. Every multiple-streams project has two
reserved workstreams, `project-management` and `maintenance`; report a project
missing either as incompletely initialized. Bug records under
`engineering-docs/bugs/` are routed by their frontmatter `owner` field: list
the open bugs owned by the selected workstream at session start, and file new
ones with `owner` set to the open workstream whose goal covers them, otherwise
`maintenance`. See *Bug Intake* in `WORKFLOW.md`.

The workflow is intentionally incomplete. Where it is silent, use judgment,
record the gap and the action taken in the selected handoff, and continue
unless another instruction requires stopping or asking for authority.

Maintain `index.md` when permanent Markdown files are added, removed, renamed,
or moved. Preserve existing project-specific instructions when extending this
file; refresh the reusable definition only when the developer explicitly asks.
