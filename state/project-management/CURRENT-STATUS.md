# Workstream Current Status: Project Management

Mnemonic: `project-management`

Start date: 2026-08-09

State: active 2026-09-28; 0.2.15 final verified on `main`; owner dogfooding 0.2.15 in this capsule; 0.2.16 proposal awaiting owner decisions; 25 undecided intake items

Definition read: WORKFLOW.md@89c7023c443d, WORKFLOW-LOCAL.md@5b4a80ae583e

Branch association: `ws-project-management/coordination` (renamed from `project-management/coordination` by the owner-directed migration on `main`, commit `4827ade`)

Integration target: `main`

Delivery method: pull request

Requirements: `R-PRODUCT-003`, `R-PRODUCT-005`, `R-PRODUCT-006`

## Goal

Own project-wide priorities, sequencing, cross-workstream dependencies and
lifecycle decisions. This reserved workstream remains open for the lifetime of
multiple-stream mode. Its immutable 2026-08-09 start predates the general rule;
the adoption exception remains recorded in the mainline registry.

## Current State

Resumed 2026-09-28 in this checkout, now a released-0.2.15 capsule with the
shipped `devcapsule0` on PATH and the development CLI in the source tree's
virtualenv; workflow commands ran through the development CLI per the local
rule. Maintenance's publication notice was taken and acknowledged: **0.2.15
is final and verified from the record**, tag `v0.2.15` at accepted RC1 source
`a15ff8b`, acceptance record `releases/v0.2.15.json` on `main` (ancestry
method, baseline `abb785d`), release branch merged through PRs #145, #146
and #148, `main` reopened at 0.2.16.dev0 by PR #149 at `6980b60`. That
closes the pause note's verification step and the proposal's candidate C2:
0.2.15's additions are on `main`, so the 0.2.16 cut can be ordinary.
Synchronized by merging `main` at `6980b60`: the definition changed only in
its version line (0.2.16.dev0); two mechanical conflicts, this workstream's
registry row kept beside maintenance's new row, and the 0.2.15 work order
taking `main`'s implemented status. The owner's note that the pace has
accelerated was checked against `main`: non-merge commits per week rose
from about 35 in early August to about 90 through mid-September and about
135-140 in the last two weeks; merged pull requests from 5-8 to 24, 53 and
35; eight final releases since 2026-08-26, the last two days apart; since
2026-09-19, 17 bug records opened and 19 closed. Activity counts, not value.

Resumed 2026-09-27 at the owner's explicit direction, in this checkout,
to consider what is reasonable for 0.2.16 and plan it, while 0.2.15 is
still being implemented under maintenance in a different checkout. This
supersedes the pause note's ordering "after 0.2.15 is released"; the owner
chose to plan ahead, not the agent. The pause note's first step, verifying
the published 0.2.15 artifact and maintenance's acceptance record, stays
pending until that release is final. Fast-forwarded to the pushed branch
tip; zero commits behind `main`; definition and local workflow unchanged
since the last read, so nothing to synchronize. One mail item taken: the
owner's standing agent-freshness practice, acknowledged below. The
[0.2.16 planning proposal](2026-09-27-0216-release-planning.md) maps the
0.2.15 leftovers, what `main` already carries, the bug inventory and the
intake queue to nineteen candidates with a recommended scope and seven
owner decisions. No intake item other than the freshness practice is
dispositioned by the proposal; each is decided when its owner decision
lands. Documentation only; no build, container or source change.

Previous pause note follows.

Paused 2026-09-27 at the owner's explicit direction until 0.2.15 is released.
All three release-scope messages are verified in maintenance's mailbox;
implementation, validation and release now move to that workstream under the
same owner's instruction. The final work-order revision is `d34fb06`; its
source is available on the pushed project-management branch. The two older
brief observations were sent for triage to workflow-improvements as
`2026-09-27-project-management-brief-observations.md` at `5286a7bfbeb4`.
No source work or user edits remain in this checkout. The 25 pre-existing
intake items stay queued until resumption; no session record was requested.


Resumed 2026-09-27 for the owner's release-scope decision in a clean checkout
at `/tmp/devcapsule-project-management`, on the registered branch. The original
checkout remains on `release-0.2.14` with its two pre-existing document edits
and dirty website submodule untouched. This is initial selection of the
explicitly requested workstream, not resumption of obsolete local release
state. Main was merged through `0cb4b0a`: nine commits behind, current rules
unchanged, new release evidence relevant to this decision. Mechanical conflicts
kept main's fixed init-bug record and added bug-index entries. No open bug
owned by project-management was found. No waiting mail; 25 intake items remain.

The owner approved persistent `/opt/xtras` and read-only `project info` for
0.2.15, and accepted deferring the general in-capsule project-command guard
bug. The [accepted work order](../../work-orders/2026-09-27-project-environment-discovery.md)
is the current scope and acceptance contract. Maintenance is the release
driver for these three bounded slices; its general scope is not expanded.
The owner subsequently approved Antigravity's `toolPermission` default as
`always-proceed` in `$HOME/.gemini/antigravity-cli/settings.json`, completing
the initial three-slice scope. The owner then explicitly extended the agent
defaults slice to Claude: seed minimal user settings before its first launch,
with `permissions.defaultMode` set to `bypassPermissions`. Official vendor
docs permit pre-creating the file. Selected-version interactive acceptance
must establish first-use notice behavior and preservation of Claude-written
state; do not claim a fresh-launch test from documentation alone. New state
and a missing key in managed settings get the default; explicit choices and unrelated settings are preserved. Codex's
v0.2.14 seed already sets approvals to never and sandbox to danger-full-access;
existing configurations are not overwritten. Branch is current with main;
workflow definitions unchanged. No runtime implementation or new candidate
acceptance is claimed here.

Earlier coordination history follows; the 2026-09-27 decision supersedes the
fix-only restriction wherever it appears below.

The owner explicitly returned this checkout from maintenance on 2026-09-22.
Maintenance was paused, committed, pushed and published first, with its bug
triage preserved. PR #125 integrated the run-image replacement at `f0d6901`;
PR #128 integrated model-first Codex attribution and the owner-validated bug
closure at `ca3f1d3`. Both deliveries were verified through fetched main, not
inferred from the owner's report alone. The legacy PyCharm network-default
bug remains with maintenance; the coordination data-loss fix remains with
workflow-improvements. The recovered mail and source patch are historical
custody evidence, not outstanding delivery tasks.

Synchronized with main through `2c1a503` (PR #129), including the coordination
nested-directory and claim-preservation repair. Existing project-management
blog instructions and design documents remain on this branch. The legacy
branch remains registered; use explicit `--workstream project-management`.

The owner selected 0.2.14 release readiness, then challenged the generic
merge-only rule. The 2026-09-22 decision is now in `WORKFLOW-LOCAL.md` and the
canonical release runbook: main stays open; merge when suitable, otherwise
cherry-pick, adapt the correction, or establish that main is unaffected.
Record the inspected revisions and proportionate evidence with the bug.
Method selection needs no further owner approval. Git topology alone is not
proof that the correction works. The same judgment permits selective transfer
of a main-first fix onto the release line.

The decision changes propagation methods. Existing before-each-candidate timing
is retained; the optional timing question has not received a separate owner
decision. An unresolved main bug still needs an explicit owner decision before
deferral. The existing candidate gate accepts ancestry/patch equivalence;
adapted or unaffected-main outcomes use its existing evidence record under the
standing owner direction. No release gate implementation changed.

Acknowledged the 2026-09-16 runbook-alignment intake: the guide now follows
current release branch selection, driver and version rules, with the owner's
new propagation rule superseding the intake's merge-only instruction. The
remaining 20 intake items are undecided; the maintenance-release and branch
migration items still need their other requested coordination decisions.
Generic-rule revision was delivered to workflow-improvements as
`2026-09-22-project-management-release-fix-propagation.md` on coordination commit
`5d47a901d22d`; that includes clarifying routing for selective mainline delivery.
No other workstream's records or generic workflow source were edited.

## Release 0.2.15 (initial decision 2026-09-26; expanded 2026-09-27)

The owner's first-session attempt with the released 0.2.14 launcher hit a
show stopper: `project init` discards every interactive answer when a
`--authorize` name is unknown, filed as
[the init bug](../../bugs/devcapsule/2026-09-26-init-discards-answers-on-late-authorize-validation.md),
owner maintenance, severity blocking, target 0.2.15. The owner ruled the same
day: no fourth version number; fix it and release 0.2.15. This decides the
first ask of maintenance's 0.2.15 plan:

- Maintenance cut 0.2.15 from `v0.2.14` under the owner's fix-only ruling;
  the published maintenance state records that cut and the passing local gate.
  On 2026-09-27 the owner added `/opt/xtras` and `project info` via the linked
  work order. The init fix and all three additions require candidate acceptance.
- Owner ruling, same day: everything else named for 0.2.15 moves to
  0.2.16. That is the cleanup and optimization list from the 2026-09-25
  plan, its five candidates, the IDE-surface wish (maintenance estimates
  only IntelliJ fits a week and recommends none), and the release-notes
  artifact proposal. 0.2.16 is not yet registered; its driver and scope
  are the next planning decision.

Delivered to maintenance by mail on 2026-09-26; the acknowledgement is in
the decision log.

## Claim Test Quarantine (2026-09-22)

The owner reported inconsistent CI results at one revision for the claim
lifecycle test. A disposable-local-remote probe confirmed the assertion depends
on two real-clock calls remaining in the same second. On explicit owner
instruction, this release-readiness slice marks the existing test non-strict
xfail without changing its assertions or runtime behavior. The owner rejected
a quick fix and requested review of the testing approach. The confirmed minor
bug is `engineering-docs/bugs/devcapsule/2026-09-22-workflow-claim-test-flakiness.md`,
owned by workflow-improvements, with no release target yet. Its scope is the
claim/renewal/expiry contract and reliable tests; the combined test's assertion
coverage is temporarily quarantined. This adds one bug to the earlier inventory
(19 nonterminal records now). The full build passed: 1,044 tests passed,
18 deselected, one existing xfail and this test XPASS; mypy and nine packaged
checks passed. The owner-requested marker is the only test/source change;
no quick repair was made. Bug/design handoff delivered by coordination mail
`2026-09-22-project-management-claim-test-design.md` at `f263535437cb`.
The marker and bug await owner PR integration.

## Release 0.2.16 Planning (2026-09-27)

The [proposal](2026-09-27-0216-release-planning.md) recommends 0.2.16 as
"what `main` already carries, made releasable, plus the bounded cleanup
0.2.15 set aside": acceptance of the base-contract naming already on
`main`, 0.2.15's additions forward-ported before the cut, the standing
agent freshness review, release notes as a gated artifact, the named
build-context fix, the in-capsule guard bug, triage of the seven
untargeted maintenance bugs, the two first-session UX fixes as bugs, and
the first-session guide refresh. The checkout-naming default and an
IntelliJ surface are the owner's options; the upgrade experience,
mycodespace and the legacy L1-L13 capabilities are decisions, not 0.2.16
implementation. Driver recommended: maintenance, cutting from `main` as an
ordinary release. Estimate: one to two weeks of pair time after 0.2.15 is
final, IntelliJ adding days. Nothing is registered until the owner decides.

## Planned Next Step

Collect the owner's 0.2.15 dogfooding feedback as it arrives: defects go
to bug records owned by maintenance with their evidence, not into this
status. Then put the seven decisions in the proposal to the owner. On each decision:
register 0.2.16 in the registry with its driver and scope, deliver the
scope to the driver by mail as a work order, file the two first-session
UX bug records with target 0.2.16, and disposition the intake items the
decision settles. Independently of the decisions, add the *Agent
Freshness Review* section to the release runbook, the task acknowledged
from maintenance's 2026-09-27 item, and reference it from preparation and
final acceptance. The 0.2.15 verification step is done (see *Current State*).

Superseded 2026-09-27 by the owner's direction to plan ahead: after 0.2.15
is released and the owner resumes this workstream, verify the published
final artifact and maintenance acceptance record, then register 0.2.16
scope/driver and resume the coordination queue below.

Completed handoffs:

Maintenance received `2026-09-27-project-management-0215-xtras-info-scope.md`
at coordination commit `2e76c7989b32`, including the full work order. Next:
check its acknowledgement when reviewing release progress, then resume the
remaining coordination decisions below. Implementation and candidate validation
belong to maintenance; remain in project-management unless the owner explicitly
selects that workstream. The third addition is Antigravity
`toolPermission: "always-proceed"`; its supplemental maintenance handoff
`2026-09-27-project-management-0215-antigravity-default.md` was delivered at
coordination commit `ebf07f17ef87`. Claude is now also in the agent-defaults
slice; `2026-09-27-project-management-0215-claude-default.md` was delivered
at coordination commit `0b272657b687`. Check both acknowledgements. No further
slice is selected.

Previous planning context (2026-09-26):

Resumed 2026-09-26 on `ws-project-management/coordination`, synchronized with
`main` at `f4949aa` (v0.2.14 published 2026-09-25; `main` reopened at
0.2.15.dev0). The definition text is unchanged since the last read apart from
its version line; `WORKFLOW-LOCAL.md` gained the dogfooding CLI selection,
local launch networking and the deferred rename deadline, all read.

Six mailed items were taken on resume and joined the 20 already in `intake/`;
the 0.2.15 plan is decided, 25 remain. The first decisions to put to the owner, in order:

1. Done 2026-09-26: 0.2.15 registered with maintenance as driver, the
   blocking init bug initially its only content (expanded 2026-09-27); see *Release 0.2.15* above. The rest
   of that plan is 0.2.16 material: register 0.2.16 with the owner once
   0.2.15 is out, sequencing the cleanup candidates and ruling on surfaces.
2. Release notes as a release artifact
   (`2026-09-26-maintenance-release-notes-artifact.md`): adopt into the
   runbook and the 0.2.15 plan or not.
3. The mycodespace design note and checkout-naming default
   (`2026-09-25-maintenance-mycodespace-and-checkout-naming.md`).
4. The V1 gate on legacy launch capabilities
   (`2026-09-22-maintenance-v1-legacy-launch-capabilities.md`): acknowledge
   into the V1 scope ledger.
5. The two branch-migration items from 2026-09-22 are overtaken by the
   migration `main` carried on 2026-09-25; decide them as acknowledged with
   the remaining cleanup named.

Then the 20 older intake items, oldest first, and the queued V1
functionality/WOW discussion. Legacy branch migration is done for the active
workstreams; `eclipse-surface` has no branch yet.

The previous planned next step, the handoff of the 0.2.14 cut to maintenance,
completed: PR #131 was the baseline, maintenance cut and published 0.2.14.

## Validation And External State

2026-09-27 planning checkpoint: documentation only. Relative links in the
changed documents checked; no build run, since no source or test changed
and the developer virtualenv is absent in this checkout. Facts in the
proposal were read from `origin/main` at `0cb4b0a`, `origin/release-0.2.15`
at `8028a11` and the live coordination state, not from this checkout's
stale local `main`. The stray edit found on arrival, a typed "Will" at the
top of the legacy launch work order on `release-0.2.15`, was discarded
before switching; nothing else was dirty. Git author verified as Costin
Cozianu; this session's model is Claude Fable 5.1.

2026-09-27 coordination checkpoint, including the Antigravity and Claude supplements:
diff whitespace and changed-document relative links checked. Codex defaults
were verified in v0.2.14 source and the current component/seed implementation.
No live agent settings were edited. The required `.venv/bin/python -m nox -s build` could
not start in the clean checkout because its developer virtualenv is absent
(exit 127). No environment provisioned for this documentation-only handoff;
no new build pass or implementation validation claimed. Earlier build results
below belong to their recorded checkpoints. The original checkout and website
edits remain untouched. Git author identity was verified as Costin Cozianu.


Release-workspace setup changes documentation only; relative links, all 19 bug
rows against committed metadata, and whitespace were checked. Reuse the full
build result recorded above for the unchanged runtime/test tree. A pre-existing
working-tree edit changed the Codium sudo bug's opening delimiter from `---`
to `--`. Before switching workstreams, preserved its exact diff in
`.git/codex-preserved-codium-sudo-edit.patch` and restored the committed file
for a clean switch. The edit can be recovered with `git apply` of that patch;
it has not been incorporated into release source.


The required `.venv/bin/python -m nox -s build` passed on the synchronized
source: 1,045 tests, 18 deselected, one existing xfail, mypy across 167 source
files, shell/CLI checks, local PEX build/smoke and nine packaged checks. Reviewed
the guide against the release gate implementation and checked whitespace. The
working-tree build produced the local validation artifact; no release artifact
or downloaded-candidate acceptance is claimed by these documentation changes.

The Git author is Costin Cozianu and this session's recorded model is
`gpt-6-astra`; new authored commits use the model-first Codex trailer. Git uses
SSH; all GitHub PR and publication operations remain owner-operated via UI.
Coordination commands ran from the repository root with an absolute `--project`;
the nested-directory repair is now on main, but these commands do not constitute
its next real nested-directory acceptance run. No containers, host settings or
submodules were changed.

## Open Threads

- Owner finding 2026-09-28, diagnosed, no fix chosen: the website at
  devcapsule.mycodespace.ai was last published 2026-09-21 and still pins the
  first-session guide to v0.2.12, although 0.2.14 and 0.2.15 have shipped.
  Three layers: the guide on `main` itself still says v0.2.12, so a republish
  alone would not help; `docs/versions.yaml`, which R-DOCS-003 calls
  authoritative, does not exist on `main`; and publication is two manual
  Actions runs that no runbook step names. Decisions are the owner's: whether
  documentation refresh and website publication become release gates, and
  which workstream owns each.
- Awaiting the human: the seven 0.2.16 decisions in the proposal, chiefly
  scope, driver, IntelliJ in or out, and the release-notes artifact. The
  registration waits on them; the runbook freshness section does not.
- Awaiting the owner's 0.2.15 dogfooding verdict, which may add bug
  records to the 0.2.16 triage candidate C9 or change the scope.
- Weighed and unresolved: whether IntelliJ needs a new `ide-surfaces`
  workstream or fits a rescoped `eclipse-surface`; whether C7, choosing a
  newer recommended base from `config`, is left with anything after the
  base-contract change. The upgrade experience is deliberately kept out of
  0.2.16 as implementation; a parallel design slice is proposed instead.
- Observed, not owned here: the website-link bug still targets shipped
  0.2.14 and needs its owner's retarget; `[workflow] version` in the
  declaration reads 0.2.14.dev0 while the definition's frontmatter reads
  0.2.15.dev0, a doctor-class finding for workflow-improvements if it recurs.
- Handed off earlier: init fix plus xtras, project info and Claude/Antigravity
  defaults to maintenance; two brief observations to workflow-improvements.
- Preserved separately: original checkout's release-document and website edits;
  historical host settings on `project-management/local-host-settings-20260915`.
- Deliberately not preserved: no transcript/session record or disposable builds.

## Workstream Document Index

- [0.2.16 planning proposal](2026-09-27-0216-release-planning.md): candidates, recommended scope, driver and the owner decisions; proposed 2026-09-27.
- [0.2.15 environment discovery work order](../../work-orders/2026-09-27-project-environment-discovery.md): approved xtras/info/agent-defaults scope, guard deferral and acceptance checks.

- [0.2.14 release overview](../../releases/v0.2.14/README.md): maintained release checklist and evidence.
- [0.2.14 bug triage](../../releases/v0.2.14/bugs.md): release dispositions and next actions; canonical bug records remain linked.

- [Prior coordination status](2026-09-22-record-prior-coordination-status.md): full historical handoff, decisions, open-thread context and external-state claims; read when reconciling a specific prior topic.
- [Intake decisions](intake-dispositions.md): append-only outcomes; `intake/` contains the 25 pending items.

- [Diagnostic print-command and run-image retirement](2026-09-21-design-editable-project-launch.md): accepted simplified contract and maintenance implementation scope.
- [Design issue: V1 completeness and the WOW experience](2026-09-19-v1-wow-functionality-areas.md)
- [Why try DevCapsule? — promoted to the project README](../../../README.md)
- [Portfolio checkpoint 2026-08-15](2026-08-15-portfolio-checkpoint.md)
- [Portfolio checkpoint 2026-08-16](2026-08-16-portfolio-checkpoint.md)
- [V1 readiness assessment 2026-08-16](2026-08-16-v1-readiness-assessment.md)
- [V1 scope ledger](v1-scope-ledger.md)
- [Competitive comparison: promoted research
  (refreshed 2026-09-12)](../../design-notes/devcapsule/competitive-comparison.md)
- [Display transport options and clipboard policy
  2026-08-19](2026-08-19-display-transport-options.md)
- [The workflow versus Jira and GitHub Issues
  2026-08-19](2026-08-19-workflow-versus-issue-trackers.md)
- [Coordination backlog](coordination-backlog.md)
