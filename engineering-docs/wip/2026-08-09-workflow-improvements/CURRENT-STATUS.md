# Workstream Current Status: Workflow Improvements

Mnemonic: `workflow-improvements`

Start date: 2026-08-09

State: paused. Paused on 2026-08-17, resumed twice the same day — to specify
publishing before integration, then to record merge strategy and commit
identity. Paused rather than blocked because the backlog now holds one item that
is actionable today. The acknowledged external-resource item is separately
blocked and still cannot be written until `recursive-e2e` Stage 7 exists to
exercise it.

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

`workflow-improvements/outbox` was created on 2026-08-16 from `main` and is the
first use of the outbox mechanism. It has sent three times, all merged: the
first carried three deliveries to `project-management`, one to `recursive-e2e`,
this branch's registry row, and six intake deletions; the second the intake
staleness decision; the third, at the pause, three protocol questions and the
registry row change to `blocked`; the fourth this workstream's own disposition
log and handoff, which is the rule written the same day being applied to
itself. It is not an editing checkout; see selection rule 6.

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
- All six files are gone from `main` and from this branch, which was
  synchronized after the merge on 2026-08-17.
- A seventh item, on shared bug vocabulary, is committed on
  `project-management/coordination` and arrives when that branch merges — itself
  an illustration of why the outbox now exists. Expect the queue to be
  non-empty again.
- Eight workflow changes are on `main` as of 2026-08-17: the reserved
  `project-management` workstream, the outbox branch, the two-outcome intake
  disposition protocol with its completion gate, the latitude clause, the
  purpose-and-principles preamble, the removal of worktrees from the protocol,
  the working model of checkouts and branches, and workstream states with
  pausing and resuming.
- Several commits on this branch are not yet on `main`: the two corrected Git
  claims, the disposition log, the staleness closure's handoff record, the
  pause, and publishing before integration. They are this workstream's entire
  unmerged deliverable and need the human to open and merge the pull request.
  Until that lands, `WORKFLOW.md` on `main` has neither *The Disposition Log*
  nor *Publishing Before Integration* and still carries both disproved Git
  claims, so other workstreams reading `main` will reset an outbox from history
  it no longer contains.
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

### Seventh Task: State The Working Model

Directly caused by the previous task. The worktree confusion happened because
`WORKFLOW.md` never stated its own model of where work happens, so a reader
supplied one — and the wrong one. Removing the worktree references fixed the
symptom; this fixes the cause.

`WORKFLOW.md` now defines *Checkouts, Branches, And Workstreams* before any
rule, and `AGENTS.md` carries the short form. Six terms are fixed — project,
remote, checkout, branch, workstream, pair — with the relationships between
them stated as cardinalities, so what "current branch" and "current workstream"
refer to is checkable rather than inferred. The load-bearing line: the current
branch determines the current workstream, not the reverse.

Sequential within a checkout, concurrent across checkouts. One checkout works
on many workstreams over time by switching branches from a clean tree; genuine
concurrency comes from several pairs in several checkouts integrating through
the remote, never from a local arrangement of directories.

Two edges were specified rather than left implicit, both places the model would
otherwise have produced the same class of confusion it was written to end.

**What is shared versus local.** The remote carries what the project agrees on;
a checkout carries only local facts, none of them registered or coordinated.
This is the reason two pairs can hold different current workstreams at once
without either being wrong, and the reason the registry is a record rather than
a presence system. "Active" means opened and not concluded, not that anyone is
working on it now. The document asserted the non-locking property already
without ever explaining what made it true.

**Two pairs may select the same workstream.** Nothing prevents it and no lock
exists, so leaving it unsaid would have made it undefined behaviour of exactly
the kind the latitude clause was written about. Stated: it is permitted, they
will contend on one handoff, coordinate outside the protocol before doing it
deliberately, and an accident normally costs a conflict rather than lost work.

### Eighth Task: Pausing And Resuming

Reviewed at the product owner's request, then written. The review found the gap
worse than the intake item suggested: `paused` existed only as a value in the
registry's list of states — "active, paused, blocked, or integrating" — and
nothing in the repository defined any of the four, distinguished paused from
blocked, or said what to do at either end of a pause. Both procedures were
absent, not merely thin.

`WORKFLOW.md` gains *Workstream States, Pausing, And Resuming*; `AGENTS.md`
carries the short form. Item 2 of *Acknowledged Work* is closed.

**The four states are now defined**, which was unplanned and turned out to be
the load-bearing part. Paused and blocked look identical from outside and are
not: a paused workstream needs someone to *choose* it, a blocked one needs its
blocker cleared. So blocked now carries obligations paused does not — name the
blocker, name what would clear it, and tell whoever can clear it, through their
intake if it is another workstream. A blocked workstream nobody was told about
is indistinguishable from an abandoned one, and the registry has been unable to
tell those apart since it existed.

**Pausing is a six-step act**, placed where the knowledge is. The sender's
argument was decisive: only the pair stopping work knows whether a thread
finished or was suspended, and they know it while stopping. Asking on return is
guesswork after the information is gone. One step is new and comes from this
session rather than from the item — send anything owed through the outbox,
because a paused workstream holding undelivered mail blocks its recipients
without telling them. That failure only became possible when the outbox was
introduced yesterday.

**Open Threads is specified in the shape this handoff has been using** since
2026-08-16: awaiting the human, weighed and unresolved, deliberately not
preserved. Bounded to roughly ten lines, deliberately too small to become a
dumping ground. The third part is the least obvious and worth keeping — naming
what was dropped on purpose stops a later reader hunting for a conversation
that was intentionally let go.

**Conversational replay is recorded as a non-goal**, not an unimplemented
feature, so nobody builds it later. Two reasons: a replayed transcript is
expensive to read and mostly noise, and depending on an agent's session
resumption would break the portability principle.

**Resuming has two steps that exist because of failures observed in this
session.** Synchronize before planning, since intake arrives on `main` while a
workstream sleeps — the stale-branch finding. And re-verify what the handoff
claims about external state rather than trusting it: this handoff itself
asserted for days that the environment had no Git publication credentials,
which was false and had caused work to be withheld twice.

### Ninth Task: Integration, And Two Defects It Exposed

Both pull requests were merged by the product owner on 2026-08-17. Verified
against `origin/main` by content rather than by commit identity, since the
repository's rebase merge rewrites SHAs:

- all eight workflow changes are present, including the eight new or rewritten
  sections;
- this workstream's `intake/` on `main` contains only its `README.md`;
- the registry row reads `workflow-improvements/v1`;
- all four deliveries arrived — three in `project-management`'s intake, one in
  `recursive-e2e`'s; and
- one `worktree` mention survives in `WORKFLOW.md`, which is the intended one
  naming it as an implementation detail, and none in `AGENTS.md`.

Both branches were then synchronized. Doing so exposed two defects in rules
written one and two days earlier, both invisible until the first post-merge
synchronization and both now fixed.

**A merged outbox is not an ancestor of `main`.** *The Outbox Branch* said it
was, and that the next send "resets it forward" from there. True under
fast-forward or merge-commit delivery; false under squash or rebase merge,
which is what this repository uses. `git merge-base --is-ancestor` confirms the
outbox is unreachable from `main` despite every one of its changes being
present. An agent trusting that sentence would build the next send on stale
history. The step is now an explicit hard reset, with a note that this is a
force-push the prohibition on force-pushing `main` does not reach, since an
outbox has no independent content to lose.

**Rebasing is the wrong way to synchronize a branch whose own delivery just
landed.** *Staying Current With `main`* said rebasing "silently drops commits
that already landed". That holds when patch identities match; it failed here.
Rebasing `workflow-improvements/v1` onto the merged `main` conflicted on
`CURRENT-STATUS.md` and `intake/README.md`, because rebase replays commits one
at a time onto a `main` that already contains their final effect, and the
intermediate states disagree even where the end states do not. The branch had
nothing `main` lacked, so the correct operation was a hard reset. Recorded as
such: rebase carries unlanded work forward and is the wrong tool for a branch
with nothing left to carry.

Both defects share a shape worth noting. Each was a claim about Git behaviour
that is true under some merge strategies and false under this repository's, and
neither could be caught by review — only by the first branch to complete a full
round trip through `main`.

### Tenth Task: The Disposition Log

The product owner's answer to the acknowledgement half of item 3, given
2026-08-17: a per-workstream disposition log, pushed to `main` through the
outbox, so an interested party finds an item either in `intake/` or in the log,
both kept current.

`WORKFLOW.md` gains *The Disposition Log*, the acknowledge and forward steps
now write an entry in the same outbox commit that removes the item,
registration creates an empty log, and `AGENTS.md` carries the short form. This
workstream's own log is written and backfilled with all six real dispositions.

**The invariant is the point.** On `main`, every item ever delivered to a
workstream is in exactly one of two places — still in `intake/`, meaning
undispositioned, or in the log, meaning resolved. Never both, never neither.
Entry and deletion are one commit specifically to keep that true; as two steps
it would be false whenever one landed without the other. That invariant turns
"did they get it, and what did they decide" from a question requiring a reply
into a lookup, and it is mechanically checkable, which matters for the staleness
work that remains.

**Why not the reply the sender proposed.** The original item suggested writing a
short reply into the sender's own intake. Declined: a reply is not work, and a
queue whose entire meaning is "own this or forward it" should not carry messages
that are neither. It would also have doubled traffic and required a second
category inside the queue. Recorded because it was the sender's own suggestion
and deserves a reason rather than silence.

**The log is an archive, intake is a queue.** Never pruned, travels into
`engineering-docs/archive/` with the workstream. A concluded workstream's log is
the record of what it was asked to do and what it decided, which is what a later
reader reopening one of those decisions needs. Being durable, it belongs in the
workstream's own document index, unlike intake items.

Item 3 is not finished. The acknowledgement half is done; see *Open Threads*
for the staleness residual.

### Eleventh Task: Close Staleness By Not Specifying It

Product-owner decision, 2026-08-17: intake staleness is deliberately left
unspecified, and `project-management` may act on it as it sees fit. No rule was
added to `WORKFLOW.md`, which is the point rather than an omission.

The reasoning, which is stronger than it first sounds: V1 cannot be produced
while anything remains in its backlog. A rotting intake item is therefore
already caught, by the release gate rather than by a staleness mechanism, and
the workstream that owns release readiness is the one positioned to notice. A
dedicated signal would duplicate a check the project performs anyway, on a
schedule that matters less than it appears — an item nobody needed for months
did not cost anything by waiting.

This is the latitude clause working as designed rather than a gap left by
accident. The workflow declines to specify something, says so, and names who
may decide it.

Item 3 of *Acknowledged Work* is now complete: acknowledgement implemented as
the disposition log, staleness resolved by an explicit decision not to specify
it. Delivered to `project-management` through the outbox, including the
observation that the disposition-log invariant makes an automated check cheap
should they ever want one.

### Twelfth Task: Three Protocol Questions Routed Rather Than Acknowledged

Raised by the product owner on 2026-08-17 while deciding whether to leave this
workstream. Three questions about the workflow's shape rather than its rules.
All three were delivered to `project-management` to be decided as features,
tasks, or rejections; none was acknowledged here.

**Why route rather than acknowledge.** Each is a scope call — V1 or later, and
in the third case an amendment to `R-PRODUCT-004` — and scope is not this
workstream's to decide. The practical argument is stronger: this workstream is
pausing with its one remaining item blocked, so acknowledging three more would
put them in a queue nobody is selecting. That is precisely how items went quiet
before the disposition protocol was written, and doing it here would be this
workstream demonstrating the failure it just fixed.

This also answers *Open Threads* question 1 by construction. The right size for
this workstream is not a number of items; it is that new protocol findings route
through coordination instead of accumulating in a track whose registered goal is
already dispositioned.

The three, with the analysis delivered alongside each:

**A human-readable workflow document.** `WORKFLOW.md` is 1772 lines across
roughly 45 sections, ordered for lookup by an agent rather than for reading by a
person. The recommendation against a second document is the load-bearing part: a
parallel human-facing doc would be the third instance of a failure this
workstream has already paid for twice — the `intake/README.md` sentence that
went stale in four places at once, and the two Git claims that survived review
because nothing checked them. Two documents describing one protocol diverge, and
the non-normative one loses, because nobody's work breaks when it is wrong. The
cheaper shape is to extend the front matter that is already there for humans —
*Purpose And Principles*, *How To Read This Document*, and *Checkouts, Branches,
And Workstreams* — into an explicit onramp, and mark the rest reference.

**Packaging the workflow as a "skill".** Recommended against as stated, because
skills are a vendor mechanism, this repository forbids agent-specific storage,
and `R-PRODUCT-004` requires transfer across agents. But the instinct is right
and is not really about skills: what a skill buys is progressive disclosure, and
`AGENTS.md` currently points at a monolithic document that is loaded in full
whether or not the session will ever reach the completion sequence or the
archive format. The portable version of the same fix is a small mandatory core
with procedure loaded on demand. Per-agent adapters generated from that neutral
source then fit the shape this project already uses for optional agent
components under `D-0005`, rather than inverting it.

**Extracting the workflow to its own repository.** Agreed in direction, with the
observation that it cannot be a task: `R-PRODUCT-004` states the workflow is
part of the product idea, and the premise that it is orthogonal contradicts that
requirement, so it needs a `D-####`. Three costs named: this workstream's own
dogfood loop, with its intake, outbox, and registry, would cross a repository
boundary; a separate repository implies versions, which implies adopters on old
ones, which implies migration that does not exist; and submodule versus
vendoring is a live tradeoff the `sample-projects` workstream is deciding
separately for something else. The cheap half is separable and is the
prerequisite for the expensive half — define the seam, naming what the product
actually depends on, which is the `AGENTS.md` entry point, `workflow-type` in
`.devcapsule/devcapsule.toml`, and the `engineering-docs/` layout. With the seam
stated, adopters can substitute their own workflow immediately, and extraction
later becomes packaging rather than architecture.

None of the three assigns a priority, sequence, or release target, per *Writing
an item*. Effort and dependency are stated as evidence; placement is the
recipient's.

### Thirteenth Task: Publishing Before Integration

The product owner raised the gap on 2026-08-17, immediately after the pause, and
gave the concrete case: `intake-dispositions.md` should already be on `main`, so
that the `WORKFLOW.md` section introducing the disposition log links to
something that exists. `WORKFLOW.md` gains *Publishing Before Integration*;
`AGENTS.md` carries the short form; the outbox's list of what it carries and the
pause procedure both follow.

**This workstream was its own counterexample.** *The Disposition Log*, written
2026-08-17, says the log is pushed to `main` through the outbox. This
workstream's log was created on the working branch instead, as a backfill of six
dispositions already made, and so exists nowhere `main` can see it. The rule and
the only implementation of it disagreed within a day of the rule being written,
which is a reasonable measure of how easy the mistake is.

**The generalization is the useful part.** The rule is not about disposition
logs. Files on a workstream branch divide into two kinds: the deliverable, which
is reviewed as a whole and travels a pull request, and records — handoff,
disposition log, registry row, intake — which are how the project reads a
workstream while it runs and are useless where `main` cannot see them. Records
travel the outbox, at any time.

Three triggers for publishing a record early, all from observation rather than
imagination: a document on `main` names its path; the workstream pauses or
blocks, so the registry sends readers to a handoff that must not be frozen at
the last integration; or another workstream cannot act until it reads it.

Two points were decided rather than transcribed.

**The ordering rule matters more than the routing rule.** A reference published
ahead of its target is a broken rule for as long as the gap lasts, so the target
lands no later than the reference. Since deliverables travel pull requests and
records travel the outbox, the outbox goes first. Without this the routing rule
would still permit exactly the failure that prompted it.

**Verbatim, not a version written for `main`.** Publishing a record is not an
occasion to write a different one. Copying what the branch holds keeps the two
identical, which makes the next synchronization a no-op and makes conflict
impossible; anything else recreates two-versions-of-one-truth at a new level.

Also settled, because it is the other half of "push to `main` before finalizing"
and was genuinely undefined: **the deliverable may land in slices.** An ordinary
pull request for a finished slice is permitted and often right, since a
correction others are waiting on should not sit behind work with months to run.
The completion sequence concludes a workstream rather than being its only
delivery. Slices travel the working branch, never the outbox — merging an outbox
publishes everything on it, without the review a deliverable is owed.

### Fourteenth Task: Record What The Merge Strategy Changes

The product owner merged both pull requests as merge commits rather than by the
rebase merge every earlier delivery used, then asked what that changes for this
workflow. The answer is now an engineering note,
[merge strategy and commit identity](../../implementation-notes/workflow/2026-08-17-merge-strategy-and-commit-identity.md),
listed in `index.md` and filed under a new `implementation-notes/workflow/`
scope, since the existing scopes are `devcapsule` and `docker4pycharm` and this
is neither.

It records the mechanism — a commit's SHA covers its parent and committer
timestamp, so replaying a diff onto a new base produces a different commit with
identical content — and the four consequences this repository actually suffered:
ancestry answering "no" for integrated work, duplicate commits accumulating on
branches, a rebase conflicting against its own merged content, and any recorded
SHA pointing at history `main` does not contain.

The evidence is from this repository rather than from documentation. Both halves
of one rewritten pair still exist here, `3369539` and `285962b`, identical in
tree, author, message, and patch-id, differing in parent and committer date.
`recursive-e2e/stage-4` currently reports 17 commits ahead of `main` of which
`git cherry` shows 15 already upstream — worth knowing before that workstream is
resumed.

The recommendation is merge commits, with the stronger point being uniformity:
rules that hold under one strategy and fail under another cannot be relied on in
a repository that varies it per pull request. The decision is the product
owner's and is open; the note says where it should be recorded if adopted, which
is the *Coordination Baseline* rather than `WORKFLOW.md`.

The adopter-facing version is deliberately not this document, and is now the
backlog's only item.

## Next Resumable Task

Write the adopter-facing treatment of merge strategy, backlog item 1. It is
actionable today, needs no external event, and has its engineering source
already written.

One acknowledged item remains — the external-resource ownership convention — and
it is blocked: its main consumer, `recursive-e2e` Stage 7, has not been reached,
and the convention should be written against a consumer that can exercise it
rather than in the abstract. `recursive-e2e` was told, through its intake on
2026-08-17.

Three further events would add work, and all three are outside this workstream:

1. `recursive-e2e` reaches Stage 7, which unblocks the convention.
2. `project-management` routes one of the three questions above back here, or
   decides this workstream should conclude and hand the convention onward.
3. The bug-vocabulary item lands. It is committed on
   `project-management/coordination` and arrives when that branch merges, at
   which point the intake queue is non-empty again and the completion gate
   applies.

Everything this workstream wrote is now integrated. The product owner merged
`workflow-improvements/v1` as [`PR #19`](https://github.com/ccozianu/devcapsule/pull/19)
and `workflow-improvements/outbox` as
[`PR #20`](https://github.com/ccozianu/devcapsule/pull/20) on 2026-08-17, both as
merge commits rather than by the rebase merge every earlier delivery used.
`git cherry` reports nothing unique on either branch.

Two things remain unmerged, both written 2026-08-17 after those pull requests:
this branch's engineering note and its `index.md` entry, and an outbox send
setting the registry row to `paused`. The row is `paused` and not `blocked`
because the backlog item added the same day is actionable today; the state was
briefly recorded as blocked, before that item existed, and the outbox commit was
rewritten rather than sent twice.

A row reading `active` for a workstream nobody is working on is the failure the
states were defined to prevent, which is why the send is a step rather than an
afterthought. Noted while doing it: a resumption this short costs two
registry sends for a state that was true for one session. Whether that is worth
a rule is not obvious enough to write one now, and it is recorded here so the
second occurrence is recognized rather than re-derived.

On resuming, synchronize first — the pause procedure exists because intake
arrives on `main` while a workstream sleeps — and re-verify the claims in
*External State And Risks* rather than trusting them.

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
2. ~~A pause action and reasoning continuity.~~ Done 2026-08-17. See *Eighth
   Task*.
3. ~~Intake acknowledgement and staleness.~~ Done 2026-08-17. Acknowledgement
   implemented as the disposition log; staleness deliberately left unspecified
   and routed to `project-management`. See *Tenth Task* and *Eleventh Task*.
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

**1. Bring merge strategy and commit identity into end-user documentation.**
Added 2026-08-17 by the product owner. The engineering source is written —
[merge strategy and commit identity](../../implementation-notes/workflow/2026-08-17-merge-strategy-and-commit-identity.md)
— and this item is the adopter-facing treatment, which is a different document
rather than a relocation of that one.

Done means an adopter can choose a merge strategy deliberately and knows what
the choice costs them: that rebase and squash rewrite commit identity, that this
makes ancestry the wrong test for whether work has landed, and that
`git cherry` is the test that survives every strategy. It should teach the
consequence, not the forensics — no `patch-id` internals, no citations of this
repository's refs.

Two constraints. It belongs in `docs/`, which holds current user-facing material
only, and it must not tell adopters which strategy to use: `WORKFLOW.md` stays
strategy-neutral under `R-PRODUCT-004`, and a project's merge policy is usually
set by its host or its organization rather than by this product. Follow *User-Level
Documentation Protocol* and *Draft User Documentation* in `WORKFLOW.md`.

This is actionable now and depends on nothing external, which is why this
workstream is paused rather than blocked.

The earlier item — making `project-management` a mandatory permanent workstream
— was completed on 2026-08-16. Its done-criteria were met as follows:

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

Rewritten at the pause of 2026-08-17, superseding the 2026-08-16 version. Short
by design.

### Awaiting The Product Owner

None.

### Settled Since The Last Pause

- **What the V026 workflow-improvement condition requires.** Resolved
  2026-08-17 by the product owner: most findings have been identified and the
  workflow improvements completed so far are merged to `main`. The workstream
  may remain open and paused until the pair returns to its remaining work; its
  continued existence does not hold the already-merged improvements open.

- **Repository merge strategy.** Routing resolved 2026-08-17, substance
  deliberately deferred. This is a later `project-management` decision, not a
  decision for this workstream or for an agent acting alone. Agents push the
  required branches and the human delivers them to `main` through GitHub pull
  requests; until coordination adopts a repository-wide policy, the human
  chooses the merge method there.

- **Obsolete intake README boilerplate.** Resolved for this workstream on
  2026-08-17 by the product owner: the three stale `intake/README.md` copies are
  obsolete and are not cleanup owned by `workflow-improvements`. Their
  replacement, removal, or reassignment is delivered to `project-management`
  for routing rather than performed across other workstreams' directories
  here.

- **The right size for this workstream.** Question 1 of the 2026-08-16 pause is
  answered, not by a number but by a routing rule: new protocol findings go to
  `project-management` to be placed, rather than accumulating here. Three
  arrived on 2026-08-17 and all three were routed; see *Twelfth Task*.

- **Intake staleness.** Resolved 2026-08-17 by the product owner: deliberately
  not specified, and left to `project-management` to act on as it sees fit. The
  reasoning is that V1 cannot be produced while anything remains in its
  backlog, so the release gate already catches a rotting item before it can do
  lasting damage, and the workstream that owns release readiness is the one
  positioned to notice. Delivered to that workstream; see *Eleventh Task*.

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

- **Whether the outbox was worth building.** Its own intake item doubted it
  outside a protected-`main` future. Answered in use rather than in argument: it
  has sent three times in two days, and the second and third sends each carried
  something that would otherwise have waited on this branch's still-unmerged
  pull request. The doubt is closed.

### Weighed And Unresolved

- **Whether this workstream should conclude rather than wait.** Its registered
  goal is dispositioning the dogfood cycle's findings, and that is done except
  for one item blocked on another workstream's Stage 7. Concluding and handing
  the convention onward is a real option; it was not taken because the
  lifecycle call belongs to `project-management`, which has now been told. The
  cost of waiting is a registry row that looks abandoned; the cost of
  concluding is that the next protocol finding has no open owner.
- **Whether the three routed questions are one question.** All three are about
  the workflow's packaging rather than its rules — who reads it, how it loads,
  where it lives. They were sent separately because they can be decided
  separately, but a decision to extract the workflow would largely determine
  the other two, and `project-management` may prefer to take them as one.

### Deliberately Not Preserved

The 2026-08-16 and 2026-08-17 conversations. What mattered is above, in the
task sections, or in the intake files. The three routed questions carry their
own reasoning to the recipient, so this handoff does not restate it beyond
*Twelfth Task*.

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
- Verified at the 2026-08-17 pause, not carried forward on trust: `origin/main`
  is at the merge of this workstream's third outbox send;
  `workflow-improvements/v1` is three commits ahead of it and pushed;
  `workflow-improvements/outbox` holds the third send and merges independently.
  This workstream holds no containers, ports, or manual environment state — its
  entire external footprint is Git refs.
- Registration versus pull-request delivery is no longer a conflict. Resolved
  2026-08-16: registration travels the sender's outbox like any other message,
  so nothing commits directly to `main`. Recorded here because this entry
  asserted the opposite for a week.
- Corrected 2026-08-17, second time this claim has moved. This entry said the
  repository merge strategy rewrites commit identities. It did for every
  delivery up to and including the third outbox send, and it did not for
  `PR #19` and `PR #20`, which the product owner merged as merge commits. Both
  branches are now ancestors of `main`, and synchronizing this one was a
  fast-forward where the same operation previously required a hard reset.
  Strategy is therefore a per-pull-request property of this repository today,
  not a fixed fact — so keep verifying by content with `git cherry`, which is
  correct under every strategy, rather than by ancestry, which is correct only
  under some. See *Open Threads* for the standing question.
- This track overlaps `CURRENT-STATUS.md`, `WORKFLOW.md`, `AGENTS.md`, and the
  workflow requirements. Synchronize with `main` before integrating.
- Two bootstrap exceptions have now published workflow changes from
  `project-management` because this workstream had not started. A third would
  suggest the split between the two tracks is not working as intended.

## Workstream Document Index

This workstream owns:

- this status file;
- [`intake-dispositions.md`](intake-dispositions.md), the durable record of
  what became of every item delivered here; and
- its `intake/` directory.

Intake items are a queue rather than permanent documents and are deliberately
not listed here or in `index.md`; the directory listing is the queue. The
disposition log is the opposite and is listed, though not in `index.md`.
