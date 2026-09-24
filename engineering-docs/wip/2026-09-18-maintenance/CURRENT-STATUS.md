# Workstream Current Status: Maintenance

Mnemonic: `maintenance`

Start date: 2026-09-18

State: active; releasing 0.2.14; RC3 public and verified, all local proofs passed against the download; owner testing of RC2/RC3 and the configuration-inspection decision pending

Definition read: WORKFLOW.md@bc1937f188ca, WORKFLOW-LOCAL.md@5b4a80ae583e

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
The owner originally said known bugs did not prevent publication. On
2026-09-24 the missing runtime CLI became the first release blocker; fix and
validate it before resuming the remaining end-user journeys.

Retired the two old codium_with_claude option-parity and ambient-sudo records:
the exact candidate lacks the old command module, launcher and entrypoint, and
both local and downloaded RC0 reject the command. This implements the saved
triage recommendation; it does not claim complete VSCodium acceptance. The
[working bug table](../../releases/v0.2.14/bugs.md) now has 23 rows:
18 open (including the runtime CLI blocker), two closed and three retired. On 2026-09-22 the owner accepted closure
of the upgrade-recovery and configuration-contract bugs; their records now
link the owner/graphical acceptance and verified PR #117 integration. No
runtime code changed during those earlier record updates. The subsequent
legacy-network retirement now includes the command-removal implementation.

## Planned Next Step

RC2's backend run (36023910604) failed at "Verify pinned base availability
and runtime sessions": `docker build` of the disposable runtime image exited
1 after 42 seconds on the hosted runner, where the rc1 run had passed the
same step in 74 seconds with identical test code; the e2e helper discarded
the build's stderr, and the step log needs administrator rights. The local
reproduction against the same digest and PEX source passed. The owner ruled
that no test on hosted infrastructure runs Docker. Filed as a blocking bug
([record](../../bugs/devcapsule/2026-09-24-release-workflow-gated-on-docker-on-hosted-runner.md))
and fixed on this branch: the release workflow runs no Docker (both
clean-machine proofs, component-cache and runtime-session steps removed);
those proofs are local acceptance steps against the downloaded assets; the
e2e helpers now fail with the command's output; the operator guide,
DEVELOPING.md and the source README describe the new split.

Done since: PR #138 merged, `v0.2.14-rc3` tagged and published, assets and
all local proofs verified (see validation below). Next: the owner tests `config list`/`resolve` on this
repository with 0.2.12 and RC3 and the `devcapsule0` exception in a real
capsule. RC2's tag stays, without assets. The RC1 configuration-inspection
bug remains open for the owner's fix-or-defer call.

Owner-directed release steering resumed 2026-09-24 from this checkout. The
owner reported `project config list` and `config resolve` failing on a fresh
DevCapsule checkout with `runtime-effect must be one of: docker.memory-limit`.
Root cause, reproduced with the published executables: commit `658749f`
declared `runtime-effect = "devcapsule.command-name"` in this repository's
own manifest while adding it to the vocabulary; v0.2.12 and rc0 reject any
effect they do not know, so every released client failed on `main` and
`release-0.2.14`; rc1 accepts it. Filed as a blocking bug
([record](../../bugs/devcapsule/2026-09-24-released-launchers-reject-repository-manifest.md)),
then fixed on this branch: the value name `runtime.devcapsule-command` is
reserved and carries the effect without the attribute, unknown effects are
reported with the running version, the manifest drops the attribute, and a
guard test pins the repository manifest to the released vocabulary. Published
0.2.12 now lists and resolves the manifest. Full gate passed.

Next: the owner opens the PR from `release-0.2.14` to `main`. After the
merge, verify the candidate gate by ancestry, tag `v0.2.14-rc2` atomically
with the branch, download and verify the assets, and validate that RC2 applies
`devcapsule0` from the reserved name inside a real capsule. Then decide the
RC1 configuration-inspection bug with the owner: fix both causes on this
branch under maintenance, or defer. The receiving workstream is paused.

RC1 owner feedback: mostly works, except configuration inspection. Both
reported failures are confirmed; the [bug](../../bugs/devcapsule/2026-09-24-runtime-configuration-inspection-fails.md)
belongs to component-upgrades' runtime inspection contract, target 0.2.14.
Evidence delivered to component-upgrades by coordination mail
`2026-09-24-maintenance-rc1-runtime-configuration.md` at `dc91dbc8e484`.
Next: agree the release repair with the owner and receiving workstream.
No source fix or workstream switch was performed. Initial coordination claims
hit SSH authentication errors and a Git push hit a remote internal-server
error; mail delivery subsequently succeeded.


The runtime CLI blocker has a source fix and Docker regression evidence on
`release-0.2.14`. Normal capsules expose the shipped `devcapsule`; the owner
requested a saved configuration exception and this repository recommends
`runtime.devcapsule-command = "devcapsule0"`. That real command leaves the normal
name for development tooling; internal absolute-path calls retain the shipped
PEX. Explicit checkout values/omissions override ordinary recommendations.
Owner accepted the real recursive PyCharm/devcapsule0 session at `9cc0868`.
PR #136 integrated the release fixes; RC1 is tagged at `cec7a0c`.
Published RC1 assets are downloaded and checksum/version/source-verified.
The owner-requested local base is built and smoke-checked. Next: carry the
local PyCharm acceptance into exact-RC1 validation before closing the blocker.

The owner requested the installed-IDE reuse bug be filed first and its design
reviewed together before implementation. No release target or implementation
approach is approved. Review the linked bug when the owner resumes that topic;
do not start cache implementation or the broader composition redesign.
No live capsule or website source was patched. URL opening and non-blocking
workflow onboarding remain with their previously notified owners.

A single entry point now supports existing-project sessions:
`smoke/runner.py launch --project PATH`, followed by `resume`, `report` and
explicit actor `note` records. It verifies exact RC0 and captures process and
container facts without promoting them into a graphical PASS. The original website observation lacked candidate details; the subsequent
runner sessions establish exact RC0 startup and file/IDE resume evidence.
Owner confirmed the website VSCodium session works. Runner attempts 2 and 3
finished with exit 0, container absent and no monitor errors; owner confirmed
the S10 file/IDE resume checklist. `launch` and `resume` now accept a per-session
`--network host|bridge` override using the product authorization grammar. Next:
continue remaining campaign checks using `--network host` per local policy;
agent continuation is still untested. Owner verified host-network attempt 4.

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

RC3 local proofs (2026-09-24), against the verified download
`/opt/devcapsule-gate/rc3-published/devcapsule.pex` (SHA-256
`9a82ae7f91662f448ad180854e2cd43b14b6deca54c598d30440dd4a87ae4d43`), with
`DEVCAPSULE_PEX_UNDER_TEST`, `DEVCAPSULE_EXPECTED_BUILD_MNEMONIC=v0.2.14-rc3`
and `DEVCAPSULE_EXPECTED_RELEASE_VERSION=0.2.14rc3` exported, pytest scratch
on the overlay: packaging integration tests 9 passed; clean-machine proof
(`nox -s pex_clean_machine`, `docker run` without Python or network) passed;
component-cache reuse and launcher delivery 5 passed in 91 s; runtime image
on the manifest's single pinned base, the v0.2.12-rc5 digest, 1 passed in
28 s on a warm builder cache. Log `/opt/devcapsule-gate/rc3-local-proofs.log`;
its first packaging and clean-machine attempts failed only because the
release-version variable was not exported, and passed on rerun with it.
RC2 assets verified the same way: SHA-256
`eddf2cde00e07c8d7874c229283ff1a20f409400b5b7bbdcc9b5cc54dca8d3b1`,
version `0.2.14rc2`, source `a779295`, mainline integration.

RC3 tag (2026-09-24): the owner merged PR #138 (fetched main `7c0b5a2`
contains `997cd67`, zero unintegrated commits) and reported that a rerun of
rc2's failed run succeeded, which confirms the runner failure as flakiness.
`scripts/release-protocol.py v0.2.14-rc3` passed, record at
`/opt/devcapsule-gate/rc3-release-protocol.json`; annotated tag pushed
atomically with the branch, peeled commit `997cd67445b00c78da38f1a77c7f0622eaf5a0b3`.
A watcher downloads and verifies the rc2 and rc3 assets; the three local
Docker proofs against the rc3 download follow.

Docker-free release workflow (2026-09-24): workflow YAML parses; the two
edited e2e modules collect (six e2e tests, deselected as before) and pass
mypy; full `nox -s build` passed: 1064 tests, 20 deselected, one xfail, one
quarantined XPASS, mypy, PEX smokes and nine packaged integrations; log
`/opt/devcapsule-gate/no-docker-workflow-build.log`. Local
reproduction of rc2's failed step, `tests/e2e/test_runtime_image.py` with
`DEVCAPSULE_E2E_BASE_IMAGE` set to the v0.2.12-rc5 digest and the PEX built
from `8d005b3`: one passed in 608 seconds; log
`/opt/devcapsule-gate/rc2-runtime-image-repro.log`. Step timings from the
public jobs API: rc1 runtime-session step 74 s success; rc2 42 s failure;
rc2's component-cache Docker step 71 s success, so Docker itself worked on
that runner.

RC2 tag (2026-09-24): the owner merged the release PR; fetched main
`9e2396d` contains `8d005b3` and `a779295`, zero unintegrated commits.
`scripts/release-protocol.py v0.2.14-rc2` passed; record at
`/opt/devcapsule-gate/rc2-release-protocol.json`. Annotated tag pushed
atomically with the branch; remote tag object `4a02aa31d817`, peeled commit
`a779295d7343158d846df89d2d5da184548bfd1d`. Asset publication is the
workflow's; a watcher downloads and verifies the public assets when they
appear. No matrix or lock change: the default base remains the v0.2.12-rc5
digest pin, which carries no runtime (D-0009) and whose recipe is unchanged.

Local rc2 base (2026-09-24): built `devcapsule-base:0.2.14-rc2-local`, image
`sha256:64c8db54eac0bfbefa019c20777bc486abcad4bc5b0ff420d229f79a5f50718a`,
recipe `ubuntu-24.04@9`, host-network build, root `ubuntu:24.04`, by a
revision-bearing PEX built from the pushed branch head
`8d005b38af9777b7e3314bf3e2910314effef4d2` with `--source-revision` asserted.
The recipe is unchanged since rc1, so the content matches the rc1-local base;
only builder provenance differs. Not pushed to any registry, no lock repin,
no matrix change: the owner's reading of "reference the rc2 base by tag"
(digest pin of a new base named for rc2, or a literal tag reference) and the
merge of the release PR are pending. Log `/opt/devcapsule-gate/rc2-local-base.log`.
A first attempt with the `nox -s pex` local artifact was refused by the
builder for lacking a public source revision, as designed.

Manifest compatibility fix (2026-09-24): focused tests 15 passed; full
`nox -s build` passed with 1064 tests, 20 deselected, one xfail, one
quarantined XPASS, mypy, PEX smokes and nine packaged integrations; log
`/opt/devcapsule-gate/manifest-compat-build.log`. Published v0.2.12 and rc1
executables, checksums verified, exercised against the fixed manifest with
isolated XDG state: 0.2.12 `config list` and `config resolve` exit 0; rc1
`config list` exit 0. Pytest scratch had to move to the overlay: this
capsule's 2 GB `/tmp` overflowed on the first run, and a second run under
the home directory failed only `test_unmountable_staging_fails_loudly`,
which expects an unmounted scratch path; the single test passes in `/tmp`
and on the overlay. No capsule was launched; the effect application from
the reserved name is covered by unit tests until RC2 exists.

RC1 configuration failure intake (2026-09-24): owner could not retain the log.
Original successor inspection showed exit 0 and no launch-context/configuration
mounts. One disposable read-only CLI probe of the exact image reproduced
`config list` and `versions show` failures from /opt and the actual project
mount. Bare `project config` prints help successfully. Evidence lives in the
retained run's `configuration-diagnostics.json`; the bug records exact errors
and producer/reader causes. No IDE restart, host-record edit or source fix.
Earlier recursive inspection PASS did not cover this story. No full source
suite was needed for this documentation-only intake.


Published-RC1 recursive PyCharm launch (2026-09-24): retained run
`0edc6f491291f0d5ffa4e31b0238863b` beneath the persistent-home
`e2e-workspaces/` directory. Clean clone at exact RC1 source `cec7a0c`; launched
with downloaded RC1 bytes, SHA-256
`68c58ec09c1a73e07c3bb1b1f7514341ddddaf645c7fae1ff4ff0763ff6f7689`.
The isolated checkout explicitly selects `devcapsule-base:0.2.14-rc1-local`,
pinned locally to image `sha256:0d9a185ec5a2ac04380e9b5540bae2b212356b8b5d4c0f91c7db320d486a414a`;
the project lock is unchanged. Successor image:
`sha256:bc387eb69b8457f61f016a0a21485302e3fc14bcbbae977e4a1623b8d5544863`.
Container `devcapsule-e2e-0edc6f491291f0d5ffa4e31b0238863b-successor` is running
with host networking; the actual PyCharm JVM is PID 42. Independent
`inspect-successor` passed. As UID 1000, public `devcapsule0` reports published
RC1 and exact runtime bytes, ordinary `devcapsule` is absent, and workflow
installation succeeds in a disposable directory. Evidence in the retained run:
`inspection.json`, `runtime-check.json`, `cli-check.log`, `launch.log`.
Owner received the desktop URL; its token is not committed. Human GUI acceptance
of this exact session is pending; no full recursive Nox suite or final-release
acceptance is inferred. Both this session and the earlier local-source session
remain available. No source changes or new downloads of PyCharm were needed.


Published RC1 and local base (2026-09-24): downloaded the public PEX, checksum
and manifest into `devcapsule-src/dist/rc1-published/`. Verified version
`0.2.14rc1`, mnemonic `v0.2.14-rc1`, source
`cec7a0c2f3467b8cc9d84eca820f35ee869087ec`, and SHA-256
`68c58ec09c1a73e07c3bb1b1f7514341ddddaf645c7fae1ff4ff0763ff6f7689`.
Used those exact bytes to build `devcapsule-base:0.2.14-rc1-local` with
`--network host`, recipe `ubuntu-24.04@9`. Image ID:
`sha256:0d9a185ec5a2ac04380e9b5540bae2b212356b8b5d4c0f91c7db320d486a414a`.
Build reused cached installation layers. Metadata and a disposable offline
container smoke passed: Python/Git/Docker, Node/JDK/Maven, display executables;
no bundled runtime PEX or agent CLI. Base is local only, with no registry push
or project-lock change. Evidence: `dist/rc1-published/local-base-build.json`;
log `/tmp/maintenance-rc1-base-build.log`. No GUI acceptance of this new base
or final-release acceptance is claimed. Source unchanged; no need to rerun
the source gate for this image build. Initial coordination claim hit a transient
SSH rejection; a subsequent claim succeeded. The release branch was not rebased.

RC1 publication trigger (2026-09-24): fetched main is
`c6bea96cfbbb15a428c86bde6924df8ff3db1c15` (PR #136); it contains release
commit `cec7a0c2f3467b8cc9d84eca820f35ee869087ec`, with matching runtime/test
sources. Candidate gate passed: mainline, zero unintegrated commits. Pushed
annotated `v0.2.14-rc1` atomically with the release branch and verified both
remote tag object and peeled commit. Expected package version is `0.2.14rc1`.
The public manifest returned HTTP 404 immediately afterward; publication is
pending, not failed or verified. No GitHub API/UI inspection was attempted.
Existing source/type/packaging and real PyCharm evidence applies; no runtime
code changed since acceptance. The release branch was not rebased.

Owner follow-up (2026-09-24): "Everything works" for the retained recursive
PyCharm session below. The installed-IDE cache gap was confirmed by reading
the acquisition/materialization path; filed with proposed acceptance scenarios,
severity minor, target none. No implementation or new Docker experiment was
performed for that report. Documentation links and whitespace were checked.

Owner-requested recursive PyCharm launch (2026-09-24): clean local clone of
`9cc08686c5f6c9b44a1a132bf81e4befd0ecf641`, retained run
`29fb2abc530735da1ebd625acd991622` beneath
`/home/devcapsule/.local/share/devcapsule/e2e-workspaces/`.
The original checkout's preflight fails on its existing website Git pointer;
the exact-commit clone passes without changing the original or its user edits.
Built a revision-bearing PEX, initialized isolated checkout configuration/state,
and ran `recursive-e2e launch-successor` with the pinned real PyCharm distribution.
Successor `devcapsule-e2e-29fb2abc530735da1ebd625acd991622-successor` remains
running with host networking. Independent `inspect-successor` passed; PyCharm's
JVM is running and the desktop has a `PyCharm User Agreement` window.
As UID 1000, `devcapsule0` reports the exact source revision and identical PEX
SHA-256 `a0e29d237e978d8c6575ccf12541571a1c0f1d9e016e8f3174ae1b1e23efb34b`;
`devcapsule` is absent. Workflow bootstrap by public command created the expected
files in a disposable in-container directory. Owner received the desktop URL;
its session token is deliberately excluded from committed records. Fresh IDE
first-run interaction and owner terminal acceptance remain pending. This was
the actual successor launch/inspection, not a claim that the full recursive
Nox suite or release-candidate campaign passed. No new release tag was published.

Owner-requested enum cleanup (2026-09-24): `RuntimeCommand` now owns the
supported public names. Configuration boundaries construct enum members;
materialization accepts the enum without repeating string-domain checks.
Existing tests pass enum members and assert typed forwarding from the launcher.
Required `nox -s build`: type checks, 1,060 source tests and nine packaged
integrations passed (20 deselected, one xfail and one quarantined XPASS).
The final Git-status step still fails on the existing website Git pointer;
the overall gate remains failed. Log:
`/tmp/maintenance-runtime-command-enum-build.log`. No new Docker/GUI campaign
was needed for this refactor; the prior command-mode evidence remains separate.
The release branch was not synchronized or rebased; its local workflow
difference from main is the already-read dogfooding rule from this repair.

CLI repair and development exception (2026-09-24): 311 focused checks passed;
four real-Docker variants passed for PyCharm/VSCodium and devcapsule/devcapsule0.
Tests invoke the command by name as UID 1000, verify exact runtime identity,
and install workflow files in a disposable project. Development mode permits
an independent development command without a shipped fallback. Three additional
filesystem cases ensure only our inherited shipped link is removed, preserving
a development script or symlink (eight runtime-artifact checks passed).
Full gate log: `/tmp/maintenance-runtime-cli-build-final.log`; final source
checks passed (1,060 tests, 20 deselected, one xfail and one quarantined XPASS),
as did type checks and nine packaged integrations. Final Git status then
failed on the existing `/home/devcapsule/.git-website` pointer; overall gate
remains failed.
No actual IDE-terminal acceptance of the new code or RC1 publication is claimed.
Earlier lowercase-help assertion failure was a harness defect, corrected before
the four Docker passes. The pre-fix Docker test reproduced exit 127 as expected.

Blocker intake (2026-09-24): live read-only Docker inspection and runtime
version/hash checks confirm the missing public CLI; IDE process environment
inspection confirms the URL-opener conditions. Evidence is in the two new bug
records. No runtime or website source was changed. New record links/index and
Git diff whitespace checks passed. Full build source/type/PEX checks and nine
packaged integrations passed, then final Git status failed on the pre-existing
website pointer to `/home/devcapsule/.git-website`; overall gate not passed.
Log: `/tmp/maintenance-rc0-blocker-intake-build.log`.
Mail delivered: `2026-09-24-maintenance-url-opening-triage.md` to
contained-display at `ba6768619aac`; workflow-onboarding item delivered to
workflow-improvements. Both await disposition, not implementation in this checkout.

Host-network validation (2026-09-24): owner confirmed the runner's host-network
session works. Attempt 4 in `dist/rc0-runs/session-7a4dbc068f58/run.json` records
requested `host`, observed Docker network `host`, exit 0, container absent and
PROCESS_CHECKS_PASSED. The owner made host networking the standing local launch
preference; see WORKFLOW-LOCAL.md, Local Launch Networking. Deliberate network
isolation tests retain their declared mode. Release branch was not rebased.

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

- Owner's rc3 test, 2026-09-24, produced three findings, all recorded:
  the launcher change rebuilt the formation with a 4.28 GB context transfer
  and 39 retained images at 266 GB (added to the installed-IDE reuse bug);
  `config list` advises resolve on a fresh resolution (new minor bug, fix
  proposed); and an untouched 0.2.12 checkout now owes a required
  antigravity-download decision (new bug under R-COMPAT-001, disposition
  needed: restore 0.2.12 behavior or name the exception in the notes).
  The rc3 launch itself worked; `devcapsule0` acceptance in the capsule is
  still to be confirmed by the owner.

- RC2 is required: rc1 accepts the fixed manifest but applies the
  `devcapsule0` exception only from the attribute, so dogfood sessions
  launched with rc1 on the fixed manifest get the normal `devcapsule` name
  until RC2. Existing running capsules are unaffected.
- The owner's host executable was not identified; the reported message can
  only come from 0.2.12 or rc0. Ask for `devcapsule version` when closing.
- The guard test pins `docker.memory-limit` as the released vocabulary; move
  it to include `devcapsule.command-name` when 0.2.14 final ships.
- The website checkout in this capsule has an embedded `.git` directory
  since 2026-09-23; the other checkout's pointer repair did not hold, as the
  owner's `git status` failure shows. Not repaired from here.

- RC1 runtime-configuration inspection bug needs component-upgrades triage;
  owner expects read-only inspection from /opt as well as the project root.
  Mail delivered at `dc91dbc8e484`; acknowledgement and repair remain pending.
- Run `0edc6f491291f0d5ffa4e31b0238863b` subsequently exited normally (code 0);
  earlier retained-running notes below are historical. No restart was attempted.

- Published RC1 plus the newly built local base is running in retained recursive
  run `0edc6f491291f0d5ffa4e31b0238863b`; agent checks passed, owner GUI acceptance
  pending. Keep it running for the owner; do not stop the earlier session either.

- Recursive PyCharm successor run `29fb2abc530735da1ebd625acd991622` is deliberately
  retained for the owner; see validation above. Do not stop or remove it merely
  because this agent turn finishes. Owner subsequently confirmed everything works.
- The runtime CLI blocker is fixed in source, awaiting main integration and
  exact-RC1 validation; public assets now verified and PR #136 is merged. Owner accepted
  the local PyCharm/devcapsule0 session; exact-candidate validation remains.
  Existing running capsules retain their original commands until relaunched.
- URL-opening triage and workflow-onboarding work item are handed to their
  owners through coordination mail. Their acknowledgement remains pending.
- The local workflow change reported by brief is our owner-directed host-network
  rule, already read; the release branch was not synchronized or rebased.
- Website Git pointer repaired locally on 2026-09-24 after the owner reported
  plain `git status` failing. Replaced missing `/home/devcapsule/.git-website`
  with relative `../.git/modules/website`; the existing metadata HEAD matches
  the parent's pinned commit `78b7b7f`. Original pointer saved at
  `.git/codex-website-git-pointer.before`. Plain parent/submodule status now
  works; website status and staged/unstaged binary diffs are unchanged.
  No source, index or ref was reset. The earlier policy-only full build passed
  source/type/PEX checks and nine packaged integrations before failing at this
  status operation; log `/tmp/maintenance-host-network-policy-build.log`.
  That historical full gate was not rerun for this local metadata repair.
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

- [Released launchers reject the repository manifest](../../bugs/devcapsule/2026-09-24-released-launchers-reject-repository-manifest.md): blocking, fixed on branch, needs RC2.

- [RC1 runtime configuration inspection](../../bugs/devcapsule/2026-09-24-runtime-configuration-inspection-fails.md): component-upgrades; confirmed, target 0.2.14.

- [Installed IDE Docker reuse](../../bugs/devcapsule/2026-09-24-installed-ide-docker-reuse.md): review design with owner before implementation; no release target.

- [Runtime CLI blocker](../../bugs/devcapsule/2026-09-24-runtime-cli-not-on-path.md): next implementation task; blocks 0.2.14.
- [URL-opening defect](../../bugs/devcapsule/2026-09-24-url-opening-without-browser-handler.md): contained-display triage.
- [Workflow onboarding](../../work-orders/2026-09-24-workflow-installation-onboarding.md): non-blocking follow-up.

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
