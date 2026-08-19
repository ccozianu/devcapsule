---
date: 2026-08-19
capture-mode: detailed
requested-by: user
scope: project-management resume, outbox correction, and the framing of the individual real projects
session-span: 2026-08-19
related:
  - CURRENT-STATUS.md
  - AGENTS.md
  - WORKFLOW.md
  - engineering-docs/wip/2026-08-09-project-management/CURRENT-STATUS.md
  - engineering-docs/wip/2026-08-09-project-management/v1-scope-ledger.md
  - engineering-docs/wip/2026-08-09-project-management/2026-08-19-display-transport-options.md
  - engineering-docs/wip/2026-08-09-project-management/2026-08-16-v1-readiness-assessment.md
  - engineering-docs/wip/2026-08-14-sample-projects/CURRENT-STATUS.md
  - engineering-docs/bugs/devcapsule/2026-08-16-x11-passthrough-grants-full-session-credential.md
---

# Session Record: Resuming Project Management And Framing The Individual Projects

This is a detailed, sanitized, agent-authored reconstruction. It is not a
verbatim transcript. Commit revisions and branch names are retained because
resuming depends on them; no credentials or secret values appear in the source
material.

This was the second `project-management` session of 2026-08-19. The first was
interrupted for travel and paused the workstream. This one resumed it, spent
its effort on verification and correction rather than on new decisions, and
ended inside a question the product owner asked to persist rather than answer.

## Why This Session Mattered

Three things.

First, the handoff was wrong, and wrong in the project's favour. It opened with
"before anything else: the outbox needs a pull request" and named five
deliveries stranded off `main`. Both pull requests had merged during the pause.
An agent that trusted the handoff would have spent the session re-solving a
solved problem, and would have re-reported a communication failure that had
already been repaired. This is the third consecutive session in which
re-verifying external state on resume changed what the session did — the rule in
`AGENTS.md` earns its place.

Second, the outbox was, for the first time, used the way its own rule describes:
reset from current `main`, carrying exactly one item. Every previous send on
this workstream appended to a branch that had accumulated undelivered mail,
which is the gap already reported to `workflow-improvements` in the
2026-08-18 outbox-is-a-mechanism item.

Third, the individual real projects — thread 7, and the topic the product owner
chose for the session — turned out to have no recorded substance anywhere in the
repository. The session produced a frame and one coordination question for them
instead of a plan, because the material to plan with does not exist outside the
product owner's head.

## Chronology And Decisions

### 1. Protocol Reading

Followed `AGENTS.md` in order: `README.md`, the `workflow-type` field in
`.devcapsule/devcapsule.toml` (`multiple-streams`), the registry, the selected
workstream handoff, and its `intake/`.

The checkout was clean on `project-management/coordination`, which is the
persistent workstream selection, so no selection question arose.

The registry copy on local `main` was stale. `origin/main` was nine commits
ahead and authoritative, and it already carried a fifth registry row —
`contained-display`, opened 2026-08-19 — that the local copy did not show. The
rule that the registry is read from the locally accepted mainline ref, taking
fetched remote-tracking `main` when it is newer, is what surfaced this.

### 2. External-State Re-Verification

What the handoff claimed, and what was found:

| Claim at the pause | Found on resume |
|---|---|
| Nothing stashed, nothing dirty, everything pushed | Held exactly |
| `project-management/outbox` at `afb893f`, undelivered | `PR #30` merged the branch at `4b46db5`; `afb893f` alone had not travelled |
| Five deliveries invisible to every recipient | All five present in recipients' `intake/` on `origin/main` |
| `contained-display` "not yet real to anyone but this branch" | Registered on `main`, row present, owner assigned |
| Branch at `5f5ce8a` and later, unmerged | `PR #31` merged the branch at `6a690c1`; four later commits unmerged |
| No `gh` CLI, no GitHub token | Still true; re-verified |
| `recursive-e2e` item in both `intake/` and its disposition log | Still true on `main`; still unreported to its owner |

The two merges were `PR #30` at `5f3341d` and `PR #31` at `21d2503`, both
opened and merged by the product owner while the pair was paused.

### 3. Synchronization

Local `main` was fast-forwarded to `21d2503`. The workstream branch was rebased
onto it; the rebase dropped nothing and replayed the four commits written after
the state `PR #31` merged.

The branch is published, so the rebase required a force-push. `WORKFLOW.md`
permits that only when the branch is known to be unshared, and prefers merging
`main` in otherwise. This branch is worked by one pair in one checkout, so the
rebase was kept and pushed with `--force-with-lease`. Merging would also have
been correct here, since the repository's merge strategy preserves commit
identity; the rebase was chosen for a linear branch history, not out of
necessity.

### 4. The Outbox Correction

`afb893f` — the amendment separating the ratified storage boundary from the
argument around it — was written after the branch state that `PR #30` merged,
so it was still owed. It also sat on a stale base, three commits behind.

Rather than rebasing the old outbox forward, the branch was reset to current
`main` and the single item re-committed on top, at `b1f7273`. This is what the
outbox rule asks for: a branch reset from `main` carrying only what is being
sent. It was safe to do here precisely because the earlier items had already
landed — the reason resetting was refused on 2026-08-19 in the first session
was that it would have destroyed undelivered mail, and that condition no longer
held.

The resend awaits a pull request. This environment still cannot open one.

### 5. Correcting The Handoff

Committed at `758a26f`. It records the two merges, the resend, the
synchronization, and demotes the outbox from a blocker to a follow-up that
gates nothing, since the amendment refines an already-delivered item.

### 6. Choosing The Session's Work

Four live options were offered, with the planned next step first:

1. Settle the release thesis and continue the V1 ledger — the handoff's planned
   next step. Agent recommendation: the containment thesis, on the argument that
   it is where the project is ahead of the field rather than behind it.
2. Write up the three use cases (thread 5), small and overdue, and depended on
   by both 2026-08-19 notes.
3. Disposition the seven intake items (thread 8).
4. Discuss the individual projects (thread 7).

The product owner chose the individual projects.

### 7. The Individual Projects

Searched the checkpoints, the session records, the sample-projects handoff, and
the whole of `engineering-docs/`. **Nothing project-specific is recorded
anywhere.** The only trace is the general judgment carried in the handoff: v026
is good enough to start real projects on; the X11 exposure is open; real
projects will probably reopen the V1 rulings on service dependencies and port
allocation.

The frame put to the product owner had three parts.

**What is known to be open, and how a real project meets it.**

- The X11 passthrough hands each capsule the developer's *trusted* host cookie:
  every keystroke in any window, any window's contents, XTEST injection, and the
  shared clipboard. The launcher refuses to start without `DISPLAY`, so GUI use
  cannot avoid it. `contained-display` owns the fix and it is sequenced to v027.
  Real projects worsen exactly the dimension that matters, because the display
  note already establishes that agent-driven work runs for hours: more capsules,
  more hours, same host session.
- Service dependencies. `fastapi-webapp` needed real PostgreSQL and got it by
  hand. "Minimum state-management surface" and "starter catalog contents" are
  two of the five functional scope decisions the gap review left open, undated
  and unassigned. A project with a database, a queue, or a second service forces
  them.
- Port allocation, already contended by the contained-display change and
  contended again by any project running a dev server.

**One coordination question, raised deliberately before any project starts.**
If each individual project is its own repository with its own `.devcapsule/`
rather than a workstream here, then findings have no route home. A gap found
while building `fastapi-webapp` reached `project-management` because that work
lives in this repository and has an outbox into it. A separate project has
neither, so "I hit a DevCapsule bug in my real project" becomes chat that dies
with the session — the precise failure this workstream has now recorded three
times.

**What would be captured per project**, if named: name and repository; what it
is and roughly how big; declared capabilities (IDE, agents, Docker, network,
GPU); services needed beyond the checkout; whether it is GUI-driven, which
decides whether the X11 exposure applies today; and what it is expected to prove
or stress about DevCapsule.

The product owner did not name the projects in this session. He asked for the
conversation to be persisted and made the handoff instead, which is why this
record exists and why the question is carried forward unanswered.

## Implementation And Documentation Changes

No product code was touched. This was a coordination session.

- `758a26f` — handoff correction: verified resume state, the outbox resend, and
  the synchronization record.
- `b1f7273` on `project-management/outbox` — the ratified-boundary amendment,
  resent from a branch reset to current `main`, one item.
- Local `main` fast-forwarded to `21d2503`;
  `project-management/coordination` rebased onto it and force-pushed with a
  lease.
- This session record, and its `index.md` entry.

## Validation And External-State Evidence

- `gh` is absent from `PATH`; neither `GH_TOKEN` nor `GITHUB_TOKEN` is set.
  Pull requests remain a product-owner action. Verified 2026-08-19.
- `origin/main` at `21d2503` carries all five prior deliveries in the
  recipients' `intake/` directories.
- `project-management` intake is unchanged at seven items plus its `README.md`,
  identical on `main` and locally, and still undispositioned. This workstream
  has no `intake-dispositions.md` yet, because it has dispositioned nothing.
- On `origin/main`, `recursive-e2e` still holds
  `2026-08-17-workflow-improvements-external-resource-reaping.md` in both
  `intake/` and line 15 of its disposition log. Confirmed, still unreported.
- Local and remote agree on both `project-management` branches at the end of
  the session.

## Rejected Or Deferred Alternatives

- **Merging `main` into the branch instead of rebasing.** Legitimate under
  `WORKFLOW.md` and it would have avoided rewriting published history. Rejected
  because the branch is unshared and a linear history is easier to read; the
  choice is recorded here because it is a preference, not a rule.
- **Rebasing the old outbox forward instead of resetting it.** Would have
  carried a stale base and repeated the append pattern already reported as a
  gap.
- **Treating the outbox resend as a blocker.** Rejected: it refines an item
  already on `main`, so nothing downstream waits on it.
- **Answering the individual-projects question with a proposal.** Not attempted.
  The projects are the product owner's to name, and inventing candidates would
  have put agent-authored fiction into project memory.

## Unresolved Questions And Next Work

The resume point is the unanswered half of the individual-projects discussion:
which projects, and whether they are dogfood instruments that owe findings back
to this repository or simply the product owner's work that happens to run in a
capsule. Everything else in the frame above is already recorded.

Behind it, unchanged: the release thesis still blocks roughly half the
V1 ledger, the three use cases are still unwritten, and the seven intake items
are still undispositioned.

## Canonical Artifacts Carrying The Resulting Truth

- [Project-management handoff](../../wip/2026-08-09-project-management/CURRENT-STATUS.md)
  — state, next task, and open threads.
- [V1 scope ledger](../../wip/2026-08-09-project-management/v1-scope-ledger.md)
  — six decided rows and the rows still to be written.
- [X11 passthrough bug](../../bugs/devcapsule/2026-08-16-x11-passthrough-grants-full-session-credential.md)
  — the exposure real projects inherit today.
- [Display transport options](../../wip/2026-08-09-project-management/2026-08-19-display-transport-options.md)
  — the transport choice and the hours-long-session argument.
- [V1 readiness assessment](../../wip/2026-08-09-project-management/2026-08-16-v1-readiness-assessment.md)
  — the five open functional scope decisions.
