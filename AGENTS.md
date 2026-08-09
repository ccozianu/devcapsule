# Agent Instructions

Before starting work in this repository, read the developer brief at:

```text
README.md
```

Then read the top-level `workflow-type` field in:

```text
.devcapsule/devcapsule.toml
```

The supported values are `single-stream` and `multiple-streams`; a missing
field means `single-stream`. Treat any other value as invalid and ask the user
to correct it rather than guessing which handoff protocol applies.

Then read the root project status at:

```text
CURRENT-STATUS.md
```

In `single-stream` mode, treat it as the active project handoff. In
`multiple-streams` mode, treat it as the open-workstream registry, select the
workstream explicitly named by the user or unambiguously associated with the
current branch prefix or documented adoption exception, and read
the handoff linked from its registry row at
`engineering-docs/wip/YYYY-MM-DD-MNEMONIC/CURRENT-STATUS.md`. The date is the
workstream's immutable start date. Explicit user intent takes precedence over
branch inference but does not authorize mixing two workstreams' dirty state.
Ask the user to select a workstream only when several remain plausible and the
choice materially changes the work.

Pay special attention to the selected handoff's current stage, current state,
and planned next step. Then read any target-specific documents referenced
there and any declared cross-workstream dependency needed for the selected
slice.

After reading the required documents, acknowledge to the user that you
understand what the project is about, including the requirements and
specification described in the brief.

Treat `REQUIREMENTS.md` as the overview/index for root requirements. Read the
specific detailed files under `engineering-docs/requirements/product/` only as
needed for the task you are working on.

If the selected handoff defines a planned next step, state that next step to
the user before proceeding.

If the selected handoff does not define a planned next step, remind the user
through the agent or IDE plugin to help choose the next step to work on.

At an appropriate moment, such as when completing a stage, changing the project
state materially, or ending a session, do your best to update the selected
handoff so the next agent/model pair can resume from the then-current state. In
`single-stream` mode this is `CURRENT-STATUS.md`. In `multiple-streams` mode,
routine progress updates only the selected workstream handoff;
`CURRENT-STATUS.md` changes when a workstream opens, pauses, resumes, blocks,
integrates, completes, changes routing, or creates a repository-wide
coordination fact. Update `README.md` only when stable, developer-facing project
information changes.

In `multiple-streams` mode, do not edit from a checkout carrying another
workstream's dirty or independent source state. Use the appropriate Git branch
and worktree, and treat the committed root registry as eventually consistent
rather than as live presence or locking. Follow `WORKFLOW.md` for routing,
main-first registration, branch ownership, WIP documentation, completion,
integration, and recovery rules.

When a selected workstream is ready to integrate, treat preparation,
policy-permitted branch synchronization, mechanical conflict resolution, final
document moves, and validation as normal agent work. Pull-request delivery is
the default unless repository policy or the selected handoff explicitly allows
direct-main integration. Follow the repository's configured merge strategy or
merge queue; do not impose a rebase or fast-forward policy on a pull-request
workflow. Ask the human when intent is required or credentials, approval,
branch protection, or repository policy prevent the next operation. Never
force-push `main`. A workstream is not completely done until remote `main`
contains its finalized tree.

The repository-level documentation index lives at:

```text
index.md
```

Whenever you add, delete, rename, or move a permanent `.md` file, update
`index.md` in the same change so it continues to list permanent documentation
using relative links grouped by category. In `multiple-streams` mode,
`index.md` lists each WIP or archived workstream `CURRENT-STATUS.md` but not
every internal workstream document. Maintain the internal WIP/archive document
list in that workstream's status file. On successful promotion to permanent
locations, add the promoted documents to `index.md`.

Persist a consequential chat or working session beneath the relevant scope in
`engineering-docs/session-records/` only when the user explicitly requests it.
Default to a detailed, sanitized agent-authored record; use a summary when
requested, and call a record verbatim only when the user or IDE supplies an
export. Follow `WORKFLOW.md` and the directory README, keep canonical
decisions, requirements, and status in their normal files, and update
`index.md`.
