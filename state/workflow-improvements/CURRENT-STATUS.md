# Workstream Current Status: Workflow Improvements

Mnemonic: `workflow-improvements`

Start date: 2026-08-09

State: active; published live on the coordination branch; every 2026-09-19

Definition read: WORKFLOW.md@60772d54f11b, WORKFLOW-LOCAL.md@ed70f3147563
round merged. Resumed 2026-09-16 by the product owner at the release-candidate
check the 2026-08-30 freeze scheduled: v0.2.11 and v0.2.12 have shipped. The
owner chose the release-related intake first and, on 2026-09-18, the reserved
`maintenance` workstream with the bug vocabulary, then the `ws-` branch
vocabulary and the workflow declaration, granting the freeze exception each
needed. Eight intake items remain undispositioned; see *Next Resumable Task*.

Integration target: `main`

Delivery method: pull request

Branch association: `ws-workflow-improvements/v1`

Requirements: `R-PRODUCT-003`, `R-PRODUCT-004`, `R-PRODUCT-005`,
`R-PRODUCT-006`

## Goal

Improve the multiple-stream human/agent workflow from concrete problems,
ambiguities, and avoidable mechanical friction found while dogfooding it during
the recursive E2E cycle. Keep each correction narrow and evidence-based, and
conclude this workstream when that dogfood cycle's accepted findings have been
fixed, explicitly deferred, or rejected.

## Branch Association

`ws-workflow-improvements/v1`, forked from `main` and kept level with it by
rebasing; nothing unique remains on it after each merge. No outbox: records
travel this branch and are published live. The branch's earlier names and
the outbox's history are in the
[record](2026-09-21-record-tasks-and-decisions-2026-08-16-to-2026-09-21.md).

## Current State

- Every round through 2026-09-19 is merged: the release rules and vocabulary,
  the reserved `maintenance` workstream and bug frontmatter, the `ws-` branch
  form, the declaration and version, the local workflow file, the glossary,
  mail on the coordination branch, and published state with the outbox
  retired. The tool `devcapsule workflow mail|publish|list` is on `main`.
- This workstream's intake is empty for the first time since 2026-08-16, and
  its mailbox is empty. The last three items were decided on 2026-09-21: the
  component's shape acknowledged and folded into the review, the Stage 7
  convention item forwarded, and the review acknowledged as *What Adopters
  Inherit*.
- On the working branch, unmerged: the records of the 2026-09-21 decisions,
  *The Open-Work Directory* rule, the design discussion on the workflow's
  open issues and size, and this status file's own shedding into a record.
- Only this workstream has published state; the other eight rows await their
  owners' first publish. Two messages of ours wait in `project-management`'s
  and `user-docs`' mailboxes.

## Last Task And Status

Last task: the patch-handoff rule, from `project-management`'s 2026-09-22
item relaying the owner's proposal. A bounded change found to belong to
another workstream travels to it as a diff in an ordinary intake item, with
base revision, paths, new files, reason, and validation status; the sender
verifies delivery, reverts only what the patch represents, and records the
handoff; the recipient owns review, application, and integration; a patch is
a proposal, not acceptance. Written under *Publishing Before Integration* in
both definition copies with short forms in both agent files, decided in one
commit, and **held on this branch unmerged at the owner's direction so the
0.2.14 scope stays as cut**.

Before that: `brief` and claims, backlog items 4 and 5, plus when each
workstream last published. `workflow claim "<slice>"` writes who, branch,
slice, and a twelve-hour expiry to `state/<name>/claim`; `status` shows live
and expired claims and the publish age; `claim --release`, pausing, and
retiring remove it. `workflow brief` prints the selected workstream's row
and next task, who is working on what, waiting mail, the *Changes* titles
not yet read since the stamp, and the synchronization facts with a suggested
verdict. *Resuming* ends with a claim, *Pausing* with its release; both
agent files start the session with the brief. Tests cover claim, expiry,
release, and the brief before and after a definition change on `main`.

Before that: the session-start synchronization judgment, and the facts that
feed it. The owner's rule of 2026-09-21: tooling supplies facts, the agent
proposes whether to synchronize with `main` and why, the human decides only
when it matters, and a changed definition or local workflow file is a must.
Done: *Resuming* step 2 and *Staying Current With `main`* in both definition
copies and both agent files; `publish` stamps a `Definition read:` line with
the definition files' content ids; `list` shows commits behind `main` and
whether the definition changed since that stamp; `mail send` takes a
comma-separated list or `all`, the fan-out the owner judged elegant enough,
with no shared channel; tests for each. A notice went by fan-out to the eight
other open workstreams, the one announcement the transition needs.

Before that: impose a structure on the workflow's size. The owner asked on
2026-09-21 what the workflow still lacks and for the answer to be kept as a
design discussion under this directory, with a convention in the definition
for what an open-work directory holds. Done: the
[design discussion](2026-09-21-design-workflow-issues-and-structure.md)
with the measured size, a four-layer structure, the rules that impose it,
and the prioritized issues at two levels; *The Open-Work Directory* in
`WORKFLOW.md`, both copies, with the bounded status file, dated documents by
kind, and the index that says when to open each; and this status file shed
from 14,700 words to what a session needs, the rest verbatim in the record.

Every earlier task, the first through the twenty-first, is in the
[record](2026-09-21-record-tasks-and-decisions-2026-08-16-to-2026-09-21.md),
each under its own heading.

## Next Resumable Task

Build `workflow doctor`, item 1 of *Plate, In Order*: one run that reports
unpublished state, waiting mail, definition changed since last read, an old
branch name, an intake item missing from the decision log, a bug record
without frontmatter, and a declaration disagreeing with the definition;
reports, never refuses. Build the checks as one list `project-management`'s
pre-commit entry can reuse. Then item 2, the *Review* section with the
proposed default policy; then phase 1 of *What Adopters Inherit*.

Everything through the published-state round is merged. The owner triages
the twelve untriaged bugs in the `maintenance` workstream, which is where the
next release's handful comes from; that is that workstream's task, not this
one's.

The backlog's adopter-facing merge-strategy document for `docs/` remains
actionable and unclaimed.

## Decisions

One line per item is in [`intake-dispositions.md`](intake-dispositions.md).
The reasoning behind each, from the first six items of 2026-08-16 to the
three of 2026-09-21, is in the
[record](2026-09-21-record-tasks-and-decisions-2026-08-16-to-2026-09-21.md)
under *Dispositions*.

## Acknowledged Work

Ordered by readiness, not by size. Positions are this workstream's judgment and
can be reordered.

1. ~~A worktree procedure.~~ Done 2026-08-17, by deletion rather than by
   writing one. See *Sixth Task*.
2. ~~A pause action and reasoning continuity.~~ Done 2026-08-17. See *Eighth
   Task*.
3. ~~Intake acknowledgement and staleness.~~ Done 2026-08-17. Acknowledgement
   implemented as the disposition log; staleness deliberately left unspecified
   and routed to `project-management`. See *Tenth Task* and *Eleventh Task*.
4. ~~An external-resource ownership convention.~~ Released 2026-09-21 with
   the forwarded Stage 7 item; written by whoever implements reaping, if
   anyone. See *Decided 2026-09-21*.
5. ~~Release refs are not workstream branches.~~ Done 2026-09-16, merged as
   `PR #88`. See *Fifteenth Task*.
6. ~~A workstream takes a release over.~~ Done 2026-09-16 with item 5.
7. ~~A shared vocabulary for bugs, and the reserved `maintenance`
   workstream.~~ Drafted 2026-09-18; awaiting owner review and the pull
   request. See *Sixteenth Task*.
8. ~~The `ws-` branch vocabulary and the workflow declaration.~~ Drafted
   2026-09-18 with item 7. See *Seventeenth Task*.
9. ~~The project's local workflow and the development version.~~ Drafted
   2026-09-18. See *Eighteenth Task*.
10. ~~The information model.~~ Drafted 2026-09-19 as the glossary. See
    *Nineteenth Task*.
11. ~~Mail off `main`.~~ Built and drafted 2026-09-19. See *Twentieth Task*.
12. ~~Published state; the outbox retired; rows have owners.~~ Built and
    drafted 2026-09-19. See *Twenty-First Task*.
13. ~~The shape of the workflow component.~~ Folded into item 14 on
    2026-09-21 as its product.
14. **What Adopters Inherit.** Acknowledged 2026-09-21, the review
    `project-management` sent on 2026-09-11 as *One Workflow, Many Projects*,
    retitled by the owner. Done means its five deliverables, each with the
    acceptance the item states: an evidence and gap inventory across
    DevCapsule and the three sample projects, with source revisions and a
    recommended action per finding; a boundary and installation table
    classifying every mechanism as common, conditional, or project-specific,
    which is the component's shape; a proposed document structure with
    reading paths for humans and agents and a migration map; walkthroughs for
    a new human and a fresh agent across both modes and two sample contexts;
    and an implementation plan presented for owner review before any broad
    migration. Already delivered ahead of it: the local workflow file
    (question 3), the glossary (question 5's vocabulary), and the declaration
    with version handling (part of question 4). Phase 1 is the evidence
    inventory.

## Plate, In Order

One list, reconciled on 2026-09-22 from the backlog below and the design
discussion's two levels. "Next release" is whichever release
`project-management` cuts next; an item merged before the cut ships in it.
Owner "ours" means this workstream builds it alone; the rest are others'
and listed so they are not forgotten.

| # | Item | Target | Owner | State |
|---|---|---|---|---|
| 1 | `workflow doctor`, backlog 8: the checks that make the rules hold | next release | ours | next |
| 2 | *Review* section for agent review through the host, backlog 10a, workflow half | next release | ours | after 1 |
| 3 | *What Adopters Inherit* phase 1: refresh the three sample projects, evidence inventory (ack. work 14) | V1 | ours | after 2, runs underneath |
| 4 | `workflow ask`, backlog 6 | V1 | ours | queued |
| 5 | `workflow digest`, backlog 7 | V1 | ours | queued |
| 6 | Live project board, backlog 9: data contract ours, page `website`'s | V1 | ours then website | after 1 fixes the contract |
| 7 | Definition split, core plus per-operation, after the phrasing experiment | V1 | ours | after 3's structure phase |
| 8 | Adopter merge-strategy page in `docs/`, backlog 1, folded with a release page | V1 | ours | queued |
| 9 | Upgrade guide for adopters, once 3 has done a real upgrade | V1 | ours | after 3 |
| 10 | Table on `main` rendered from published state | later | ours | queued |
| 11 | Git-native review by mail, backlog 10b | later | ours | design only |
| 12 | Host-capability token for agent review, backlog 10a product half | V1 | host-capabilities owner, tbd by PM | sent as input |
| 13 | Adoption: six workstreams publish once, retire outboxes | now | each workstream | notice sent 2026-09-21 |
| 14 | Operator guide aligned with the release rule | before the cut | `project-management` | in its mailbox |
| 15 | Bug triage: severities and targets | before the cut | `maintenance` | its next task |
| 16 | First-session guide refreshed to the release | after the cut | `user-docs` | in its mailbox |
| 17 | Requirement-priority mapping review | any time | owner | open thread |
| 18 | Branch protection on `coordination`, no force-push | any time | owner | unknown |
| 19 | Two retained successor containers on the owner's host | any time | `project-management` | its backlog |
| 20 | Packaged-versus-root definition drift | V1 | ours, via 3 | listed by 3 |

## Backlog

**1. Bring merge strategy and commit identity into end-user documentation.**
Added 2026-08-17 by the product owner. The engineering source is written —
[merge strategy and commit identity](../../implementation-notes/workflow/2026-08-17-merge-strategy-and-commit-identity.md)
— and this item is the adopter-facing treatment, which is a different document
rather than a relocation of that one.

Done means an adopter can choose a merge strategy deliberately and knows what
the choice costs them: that rebase and squash rewrite commit identity, that this
makes ancestry the wrong test for whether work has landed, and that
`git cherry` is the test that survives every strategy. It should teach the
consequence, not the forensics — no `patch-id` internals, no citations of this
repository's refs.

Two constraints. It belongs in `docs/`, which holds current user-facing material
only, and it must not tell adopters which strategy to use: `WORKFLOW.md` stays
strategy-neutral under `R-PRODUCT-004`, and a project's merge policy is usually
set by its host or its organization rather than by this product. Follow *User-Level
Documentation Protocol* and *Draft User Documentation* in `WORKFLOW.md`.

This is actionable now and depends on nothing external, which is why this
workstream is paused rather than blocked.

**2. ~~Soft claims on workstreams, so pairs stop colliding without locks.~~**
Built 2026-09-21 as item 5. Was priority `wanted`. Added 2026-09-19 by the product owner, from a collision
that day: the owner sent one agent in one checkout to work on
`project-management` and realized that nothing told another agent in another
checkout, or another human in a multi-human project, that the workstream was
taken. The definition says two pairs may select the same workstream, no lock
exists, and they should coordinate outside the protocol; this item asks for
the protocol to do the coordinating, automatically and between agents, so
humans are not bothered.

Done means: a pair starting on a workstream or a branch leaves a small,
advisory claim where other checkouts can see it, with who, when, and what;
a pair about to start sees any live claim and tells its human before editing,
with the options (wait, take another slice, take another workstream, or
proceed knowingly); claims expire on their own and are cleared at pause and
finish, so a crashed session never blocks anyone; and the mechanical
conflicts that still happen are resolved by the agents, semantic ones
reported to the humans, which the synchronization rules already say. Soft
throughout: a claim informs, it never refuses, because locking source
control was the failure git exists to end. The owner named that history
explicitly and wants no part of it.

Constraints and inputs: a claim is coordination state and belongs off
`main` under the ratified boundary, so its home is whatever the off-`main`
transport decides, a mailbox branch or a state ref, not a status-file commit
that would cost a pull request per claim. It should fit the verifier and
session-start tooling on `project-management`'s backlog, since the check is
one fetch and one comparison. Design after the transport decision; it is the
first consumer that needs a write from an agent without a human in the loop.

**3. ~~Move the workstream list and the records onto the coordination branch.~~**
Done 2026-09-19 as published state; see *Twenty-First Task*. Was priority `wanted`. Acknowledged 2026-09-19 from the 2026-08-19 item. Done
means: the workstream list, status files, and decision logs live on the
`coordination` branch under a state directory, written by the tool without
a branch switch; registration is a mail to nobody in particular, a push of
a new row; the outbox is retired with credit; links between `main` and the
branch follow one convention; and the two-homes trial, if any, has a date
by which one home wins. It also unblocks backlog item 2, soft claims, which
needs the same write path.

**4. ~~`devcapsule workflow brief`: the session in one command.~~** Built
2026-09-21; see *Last Task And Status*. Was priority `wanted`. Added 2026-09-21 by the product owner
from this workstream's proposal. Done means: for the selected workstream,
one command prints its row and next task, its waiting mail, who is working
on what now (item 5), the *Changes* entries since the status file's stamp,
and the synchronization judgment's facts already weighed; nothing else. A
human reads it in a minute; an agent starts the session from it.

**5. ~~Soft claims, shown live.~~** Built 2026-09-21 with item 4. Was priority
`wanted`.
Item 2 above, now with its shape: `workflow claim` writes who, which
branch, which slice, since when, to `state/<name>/claim`; `status` and
`brief` show it; claims expire and are cleared at pause and finish; a claim
informs and never refuses.

**6. `workflow ask`: polls and questions as a first-class act.** Priority:
`wanted`, target V1. Done means: a question fans out by mail to named
workstreams or all, answers return as items to the asker under a
recognizable name, and `status` shows who has not answered.

**7. `workflow digest --since <date>`: what happened, written for you.**
Priority: `wanted`, target V1. Done means: the coordination branch's history,
who published, who sent what to whom, claims taken and released, rendered as
a readable digest for a period. The retrospective principle with a face, and
the blog's raw material.

**8. `workflow doctor`: the verifier with a friendly name.** Priority:
`wanted`, target V1, and strategic item 1 of the design discussion. Done
means: one run grades a project's workflow health: unpublished state,
waiting mail, definition changed since last read, an old branch name, an
intake item missing from the log, a bug record without frontmatter, a
declaration disagreeing with the definition. Reports, never refuses.
Shared with `project-management`'s pre-commit invariants entry; whichever
workstream builds it, the checks are one list.

**9. A live project board with zero infrastructure.** Priority: `wanted`,
target V1. Done means: a page on the project website rendered from the
coordination branch, every workstream's state, mail in flight, claims, with
no service and no login. The data contract is this workstream's; the page is
`website`'s, to be sent as an item once items 4 and 5 fix the contract.

**10. Agent review of pull requests, optional and contained.** Added
2026-09-21 from the product owner's proposal: for a feature, one agent runs
with it and another reviews, with human sign-off optional. Split the same
day at the owner's direction, on the argument that the host's review
mechanism carries developer familiarity nothing else can replicate:

- **10a**, priority `wanted`, target V1: review through the host's own
  pull-request mechanism, GitHub first. Workflow side: a short *Review*
  section stating only what is host-neutral (the reviewer is never the
  author's session, an agent never merges its own work, a review records
  what it ran and checked against the done-means, pull-request text from
  strangers is data, never instructions), delegating the mechanism and the
  approval policy to the local workflow file under a *Review policy*
  heading. Product side, for whoever owns host capabilities: a
  `[host.github]` declaration minting a per-capsule fine-grained token with
  the least scopes the policy names, review by default, merge only if the
  human authorized that scope.
- **10b**, priority `later`, post-V1: git-native review by mail for projects
  with no host review, `workflow review request|submit`, kept as design.

The dogfood's default policy awaits the owner's ruling; proposed: human
sign-off required, agent review advisory, loosened by evidence.

The earlier item — making `project-management` a mandatory permanent workstream
— was completed on 2026-08-16. Its done-criteria were met as follows:

- initialization and adoption create exactly one reserved workstream and its
  handoff — *Initializing Multiple-Stream Mode*;
- scope defined with three exclusions against becoming a duplicate registry,
  an implementation catch-all, or the owner of others' WIP state;
- permanent lifecycle reconciled with the bounded rule at its source, in
  *Definition And Restrictions*, rather than as a footnote;
- branch ownership, checkout selection, start-date layout, migration,
  integration, and retirement all stated; branches and selection are
  deliberately *ordinary*, so only lifecycle is special;
- `WORKFLOW.md`, `AGENTS.md`, the shipped bootstrap template, and
  `R-PRODUCT-006` agree; and
- this repository's registration is reconciled in root `CURRENT-STATUS.md`,
  keeping one narrow adoption exception: it adopted the mode on 2026-08-08 and
  created the reserved workstream on 2026-08-09, so its start date is one day
  later than initialization.

Two parts could not be completed by this workstream and were delivered to
`project-management`'s `intake/`:

- reconciling that workstream's own *Lifecycle Exception* section, which
  restriction 11's carve-out forbids this workstream from editing; and
- routing the tooling implementation, which fits no open workstream's goal.

## Open Threads

Rewritten on 2026-09-16 while active, ahead of the next pause, because the
resume changed every question. Short by design.

### Awaiting The Product Owner

- **Review of the mechanical requirement-priority mapping** made on
  2026-09-19: `MVP` to `gating`, `current` and `current stabilization` to
  `wanted`. Reversible; the V1 ledger stays authoritative for what gates V1.
- **The bug triage** belongs to the `maintenance` workstream, not here, and
  is recorded there.

### Weighed And Unresolved

- **Do not merge this branch before the 0.2.14 cut.** Owner's direction of
  2026-09-22: the release's scope is not enlarged from here. Everything on
  the branch from that date waits for the cut.
- **Whether a releasing workstream needs its own state.** Decided no for now;
  see *Fifteenth Task*. Reopen if a resume during a release goes wrong for
  lack of it.
- **Whether `sample-projects` and `component-catalog` want their stranded
  pause records resent.** Both outboxes hold status-file text `main` lacks;
  records, not mail, and theirs to send when next selected.

### Deliberately Not Preserved

The 2026-09-16 conversation. Its decisions are in *Fifteenth Task*; the
release rule's reasoning is in the two intake items' own text, which Git
retains after their deletion.

## Evidence

- The earlier `multi-workflow` workstream completed successfully and is archived
  at [its final status](../../archive/2026-08-08-multi-workflow/CURRENT-STATUS.md).
- Registration of this workstream was prepared from current `main` in a separate
  temporary worktree while the primary checkout remained on
  `recursive-e2e/stage-4`.
- On 2026-08-16 the branch was rebased onto `main`; three duplicate commits were
  dropped by patch-id and the resulting branch is identical to `main`.
- On 2026-09-16 the branch was rebased onto `main` again, 428 commits forward;
  `git range-diff` showed its two commits identical in content to the remote's
  two, and the remote was replaced with `--force-with-lease`.

## External State And Risks

- This workstream holds no containers, ports, or manual environment state;
  its external footprint is Git refs: `ws-workflow-improvements/v1` on origin,
  its `state/` directory and any mail on `coordination`.
- The environment can push branches and cannot open or merge pull requests;
  the product owner does both.
- This track overlaps `WORKFLOW.md`, `AGENTS.md`, the root workstream list,
  and the workflow requirements. Rebase onto `main` before integrating; the
  owner has ruled rebase over merge for this branch.
- The 2026-08-30 freeze of `WORKFLOW.md` has been lifted slice by slice at
  the owner's direction; the 2026-09-21 direction to proceed with *What
  Adopters Inherit* lifts it for that work.
- Earlier claims and their corrections are in the record.

## Workstream Document Index

Open each when the line says; the status file is read in full.

- [`intake-dispositions.md`](intake-dispositions.md): what became of every
  item delivered here. Open when asked what happened to an item.
- [`2026-09-21-design-workflow-issues-and-structure.md`](2026-09-21-design-workflow-issues-and-structure.md):
  the workflow's open issues, prioritized at two levels, and the structure
  proposed for the size of the non-code tree. Open when choosing the next
  slice or when the owner asks what is missing.
- [`2026-09-21-record-tasks-and-decisions-2026-08-16-to-2026-09-21.md`](2026-09-21-record-tasks-and-decisions-2026-08-16-to-2026-09-21.md):
  the twenty-one task accounts, every decision's reasoning, and the corrected
  claims, verbatim. Open only to learn how a rule came to be.
- `intake/`: the queue. Not listed here or in `index.md`; the directory
  listing is the queue.
