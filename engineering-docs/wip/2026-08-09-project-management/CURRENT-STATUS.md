# Workstream Current Status: Project Management

Mnemonic: `project-management`

Start date: 2026-08-09

State: active; permanent coordination

Integration target: `main`

Delivery method: pull request

Requirements: `R-PRODUCT-003`, `R-PRODUCT-005`, `R-PRODUCT-006`

## Goal

Provide the durable project-management home for project-wide priorities,
sequencing, cross-workstream dependencies, and lifecycle decisions while this
repository uses the multiple-stream workflow.

This permanent track coordinates other workstreams but does not duplicate
their detailed handoffs, implement their scoped changes, edit their WIP state,
or become a miscellaneous backlog.

## Lifecycle Exception

The user explicitly opened this permanent workstream as a one-off operation
before the general workflow defines it. Unlike ordinary bounded workstreams,
`project-management` remains open while the repository uses
`workflow-type = "multiple-streams"`. The `workflow-improvements` backlog owns
formalizing that exception for all multiple-stream projects, including any
valid retirement or workflow-mode migration procedure.

## Branch Association

The branch is `project-management/coordination`. On 2026-08-18 the product
owner explicitly switched this checkout from `recursive-e2e/stage-4` to this
workstream after pausing recursive E2E. This branch was then rebased onto
current remote `main` at `a72d0a8` before project-management work resumed.

## Current State

- The first portfolio checkpoint is recorded for 2026-08-15.
- Workstream intake was introduced on 2026-08-16 at the product owner's
  direction, as a second deliberate bootstrap exception: `project-management`
  published the `WORKFLOW.md` and `AGENTS.md` changes because handing the item
  to `workflow-improvements` required the very mechanism being defined. The
  four workstreams now have `intake/` directories, and the two checkpoint items
  that were never delivered on 2026-08-15 have been delivered, along with the
  product owner's commit-cadence and branch-synchronization proposal.
- A V1 readiness assessment is recorded for 2026-08-16. Its central finding is
  that V1 itself is untracked: the gap review defines four milestones, three of
  which appear in no other document and have no owning workstream. Defining V1
  precisely is therefore this workstream's next task.
- The minimal workflow improvements it identified are published in
  `WORKFLOW.md`: verified divergence resolution, the merge-landed check,
  and non-exclusive file editing with a handoff carve-out. This was a
  deliberate bootstrap exception, because `workflow-improvements` could not
  start cleanly without them.
- The second portfolio checkpoint is recorded for 2026-08-16. It sets release
  sequencing: v026 carries the self-contained entry point and the URL-open fix
  and is delegated to `recursive-e2e`; the contained display moves to v027; and
  bug vocabulary goes to `workflow-improvements`.
- v026 is complete and recommended on `main`. `recursive-e2e` is paused by the
  product owner as of 2026-08-18 after completing Stage 6; Stage 7 is its next
  task when resumed. Its widened registered goal remains accurate because it
  delivered product work as well as recursive-E2E evidence.
- `workflow-improvements` is paused as of 2026-08-17 with its intake
  dispositioned. `project-management` itself has seven pending intake items
  from that workstream; they have been read but not yet dispositioned.
- This workstream's outbox branch was created and first used on 2026-08-18,
  carrying one item to `workflow-improvements`: a request to state what kind of
  thing the outbox is. The product owner, who proposed the outbox, reports that
  its intent — a Git convention for reaching `intake/` on `main` without the
  sender's work-in-progress riding along, not an entity in the information
  model — is not conveyed by the current text. Delivered: the send landed on
  `main` through `PR #25`, verified 2026-08-18 against `origin/main`.
- Two intake items written on 2026-08-16 sat undelivered until 2026-08-18: the
  bug vocabulary for `workflow-improvements` and the v026 deliverables for
  `recursive-e2e`. Both existed only in `944a0a6` on this workstream's branch.
  The 2026-08-16 checkpoint states they were delivered; that was true of the
  branch and false of `main`. Both rode the outbox at `dd1e892` and landed
  through the same `PR #25`; all three items are present in the recipients'
  `intake/` directories on `origin/main`. That `workflow-improvements` paused
  reporting its intake dispositioned is not an obstacle to delivering the first:
  the
  authoritative invariant is evaluated against `main`, not against a
  workstream's account of itself, and a recipient that has stopped is exactly
  the case the durable queue and *Intake Gates Completion* exist to cover.
- The outbox is pushed and undelivered as of 2026-08-18. Local and remote
  `project-management/outbox` both stand at `4b46db5`, carrying six deliveries
  including the `contained-display` registration: the
  registry-row ownership gap to `workflow-improvements` and the offer to
  `recursive-e2e` to widen its own goal cell, both from the `PR #28` conflict;
  the product owner's task to `workflow-improvements` to define the workflow's
  information model minimally and for non-native readers; and the notice that
  the same workstream owns the in-V1 workflow component; and, on 2026-08-19, the
  measured case that coordination state does not belong on `main` at all, with
  the recommendation to move it to a separate ref in the same repository. The
  later items were
  appended rather than sent from a reset branch, because resetting would have
  destroyed the earlier ones as undelivered mail; that gap is already reported
  in the 2026-08-18 outbox-is-a-mechanism item. All five await a pull request
  this environment still cannot open — re-verified 2026-08-18 that there is no
  `gh` CLI and no GitHub token here.
- The product owner ratified a storage boundary on 2026-08-19: durable records
  stay on `main` and keep review; coordination state — the chatter, status, and
  coordination items — moves off the main branch, with a detached branch
  preferred. It is recorded as a constraint on the workflow-component ledger row
  rather than as its own row, since the component's shape already owns it, and
  the item on the outbox now separates the ratified boundary from the argument
  around it. Not yet implemented, and deliberately sequenced after the
  information model so the protocol text is not written twice.
- `contained-display` was opened on 2026-08-19 at the product owner's direction,
  resolving the unassigned owner on the contained-display ledger row. The
  question of whether to conclude `recursive-e2e` and open a v027 workstream was
  raised and answered no on two grounds: Stage 7 is the persistence and
  safe-cleanup half of that workstream's own registered goal, and its intake is
  not clear, which *Intake Gates Completion* makes a hard bar. It ends when
  Stage 7 lands and its intake clears, not administratively.
- Found while checking that bar, and reported to nobody yet: on `main`,
  `recursive-e2e`'s `2026-08-17-workflow-improvements-external-resource-reaping`
  item is in **both** `intake/` and its disposition log, which that log's own
  header forbids. The disposition was recorded on the branch on 2026-08-17 and
  the deletion never reached `main`. Harmless in itself, one line for its owner
  to fix through its outbox, and the same failure family as the stranded items.
- The V1 ledger gained its sixth decided row on 2026-08-18: the workflow ships
  in V1 as an optional component, owned by `workflow-improvements`. The row
  states the tooling question as open and sequenced behind the information
  model, which discharges shortcoming 8's requirement that a workflow-tooling
  deferral not be silent. The product owner also accepted the present
  terminology ambiguity for the duration of the current dogfood work, which is
  why the information model was sent as a task rather than fixed in place.
- `PR #28`, this workstream's own delivery of the 2026-08-16 checkpoint and the
  ledger work, merged at `8b2ac0c` on 2026-08-18 with its registry conflict
  resolved in favour of `recursive-e2e`'s version. The checkpoint, the ledger,
  and the registry updates are therefore on `main`, and this branch has been
  rebased onto `fdf4c37`.
- `project-management` is the standing home for cross-workstream priority,
  sequencing, dependency, and lifecycle decisions.
- No other workstream's task details or WIP documents have been moved here.

## Last Task And Status

Last task: record the second portfolio checkpoint, setting release sequencing
across v026 and v027 and delegating the work.

Status: complete. The
[2026-08-16 checkpoint](2026-08-16-portfolio-checkpoint.md) records three
decisions, delivers two handoffs through intake rather than announcing them,
corrects two stale registry facts about `recursive-e2e`, and widens that
workstream's registered goal so the registry no longer understates where product
work lives.

Preceding tasks, both complete: the
[V1 readiness assessment](2026-08-16-v1-readiness-assessment.md), which records
eight unowned shortcomings and seven documented items to pin to V1; and the
[first portfolio checkpoint](2026-08-15-portfolio-checkpoint.md).

## Next Resumable Task

Define V1. Until now V1 has been a target held in the product owner's head plus
a dated gap-review snapshot; the obvious prerequisites were clear, but the
release boundary is not. Complete the [V1 scope ledger](v1-scope-ledger.md),
which now holds six decided or proposed rows.

Start by settling the release thesis in *Open Threads* below. Roughly half the
remaining rows cannot be written without it, so beginning anywhere else produces
verdicts that may not survive the answer.

Done means:

- every gap in the V1 gap review carries a release verdict — in V1, deferred to
  a later release, or rejected — with the rejections and deferrals stated rather
  than left silent;
- every item retained for V1 names an owning workstream, and any milestone with
  no owning workstream is either registered as one or explicitly reassigned;
- the five functional scope decisions the gap review left open are decided, or
  carry a decision date and a named decider;
- V1 acceptance is stated as criteria that can be checked: which requirement
  records must reach `validated`, which open bugs block, and which documents
  must exist;
- the seven at-risk items in the readiness assessment each hold a single
  recorded home rather than several partial ones; and
- the ledger's cross-workstream consequences actually reach the affected
  workstream handoffs, given that the previous checkpoint's handoff to
  `workflow-improvements` never arrived in the document that workstream reads.

Record a further checkpoint only when the next cross-workstream priority,
sequence, dependency, or lifecycle decision becomes due. Checkpoints are
written because a decision is needed, not on a schedule.

## Deferred From This Workstream

Decide the release target for the file locking protocol in the
[coordination backlog](coordination-backlog.md), including whether ordinary Git
conflict resolution makes it unnecessary. Recording that it is unnecessary is a
valid outcome. This was the previously planned next task and is deliberately
sequenced behind defining V1, since the V1 boundary determines whether the
protocol is a release commitment at all.

## Open Threads

Written at pause on 2026-08-16 and re-read on resume on 2026-08-18. This is a
trial of the `Open Threads` shape
proposed to `workflow-improvements`; the format is not ratified, and structuring
this workstream's own handoff needs no protocol change. Kept deliberately short:
questions and reasoning hooks, not a transcript.

### Awaiting The Product Owner

1. **The release thesis.** Containment product — one IDE, boundary provable,
   agent-safety wedge — versus workspace product with multi-IDE breadth. Decides
   roughly half the unwritten ledger rows. Agent recommendation: containment,
   because it is where the project is ahead of the field rather than behind it.
2. **Java: inside the V1 window or immediately after.** Inside, it competes with
   concurrency and the entry point; after, it becomes the first post-V1
   milestone and gives the announcement a concrete next promise.
3. **Fourth agent, Case A.** Bring-your-own-endpoint is proposed `in-v1` and
   unratified. Case B, DevCapsule running the model, is proposed `deferred`.
4. **The twelve-week release shape**, carried as `proposed` in the ledger and
   never ratified — and now stale, because moving the contained display to v027
   removed a block the shape assumed was inside the window. It needs rebuilding
   before it can be ratified.
5. **Is the use-case set complete at two?** The learner/tinkerer and the serious
   solo developer. The agent offered to write the set up as a ledger section
   once complete; that remains undone.

### Weighed And Unresolved

- **Concurrency was chosen over VSCodium** for the extra four weeks, on the
  argument that a broken first ten minutes costs more than a narrower platform
  list. Not revisited since the v027 deferral changed the surrounding shape.
- **noVNC provisionally preferred over Xpra seamless mode**, with a spike to
  decide. Xpra is the option that actually fixes desktop integration; noVNC is
  the more predictable and more demo-friendly. Neither is committed.
- **Skeleton delivery mechanism undecided:** submodule, matching the existing
  sample convention, or in-tree, which avoids another publishable repository and
  the unreachable-pointer bug. Raised, not answered.
- **`recursive-e2e`'s widened goal** is a registry patch, not a settled shape.
  The alternative is registering a separate workstream for product work; that
  workstream may raise it back.
- **uid/gid across machines** is unverified. Whether formation identity and
  state layout survive a second developer with a different UID should be checked
  before "scales to multi-developer" is claimed anywhere.

### Deliberately Not Preserved

The conversation itself. Decisions are in the ledger and the two checkpoints,
and everything above is what would otherwise have been lost. Nothing else from
the 2026-08-16 session needs recovering to resume this workstream.

## External State And Risks

- Corrected 2026-08-15: this environment does have Git publication credentials
  and can push branches and unprotected `main`, and the local Docker CLI is
  authenticated to the registry. The earlier statement that a human must
  publish mainline commits was stale for at least two sessions and cost
  avoidable friction. Verify such constraints before relying on them.
- Refined 2026-08-16, so the correction above is not over-read. The `origin`
  remote is SSH, and that key authorizes Git transport only. There is no `gh`
  CLI and no `GH_TOKEN` or `GITHUB_TOKEN`, so this environment cannot create,
  review, or merge a pull request; those are GitHub API objects. For any
  workstream whose delivery method is a pull request, an agent prepares and
  pushes the branch and the human opens and merges it. Installing and
  authenticating `gh` would remove that limit.
- The permanent lifecycle is a documented repository-local exception until
  the `workflow-improvements` workstream defines and validates the general
  rule.
- Project management must remain coordination rather than a path for bypassing
  branch ownership, integration policy, or another workstream's handoff.

## Workstream Document Index

- [Portfolio checkpoint 2026-08-15](2026-08-15-portfolio-checkpoint.md)
- [Portfolio checkpoint 2026-08-16](2026-08-16-portfolio-checkpoint.md)
- [V1 readiness assessment 2026-08-16](2026-08-16-v1-readiness-assessment.md)
- [V1 scope ledger](v1-scope-ledger.md)
- [Workflow prior-art comparison 2026-08-16](2026-08-16-workflow-prior-art-comparison.md)
- [Display transport options and clipboard policy 2026-08-19](2026-08-19-display-transport-options.md)
- [Coordination backlog](coordination-backlog.md)
