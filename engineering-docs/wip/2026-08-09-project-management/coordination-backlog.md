# Coordination Backlog

Owned by: `project-management`

Cross-workstream coordination work and accepted follow-ups. Each entry states
its own release commitment. Older undecided entries gain no V1 commitment
merely by appearing here. An assigned item is carried by its owning workstream;
this list retains only the coordination obligation.

## Accepted Work Retained After Intake Closure

Confirmed by the owner, 2026-10-09. These entries preserve work from the 23
closed intake messages. They are not new questions to repeat at each session.
Read the matching entry when its revisit condition applies. An unresolved
release placement is not permission to mark a committed gate as later.

The workflow already permits priority `later` (not for this release), and
acknowledgement with an item's place in the work recorded. It does not define
automatic reminders or a mandatory trigger field. The revisit conditions below
are this workstream's scheduling notes, not a new generic workflow rule.
No accepted commitment is postponed by this explanation.

### Configuration Presentation

Owner for implementation: `component-upgrades`, within the upgrade experience.
Priority: `wanted`. Release placement: unresolved; no new 0.3.0 gate.
Revisit when the broader upgrade-design slice is scoped; compare the integrated
base/configuration contract before assigning implementation.

Owner rulings of 2026-09-13/14: render configuration according to the schema it
was configured against; only mention a newer schema, rather than present new
nodes as recorded state. Offer the pinned base, the newest known recommendation
when different, and the current checkout choice, clearly marked as an override
when appropriate. Name the supported action for each choice. Launch must explain
when an override selects a different base. Preserve these outcomes when newer
commands supersede old spellings. Implementation is not claimed complete.

### Component Status Reliability

Owner: `component-upgrades`. Priority: `wanted`, toward V1, not a release gate.
Revisit when that workstream scopes its R-UPGRADE-002 follow-up after its current
consent slice, or if a concrete service incident requires earlier attention.

[R-UPGRADE-002](../../requirements/product/r-upgrade-002-status-operational-reliability.md)
is the canonical accepted contract: 48-hour observations, independent monitoring,
verified notification routes and failure drills. Provider, routes, thresholds,
operational owner and supported-adapter window are design decisions there.
Do not repeat whether to adopt the already accepted requirement.

### Repository IDE Files

Owner: `project-management`. Priority: `wanted`. Target: 0.3.0, no gate.
Revisit at the next repository-hygiene slice before release preparation.

Owner ruling of 2026-10-01: ignore this repository's .idea files. Untrack them
without deleting local files, add a root ignore entry, and document the rule
in the developer brief or local workflow. Other projects may track their own.
Keep current IDE edits out of the intake-disposition commit. No tooling feature
is requested, and this reconciliation does not execute the untracking.

### Release And V1 Obligations

The [0.3.0 proposal](2026-09-27-0216-release-planning.md) owns the current release
commitments and cut decisions. The [V1 ledger](v1-scope-ledger.md) owns the legacy
capability gate. Their planning events are the revisit triggers. First-session
UX, release automation and forced configuration remain with maintenance;
consent remains with component-upgrades. These are assigned work, not new
adoption votes. The eleven user-docs proposals still require an owner decision
before 0.3.0; L1-L13 and chosen delivery still gate V1.

## Ecosystem Bootstrap: 0.9, After Project-Type Templating

Owner decision, 2026-10-11: move ecosystem-aware bootstrap from 0.3.0 to 0.9.
Maintenance retains the bug; project-management coordinates the prerequisite
project-type templating, whose implementation owner remains to be selected.
Revisit at 0.9 planning with that dependency explicit, not during routine 0.3.0
planning. This is the bootstrap feature numbered 7 in the later release-work
list, distinct from agenda item 7 (mycodespace/checkout naming) below.

The user's intended ecosystem (Java/Maven, Scala/sbt, Python/nox, Node/npm or
Node/Yarn, for example) determines tooling discovery and environment setup.
Project utilities should be on PATH throughout the capsule by default.
Exceptional project types may use `devcapsule project shell` inside the capsule
to activate the required environment. The [accepted decision](2026-10-11-decision-project-operations-and-bootstrap.md)
preserves the details, dependency and separate 0.3.0 workflow obligation.

For 0.3.0, workflow-improvements owns the generic rule requiring the agent to
establish and maintain project build, test, run and debug instructions with the
human in WORKFLOW-LOCAL.md. This remains necessary when all execution is
delegated to the agent. It does not wait for bootstrap automation.

## Pagefind: Catalog Proposal Closed, Website Owns Integration

Owner decision, 2026-10-10. Do not create a Pagefind DevCapsule component for
the website's build dependency. The website must declare a pinned npm dependency
and lockfile and build without global Pagefind or /opt/xtras when it implements
W10 search. The personal xtras install was temporary experimental convenience.
Playwright's already delivered component is a separate decision.

Handoff `2026-10-10-project-management-pagefind-project-dependency.md` delivered
to website at coordination `5b05eeecda11`, with portable-build, static-output
browser-search and atomic-publication acceptance criteria. No new delivery date
is assigned. This is a routing record, not an open catalog decision or another
project-management implementation task. Consult website's acknowledgement at
its next publication rather than reopen the dropped catalog proposal.

## Pre-V1 Work: Tentatively 0.9, Excluded From 0.3.0

Owner decision, 2026-10-10: postpone items 7, 8 and 12 from the consolidated
agenda until before V1, tentatively 0.9, definitely not 0.3.0. Priority: `later`
relative to the current release. Coordination owner: `project-management`.
Implementation owners are assigned at pickup. The intake messages are
acknowledged with this place in the work; none is marked implemented.

Revisit when planning 0.9 or another final pre-V1 cycle, whichever comes first.
Check again before V1 acceptance so a changed version sequence cannot lose
these items. Keep them off the 0.3.0 agenda unless the owner explicitly changes
this direction. This is a postponement within the pre-V1 plan, not the ledger's
`deferred` verdict, which means outside V1. Tentative 0.9 is not a release date.

### Item 7: mycodespace And Checkout Naming

Revisit the proposed [mycodespace direction](../../design-notes/devcapsule/2026-09-24-mycodespace-lifetime-namespace-and-archive.md)
with the owner: lifetime project namespace, one-action materialization, owned
archive, runnable retained environments and the workspace/submodule relationship.
Direction and any first implementation slice remain undecided; postponement
does not approve the entire proposal.

Keep the checkout-naming proposal with it: use the directory's last component
when unique among live checkouts; retain vanished records as missing without
letting them occupy the default slot; expose directory-to-record mappings.
D-0004 remains the current contract until the owner decides a change. Showing
a checkout name in project info does not decide how that name is assigned.

### Item 8: OpenCode Evaluation

Schedule and assign a bounded OpenCode/local-model evaluation. Identify the
model, runtime, hardware and context needs; prove a small useful coding task
and resumption; assess project instructions, persistence and explicit host
boundaries. Gemma remains a candidate, not a selected model. Record evidence
and gaps for user-docs before considering component integration. No installation
or integration is authorized by this postponement.

### Item 12: Routine Documentation Cleanup

- Intake READMEs: project-management's pointer is already thin; inspect remaining
  stale copies, particularly sample-projects, and route corrections to their
  owners. Treat recursive-e2e's archived copy as history rather than a live
  protocol. Do not revive its workstream for this cleanup.
- Contract wording: reconcile the producer specification's literal-version rule
  with the authoritative website contract and existing checks, including the
  loopback-address boundary and tokenized links. The docs-0.2.15 copy already
  landed; do not repeat that delivery. This is wording reconciliation, not a
  new version-check implementation or a 0.3.0 documentation gate.

The four original messages are recoverable in Git at
`967e9f9a3622d3b84c42eec6df004267a1abf143` under this workstream's intake:
`2026-09-25-maintenance-mycodespace-and-checkout-naming.md`,
`2026-09-15-user-docs-opencode-evaluation.md`,
`2026-08-17-workflow-improvements-obsolete-intake-readmes.md`, and
`2026-09-28-user-docs-contract-version-check-and-docs-0215.md`.

### Item 13: Search Discoverability, The Rest Of The SEO Objective

Owner decision, 2026-10-16: the SEO objective set for V1 on 2026-10-16 is
worked in the 0.9.x timeframe, not now. One part is already issued and runs
on the website's own clock: the website repository's work order
[social metadata and page identity](https://github.com/ccozianu/devcapsule-website/blob/main/engineering-docs/work-orders/2026-10-16-social-metadata-and-page-identity.md)
(W09 there: derived Open Graph and X tags, the `social` field, the landing
marker, optional JSON-LD). Everything else is postponed here, with no
priority among the items and no implementation owner until pickup:

1. The unindexed pages. The Search Console review of 2026-10-16 found 25
   pages indexed and 35 not, several with "temporary processing error" on
   ordinary pages such as `/docs/current/sessions/what-persists/`. Diagnose,
   re-request indexing, and set a re-check date; separate the versioned
   twins and the redirects that correctly point elsewhere from real errors.
2. The versioned twins. Older version pages are self-canonical by the
   contract's design, so a supported version page and its `current` copy
   compete for the same query. Decide whether a supported version page
   canonicalizes to `current`; a contract amendment if so.
3. The producer's companion to W09: delivered 2026-10-16 in PR #219, the
   `website:social` marker in `README.md`, the amendment to R-DOCS-003 and
   the pin at the website's `5dbfe49`, once the website shipped slices 1 to
   4 together. What remains here is the pass over every page's
   `description` for the search result it should earn.
4. Search intent per entry page: which queries each entry page should win,
   and the landing page's links into the documentation chosen for that.
   Content work on the producer side, owned by user-docs at pickup.
5. Measurement: a recurring Search Console reading, the Bing Webmaster
   submission the records never confirm, and a page-performance check,
   under or beside the website's W13 analytics item. The pages are light
   today: the landing page is 16 KB and answers in about 0.3 s.
6. Off-site presence: the repository's GitHub description and topics,
   listings, and where journal entries are posted. The owner's, outside
   both repositories' files.

Correct today and not items: language, viewport, one heading per page,
image alternative text, a 50-entry sitemap and a robots file naming it.

## Notification When A Host Bridge Is Not Granted

Opened: 2026-10-03, from the closure of the
[URL-opening bug record](../../bugs/devcapsule/2026-09-24-url-opening-without-browser-handler.md)
at the owner's ruling. A backlog entry, not a bug: the capsule behaves as
its denial says.

When a capsule has no `host-browser` grant and something asks to open a URL,
the user today gets nothing: `BROWSER` is unset and `xdg-open` finds no
handler. The owner wants this handled by the contained desktop's own
notification mechanism, a graphical notice that host-browser is not granted
and the one command that grants it, rather than by text on a terminal that
the click may not have come from. The contained desktop has no notification
daemon today (no `notify-send`, no daemon in the runtime image); the entry
includes choosing one frugal enough for the desktop the project keeps.
Likely owner: `contained-display`. Priority: `later`; no release target.

## File Locking Protocol

Opened: 2026-08-15

Release target: **undecided (V1 or V2)**

Context: on 2026-08-15 the product owner established that no workstream holds
exclusive editing rights over any file. Exclusivity applies only where a
documented locking protocol exists and is actually used. No such protocol
exists, so today nothing is exclusive.

That is the right default while work is sequential. Under genuine concurrency
it leaves a gap: two workstreams may edit the same file with no mechanism to
coordinate beyond ordinary Git conflict resolution.

A protocol would need to define at least:

- what may be locked, and at what granularity: a file, a directory, or a
  declared area such as a handoff or a requirements register;
- how a lock is taken, recorded, and made visible to another agent that only
  has the repository and no shared runtime;
- how long a lock survives, and how a lock left by an interrupted or abandoned
  session is detected and released without a human arbitrating every case;
- what an agent does when it needs a locked file, including whether it waits,
  proceeds and reconciles later, or escalates; and
- whether locks are advisory or enforced, given that nothing prevents an agent
  from simply editing the file.

Open question to settle before choosing a target: whether ordinary Git conflict
resolution plus clear workstream scoping is sufficient in practice, making a
lock protocol unnecessary complexity. Deciding that it is sufficient is a valid
outcome and should be recorded rather than left implicit.

Related: `WORKFLOW.md` rule 11 currently states a narrower exclusivity for
another workstream's WIP directory and recovery state. Whether that is a
carve-out or a contradiction should be reconciled by `workflow-improvements`
independently of this item, since readers need an answer now.

## Dissolved Stage 7 Items

Opened: 2026-08-27, when the product owner judged `recursive-e2e`'s pending
Stage 7 not consequential enough to gate that workstream's conclusion and
directed its identified items here as decisions to be made, not work already
scheduled. Each leaves this backlog when it gains a release target and an
owner, or a recorded rejection.

### External-Resource Ownership And Reaping

Closed: 2026-10-09, at the owner's direction. No further action is required
on the standalone Stage 7 resource-convention request. Its requester was
archived and the old plan no longer describes current development. Remove
this request from the active decision agenda; do not recreate it as later work.

Maintenance's concrete cleanup defects and its current reuse/reaping work
remain independently owned and tracked. This closure neither resolves those
bugs nor authorizes deleting retained host resources. The persistent-diagnostics
proposal of 2026-10-08 arose from a separate noVNC incident and is not part of
this retired Stage 7 request.

### Retained-Successor Evidence Disposal

Release target: **undecided; cheap either way**

Two exited successor containers (`b2093d85…` and `482c34f2…` runs) and their
run roots remain on the owner's host under a do-not-delete constraint that
existed for Stage 7's benefit. With Stage 7 dissolved, decide when to release
the constraint and remove them — by their exact GUID-derived names, which is
itself a small live exercise of the cleanup rule.

### Successor Persistence And Stability Proof

Release target: **undecided; likely reject**

The bounded second-inspection stability result was never produced: both
retained successors exited while paused, so it needs a fresh launch. Its value
was recursive-dogfood assurance, not adopter-facing persistence — project
state and home persistence are separately covered. Recording rejection is a
valid outcome.

### Non-Interactive Runs

Release target: **undecided — but the product owner ruled on 2026-08-23 that
this blocks V1**; the entry must not bury that ruling.

Delivered to this workstream's intake on 2026-08-27 (written 2026-08-23,
delayed by the outbox failure). Unattended operation has no owner, no
requirement, and no defined behavior for authorization and acquisition
acknowledgements. The decisions it needs are recorded in the intake item:
support versus explicit refusal in V1, the pre-recorded authorization shape if
supported, whether it becomes a requirement and a ledger row, and which
workstream carries it.

**Mechanism decided 2026-08-29.** The product owner ratified the capsule
supervisor for V1 (ledger row *Capsule Supervisor And Multi-IDE Sessions*):
non-interactive runs are the supervisor with no GUI children, so the
"support versus refusal" question is answered — supported, in V1. The owning
workstream is settled 2026-08-30: `contained-display` carries the supervisor
core and with it this item's design work. Still open from the list above: the
pre-recorded authorization and acquisition acknowledgement shape, and the
requirement record.

### Workflow Invariants As Pre-Commit Hooks

Release target: undecided. Owner: none yet, per the 2026-08-29 unowned-rows
ruling; assigned at pickup.

Directed by the product owner on 2026-08-29 while dispositioning the
intake-staleness item. The workflow's mechanical invariants — the intake
exclusive-or, append-only disposition logs, intake naming, the WIP carve-out,
registry agreement — become a `devcapsule workflow verify` check exposed to
adopters as opt-in `pre-commit` local hooks seeded by bootstrap, and to this
repository as a Nox gate session. Design fleshed out in
[the 2026-08-29 note](2026-08-29-workflow-invariants-pre-commit.md). Shares
its delivery path with the initialization-tooling entry below; whichever
workstream picks up one should expect the other.

### Multiple-Stream Initialization Tooling

Release target: undecided. Owner: none yet, per the 2026-08-29 unowned-rows
ruling; assigned at pickup.

Recorded 2026-08-30 at the product owner's direction, dispositioning the
2026-08-16 intake item from `workflow-improvements`. The owner asked that the
reserved `project-management` workstream be "initiated by the tooling on all
devcapsule projects"; the protocol half is done, but the only path that seeds
workflow files today is `devcapsule bootstrap project` running
`docker4pycharm/bootstrap-project.sh`, a script predating the multiple-stream
workflow entirely. The work is product implementation in `devcapsule-src`:
teach the bootstrap to initialize multiple-stream mode, including the reserved
workstream, per `WORKFLOW.md`'s *Initializing Multiple-Stream Mode*. Shares
its delivery path with the pre-commit invariants entry above — the same
bootstrap seeds both.

### Silent Empty Bind-Source Failure

Release target: V1, per the ledger's at-risk homes. Owner: none yet; assigned
at pickup.

At-risk item 6 of the readiness assessment, homed here 2026-08-30. Docker
invents an empty directory when a bind source is missing — a data-shaped
silent failure that recurred twice in one recorded session. Make it
structurally loud once: launches must verify bind sources exist and refuse
with an actionable message rather than let Docker fabricate them.

### Submodule Pointer Publication Ordering

Release target: V1, per the ledger's at-risk homes. Owner: none yet;
`sample-projects` is the natural owner at pickup, since its submodules are
where the failure bites.

At-risk item 7 of the readiness assessment, homed here 2026-08-30. `main`
can currently advertise a submodule pointer that no clone resolves, breaking
the first command an adopter runs. Specify and check the publication order:
the submodule's commit is publicly reachable before the superproject pointer
lands.
