# Intake: Coordination State May Not Belong On `main` At All

Delivered: 2026-08-19

From: `project-management`. The analysis is this workstream's. **One part is now
a ratified product-owner decision — the storage boundary in *The Ratified
Boundary* below — and the rest is argument.** Everything outside that section is
the strongest case this workstream can make, not an instruction; the shape of
the workflow component remains yours.

## What Is Being Handed Over

The product owner's concern: work-management commits, branches, pull requests,
and conflict resolution crowd out actual software changes in the GitHub
repository. Workflow-definition changes are explicitly discounted from the
complaint, since `WORKFLOW.md` is expected to migrate to its own repository. The
concern is about everything else — the registry, handoffs, intake, dispositions,
checkpoints, and the machinery that moves them.

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

Trace the dependency. Intake items must reach `main` so recipients can see them.
`main` is pull-request gated because *code* needs review. Therefore a standing
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
- **The human stops being the network.** Delivering an intake item needs no pull
  request, so the two-day stranded-item latency observed on 2026-08-16 dissolves
  rather than being documented around.
- "Outbox" leaves the vocabulary entirely.

That last point is why this is being sent alongside the information-model task
rather than after it. This item may **delete a concept rather than rename one**,
and the model should be defined knowing that the outbox is contingent on a
storage decision rather than fundamental to the workflow.

## The Ratified Boundary

Decided 2026-08-19 by the product owner, after the options above were put to him
with the narrow-versus-wide split named explicitly.

**Durable records stay on `main`, on the main branch.** Requirements, decision
records, bugs, and user-facing documentation are product artifacts. They are
referenced by code, they are worth reviewing, and requirement changes are the
one class of coordination that genuinely should pass through review.

**Coordination state moves off the main branch.** The product owner's own terms:
the chatter, the communication, the status, and the coordination items. In
present paths that means `engineering-docs/wip/**` and root `CURRENT-STATUS.md`
— handoffs, intake, disposition logs, checkpoints, and the registry.

**A detached branch is the preferred shape**, as the simplest thing that works.

What that decision does *not* settle, and is yours:

- the exact file list at the boundary, and what happens to workstream documents
  that are really design notes rather than status;
- the link convention that replaces relative paths across the boundary;
- whether the outbox concept survives at all — on this analysis it does not;
- timing, and whether any of it is a V1 commitment; and
- how the state ref is written and read in practice.

## What Makes This Cheaper Than The Cost List Suggests

Three findings from checking the repository on 2026-08-19, after the costs below
were written. They do not remove any cost; they resize three of them.

**CI will not fire.** `tests.yml` triggers only on push to `main` and the
release workflow only on tags, so a state branch is invisible to CI: no test
runs, and no `chore: update coverage badge [skip ci]` commits, which are
themselves part of the noise on `main` today.

**Use `refs/heads/`, not a custom namespace.** This retracts the "invisible by
default" cost below in part. An orphan *branch* appears in GitHub's branch
dropdown and renders normally in the web interface; a `refs/state/*` namespace
would be hidden. The price is that it appears in branch listings and could in
principle be merged into `main` by accident, which argues for a name that makes
that obviously wrong.

**The link migration is small and asymmetric.** Only three files on `main` link
into `wip/` — `index.md`, root `CURRENT-STATUS.md`, and the X11 bug — thirteen
links in total. The larger half is twenty-six links pointing *out* of `wip/` at
main-resident bugs, requirements, and decisions, which break because those paths
do not exist on an orphan branch. That is the one real chore, and it is the
reason a link convention is named as open work above.

## The Flow Win Is Larger Than The Noise Win

Sending one intake item today costs: clean the working tree, check out the
outbox, add the file, commit, push, and check the working branch back out. In
the session that produced this item that sequence ran four times.

A state ref can be written with plumbing — a temporary `GIT_INDEX_FILE`, then
`read-tree`, `update-index`, `commit-tree`, `update-ref`, and a push — **without
leaving the current branch and without a clean working tree.** One command,
mid-edit, no branch switching and no stash, in roughly fifteen lines of shell.

So the change removes ceremony rather than only log noise, and the latency fix
comes with it: no pull request per delivery means the human stops being the
network, which is what stranded two items for two days on 2026-08-16.

## The Costs, Stated Honestly

- **Coordination loses review.** Probably a gain, given that nobody reviews it,
  but the ability to object to a checkpoint before it lands is genuinely lost.
- **No atomic commit spanning code and status.** Real but rarely wanted. The
  atomicity that carries weight — an intake item's deletion landing in the same
  commit as its disposition — is preserved within the state ref.
- **Invisible by default.** A fresh clone shows no state without a command or a
  worktree, and GitHub's interface will not render a non-standard ref. This is
  only tolerable if tooling exists.
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

## Sequencing, And One Caveat On Trialling It

**Mechanism after model.** The plumbing is roughly a day. The protocol text is
not: `WORKFLOW.md` carries forty-nine references to intake and forty-two to the
outbox, all predicated on `main` being the transport, and this change may delete
the outbox concept rather than adjust it. Patching ninety-one references before
the information model is settled means writing them twice.

**A trial must be time-boxed.** Putting new coordination on the state branch
while existing files stay on `main` is additive and fully reversible, which
makes it the safe way to try. But two homes for one kind of document is exactly
what this project already paid for with the duplicated `intake/README.md`
normative text. If it is trialled that way, the trial needs a stated date by
which one home wins, or it becomes the worst of both.

**The door is hard to reopen.** The change takes coordination out of review
entirely. On the evidence that is a gain, since nobody reviews it — but once the
protocol assumes direct pushes, restoring review is a protocol change rather
than a preference.

Items sent by `project-management` cannot be forwarded. Disagreement with the
argument is expected and welcome, and the shape is yours; the boundary in *The
Ratified Boundary* is the product owner's and is not open on the same terms.
Raise it with him if you judge that premise wrong.
