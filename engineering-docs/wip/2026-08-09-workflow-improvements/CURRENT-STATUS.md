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
- This workstream's `intake/` holds six delivered items. A seventh, on shared
  bug vocabulary, is committed on `project-management/coordination` and reaches
  this directory when that branch merges.
- No item has been accepted, deferred, or rejected yet. Dispositioning the
  queue is the next task.
- The branch was 37 commits behind `main` and carried three commits that were
  patch-identical duplicates of the registration commits. Rebasing dropped all
  three; the branch is now identical to `main`.

## Last Task And Status

Last task: resume the workstream, synchronize the branch, and assess the intake.

Status: complete. Nothing was dispositioned; this was orientation.

One finding came from the resumption itself and belongs to this workstream
rather than to any sender. **A stale branch cannot see its own intake.** Before
synchronizing, the workstream directory on this branch held only
`CURRENT-STATUS.md`. `WORKFLOW.md` correctly says to read intake from the
locally accepted mainline ref, so discovery works, but nothing says a branch
must be synchronized before an agent can *work* on the items it discovers. That
gap is one day old and was hit on the mechanism's first real use.

## Next Resumable Task

Disposition the intake queue: accept, defer, or reject each item, record the
outcome and reasoning here, then remove the file. Intake is a queue, not an
archive; Git retains the history.

Correct the three stale facts identified on 2026-08-16 in the same pass — two
are already corrected above and in *External State And Risks*; the third was
this document's claim to own only a status file.

Done means:

- every item present carries a recorded disposition and reasoning;
- accepted items have an order, since several are one design rather than
  several;
- deferred and rejected items say why, so they are not silently reopened; and
- the workstream's bounded scope is still credible after the accepted set is
  known.

## Assessment Of The Queue

Recorded on 2026-08-16 to inform dispositioning. Not itself a disposition.

The six items are not six independent problems. They cluster into three
designs.

**Delivery and synchronization mechanics.** The outbox-branch proposal, commit
cadence and branch synchronization, and this workstream's own long-standing
question about main-first registration under a pull-request policy. The outbox
item states explicitly that it and the registration question should be designed
together. A fourth input arrived on 2026-08-16: the repository is configured for
**rebase merge**, so every workstream branch acquires patch-identical duplicate
commits the moment its pull request lands. That is structural, not agent
improvisation, and it has now been observed on three branches. It also sits
awkwardly beside `AGENTS.md`, which cautions against imposing a rebase policy on
a pull-request workflow.

**Communication-protocol completeness.** Intake acknowledgement, and pausing
with conversational continuity. Both concern the shape of the message-passing
system rather than its plumbing: the first that delivery is fire-and-forget with
no reply path and no staleness signal, the second that pausing a workstream has
no defined effect on the conversation's substance.

**Concurrency.** The worktree procedure and external-resource ownership and
reaping. Both need design; the second needs code, and closes the detached
container cleanup bug as a side effect.

## Backlog

1. Make `project-management` a mandatory permanent workstream for every
   multiple-stream project.

   Done means:

   - multiple-stream initialization and adoption create exactly one reserved
     `project-management` workstream and its handoff;
   - the workflow defines its project-planning scope without turning it into a
     duplicate registry, implementation catch-all, or owner of other
     workstreams' WIP state;
   - its permanent lifecycle is reconciled explicitly with the current rule
     that ordinary workstreams are bounded and eventually end;
   - branch ownership, checkout selection, start-date layout, migration,
     integration, and exceptional retirement rules are deterministic;
   - `WORKFLOW.md`, agent instructions, reusable bootstrap assets, and
     `R-PRODUCT-006` agree; and
   - this repository's one-off `project-management` registration is reconciled
     with the adopted general rule and validation passes.

## Open Threads

Written at pause on 2026-08-16. Trial of the shape proposed in the pause and
continuity intake item. Short by design.

### Awaiting The Product Owner

1. **Rename this branch?** `workflow-improvements/intake` now collides with the
   `intake/` directory convention and already confused a human reader once. The
   branch currently has zero unique commits, so a rename costs only a registry
   row and a push — it will never be cheaper than now. Something like
   `workflow-improvements/protocol` would remove the ambiguity.
2. **Does "the workflow improvements already identified" mean identified, or
   identified and implemented?** The product owner named that as a condition for
   starting their own projects on v026. The two readings put very different
   obligations on this workstream, and it is currently described as being on the
   critical path for those project starts.

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
