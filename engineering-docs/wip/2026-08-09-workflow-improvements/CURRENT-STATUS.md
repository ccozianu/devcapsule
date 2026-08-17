# Workstream Current Status: Workflow Improvements

Mnemonic: `workflow-improvements`

Start date: 2026-08-09

State: active; intake queue empty, four acknowledged items in progress

Integration target: `main`

Delivery method: pull request

Requirements: `R-PRODUCT-003`, `R-PRODUCT-004`, `R-PRODUCT-005`,
`R-PRODUCT-006`

## Goal

Improve the multiple-stream human/agent workflow from concrete problems,
ambiguities, and avoidable mechanical friction found while dogfooding it during
the recursive E2E cycle. Keep each correction narrow and evidence-based, and
conclude this workstream when that dogfood cycle's accepted findings have been
fixed, explicitly deferred, or rejected.

## Branch Association

The active branch is `workflow-improvements/v1`, forked from the registration
commit on `main` and resynchronized with `main` on 2026-08-16. It was renamed
from `workflow-improvements/intake` on 2026-08-16: the old name collided with
the `intake/` directory convention introduced the same day, and the new one
says what the branch is for — workflow improvements bound for the V1 release.
The old ref is deleted locally and on `origin`; nothing should reference it.

`workflow-improvements/outbox` was created on 2026-08-16 from `main`, carrying
deliveries to `project-management` and the registry row for this rename, and
nothing else. It is the first use of the outbox mechanism. It is not an editing
checkout; see selection rule 6.

## Current State

- Corrected 2026-08-16. This handoff previously said no workflow correction had
  been implemented. Two rounds have since landed, both published by
  `project-management` as deliberate bootstrap exceptions because this
  workstream had not started: verified divergence resolution, the merge-landed
  check, and rule 11's non-exclusive editing on 2026-08-15; then the whole
  workstream intake mechanism on 2026-08-16.
- The intake queue is empty. Six items were received and all six are
  dispositioned: two acknowledged and implemented on 2026-08-16, four
  acknowledged on 2026-08-17 and now carried as *Acknowledged Work*. None was
  forwarded. See *Dispositions*.
- The four files are deleted from `main` through the outbox. They remain on
  this branch until its next synchronization, which is what the protocol
  prescribes; do not delete them here.
- A seventh item, on shared bug vocabulary, is committed on
  `project-management/coordination` and arrives when that branch merges — itself
  an illustration of why the outbox now exists. Expect the queue to be
  non-empty again.
- Five workflow changes have been written across 2026-08-16 and 2026-08-17 and
  await integration: the reserved `project-management` workstream, the outbox
  branch, the two-outcome intake disposition protocol with its completion gate,
  the latitude clause, and the purpose-and-principles preamble.
- The branch was 37 commits behind `main` and carried three commits that were
  patch-identical duplicates of the registration commits. Rebasing dropped all
  three; the branch is now identical to `main`.
- The sole backlog item — making `project-management` a mandatory permanent
  workstream — was implemented on 2026-08-16. The backlog is now empty. This
  was the first correction this workstream published itself rather than
  receiving through a bootstrap exception.

## Last Task And Status

Last task: make `project-management` a mandatory reserved workstream created
when a project initializes or adopts `multiple-streams`. Chosen by the product
owner on 2026-08-16 as the tractable item, ahead of the intake queue.

Status: complete for the protocol; the tooling half is delivered to
`project-management` for routing.

The product owner's phrasing was "initiated by the tooling on all devcapsule
projects". Investigation found no tooling to hang that off: `devcapsule
bootstrap project` shells out to `docker4pycharm/bootstrap-project.sh`, which
predates the multiple-stream workflow entirely — it emits
`engineering-docs/workstreams/`, never reads `workflow-type`, and knows nothing
about the registry, start-date directories, or intake. The product owner chose
to land the protocol now and deliver the code need as intake rather than
modernize a frozen script or build an initialization command inside a workflow
correction.

Changed:

- `WORKFLOW.md`: restriction 12 reserves the mnemonic; new *Initializing
  Multiple-Stream Mode* and *The Reserved `project-management` Workstream*
  sections; *Markdown Roles* and *Applying This To Other Projects* updated.
- `AGENTS.md`: the reserved workstream, and the instruction to report an
  incompletely initialized project rather than work around it.
- `devcapsule/assets/pycharm/image-assets/vibe-coding-process.md`: the
  bootstrap prompt now names the reserved workstream.
- `R-PRODUCT-006`: statement and verification list.
- Root `CURRENT-STATUS.md`: the permanence exception, and this repository's
  reconciliation.
- Root `README.md`, `docker4pycharm/README.md`, `index.md`: the frozen status
  of `docker4pycharm/` made explicit, at the product owner's request after they
  challenged an edit made there.

Two design choices worth knowing, both mine unless overruled. Coordination
authority is **advisory and recorded, not procedural** — the reserved
workstream does not gate anyone's commits or integrations, because a
coordination track that can block is a coordination track that becomes a
bottleneck. And retirement is **only** by migration back to `single-stream`,
which forces the question of what happens to open workstreams at migration; the
procedure requires concluding them first.

### Second Task: The Outbox Branch

The product owner then settled how work moves between workstreams: each
workstream sends through a standing `<mnemonic>/outbox` branch, which merges to
`main`, and every workstream stays current with `main` by rebasing often. This
dispositioned two intake items and closed two open questions; see
*Dispositions*.

Changed:

- `WORKFLOW.md`: restriction 13; *The Outbox Branch*; *Staying Current With
  `main`*; a commit-cadence rule in *Development And Checkpoints*; *Beginning A
  Workstream* step 6 now routes registration through the outbox; the intake
  delivery paragraph points at the outbox; new selection rule 6, because the
  outbox otherwise creates a checkout that identifies a workstream but must not
  be worked in — found by using the mechanism, not by reading it.
- `AGENTS.md`: synchronize before planning, send through the outbox.
- This workstream's `intake/README.md`: points at `WORKFLOW.md` rather than
  restating the delivery rule, so the next protocol change does not make it
  stale again.

An earlier finding of this workstream's own is now fixed by the same section.
**A stale branch cannot see its own intake.** Discovery reads `main`, so items
are visible from anywhere, but the files an agent must edit and delete to
disposition them exist only on a synchronized branch. *Staying Current With
`main`* states that directly.

### Third Task: The Intake Disposition Protocol

The product owner specified on 2026-08-17 how intake items must be resolved.
`WORKFLOW.md`'s *Workstream Intake* now defines two outcomes and a completion
gate; `AGENTS.md` and this workstream's `intake/README.md` follow.

Changed:

- Disposition has exactly two outcomes, **acknowledge** or **forward**.
  Acknowledging means converting the item into a requirement or task the
  workstream will actually do — recording an opinion about it does not count.
  Forwarding sends it to `project-management` with the original text and a
  reason, and does not name a new owner, because routing is that workstream's
  decision.
- Deferral is retired as an outcome. An item accepted for later is
  acknowledged with its position recorded. This removes the state in which an
  item is neither owned nor refused, which is where items went quiet before.
- Deleting the item from `main` through the outbox is the recipient's
  obligation, and the working branch picks the deletion up on synchronization
  rather than repeating it.
- **Intake gates completion.** No workstream concludes, successfully or
  unsuccessfully, with items left in its intake on `main`. The successful
  sequence checks it first, before anything expensive; the unsuccessful
  sequence requires forwarding what will not be done, so a failing workstream
  cannot take other workstreams' work down with it.
- Items from `project-management` are not forwardable, since it is
  authoritative for what is worked on, by whom, and in what order.

Three points were decided rather than transcribed, and are open to reversal.

**The exemption needed a mirror.** If `project-management` cannot be refused
and also cannot forward — it has nowhere to send — then an item reaching it
must end there. Its dispositions are therefore terminal: assign onward, make it
the reason to begin a workstream, or drop it with recorded reasoning. Without
that, a refused item circulates indefinitely.

**Disagreement needed a path.** A recipient that thinks a `project-management`
item is impossible or misrouted raises it with the human. It does not return it
through intake, and the item stands until the routing decision changes. The
alternative — no path at all — would make a wrong routing decision unfixable.

**Deletion had to be prompt.** The queue is read from `main`, so absence from
`main` is the only acknowledgement a sender ever gets. Deleting only on a
working branch would leave `main` advertising handled work for as long as that
branch takes to merge.

This narrows, but does not close, the still-queued *intake has no
acknowledgement* item. Refusals now reach `project-management`, and prompt
deletion makes absence meaningful. A sender still learns nothing when its item
is accepted, and nothing surfaces an item that has sat untouched for a long
time.

### Fourth Task: Latitude Where The Workflow Is Silent

Raised by the product owner on 2026-08-17, immediately after the previous task
observed that some scenarios will land in states the protocol does not define.
Rather than chase completeness, V1 admits the incompleteness and says how to
behave inside it. `WORKFLOW.md` opens with *Latitude Where This Document Is
Silent*; `AGENTS.md` and `R-PRODUCT-004` follow.

The constitutional principle as given: what is not expressly denied is allowed.
A human/agent pair meeting an uncovered situation resolves it with judgment and
keeps working, because being stopped by silence is itself a failure.

Four qualifications were added. The first two protect the rule from being
read as a general override; the third and fourth are what make it useful rather
than merely permissive.

- **Express denials are not silence.** Stated flatly, the principle would have
  repealed six existing rules by implication: never force-push `main`; stop
  before editing when branch and registry disagree; do not infer permission to
  update `main` from the ability to do so; and three explicit instructions to
  ask the human. Those are decisions already made, generally because the
  failure they prevent is expensive or irreversible. The clause names them and
  excludes them.
- **Silence is not a rule you dislike.** A pair must establish that the
  protocol is actually silent, not merely inconvenient. Otherwise "the workflow
  is underspecified" becomes the universal solvent for any rule with a cost.
- **Ambiguity and contradiction are defects, not silence.** Where two rules
  conflict, choose the reading that serves evident intent, say which reading
  you chose, and report the defect — rather than treating the conflict as
  licence to pick the convenient side.
- **Exercised latitude must be recorded.** This is the obligation that makes
  the permission safe. Record what was missing, what was done, and why; deliver
  it to the workflow-owning workstream when the gap would recur in any project.
  Unrecorded latitude leaves the gap invisible, the next pair re-derives it
  differently, and two projects believing they share a protocol quietly
  diverge. Recorded latitude is how the next version of the document gets
  written, which makes this clause a discovery mechanism rather than only an
  escape hatch.

Scoped explicitly to V1 and dated, with a reopen condition: revisit when
discovering a gap becomes a surprise rather than a routine event.

Not done: no `D-####` decision record was created. The clause has a V1 sunset
and `WORKFLOW.md` is its authority, so a durable decision record seemed
premature. Worth adding if the principle outlives V1.

### Fifth Task: The Purpose And Principles Preamble

Requested by the product owner on 2026-08-17, who supplied four principles and
asked whether they were enough. `WORKFLOW.md` now opens with *Purpose And
Principles* before any rule, so both audiences meet the intent first.

The four given: low-ceremony coordination; no accidental loss of knowledge;
latitude where underspecified; retrospective value that does not interfere with
the source tree's main purpose. All four are in, close to as stated.

Three additions were made, all open to being struck.

- **Resumability**, placed first. This looked structural rather than optional.
  It is the document's own opening claim, and it is what handoffs, the single
  authoritative status per effort, and the recorded next resumable task all
  exist to produce. It is adjacent to but distinct from knowledge preservation:
  that one is about a fact being findable, this one is about a cold-start pair
  being able to *act*. Without it, the most load-bearing machinery in the
  document has no stated reason.
- **Explicit decision rights.** The document repeatedly separates what an agent
  does unasked from what requires the human, and that separation had no
  principle behind it. Stating it matters most for agents, which otherwise
  calibrate autonomy by guesswork.
- **Portability across agents and projects.** Already required by
  `R-PRODUCT-004` and by this repository's rule against agent-specific storage,
  but it was an unstated reason for visible choices — plain markdown, no
  tool-specific state, protocol kept separate from project facts.

A *When These Conflict* subsection was added because the principles genuinely
oppose each other: recording everything serves knowledge and violates low
ceremony, full retrospective detail competes with a source tree about software,
latitude opposes predictability. Principles without a tiebreak produce
inconsistent behavior and let an actor justify nearly anything by picking a
favorable one. The order given is resumability first, then write only what
changes future behavior, then prefer one durable record to several.

A short *How To Read This Document* subsection tells each audience where to
start, and states that where a rule and the preamble disagree the rule governs
and the disagreement is a defect to report — so the preamble cannot be used to
argue around a rule.

### Sixth Task: Remove Worktrees From The Protocol

The product owner corrected a premise on 2026-08-17. Worktrees were never
intended as a workflow concept. Extra checkout directories had appeared in
practice for two reasons — e2e dogfood testing, which is outside the workflow,
and manoeuvring edits onto other branches such as the outbox — and both are
implementation details.

The assumption ran deeper than the wording suggested: eleven references in
`WORKFLOW.md` and three in `AGENTS.md`, including the session-start selection
rules, which were written in terms of worktrees rather than branches.

All fourteen are gone. The protocol is now stated in terms of branches and
checkouts, with one paragraph saying explicitly that local checkout arrangement
is an implementation detail — one checkout has one branch and therefore at most
one selected workstream, and whether an extra one is a clone, a Git worktree,
or a container is the developer's business and is not workflow state. A second
sentence puts checkouts made for other purposes, such as running the product
against itself, outside this document entirely.

Restriction 11's second carve-out was the subtlest case. It protected "another
worktree's recovery state", which named a mechanism in order to describe
something simpler: uncommitted work belonging to someone else's session. It now
says that.

Two things worth recording.

**The resolution was subtraction, and that was the better outcome.** The
document got smaller while covering the same ground, which is what the
low-ceremony principle in the preamble asks for. A workflow gap does not always
mean something is missing; sometimes it means something is present that should
not be.

**The evidence was already in this session.** Every branch switch performed
across three days of this work — between `workflow-improvements/v1` and
`workflow-improvements/outbox`, repeatedly — used a plain `git switch` in one
checkout. The mechanism the protocol kept pointing at was never once needed by
the protocol itself.

## Next Resumable Task

Define the pause action — item 2 of *Acknowledged Work*, and now the only
acknowledged item that is both ready and unblocked.

Done means: a defined pause action in `WORKFLOW.md`; a place in the handoff for
open threads, options weighed but unresolved, and questions awaiting the human;
and an explicit statement of what is deliberately not preserved. The shape is
already proven — this handoff's *Open Threads* section has been written in it
since 2026-08-16 and has produced two answered questions and several still
open. The work is promotion from local practice to protocol, not design.

Item 3 is blocked on the product owner. Item 4 is the largest and its main
consumer, `recursive-e2e` Stage 7, has not been reached.

The nearer obligation is integration, not writing. Six workflow changes are
written and unmerged, and this workstream cannot conclude while
`workflow-improvements/outbox` carries undelivered mail.

## Dispositions

One line per item, with the reasoning that produced it. Items are removed from
`intake/` when dispositioned; Git retains them.

### Accepted And Implemented, 2026-08-16

**Per-workstream outbox branch** (`project-management`, relaying the product
owner). Accepted and implemented on the product owner's direct instruction the
same day. `WORKFLOW.md` gains restriction 13 and *The Outbox Branch*.

The item asked to be designed together with this workstream's standing
main-first-registration-versus-pull-request question, and it was: registration
now travels the sender's outbox like any other message, so nothing has to
commit directly to `main`. That question is closed.

The item's own doubt — that an outbox earns its cost only if `main` becomes
protected or agents rarely hold `main` write authority — was overtaken. The
product owner chose it as the general mechanism regardless, and the deciding
argument was different from the one the item anticipated: the outbox is what
makes prompt delivery possible *without* direct-`main` commits, which matters
under the existing pull-request default rather than under some future
protection.

**Commit cadence and branch synchronization** (`project-management`, relaying
the product owner). Accepted and implemented. `WORKFLOW.md` gains a commit
cadence rule in *Development And Checkpoints* and *Staying Current With
`main`*.

All four of the sender's cautions were honored rather than noted:

- Method follows publication state. Rebase what only you have, merge what
  others may have — so the rule never implies force-pushing a shared branch.
- The `AGENTS.md` caution against imposing rebase on a pull-request workflow is
  reconciled by scope, stated explicitly: keeping a branch current with `main`
  is a different act from delivering work to `main`, and only the first is
  governed here.
- Conflicts are split by kind. Mechanical is agent work, semantic is the
  user's.
- Commit cadence versus clean history is resolved by declining to couple them.
  What `main` sees is a property of the configured merge strategy, not of the
  cadence rule, so an agent never has to hesitate before committing.

The stale-branch finding this workstream raised about itself is fixed by the
same section, since the fix is the same rule.

### Acknowledged 2026-08-17

The remaining four items, dispositioned under the two-outcome protocol adopted
the same day. All four are acknowledged; none is forwarded. Each is a gap in
the workflow protocol itself, which is this workstream's registered goal, and
none has a better owner. The ordered work they became is in *Acknowledged
Work*.

**A worktree procedure.** Acknowledged, then resolved by subtraction on
2026-08-17. Closed; see *Sixth Task*.

The item correctly identified that `WORKFLOW.md` referenced worktrees
throughout and defined them nowhere. The assumed fix was to write the missing
procedure. The product owner corrected the premise: worktrees were never
intended as a workflow concept at all. Extra checkouts had been used by agents
for dogfood testing, which is outside the workflow, and for manoeuvring edits
onto other branches, which is an implementation detail. The right resolution
was therefore to remove the dependency rather than document it.

**Pausing and conversational continuity.** Acknowledged. The sender's cheap
version has in fact already been trialled here: this handoff's *Open Threads*
section was written in that shape at the 2026-08-16 pause, and it worked —
question 1 of that trial produced the branch rename, and the reserved-ideas
question is still doing its job. What remains is promoting a proven shape from
one workstream's local practice into protocol, which is the least speculative
kind of change this workstream can make.

The sender's three-way split is adopted as the design's frame: state resumption
is already served, reasoning continuity is the real gap, and literal
conversational replay is a false goal. Its argument that this project's own
premise forbids depending on a vendor's session resumption is decisive.

**Intake acknowledgement and staleness.** Acknowledged, and partly overtaken.
The item frames intake as message passing between isolated processes with four
known failure modes: undelivered messages, unacknowledged messages, unbounded
queues, and no dead-letter handling. Two are now closed. The outbox fixed
undelivered. Forwarding to `project-management`, whose dispositions are
terminal, is dead-letter handling. The completion gate bounds queues at
workstream end, though not during a long-running one.

What remains is genuinely open: a sender still learns nothing when its item is
*accepted*, and nothing surfaces an item sitting untouched. Blocked on the
product owner, who reserved ideas for this specifically; see *Open Threads*.

**External-resource ownership and reaping.** Acknowledged, for the convention
only. The protocol governs Git state well and external state not at all, while
every concurrency hazard observed in the recursive E2E cycle was outside Git —
a hard-coded container name, a colliding host port, hand-rolled `HOME` and
`XDG_*` roots, a reused image tag, and a shared Docker daemon whose only
ownership model lives inside one workstream's code.

The implementation is a separate matter and was **delivered onward, not
forwarded**. `recursive-e2e` Stage 7 is already scoped to "persistence and
deterministic cleanup", so the reaping implementation and the detached-container
cleanup bug were delivered to its intake as derived work. That is a new item
from this workstream, not a refusal of this one: the convention is acknowledged
here and the code is handed to where it belongs.

**Scope after acknowledging four.** The workstream's goal commits it to conclude
once findings are dispositioned, and four acknowledged items is not a small
remainder. It is defensible because all four are protocol and this workstream
is the protocol owner, but *done* is now visibly further away than it was, and
the product owner should see that rather than discover it. See *Open Threads*.

## Acknowledged Work

Ordered by readiness, not by size. Positions are this workstream's judgment and
can be reordered.

1. ~~A worktree procedure.~~ Done 2026-08-17, by deletion rather than by
   writing one. See *Sixth Task*.
2. **A pause action and reasoning continuity.** Ready now, and the shape is
   already proven in this handoff. Done means: a defined pause action in
   `WORKFLOW.md`; a place in the handoff for open threads, options weighed but
   unresolved, and questions awaiting the human; and an explicit statement of
   what is deliberately not preserved.
3. **Intake acknowledgement and staleness.** Blocked on the product owner.
   Done means: an acceptance signal a sender can observe, and a staleness
   signal that surfaces where a human actually reads — or a recorded decision
   that the remaining gap is acceptable and why.
4. **An external-resource ownership convention.** Largest, needs product
   knowledge, and its main consumer is not ready. Done means: how a resource
   derives its owning workstream and run identity; how names avoid collision by
   construction rather than by discipline; how an agent enumerates what is held
   and by whom; and what an agent may and may not remove.

## Assessment Of The Queue

Recorded on 2026-08-16 to inform dispositioning. Not itself a disposition.

The six items are not six independent problems. They cluster into three
designs.

**Delivery and synchronization mechanics.** *Closed 2026-08-16; see
Dispositions.* The outbox-branch proposal, commit cadence and branch
synchronization, and this workstream's own long-standing question about
main-first registration under a pull-request policy. The outbox item stated
explicitly that it and the registration question should be designed together,
and they were. A fourth input arrived the same day: the repository is
configured for **rebase merge**, so every workstream branch acquires
patch-identical duplicate commits the moment its pull request lands. That is
structural, not agent improvisation, and it has now been observed on three
branches. It sat awkwardly beside `AGENTS.md`, which cautions against imposing
a rebase policy on a pull-request workflow; the adopted rule separates the two
by scope, and frequent rebasing now drops those duplicates as a side effect
rather than leaving them to accumulate.

**Communication-protocol completeness.** Intake acknowledgement, and pausing
with conversational continuity. Both concern the shape of the message-passing
system rather than its plumbing: the first that delivery is fire-and-forget with
no reply path and no staleness signal, the second that pausing a workstream has
no defined effect on the conversation's substance.

**Concurrency.** The worktree procedure and external-resource ownership and
reaping. Both need design; the second needs code, and closes the detached
container cleanup bug as a side effect.

## Backlog

Empty. The one item — making `project-management` a mandatory permanent
workstream — was completed on 2026-08-16. Its done-criteria were met as
follows:

- initialization and adoption create exactly one reserved workstream and its
  handoff — *Initializing Multiple-Stream Mode*;
- scope defined with three exclusions against becoming a duplicate registry,
  an implementation catch-all, or the owner of others' WIP state;
- permanent lifecycle reconciled with the bounded rule at its source, in
  *Definition And Restrictions*, rather than as a footnote;
- branch ownership, checkout selection, start-date layout, migration,
  integration, and retirement all stated; branches and selection are
  deliberately *ordinary*, so only lifecycle is special;
- `WORKFLOW.md`, `AGENTS.md`, the shipped bootstrap template, and
  `R-PRODUCT-006` agree; and
- this repository's registration is reconciled in root `CURRENT-STATUS.md`,
  keeping one narrow adoption exception: it adopted the mode on 2026-08-08 and
  created the reserved workstream on 2026-08-09, so its start date is one day
  later than initialization.

Two parts could not be completed by this workstream and were delivered to
`project-management`'s `intake/`:

- reconciling that workstream's own *Lifecycle Exception* section, which
  restriction 11's carve-out forbids this workstream from editing; and
- routing the tooling implementation, which fits no open workstream's goal.

## Open Threads

Written at pause on 2026-08-16. Trial of the shape proposed in the pause and
continuity intake item. Short by design.

### Awaiting The Product Owner

1. **Were the outbox and disposition rules the ideas you reserved for intake?**
   The acknowledgement item says the product owner held further ideas about how
   intake should be processed and told this workstream to ask before designing.
   Since then they specified the outbox and the two-outcome protocol, which may
   simply *be* those ideas. If so, item 3 shrinks to an acceptance signal and a
   staleness signal. If more was reserved, item 3 should not be designed
   without it.

2. **Is four acknowledged items the right size for this workstream?** Its goal
   commits it to conclude once findings are dispositioned. All four are
   protocol and this workstream owns protocol, so no forward was honest — but
   the practical effect is that conclusion moved further away. Options if that
   is unwelcome: hand items 3 and 4 to `project-management` to place elsewhere,
   or accept that this workstream runs until V1.

3. **Does "the workflow improvements already identified" mean identified, or
   identified and implemented?** The product owner named that as a condition for
   starting their own projects on v026. The two readings put very different
   obligations on this workstream, and it is currently described as being on the
   critical path for those project starts. The 2026-08-16 rename to
   `workflow-improvements/v1` presumes this workstream delivers *for* V1, which
   sharpens the question rather than answering it.

4. **Who owns protocol boilerplate that lives inside another workstream's
   directory?** Each `intake/README.md` restated the delivery rule, so changing
   that rule made four workstreams' READMEs stale at once — and restriction
   11's carve-out bars this workstream from editing three of them. Its own
   README now points at `WORKFLOW.md` instead of restating it, which removes
   the recurrence. The other three still carry the superseded sentence and are
   noted in the outbox delivery, but "duplicated protocol text inside a
   carve-out" is a shape that will recur, and the rule does not say who
   resolves it.

### Settled Since The Last Pause

- **How intake deliveries reach `main`.** Resolved 2026-08-16 by the product
  owner: through the sender's `<mnemonic>/outbox` branch. This also closed the
  main-first registration question. See *Dispositions*.
- **The branch name.** Resolved 2026-08-16: renamed to
  `workflow-improvements/v1`, which names the delivery target rather than a
  mechanism and no longer collides with the `intake/` directory.
- **Tooling scope for the reserved workstream.** Resolved 2026-08-16: land the
  protocol here, deliver the code need as intake. Recorded because the
  alternatives were live options, not strawmen — modernizing the frozen
  `bootstrap-project.sh`, or building an initialization command in
  `devcapsule-src` — and either could be chosen later without reopening the
  protocol.

### Weighed And Unresolved

- **Bounded scope versus seven items.** This workstream's goal commits it to
  conclude once findings are fixed, deferred, or rejected. Accepting all seven
  would make it unbounded by accident. Deliberate deferral of at least the
  concurrency cluster is worth considering, since that cluster needs code and
  has a natural home in the recursive-dogfood Stage 7 work.
- **Whether the outbox is worth building at all.** Its own intake item argues it
  earns its cost only if `main` becomes protected, or if the project decides an
  agent should rarely hold `main` write authority. Neither is true today.

### Deliberately Not Preserved

The 2026-08-16 conversation. What mattered is above or in the intake files.

## Evidence

- The earlier `multi-workflow` workstream completed successfully and is archived
  at [its final status](../../archive/2026-08-08-multi-workflow/CURRENT-STATUS.md).
- Registration of this workstream was prepared from current `main` in a separate
  temporary worktree while the primary checkout remained on
  `recursive-e2e/stage-4`.
- On 2026-08-16 the branch was rebased onto `main`; three duplicate commits were
  dropped by patch-id and the resulting branch is identical to `main`.

## External State And Risks

- Corrected 2026-08-16. This document previously said the environment has no Git
  publication credentials. It does: branches and unprotected `main` can be
  pushed. What is absent is any GitHub API access — there is no `gh` CLI and no
  token — so pull requests must be opened and merged by the human. That stale
  claim caused work to be withheld at least twice.
- Repository policy defaults workstream delivery to pull requests, while the
  beginning procedure commits registration directly on `main`. This remains
  unresolved and is now entangled with the outbox proposal.
- This track overlaps `CURRENT-STATUS.md`, `WORKFLOW.md`, `AGENTS.md`, and the
  workflow requirements. Synchronize with `main` before integrating.
- Two bootstrap exceptions have now published workflow changes from
  `project-management` because this workstream had not started. A third would
  suggest the split between the two tracks is not working as intended.

## Workstream Document Index

This workstream owns this status file and its `intake/` directory. Intake items
are a queue rather than permanent documents and are deliberately not listed
here or in `index.md`; the directory listing is the queue.
