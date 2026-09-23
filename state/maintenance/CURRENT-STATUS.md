# Workstream Current Status: Maintenance

Mnemonic: `maintenance`

Start date: 2026-09-18

State: active; releasing 0.2.14; RC0 public; legacy PyCharm launch integrated; RC0 ready for owner testing

Definition read: WORKFLOW.md@bc1937f188ca, WORKFLOW-LOCAL.md@77b593f70215

Integration target: `main`

Delivery method: pull request; agent pushes the branch, owner opens and merges on GitHub

Branch association: `release-0.2.14`

Requirements: `R-PRODUCT-006`, `R-COMPAT-001`, `R-PRODUCT-002`

## Goal

Own defects no open workstream covers and drive maintenance releases. This
reserved workstream remains open for the lifetime of multiple-stream mode.
Its 2026-09-18 start is the recorded adoption exception.

## Current State

Owner-authorized retirement of `pycharm run` is implemented on the release
branch. The old adapter and CLI-only option helpers are gone; old invocations
fail before launch/state preparation and are absent from help. Shared project
launch and the image utilities remain. User guidance, diagnostics and packaged
smokes reflect the retirement. This changes source after RC0 and needs
the next immutable candidate. PR #133 integrated commit `1f425f3` at
`c8ab2d0`; ancestry was verified against fetched main on 2026-09-23.

Published `v0.2.14-rc0` at `d078b879469c1790647e32db75005d0fa4369b27`, already
integrated through PR #132 at `e50b9f1`. Tag push was verified through remote
refs; public PEX, checksum and manifest were downloaded without credentials.
Checksum, version 0.2.14rc0, tag mnemonic and exact source identity agree.
The downloaded executable passed clean-machine validation with no Python or
network. Full evidence, artifact locations and the acceptance checklist are in
[release work](../../releases/v0.2.14/README.md).

The owner explicitly deferred legacy branch renames through 0.2.14 publication,
before substantive work on the next release. WORKFLOW-LOCAL.md records this;
project-management received `2026-09-22-maintenance-rename-deadline-deferred.md`
on coordination at `4013fca06a54`, superseding the earlier pre-RC0 deadline.
The owner says known bugs do not prevent publication on bug grounds; fix or
verify a selected few and validate major end-user journeys before final acceptance.

Retired the two old codium_with_claude option-parity and ambient-sudo records:
the exact candidate lacks the old command module, launcher and entrypoint, and
both local and downloaded RC0 reject the command. This implements the saved
triage recommendation; it does not claim complete VSCodium acceptance. The
[working bug table](../../releases/v0.2.14/bugs.md) retains all 19 rows, now
14 open, two closed and three retired. On 2026-09-22 the owner accepted closure
of the upgrade-recovery and configuration-contract bugs; their records now
link the owner/graphical acceptance and verified PR #117 integration. No
runtime code changed during those earlier record updates. The subsequent
legacy-network retirement now includes the command-removal implementation.

## Planned Next Step

A single entry point now supports existing-project sessions:
`smoke/runner.py launch --project PATH`, followed by `resume`, `report` and
explicit actor `note` records. It verifies exact RC0 and captures process and
container facts without promoting them into a graphical PASS. The original website observation lacked candidate details; the subsequent
runner sessions establish exact RC0 startup and file/IDE resume evidence.
Owner confirmed the website VSCodium session works. Runner attempts 2 and 3
finished with exit 0, container absent and no monitor errors; owner confirmed
the S10 file/IDE resume checklist. `launch` and `resume` now accept a per-session
`--network host|bridge` override using the product authorization grammar. Next:
continue remaining campaign checks; agent continuation is still untested.

The owner requested an engineering test specification before further campaign
work: enumerate stories, distinguish validation prerequisites from reused data,
state feature promises/preconditions/postconditions, and assign each action to
an agent or program. The [21-story specification](../../releases/v0.2.14/smoke/stories.md)
now does that. Fixed prompt answers are automated both through an actual terminal
and through unattended flags. S02/S03 and S17 (exact preservation of unrelated
coordination blobs) pass against downloaded RC0, with durable JSON evidence.
Fresh and all three public sample configurations complete unattended. Whole
GUI/upgrade/service stories are not yet implemented or passed; continue the
runner implementation from the story table, and establish desktop-control
tooling for the assigned graphical steps. Do not transfer unfinished automation
to the human. Personal provider login/MFA and release judgment remain owner acts.
The retirement is integrated;
publish RC1 when the owner is ready to test that change. RC0 still contains
the old command; do not move its tag. No base rebuild is needed: the existing
local Ubuntu recipe-9 image and published RC0 executable were rechecked on
2026-09-23, and base build inputs are unchanged. Release refs are not rebased;
main has no workflow-definition or devcapsule-src difference from this branch.

The owner requested and received a permanent
[V1-blocking legacy capability work item](../../work-orders/2026-09-22-legacy-launch-capability-disposition.md).
It preserves the full inventory, existing project-run equivalents and the
undecided image-oriented/non-DevCapsule-directory alternative. Project-management
is to register the owner's V1 gate and sequence future-release decisions and
implementation; this is not a new 0.2.14 implementation commitment.
Delivered the complete work item by coordination mail
`2026-09-22-maintenance-v1-legacy-launch-capabilities.md` at `5df12452fba6`;
project-management's acknowledgement/ledger update remains pending. Links,
all 13 inventory rows and the permanent documentation index were checked.

The two owner-approved configuration closures are applied. The networking bug
was marked retired before removal as requested, and its command is now removed.
Thirteen rows remain undecided in the [release bug table](../../releases/v0.2.14/bugs.md),
including eight targeted verifications and five deferrals. Other records still
have independent scope: shared image rendering, modern PyCharm behavior,
project display policy, and resource lifecycle do not disappear with the CLI.

Owner deferred the confirmed multiline execution-rendering bug for 0.2.14
unless it recurs during the release E2E campaign. Watch for that recurrence
during acceptance and reconsider the deferral if observed. After this release,
the accepted follow-up is a clean redesign of component image composition
around documented, unit-testable contracts; the bug and release table record
the scope. The release branch remains unsynchronized as required for release refs;
the command removal, unlike the earlier records-only decisions, needs a new candidate.

Use downloaded RC0 for the release overview's end-user acceptance journeys:
fresh project, predecessor upgrade/recovery, IDE/agent work and resume,
graphical/login behavior, diagnostic command and isolated coordination scenario.
Pick further bugs from the table, fix, verify obsolete, or explicitly defer.
Capture the actual platform/surface/agent and user-visible outcome. Neither
unit coverage nor executable portability alone completes release acceptance.
New source fixes require the next immutable candidate and a main disposition.
Only after owner acceptance of an exact candidate prepare the final JSON/tag.

## Validation And External State

Runner network option: `--network host` or `--network bridge` on launch/resume
maps to `project run --authorize network VALUE` for that invocation only.
Omitting the option uses saved configuration, not the previous override.
Requested override is saved with each attempt; Docker inspection already
records actual network mode. Existing run records remain readable. No new
container was started solely to test argument forwarding. The eight focused
runner tests pass, including both override values and omission behavior.
Full `nox -s build` passed (source tests, type checks, PEX smokes and nine
packaged integrations); log `/tmp/maintenance-rc0-network-runner-build.log`.
The release branch was not rebased; workflow definition is unchanged.

Website run (2026-09-23): published RC0 passed its checksum gate and
launched VSCodium from this capsule through the host Docker daemon. Run directory:
`devcapsule-src/dist/rc0-runs/session-7a4dbc068f58`; container
`rc0-runner-7a4dbc068f58`; tool PTY session `73149` (now finished).
Attempt 1 failed with exit 2 before creating a container: local resolution was
missing. `config resolve` exposed unanswered local choices. Applied the existing
campaign policy to this capsule's website checkout record: pinned base plus
Claude/Antigravity downloads accepted; host network/Docker/sudo/browser/X11
denied. Explicit resolve succeeded; website source/lock were not regenerated.
Attempt 2 reused the canonical Codium image, translated bind sources to host
paths, and reached contained-desktop readiness on host loopback port 52123.
The runner captured a running container, bridge network, read-only root and
non-privileged execution with no monitor errors. Terminal reports VSCodium
startup. Owner subsequently confirmed "This is working"; recorded as an S05
startup observation in run.json, without claiming specific editing/debugging
assertions. Attempt 2 ended at 23:17:56 UTC with launcher exit 0, container
absent and no monitor errors: PROCESS_CHECKS_PASSED. Owner subsequently
confirmed the file/IDE resume checklist; attempt 3 passed
exit/cleanup checks and its S10 human observation is saved. Agent-session
continuation remains untested. Token URL stays in the terminal/chat, not this record.
The launcher warned that this capsule lacks a global Git author identity;
no identity settings were changed. Existing full gate remains applicable:
this slice changed only launch configuration and records, not implementation.

Session runner (2026-09-23): seven focused stdlib tests passed, including
Docker errors versus absence, nonzero launch, no inferred graphical PASS,
configuration preservation, wrong candidate, changed daemon and concurrent
writers. `runner.py cli --run /tmp/rc0-stories-cli-only-20260923` passed S02,
S03 and S17 against downloaded RC0; attempt `evidence/cli-y6r9a2ve`.
No real GUI/container session was launched through the new wrapper.
The full required gate passed (1,046 tests, 18 deselected, one xfail, one
quarantined XPASS, type checks and nine packaged integrations), log
`/tmp/maintenance-rc0-session-runner-build.log`. No runtime code changed.
Fetched main and live coordination were inspected; mail was empty. Workflow
files are unchanged; the release branch was not synchronized or rebased.

Story automation (2026-09-23): `verify-cli.py` passed real terminal base
accept/decline, fixed creator/default-agent/host answers, missing-base refusal
and CLI remedy, prompted/batch semantic equivalence, and nine local-remote
coordination operations checking every path/blob plus exact staged mail bytes.
Saved evidence: [CLI validation](../../releases/v0.2.14/smoke/cli-validation.json).
Every attempt gets its own directory; S17 runs independently of failed init,
while S03 requires S02's choices.json. The first harness expectation incorrectly
rejected explicit denials; its correction and retained failure are documented.
The fixed configuration wrapper passed on fresh/TypeScript/trading/FastAPI
fixtures without stdin or human answers. CLI-only preparation also passed.
The required gate passed: 1,046 tests, 18 deselected, one existing xfail and
one quarantined XPASS, type checks and nine packaged integrations; log
`/tmp/maintenance-rc0-story-contracts-build.log`. No graphical/provider/service
acceptance was inferred. Shell syntax and documentation links were checked. The retained preview/launch
helpers now fail on Docker query errors instead of misreporting absence;
fault checks distinguish daemon error, missing container and present container.

RC0 smoke harness (2026-09-23): shell syntax, complete preparation with the
verified published PEX, exact public sample clones, fresh initialization,
resolution and configuration-wrapper roundtrip passed in isolated XDG state.
Refusal checks covered an existing run directory, invalid case/arguments and
a mismatched candidate checksum before CLI execution. Validation directory:
`/tmp/rc0-smoke-script-validation-20260923` (preparation/configuration only;
not a host-backed launch location). No IDE, service or provider campaign was
run while authoring these scripts; the generated result sheet remains NOT RUN.
The required `nox -s build` passed: 1,046 tests, 18 deselected, one existing
xfail and one quarantined XPASS, mypy and nine packaged checks. Log:
`/tmp/maintenance-rc0-smoke-scripts-build.log`. These are harness/repository
checks, not acceptance of the unrun graphical campaign.

Legacy-command removal: 115 focused checks passed, followed by successful
`nox -s build`: 1,046 tests, 18 deselected, one existing xfail and one
quarantined claim XPASS, mypy over 167 source files, source/PEX smokes and
nine packaged integrations. Log: `/tmp/maintenance-retire-pycharm-run-build.log`.
Direct built-PEX checks reject bare/help/legacy-option invocations, show only
retained utilities in PyCharm help, and create no checkout state. Source tests
also prove no launcher/subprocess call. Validated artifact:
`devcapsule-src/dist/devcapsule-local.pex`. The gate skipped revision-bearing
packaging due to checkout edits; no fresh Docker/GUI run was necessary for
this command removal, and no such acceptance is claimed. Main integration
is verified through PR #133; the next candidate remains pending. The pre-existing local bug-file edit
remains unstaged and is excluded from delivery.

Bug-combing review at `8e7cc21`: fetched main remains `e50b9f1`; PR #117 merge
`d2386bb` is in main and RC0. At that review runtime/test sources matched RC0. A CLI probe with
only the launcher substituted confirms legacy `pycharm run` still passes host
networking without an explicit choice. 243 focused existing checks passed;
the earlier image review passed 45. No Docker or provider acceptance was run
for this review. The release table distinguishes prior evidence from proposed
candidate checks, including the incomplete byte-preservation assertion in the
nested-directory regression. No branch synchronization or runtime change.

RC0's integration gate passed by mainline ancestry with zero missing commits.
Local RC0 PEX and Docker base were built from a disposable exact-tag worktree,
which was removed after the build; this checkout remains on release-0.2.14.
Nine packaged assertions/checks passed: eight in the first run, then the
identity check after using the harness's canonical artifact filename. No code
was changed to satisfy that filename check. Local and downloaded PEX each
passed the networkless/no-Python clean-machine check. The locally built base
retains tag devcapsule-base:0.2.14-rc0-local and is not published to a registry.

Prior full source gate: 1,044 passed, 18 deselected, one existing xfail and one
quarantined XPASS, mypy and packaged checks. RC0 has identical runtime/test
inputs. That gate describes RC0, not the subsequent removal. The old claim-test
xfail remains; the retirement has its own validation below.

GitHub PR/workflow UI operations stay with the owner; neither gh nor SSO is
available here. No credential probes or API operations were attempted. Public
asset downloads verify publication; no credentialed Actions-run inspection is
claimed. No final release or graphical/end-user acceptance is claimed yet.

## Open Threads

- Exact RC0 website startup and file/IDE resume now have owner confirmation.
  Do not extend that evidence to unperformed edit/debug or agent tasks.
- Website runner attempts 2/3 are complete: owner confirmed startup and
  file/IDE resume; automatic exit/cleanup checks passed. Agent continuation
  and detailed edit/debug assertions still need execution. Website submodule
  changes belong to the owner and were untouched.
- Owner rejected the earlier manual-heavy campaign. Stories now govern the
  work; do not describe all 21 as automated. Implement remaining machine steps;
  desktop-control tooling is absent here. No provider/GUI acceptance is claimed.
- A pre-existing single `c` insertion in the smoke README remains in the working
  tree and is excluded from the rewritten document's commit, like the earlier
  unrelated bug-file edit. Its intent was not inferred.

- Legacy launch capabilities now have an owner-directed V1 gate: decide what
  is already covered, migrate selected capabilities, design an image-oriented
  mode only if justified, or explicitly drop them. The work order preserves
  the findings; project-management owns scheduling and ledger registration.
- Owner review of the 13 remaining bug dispositions remains; the full rationale
  and grouped acceptance observations are in the release bug table. Review
  project-launch old-base/X11 scope before closure of the display exposure record;
  distinguish repaired formation boot behavior from remaining image cleanup.
- A pre-existing local edit in the legacy-network bug removes one word and
  leaves trailing whitespace. It was preserved verbatim and excluded from
  all agent commits. Agent-authored retirement notes in that same file are
  staged separately from the pre-existing edit.
- Image composition redesign is deferred beyond 0.2.14 unless the confirmed
  multiline-rendering defect recurs during the release E2E campaign; preserve
  its documented-contract and unit-testing scope when scheduling the work.
- RC0 is published; end-user acceptance and selected further bug dispositions remain.
- Project-management coordinates renames after 0.2.14 publication, before
  substantive next-release work. This no longer holds 0.2.14 candidates.
- Workflow-improvements owns the claim-test design repair and generic release
  propagation rule revision; the local owner exception already governs here.
- Preserve retired-outbox follow-up, configuration contracts/coverage limits,
  and historical host/blog acceptance gaps; no unrelated cleanup was done.
- The pre-existing Codium delimiter edit remains saved at
  `.git/codex-preserved-codium-sudo-edit.patch`; its intent was never inferred.
  The canonical bug record now records retirement, so review before applying it.
- No transcript/session record was requested; canonical decisions live in the
  release documents and bug records.

## Workstream Document Index

- [Legacy launch capability work item](../../work-orders/2026-09-22-legacy-launch-capability-disposition.md): future-release decisions and delivery, blocking V1.
- [Release overview](../../releases/v0.2.14/README.md): cut, candidates and acceptance checklist.
- [Release bug triage](../../releases/v0.2.14/bugs.md): maintained dispositions and evidence.
- [RC0 validation runner](../../releases/v0.2.14/smoke/README.md): executable coverage and exact candidate inputs.
- [RC0 validation stories](../../releases/v0.2.14/smoke/stories.md): dependency types, actors, contracts and remaining automation.

- [Attribution checkpoint](2026-09-22-record-commit-attribution.md): integrated authorship convention, owner acceptance and build evidence.

- [Run-image replacement checkpoint](2026-09-22-record-run-image-replacement.md): merged implementation, validation and coordination recovery evidence; open only for those details.
- [Prior checkpoint record](2026-09-21-record-maintenance-before-component-upgrades.md): historical implementation, tests and graphical evidence; open only for those details.
- [Proposed bug triage](2026-09-21-note-proposed-bug-triage.md): open on resuming triage; not applied.
- [Pre-V1 assessment](2026-09-21-note-pre-v1-adopter-and-contributor-case.md): positioning input and owner Windows correction.
- [Early-adopter blog](../../blog/2026-09-21-why-try-devcapsule-before-v1.md): merged article and editorial follow-up.
- [Upgrade recovery contract](upgrade-recovery-contract.md): scope of the merged recovery fix.
- [Configuration contract](configuration-contract.md): lifecycle requirements relevant to future changes.
- [Correctness/test map](configuration-correctness.md): implementation evidence and coverage limits.
- [Intake decisions](intake-dispositions.md): outcomes of received mail.
- `intake/`: no pending items; both project-management messages acknowledged in the decision log.
