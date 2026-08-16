# V1 Readiness Assessment: 2026-08-16

Recorded by: `project-management`

This assessment answers two questions the product owner asked on 2026-08-16:

1. which current shortcomings are **not** on the path to be solved by V1; and
2. of the shortcomings that **are** documented, which must be pinned to V1 now
   so that they are not quietly deferred later.

The second question exists because backlogged items drop out of releases even
when nobody decides to drop them. This file records the items whose current
placement makes that outcome likely.

Sources read for this assessment: root `CURRENT-STATUS.md`, all four workstream
handoffs, the
[V1 gap review](../../design-notes/devcapsule/2026-08-06-v1-gap-review.md), the
[V1 test backlog](../../implementation-notes/devcapsule/2026-08-07-v1-test-backlog.md),
the [portfolio checkpoint](2026-08-15-portfolio-checkpoint.md), the
[coordination backlog](coordination-backlog.md), the
[cleanup bug](../../bugs/devcapsule/2026-08-15-detached-successors-not-cleaned-up.md),
the [2026-08-16 session record](../../session-records/devcapsule/2026-08-16-inspector-hardening-samples-and-workflow-bootstrap.md),
and the repository's actual Git state.

This is an assessment, not a decision record. Items become commitments when the
product owner assigns them a release target and an owning workstream.

## Part 1: Shortcomings Not On The Path To V1

These are not backlogged, deferred, or rejected. They are unowned.

### 1. Nothing Tracks V1; The Gap Review Is A Snapshot, Not A Plan

The gap review defines Milestones 1 through 4 across gaps F1–F8 and E1–E8. The
strings `Milestone 2`, `Milestone 3`, and `Milestone 4` appear in no other file
in the repository. `F1` appears twice, in the milestone-1 plan, as future work.

The registry holds four workstreams and none of them is a V1 milestone.
Milestone 1 corresponds roughly to `recursive-e2e`, which is paused. Milestones
2, 3, and 4 have no owner, no branch, no handoff, and no dates.

Consequence: the question "how far is V1, what remains, and who is doing it"
cannot be answered from any single document, and reconstructing it from six
documents shows that most of V1 is unowned.

The gap review has also never been amended. `sample-projects` delivered
container-aware launching and the `postgresql-client` component, which bear on
E2, F5, and F7, and the gap list still reads as though none of it happened. A
snapshot that nothing updates stops being a plan on the day work diverges from
it.

### 2. Cross-Workstream Handoffs Have No Delivery Mechanism

The 2026-08-15 checkpoint hands four items to `workflow-improvements`. That
workstream's handoff was last modified 2026-08-09; its next resumable task is
the registration procedure; its backlog holds one unrelated item. The four
items are not in it. The receiving workstream does not know it received
anything, while the registry reports its intake as ready.

This is structural rather than an oversight. `WORKFLOW.md` rule 11 keeps a
carve-out preventing one workstream from editing another's handoff, so a
cross-workstream handoff can be announced in a checkpoint but never delivered
into the document its recipient actually reads at session start. Both documents
are individually correct, which is why the gap is invisible.

Any V1 scope decision this workstream makes will be transmitted the same way and
will fail the same way unless the mechanism is fixed.

### 3. No Gate Protects The Process Artifacts

`AGENTS.md` and `WORKFLOW.md` require that `index.md` is updated in the same
change as any permanent document, that registry rows link to real handoffs,
that requirement identifiers stay consistent, and that links resolve. No
automated check covers any of it.

258 tests guard the Python distribution. Nothing guards durable project memory,
which is the product this repository exists to demonstrate. Every invariant
rests on an agent recalling 1,072 lines of `WORKFLOW.md` plus 114 lines of
`AGENTS.md`.

The registry is stale as this is written. Root `CURRENT-STATUS.md` describes
`recursive-e2e` as "active; Stage 4 ready to begin"; its handoff reports Stages
0 through 5 complete with Stage 6 substantially done; the portfolio checkpoint
reports it paused. Three documents, three answers, and no mechanism that would
ever surface the disagreement.

### 4. Merged-Value Delivery Pauses Silently When A Workstream Pauses

Commits `c26d877` (Stage 6 inspector, roughly 1,600 lines including the mount
set-equality check that closed a security blind spot) and `c24b442` are on
`recursive-e2e/stage-4`, published to the remote, and are the only commits in
the repository not present on `origin/main` by content. The workstream is
paused by product-owner decision, so nothing is scheduled to integrate them.
Local `main` is 13 commits behind `origin/main`.

The session record files this as an unresolved question, which is not an owned
task. No rule states what happens to a paused workstream's unintegrated value,
and the consequence here is that the best code of the last session is the code
most at risk.

### 5. V1 Has No Acceptance Definition

Milestone 4 closes when candidates are "ready for the V1 release decision".
Against what criteria is unstated.

- Thirteen open bugs are indexed with no triage against V1. Nobody has recorded
  which ones block the release.
- Requirement records carry `proposed`, `accepted`, `implemented`, `validated`,
  `deferred`, and `rejected` statuses, but nothing reports the current
  distribution or names what remains unvalidated.
- The gap review's five "Functional Scope Decisions Still Required" — CUDA
  support, the D-0001 catalog freshness contract, the starter catalog contents,
  which transitional commands survive, and the minimum state-management surface
  — are ten days old, undated, and unassigned, and they gate Milestones 2 and 3.

V1 can therefore neither be declared nor refused on evidence.

### 6. User-Facing Documentation Is A Rounding Error With No Owner

`docs/` contains a map, four product and announcement drafts, and one
historical Docker4PyCharm guide. There is no installation guide, no getting
started, no `devcapsule project run` reference, and no troubleshooting.

Its only appearances in V1 scope are a sub-bullet of F8 and a bullet inside the
test backlog. For a release intended to be announced publicly, this is the
artifact that decides adoption, and it is a footnote inside two other items.

Related: `R-GTM-001` carries `status: implemented` on the strength of an
announcement draft written before the product's current shape. Nothing flags
that it must be rewritten against what V1 actually ships.

### 7. Workstream Goals No Longer Describe What Workstreams Do

The portfolio checkpoint records `sample-projects` owning core launcher work as
a naming question rather than a delivery risk. This assessment disagrees on one
point: the risk is not the label. It is that product work lands with no
milestone home, so nothing updates the V1 gap list when a gap closes, and the
project loses the ability to state what is done.

Two workstreams have already drifted: `sample-projects` into core product work,
and `project-management` into publishing `WORKFLOW.md` changes under a
documented bootstrap exception.

### 8. The Cost Of Following The Protocol Is Unmeasured And Unowned

An agent has already deviated from the documented procedure, and the correct
diagnosis in the session record is that the deviation was unauditable rather
than that it was wrong. Nobody owns the question of whether the protocol is
becoming cheaper or more expensive to follow. There is no short session-start
path and no supporting tooling, in a project whose product is agent-ready
development environments.

Deferring workflow tooling past V1 is defensible. Leaving the deferral unstated
is not.

## Part 2: Documented Items To Pin To V1 Now

Ranked by drop risk multiplied by the cost of dropping, not by size.

### 1. External-Resource Ownership And Reaping

Closes the [detached-container cleanup bug](../../bugs/devcapsule/2026-08-15-detached-successors-not-cleaned-up.md).

This is a user-visible broken promise. Developers are told that closing the IDE
leaves nothing behind; the detached path silently accumulates `Exited (0)`
containers holding image references, names, and writable layers.

It currently lives in four places: the bug file, checkpoint Decision 3,
the test backlog under *Owned Workspace And Manifest*, and Stage 7 of a paused
workstream. Four homes is the signature of an item that ships in the following
release. It needs one owner and one milestone slot.

### 2. The `devcapsule project run` Interface Audit And Documentation

The largest and most adopter-facing item in the test backlog. It contains this
obligation: correct any option that can grant Docker, network, sudo,
filesystem, secret, or other host access beyond the resolved checkout
authorization, and ensure `--force` never becomes an authorization bypass.

That is a security audit of the product's primary command, filed inside a
document titled a test backlog whose closure rule is that a focused automated
test passes. Nothing reading that title will prioritize it. It should be lifted
out and named a V1 blocker in its own right, together with the user
documentation it requires.

### 3. The Authorization-Negative Launch Proof

Transferred out of recursive-dogfood Stage 5 when the product owner accepted
that stage on 2026-08-12.

Transfer-on-closure is the highest-risk deferral pattern available: the sentence
that records completion also records the omission, and completion is what is
remembered. This particular obligation proves the product's central claim, that
absence of authorization yields no host Docker socket, no host networking, and
no development sudo. Without it, `R-PRODUCT-002`, `R-SCOPE-001`, and
`R-DOCKER-001` are asserted at V1 rather than demonstrated.

It is also cheap: an isolated resolution plus a small non-GUI probe against the
resulting plan.

### 4. F1: Clean Checkout To Ready Development Environment

The largest adopter-visible functional gap. Its source bug notes are dated
2026-08-03 and it is folded into Milestone 2, which has no workstream.

Everything adjacent to it has moved for two weeks while it has not moved at all.
An item with no owner for two weeks, while neighbouring work sprints, is already
deferred in practice whatever the backlog says. If V1 ships without it, the
first action of every adopter is to hand-build a virtual environment.

### 5. The Four Functional Scope Decisions

These are decisions rather than work, they cost hours rather than weeks, and
each one shrinks a milestone. Deciding that CUDA is experimental and that the
transitional `pycharm build` command leaves the supported V1 surface removes
real validation load and closes the multiline-quoting bug as obsolete.

What should be scheduled is a decision date, not the work.

### 6. The Silent Empty-Directory Failure Mode

Container-aware launching fixed path translation. The `sample-projects` handoff
records that the silent empty-directory failure is worth addressing regardless
of how the GUI verification is routed.

Docker inventing empty bind sources is a data-shaped silent failure, the worst
class available, and the session record shows the same class recurring a second
time within one session through container-local tmpfs staging. It should be made
structurally loud once, in V1.

### 7. Submodule Pointer Publication Ordering

From the test backlog's *Mainline Change Propagation* item. Small, but `main`
can currently advertise a submodule pointer that no clone resolves, which breaks
the first command an adopter runs. Cheap to specify, cheap to check, and
embarrassing to ship.

## The Pattern Worth Keeping

Every at-risk item in Part 2 is recorded as a note attached to something else: a
transferred obligation, a bullet inside a backlog, a bug that should be closed
by another slice, or a checkpoint entry handed to a workstream that never
received it.

Items with their own row in a tracked list get done. Items that are a sentence
inside another document do not. That observation is the argument for the V1
scope ledger proposed as this workstream's next task.
