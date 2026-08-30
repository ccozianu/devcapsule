# Spike: Moving Workstream Mail Off `main`

Written 2026-08-30 by `project-management` at the product owner's direction: a
brief design spike on a communication protocol for intake items, decisions,
and task messages that does not require `main` as the transport, while
keeping the project's standing principle that everything is reflected in the
source tree.

Status: design spike, not a decision. **`WORKFLOW.md` is frozen until a
release candidate** (2026-08-30 ruling), so nothing here changes the protocol
now; this note is input to the *Workflow Improvements At The Release
Candidate* check, or to an explicit earlier unfreeze if the owner rules the
current mail path defective enough to qualify.

## The Problem, Stated Once

Today intake delivery travels the sender's outbox branch and is only visible
to its recipient on `main`. That yields exactly the two bad options the owner
named, plus a third failure already paid for:

1. agents committing directly to `main` for mail — a practice real projects
   forbid, and a standing hole in branch protection;
2. a human pull-request cycle whose only content is flushing somebody's
   outbox — ceremony with no product value; and
3. the recorded 2026-08-17/27 loss: sender-side outbox resets destroyed
   undelivered mail, because the sender owned a buffer whose contents only
   the recipient could confirm received.

Timeliness rides on the same flaw: a message is invisible until a human
merges something, so "when does the workstream get its inbox" has no better
answer than "whenever `main` next moves."

## The Reframe That Unlocks It

The current design conflates two different things: the **durable record**
(which belongs on `main`) and the **wire** (which does not). Postal mail is
not archived in the envelope; it is archived by the recipient, after
receipt. `main` should record *outcomes* — dispositions, decisions, accepted
work — and something else should carry the mail. Everything stays in the
source tree in the sense that matters: in the repository, in Git, versioned,
offline-capable, no external service. It just is not on `main` while in
flight.

## Candidate Designs

### A. Recipient-owned mail branches — recommended

One standing branch per workstream, `mail/<mnemonic>`, holding only that
workstream's unread inbox. The rules:

- **Senders append.** To deliver, fetch `mail/<recipient>`, add one item
  file, push. A non-fast-forward rejection means another sender got there
  first: fetch and retry. No sender ever deletes or rewrites anything.
- **Only the recipient resets.** At session start the recipient fetches its
  own mail branch, copies the items into its `intake/` on its own working
  branch, and only then resets `mail/<mnemonic>` to empty. The 2026-08-17
  failure mode is structurally impossible: the party that empties the buffer
  is the party that has provably received its contents.
- **Everything else is unchanged.** Intake, disposition logs, and the
  exclusive-or invariant work exactly as today; items simply arrive on the
  recipient's branch instead of on `main`, and reach `main` through the
  recipient's own ordinary pull request — mail never needs a PR of its own,
  and no agent ever commits to `main`.
- **The invariant gains one place.** On the union of `main` and the mail
  branches, every item ever sent is in exactly one of: the recipient's mail
  branch (in flight), the recipient's `intake/` (received, undispositioned),
  or its disposition log (resolved). Never two, never none. The pre-commit
  `workflow verify` proposal can check all three.

Timeliness becomes a rule instead of a hope: **fetch your mail branch at
session start**, before selecting work — one cheap fetch, no merge, no
human. A capsule that is offline simply reads what it last fetched, which is
the same behavior the whole workflow already has toward `main`.

Cost: a `WORKFLOW.md` section replacing *The Outbox Branch* (registration
travels the same way — it is mail to `project-management`), a session-start
line, and optional CLI sugar later (`devcapsule workflow mail check|send`)
riding the same surface as the invariant checker. No code is strictly
required to start.

### B. One shared `post-office` branch

Same mechanics, one branch for all mailboxes. Simpler to explain, one place
to look, but every sender contends on one ref, and the recipient-owned reset
becomes muddier (who may reset what). Worth keeping in the drawer if
per-workstream branches ever feel like sprawl; at four workstreams they will
not.

### C. Rejected briefly

- **Git notes** (`refs/notes/*`): the right plumbing shape, but obscure,
  poorly surfaced by hosts, and hostile to review. The mail should be
  ordinary files in ordinary commits.
- **Host-side channels** (issues, PR comments, discussions): off-thesis and
  already answered by the issue-tracker positioning — network, credentials,
  and an attacker-writable surface, for messages the capsule could carry in
  Git itself.
- **Direct agent commits to `main`, mail-only**: the owner's own objection
  stands; once the credential can push to `main` for mail, the restriction
  is a convention, not a boundary. Rejected without needing more argument.

## Why This Is An Adopter Feature, Not Just Our Plumbing

The multi-agent story this product ships — several workstreams, human and
agent sessions handing off through the tree — currently requires either
merge-to-`main` discipline or lost mail. Recipient-owned mail branches give
an adopting team asynchronous agent-to-agent and human-to-agent messaging
with nothing but Git: no tokens, no tracker, no service, working against any
remote including a bare directory on a shared disk. That is the workspace
thesis applied to coordination, and it is cheap enough to demonstrate in the
V1 samples if the ratification lands it.

## Recommendation

Adopt design A at the release-candidate workflow check (or earlier by
explicit unfreeze): recipient-owned `mail/<mnemonic>` branches, sender
append-only, recipient-only reset, session-start fetch, invariant extended
to three places. Retire the outbox with credit: its one-way flow was right;
it merely put the buffer under the wrong owner and the visibility on the
wrong branch.
