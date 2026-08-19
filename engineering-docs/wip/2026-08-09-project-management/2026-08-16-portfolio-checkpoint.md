# Portfolio Checkpoint: 2026-08-16

Recorded by: `project-management`

The second portfolio checkpoint. It exists because a set of sequencing decisions
became due together once V1 acquired a defined scope: what ships in v026, what
waits for v027, who owns each, and which questions belong to another workstream.

Detailed implementation state stays in each workstream's handoff. This file
records only what needed deciding across them.

## Portfolio State

| Workstream | State | Note |
|---|---|---|
| `recursive-e2e` | resuming | Delegated the v026 deliverables. Stage 6 hardening still outstanding, and two commits including the Stage 6 inspector remain unintegrated. |
| `sample-projects` | active | Owns sample skeletons derived from the product owner's own projects once those begin. |
| `workflow-improvements` | active; not yet started | Intake now holds six items. Starting it is on the critical path for the product owner's project starts. |
| `project-management` | active; permanent | This checkpoint. |

## Decision 1: v026 Scope And Delegation

The v026 base carries two deliverables, and bugs fixed for v026 are the current
top priority:

1. **A self-contained tool entry point.** The published artifact must run on a
   supported host with no Python installed. See the
   [V1 scope ledger](v1-scope-ledger.md).
2. **The URL-open fix.** Clicking a link in the containerized IDE must open a
   browser on the developer's desktop. A shim forwarding to a host-side helper
   is transport-independent and therefore does not wait on the display decision.

Both are delegated to `recursive-e2e`, and delivered to its intake rather than
announced here.

The product owner has judged v026 plus these two fixes sufficient to begin their
own projects without being blocked or wasting inordinate effort.

### Consequence: The Registered Goal Understates The Work Again

`recursive-e2e` is registered to build and launch a successor DevCapsule from
inside the dogfood environment. A self-contained entry point and a URL shim are
product work, not recursive-E2E work.

This is the second instance of the pattern the
[2026-08-15 checkpoint](2026-08-15-portfolio-checkpoint.md) recorded for
`sample-projects`, and the
[V1 readiness assessment](2026-08-16-v1-readiness-assessment.md) argued it is a
delivery risk rather than a naming question: when product work lands with no
milestone home, nothing updates the V1 gap list as gaps close.

Resolved here by widening the registered goal in root `CURRENT-STATUS.md` rather
than leaving the registry understating where the work lives.

### Related State This Decision Should Not Ignore

- The workstream was paused. Root `CURRENT-STATUS.md` still described it as
  "Stage 4 ready to begin" while its handoff reported Stage 6 substantially
  complete. Both are corrected in this change.
- Two commits, `c26d877` and `c24b442`, including roughly 1,600 lines of Stage 6
  inspector work, are published on the branch and not on `main`. Resuming the
  workstream is the moment to land them; the readiness assessment recorded them
  as the repository's clearest drop risk.
- The branch is named `recursive-e2e/stage-4` while the work sits at Stage 6 and
  now includes v026 product deliverables. Cosmetic, but it will mislead.

## Decision 2: The Contained Display Waits For v027

The VNC and Xpra spike, and the contained-display direction decided earlier on
2026-08-16, move to v027. They may warrant a separate workstream rather than
joining an existing one.

Rationale: the display change touches the base recipe, the launcher, port
allocation, and the platform matrix, and its own ledger row requires a full day
of ordinary development inside the result before ratification. That is not
compatible with v026 being the base the product owner starts projects on this
week.

The URL fix is deliberately separated from it, because the shim works under
every candidate transport and fixing the most irritating symptom should not wait
on the transport decision.

Unchanged by this deferral: the
[X11 session-credential bug](../../bugs/devcapsule/2026-08-16-x11-passthrough-grants-full-session-credential.md)
remains open, and the containment claim cannot be announced as verified while
the X socket carries a full host session credential. Deferring the display
transport defers the fix, not the obligation.

## Decision 3: Bug Vocabulary Belongs To `workflow-improvements`

The product owner asked which bugs are high priority. No bug can answer: all
thirteen records carry free-text `Status:` prose, and none carries a priority or
severity field.

Rather than invent a vocabulary in this checkpoint, the question is delivered to
`workflow-improvements`, which owns the record formats. This checkpoint records
the priority decision itself — v026 bugs first — without pretending the
repository can express it yet.

## Delivered Through Intake

Both handoffs were written into the receiving workstream's `intake/` rather than
announced here, which is the mechanism introduced earlier the same day precisely
because the 2026-08-15 checkpoint's announcements never arrived.

- `recursive-e2e`: the two v026 deliverables.
- `workflow-improvements`: shared bug vocabulary and record properties.

## Next Editing Checkout

`project-management/coordination` remains selected for coordination work. The
v026 deliverables belong on the `recursive-e2e` branch; the display work belongs
wherever v027 is eventually routed.
