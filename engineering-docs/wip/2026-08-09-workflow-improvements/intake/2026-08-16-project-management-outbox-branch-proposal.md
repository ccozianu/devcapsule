# Intake: Per-Workstream Outbox Branch

Delivered: 2026-08-16

From: `project-management`, relaying a product-owner proposal made on
2026-08-16.

## What Is Being Handed Over

Each workstream gets a standing `<mnemonic>/outbox` branch that it pushes to
often, so deliveries reach `main` separately from the sender's own integration
schedule and without disturbing its working branch.

## Why It Belongs Here

It is a delivery-protocol design, and it is a candidate answer to this
workstream's already-open next task: reconciling main-first registration with a
repository policy that defaults workstream delivery to pull requests. The two
should be designed together rather than in sequence.

## Why The Question Arose

The *Workstream Intake* section added to `WORKFLOW.md` on 2026-08-16 requires
that an intake item reach `main` promptly and separately, because an item riding
along with the sender's branch stays invisible until that branch merges — which
is the original failure with extra steps. It does not say by what mechanism.
The first delivery under the new rule violated it: three intake items were
committed on `project-management/coordination` rather than delivered.

## Sender's Analysis

Offered as analysis, not as constraints on this workstream's judgment.

**Why it can genuinely be worry-free.** Intake deliveries are new files whose
names are unique by construction. Append-only, touching no shared file, such a
branch cannot conflict on merge — not rarely, but structurally.

**Three rules appear necessary to keep that property true.**

1. The outbox carries only non-conflicting additions: new files with unique
   names and no edits to shared files. Registry rows in root
   `CURRENT-STATUS.md`, `index.md` entries, and `WORKFLOW.md` genuinely conflict
   between workstreams and must stay on the ordinary delivery path. A new bug
   report is an instructive near-miss: the bug file is append-only, but its
   `index.md` entry is not, so it does not qualify.
2. The outbox forks from `main`, never from the work branch. Otherwise
   integrating it silently carries unfinished work onto `main`. This appears to
   be the proposal's one real footgun.
3. After the outbox lands, it is reset to `main`. Otherwise it accumulates
   already-merged commits, which is the duplicate-SHA problem this repository
   has already hit at least twice.

Naming it `<mnemonic>/outbox` requires no rule change, since every non-`main`
branch already belongs to exactly one registered workstream.

**When it earns its cost.** The
[project-management handoff](../../2026-08-09-project-management/CURRENT-STATUS.md)
records that this environment can push branches and unprotected `main`, and
`WORKFLOW.md` already commits workstream registration directly to `main`. While
that remains true, a small direct commit achieves the same result with no new
branch, lifecycle, or reset rule. The outbox becomes clearly worthwhile if
`main` becomes protected, where one standing branch batching deliveries beats a
pull request per item, or if the project decides an agent should rarely hold
`main` write authority, in which case routine delivery never touches it.

## What Accepting Would Mean

A delivery mechanism for intake items stated in `WORKFLOW.md`, consistent with
whatever this workstream decides about protected-main registration, including
the outbox lifecycle if adopted.
