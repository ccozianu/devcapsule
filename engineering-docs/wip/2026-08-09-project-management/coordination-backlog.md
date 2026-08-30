# Coordination Backlog

Owned by: `project-management`

Cross-workstream coordination features whose release target is not yet decided.
Items here are deliberately not assigned to V1 until someone weighs their cost
against the release. An item leaves this backlog when a release target is
chosen and an owning workstream accepts it.

## File Locking Protocol

Opened: 2026-08-15

Release target: **undecided (V1 or V2)**

Context: on 2026-08-15 the product owner established that no workstream holds
exclusive editing rights over any file. Exclusivity applies only where a
documented locking protocol exists and is actually used. No such protocol
exists, so today nothing is exclusive.

That is the right default while work is sequential. Under genuine concurrency
it leaves a gap: two workstreams may edit the same file with no mechanism to
coordinate beyond ordinary Git conflict resolution.

A protocol would need to define at least:

- what may be locked, and at what granularity: a file, a directory, or a
  declared area such as a handoff or a requirements register;
- how a lock is taken, recorded, and made visible to another agent that only
  has the repository and no shared runtime;
- how long a lock survives, and how a lock left by an interrupted or abandoned
  session is detected and released without a human arbitrating every case;
- what an agent does when it needs a locked file, including whether it waits,
  proceeds and reconciles later, or escalates; and
- whether locks are advisory or enforced, given that nothing prevents an agent
  from simply editing the file.

Open question to settle before choosing a target: whether ordinary Git conflict
resolution plus clear workstream scoping is sufficient in practice, making a
lock protocol unnecessary complexity. Deciding that it is sufficient is a valid
outcome and should be recorded rather than left implicit.

Related: `WORKFLOW.md` rule 11 currently states a narrower exclusivity for
another workstream's WIP directory and recovery state. Whether that is a
carve-out or a contradiction should be reconciled by `workflow-improvements`
independently of this item, since readers need an answer now.

## Dissolved Stage 7 Items

Opened: 2026-08-27, when the product owner judged `recursive-e2e`'s pending
Stage 7 not consequential enough to gate that workstream's conclusion and
directed its identified items here as decisions to be made, not work already
scheduled. Each leaves this backlog when it gains a release target and an
owner, or a recorded rejection.

### External-Resource Ownership And Reaping

Release target: **undecided**

The Stage 7 implementation half of the convention `workflow-improvements`
retained; closes the
[detached-successor cleanup bug](../../bugs/devcapsule/2026-08-15-detached-successors-not-cleaned-up.md).
The 2026-08-16 readiness assessment ranked this the top at-risk V1 item, but
that ranking predates v0.2.7: the ordinary attached run's exit cleanup is
verified (v026 acceptance, including broker-resource removal), so the
accumulation problem is specific to detached and E2E launches. The remaining
decision is whether that narrower exposure still earns V1 scope, and if so
which workstream implements it. The convention-readiness notice delivered to
`workflow-improvements`' intake on 2026-08-27 is overtaken if this item is
deferred or rejected; that workstream should disposition it against this
entry's outcome.

### Retained-Successor Evidence Disposal

Release target: **undecided; cheap either way**

Two exited successor containers (`b2093d85…` and `482c34f2…` runs) and their
run roots remain on the owner's host under a do-not-delete constraint that
existed for Stage 7's benefit. With Stage 7 dissolved, decide when to release
the constraint and remove them — by their exact GUID-derived names, which is
itself a small live exercise of the cleanup rule.

### Successor Persistence And Stability Proof

Release target: **undecided; likely reject**

The bounded second-inspection stability result was never produced: both
retained successors exited while paused, so it needs a fresh launch. Its value
was recursive-dogfood assurance, not adopter-facing persistence — project
state and home persistence are separately covered. Recording rejection is a
valid outcome.

### Non-Interactive Runs

Release target: **undecided — but the product owner ruled on 2026-08-23 that
this blocks V1**; the entry must not bury that ruling.

Delivered to this workstream's intake on 2026-08-27 (written 2026-08-23,
delayed by the outbox failure). Unattended operation has no owner, no
requirement, and no defined behavior for authorization and acquisition
acknowledgements. The decisions it needs are recorded in the intake item:
support versus explicit refusal in V1, the pre-recorded authorization shape if
supported, whether it becomes a requirement and a ledger row, and which
workstream carries it.

**Mechanism decided 2026-08-29.** The product owner ratified the capsule
supervisor for V1 (ledger row *Capsule Supervisor And Multi-IDE Sessions*):
non-interactive runs are the supervisor with no GUI children, so the
"support versus refusal" question is answered — supported, in V1. Still open
from the list above: the pre-recorded authorization and acquisition
acknowledgement shape, the requirement record, and the owning workstream
(the supervisor core itself has none registered yet).

### Workflow Invariants As Pre-Commit Hooks

Release target: undecided. Owner: none yet, per the 2026-08-29 unowned-rows
ruling; assigned at pickup.

Directed by the product owner on 2026-08-29 while dispositioning the
intake-staleness item. The workflow's mechanical invariants — the intake
exclusive-or, append-only disposition logs, intake naming, the WIP carve-out,
registry agreement — become a `devcapsule workflow verify` check exposed to
adopters as opt-in `pre-commit` local hooks seeded by bootstrap, and to this
repository as a Nox gate session. Design fleshed out in
[the 2026-08-29 note](2026-08-29-workflow-invariants-pre-commit.md). Shares
its delivery path with the initialization-tooling entry below; whichever
workstream picks up one should expect the other.

### Multiple-Stream Initialization Tooling

Release target: undecided. Owner: none yet, per the 2026-08-29 unowned-rows
ruling; assigned at pickup.

Recorded 2026-08-30 at the product owner's direction, dispositioning the
2026-08-16 intake item from `workflow-improvements`. The owner asked that the
reserved `project-management` workstream be "initiated by the tooling on all
devcapsule projects"; the protocol half is done, but the only path that seeds
workflow files today is `devcapsule bootstrap project` running
`docker4pycharm/bootstrap-project.sh`, a script predating the multiple-stream
workflow entirely. The work is product implementation in `devcapsule-src`:
teach the bootstrap to initialize multiple-stream mode, including the reserved
workstream, per `WORKFLOW.md`'s *Initializing Multiple-Stream Mode*. Shares
its delivery path with the pre-commit invariants entry above — the same
bootstrap seeds both.
