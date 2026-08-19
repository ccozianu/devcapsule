# Intake: Coordination State May Not Belong On `main` At All

Delivered: 2026-08-19

From: `project-management`. The analysis and the recommendation are this
workstream's; the product owner asked that both be sent, and endorsed the
recommendation as worth acting on. It is not recorded as a ratified decision —
the shape of the workflow component is yours, and this arrives as the strongest
argument this workstream can make, not as an instruction.

## What Is Being Handed Over

The product owner's concern: work-management commits, branches, pull requests,
and conflict resolution crowd out actual software changes in the GitHub
repository. Workflow-definition changes are explicitly discounted from the
complaint, since `WORKFLOW.md` is expected to migrate to its own repository. The
concern is about everything else — the registry, handoffs, intake,
dispositions, checkpoints, and the machinery that moves them.

## The Evidence

Measured 2026-08-18 against `origin/main` at `fdf4c37`, over the window since
multiple-stream adoption on 2026-08-08.

| Category | Commits |
|---|---|
| Total | 125 |
| Workflow definition (`WORKFLOW.md`, `AGENTS.md`) | 19 — discounted |
| Work management (`engineering-docs/wip/`, root `CURRENT-STATUS.md`) | 80 |
| Requirements | 9 |
| Product code (`devcapsule-src/`) | 32 |

**95 of 113 non-merge commits — 84% — touch no code at all.** With the
workflow-definition discount applied, work management alone still outnumbers
product code by 80 to 32.

The pull-request picture is worse than the commit picture. Ten pull requests
merged in that window, **four of them outbox pull requests**. Forty per cent of
all pull requests in this repository exist to move paragraphs between
directories — not to change the product, and not to change the workflow.

## The Diagnosis

The problem is not volume. It is that **two things with different change rates,
different review needs, and different audiences share one ref.**

Code changes need review, need `git blame` to mean something, and need `git
bisect` to work. Status updates need none of those. `WORKFLOW.md` itself
observes that nobody reviews a disposition log or a registry row. Yet both pass
through identical machinery, and the high-frequency one buries the one that
matters.

**The consequence worth dwelling on: the outbox exists only because coordination
shares `main` with code.**

Trace the dependency. Intake items must reach `main` so recipients can see
them. `main` is pull-request gated because *code* needs review. Therefore a
standing
branch per workstream, a reset-or-append rule that has already produced one
documented protocol gap, four pull requests, a human as the transport for every
message, and forty-two occurrences of the word "outbox" in the protocol — all of
it is machinery working around a constraint that exists only because status and
source live on the same ref.

Separate the storage and the bus is not simplified. It is unnecessary.

## The Options Considered

1. **A separate repository for work management**, as proposed for the workflow.
   Removes the noise, but loses colocation: a second clone, a second
   authentication path, cross-repository links that rot. The workflow definition
   is genuinely portable between projects; a project's own state is not, so the
   argument for extracting the workflow does not transfer to extracting the
   state.
2. **A separate ref in the same repository** — an orphan branch such as
   `project-state`, or a namespace such as `refs/state/*`. One clone, one
   credential, and it never appears in `main`'s history or its pull-request
   queue. Well-trodden ground: `gh-pages`, `git notes`, and Gerrit's
   `refs/meta/config` all do this.
3. **Squashing coordination to one commit per session.** Reduces the commit
   count, does nothing about pull requests or conflicts.
4. **Allowing direct push for coordination-only changes.** Removes the
   pull-request gate and the human-transport latency, but leaves the log noise.

## The Recommendation

**Option 2, with option 4 applied on that ref, and with derived state rather
than hand-written state.**

What it buys:

- `main`'s history becomes close to pure code, so log, blame, and bisect become
  useful again.
- The pull-request queue is code-only. The four outbox pull requests become
  zero.
- The registry stops being a merge target, so the row-ownership conflict class
  largely disappears — more so if the registry becomes one file per workstream
  rather than one shared table.
- **The human stops being the network.** Delivering an intake item needs no
  pull request, so the two-day stranded-item latency observed on 2026-08-16
  dissolves rather than being documented around.
- "Outbox" leaves the vocabulary entirely.

That last point is why this is being sent alongside the information-model task
rather than after it. This item may **delete a concept rather than rename one**,
and the model should be defined knowing that the outbox is contingent on a
storage decision rather than fundamental to the workflow.

## The Costs, Stated Honestly

- **Coordination loses review.** Probably a gain, given that nobody reviews it,
  but the ability to object to a checkpoint before it lands is genuinely lost.
- **No atomic commit spanning code and status.** Real but rarely wanted. The
  atomicity that carries weight — an intake item's deletion landing in the same
  commit as its disposition — is preserved within the state ref.
- **Invisible by default.** A fresh clone shows no state without a command or
  a worktree, and GitHub's interface will not render a non-standard ref. This
  is only tolerable if tooling exists.
- **Push races replace merge conflicts.** Without pull requests, two agents can
  race the ref. One file per workstream makes that nearly conflict-free, but it
  needs a fetch-rebase-retry loop.
- **Joint history is lost.** "What did the plan say when this code was written"
  becomes a timestamp correlation rather than a single log.

Three of those five are answered by tooling, which is the open sub-question on
the V1 ledger row you now own. That is not a coincidence; it is the same
decision seen from another side.

## Relationship To The Other Items In Flight

- The **information-model task** (2026-08-18) should treat the outbox as
  contingent rather than given, per the note above.
- The **workflow-component ownership notice** (2026-08-18) makes this a product
  design question, not repository housekeeping: whatever storage shape is chosen
  is what adopters inherit.
- The **extraction decision** for `WORKFLOW.md` is unaffected. This item is
  about where a project's own state lives, not about where the protocol text
  lives.

Items sent by `project-management` cannot be forwarded. Disagreement with the
recommendation is expected and welcome — it is an argument, and the shape is
yours. Raise it with the product owner if you judge the premise itself wrong.
