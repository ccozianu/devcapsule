# Human / Agent Iteration Workflow

This project treats markdown files in the repository as the durable memory for
human/agent work. Conversation is useful for speed, but project state must
survive model changes, IDE restarts, and future sessions.

## Purpose And Principles

This document structures how a human and a coding agent build software
together. Its purpose is to make that pair more productive than either would be
alone, and it tries to achieve that by removing specific frictions rather than
by adding process. Every rule below is meant to pay for itself.

The rules follow from a small number of intents. Read a rule against these when
it seems arbitrary, and reason from these when the document is silent.

**Resumability.** A competent human/agent pair should be able to open this
repository cold, discover the current state, and continue — without access to
the conversation that produced it. Sessions end abruptly, models change,
context windows fill, and people forget. So state lives in committed files
rather than in chat, exactly one document is authoritative for each effort, and
the next step is written down rather than remembered. A workflow that only
works while someone remembers the last conversation is not a workflow.

**Low-ceremony coordination.** Coordination should cost as little as it can
while still working. Where several efforts run concurrently, the structure
exists to keep them from colliding — not to schedule them, gate them, or make
them negotiate. Contention is treated as a design failure rather than something
to arbitrate. Prefer conventions that make conflicts impossible over procedures
that resolve them, and prefer a rule an agent can apply alone over one
requiring a round trip.

**No accidental loss of knowledge.** Anything of importance surfaced during
development is recorded in the source tree and is predictably discoverable.
*Predictably* is the operative word: a fact stored somewhere nobody thinks to
look has been lost as surely as one never written. This is why documents have
assigned roles and fixed locations, and why an index exists at all. Knowledge
that only survives in a chat log is one session away from gone.

**Latitude where this document is silent.** The workflow is incomplete and says
so. What it does not expressly deny is allowed, and a pair meeting an
unforeseen situation decides for themselves what best suits it rather than
stalling. The obligations that keep this safe rather than merely permissive are
in *Latitude Where This Document Is Silent*.

**Retrospective value, subordinate to the work.** Record enough about how the
project evolved to support later analysis, learning, and rediscovery of
reasoning that would otherwise have to be reconstructed. But the source tree's
first purpose is the software. Process records are placed and structured so
that someone reading the code can ignore them entirely, and so that they never
compete with source for attention or for space in the paths people actually
work in.

**Explicit decision rights.** The pair is not two interchangeable actors.
Mechanical, reversible, and evidently-intended work is the agent's to do
without asking; product intent, ambiguity that changes the outcome, and
irreversible or outward-facing acts are the human's. This document says which
is which at each point rather than leaving each pair to renegotiate it, because
an agent that asks about everything is useless and one that asks about nothing
is dangerous.

**Portability across agents and projects.** The workflow must work for any
capable agent, not one vendor's, and in an adopter's repository, not only this
one. It therefore lives in plain markdown in the source tree, depends on no
tool-specific storage or feature, and keeps project-specific facts separate
from the reusable protocol.

### When These Conflict

They will. Recording everything imaginable serves knowledge and violates low
ceremony. Full retrospective detail competes with a source tree that stays
about the software. Latitude sits in tension with predictability.

Three tiebreaks, in order:

1. **Resumability wins.** If dropping a record would leave the next pair unable
   to continue, or able to continue only by guessing, write it. This is the
   purpose the others serve.
2. **Write what changes future behavior; skip what merely proves work
   happened.** A decision, a constraint, a rejected alternative, or a
   non-obvious reason changes what someone does next. A narrative of activity
   does not. When unsure, ask what a reader would do differently having read it.
3. **Prefer one durable record to several.** Update an existing document rather
   than adding one; link rather than copy; put a fact where its role says it
   belongs even when somewhere else is more convenient today. Duplication is
   how records drift apart and stop being trustworthy.

### How To Read This Document

Humans: the *Multiple-Stream Workflow* and *Markdown Roles* sections carry the
structure; the rest is detail you can consult when it becomes relevant.

Agents: read the whole applicable path before acting, treat the numbered
restrictions and procedures as binding, and treat prose as the reasoning that
explains them. Where a rule and this preamble appear to disagree, the rule
governs and the disagreement is a defect worth reporting.

## Latitude Where This Document Is Silent

This workflow is incomplete, and for V1 the project says so rather than
pretending otherwise. It was written from real use, and real use keeps
producing situations it does not describe. Adopters should expect to meet them.

**The principle: what this document does not expressly deny is allowed.** A
human/agent pair that reaches a situation the protocol does not cover resolves
it with judgment and keeps working. Being stopped by silence is itself a
failure — the protocol exists to make work possible and legible, not to
authorize each step of it.

**Silence is not the same as a rule you dislike.** Before invoking this,
establish that the protocol is actually silent. A rule that is inconvenient,
costly, or arrived at for reasons no longer visible is still a rule; change it
through the workflow-owning workstream rather than around it.

**Express denials are not silence.** This principle never overrides an
instruction to stop, ask, refrain, or seek authority. Those are decisions
already made, usually because the failure they prevent is expensive or
irreversible. In this document they include, and are not limited to: never
force-pushing `main`; stopping before editing when branch and registry
disagree; not inferring permission to update `main` from the mere ability to do
so; the carve-outs in restriction 11; and every explicit instruction to ask the
human. Where such a rule applies, follow it and raise the difficulty.

**Ambiguity and contradiction are defects, not silence.** If two rules conflict,
or one admits several readings that lead to materially different work, that is a
flaw in this document. Choose the reading that best serves the evident intent,
say which reading you chose, and report the defect. Do not treat a contradiction
as permission to pick whichever side is convenient.

**Exercised latitude must be recorded.** This is the obligation that makes the
permission safe. When a pair resolves something the protocol does not cover,
record in the selected handoff what was missing, what was done, and why. If the
gap would recur in any project rather than only this one, deliver it to the
workstream that owns the workflow, through the sender's outbox. Unrecorded
latitude means the gap stays invisible, the next pair re-derives it differently,
and two projects using "the same" workflow quietly diverge. Recorded latitude is
how the next version of this document gets written.

**Scope.** This clause is a V1 position, adopted 2026-08-17. It reflects a
workflow young enough that its gaps outnumber the cost of specifying them in
advance. Revisit it when the gaps become rare enough that discovering one is a
surprise rather than a routine event.

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
develops, and ends successfully or unsuccessfully. Exactly one exception
exists: the reserved `project-management` workstream, which every
multiple-stream project has and which stays open for as long as the project
uses that mode. See *The Reserved `project-management` Workstream*.

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
   `main` and is intended to return to `main` if the workstream succeeds. Its
   outbox branch is the exception: it starts from `main` and returns to `main`
   repeatedly, throughout the workstream's life rather than at its end.
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
    it. Two carve-outs stand: another workstream's WIP handoff directory
    excluding its `intake/` subdirectory, and another worktree's recovery state.
    Each is a workstream's account of its own state, which another workstream
    cannot restate accurately; report what you observe about another workstream
    instead of editing its record. Delivering work to another workstream is a
    different act from restating its state, and belongs in its `intake/`; see
    *Workstream Intake*. Wider
    exclusivity applies only where a documented locking protocol exists and is
    actually used for that file. No such protocol exists today.
12. `project-management` is a reserved mnemonic. Exactly one workstream in the
    project carries it, no ordinary workstream may take it, and it is never
    archived and recreated while the project stays in `multiple-streams` mode.
13. `<mnemonic>/outbox` is a reserved branch name in every workstream. It
    carries only what the workstream sends to `main` ahead of its own
    integration, never its working changes. See *The Outbox Branch*.

### Initializing Multiple-Stream Mode

Selecting `multiple-streams` is an act with required structure, whether it
happens when a project is first set up or when an existing single-stream
project adopts the mode later. Both paths produce the same starting shape.

In one commit on `main`:

1. Set `workflow-type = "multiple-streams"` in `.devcapsule/devcapsule.toml`.
2. Convert root `CURRENT-STATUS.md` from a detailed handoff into the compact
   open-workstream registry. Detailed state carried over from single-stream
   mode moves into a workstream handoff rather than staying at the root.
3. Create the reserved `project-management` workstream by the procedure in
   *Beginning A Workstream*, using the initialization date as its immutable
   ISO start date, and register it in the new registry.
4. Create `engineering-docs/wip/` and `engineering-docs/archive/`.

A multiple-stream project with no `project-management` workstream is
incompletely initialized. Report that rather than working around it.

Initialization creates exactly one workstream. Ordinary workstreams begin
afterwards, separately, and only when there is real work for them.

### The Reserved `project-management` Workstream

Coordinating a portfolio of workstreams is itself continuing work, and it
belongs to no single bounded effort. Without a reserved home, it either lands
in whichever workstream happens to be selected — distorting that workstream's
scope and its record — or it survives only in conversation. The reserved
workstream gives it a durable owner.

**Scope.** It owns project-wide priorities, sequencing, cross-workstream
dependencies, portfolio-level checkpoints, lifecycle decisions about opening,
pausing, resuming, blocking, and concluding other workstreams, and routing work
that has no owning workstream yet.

Three exclusions keep it from absorbing the project:

- It is not a second registry. Root `CURRENT-STATUS.md` on `main` remains the
  single authoritative list of open workstreams. `project-management` records
  reasoning, sequencing, and dependencies, not a parallel copy of the roster.
- It is not an implementation catch-all. Work that fits an open workstream's
  goal belongs to that workstream. Work that fits none is a reason to begin a
  workstream, which is a `project-management` decision to make and hand over,
  not work for it to perform.
- It does not own other workstreams' state. Restriction 11's carve-out binds it
  like anyone else: it reports what it observes about another workstream and
  delivers to that workstream's `intake/`; it does not edit that workstream's
  handoff.

Its coordination authority is advisory and recorded, not procedural. It does
not gate other workstreams' commits, integrations, or checkpoints.

**Lifecycle.** It is permanent for the lifetime of `multiple-streams` mode
rather than open-ended by neglect. Restriction 12 reserves its mnemonic;
initialization creates it; it has no completion criteria and is never listed as
active-with-a-final-goal. Its registry state reads `active; permanent
coordination`, and paused or blocked are as legitimate for it as for any other
workstream — a project can go a long time with nothing to coordinate.

**Branches, selection, and integration are ordinary.** Its branches are
`project-management/<topic>`, forked from `main`, returning to `main` by the
repository's default delivery method. `project-management/coordination` is the
conventional first branch. Checkout selection, intake, checkpoints, commit
cadence, and integration follow the same rules as any other workstream. Only
its lifecycle is special.

**Retirement.** It ends only when the project leaves `multiple-streams` mode,
never as an ordinary conclusion. Migrating to `single-stream`, in one commit on
`main`:

1. Confirm no ordinary workstream is still open. Migrating with open
   workstreams silently orphans their handoffs; conclude or archive them first.
   Its own intake must be empty as well, and it is the last queue that can be
   emptied: once it is gone there is nowhere left to forward anything.
2. Fold the coordination state that remains useful into root
   `CURRENT-STATUS.md`, which becomes the detailed single-stream handoff again.
3. Move `engineering-docs/wip/<start-date>-project-management/` to
   `engineering-docs/archive/<start-date>-project-management/` unchanged, and
   record the migration, its date, and the resulting mode in its final status.
4. Set `workflow-type = "single-stream"`.

**Adoption exception.** A project adopting `multiple-streams` that already has
a branch, directory, or bounded workstream named `project-management` records a
migration exception in the reserved workstream's handoff, in the same form as
any other adoption exception, rather than renaming history.

### Beginning A Workstream

Begin from a clean, current `main` checkout:

1. Choose the goal, unused mnemonic, and ISO start date.
2. Create
   `engineering-docs/wip/<start-date>-<mnemonic>/CURRENT-STATUS.md` on `main`.
3. Record the start date, goal, state, branch prefix, integration target,
   delivery method or applicable repository default, current task, and next
   resumable task.
4. Create `engineering-docs/wip/<start-date>-<mnemonic>/intake/README.md` so the
   workstream can receive work from others; see *Workstream Intake*.
5. Add the workstream to root `CURRENT-STATUS.md`.
6. Deliver that source-level registration to `main` through the outbox of the
   workstream opening it; see *The Outbox Branch*. Registration is a message to
   the project, not part of anyone's deliverable, so it travels the same route
   as intake and does not require committing directly to `main`. At
   initialization, when no workstream exists yet to send it, the initializing
   commit on `main` carries it.
7. Fork the first `<mnemonic>/...` branch from the registration commit once it
   is on `main`.
8. Perform workstream changes only on its associated branch or branches. Its
   own `<mnemonic>/outbox` is created on first use, not at registration.

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
6. A checked-out `<mnemonic>/outbox` identifies its workstream but is not an
   editing checkout. It carries only outbound messages; see *The Outbox
   Branch*. Do not resume workstream work there. Switch to a working branch
   first, and treat uncommitted working changes found on an outbox as recovery
   material that belongs elsewhere.
7. Detached HEAD, an unregistered branch, or more than one plausible mapping
   has no default. Ask the user only when the desired workstream cannot be
   established from explicit intent and a unique registered association.
8. Follow the selected registry row's handoff link. Do not guess its start date
   from branch or commit timestamps. On the selected workstream branch, its
   committed handoff is authoritative for the latest track-local state; the
   copy reachable from `main` is the latest published snapshot.
9. Read the selected workstream's `intake/` directory from the locally accepted
   mainline ref before planning the session. Items there are work other
   workstreams have delivered and this workstream has not yet dispositioned;
   see *Workstream Intake*. A handoff read without its intake is an incomplete
   picture of what the workstream owns.

If the selected workstream differs from the current branch, switch to its clean
worktree before editing. Do not combine dirty state from two workstreams, and
do not use a stash as their durable handoff boundary. Different users and
clones may select different workstreams independently because their checked-out
branches and worktrees are local state.

### Workstream Intake

Every workstream directory carries an `intake/` subdirectory. It is the only
place another workstream may write inside a workstream's WIP directory, and it
exists because a protocol that forbids all such writing has no way to hand work
over. Announcing a handoff in the sender's own checkpoint does not deliver it:
the recipient reads its own handoff at session start, so an item recorded
anywhere else is invisible to the workstream expected to do it.

**Writing an item.** Any workstream, or the user, may add a file. One item per
file, named `YYYY-MM-DD-<sender-mnemonic>-<slug>.md`, where the date is the
delivery date. The file states what is being handed over, why it belongs to the
recipient rather than the sender, the evidence or documents behind it, and what
accepting it would mean. The sender does not assign priority, sequence, or a
release target; those are the receiving workstream's judgment.

**Delivery must reach `main` promptly.** An intake file that waits for the
sender's own integration is invisible for as long as that takes, which
reproduces the failure this mechanism exists to fix. Deliver it through the
sender's outbox branch, separately from the sender's ordinary work. Intake
delivery is deliberately decoupled from the sender's delivery schedule. See
*The Outbox Branch*.

**Ownership is asymmetric.** A sender may add files and amend files it wrote. It
may not edit another sender's file, remove any file, or touch anything else in
the recipient's directory. Only the receiving workstream removes or reclassifies
items in its own intake. Its account of itself remains exclusively its own.

**Disposition has exactly two outcomes: acknowledge or forward.** Every item
ends in one of them, and no item may be left alone indefinitely; see *Intake
Gates Completion*.

Scheduling is not a third outcome. An item accepted but not scheduled yet is
acknowledged, with its position recorded. "Later" is a property of work a
workstream owns, not a way to avoid owning it.

**Acknowledge** means the workstream takes the item as its own responsibility
and turns it into work it will actually do. Recording an opinion about an item
is not acknowledging it; converting it into a requirement, backlog entry, task,
or next step is.

1. On the working branch, record it in the handoff as a requirement or task,
   with the reasoning that led to accepting it, and place it in the
   workstream's order of work.
2. Through the outbox, delete the intake file from `main`.

**Forward** means the workstream is not the right owner. Legitimate reasons
include: the item is not a well-formed requirement; it will not be fixed; it
belongs to a different workstream; it belongs to a later release; or it is out
of this workstream's registered scope. The workstream states the reason but
does not choose a new owner — routing is `project-management`'s decision.

1. Through the outbox, write a new item into
   `engineering-docs/wip/<start-date>-project-management/intake/`, following
   *Writing an item*. Include the original item's full text, or its path and
   the revision it can be recovered from, together with the reason for
   refusing it.
2. In the same outbox commit, delete the original item from `main`.
3. Record in the handoff what was forwarded and why, so the decision is not
   silently reopened later.

**Deleting from `main` is the recipient's job, and it is prompt.** The queue is
read from `main`, so an item still present there has not been dispositioned,
and an item removed from there has been. That absence is the only signal a
sender gets. Deleting through the outbox keeps the signal honest; deleting only
on a working branch leaves `main` advertising work that is already handled for
as long as that branch takes to merge. The working branch picks the deletion up
at its next synchronization, so do not also delete it there.

Intake is a queue, not an archive. Git retains every item and every reason.

**Items from `project-management` are not forwardable.** That workstream is
authoritative for structuring work — what is worked on, by whom, in what order
— so an item it sends is a routing decision, not a proposal, and forwarding it
back would be a loop. Acknowledge it.

A recipient that believes such an item is genuinely wrong — impossible,
misrouted, or in conflict with its registered scope — raises that with the
human rather than returning it through intake. Until the routing decision
changes, the item stands.

**`project-management`'s own dispositions are terminal.** It has nowhere to
forward to, so an item reaching it ends there in one of three ways: assigned to
a workstream by delivering it onward, made the reason to begin a new
workstream, or dropped with recorded reasoning. This is what stops a refused
item from circulating indefinitely.

**Intake gates completion.** A workstream is not complete, successfully or
unsuccessfully, while any item remains in its intake on `main`. An empty intake
is a precondition of concluding, checked as part of the completion sequence.
A workstream ending unsuccessfully still owes its queue a disposition: items it
will not do are forwarded to `project-management`, not abandoned with the
workstream. Leaving items behind would silently destroy work other workstreams
handed over in good faith.

**Presence.** The directory carries a `README.md` so that an empty intake is
unambiguous rather than an untracked absence. Intake items are not listed in
`index.md` or in the workstream's own document index; the directory listing is
the queue, and indexing it would create churn for items designed to be
short-lived.

### The Outbox Branch

Intake defines where a message lands. The outbox defines how it travels.

Every workstream has one standing branch named `<mnemonic>/outbox`. It carries
what the workstream needs to publish to `main` ahead of, and independently of,
its own integration. A workstream's working branch may run for weeks; anything
riding along with it is invisible until it merges, which is the failure intake
was built to fix, one step further along.

**What the outbox carries.** Anything the project needs to know now that is not
part of the sender's own deliverable:

- intake items delivered to other workstreams;
- registrations of new workstreams the sender is opening; and
- changes to the sender's own row in root `CURRENT-STATUS.md` — state, branch
  association, or anything else other agents route by.

The last matters more than it looks. The registry is how every other checkout
decides where work belongs, and a routing fact that waits for the sender's
integration leaves `main` describing a branch that may no longer exist. Under
*Selecting Work At Session Start* that is invalid routing, so a stale row does
not merely mislead; it stops other agents before they edit.

The outbox is also the answer to the standing question of how main-first
registration coexists with a pull-request delivery policy: registration travels
the same route as any other message, so nothing has to commit directly to
`main`.

**What it must never carry.** The sender's working changes. Merging an outbox
publishes everything on it, so a working change that leaks into one is
unfinished work promoted to `main` without review. Keep the two branches
strictly separate; when in doubt, rebuild the outbox rather than reuse a dirty
one.

**Sending.** From a clean checkout, and never from the working branch:

1. Fetch, and create or reset `<mnemonic>/outbox` to current `main`. The outbox
   holds no history of its own worth preserving; every send starts from `main`.
2. Add only the files being sent. One commit per coherent delivery.
3. Push the branch and deliver it to `main` by the repository's default method.
4. Leave the branch in place. After the merge it is an ancestor of `main` and
   the next send resets it forward again.

Sending is a small, self-contained operation. It does not touch the sender's
working branch, does not require that branch to be clean or current, and is not
a checkpoint of the sender's own work.

**Receiving is not symmetric.** A recipient does nothing to receive. Items
appear in its `intake/` directory when the outbox merges to `main`, and it sees
them by staying current with `main`.

**Ending.** The outbox branch is deleted when the workstream ends, like any
other branch it owns. An outbox with unmerged commits at that point is
undelivered mail: merge it before concluding, or say in the final status why it
was abandoned.

### Staying Current With `main`

`main` is the medium every message travels through, so a workstream that does
not watch it does not receive. Intake arrives there, registrations arrive
there, and repository-wide coordination facts arrive there.

Synchronize the working branch with `main` often — at least at every stage
boundary, before beginning a substantial slice, and before integrating.

**Method follows publication state.** Rebasing an unpublished branch onto
`main` is clean, and it silently drops commits that already landed, which
matters in a repository whose merge strategy rewrites them. Rebasing a
published branch rewrites shared history and needs a force-push; do that only
when the branch is known to be unshared, and prefer merging `main` in
otherwise. Rebase what only you have; merge what others may have.

This rule is about keeping a workstream branch current with `main`. It says
nothing about how work is delivered *to* `main`, which follows repository
policy and its configured merge strategy or merge queue.

**Conflicts split by kind.** Mechanical conflicts — reformatting, moved
sections, adjacent edits — are ordinary agent work; resolve them and say so.
Semantic conflicts, where two workstreams assert incompatible things, are the
user's decision. Do not let an unresolved conflict of either kind become a
reason to stop synchronizing entirely; that is how a branch drifts far enough
that the conflict becomes unaffordable.

Two practical consequences:

- A stale branch cannot act on its own intake. Discovery reads `main`, so items
  are visible from anywhere, but the files an agent must edit and delete when
  dispositioning them exist only on a synchronized branch. Synchronize before
  planning a session's work, not after.
- A long-lived branch that never rebases accumulates conflicts against work it
  could have absorbed cheaply, and diverges from coordination decisions it is
  expected to be following.

### Development And Checkpoints

The workstream handoff—not root `CURRENT-STATUS.md`—records detailed progress,
evidence, the current or last task, and the next resumable task. Routine
workstream commits update only that handoff and workstream-owned files.

**Commit often.** Commit each coherent unit of work as it is finished rather
than accumulating many files across a long session. An uncommitted session is
one interruption away from losing not just the changes but the order in which
decisions were made, which is the part no one can reconstruct. Committing is
cheap and local; it is not publication, and it does not require the work to be
complete. A checkpoint is a statement about project state and belongs in the
handoff; a commit is a save point. Every checkpoint is committed, but most
commits are not checkpoints.

Commits reach `main` through the repository's configured merge strategy, so
whether frequent commits become individual commits on `main` is a property of
that strategy rather than of this rule. Write commit messages that would read
well either way, and do not let uncertainty about the merge boundary become a
reason to delay committing.

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

Before integration begins, the workstream's intake on `main` must be empty. See
*Intake Gates Completion*. Check this first: a forwarded item has to travel the
outbox and reach `main`, so discovering a full queue late in the sequence stalls
the integration rather than merely adding a step.

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

Ending unsuccessfully does not discharge the intake queue. Before the sequence
below, disposition every remaining item: forward to `project-management`
anything this workstream will not do, with the reason. Work handed over in good
faith must not disappear with the workstream that failed to do it. See *Intake
Gates Completion*.

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
  detailed handoff for an open workstream in `multiple-streams` mode. Exactly
  one of these is always the reserved `project-management` workstream, which
  holds project-wide priorities, sequencing, and lifecycle reasoning rather
  than a second copy of the registry.
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
.devcapsule/devcapsule.toml to single-stream or multiple-streams. If
multiple-streams, follow Initializing Multiple-Stream Mode, including the
reserved project-management workstream.
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
