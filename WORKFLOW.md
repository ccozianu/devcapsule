# Human / Agent Iteration Workflow

This project treats markdown files in the repository as the durable memory for
human/agent work. Conversation is useful for speed, but project state must
survive model changes, IDE restarts, and future sessions.

## Workflow Type Selection

Before interpreting project status, read the top-level `workflow-type` field in
`.devcapsule/devcapsule.toml`:

```toml
workflow-type = "single-stream"
```

The supported values are `single-stream` and `multiple-streams`. A missing
field means `single-stream`. Any other value is invalid; report it instead of
guessing which status protocol applies. The field selects repository workflow,
not runtime behavior or live contributor presence.

## Single-Stream Workflow

`single-stream` preserves the existing linear process:

- root `CURRENT-STATUS.md` is the detailed active handoff;
- it records current state, evidence, and one next resumable slice;
- routine checkpoints update that file; and
- branches and worktrees remain optional implementation tools.

The remaining general sections of this document apply as they did before
multiple-stream support was introduced.

## Multiple-Stream Workflow

### Definition And Restrictions

A workstream is a bounded set of changes developed toward one goal. It begins,
develops, and ends successfully or unsuccessfully.

The following restrictions keep concurrent work understandable:

1. Workstreams are flat. Do not create parent, child, or nested workstreams.
2. Every workstream has one unique lowercase mnemonic made from letters,
   numbers, and hyphens. Never reuse an archived mnemonic.
3. Every workstream has one immutable ISO start date: the calendar date on
   which its registration is first committed to `main`. Migration exceptions
   record their historically established start date.
4. Every branch other than `main` belongs to exactly one workstream.
5. Each workstream branch name begins with `<mnemonic>/`.
6. A workstream may have more than one branch, but every branch starts from
   `main` and is intended to return to `main` if the workstream succeeds.
7. `main` belongs to no workstream. It is the shared registration, visibility,
   finalization, and integration branch.
8. Ordinary workstream implementation does not happen directly on `main`.
9. Each open workstream has exactly one detailed handoff at
   `engineering-docs/wip/<start-date>-<mnemonic>/CURRENT-STATUS.md`.
10. Root `CURRENT-STATUS.md` on `main` lists open workstreams only. An open
   workstream remains listed while active, paused, blocked, or integrating.
11. No workstream holds exclusive editing rights over a file. A workstream may
    edit any file its task genuinely requires, and exclusivity may not be
    inferred from a file's subject, its directory, or which workstream created
    it. Two carve-outs stand: another workstream's WIP handoff directory, and
    another worktree's recovery state. Each is a workstream's account of its
    own state, which another workstream cannot restate accurately; report what
    you observe about another workstream instead of editing its record. Wider
    exclusivity applies only where a documented locking protocol exists and is
    actually used for that file. No such protocol exists today.

### Beginning A Workstream

Begin from a clean, current `main` checkout:

1. Choose the goal, unused mnemonic, and ISO start date.
2. Create
   `engineering-docs/wip/<start-date>-<mnemonic>/CURRENT-STATUS.md` on `main`.
3. Record the start date, goal, state, branch prefix, integration target,
   delivery method or applicable repository default, current task, and next
   resumable task.
4. Add the workstream to root `CURRENT-STATUS.md`.
5. Commit that source-level registration on `main`.
6. Fork the first `<mnemonic>/...` branch from that commit.
7. Perform workstream changes only on its associated branch or branches.

A branch created before the registration commit is not a valid new workstream
branch. Existing branches that predate adoption require an explicit migration
exception in their workstream status. An inactive legacy branch does not become
an open workstream merely because the ref still exists; register and associate
its continuation on `main` before committing new work to it.

### Selecting Work At Session Start

Workstream discovery and checkout selection are related but distinct:

- The open-workstream registry is read from the locally accepted mainline ref,
  not from a potentially stale copy of root `CURRENT-STATUS.md` on a long-lived
  workstream branch. The mainline ref is normally current local `main`, or a
  fetched remote-tracking `main` when it is newer and authoritative. If the
  candidates have diverged, do not choose silently; resolve the divergence
  under *Verifying Shared Branch State*. Refresh them according to repository
  policy when an operation requires current shared state; routine offline
  resumption may use the latest unambiguous locally available snapshot.
- The current worktree and its checked-out branch provide the persistent local
  selection. This first protocol deliberately defines no second untracked
  "current workstream" preference file.

Select exactly one editing workstream for the current worktree:

1. Identify the current Git worktree, branch, and dirty state, then read the
   open-workstream registry from the locally accepted mainline ref.
2. If the user explicitly names an open workstream, select it. Explicit intent
   chooses the target but does not reassign the current branch or authorize
   mixing dirty state.
3. Otherwise, when the current branch starts with `<mnemonic>/`, select the one
   open registry entry with that mnemonic. A documented adoption exception may
   provide the same unique association for a historical branch.
4. Treat a mnemonic-prefixed or excepted branch whose workstream is absent from
   the open registry, or whose registry association disagrees, as invalid
   routing. Stop before editing and report the inconsistency.
5. `main` belongs to no workstream and therefore has no default editing
   workstream. Registry coordination and repository-wide inspection may occur
   there. Workstream changes require an explicit selection followed by a switch
   to that workstream's clean branch or worktree.
6. Detached HEAD, an unregistered branch, or more than one plausible mapping
   has no default. Ask the user only when the desired workstream cannot be
   established from explicit intent and a unique registered association.
7. Follow the selected registry row's handoff link. Do not guess its start date
   from branch or commit timestamps. On the selected workstream branch, its
   committed handoff is authoritative for the latest track-local state; the
   copy reachable from `main` is the latest published snapshot.

If the selected workstream differs from the current branch, switch to its clean
worktree before editing. Do not combine dirty state from two workstreams, and
do not use a stash as their durable handoff boundary. Different users and
clones may select different workstreams independently because their checked-out
branches and worktrees are local state.

### Development And Checkpoints

The workstream handoff—not root `CURRENT-STATUS.md`—records detailed progress,
evidence, the current or last task, and the next resumable task. Routine
workstream commits update only that handoff and workstream-owned files.

Keep all unfinished workstream documentation beneath:

```text
engineering-docs/wip/<start-date>-<mnemonic>/
```

The root documentation index lists the workstream `CURRENT-STATUS.md`, not
every internal WIP document. The workstream status must contain a small local
index of its WIP documents. This avoids making `index.md` a routine conflict
point. Permanent documents are added to the root index when finalized.

Workstream documentation may be integrated into `main` before source changes
when visibility is useful. Publish documentation-only checkpoints, then
synchronize the workstream branch with the resulting `main` state before
editing the same files again. The branch handoff remains authoritative for the
latest track-local state; the copy on `main` is the latest published snapshot.

### Draft User Documentation

Root `docs/` contains only current user-facing documentation. Workstream drafts
live at:

```text
engineering-docs/wip/<start-date>-<mnemonic>/docs/
```

`docs/` is otherwise a reserved directory name beneath `engineering-docs/`.
It is allowed only inside `wip/<start-date>-<mnemonic>/` and
`archive/<start-date>-<mnemonic>/` workstream directories.

For an entirely new user document, store the actual draft under the workstream
`docs/` directory at its intended relative destination. For example:

```text
engineering-docs/wip/2026-04-12-api/docs/guides/new-guide.md
```

is intended to become:

```text
docs/guides/new-guide.md
```

For a change to an existing root `docs/` file, do not create a divergent copy.
Write a change proposal in the workstream `docs/` directory that identifies:

- the target file;
- why it must change;
- the intended semantic and material wording changes;
- implementation dependencies; and
- final verification.

Apply that proposal to the existing user document only when finalizing a
successful workstream.

### Successful Completion And Integration

Successful integration is normally mechanical agent work, but delivery to
`main` follows repository policy. A pull request is the default delivery method
unless the repository or selected handoff explicitly permits direct
integration. Do not infer permission to update `main` merely from the ability
to do so.

Before integration begins, the selected handoff records:

- the integration target, normally `main`;
- the designated integration branch;
- the delivery method: `pull-request` or `direct-main`;
- the repository's branch-synchronization and merge policy; and
- any known human-only publication, approval, or merge step.

The agent owns routine preparation, synchronization, file movement, conflict
resolution where intent is clear, and validation. Ask the human for help when
a conflict requires a product or documentation decision, repository policy is
unclear, credentials or approval are unavailable, or another condition makes
the intended result ambiguous.

#### 1. Prepare The Integration Candidate

1. Verify the designated integration branch and every involved worktree are
   clean and all accepted workstream changes are committed. Freeze that branch
   against unrelated work while integration proceeds.
2. Inspect current local and remote `main`, fetching remote refs when network
   access is available. If they have diverged, resolve it under *Verifying
   Shared Branch State*: reset only when every local commit is proven already
   upstream, and otherwise do not discard local commits or choose a side.
3. Synchronize the integration branch with current `main` according to
   repository policy. A project may require rebasing, merging `main`, a hosting
   platform's update-branch operation, or a merge queue. Pull-request delivery
   does not imply rebasing. Direct-main delivery uses the rebase and
   fast-forward procedure below.
4. Resolve mechanical conflicts. When reconciliation requires intent, preserve
   the evidence and ask the human before choosing a result.
5. Run the workstream-specific and shared validation required by the handoff.

#### 2. Finalize At The Delivery Boundary

The following file changes close the workstream and belong in one finalization
commit. For pull-request delivery, keep the workstream registry entry and WIP
handoff during ordinary review and add this commit only when the pull request
is otherwise merge-ready. For direct-main delivery, add it after rebasing and
validating the branch and before fast-forwarding local `main`.

1. Apply proposals for existing user documentation and move new user documents
   into root `docs/`.
2. Move enduring engineering records from WIP into their normal requirements,
   specifications, decisions, design notes, implementation notes, bugs, or
   other permanent categories.
3. Update links and the root documentation index.
4. Remove the workstream from root `CURRENT-STATUS.md`.
5. Create
   `engineering-docs/archive/<start-date>-<mnemonic>/CURRENT-STATUS.md`
   containing a brief successful outcome, evidence, delivery method and
   durable integration reference, residual risks, and links to permanent
   records. Preserve the same start-date-and-mnemonic directory name used in
   WIP. For a pull request, record its number or URL; the eventual merge
   revision need not be predicted before the hosting platform creates it.
6. Preserve only brief additional archive notes that have lasting value and
   remove the WIP directory.
7. Run the required checks on the complete final tree.

The finalization tree is provisional while it exists only on the workstream
branch or in an open pull request. Root `CURRENT-STATUS.md` on remote `main`
remains the authoritative open-workstream registry until delivery completes.
Never append or merge the workstream status text into that root registry.

#### 3A. Deliver Through A Pull Request

1. Publish the integration branch and open or update its pull request using the
   repository's normal tools and required base branch.
2. Address review and continuous-integration results. Resynchronize the branch
   only by methods allowed by repository policy; rerun required checks after
   any synchronization or finalization change.
3. Add the finalization commit only when the pull request is otherwise ready to
   merge, then allow any checks or approvals invalidated by that commit to run
   again.
4. Merge through the hosting platform using the repository's configured merge,
   squash, rebase, or merge-queue policy. The agent may perform this action
   when authorized; otherwise ask the human or designated reviewer.
5. Verify from the updated remote ref that `main` contains the merged final
   tree and that the workstream registry entry and WIP directory are absent.

The pull request and resulting remote history are the durable integration
record. A follow-up commit solely to predict or insert the platform-generated
merge revision is not required.

#### 3B. Deliver Directly To Main

Use this path only when repository policy or the selected handoff explicitly
permits direct integration:

1. Bring clean local `main` to the accepted remote `main` by ordinary
   fast-forward. If they have diverged, apply *Verifying Shared Branch State*.
   Reset local `main` only when every local-only commit is proven already
   upstream, reporting that evidence; otherwise stop and ask the human rather
   than choosing or discarding history.
2. Rebase the frozen integration branch onto local `main` and rerun required
   validation. Resolve mechanical conflicts and ask the human when intent is
   required.
3. Fast-forward local `main` with
   `git merge --ff-only <integration-branch>`. If this fails because `main`
   moved, do not create a non-fast-forward merge; repeat synchronization and
   rebase.
4. Push `main` normally to its integration remote, normally with
   `git push origin main`. Never force-push `main`. If credentials, approval,
   or repository policy prevent publication, ask the human to perform it. If
   remote `main` moved, fetch it and repeat the direct-integration procedure
   without force.
5. Verify that remote `main` contains the finalized integration commit.

The workstream is completely done only when remote `main` contains the final
tree produced by either delivery path. Until then, an open integration pull
request or a local `main` ahead of its remote is pending integration, not a
completed workstream. Associated worktrees and branches may be removed after
completion once their changes are reachable from remote `main`.

### Unsuccessful Completion

Do not promote unfinished source or user documentation. On `main`:

1. Publish the workstream branch's final complete WIP documentation checkpoint
   to `main` without integrating unfinished source changes.
2. Remove the workstream from root `CURRENT-STATUS.md`.
3. Move the complete
   `engineering-docs/wip/<start-date>-<mnemonic>/` tree to
   `engineering-docs/archive/<start-date>-<mnemonic>/` without changing its
   directory name.
4. Update its `CURRENT-STATUS.md` to record the unsuccessful conclusion, the
   last task, and that task's final status.
5. Record the reason for ending, associated branches and revisions, and any
   reconsideration condition when useful.
6. Update links and the root documentation index.

Draft user documentation stays inside the engineering archive and never
appears in root `docs/`.

### Integration And Recovery

Before entering the successful-completion sequence, inspect changes since the
branch point, reconcile overlaps with other open workstreams, and record the
chosen integration branch, delivery method, and applicable repository policy
in the handoff. Workstream state in Git and the hosting platform is durable but
not a live lock or presence system.

After interruption, enumerate worktrees and branches, inspect each dirty state
separately, compare local `main` with remote `main`, match branch prefixes to
workstreams, and resume from the selected workstream's last committed status.
An open integration pull request or a local finalization already
fast-forwarded to `main` but not its remote is pending integration, not a new
workstream. Treat newer uncommitted files as recovery material, not canonical
status.

Throughout the rest of this document, **selected handoff** means root
`CURRENT-STATUS.md` in `single-stream` mode and
`engineering-docs/wip/<start-date>-<mnemonic>/CURRENT-STATUS.md` in
`multiple-streams` mode. General execution-loop rules apply to both modes.

## Core Loop

1. Start each session by reading the repository brief, workflow type, root
   status, and selected handoff.
2. Read `REQUIREMENTS.md` for the requirement overview when changing behavior,
   validation scope, or priorities, then open the relevant detailed files under
   `engineering-docs/requirements/product/` as needed.
3. Work from the selected handoff's active task or next slice, not from stale
   conversation memory.
4. Keep each cycle narrow enough that the user can validate the result.
5. When the user validates something manually, update the selected handoff so
   the same task is not picked up again.
6. When an issue disappears or is deferred, remove it from the active task list
   and preserve the symptoms, logs, and reasoning in the completed-task archive.
7. Commit coherent units of work when asked, or at natural save points when the
   user wants the session state preserved.

## Release, Milestone, Stage, Task, And Checkpoint Terminology

Use these terms consistently so a saved checkpoint is not mistaken for a
product release and a broad release does not become one unbounded task.

- **Release:** an externally meaningful product version with a defined product
  contract, artifacts, documentation, and acceptance evidence. Names such as
  V1 and V2 identify releases, not milestones.
- **Milestone:** a coherent, outcome-based checkpoint on the path to a release.
  A milestone contains one or more tasks and has explicit closure criteria and
  evidence. Name it for the outcome, such as `PyCharm Functional Closure`, not
  merely for a date or arbitrary time interval.
- **Stage:** a sequential subdivision inside a milestone or execution plan.
  Stages make dependencies and ordering clear but do not create an external
  product commitment by themselves.
- **Task:** a bounded implementation, documentation, investigation, or
  validation unit within a milestone.
- **Slice:** the narrow unit selected for the current human/agent work cycle.
- **Checkpoint:** a durable state snapshot or handoff. It may preserve partial
  progress and does not imply that a task or milestone is complete.
- **Release candidate:** an actual candidate set of versioned artifacts and
  documentation subjected to release acceptance. Do not use it as another name
  for an ordinary milestone.

Requirements, decisions, and bugs are orthogonal records: requirements define
what must be true, decisions explain durable choices, and bugs preserve defect
evidence. A release selects requirements; milestones organize outcomes toward
that release; tasks and slices execute the work.

When planning a release:

1. Record a dated, revision-scoped gap review when the remaining scope needs a
   durable baseline.
2. Group accepted gaps into a small sequence of outcome-based milestones.
3. Define closure and evidence before activating a milestone.
4. In `single-stream` mode, keep `CURRENT-STATUS.md` focused on the active
   release, milestone, and next task. In `multiple-streams` mode, keep that
   detail in the selected handoff and only open-workstream discovery in the
   root registry.
5. When a milestone closes, update the selected handoff and gap review or
   successor plan without claiming that the release is complete.
6. Reserve release completion for the product-owner decision after the selected
   artifacts, documentation, and release-level acceptance evidence exist.

## Turn-Level Choreography

Use each meaningful work cycle as a small contract between the human and the
agent.

1. Frame the slice.
   - The human states the goal, constraint, or uncertainty.
   - The agent restates the target outcome, relevant assumptions, and the next
     narrow slice it intends to execute.
2. Define closure before deep work.
   - State what "done for this slice" means.
   - State what evidence will count: test output, diff review, manual
     validation, or a documented decision.
3. Execute one narrow slice.
   - Prefer one coherent change over multiple partially finished ideas.
   - If the work uncovers a larger issue, record it and either finish the
     current slice or stop at a clear checkpoint.
4. Report with evidence.
   - Lead with the result.
   - Include only the evidence the human needs to evaluate the slice.
   - Separate "done", "not done", and "needs human input".
5. Decide the next branch explicitly.
   - Continue to the next slice.
   - Ask the human to validate or choose.
   - Stop and update the selected handoff because the session reached a useful
     checkpoint.

The goal is steady throughput, not long uninterrupted agent runs with vague
status.

## Slice Sizing Rules

Prefer slices that fit one of these shapes:

- one code path plus its direct tests;
- one documentation or workflow improvement plus the matching handoff update;
- one bug reproduction or diagnosis write-up;
- one manual-validation request with exact commands and expected observations;
- one decision that removes ambiguity for later implementation work.

Avoid slices that mix several of these unless the work is trivial. If a task is
too large to validate in one pass, split it before implementation.

## Human Input Contract

The human should provide, when relevant:

- the current priority or outcome to optimize for;
- risk tolerance, especially for host access, credentials, and security
  tradeoffs;
- manual validation results that only the human can observe;
- tie-break decisions when several defensible approaches remain.

The agent should ask for human input only when it materially changes the work
or when external validation is required. Otherwise, make the smallest reasonable
assumption, state it, and continue.

## Agent Reporting Contract

For each meaningful slice, the agent should report in this order:

1. Outcome.
2. Evidence.
3. Remaining gap or risk.
4. Recommended next slice.

Keep reports concise. The user should not need to reconstruct the state from a
long chronology.

## Decision And Escalation Rules

Escalate to the human when:

- a choice changes scope, architecture, or security posture materially;
- repository evidence is insufficient and several plausible interpretations
  remain;
- external state must change outside the agent's authority;
- the next slice would otherwise become speculative or broad.

Do not escalate merely because implementation is tedious or because several
small, compatible actions are possible.

## Checkpoint Triggers

Create or refresh durable state when any of these happen:

- a stage or subtask reaches a real closure point;
- manual validation changes project state;
- a new bug, decision, or requirement appears;
- the session ends with unfinished but resumable work;
- the active next step changes.

If the user and agent are moving quickly, prefer more frequent small selected-
handoff updates over one large retrospective rewrite.

## Markdown Roles

Use markdown files with distinct responsibilities:

- `README.md`: stable, developer-facing welcome page, project overview, setup,
  and documentation entry points.
- `CURRENT-STATUS.md`: the active handoff in `single-stream` mode and the
  open-workstream registry on `main` in `multiple-streams` mode. Refresh it
  according to the selected mode's checkpoint rules.
- `REQUIREMENTS.md`: implementation-agnostic requirement overview and index for
  project-level goals and concrete requirements.
- `docs/`: stable product guidance and reference material intended for users
  and adopters.
- `engineering-docs/`: contributor- and agent-facing engineering records,
  classified by authority and purpose.
- `engineering-docs/requirements/product/`: one markdown file per root
  requirement, with frontmatter metadata and canonical detailed requirement
  text.
- Subproject requirement overviews, such as `devcapsule-src/REQUIREMENTS.md`:
  implementation-specific requirement scope, status framing, and links to the
  canonical detailed requirement records for that subproject.
- `AGENTS.md`: instructions every future agent should read before touching the
  repository.
- `engineering-docs/design-notes/`: proposals, alternatives, research, and
  unsettled implementation-scoped architecture.
- `engineering-docs/implementation-notes/`: execution plans, validation
  details, debugging history, checklists, and other evidence that should not
  clutter the active task list.
- `engineering-docs/wip/YYYY-MM-DD-MNEMONIC/`: temporary documentation and the
  detailed handoff for an open workstream in `multiple-streams` mode.
- `engineering-docs/archive/YYYY-MM-DD-MNEMONIC/`: final status and retained
  historical material for an ended workstream.
- `engineering-docs/bugs/`: one file per active or recently investigated
  bug, with symptoms, reproduction, evidence, hypotheses, verification target,
  and close criteria.
- `engineering-docs/completed-tasks/`: one file per completed, retired,
  manually validated, or no-longer-reproduced task. This is the retrospective
  archive.
- `engineering-docs/session-records/`: user-requested preservation of a
  consequential human/agent session. These records are historical context,
  not canonical decisions, requirements, handoff state, or active backlog.
- Target-specific docs such as `docker4pycharm/README.md`: operational usage
  for one subproject or runtime target.
- Subproject implementation notes: strategy, decisions, retired issues,
  validation details, debugging history, and tradeoffs specific to one
  implementation path.

## User-Requested Session Records

Create a repository session record only when the user explicitly asks for the
conversation or session to be preserved. Do not infer this request merely from
session length, importance, a checkpoint, or session closure.

Store the record beneath the relevant scope in
`engineering-docs/session-records/`. For example, DevCapsule implementation
sessions use `engineering-docs/session-records/devcapsule/`. Repository-wide
sessions may live directly beneath `engineering-docs/session-records/` or in a
documented `product/` scope.

The default capture mode is `detailed`: an agent-authored chronological record
of important user instructions, decisions, rationale, examples, changes,
validation, rejected alternatives, and open work. Use `summary` when the user
asks for a concise record. Use `verbatim` only when the user or IDE supplies an
export and explicitly asks to store it; an agent reconstruction must never be
represented as an exact transcript.

Before writing, remove credentials, secret values, unrelated personal data,
hidden model reasoning, and raw output that does not improve durable project
memory. Record material omissions or redactions when they affect
interpretation.

Session records supplement the canonical project files. Propagate decisions,
requirements, bugs, validation, current state, and next work to their normal
artifacts, then link those artifacts from the session record. Never require a
future agent to read a session record to discover the current next task.

Use `YYYY-MM-DD-short-session-topic.md`, include capture metadata, and update
`index.md` for every record added, removed, or renamed. The detailed policy and
template guidance live in the `README.md` of each session-record directory.

## Subproject Roles

Top-level documentation must keep the repository split clear:

- `devcapsule-src/` is the active Python distribution project. New framework
  behavior, configuration protocol work, packaging, and tests should normally
  be implemented there.
- `docker4pycharm/` is the historical/reference PyCharm shell subproject. It
  remains useful as an operational baseline and comparison target, but current
  docs should not present it as the active development path unless the work is
  explicitly about preserving or validating the reference implementation.

When editing user-facing docs, avoid mixing these roles. Historical notes may
describe old commands, but current instructions should point users to
`devcapsule-src/` and the configuration-first CLI when describing active
development.

## Requirements Register

Use root `REQUIREMENTS.md` as the project-level overview and index for
requirements that should remain true across implementations. Use
`engineering-docs/requirements/product/` for the canonical detailed record of each root
requirement. Use subproject requirements files for implementation-specific
behavior, validation scope, and traceability.

The selected handoff says what to do next; the relevant requirements register
says why the task exists, how important it is, and how implementation and
validation map back to project intent.

Each root requirement record under `engineering-docs/requirements/product/` should have:

- A stable ID such as `R-CONC-001`.
- A short title.
- A type split: high-level goal or concrete requirement.
- A clear statement.
- Priority: `MVP`, `current stabilization`, or `later`.
- Status: `proposed`, `accepted`, `implemented`, `repo-validated`,
  `manually validated`, `deferred`, or `rejected`.
- Frontmatter metadata that stays easy to maintain in source control.
- Validation references or evaluation signals appropriate to the item type.
- Related tasks, bug records, decisions, or completed-task records.

Goals are evaluated by judgment and accumulated evidence. Concrete requirements
must be testable in principle, even if some verification is manual.

When a task, bug, or implementation note materially implements, validates,
changes, defers, rejects, or reinterprets a requirement, add a `Requirements:`
line with the relevant IDs. If no requirement exists yet, either add a proposed
requirement first or explicitly note that the work is exploratory.

Do not turn requirements files into a second active backlog. Requirements
should remain stable enough to help future sessions understand intent. The
active tasks in `README.md` remain the source of truth for immediate next work.

## User-Level Documentation Protocol

When changing behavior that an end user can observe or invoke, update the
user-level documentation in the same change as the code and requirement update.
Examples include command names, command order, options, defaults, generated
artifacts, setup steps, validation expectations, IDE configuration names, or
host-exposure behavior.

Use this documentation split:

- `REQUIREMENTS.md` records the requirement overview and links to the
  canonical detailed requirement files.
- Target user docs such as `devcapsule-src/README.md` describe how the user does
  it: installation path, command path, common examples, validation expectations,
  and current limitations.
- Root `CURRENT-STATUS.md` records the linear handoff or open-workstream
  registry selected by `workflow-type`; a WIP status records track-local state
  in `multiple-streams` mode.
- Implementation notes record design rationale, rejected alternatives, and
  evidence that would distract from user instructions.

For every user-visible change, check:

1. Is there an accepted or proposed requirement for the behavior?
2. Does the relevant user-level README show the supported command path and
   defaults?
3. Are unsupported or intentionally removed paths absent from current user docs?
4. If host exposure, credentials, devices, Docker access, or persistent state
   changed, is the isolation impact documented beside the option/default?
5. Does the selected handoff mention any manual validation still required?

Do not rely on historical notes as user documentation. Historical sections may
keep old command names when they describe what happened at that time, but
current user docs must show only the supported interface.

## Active Task Format

Each active task should include enough closure detail that the next agent knows
when to remove it from the list:

```markdown
1. Task title.
   Requirements: R-...
   Done means: ...
   Verification: ...
   Reopen if: ...
```

Use a lighter form only for very small tasks. The important rule is that the
done condition and verification path should be explicit before work starts.

## Active Tasks Versus Historical Context

The selected handoff's active task list should contain only work that the next
session on that track should actually consider doing.

## Bug Intake

Use the relevant scope beneath `engineering-docs/bugs/` when a bug needs
durable evidence before it is fixed, retired, or converted into a completed
task. Name files like:

```text
engineering-docs/bugs/SCOPE/YYYY-MM-DD-short-title.md
```

Each bug file should capture:

- Requirements, if the bug affects known requirements.
- Symptom.
- Environment: image, launcher command, project path or mount, host
  assumptions, and relevant versions.
- Reproduction: manual steps are acceptable when automation is not practical.
- Expected and actual behavior.
- Evidence: logs, stack traces, screenshots, commands, and timestamps.
- Current hypothesis, with uncertainty.
- Verification target: automated test, script/check, or manual validation.
- Fix notes and close criteria.

Do not include secrets. Keep detailed bug evidence in the bug file. The
selected handoff should only contain the next action, such as investigating the
bug, validating a fix, or adding a regression check.

When a task is completed, validated, no longer reproduced, or intentionally
retired:

1. Remove it from the active list.
2. Add a dated status note near the current-state section if future agents need
   to know why it disappeared.
3. Move detailed evidence into the corresponding scope beneath
   `engineering-docs/completed-tasks/`.
4. State when the task should be reopened, for example "only if a later image or
   launcher change regresses this path."

This keeps the next-session question "what should we do next?" unambiguous.

## Completed Task Archive

Use one markdown file per closed task:

```text
engineering-docs/completed-tasks/SCOPE/YYYY-MM-DD-short-task-name.md
```

Recommended structure:

```markdown
# Completed Task: ...

Date: ...

Status: completed | retired | manually validated | no longer reproduced

## Original Task

...

## Requirements

R-...

## Done Means

...

## Verification

...

## Environment Provenance

- Image: ...
- Launcher mode: ...
- Project mount: ...
- Important host-side assumptions: ...

## Retrospective Notes

...

## Reopen If

...
```

This folder is not a second active backlog. It is the evidence trail for
retrospective, debugging, and future comparison.

## Human And Agent Responsibilities

The human owns product direction, risk tolerance, code-quality judgment,
overall project-quality acceptance, manual validation in the GUI, and external
operations the container cannot perform, such as pushing without Git
credentials.

The agent owns repository inspection, implementation, documentation updates,
status hygiene, tests or static checks that can run in the current environment,
and commits when requested.

When the human reports a manual validation result, treat it as authoritative
project state and update markdown accordingly.

In practical terms:

- the human chooses the hill to climb;
- the agent chooses the next safe foothold;
- both should expect each slice to end in evidence or an explicit blocker.

## Session Close Checklist

At the end of a meaningful session, update the selected handoff with:

```text
Changed:
- ...

Requirements:
- ...

Validated:
- ...

Not validated:
- ...

External state:
- ...

Uncommitted changes:
- ...

Next task:
- ...
```

Keep this concise. The goal is to make the next session start cleanly.

## Design Decision Records

Some choices outlive the implementation that provoked them. "We chose
capabilities over named configurations" stays true across rewrites, new
subprojects, and model changes. Those get a ceremony.

Design decision records live at:

```text
engineering-docs/decisions/product/
```

They are root-level because they are implementation-agnostic and outlast any
subproject. Use `engineering-docs/decisions/product/_template.md` as the starting point.

### Two Tiers

- `engineering-docs/decisions/product/`: product and architecture decisions. Ceremonial,
  human-adopted, immutable once accepted. Use when a choice crosses
  subprojects, changes an accepted requirement, or moves a security boundary.
- `engineering-docs/design-notes/SCOPE/`: lightweight proposals and decision
  notes described in the next section. They are local, reversible,
  implementation-scoped, and writable by an agent without decision-record
  ceremony.

Promotion rule: a lightweight note that turns out to change a requirement,
cross subprojects, or set a boundary graduates into a root decision record.
Keeping the ceremony rare is what makes it mean something.

### The Ceremony

1. Propose.
   - A human or an agent writes the record with `status: proposed`.
   - It must carry at least two real options, each with an honest cost, plus a
     recommendation.
   - An agent may propose. An agent never adopts.
2. Review.
   - The human rejects, amends, or asks for more options.
3. Adopt.
   - The human states the decision. Status becomes `accepted`, and
     `date-decided` plus `decided-by` are filled in.
   - The agent records the act; it does not perform it.
4. Propagate.
   - An accepted decision produces or changes a requirement record, and a task
     if work follows. The decision is linked from both.
   - Decisions say why. Requirements say what must be true. Tasks say what to
     do next. Do not let a decision record become a second backlog.
5. Supersede, never edit.
   - Once accepted, the Decision and Rationale sections are frozen.
   - Changed your mind? Write a new record and mark the old one
     `superseded-by`. Editing an accepted decision retcons history and destroys
     the only property that makes it trustworthy as memory.

### Status Values

- `proposed`: written, not yet decided.
- `accepted`: adopted by the human owner.
- `rejected`: considered and intentionally not pursued.
- `deferred`: accepted direction, intentionally outside the current target.
- `superseded`: replaced by a later record.

A decision is never `implemented` or `repo-validated`. A decision is not built;
its consequences are. Those belong to requirements and tasks.

### Triggers

Write a design decision record when:

- a choice changes scope, architecture, or security posture materially;
- several defensible options remain and the choice will be re-litigated later;
- an accepted requirement is being reinterpreted or superseded;
- an isolation relaxation is being deliberately accepted.

These mirror the escalation rules above, because the same conditions that
warrant asking a human also warrant recording the answer.

## Decision Notes

These are the lightweight tier described above. For decisions that may be
revisited but stay local to one implementation, use a small note under the
relevant scope in `engineering-docs/design-notes/`:

```markdown
# Decision: ...

Date: ...

Context:
...

Options:
...

Decision:
...

Consequences:
...

Reopen if:
...
```

## External State Register

Some state cannot or should not live in Git: credentials, GUI logins, local
image tags, manually built images, host firewall behavior, or services running
outside the container. Record these facts without secrets in the current-state
section or an implementation note.

## Git Hygiene

Before editing or committing:

1. Check `git status --short --untracked-files=all`.
2. Keep unrelated user or IDE changes out of commits unless they are clearly
   part of the requested save point.
3. Use one commit message that describes the saved state, not every small
   conversational step.
4. If pushing is blocked by missing user credentials, commit locally and let the
   human push externally.

### Verifying Shared Branch State

Two questions about shared refs are easy to answer incorrectly by inspection.
Run the check rather than inferring the answer.

**Has this branch's work reached `main`?** Ancestry is the wrong test. A squash,
a rebase, or a merge queue rewrites commits, so

```text
git merge-base --is-ancestor <branch> origin/main
```

answers "no" for work that is already fully integrated. An agent that trusts it
concludes the merge failed and redoes integrated work. Compare by patch
identity instead:

```text
git cherry origin/main <branch>
```

Lines beginning `+` are genuinely absent from `main`. Lines beginning `-` are
already upstream under different commit identifiers. No `+` lines means the
work has landed, whatever the commit identifiers say.

**Have two refs diverged, and is the divergence real?** When a local ref and its
remote have both advanced, first establish whether the local-only commits carry
anything that is actually missing:

```text
git rev-list --left-right --count <local>...<remote>
git cherry <remote> <local>
```

If every local commit is reported as already upstream, the divergence is an
artifact of rewritten history and resetting the local ref to the remote one
discards nothing. An agent may do that without asking, and must then report the
evidence it relied on: the counts, the `git cherry` output, and the ref it
reset.

If any commit is genuinely missing, stop and ask the human. Do not choose a
side, discard history, or force-push to resolve it.

This applies to any ref, not only `main`. A stale workstream branch left by an
earlier session diverges the same way and is resolved the same way. Never
force-push `main` under either outcome.

## Applying This To Other Projects

When using a Dockerized IDE environment created by this project on another
repository, the same process should live inside that repository, not only
inside this DevCapsule repo.

An environment may include a reusable bootstrap template at a documented path,
for example:

```text
/usr/local/share/docker4ide/vibe-coding-process.md
```

In the mounted project, ask the agent:

```text
Bootstrap the vibe-coding process documentation from
/usr/local/share/docker4ide/vibe-coding-process.md into this project.
Create or update AGENTS.md, README.md, CURRENT-STATUS.md, REQUIREMENTS.md,
docs/, and engineering-docs/ as appropriate. Preserve existing project docs
and adapt the process to this repository. Set workflow-type in
.devcapsule/devcapsule.toml to single-stream or multiple-streams.
```

At minimum, add or update these files in the target project:

```text
.devcapsule/devcapsule.toml
AGENTS.md
README.md
CURRENT-STATUS.md
REQUIREMENTS.md
docs/
engineering-docs/requirements/
engineering-docs/specifications/
engineering-docs/decisions/
engineering-docs/design-notes/
engineering-docs/implementation-notes/
engineering-docs/wip/
engineering-docs/archive/
engineering-docs/bugs/
engineering-docs/completed-tasks/
engineering-docs/session-records/
```

The target project's `README.md` should point to its current status and workflow
entry points. The target project's `REQUIREMENTS.md` should give an overview
and index of accepted requirements with stable IDs, while the canonical
detailed records live under `engineering-docs/requirements/`. The target
project's `AGENTS.md` should instruct agents to read the brief, workflow type,
root status, and selected handoff. Design proposals and lightweight decisions
belong in `engineering-docs/design-notes/`; execution and validation evidence
belongs in `engineering-docs/implementation-notes/`; active bug evidence
belongs in `engineering-docs/bugs/`; and closed task records belong in
`engineering-docs/completed-tasks/`.

The Docker image and launcher provide the working environment. The mounted
project provides the source of truth for the work.
