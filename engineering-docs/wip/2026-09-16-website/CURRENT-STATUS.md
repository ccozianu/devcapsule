# Workstream Current Status: Website

Mnemonic: `website`

Start date: `2026-09-16`

State: active; fresh-context start performed; consolidated human setup checkpoint pending; implementation not begun

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

Resolve the consolidated setup request below, verify access to the new website
repository, and confirm the preview, warning, budget, and final delivery paths.
Then begin implementation. Do not interpret elapsed time as setup agreement.

Then execute the scoped autonomous experiment without routine design approvals.
Keep progress, estimates, open questions, and resumable checkpoints here.
No website implementation or infrastructure provisioning has been performed.

## Setup Checkpoint: 2026-09-16

The human explicitly selected this workstream and authorized the experiment.
The checkout was clean on entry. Fetched `origin/main` at `02eb470`; local
`main` was strictly behind it (0 local-only, 102 remote-only commits).
The work order and registry are present on accepted main, and website intake
contains only its README. Switched to `website/initial-cut` and fast-forwarded
from `6e87fc7` to `02eb470`, preserving the published history. No other
workstream was edited.

Proposed approach, pending resource/setup agreement:

- Eleventy with custom layouts and CSS, using the installed Node 22/npm.
  Website machinery belongs in public `ccozianu/devcapsule-website`, included
  at `website/`. DevCapsule Markdown remains authoritative.
- The build accepts an explicit content checkout and records both source and
  implementation revisions. Standalone website development can obtain content
  without recursively checking out the parent submodule.
- Local loopback preview is the review target; confirm owner browser access
  (direct localhost or IDE port forwarding). Hosted preview is optional and
  omitted initially. No production DNS action is needed to review locally.
- An owner-triggered DevCapsule GitHub Actions workflow builds its pinned
  website submodule and publishes to DevCapsule's GitHub Pages site after review.
  Local build/preview works before either PR is merged. No cross-repository
  write token or cloud account is needed for that design.
- Expected hosting/standard public-repository runner cost is $0 under current
  GitHub terms; do not enable paid services. After acceptance, the owner merges
  website then parent PRs, enables Pages/Actions, and configures the production
  custom domain and DNS/TLS. Exact final instructions accompany delivery.

Observed access and tooling:

- Node `v22.23.1`, npm `10.9.8`, Python available. `gh`, browser executable,
  and a `devcapsule` executable on PATH are absent. Install local project and
  browser-validation dependencies within the agreed run; no Docker launch is
  needed for the website build.
- Git fetch succeeded; `git push --dry-run` to `website/initial-cut` succeeded.
  This is transport evidence, not proof that workflow-file writes or API
  mutations are allowed.
- GitHub connector identifies `ccozianu` and reads DevCapsule metadata, which
  reports owner admin/push rights. The collaborator-permission endpoint returns
  403 `Resource not accessible by integration`; API mutation rights remain
  unverified. No GH_TOKEN/GITHUB_TOKEN environment variable is present.
- The proposed website repository returns 404 through the connector: absent or
  inaccessible. Ask the owner to create it with an initial README and provide
  this environment Git write access; connector access is useful but optional
  if the owner handles PR creation/merge.

Feasibility: this is a small static publishing project with existing content;
completion appears feasible within the authorized ceiling, without needing to
consume a month allowance. Reassess after content rendering, complete preview,
and delivery validation; stop polishing once acceptance checks are met.
No account allowance/reset telemetry is exposed by the current tools, and no
reset control is established. Ask the owner for visible allowance/reset status
and confirm this chat as the exceptional-warning channel, or an explicit
alternative. Warn with a resumable checkpoint before an anticipated overrun;
an invisible abrupt platform cutoff cannot guarantee advance warning.

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
- The setup proposal above identifies the implementation and hosting
  prerequisites. Routine design choices remain delegated after setup.

## Open Threads

- Awaiting human: create/access the website repository; agree local preview
  access and owner-managed final merges/Pages/DNS; establish warning channel
  and visible allowance/reset status. Verify supplied access before building.
- Budget is at most the agreed subscription-month allowance plus the three
  reported resets. Establish visibility and warning arrangements at setup;
  do not invent a token balance or assume control of account resets.
- The owner judges first; if necessary, the three-friends procedure in the
  work order is final. No evaluation has happened yet.
- Weighed: GitHub Pages avoids cloud provisioning and cross-repository secrets;
  local review avoids making DNS or an early mainline merge a prerequisite.
- Deliberately not preserved: full chat transcript or speculative visual designs.
  The work order is scope; fictional blog dialogue is content, not instruction.

## Documents

- [Work order](../../work-orders/2026-09-16-website-autonomy.md)
- [Intake](intake/README.md)
- [Disposition log](intake-dispositions.md)
