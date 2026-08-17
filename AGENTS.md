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

Work means editing files in a **checkout**: one local clone directory. A
checkout has one current branch, that branch belongs to one workstream, and so
a checkout has at most one selected workstream at a time. A checkout may work
on many workstreams over time by switching branches from a clean tree, but
never on two at once. Concurrency comes from several human/agent pairs in
several checkouts integrating through the shared remote, not from any local
arrangement of directories, which is an implementation detail and not workflow
state. See *Checkouts, Branches, And Workstreams* in `WORKFLOW.md`.

This workflow is incomplete by admission, and `WORKFLOW.md` opens with
*Latitude Where This Document Is Silent*. Where the protocol does not cover a
situation, what it does not expressly deny is allowed: resolve it with judgment
and keep working rather than stalling. This never overrides an instruction to
stop, ask, refrain, or seek authority, and it does not license working around a
rule you merely find inconvenient. Whenever you do exercise that latitude,
record in the selected handoff what was missing and what you did, and hand the
gap to the workflow-owning workstream when it would recur in any project.

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

The checked-out branch is the persistent local workstream selection; there is
no separate untracked selection file. `main`, detached
HEAD, and unregistered branches have no default editing workstream. If the
selected workstream differs from the current branch, move to that branch in a
clean checkout before editing. Treat a branch-to-registry mismatch as invalid
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
and this workstream has not yet dispositioned. A handoff read without its
intake is an incomplete picture of what the workstream owns.

Every item ends one of two ways. Either the workstream **acknowledges** it,
making it a requirement or task in its own handoff, or it **forwards** it to
`project-management` with a reason. Deferral is not a third outcome; an item
accepted for later is acknowledged with its position recorded. Either outcome
is recorded in the workstream's `intake-dispositions.md` in the same outbox
commit that removes the item, so that on `main` every delivered item is either
still in `intake/` or in that log — which is how a sender learns what happened
to what it sent. Items sent by
`project-management` cannot be forwarded, because that workstream is
authoritative for what is worked on, by whom, and in what order; raise genuine
disagreement with the human instead. Either way, the recipient deletes the item
from `main` through its outbox, and no workstream may be concluded while items
remain in its intake. Follow `WORKFLOW.md` for how items are written,
delivered, and dispositioned.

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

When leaving a workstream, pause it deliberately rather than simply stopping:
commit everything, update the handoff, send anything owed through the outbox,
and write *Open Threads* — questions awaiting the human, options weighed but
unresolved, and what is deliberately not preserved. Only the pair stopping work
knows whether a thread finished or was suspended, and only while they are still
stopping. On resuming, read *Open Threads* before planning, and re-verify what
the handoff claims about external state rather than trusting it. See *Workstream
States, Pausing, And Resuming* in `WORKFLOW.md`.

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
workstream's dirty or independent source state. Use the appropriate Git branch, and treat the
committed root registry as eventually consistent rather than as live presence
or locking. How many checkouts exist locally is your own implementation detail
and is not workflow state. Follow `WORKFLOW.md` for routing,
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
