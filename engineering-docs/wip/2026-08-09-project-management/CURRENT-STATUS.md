# Workstream Current Status: Project Management

Mnemonic: `project-management`

Start date: 2026-08-09

State: active; permanent coordination

Integration target: `main`

Delivery method: pull request

Requirements: `R-PRODUCT-003`, `R-PRODUCT-005`, `R-PRODUCT-006`

## Release Process Adopted (2026-09-11)

The product owner selected the release-candidate intake and directed this
workstream to handle it here, without further delegation, adopting the
successful v0.2.11 process for new versions. **Decision: acknowledged; the
release-process documentation task is complete on this branch.** The existing
[release guide](../../implementation-notes/devcapsule/2026-09-01-release-and-validation-process.md)
is the single canonical operator document. It now leads with preparation,
immutable RC publication, downloaded-candidate validation, acceptance,
integration, final tagging at the accepted source, and final download
verification. It includes the actual RC3/final source and acceptance record,
maintenance releases, and publication recovery. Prominent links in the root
README, documentation index, engineering welcome page, and CLI README make it
discoverable without a second process document.

Validation: compared the instructions with `release-pex.yml`,
`release-protocol.py`, and `prepare-promotion.py`; verified that the RC3 and
final tags both resolve to `94e798f1d1a7aaab93ae3e47d9636471448a8e66`, that this
commit is on fetched `origin/main`, and that it matches the committed acceptance
record. Relative documentation links and anchors pass; `git diff --check`
passes. This is a documentation change, so no new release or runtime test is
required.

Delivery: the guide travels this branch's ordinary PR. The release-candidate
intake's acknowledgment and deletion travel together through this workstream's
outbox; until that lands, the file remains in main's intake. The other seven
items are unchanged. The original intake's proposed coupling between every
matrix combination and promotion is not silently adopted: the shipped process
records the actual scope of acceptance, while the separate matrix-learning
and automated-validation items remain for their own decisions.

**Planned next step:** deliver this documentation and its intake disposition,
then continue reconciling the remaining seven intake items against v0.2.11
and the owner's decisions. No additional implementation task is selected.

**Open threads for this task:** PR/outbox delivery must be verified on remote
main before calling the item fully dispositioned. No release-process design
question is left open by this task, and no work was sent to another workstream.
Earlier next-step and eight-pending-item statements below are historical where
superseded by this section.

## Checkout Selected After v0.2.11 (2026-09-09)

The owner replaced component-catalog closure with a pause at the successful
v0.2.11 milestone, keeping it open for future components, and retained the
instruction to position this checkout on `project-management/coordination`.
That switch is complete. The local branch was fast-forwarded to current main
`a27e0ed`, which contains its prior recovery work through PR #67 and the outbox
deliveries through PRs #68 and #69. An initial switch to the obsolete local
branch would have overwritten populated sample-submodule files; fast-forwarding
the inactive branch first avoided changing or removing those files.

Component-catalog's unmerged archive proposal is withdrawn. Its working branch
at `85a94d6` and standing outbox at `986136f` carry the pause, resumable WIP
handoff, successful release/GUI evidence, and corrected historical intake claim.
The outbox contains only records/index changes and awaits main delivery; the
GitHub connector last rejected PR creation with HTTP 403. Do not infer that
the earlier closure proposal or a stale registry row is the owner's intent.
The separately registered `eclipse-surface` workstream retains its routing.

Read this handoff, Open Threads, and all eight intake items. Their historical
statements need reconciliation: launcher-delivered runtime and the RC promotion
protocol are now shipped in [v0.2.11](https://github.com/ccozianu/devcapsule/releases/tag/v0.2.11).
The original sync intake is recoverable at commit
`802adafa3d545895b979288a57cf1363329b94c7`; component-catalog corrected its
delivery account, and PR #69 published its acknowledgment. No intake item was
dispositioned merely by this checkout-selection task.

**Planned next step:** reconcile the queued intake against the shipped milestone
and owner decisions before prioritizing further work. The user has not selected
a new implementation task. Earlier pending-release, component-catalog closure,
and undelivered-PR statements below are historical, superseded where noted here.

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
- Decided 2026-08-29, by the product owner, closing the individual-projects
  routing question (formerly Open Thread 7): there will be **no dedicated
  findings-route mechanism** for real projects living in separate
  repositories — it is too fanciful a feature for V1. Adopters and external
  projects report findings as ordinary GitHub issues on the DevCapsule
  repository. In-tree projects carried by `sample-projects`, such as
  `devcapsule-sample-trading-research`, keep the workstream-intake route that
  already produced `R-SETTINGS-001`. No further action.
- Decided 2026-08-30, by the product owner: **the capsule supervisor core is
  assigned to `contained-display`** — one workstream for one sequenced
  effort, supervisor first, display as its first consumer. The assignment is
  delivered to that workstream's intake with the recommended V1 scope cut
  (PID-1 duties, declarative children, explicit session end, headless mode);
  the root registry row is updated, and the delivery travels this branch
  rather than the outbox under the recorded target-lands-no-later-than-the-
  reference latitude, since it cites ledger rows not yet on `main`.
- Decided 2026-08-30, by the product owner, settling the carried commit-ratio
  question: **`WORKFLOW.md` is considered frozen until a release candidate
  exists.** The scheduled check — whether workflow improvements are then
  needed — is the `v1-optional` ledger entry *Workflow Improvements At The
  Release Candidate*, which also records the freeze's interpretation: no new
  protocol changes, while already-decided release content (the human-readable
  onramp) and rule-mechanizing checks (the pre-commit invariants) proceed.
- Decided 2026-08-30, by the product owner: **`component-catalog` is
  registered** as the workstream that makes IDE surfaces and agent CLIs
  regular catalog components — the `codium` interactive surface first
  (taking ownership of the ledger row *Independent IDE Surface* and
  subsuming the anticipated `codium-surface` registration), then the
  Antigravity CLI as the Google agent slot. Three companion rulings recorded
  with it: Antigravity is a **default-selected component, not a base-image
  install** — the product owner explicitly chose this reading when the
  base-image phrasing was flagged as conflicting with `D-0005`, so agent
  neutrality stands, with just-in-time materialization into a cached local
  image and an `/opt/antigravity-cli` archive-unpack prefix preferred;
  `contained-display` is **paused until `component-catalog` shows
  significant progress**, with a resume-time intake item directing it not to
  change the supervisor↔component contract inadvertently; and the new
  workstream integrates to `main` **once per validated component** (unit
  tests plus a product-owner smoke test). The registration travels this
  branch under the same target-lands-no-later-than-the-reference latitude as
  the supervisor-core assignment above.
- **Found 2026-09-08: the outbox-reset loss recurred, and this time it took
  a real item.** `component-catalog` sent
  `2026-09-06-component-catalog-one-devcapsule-inside-and-outside.md` to this
  intake on 2026-09-06 and recorded the send in its handoff (`4e00985`, on
  `main` through PR #61) as outbox `802adaf`; its 2026-09-07 pause note
  records the delivery as merged. Neither is true of `main`. Verified against
  every ref in this clone: `802adaf` is not a valid object, the filename
  appears in no tree on any branch, and `component-catalog/outbox` was reset
  from `main` at `8d7d2fa` on 2026-09-07 (`47b4442`) carrying only the
  registry row and the handoff copy. This is exactly the mechanism answered
  on 2026-08-29 under `2026-08-17-recursive-e2e-audit-undelivered-work.md` —
  a send resets the outbox from current `main` and carries only what is being
  sent, with no rule protecting unreceived mail — and it is the **third**
  recorded occurrence, after the 2026-08-16 pair that sat undelivered until
  `PR #25` and the audit request `ebad342` that was orphaned by a later reset
  and recovered only through `PR #43`. The 2026-08-29 disposition routed
  prevention to `workflow-improvements` "when it next resumes" and observed
  that the exposure ends structurally only when a send stops implying a reset
  while unreceived mail exists; `WORKFLOW.md` has been frozen until a release
  candidate since 2026-08-30, so the exposure was knowingly left standing and
  has now been paid for a third time. Two consequences worth separating:
  - **The item is recovered**, reconstructed into this intake under its
    original filename so the handoff pointer resolves, and labelled as a
    reconstruction. The owner's question, the diagnosis, the recommended
    shape, and the 0.2.10 advice are recovered from the `component-catalog`
    handoff on `main`; the sender's two non-preferred shapes survived
    nowhere and are this workstream's reconstruction, flagged as such in the
    file. One mechanism fact was added from the tree: the inside/outside
    coupling in `devcapsule/container_runtime/contract.py` is already an
    explicitly versioned contract (`RuntimePlan.version` and
    `ComponentRuntimeTemplate.version` are written as `1` and refuse any
    other value), which reframes the question as a missing compatibility
    policy rather than a missing synchronization mechanism.
  - **The correction is delivered, not applied.** Restriction 11's carve-out
    protects `component-catalog`'s handoff, so the two false records were
    reported to its `intake/` as
    `2026-09-08-project-management-sync-item-never-arrived.md` rather than
    edited here.
- **Observed 2026-09-08, and this one is mechanically checkable.** The
  pre-commit invariant already designed in
  [Workflow Invariants As Pre-Commit Hooks](2026-08-29-workflow-invariants-pre-commit.md)
  checks the intake exclusive-or: every delivered item is either in `intake/`
  or in the disposition log. That design is not implemented yet, so nothing
  mechanical ran here — but **the invariant would not have caught this even if
  it had**: a lost item is in neither place, and nothing knows it was ever
  supposed to exist. The signal that was actually available is different and
  cheap — a handoff citing an outbox commit that is not an ancestor of `main`,
  and an outbox reset discarding commits not reachable from `main`. Offered to
  the backlog entry as a second, distinct check rather than folded into the
  first, since they detect different things. Whether it is written before the
  release candidate is a `workflow-improvements` scheduling question under the
  freeze, not this workstream's to settle.

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

- **`2026-08-16-workflow-improvements-initialization-tooling-has-no-owner.md`
  — accepted, 2026-08-30, by the product owner**, routed as directed: it is
  now the unowned coordination-backlog entry *Multiple-Stream Initialization
  Tooling*, assigned at pickup per the unowned-rows ruling, sharing its
  delivery path with the pre-commit invariants entry.

- **`2026-08-16-workflow-improvements-outbox-adopted.md` — acknowledged,
  2026-08-30; its three consequences are resolved or routed.** (1) The two
  then-stuck deliveries have long since landed: the v026-deliverables item
  reached `recursive-e2e` (dispositioned in its archived log) and the
  bug-vocabulary item sits in `workflow-improvements`' intake, awaiting that
  workstream's release-candidate resume along with six later arrivals.
  (2) The registration-travels-the-outbox answer is noted and already
  reflected in the unowned-rows ruling (registration at pickup). (3) The
  stale-README question — who owns protocol boilerplate inside another
  workstream's carve-out — is answered as a coordination ruling: each
  workstream owns its own copy, and the durable fix is READMEs as pointers
  to `WORKFLOW.md` rather than restatements. This workstream's own README
  is converted in this commit; `recursive-e2e`'s copy is archived and moot;
  `sample-projects`' copy is flagged for that workstream's next delivery.

Intake is empty. Every item ever received is in the disposition log.

## Last Task And Status

Last task: the 2026-08-29/30 rulings sessions, which settled all four resume
questions of the 2026-08-27 pause and went well beyond them.

Status: complete. In summary:

1. **The release thesis is decided**: workspace *and* containment — a
   workspace product wherein agents are sensibly contained so the user can
   happily run yolo mode by default. The twelve-week budget yielded to a
   maximal-wow bar; Java and Quarkus are in as samples (Eclipse default,
   IDEA available); the project-type divergence resolved by union; the
   devcapsule-on-the-side scenario is `in-v1`; the announcement was
   fact-checked, aligned, and now answers the issue-tracker objection with
   `docs/product/issue-tracker-positioning.md` behind it; `R-GTM-001`'s
   stale flag closed.
2. **The supervisor split is ratified** (core in V1, desktop integration
   post-V1), answering non-interactive runs; unowned rows are acceptable
   until pickup; `WORKFLOW.md` is frozen until a release candidate; the
   fourth agent Case A and CUDA are parked `v1-optional`.
3. **This workstream's intake went from nine items to empty**, every
   disposition logged; the invariant got its future guard (the pre-commit
   proposal) after this workstream briefly violated it itself.
4. **The ledger is structurally complete**: all sixteen gap verdicts written
   (`E1`–`E4` recorded as delivered), the seven at-risk items homed, the
   five scope decisions dispositioned, and a V1 acceptance section proposed.
   Five agent-proposed items await ratification.

The previous task record follows.

Previous task: the 2026-08-27 session, resumed at the product owner's direction
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

**Session 2026-09-08: eight intake items are pending and one of them was
recovered from a failed delivery.** What this session did, and what is left:

- Done: the lost `one-devcapsule-inside-and-outside` item is reconstructed
  into `intake/` (see *Current State*), and the correction `component-catalog`
  must make to its own two records is written to its `intake/` as
  `2026-09-08-project-management-sync-item-never-arrived.md`. Both await this
  branch's pull request; the correction additionally needs this workstream's
  outbox, since it is delivery to another workstream on `main`.
- **Not done, and deliberately: none of the eight pending items is
  dispositioned.** Every row in the disposition log names the product owner
  as the decider, and the sync item in particular decides whether the matrix
  keeps pinning base digests at all. The analysis is prepared; the ruling is
  the owner's.
- The eight pending items, in the order they are worth taking:
  1. **`one-devcapsule-inside-and-outside`** — the reframing to settle first,
     since the recovered item shows the contract is already versioned and the
     gap is a compatibility policy. It gates `component-catalog`'s resume,
     whose handoff forbids starting any of the three shapes without this
     disposition.
  2. **`release-candidate-concept`** — composes with it: the candidate stage
     decides whether a base release and a CLI release are one act or two,
     which is what shape 1 changes.
  3. **`internal-naming-drops-generation-vocabulary`** — note before ruling
     that its points 1 and 2 are already *executed*: `component-catalog`
     retired v026, added the `postgresql-client` entry, and renamed
     `substrate` to `base_family` with the single family `ubuntu-24.04`
     (matrix `embedded-16`, D-0007's second 2026-09-06 amendment). What is
     genuinely open is point 3, the commit/record house style, and where it
     is written down.
  4. **`matrix-learns-from-experiments`** — named by the release-candidate
     item as the source of its promotion rule ("a candidate becomes a release
     when every combination it pins has a claim of a successful run"), so it
     is read together with item 2 rather than separately.
  5. **`upgrade-experience-as-a-v1-feature`** (2026-09-03),
     **`automated-component-version-validation-research`** (2026-09-04),
     **`init-regenerate-versus-config-semantics`**, and **`development-blog`**
     — the remaining arrivals, unread this session. Note that
     `init-regenerate-versus-config` already carries an owner decision (leave
     `init` as is for now; settle the semantics here) and that
     `component-catalog` fixed one of its five points in `eb395fa` without
     waiting, so its disposition starts from four.
- Also for the owner, observed not acted on: `component-catalog/outbox` at
  `47b4442` is unmerged, so `main`'s registry still shows that workstream as
  active with the 0.2.10 walk mid-flight rather than paused with it complete;
  and `main` still declares version 0.2.10 after the tag, so a PEX built from
  `main` would be mislabeled.

The standing coordination work below is unchanged by this session.

**All four questions of the 2026-08-27 pause are settled** (see *Last Task
And Status*). The next resumable coordination work, in order of leverage:

1. **The ratification pass.** Five agent-proposed items in the
   [V1 scope ledger](v1-scope-ledger.md) await the product owner: `E5`
   conformance suite `in-v1`, `F6`'s destructive-surface split, `F7`'s
   `pycharm build` removal, D-0001 parked `v1-optional`, and the
   *V1 Acceptance* section.
2. **Rebuild the release shape wow-first** from the completed gap verdicts —
   the superseded twelve-week shape's deferrals are gone; sequence the
   unowned `in-v1` rows (supervisor core, contained display, VSCodium
   surface, on-the-side, `F1` bootstrap, `E5`, human-readable onramp) into
   milestones the owner can ratify.
3. **The one live Open Thread**: whether the storage boundary earns a
   `Shared Constraints` registry line.

The functional work itself proceeds outside this workstream, from the
decided-but-unowned rows; the owner picks targets there directly.

The earlier task list follows for history; its four questions are settled and
its ledger task is done.

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

Reviewed at the 2026-08-29/30 rulings sessions, which settled nearly the
whole list: the release thesis (workspace and containment), Java (in as
samples, Eclipse default with IDEA available), the fourth agent Case A
(`v1-optional`), the twelve-week shape (superseded by the maximal-wow
budget), the use-case set (recorded through the union row, the one-to-five
promise, and the issue-tracker positioning), `R-GTM-001` (criteria satisfied,
flag closed), and the commit-ratio question (`WORKFLOW.md` frozen until a
release candidate). Settled threads are removed rather than annotated, per
this section's convention. Earlier review history: rewritten at the
2026-08-19 pauses; originally written at the 2026-08-16 pause. The format
remains the unratified `Open Threads` trial shape.

### Awaiting The Product Owner

1. **Whether the storage boundary earns a `Shared Constraints` line** in the
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
