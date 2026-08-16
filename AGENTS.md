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
`multiple-streams` mode, treat the copy on the locally accepted mainline ref as
the open-workstream registry; this is normally current local `main`, or fetched
remote-tracking `main` when it is newer and authoritative. Do not rely on a
potentially stale registry copy on a long-lived workstream branch, and do not
choose silently if mainline refs have diverged. Select the workstream explicitly
named by the user or unambiguously associated with the current branch prefix or
documented adoption exception, and read the handoff linked from its registry
row at
`engineering-docs/wip/YYYY-MM-DD-MNEMONIC/CURRENT-STATUS.md`. The date is the
workstream's immutable start date. Explicit user intent takes precedence over
branch inference but does not authorize mixing two workstreams' dirty state.
Ask the user to select a workstream only when several remain plausible and the
choice materially changes the work.

Every `multiple-streams` project has exactly one reserved `project-management`
workstream, created when the mode is initialized or adopted and open for as
long as the mode lasts. It owns project-wide priorities, sequencing,
cross-workstream dependencies, and lifecycle decisions; it is not a second
registry, not an implementation catch-all, and not the owner of other
workstreams' state. Select and work in it exactly as you would any other
workstream. If a project declares `multiple-streams` and has no such
workstream, report that it is incompletely initialized rather than working
around it. See *The Reserved `project-management` Workstream* in `WORKFLOW.md`.

The checked-out branch and worktree are the persistent local workstream
selection; there is no separate untracked selection file. `main`, detached
HEAD, and unregistered branches have no default editing workstream. If the
selected workstream differs from the current branch, move to its clean branch
or worktree before editing. Treat a branch-to-registry mismatch as invalid
routing and stop rather than guessing.

Pay special attention to the selected handoff's current stage, current state,
and planned next step. Then read any target-specific documents referenced
there and any declared cross-workstream dependency needed for the selected
slice.

In `multiple-streams` mode, synchronize the selected workstream's branch with
`main` before planning the session's work, normally by rebasing. `main` is how
intake, registrations, and repository-wide coordination facts reach a
workstream, and a stale branch cannot act on items it can nonetheless see. To
send work the other way — an intake item for another workstream, or a new
workstream's registration — use the sender's standing `<mnemonic>/outbox`
branch, reset from current `main` and carrying only what is being sent, never
working changes. See *The Outbox Branch* and *Staying Current With `main`* in
`WORKFLOW.md`.

In `multiple-streams` mode, also read the selected workstream's `intake/`
directory beside its handoff. It holds work other workstreams have delivered
and this workstream has not yet accepted, deferred, or rejected. A handoff read
without its intake is an incomplete picture of what the workstream owns. Follow
`WORKFLOW.md` for how items are written, delivered, and dispositioned.

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
