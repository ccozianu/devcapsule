# Custody Record: Two Live Outbox-Reset Losses, Caught Before They Happened

Written 2026-09-09 by `eclipse-surface` at the product owner's explicit
direction, while opening this workstream.

**This document is not `eclipse-surface` work and this workstream does not own
it.** It is held here temporarily because the owner asked for a record that
cannot be lost, and this workstream's registration was the commit already on
its way to `main`. It should be moved to whichever workstream the owner
assigns — `project-management` owns the communication record, and
`workflow-improvements` owns the protocol fix — and deleted from here in the
same change.

## Why This Exists

While preparing this workstream's registration for delivery, the send protocol
required hard-resetting `project-management/outbox` from current `main`. That
branch turned out to be carrying an undelivered item from 2026-08-19 that has
never reached `main`. Performing the prescribed reset would have destroyed it.

The full content of that item is reproduced verbatim in *Appendix A* below, so
that it survives even if every branch carrying it is deleted.

Auditing the other four outboxes afterwards found a second live one, stranded
since 2026-08-17 on `workflow-improvements/outbox`. It is reproduced verbatim in
*Appendix B*. It has survived only because its sender has been idle; the next
send from that workstream destroys it.

## The Mechanism, Stated Plainly

The loss is not caused by anyone doing the protocol wrong. It is caused by the
protocol as specified. `project-management` established this on 2026-08-29 when
it answered `2026-08-17-recursive-e2e-audit-undelivered-work.md`: *"undelivered
work was lost because outbox resets destroy undelivered mail, and the protocol
as then specified permitted exactly that… The specified protocol was followed;
the specification was incomplete."*

The chain has four links, and each one is individually reasonable:

1. **An outbox is a one-shot mailbox that must be emptied.** *The Outbox
   Branch* in `WORKFLOW.md` says every send begins by creating or hard-resetting
   `<mnemonic>/outbox` to current `main`, because "the outbox holds no history
   of its own worth preserving." That rule exists for a good reason: it is what
   stops the sender's working changes from leaking onto `main`.

2. **Delivery is asynchronous and not guaranteed.** The branch is pushed and
   then merged "by the repository's default method" — here, a pull request. The
   push is the sender's last act. Whether a human ever opens, reviews, and
   merges that PR is outside the sender's control and outside the protocol.

3. **The next send resets regardless.** Step 1 is unconditional. There is no
   precondition of the form "only reset if the previous send landed." So if a
   send is pushed and never merged, the *next* send silently overwrites it, and
   on the remote the orphaned commit becomes unreachable.

4. **No usable safety check exists at that moment.** The obvious guard — "is the
   outbox tip an ancestor of `main`?" — is explicitly disallowed. `WORKFLOW.md`
   warns "Do not assume a merged outbox is an ancestor of `main`," because under
   squash and rebase merges a *successfully delivered* outbox is never an
   ancestor. That warning correctly stops the agent concluding "landed" from
   ancestry, but it supplies no positive test to replace it, so the reset step
   ends up with no guard at all.

The result is a mailbox that is emptied on a schedule set by the sender and
filled by a process completed by someone else, with no interlock between them.

### Why It Is Invisible Afterwards

Worse than the loss is that nothing detects it. The disposition-log invariant —
"on `main`, every item ever delivered here is either still in `intake/` or
listed in the disposition log" — only ranges over items that actually reached
`main`. A stranded item is in neither place, so:

- the **recipient** never knew it existed and cannot miss it;
- the **sender** recorded "delivered at outbox `<sha>`" in its own handoff and
  believes the job is done; and
- the **invariant** is satisfied, because the item is outside its domain.

The failure therefore surfaces only when someone follows a handoff pointer into
a commit that no longer resolves. That is exactly how the 2026-09-08 loss was
found: the `component-catalog` handoff cited outbox `802adaf`, and the commit
"is not a valid object, the filename is in no tree on any ref."

### One Structural Aggravator

Rebase and squash merges rewrite commit identity, which is what breaks the
ancestry test in link 4. `workflow-improvements` already recorded the evidence
that merge commits would fix this class of defect — under merge commits
"ancestry answers correctly again, the outbox reset stops needing a force-push,
and synchronizing a delivered branch becomes a fast-forward" — and noted that
what matters most is that the strategy stop varying per pull request. That
question is open.

## The Recorded Occurrences

Five, of which the last two are the first ever caught before the damage. Both
survive only because their senders are paused, which is luck rather than
protocol.

| # | Item | Sender | Stranded | Fate |
|---|---|---|---|---|
| 1 | `2026-08-16-project-management-v026-deliverables.md` (two v026 items) | `project-management` | 2026-08-16 | Sat undelivered; landed only via `PR #25`. Resend was recommended and still did not arrive. |
| 2 | `2026-08-17-recursive-e2e-audit-undelivered-work.md` at `ebad342` | `recursive-e2e` | 2026-08-17 | Orphaned by a later reset; recovered and delivered 2026-08-27 via `PR #43`. Self-demonstrating: the audit asking about the failure was destroyed by the failure. |
| 3 | `2026-09-06-component-catalog-one-devcapsule-inside-and-outside.md` at `802adaf` | `component-catalog` | ~2026-09-07 | Destroyed. Not recoverable; **reconstructed** on 2026-09-08 in `2c1113e`, and the sender's two non-preferred design shapes "survived nowhere." |
| 4 | The `2026-08-19` amendment at `b1f7273` (Appendix A) | `project-management` | 2026-08-19 | Caught 2026-09-09 immediately before the reset that would have destroyed it. **Recovered and delivered the same day** through `PR #66`; `main` now carries it byte-identical to `b1f7273`. |
| 5 | `2026-08-17-workflow-improvements-obsolete-intake-readmes.md` at `19daa31` (Appendix B) | `workflow-improvements` | 2026-08-17 | **Still intact on `origin/workflow-improvements/outbox`.** Found 2026-09-09 by the audit. Alive only because that workstream is open-idle and has not sent since; its next send destroys it. |

Occurrence 3 was known to be permitted and was left standing deliberately:
prevention is protocol content, `workflow-improvements` owns it, and
`WORKFLOW.md` has been frozen until a release candidate since 2026-08-30. That
is a defensible call, but the ledger now reads four losses in three weeks, one
of them a ratified decision.

## Why Occurrence 4 Is The Serious One


The other three were work items and arguments. This one contains **a ratified
product-owner decision** that has been invisible to the project for 21 days.

The item is `project-management`'s coordination-storage analysis, delivered to
`workflow-improvements`' intake. `main` has its original 2026-08-19 form, which
is explicitly framed as argument: *"It is not recorded as a ratified decision —
the shape of the workflow component is yours."* The amendment stranded on the
outbox rewrites that framing to: *"One part is now a ratified product-owner
decision — the storage boundary in* The Ratified Boundary *below — and the rest
is argument."*

The string "Ratified Boundary" appears **nowhere on `main`**, on any ref.
Verified 2026-09-09 against `main` at `857035a`.

The decision it carries, quoted in full in Appendix A:

- **Durable records stay on `main`** — requirements, decision records, bugs, and
  user-facing documentation are product artifacts.
- **Coordination state moves off the main branch** — in present paths,
  `engineering-docs/wip/**` and root `CURRENT-STATUS.md`.
- **A detached branch is the preferred shape**, as the simplest thing that
  works.
- And explicitly *not* settled, left to `workflow-improvements`: the exact file
  list, the cross-boundary link convention, timing and V1 commitment, how the
  state ref is written and read, and **"whether the outbox concept survives at
  all — on this analysis it does not."**

That last clause is why this record matters beyond bookkeeping. The mechanism
described above is a property of the outbox, and a ratified decision that may
abolish the outbox has itself been trapped by the outbox for three weeks.

## Occurrence 5: What The Audit Found

`19daa31`, "Route obsolete intake README cleanup", pushed 2026-08-17 on
`workflow-improvements/outbox`. It adds one intake item for
`project-management`, sent at the product owner's direction, asking it to route
the cleanup of three workstream-local `intake/README.md` files that repeat
protocol text the current workflow has superseded.

Verified 2026-09-09 against `main` at `857035a`: the filename is in no tree on
`main`, appears in no disposition log anywhere under `engineering-docs/`, and
exists on no ref except that branch. So it is neither delivered nor
dispositioned — invisible to its recipient and, by the disposition-log
invariant, not even detectable as missing.

It is a smaller item than occurrence 4, and its substance may well be stale
after three weeks: `workflow-improvements` has since pointed its own
`intake/README.md` at `WORKFLOW.md` instead of restating it, so part of the
cleanup it asks for may already be done. Staleness is the recipient's
judgement, not a reason for the item to have vanished. It is recorded here
because a silently destroyed message is a protocol failure whether or not
anyone would still have acted on it.

## The Check That Found It

Ancestry cannot answer this — a delivered outbox is a non-ancestor of `main`
under squash and rebase merges, which is exactly what made the reset
unconditional in the first place. But content can. The outbox added specific
files; if `main` already has them, the send landed.

```sh
base=$(git merge-base "$ref" origin/main)
git diff --diff-filter=A --name-only "$base" "$ref" | while read -r f; do
  git cat-file -e "origin/main:$f" 2>/dev/null || echo "MISSING: $f"
done
```

Run against all five outboxes on 2026-09-09 at `main` `857035a`:

| Outbox | Result |
|---|---|
| `project-management/outbox` | occurrence 4 (before the reset) |
| `workflow-improvements/outbox` | **occurrence 5** |
| `contained-display/outbox` | clean — its `supervisor-core-design.md` is on `main` |
| `sample-projects/outbox` | clean |
| `component-catalog/outbox` | clean — nothing pending |

One caveat, learned by getting it wrong first: restrict the comparison to files
the outbox **added**. Comparing *modified* shared files — root
`CURRENT-STATUS.md` above all — reports every outbox as holding unreceived mail,
because `main` legitimately moves on after a delivery lands. Added files are the
reliable signal, and intake items are always added files.

This is a guard, not a cure. It tells a sender to stop; it does not say what to
do instead. The cure is the one `project-management` already stated on
2026-08-29: the exposure "ends structurally only when a send stops implying a
reset while unreceived mail exists" — carry the pending commits onto the new
base, or refuse the send until the open pull request lands.

## Outcome For Occurrence 4

Recorded 2026-09-09, after the fact, because it changes what this document is
for.

The preserved branch `project-management/outbox-pending-2026-08-19` was merged
to `main` through `PR #66` while this record was being written. Verified: the
intake file on `main` is now byte-identical to the `b1f7273` version, so the
2026-08-19 amendment and its *Ratified Boundary* section are delivered in full,
21 days late, to the recipient they were always addressed to.

That makes occurrence 4 the **first of the five to be recovered rather than
reconstructed**. Occurrence 3 was rebuilt from a surviving handoff record and
the sender's two non-preferred design shapes "survived nowhere"; occurrence 4
lost nothing. *Appendix A* is therefore now a redundant custody copy rather
than the only surviving text, and it is kept only so the record is
self-contained.

Occurrence 5 has not been delivered. Its content is safe here, but the item
itself is still absent from `project-management`'s intake, and only
`workflow-improvements` can send it.

## What Was Done, And What Was Not

Done: the item's full content is preserved verbatim in Appendix A, inside a
commit bound for `main`. It can no longer be lost by any branch operation.

Not done, and left to the owner:

- **Dispositioning occurrence 4.** It was delivered on 2026-09-09 through
  `PR #66` — see *Outcome* below — so `workflow-improvements` can now see it.
  That workstream is open-idle with seven items already waiting, and
  `WORKFLOW.md` is frozen until a release candidate.
- **Fixing the protocol.** `workflow-improvements` owns it. The 2026-08-29
  finding already states the shape of the fix: the exposure "ends structurally
  only when a send stops implying a reset while unreceived mail exists."
- **Recovering occurrence 5.** Its content is safe here, but it is still
  undelivered: it belongs in `project-management`'s intake, and only
  `workflow-improvements` can send it. That workstream is open-idle with seven
  items already waiting.

---

# Appendix A: `2026-08-19-project-management-coordination-does-not-belong-on-main.md`

Reproduced verbatim from `origin/project-management/outbox` at `b1f7273`
("Amend the coordination-storage item with the ratified boundary", 2026-08-19),
which is the amended form that never reached `main`. `main` carries the earlier
form from `bfb429a`. This is a custody copy, not a delivery: the item's real
home is `engineering-docs/wip/2026-08-09-workflow-improvements/intake/`.

> # Intake: Coordination State May Not Belong On `main` At All
>
> Delivered: 2026-08-19
>
> From: `project-management`. The analysis is this workstream's. **One part is now
> a ratified product-owner decision — the storage boundary in *The Ratified
> Boundary* below — and the rest is argument.** Everything outside that section is
> the strongest case this workstream can make, not an instruction; the shape of
> the workflow component remains yours.
>
> ## What Is Being Handed Over
>
> The product owner's concern: work-management commits, branches, pull requests,
> and conflict resolution crowd out actual software changes in the GitHub
> repository. Workflow-definition changes are explicitly discounted from the
> complaint, since `WORKFLOW.md` is expected to migrate to its own repository. The
> concern is about everything else — the registry, handoffs, intake, dispositions,
> checkpoints, and the machinery that moves them.
>
> ## The Evidence
>
> Measured 2026-08-18 against `origin/main` at `fdf4c37`, over the window since
> multiple-stream adoption on 2026-08-08.
>
> | Category | Commits |
> |---|---|
> | Total | 125 |
> | Workflow definition (`WORKFLOW.md`, `AGENTS.md`) | 19 — discounted |
> | Work management (`engineering-docs/wip/`, root `CURRENT-STATUS.md`) | 80 |
> | Requirements | 9 |
> | Product code (`devcapsule-src/`) | 32 |
>
> **95 of 113 non-merge commits — 84% — touch no code at all.** With the
> workflow-definition discount applied, work management alone still outnumbers
> product code by 80 to 32.
>
> The pull-request picture is worse than the commit picture. Ten pull requests
> merged in that window, **four of them outbox pull requests**. Forty per cent of
> all pull requests in this repository exist to move paragraphs between
> directories — not to change the product, and not to change the workflow.
>
> ## The Diagnosis
>
> The problem is not volume. It is that **two things with different change rates,
> different review needs, and different audiences share one ref.**
>
> Code changes need review, need `git blame` to mean something, and need `git
> bisect` to work. Status updates need none of those. `WORKFLOW.md` itself
> observes that nobody reviews a disposition log or a registry row. Yet both pass
> through identical machinery, and the high-frequency one buries the one that
> matters.
>
> **The consequence worth dwelling on: the outbox exists only because coordination
> shares `main` with code.**
>
> Trace the dependency. Intake items must reach `main` so recipients can see them.
> `main` is pull-request gated because *code* needs review. Therefore a standing
> branch per workstream, a reset-or-append rule that has already produced one
> documented protocol gap, four pull requests, a human as the transport for every
> message, and forty-two occurrences of the word "outbox" in the protocol — all of
> it is machinery working around a constraint that exists only because status and
> source live on the same ref.
>
> Separate the storage and the bus is not simplified. It is unnecessary.
>
> ## The Options Considered
>
> 1. **A separate repository for work management**, as proposed for the workflow.
>    Removes the noise, but loses colocation: a second clone, a second
>    authentication path, cross-repository links that rot. The workflow definition
>    is genuinely portable between projects; a project's own state is not, so the
>    argument for extracting the workflow does not transfer to extracting the
>    state.
> 2. **A separate ref in the same repository** — an orphan branch such as
>    `project-state`, or a namespace such as `refs/state/*`. One clone, one
>    credential, and it never appears in `main`'s history or its pull-request
>    queue. Well-trodden ground: `gh-pages`, `git notes`, and Gerrit's
>    `refs/meta/config` all do this.
> 3. **Squashing coordination to one commit per session.** Reduces the commit
>    count, does nothing about pull requests or conflicts.
> 4. **Allowing direct push for coordination-only changes.** Removes the
>    pull-request gate and the human-transport latency, but leaves the log noise.
>
> ## The Recommendation
>
> **Option 2, with option 4 applied on that ref, and with derived state rather
> than hand-written state.**
>
> What it buys:
>
> - `main`'s history becomes close to pure code, so log, blame, and bisect become
>   useful again.
> - The pull-request queue is code-only. The four outbox pull requests become
>   zero.
> - The registry stops being a merge target, so the row-ownership conflict class
>   largely disappears — more so if the registry becomes one file per workstream
>   rather than one shared table.
> - **The human stops being the network.** Delivering an intake item needs no pull
>   request, so the two-day stranded-item latency observed on 2026-08-16 dissolves
>   rather than being documented around.
> - "Outbox" leaves the vocabulary entirely.
>
> That last point is why this is being sent alongside the information-model task
> rather than after it. This item may **delete a concept rather than rename one**,
> and the model should be defined knowing that the outbox is contingent on a
> storage decision rather than fundamental to the workflow.
>
> ## The Ratified Boundary
>
> Decided 2026-08-19 by the product owner, after the options above were put to him
> with the narrow-versus-wide split named explicitly.
>
> **Durable records stay on `main`, on the main branch.** Requirements, decision
> records, bugs, and user-facing documentation are product artifacts. They are
> referenced by code, they are worth reviewing, and requirement changes are the
> one class of coordination that genuinely should pass through review.
>
> **Coordination state moves off the main branch.** The product owner's own terms:
> the chatter, the communication, the status, and the coordination items. In
> present paths that means `engineering-docs/wip/**` and root `CURRENT-STATUS.md`
> — handoffs, intake, disposition logs, checkpoints, and the registry.
>
> **A detached branch is the preferred shape**, as the simplest thing that works.
>
> What that decision does *not* settle, and is yours:
>
> - the exact file list at the boundary, and what happens to workstream documents
>   that are really design notes rather than status;
> - the link convention that replaces relative paths across the boundary;
> - whether the outbox concept survives at all — on this analysis it does not;
> - timing, and whether any of it is a V1 commitment; and
> - how the state ref is written and read in practice.
>
> ## What Makes This Cheaper Than The Cost List Suggests
>
> Three findings from checking the repository on 2026-08-19, after the costs below
> were written. They do not remove any cost; they resize three of them.
>
> **CI will not fire.** `tests.yml` triggers only on push to `main` and the
> release workflow only on tags, so a state branch is invisible to CI: no test
> runs, and no `chore: update coverage badge [skip ci]` commits, which are
> themselves part of the noise on `main` today.
>
> **Use `refs/heads/`, not a custom namespace.** This retracts the "invisible by
> default" cost below in part. An orphan *branch* appears in GitHub's branch
> dropdown and renders normally in the web interface; a `refs/state/*` namespace
> would be hidden. The price is that it appears in branch listings and could in
> principle be merged into `main` by accident, which argues for a name that makes
> that obviously wrong.
>
> **The link migration is small and asymmetric.** Only three files on `main` link
> into `wip/` — `index.md`, root `CURRENT-STATUS.md`, and the X11 bug — thirteen
> links in total. The larger half is twenty-six links pointing *out* of `wip/` at
> main-resident bugs, requirements, and decisions, which break because those paths
> do not exist on an orphan branch. That is the one real chore, and it is the
> reason a link convention is named as open work above.
>
> ## The Flow Win Is Larger Than The Noise Win
>
> Sending one intake item today costs: clean the working tree, check out the
> outbox, add the file, commit, push, and check the working branch back out. In
> the session that produced this item that sequence ran four times.
>
> A state ref can be written with plumbing — a temporary `GIT_INDEX_FILE`, then
> `read-tree`, `update-index`, `commit-tree`, `update-ref`, and a push — **without
> leaving the current branch and without a clean working tree.** One command,
> mid-edit, no branch switching and no stash, in roughly fifteen lines of shell.
>
> So the change removes ceremony rather than only log noise, and the latency fix
> comes with it: no pull request per delivery means the human stops being the
> network, which is what stranded two items for two days on 2026-08-16.
>
> ## The Costs, Stated Honestly
>
> - **Coordination loses review.** Probably a gain, given that nobody reviews it,
>   but the ability to object to a checkpoint before it lands is genuinely lost.
> - **No atomic commit spanning code and status.** Real but rarely wanted. The
>   atomicity that carries weight — an intake item's deletion landing in the same
>   commit as its disposition — is preserved within the state ref.
> - **Invisible by default.** A fresh clone shows no state without a command or a
>   worktree, and GitHub's interface will not render a non-standard ref. This is
>   only tolerable if tooling exists.
> - **Push races replace merge conflicts.** Without pull requests, two agents can
>   race the ref. One file per workstream makes that nearly conflict-free, but it
>   needs a fetch-rebase-retry loop.
> - **Joint history is lost.** "What did the plan say when this code was written"
>   becomes a timestamp correlation rather than a single log.
>
> Three of those five are answered by tooling, which is the open sub-question on
> the V1 ledger row you now own. That is not a coincidence; it is the same
> decision seen from another side.
>
> ## Relationship To The Other Items In Flight
>
> - The **information-model task** (2026-08-18) should treat the outbox as
>   contingent rather than given, per the note above.
> - The **workflow-component ownership notice** (2026-08-18) makes this a product
>   design question, not repository housekeeping: whatever storage shape is chosen
>   is what adopters inherit.
> - The **extraction decision** for `WORKFLOW.md` is unaffected. This item is
>   about where a project's own state lives, not about where the protocol text
>   lives.
>
> ## Sequencing, And One Caveat On Trialling It
>
> **Mechanism after model.** The plumbing is roughly a day. The protocol text is
> not: `WORKFLOW.md` carries forty-nine references to intake and forty-two to the
> outbox, all predicated on `main` being the transport, and this change may delete
> the outbox concept rather than adjust it. Patching ninety-one references before
> the information model is settled means writing them twice.
>
> **A trial must be time-boxed.** Putting new coordination on the state branch
> while existing files stay on `main` is additive and fully reversible, which
> makes it the safe way to try. But two homes for one kind of document is exactly
> what this project already paid for with the duplicated `intake/README.md`
> normative text. If it is trialled that way, the trial needs a stated date by
> which one home wins, or it becomes the worst of both.
>
> **The door is hard to reopen.** The change takes coordination out of review
> entirely. On the evidence that is a gain, since nobody reviews it — but once the
> protocol assumes direct pushes, restoring review is a protocol change rather
> than a preference.
>
> Items sent by `project-management` cannot be forwarded. Disagreement with the
> argument is expected and welcome, and the shape is yours; the boundary in *The
> Ratified Boundary* is the product owner's and is not open on the same terms.
> Raise it with him if you judge that premise wrong.

---

# Appendix B: `2026-08-17-workflow-improvements-obsolete-intake-readmes.md`

Reproduced verbatim from `origin/workflow-improvements/outbox` at `19daa31`
("Route obsolete intake README cleanup", 2026-08-17), which has never reached
`main`. This is a custody copy, not a delivery: the item's real home is
`engineering-docs/wip/2026-08-09-project-management/intake/`, and only
`workflow-improvements` can send it there.

> # Intake: Retire Obsolete Intake README Boilerplate
>
> Delivered: 2026-08-17
>
> From: `workflow-improvements`, at the product owner's direction.
>
> ## What Is Being Handed Over
>
> Three workstream-local `intake/README.md` files repeat protocol text that the
> current workflow has superseded:
>
> - `engineering-docs/wip/2026-08-06-recursive-e2e/intake/README.md`
> - `engineering-docs/wip/2026-08-09-project-management/intake/README.md`
> - `engineering-docs/wip/2026-08-14-sample-projects/intake/README.md`
>
> The product owner considers these files obsolete for the purpose of the
> `workflow-improvements` workstream. That workstream should not clean up files
> inside three other workstreams merely because it found the duplication. Route
> their replacement, removal, or other disposition to an appropriate owner.
>
> ## Why It Belongs Here
>
> This is now a cross-workstream maintenance and ownership question, not an open
> workflow-protocol design question. `project-management` owns routing and
> lifecycle decisions, while `workflow-improvements` remains open but paused
> after publishing the corrections it has completed.
>
> ## Evidence
>
> All three files still say that intake items are "accepted, deferred, or
> rejected", that senders deliver them "to `main` promptly", and that recipients
> record the disposition only in their handoff before removing the file. Those
> statements duplicate protocol and are now stale:
>
> - disposition has exactly two outcomes, acknowledge or forward; deferral is
>   not a third outcome;
> - senders deliver through their own `<mnemonic>/outbox` branch;
> - disposition also writes `intake-dispositions.md` in the same outbox commit
>   that deletes the item from `main`;
> - intake gates workstream completion; and
> - items from `project-management` cannot be forwarded.
>
> `workflow-improvements/intake/README.md` already points to `WORKFLOW.md` as the
> authority rather than attempting to carry a complete local copy. `WORKFLOW.md`
> remains the normative source for the intake and outbox protocols.
>
> ## What Accepting Would Mean
>
> Decide who removes or replaces the three obsolete files, or explicitly decide
> that they should remain with a clear non-normative purpose. If they are kept,
> make them thin pointers to `WORKFLOW.md` so future protocol changes do not
> require synchronized edits across every open workstream.
>
> Priority, sequencing, and whether this is assigned to existing workstreams or
> made separate maintenance work are `project-management` decisions.
