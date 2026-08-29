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

## Lifecycle

`project-management` is the reserved workstream that `WORKFLOW.md` requires of
every multiple-stream project; it conforms to the general rule rather than
being excepted from it, and remains open while the repository uses
`workflow-type = "multiple-streams"`. Two historical facts worth keeping: the
workstream predates the rule — it was opened on 2026-08-09 by explicit
product-owner decision and the rule was written on 2026-08-16 — and one narrow
adoption exception survives: this repository adopted `multiple-streams` on
2026-08-08 and created the reserved workstream a day later, whereas a
conforming project creates both in the same commit.

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
  to `workflow-improvements` required the very mechanism being defined. The four
  workstreams now have `intake/` directories, and the two checkpoint items that
  were never delivered on 2026-08-15 have been delivered, along with the product
  owner's commit-cadence and branch-synchronization proposal.
- A V1 readiness assessment is recorded for 2026-08-16. Its central finding is
  that V1 itself is untracked: the gap review defines four milestones, three of
  which appear in no other document and have no owning workstream. Defining V1
  precisely is therefore this workstream's next task.
- The minimal workflow improvements it identified are published in
  `WORKFLOW.md`: verified divergence resolution, the merge-landed check, and
  non-exclusive file editing with a handoff carve-out. This was a deliberate
  bootstrap exception, because `workflow-improvements` could not start cleanly
  without them.
- The second portfolio checkpoint is recorded for 2026-08-16. It sets release
  sequencing: v026 carries the self-contained entry point and the URL-open fix
  and is delegated to `recursive-e2e`; the contained display moves to v027; and
  bug vocabulary goes to `workflow-improvements`.
- v026 is complete and recommended on `main`. `recursive-e2e` is paused by the
  product owner as of 2026-08-18 after completing Stage 6; Stage 7 is its next
  task when resumed. Its widened registered goal remains accurate because it
  delivered product work as well as recursive-E2E evidence.
- `workflow-improvements` is paused as of 2026-08-17 with its intake
  dispositioned. `project-management` itself has seven pending intake items from
  that workstream; they have been read but not yet dispositioned.
- This workstream's outbox branch was created and first used on 2026-08-18,
  carrying one item to `workflow-improvements`: a request to state what kind of
  thing the outbox is. The product owner, who proposed the outbox, reports that
  its intent — a Git convention for reaching `intake/` on `main` without the
  sender's work-in-progress riding along, not an entity in the information model
  — is not conveyed by the current text. Delivered: the send landed on `main`
  through `PR #25`, verified 2026-08-18 against `origin/main`.
- Two intake items written on 2026-08-16 sat undelivered until 2026-08-18: the
  bug vocabulary for `workflow-improvements` and the v026 deliverables for
  `recursive-e2e`. Both existed only in `944a0a6` on this workstream's branch.
  The 2026-08-16 checkpoint states they were delivered; that was true of the
  branch and false of `main`. Both rode the outbox at `dd1e892` and landed
  through the same `PR #25`; all three items are present in the recipients'
  `intake/` directories on `origin/main`. That `workflow-improvements` paused
  reporting its intake dispositioned is not an obstacle to delivering the first:
  the authoritative invariant is evaluated against `main`, not against a
  workstream's account of itself, and a recipient that has stopped is exactly
  the case the durable queue and *Intake Gates Completion* exist to cover.
- The outbox is pushed and undelivered as of 2026-08-18. Local and remote
  `project-management/outbox` both stand at `4b46db5`, carrying six deliveries
  including the `contained-display` registration: the registry-row ownership gap
  to `workflow-improvements` and the offer to `recursive-e2e` to widen its own
  goal cell, both from the `PR #28` conflict; the product owner's task to
  `workflow-improvements` to define the workflow's information model minimally
  and for non-native readers; and the notice that the same workstream owns the
  in-V1 workflow component; and, on 2026-08-19, the measured case that
  coordination state does not belong on `main` at all, with the recommendation
  to move it to a separate ref in the same repository. The later items were
  appended rather than sent from a reset branch, because resetting would have
  destroyed the earlier ones as undelivered mail; that gap is already reported
  in the 2026-08-18 outbox-is-a-mechanism item.
- **Delivered, verified on resume 2026-08-19.** The product owner opened and
  merged both pending pull requests while this pair was paused: `PR #30` took
  the outbox at `4b46db5` onto `main`, and `PR #31` took this branch at
  `6a690c1`. All five deliveries — the registry-row ownership gap, the goal-cell
  offer, the information-model task, the workflow-component notice, and the
  coordination-storage analysis with the `contained-display` registration — are
  now in their recipients' `intake/` directories on `origin/main`. The
  registration is real to everyone, and the three uncommunicated decisions are
  communicated.
- One outbox commit did not travel: `afb893f`, the amendment that separates the
  ratified storage boundary from the argument around it, was written after the
  branch state `PR #30` merged. On resume it was resent from an outbox reset to
  current `main`, now at `b1f7273` and carrying that single item, which is the
  shape the outbox rule asks for and the one the earlier append violated. It
  awaits a pull request this environment still cannot open — re-verified
  2026-08-19 that there is no `gh` CLI and no `GH_TOKEN` or `GITHUB_TOKEN` here.
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
- Real-project dogfood produced an accepted product requirement on 2026-08-19:
  each compatible IDE gets one developer-owned prototype of configuration and
  plugins, new projects receive independent full copies by default, an explicit
  clean start remains available, and later prototype updates are explicit after
  an advisory post-exit comparison. `R-SETTINGS-001` moved from a deferred
  implementation requirement to the product requirement set, and the
  [IDE profile prototype specification](../../specifications/product/ide-profile-prototypes.md)
  records the lifecycle. Its release target remains undecided.
- `project-management` is the standing home for cross-workstream priority,
  sequencing, dependency, and lifecycle decisions.
- No other workstream's task details or WIP documents have been moved here.

## Intake Dispositions

Recorded 2026-08-29, at the product owner's direction, closing three of the
nine pending items. Per the intake convention the files are removed from
`intake/`; Git retains them.

- **`2026-08-16-workflow-improvements-reserved-workstream-adopted.md` —
  accepted, reconciliation done.** The stale *Lifecycle Exception* section of
  this handoff is replaced by *Lifecycle* above, stating conformance to the
  now-general reserved-workstream rule while keeping the two historical facts
  the sender flagged as worth keeping. The retirement pointer is gone;
  `WORKFLOW.md` now defines retirement.
- **`2026-08-17-recursive-e2e-audit-undelivered-work.md` — answered.** The
  audit's finding, supported by persisted records rather than reconstructed
  conversation: undelivered work was lost because **outbox resets destroy
  undelivered mail, and the protocol as then specified permitted exactly
  that** — a send resets the outbox from current `main` and carries only what
  is being sent, with no rule protecting unreceived mail still on the branch.
  The specified protocol was followed; the specification was incomplete. The
  decisive evidence is self-demonstrating: this very audit request, pushed on
  `recursive-e2e/outbox` at `ebad342` on 2026-08-17, was itself orphaned by a
  later reset — the exact failure mode it asked about — and was recovered and
  delivered only on 2026-08-27 through PR #43. The recovery and the recurring
  reset-versus-unreceived-mail tension are recorded in the `recursive-e2e`
  conclusion (`engineering-docs/archive/2026-08-06-recursive-e2e/`); the
  2026-08-27 pause record of this handoff shows the same tension governed this
  workstream's own send ordering. Preventing recurrence is protocol content
  and belongs to `workflow-improvements` when it next resumes; the exposure
  ends structurally only when a send stops implying a reset while unreceived
  mail exists.
- **`2026-08-23-recursive-e2e-non-interactive-runs-have-no-owner.md` —
  accepted, already represented.** The release-blocking ruling of 2026-08-23
  is carried by the coordination backlog's *Non-Interactive Runs* entry, which
  since 2026-08-29 also records the decided mechanism: the capsule supervisor
  with no GUI children (ledger row *Capsule Supervisor And Multi-IDE
  Sessions*). Of the decisions the item asked for, support-versus-refusal is
  decided (supported, in V1); the authorization/acknowledgement shape, the
  requirement record, and the owning workstream remain open in that backlog
  entry, with owner assignment deferred until pickup per the 2026-08-29
  unowned-rows ruling.

- **`2026-08-17-workflow-improvements-intake-staleness-is-yours.md` —
  decided, 2026-08-29, by the product owner.** No dedicated staleness
  mechanism will exist; that is the decision, deliberately recorded. What is
  adopted instead is the **invariant**: the intake exclusive-or becomes
  mechanically checked, via the `pre-commit`-based design in
  [Workflow Invariants As Pre-Commit Hooks](2026-08-29-workflow-invariants-pre-commit.md)
  and its coordination-backlog entry — offered to adopters as opt-in local
  hooks and run in this repository's Nox gate, which supplies the
  checker-is-not-the-delinquent property the checkpoint-sweep option wanted
  without a manual obligation. The release gate remains what catches rot; the
  same-day evidence for the invariant check is commits `3873356`/`df36750`,
  where this workstream broke the invariant and nothing mechanical noticed.
  The item's rider — the `workflow-improvements` lifecycle call, sharpened by
  Stage 7's dissolution having changed the shape of that workstream's one
  blocked item — was decided on 2026-08-29 by the product owner:
  `workflow-improvements` **stays open, idle**. It keeps its one acknowledged
  item (the external-resource ownership convention, whose blocker changed
  shape when Stage 7 dissolved into backlog entries) rather than concluding
  and handing it onward, and it resumes when that item or new protocol work
  becomes due. Recorded here rather than in that workstream's handoff, which
  restriction 11 protects from other workstreams' edits.

- **`2026-08-17-workflow-improvements-human-readable-workflow-doc.md` —
  accepted, 2026-08-29, by the product owner: the project owes a
  human-readable workflow document.** Recorded as the `in-v1` ledger row
  *Human-Readable Workflow Documentation*, unowned until pickup. The intake
  item's recommended shape — an onramp inside `WORKFLOW.md` rather than a
  second parallel document, on the duplicated-normative-text evidence — is
  carried in the row as recommended-not-ratified, with the final shape
  settled together with the extraction-and-seam decision it interacts with.

- **`2026-08-17-workflow-improvements-workflow-loading-and-packaging.md` —
  rejected for V1, 2026-08-29, by the product owner**, unless the skills
  convention is identified as widely adopted and buying our users something
  tangible — the stated reopening trigger. Recorded as the `rejected` ledger
  row *Workflow Packaging As A Vendor "Skill"*. The item's underlying
  progressive-disclosure finding (layer the 1772-line document: small
  mandatory core, procedure loaded on demand) is deliberately kept, folded
  into the *Human-Readable Workflow Documentation* row and the open
  extraction-and-seam decision rather than dying with the rejection.

- **`2026-08-17-workflow-improvements-workflow-extraction-and-seam.md` —
  decided, 2026-08-29, by the product owner.** V1 ships with this workflow;
  `R-PRODUCT-004` stands unamended, so the decision-record amendment the item
  anticipated is unnecessary. Whether an adopter can install an alternative
  workflow moved to the ledger's *Optional For V1* list as
  *An Alternative Workflow Can Be Installed*, in plain words — the owner
  retired the word "seam" as unintuitive. Extraction to a separate repository
  is not pursued; its named costs stay recorded in the item (Git history).

Still pending in `intake/`, two items: the outbox-adoption item of 2026-08-16
(overtaken by events; closure expected next) and the initialization-tooling
routing item.

## Last Task And Status

Last task: the 2026-08-27 session, resumed at the product owner's direction
after v0.2.7 (the new argparse CLI under the unified release identity) was
released and verified. A high-progress coordination session; the owner ended
it deliberately without forcing the pending decisions.

Status: complete. What it did:

1. **`recursive-e2e` concluded successfully** (PR #44). Its outbox was first
   recovered and delivered (PR #43) — including the 2026-08-17 audit request
   that a later outbox reset had orphaned, the exact failure mode it
   reports. Its branches are deleted; its archive is
   `engineering-docs/archive/2026-08-06-recursive-e2e/`.
2. **Stage 7 dissolved** by the owner's ruling into four decision entries in
   the [coordination backlog](coordination-backlog.md) (*Dissolved Stage 7
   Items*), including the non-interactive-runs item the owner ruled
   release-blocking on 2026-08-23.
3. **The ledger gained two rows**: the decided `in-v1` VSCodium
   independent-IDE surface (retire `codium_with_claude`, normal project
   path; chess-club website proposed as its sample), and the `proposed`
   capsule supervisor (capsule lifetime = supervisor, not one foreground
   IDE; multi-IDE sessions; the natural non-interactive mechanism).
4. **The supported-project-types recap** was discussed and shaped
   (Python app/library, data-research, Python+TS web app, agent choice,
   independent IDE; Java/CUDA/teams explicitly not claimable) but is not yet
   written into the ledger — it awaits the release-thesis answer.

The previous task record follows.

Previous task: capture the IDE-profile behavior decided while bootstrapping
the first named real project, `devcapsule-sample-trading-research`.

Status: complete. The former deferred `R-SETTINGS-001` is now an accepted,
implementation-agnostic product requirement, with a dedicated specification
covering first-session capture, independent physical copies, explicit empty
state, advisory change detection, explicit atomic promotion, compatibility,
concurrency, and failure safety. The implementation release remains unassigned.

Preceding task: the second 2026-08-19 session, which resumed this workstream
after the travel pause. Status: complete and preserved in the
[2026-08-19 session record](../../session-records/devcapsule/2026-08-19-resume-verification-and-individual-projects.md).

Preceding task: the first 2026-08-19 session, which the product owner
interrupted for travel. It was a coordination session rather than a ledger
session, and it produced five decisions and five sends.

Status: complete, and delivered — its sends reached `main` through `PR #30`
and `PR #31` during the pause. What it decided:

1. **The workflow is in V1 as an optional component**, owned by
   `workflow-improvements`. Recorded as the ledger's sixth decided row.
2. **A storage boundary**: durable records stay on `main` and keep review;
   coordination state moves off the main branch, detached branch preferred.
   Recorded as a constraint on that same row.
3. **The present terminology ambiguity is accepted** for the duration of the
   current dogfood work, with the information model handed over as a task rather
   than fixed in place.
4. **v026 is good enough to start real projects on.** The product owner will
   raise the individual projects in a later session.
5. **`contained-display` was opened**, and `recursive-e2e` was not concluded.

What it sent, all riding `project-management/outbox` at `afb893f`: the
information-model task; the workflow-component ownership notice; the
coordination-storage analysis with its ratified boundary; the
`contained-display` registration with its design input; plus the two items from
the `PR #28` conflict that were already there.

What it wrote here: the
[display transport note](2026-08-19-display-transport-options.md), the
[issue-tracker note](2026-08-19-workflow-versus-issue-trackers.md), and criteria
added to `R-GTM-001` and `R-PRODUCT-004`.

Preceding task: record the second portfolio checkpoint, setting release
sequencing across v026 and v027 and delegating the work.

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

**Resume at the four questions recorded at the 2026-08-27 pause**, in rough
order of leverage. The owner deliberately left them undecided — good
progress does not require premature decisions.

1. **The release thesis**: containment product versus workspace product.
   Still gating roughly half the unwritten ledger rows (F1–F8, E1–E8), and
   the session's supported-project-types recap leans containment. Standing
   agent recommendation: containment.
2. **The capsule-supervisor split**: ratify, amend, or reject the proposal
   that V1 carries the supervisor as lifecycle anchor only (headless-capable,
   explicit session end — which answers the release-blocking
   non-interactive-runs backlog item) while the desktop-integration layer
   (tray, one-click secondary IDEs, multi-IDE sessions) leads the first
   post-V1 milestone.
3. **Register `codium-surface`**: the VSCodium row is decided `in-v1` but
   has no owning workstream; registration is main-first, and its scope
   should be shaped against the supervisor answer in question 2.
4. **Disposition this workstream's own intake** — now nine items: the seven
   workflow-improvements items pending since 2026-08-18, plus the recovered
   audit request (its answer is now largely known: outbox resets destroyed
   undelivered mail; the recovery is documented in the recursive-e2e
   conclusion) and the non-interactive-runs item (already represented in the
   backlog; the disposition should record that).

The earlier task list follows and remains valid behind these.

**Resume inside the individual-projects question.** The first project is now
named: `devcapsule-sample-trading-research`, a Python/PyCharm project with Codex
and Claude Code. Its first finding already returned to this repository as
`R-SETTINGS-001`. What remains is to name any other projects and decide whether
returning DevCapsule findings is an explicit obligation for all of them or only
an emergent practice. The original frame remains in thread 7 below and in the
[session record](../../session-records/devcapsule/2026-08-19-resume-verification-and-individual-projects.md).

**The outbox no longer blocks the work.** `PR #30` and `PR #31` merged during
the pause, so all five deliveries are on `main` and `contained-display` is
registered. One follow-up commit remains: the ratified-boundary amendment, now
on `project-management/outbox` at `b1f7273`, needs a pull request the product
owner must open. It refines an item already delivered rather than announcing
anything new, so it gates nothing below.

Then define V1. Until now V1 has been a target held in the product owner's head
plus a dated gap-review snapshot; the obvious prerequisites were clear, but the
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

Reviewed at the second 2026-08-19 pause and carried forward; only thread 7
changed, gaining the frame the session built. Rewritten at the first 2026-08-19
pause, which the product owner called for travel.
Threads settled during that session have been removed rather than annotated;
what remains is live. Originally written at the 2026-08-16 pause. This is a
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
5. **The use-case set grew to three on 2026-08-19** and is still unwritten. The
   product owner named the learner or tinkerer, the serious solo developer, and
   small teams of roughly two to five, calling the case for all three clear. It
   has never been recorded as a ledger section, and both 2026-08-19 notes now
   lean on it — the issue-tracker answer turns on the claim that these users
   have no tracker to replace. Writing it up is small and overdue.
6. **`R-GTM-001` carries `status: implemented` that is no longer true.** The
   criteria added on 2026-08-19 require the announcement to answer the
   issue-tracker objection, and `docs/product/v1-announcement.md` does not
   mention trackers at all. The status was deliberately left unchanged, because
   flipping a requirement's status is the product owner's call; `accepted` is
   the honest value if he wants it changed.
7. **The individual projects: first one named, routing rule still implicit.**
   `devcapsule-sample-trading-research` is the first real project: a
   Python/PyCharm environment with Codex and Claude Code. It is carried by the
   `sample-projects` workstream, so its finding about copied per-IDE profile
   prototypes had a route home and became accepted `R-SETTINGS-001`. The open
   coordination question is whether every real project explicitly owes such
   findings back to this repository, especially when a future project is a
   separate repository without an in-repository workstream. The original frame:
   the X11 passthrough hands every GUI capsule his trusted host session cookie
   and cannot be avoided while `DISPLAY` is required, and real projects worsen
   exactly the dimension that matters because agent work runs for hours; service
   dependencies and port allocation both reopen open V1 decisions; and — the
   part worth keeping — if each project is its own repository rather than a
   workstream here, findings have **no route home**, because a separate project
   has no outbox into this one. Per project he would be asked for: name and
   repository, size, declared capabilities, services beyond the checkout,
   whether it is GUI-driven, and what it should prove about DevCapsule.
8. **Two carried items from the 2026-08-18 critique, now the only part of it not
   superseded.** Whether the process-to-product commit ratio is acceptable
   dogfood cost or a signal to freeze `WORKFLOW.md` and spend the next stretch
   on the product; and the seven intake items in this workstream's own
   `intake/`, read on 2026-08-18 and still undispositioned. That critique was
   parked in a scratch file outside the repository; its measurements and
   recommendation are now in the delivered coordination-storage item, and these
   two questions are all that had no home.
9. **Whether the storage boundary earns a `Shared Constraints` line** in the
   root registry. Offered twice and not taken. The argument against is that it
   is not implemented yet, so a constraint would describe an intention.

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
- **The `recursive-e2e` disposition-log inconsistency is unreported.** On `main`
  its external-resource-reaping item sits in both `intake/` and its disposition
  log, which that log's header forbids: dispositioned on the branch on
  2026-08-17, deletion never travelled. One line for its owner to fix through
  its own outbox. Not sent, because it would be a third item for a paused
  workstream and the product owner may prefer it batched.
- **uid/gid across machines** is unverified. Whether formation identity and
  state layout survive a second developer with a different UID should be checked
  before "scales to multi-developer" is claimed anywhere.

### Deliberately Not Preserved

The conversations up to and including the first 2026-08-19 session. Their
decisions are in the ledger, the checkpoints, and the two 2026-08-19 notes, and
everything above is what would otherwise have been lost. Nothing from the
2026-08-16 or first 2026-08-19 sessions needs recovering to resume.

The second 2026-08-19 session is the exception, and preserved in full at the
product owner's explicit request: see the
[session record](../../session-records/devcapsule/2026-08-19-resume-verification-and-individual-projects.md).
It is a supplement, not a substitute — this handoff, the ledger, and the
requirement records remain canonical, and the record says so itself.

Also not preserved, deliberately: the scratch file holding the 2026-08-18
Git-as-substrate critique. It lived outside the repository, its substance is in
the delivered coordination-storage item, and its two unanswered questions are
thread 8 above. Nothing is lost if that file is gone.

## External State And Risks

- Paused 2026-08-27 at the end of the conclusion session. Everything is
  committed and pushed: `project-management/coordination` carries this
  handoff, the two new ledger rows, the backlog's dissolved-Stage-7 section,
  and the earlier per-IDE profile spec commit, all rebased onto `main` at
  `f29f31c`. Exercised latitude, recorded per the pause rule: the handoff
  was deliberately **not** sent alone through the outbox, because it
  references ledger rows and backlog entries that are deliverable content on
  this same branch — sending the record without its targets would publish
  broken references, and "the target lands no later than the reference"
  wins. Main's copy of this handoff is stale until the branch next
  integrates by pull request. The owner's `.idea` and trading-research
  submodule drift remain deliberately uncommitted working state.
- Paused 2026-08-19 for travel. The product owner reports that this laptop
  occasionally suffers kernel crashes when Docker instances are preserved
  through standby — rare but frequent enough to matter — so everything was
  pushed rather than merely committed. At the pause, local and remote agreed on
  both branches: `project-management/coordination` at `5f5ce8a` and later, and
  `project-management/outbox` at `afb893f`. Nothing was left in a stash or in
  the working tree. Re-verify these refs on resume rather than trusting this
  line.
- Paused again 2026-08-19, at the end of the resume session, when the product
  owner asked for the conversation to be persisted as the handoff. Everything is
  committed and pushed rather than merely committed, for the standby-crash
  reason below. At this pause: `project-management/coordination` at the head of
  this branch and `project-management/outbox` at `b1f7273`, local and remote
  agreed on both, nothing stashed and nothing dirty. The outbox carries one
  undelivered item and needs a pull request. Re-verify these refs on resume
  rather than trusting this line — the previous pause line was honest and still
  went stale within a day, because the product owner acted between sessions.
- Resumed 2026-08-19 and re-verified. The pause line held: nothing was stashed
  and nothing was dirty. `origin/main` had advanced nine commits past the local
  copy through `PR #30` and `PR #31`, so local `main` was fast-forwarded to
  `21d2503` and this branch was rebased onto it, dropping the four commits
  `PR #31` had already landed and carrying the four written after it. Because
  this branch is published but unshared, the rebase was force-pushed with a
  lease rather than merged. The outbox was reset from current `main` and resent,
  as recorded above. Local and remote now agree on both branches.

- Corrected 2026-08-15: this environment does have Git publication credentials
  and can push branches and unprotected `main`, and the local Docker CLI is
  authenticated to the registry. The earlier statement that a human must publish
  mainline commits was stale for at least two sessions and cost avoidable
  friction. Verify such constraints before relying on them.
- Refined 2026-08-16, so the correction above is not over-read. The `origin`
  remote is SSH, and that key authorizes Git transport only. There is no `gh`
  CLI and no `GH_TOKEN` or `GITHUB_TOKEN`, so this environment cannot create,
  review, or merge a pull request; those are GitHub API objects. For any
  workstream whose delivery method is a pull request, an agent prepares and
  pushes the branch and the human opens and merges it. Installing and
  authenticating `gh` would remove that limit.
- The permanent lifecycle is a documented repository-local exception until the
  `workflow-improvements` workstream defines and validates the general rule.
- Project management must remain coordination rather than a path for bypassing
  branch ownership, integration policy, or another workstream's handoff.

## Workstream Document Index

- [Portfolio checkpoint 2026-08-15](2026-08-15-portfolio-checkpoint.md)
- [Portfolio checkpoint 2026-08-16](2026-08-16-portfolio-checkpoint.md)
- [V1 readiness assessment 2026-08-16](2026-08-16-v1-readiness-assessment.md)
- [V1 scope ledger](v1-scope-ledger.md)
- [Workflow prior-art comparison
  2026-08-16](2026-08-16-workflow-prior-art-comparison.md)
- [Display transport options and clipboard policy
  2026-08-19](2026-08-19-display-transport-options.md)
- [The workflow versus Jira and GitHub Issues
  2026-08-19](2026-08-19-workflow-versus-issue-trackers.md)
- [Coordination backlog](coordination-backlog.md)
