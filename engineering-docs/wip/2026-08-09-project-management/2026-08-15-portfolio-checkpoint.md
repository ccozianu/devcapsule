# Portfolio Checkpoint: 2026-08-15

Recorded by: `project-management`

This is the first portfolio checkpoint. It exists because several coordination
decisions became due at once, and because a week of real use produced concrete
workflow findings that no single workstream owns.

Detailed implementation state stays in each workstream's handoff. This file
records only what needed deciding across them.

## Portfolio State

| Workstream | State | Note |
|---|---|---|
| `recursive-e2e` | paused by product-owner decision | Stage 6 substantially complete; failure-path coverage outstanding. Its handoff still describes a successor as running that has since exited. |
| `sample-projects` | active | First sample complete and verified end to end. Now also owns core-launcher work by explicit decision, see below. |
| `workflow-improvements` | active; never started | Intake is now ready; see the handoff list below. |
| `project-management` | active; permanent | This checkpoint. |

## Decision 1: Sample Projects Owns Its Enabling Product Work

The `sample-projects` workstream was registered to provide sample projects. It
has since delivered the `postgresql-client` component and container-aware
launching, both core product changes, because building and then verifying a
sample exposed the need for each.

The product owner accepted that scope and the work is integrated on `main`. The
workstream remains active.

Consequence for coordination: the registered goal in root `CURRENT-STATUS.md`
describes samples only, so the registry currently understates where launcher
changes live. Either the goal is widened or future enabling work is registered
separately. This is recorded rather than resolved, because it is a naming
question, not a delivery risk.

## Decision 2: File Ownership Is Not Exclusive

Effective 2026-08-15, no workstream holds exclusive editing rights over any
file. A workstream may edit any file its task genuinely requires.

The single exception is a documented locking protocol, which does not exist
yet. Exclusivity applies only when such a protocol exists *and* is actually
used for the file in question. Until then, no implicit ownership may be
inferred from a file's subject matter, its directory, or which workstream
created it.

This is a repository-wide coordination fact and is reflected in root
`CURRENT-STATUS.md`.

Reconciled the same day. `WORKFLOW.md` rule 11 previously stated that one
workstream does not edit another workstream's WIP directory or commit another
worktree's recovery state, which read as a narrower ownership claim. The
product owner kept that as a deliberate carve-out rather than a contradiction:
both are a workstream's account of its own state, which another workstream
cannot restate accurately. Rule 11 now says exactly that, and directs an agent
to report what it observes about another workstream instead of editing that
workstream's record.

The locking protocol itself is backlogged with an undecided release target; see
[coordination backlog](coordination-backlog.md).

## Decision 3: Concurrency Readiness Is A Real Gap

All work so far has been sequential task-switching inside one repository,
environment, and Docker daemon. That has masked failures that genuine
concurrency would expose immediately.

The workflow protocol governs Git state well and external state not at all.
`WORKFLOW.md` and `AGENTS.md` contain no guidance on containers, images, host
ports, or shared configuration roots, yet every concurrency hazard encountered
this week was outside Git.

### Evidence From This Week

- A fixed container name, `devcapsule-sample-todo-db`, is hard-coded in the
  sample's compose file. Two concurrent sample workstreams collide at once.
- A fixed host port already collided with an unrelated PostgreSQL on the
  development host. The failure is real today, sequentially.
- Isolating a verification run required hand-rolled `HOME` and `XDG_*` roots.
  No convention says to do this, or where.
- An image tag was reused because it happened to be unpublished. Two agents
  building bases would race on that tag.
- The shared daemon has no ownership model outside the recursive E2E's own
  `devcapsule.e2e.*` labels, which live in one workstream's code rather than in
  the protocol.

### The Cleanup Bug Is A Concurrency Bug

[Detached containers that exit and are never cleaned up](../../bugs/devcapsule/2026-08-15-detached-successors-not-cleaned-up.md)
is survivable while one agent works sequentially and remembers what it left
behind. With several agents, no one can tell which containers belong to whom,
and the existing rule against selecting cleanup targets by name or prefix makes
conservative inaction the only safe response. The pile then grows without
bound. Fixing ownership fixes both problems.

## Handoff To `workflow-improvements`

Four pieces, all derived from observed failures rather than speculation.

**Bootstrap exception, decided 2026-08-15.** Items 1 and 2, plus the rule 11
reconciliation, were written directly into `WORKFLOW.md` from this workstream
rather than waiting for `workflow-improvements` to start. Starting that
workstream cleanly requires the very procedures those items document:
registering on `main`, forking from the registration commit, resolving a stale
branch, and confirming a merge landed. Publishing the minimal set first removes
the circularity. Items 3 and 4 remain for `workflow-improvements`, which can
now begin under documented procedures.

1. **Delivered 2026-08-15.** Verification-first Git procedures: the patch-id check
   (`git cherry origin/main <branch>`) as the sanctioned way to prove commits
   are already upstream; bound when an agent may resolve divergence without
   asking; require reporting when it does. Extend the rule beyond `main` to any
   stale workstream branch.
2. **Delivered 2026-08-15.** A correct merge-landed check. `git merge-base --is-ancestor` answers
   "no" for a squashed or rebased merge whose content is fully upstream. An
   agent trusting it concludes the merge failed and redoes integrated work.
   This is a correctness trap, not a clarity gap, and should be documented with
   the check that does work.
3. **A worktree procedure.** `WORKFLOW.md` calls worktrees optional
   implementation tools and references them throughout without ever saying how
   to create, select, or dispose of one. They are the only mechanism for actual
   concurrency and need a procedure.
4. **External-resource ownership and reaping.** Every container, image tag,
   volume, host port, and state root should carry or derive a workstream
   identity, with names derived rather than fixed, plus one way to enumerate
   what is held and for whom. This closes the cleanup bug as a side effect.

Priority among these is `workflow-improvements`' call. Item 2 is the only one
that can silently cause wrong work.

## Known Stale State

- The `recursive-e2e` handoff describes a successor container as running; it
  exited on 2026-08-14. That workstream is paused, so this checkpoint records
  the fact rather than editing another workstream's handoff mid-pause.
- This workstream's own handoff described the execution focus as recursive E2E
  Stage 4 until this checkpoint corrected it.

## Next Editing Checkout

`project-management/coordination` remains the selected checkout for
coordination work. Implementing the four handoff items belongs on
`workflow-improvements/intake`, forked from current `main`.
