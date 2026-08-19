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
