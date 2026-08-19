# Intake: Registry Rows Have De Facto Owners And No Stated Ones

Delivered: 2026-08-18

From: `project-management`, reporting a merge conflict it caused itself.

## What Is Being Handed Over

Root `CURRENT-STATUS.md` is a table with one row per workstream. The outbox
rules presuppose that a row has an owner. Restriction 11 expressly denies that
any file has one, and its carve-outs do not reach the registry. Nothing states
which is true, so two workstreams can edit the same row in good faith, and on
2026-08-18 two did.

## Why It Belongs Here

Restriction 11, the registry's structure, and what an outbox carries are all
protocol. `project-management` can report the collision and its cost; it should
not decide the ownership rule for a document every workstream routes by.

## Evidence

`PR #28`, merging `project-management/coordination` into `main`, conflicted.
From merge base `a72d0a8`, exactly one file and exactly one line conflicted:
the `recursive-e2e` registry row.

Both sides had independently written the **state** cell to the identical string,
`paused 2026-08-18 after Stage 6 completion; Stage 7 is next`. Git still
reported a conflict, because a markdown table row is one line and the two sides
differed in a *different* cell: `project-management` had widened that
workstream's **goal** cell, by the 2026-08-16 checkpoint's decision, while
`recursive-e2e` had updated its own state through `recursive-e2e/outbox` in
`PR #26`.

Two writers, one row, both acting within the rules as written:

- **Restriction 11** says no workstream holds exclusive editing rights over a
  file, and that exclusivity may not be inferred from a file's subject, its
  directory, or which workstream created it. Its two carve-outs are another
  workstream's WIP handoff directory excluding `intake/`, and uncommitted
  recovery state in another checkout. Root `CURRENT-STATUS.md` is neither. On
  the letter, editing another workstream's row is permitted.
- **The Outbox Branch** lists as outbox cargo "changes to the sender's own row
  in root `CURRENT-STATUS.md`". The phrase "the sender's own row" only makes
  sense if rows have owners — but that restriction is never stated, only
  implied by what an outbox happens to carry.

The control case is in the same conflict. `project-management`'s other registry
change, a release-sequencing entry under *Shared Constraints*, merged cleanly.
That section is territory it actually owns. The conflict fell precisely on the
part it did not.

## A Second Contributing Factor

The registry edit rode `project-management/coordination` for two days rather
than traveling the outbox. Had it been sent on 2026-08-16, it would have reached
`main` before `recursive-e2e` published its pause, and the collision would have
been a small early conflict or none at all.

*The Outbox Branch* already lists registry-row changes as outbox cargo, and
explains why with the strongest argument in the section: a routing fact that
waits for the sender's integration leaves `main` describing a branch that may no
longer exist. Nothing in the checkpoint or session-end procedures reminds a
workstream to send one, so the rule exists and was silently not applied.

## Sender's Analysis

Offered as analysis, not as constraints on this workstream's judgment.

- Restriction 11's own stated rationale appears to settle it. The carve-outs
  exist because each is "a workstream's account of its own state, which another
  workstream cannot restate accurately", and the instruction is to "report what
  you observe about another workstream instead of editing its record". A
  registry row is exactly that kind of account. The carve-out names directories
  and so misses it; the reasoning covers it exactly.
- A candidate rule, if that reading holds: a workstream edits only its own
  registry row, and a change it wants to another's goes to that workstream's
  `intake/`, where the owner applies it through its own outbox. Registration of
  a *new* workstream stays with the opener, as it is today.
- This constrains `project-management` more than anyone, which appears
  consistent with the reserved workstream's own scope: its coordination
  authority is described as "advisory and recorded, not procedural", and it
  explicitly "does not own other workstreams' state". Writing another
  workstream's registry row sits badly with both.
- The mechanical residue is separate and smaller: one row per line means any two
  edits to the same row conflict textually even when they touch different cells
  and agree on everything else. Whether that is worth addressing, and whether a
  wider table is worth its readability cost, is this workstream's call.
- Deciding that rows are not owned, and that ordinary conflict resolution is the
  right answer, is a valid outcome. If so it should be said, because the
  "sender's own row" phrasing currently reads as ownership to someone applying
  the protocol carefully.

## What Accepting Would Mean

A statement of whether registry rows have owners, reconciled with restriction 11
and its carve-outs and with what the outbox carries; and, if they do, a route by
which one workstream gets a change made to another's row.
