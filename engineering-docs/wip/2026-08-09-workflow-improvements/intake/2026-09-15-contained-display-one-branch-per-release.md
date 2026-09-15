# Intake: One Branch Per Release — A Workstream Takes The Release Over

Delivered 2026-09-15 by `contained-display`, recording the product owner's
retrospective direction after the v0.2.12 release, refined in conversation
with the agent. The owner wants the workflow definition to change; the
concrete runbook steps in the release guide (project-management's) follow
from whatever rule you set.

## The Problem, With Evidence

v0.2.12 was driven from `contained-display` with **two live branches**: the
workstream's `contained-display/display-transport` and `release-0.2.12`,
cut from the workstream branch before that branch had merged to main.
Every release-time fix then had to exist twice — committed on the
workstream branch, cherry-picked to the release branch (or the other way) —
and the new candidate gate had to prove the two copies were the same patch
by `git patch-id`. The promotion record needed the `reviewed` integration
method with fourteen mapped commits instead of plain ancestry. Six
candidates were cut; two of them (a baseline version bump, an e2e race)
were pure release-mechanics churn. The checkout switched branches for
every fix and the owner found the juggling confusing. It did not hurt the
release; it will hurt the next one more.

## The Rule The Owner Proposes

A workstream can **take a release over**. For the duration:

1. **Cut from main, not from the workstream branch.** The workstream
   merges its branch to main first; that branch is then closed for
   modifications. `release-X.Y.Z` starts at the merge commit on main, and
   its first commit is the distribution-version baseline bump (guide rule
   of 2026-09-13).
2. **The release branch is the workstream's selection.** The registry row
   names it as the branch association; the workstream's handoff is edited
   there and reaches main with the merges below; the checkout sits on one
   branch from cut to final.
3. **Integrate by merging the release branch into main, never by
   cherry-picking.** Before each candidate tag, the release branch merges
   to main by pull request. The candidate gate (mainline integration or a
   documented exception; `release-protocol.py`) then passes by plain
   ancestry, and the final promotion record uses the `ancestry` method.
   Other workstreams keep merging to main in between; the release branch
   never takes their work (the "do not rebase tested release source" rule
   is unchanged).
4. **Closed means closed.** While the release is open, work on that
   workstream's subject lands only as release fixes on the release branch.
   Unrelated workstreams are unaffected.
5. **Afterwards** the workstream resumes on a fresh branch from main under
   its prefix, or concludes. The release branch remains a durable release
   anchor, not a workstream branch, exactly as the 2026-09-09 ruling had it.
6. **Who drives.** The workstream whose deliverable is the release's
   headline. When that is unclear, or for a maintenance release of an old
   version (whose branch cannot merge to main — the gate's documented
   exception case), the product owner drives from `project-management`.

## What It Touches In `WORKFLOW.md`

*Checkouts, Branches, And Workstreams* (a release branch as a workstream's
selection for a bounded period, recorded in the registry); *Beginning A
Workstream* / pausing and resuming (resume on a new branch after a
release); the 2026-09-09 release-refs ruling you already hold; and the
outbox rule that records travel verbatim (during a release the handoff
travels with release-branch merges instead).

## What Accepting Would Mean

Writing the rule into the workflow when its freeze allows, and telling
`project-management` what the runbook must say (cut point, baseline bump,
merge-then-tag, ancestry record, resume). The owner intends to continue
this design in your workstream before the next release is prepared.
