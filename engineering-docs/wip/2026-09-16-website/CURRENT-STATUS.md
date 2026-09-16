# Workstream Current Status: Website

Mnemonic: `website`

Start date: `2026-09-16`

State: active; registered for a human-triggered fresh-context start; setup and implementation not begun

Branch association: `website/initial-cut`; prefix `website/`

Integration target: `main` in DevCapsule; website submodule repository's own mainline once created

Delivery method: reviewable branches and pull requests; the human opens/merges
PRs where agent credentials do not permit it. Production publication follows review.

## Task Contract

Read the [website autonomy work order](../../work-orders/2026-09-16-website-autonomy.md)
in full. It contains the agreed requirements, autonomy exception, budget,
minimal-interruption policy, hosting choices, resources, and judging procedure.
It is sufficient context for this experiment; do not reconstruct the old chat.

The goal is a professional, engaging website with landing content, navigable
user docs, and the development blog sourced from DevCapsule. Website machinery
lives in a separate GitHub project included as a submodule, with its own
DevCapsule development setup by delivery. A local preview and a working update
mechanism are required. No database or blog comments. Final output is ready for
review and deployment; no unreviewed production launch is authorized.

## Registration And Branch Preparation

Opened at the owner's request by user-docs. The work order is delivered on
`user-docs/first-session`, beginning with commit `ba03649`; this registration
travels separately through `user-docs/outbox`. Merge the work-order delivery
before this registration so the permanent brief is available on main.

The owner expressly allowed the initial branch to be prepared from the current
user-docs branch for easy pickup of the brief. Accordingly, `website/initial-cut`
may be created and pushed after the registration records are prepared, before
their mainline merge. This is a narrow exception to the normal main-first branch
creation sequence. It does not authorize implementation before mainline
registration or before the human starts a fresh context with `/new` and selects
this workstream. The preparing pair remains in user-docs.

At setup, fetch and verify the accepted-main registry and work order. If either
delivery is missing, report the outstanding merge instead of silently treating
a branch-local registry as authoritative. Synchronize this published starting
branch with accepted main without overwriting unique work.

## Planned Next Step

After the human's fresh-context selection, read repository startup instructions,
this handoff, intake, and the work order. Conduct only the bounded investigation
needed to choose an approach and prepare one consolidated human setup request.
Include website repository creation, hosting/DNS access, costs and permissions,
exceptional-warning contact path, and how final PR/deployment steps will work.
Verify supplied access before declaring the autonomous implementation run ready.

Then execute the scoped autonomous experiment without routine design approvals.
Keep progress, estimates, open questions, and resumable checkpoints here.
No website implementation, infrastructure provisioning, or model download has
been performed by the preparing pair.

## Dependencies And Boundaries

- `user-docs` is deliberately paused for the experiment. Its v1 first-session
  rewrite and v0.2.12 cleanup remain its backlog. Current interim content is
  accepted for the website; do not make that rewrite an implementation dependency.
- The owner can create an appropriately named repository under `ccozianu`.
  Existing GitHub/Docker credentials must be checked for actual permissions.
- Hosting is GitHub static hosting or cloud storage (Google Cloud preferred
  by the owner for provisioning; AWS/Azure possible). Preview domain candidate:
  `test-devcapsule.mycodespace.ai`; production: `devcapsule.mycodespace.ai`.
- The website submodule's initial development belongs to this workstream;
  future work should be independently possible from that project.
- No stack, hosting service, repository name/path, or publication trigger has
  been chosen. These are delegated decisions, not questions to send one at a time.

## Open Threads

- Initial resource/access request and verification remain to be done by the new
  pair. No human credentials are recorded in this handoff.
- Budget is at most the agreed subscription-month allowance plus the three
  reported resets. Establish visibility and warning arrangements at setup;
  do not invent a token balance or assume control of account resets.
- The owner judges first; if necessary, the three-friends procedure in the
  work order is final. No evaluation has happened yet.
- No separate website publication, full chat transcript, or speculative design
  is preserved. The work order is the agreed scope; fictional blog dialogue
  is website content, not instruction.

## Documents

- [Work order](../../work-orders/2026-09-16-website-autonomy.md)
- [Intake](intake/README.md)
- [Disposition log](intake-dispositions.md)
