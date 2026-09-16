# Merge Strategy And Commit Identity

Recorded 2026-08-17 by the `workflow-improvements` workstream, from evidence in
this repository rather than from documentation.

## Why This Exists

Several rules in `WORKFLOW.md` are true under one merge strategy and false under
another. Two of them shipped wrong and were disproved only by the first branch
to complete a round trip through `main`; a third produced a conflict that looked
like divergence and was not. Each failure traces to the same mechanism, and none
of them is obvious from the surface behaviour of a pull request.

This note explains that mechanism, records the evidence, and states which
strategy the workflow prefers and why. It is written for contributors and agents.
An adopter-facing version is planned; see *Intended Reuse*.

## A Commit's Identity Is A Hash Of Its Metadata, Not Of Its Content

A commit object is a short text blob, and its SHA is the hash of that blob:

```text
tree bb95a3f0c1cc5cee7c06656131ccae39439eb75a
parent c34f647dbd5e0bb179e32acee968fbc8a4731e33
author Costin Cozianu <ccozianu@gmail.com> 1786298276 +0000
committer Costin Cozianu <ccozianu@gmail.com> 1786298276 +0000

Register workflow improvements workstream
```

The `tree` is the content: the entire snapshot of the repository at that commit.
Everything else is metadata. Change one byte of any of it and the SHA changes.

The consequence that matters: **the parent is part of the identity**. A commit is
inseparable from the history it sits on, so the same content on a different base
is necessarily a different commit. This is not an implementation detail that
could have been otherwise; it is what makes a Git history tamper-evident.

## What Rebase Does

Rebase does not move commits. It takes each commit's *diff*, replays it onto a
new base, and writes a new commit object with a new parent and a new committer
timestamp. The author and message are preserved, which is why the result looks
like the same commit in `git log` and is not.

Both halves of one such pair are present in this repository today:

| | `3369539` original | `285962b` replayed |
|---|---|---|
| tree | `bb95a3f0…` | `bb95a3f0…` — identical |
| author and author date | Aug 9 17:57:56 | identical |
| message | "Register workflow improvements workstream" | identical |
| patch-id | `d1d26d7c…` | `d1d26d7c…` — identical |
| **parent** | `c34f647d…` | `384ca92a…` |
| **committer date** | Aug 9 17:57:56 | Aug 13 06:40:29 |
| reachable from `main` | no | yes |

Byte-identical snapshot, byte-identical diff, two different commits. The original
survives only because `recursive-e2e/stage-4` still points at it.

GitHub's **Rebase and merge** performs exactly this replay server-side and then
advances `main` to the new commits. The branch you merged *from* therefore never
becomes an ancestor of what you merged *into*, and two lineages now describe the
same work.

## What Breaks, And Why

Every cheap way Git offers to answer "has this landed?" is built on identity:

- `git merge-base --is-ancestor <branch> origin/main` answers **no** for work
  that is fully integrated;
- `git branch --contains <sha>` answers the same;
- `git rev-list --left-right --count main...branch` counts duplicates as real
  divergence;
- any SHA written into a handoff, decision record, or status file points at a
  commit `main` does not contain; and
- once the branch ref is deleted, the originals become unreachable and are
  eventually collectable. The evidence in this note exists only because the
  branch still exists.

**A live example.** As of this note, `recursive-e2e/stage-4` reports 17 commits
ahead of `main`:

```text
git cherry origin/main origin/recursive-e2e/stage-4
   2 lines beginning '+'   genuinely absent from main
  15 lines beginning '-'   already upstream under different identities
```

Fifteen of the seventeen are ghosts. A reader trusting the count would believe
that branch carries roughly five times the work it actually does.

## The Second-Order Failure: The Conflicting Re-Rebase

Rebase does try to handle this. It computes patch-ids for upstream commits and
drops any commit whose patch already exists there. That is what
`WORKFLOW.md` originally described as rebasing "silently dropping commits that
already landed", and it usually works — on 2026-08-16 it dropped three duplicate
commits from this workstream's branch cleanly.

It fails when patch-ids do not match exactly: when a conflict was resolved during
the server-side rebase, when a commit was amended, or when another branch touched
the same lines in between. The commit is then replayed onto a `main` that already
contains its final effect, and the three-way merge compares an intermediate state
against a finished one. They disagree even though the endpoints agree.

Observed 2026-08-17: rebasing `workflow-improvements/v1` onto the merged `main`
conflicted on `CURRENT-STATUS.md` and `intake/README.md` while the branch held
nothing `main` lacked. Hence the rule that a branch whose own delivery has landed
is hard reset, not rebased.

## Why `git cherry` Is The Reliable Test

`git patch-id` hashes the *diff*, normalizing whitespace and ignoring line
numbers and context position. It knows nothing about parents, so it is unaffected
by replay. `git cherry` runs it over both sides:

```text
git cherry origin/main <branch>
```

`-` means already upstream under some identity; `+` means genuinely absent. This
answer is correct under every merge strategy, which is why *Verifying Shared
Branch State* tells agents to use it instead of ancestry.

The one case it cannot rescue is a squash merge, below.

## The Three Strategies Compared, For This Workflow

**Merge commit.** `main` gains one commit with two parents, and the branch's
commits become reachable from `main` unchanged. Identity is preserved, so
ancestry is a correct test again. Verified on 2026-08-17: after `PR #19`,
`--is-ancestor` answered yes and synchronizing `workflow-improvements/v1` was a
fast-forward, where the same operation had required a hard reset a day earlier.
Three protocol complications disappear rather than needing documentation — the
outbox reset stops requiring a force-push, post-delivery synchronization stops
needing its special case, and "did it land" stops needing a content comparison.
The cost is a non-linear `main`, read with `git log --first-parent`, which
yields one entry per delivery and matches how the registry already thinks.

**Rebase merge.** Linear history, at the cost of everything above. Every
consequence in this note was observed under it.

**Squash merge.** The worst case for this project. N commits collapse into one
new commit whose patch-id matches none of the originals, so even `git cherry`
reports every branch commit as `+` and no mechanical test remains. It also
destroys the individual commit messages, which this project writes as durable
reasoning rather than as change descriptions.

## Recommendation

Prefer merge commits, and — more important than the choice — make the strategy
uniform. Rules whose truth depends on the strategy cannot be relied on in a
repository that varies it per pull request, and a mixed history has neither
strategy's properties reliably. This repository is currently mixed: deliveries
through 2026-08-17 were rebase-merged, and `PR #19` and `PR #20` were merge
commits.

Two placement points, if the recommendation is adopted:

- the choice belongs in the *Coordination Baseline* of root `CURRENT-STATUS.md`
  as a repository fact, not in `WORKFLOW.md`, which must stay strategy-neutral
  for adopters under `R-PRODUCT-004`; and
- one sentence in *The Outbox Branch* — "expect that reset to require a
  force-push" — should be conditioned on the strategy rather than deleted, since
  it stays true for adopters on squash or rebase.

The decision itself is the product owner's and is open; see *Open Threads* in the
[workstream handoff](../../wip/2026-08-09-workflow-improvements/CURRENT-STATUS.md).

## Intended Reuse

An adopter-facing treatment is a backlog item of the `workflow-improvements`
workstream. This note is the engineering source for it and is not itself
user-level documentation: it assumes familiarity with Git internals, cites this
repository's own refs as evidence, and argues a decision that adopters do not
inherit. The user-level version should teach the choice and its consequences
without the forensics.

## Evidence Commands

Every claim here is reproducible from a clone of this repository, subject to the
named refs still existing:

```text
git cat-file commit 3369539
git show -s --format='%T %P %ci' 3369539 285962b
git show 3369539 | git patch-id --stable
git merge-base --is-ancestor 3369539 origin/main
git cherry origin/main origin/recursive-e2e/stage-4
git log --oneline --first-parent origin/main
```
