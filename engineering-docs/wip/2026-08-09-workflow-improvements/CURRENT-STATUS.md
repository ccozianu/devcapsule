# Workstream Current Status: Workflow Improvements

Mnemonic: `workflow-improvements`

Start date: 2026-08-09

State: active; intake received, not yet dispositioned

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

The active branch is `workflow-improvements/intake`, forked from the
registration commit on `main` and resynchronized with `main` on 2026-08-16.

The branch name predates the `intake/` directory convention introduced on
2026-08-16 and now collides with it confusingly. See *Open Threads*.

## Current State

- Corrected 2026-08-16. This handoff previously said no workflow correction had
  been implemented. Two rounds have since landed, both published by
  `project-management` as deliberate bootstrap exceptions because this
  workstream had not started: verified divergence resolution, the merge-landed
  check, and rule 11's non-exclusive editing on 2026-08-15; then the whole
  workstream intake mechanism on 2026-08-16.
- This workstream's `intake/` received six items and holds four. Two were
  accepted and implemented on 2026-08-16; see *Dispositions*. A seventh, on
  shared bug vocabulary, is committed on `project-management/coordination` and
  reaches this directory when that branch merges — itself an illustration of
  why the outbox now exists.
- The four remaining items are the communication-protocol and concurrency
  clusters. Dispositioning them is the next task.
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
  delivery paragraph points at the outbox.
- `AGENTS.md`: synchronize before planning, send through the outbox.
- This workstream's `intake/README.md`: points at `WORKFLOW.md` rather than
  restating the delivery rule, so the next protocol change does not make it
  stale again.

An earlier finding of this workstream's own is now fixed by the same section.
**A stale branch cannot see its own intake.** Discovery reads `main`, so items
are visible from anywhere, but the files an agent must edit and delete to
disposition them exist only on a synchronized branch. *Staying Current With
`main`* states that directly.

## Next Resumable Task

Disposition the four remaining intake items: accept, defer, or reject each,
record the outcome and reasoning under *Dispositions*, then remove the file.
Two clusters remain — communication-protocol completeness (intake
acknowledgement, pausing and conversational continuity) and concurrency (the
worktree procedure, external-resource ownership and reaping).

The stale facts identified on 2026-08-16 are all corrected.

Done means:

- every item present carries a recorded disposition and reasoning;
- accepted items have an order, since several are one design rather than
  several;
- deferred and rejected items say why, so they are not silently reopened; and
- the workstream's bounded scope is still credible after the accepted set is
  known.

Two decisions are worth making before, not during. Whether to defer the
concurrency cluster to recursive-dogfood Stage 7, which is where its code would
live and which keeps this workstream bounded. And whether the acknowledgement
item can be designed at all before the product owner supplies the ideas they
deliberately reserved for it — that item says to ask first.

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

1. **Rename this branch?** `workflow-improvements/intake` now collides with the
   `intake/` directory convention and already confused a human reader once.
   Still unanswered, and no longer free: the branch now carries unique commits,
   so a rename means a new branch, a registry row, a push, and retiring the old
   ref. Something like `workflow-improvements/protocol` would remove the
   ambiguity. Cheaper before the next integration than after.
2. **Does "the workflow improvements already identified" mean identified, or
   identified and implemented?** The product owner named that as a condition for
   starting their own projects on v026. The two readings put very different
   obligations on this workstream, and it is currently described as being on the
   critical path for those project starts.

3. **Who owns protocol boilerplate that lives inside another workstream's
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
