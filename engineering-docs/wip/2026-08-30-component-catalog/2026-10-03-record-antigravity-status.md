# Workstream Current Status: Component Catalog

Mnemonic: `component-catalog`

Start date: 2026-08-30

State: active 2026-09-09; final implementation slice ready for PR #65, graphical successor exited successfully

Integration target: `main`

Delivery method: pull request, one per validated component (see *Integration
Cadence*)

Requirements: `R-PRODUCT-001`, `R-PRODUCT-002`, `R-SCOPE-001`, `R-DOCKER-001`

## Final Delivery Boundary (2026-09-09)

Owner direction: this is the last task to deliver through this workstream.
Freeze implementation scope. Do not resume the historical feature backlog
below; remaining activity is PR delivery, the already-authorized v0.2.11
promotion, and workflow finalization. The workstream is not concluded until
those delivery obligations and its final records reach main.

Integration branch: `component-catalog/antigravity-cli`, synchronized with
fetched main. Delivery: [PR #65](https://github.com/ccozianu/devcapsule/pull/65),
open and not draft; use the repository's PR merge policy. The source branch is
frozen against unrelated changes. Release implementation and acceptance are
already integrated through PR #63; workflow naming intake through PR #64.
The remaining diff is the smoke harness, documentation, and execution evidence.
Validation: full build (579 unit tests, one existing xfail, 9 packaging tests,
mypy on 128 files), seven full-base Docker tests, two preliminary recursive
tests, and the live graphical successor inspection and exit proof below.
Later changes only record evidence and scope; no executable changes invalidate
those results. The workstream intake contains only its README.

Final tag `v0.2.11` is still absent. Promotion must tag the accepted RC3 source
`94e798f1d1a7aaab93ae3e47d9636471448a8e66`, also the retained release-branch
tip, rather than the smoke-harness branch tip. Recheck final publication before
closing the workstream. Owner's "sounds good" and request for merge readiness
accept proceeding with delivery; no specific provider-login or editor checklist
claims are inferred from that brief response.

## Graphical Recursive Successor (2026-09-09)

The owner corrected the preceding execution scope: the recursive acceptance
they requested includes a built graphical successor, manual inspection, and
normal GUI exit producing container code 0. Their recollection is confirmed by
the archived recursive workstream's live Stage 6 evidence and the
2026-08-15 detached-successor cleanup bug, which recorded both historical
successors as `Exited (0)`. The current Nox wrapper is only the preliminary
subset; calling the graphical continuation optional was an agent scope error.
The owner has already requested that continuation; do not ask for its scope
authorization again.

Executed the existing `recursive-e2e launch-successor` and independent
`inspect-successor` commands through the published RC3 executable. Created an
ownership-marked run using the existing clean-clone protocol, detached its
scratch checkout at exact RC3 source, removed its local origin, and verified
the clone is clean and independent. This is test-owned source, not a new
editing workstream. Configured isolated XDG/home/IDE state and the declared
acquisitions plus Docker/network/sudo access. The checkout explicitly authorizes
the retained full RC3-built base; its committed v0.2.10 recommendation stays
unchanged. No personal IDE or agent credential state was copied.

Run: `8d769574856fb2b7a7e3a296c04d7188`.
Source: `94e798f1d1a7aaab93ae3e47d9636471448a8e66`.
Container: `devcapsule-e2e-8d769574856fb2b7a7e3a296c04d7188-successor`, ID
`89bbff543005849e35899b7d45dabc366be754c366a55e58c3f7b5f5927ed26f`.
Materialized image:
`sha256:2e3b67566a8975e834caac5f80a34ef08a34c2818011e7d93a3501621e03b5df`.
Base identity:
`sha256:90eece0d93ab9c94265efc1ac77b363e4300d345c58761ab58bc31d20667639a`.
Runtime PEX SHA-256:
`32f900903d8a1286c62aae72b0d8e71a3e6a25e68d91fae8464595da472bd6e6`.

The real component image built successfully. Independent inspection passed
identity, exact mounts/environment/security/resource/restart settings, runtime
plan digest and read-only mount, run ID, supervised PyCharm process, and tool
versions (Claude 2.1.261, Codex 0.153.4, Node 22.23.1, javac 25.0.4, Maven
3.9.16). An additional in-container version call reports `v0.2.11-rc3`; image
labels independently confirm the new base ID and published executable checksum.

Retained run root is beneath the current capsule's
`~/.local/share/devcapsule/e2e-workspaces/`, named by the run ID. It contains
the ownership marker, `milestone-manifest.json`, `expected-plan.json`,
`candidate-inspection.json`, `candidate-launch.log`, and
`candidate-command.py`. The last file invokes the retained release executable
with the run's isolated configuration, allowing repeat inspection. Its checkout,
state and staging must remain while the GUI is running. Temporary monitoring:
`docker wait` writes `/tmp/devcapsule-rc3-successor-exit-code`.

Completion recheck: Docker records this exact successor as `exited`, code `0`,
`OOMKilled=false`, finished `2026-09-09T22:08:19.014764095Z`; the independent
`docker wait` observer also returned `0`. The owner then said "sounds good"
and asked to proceed to merge readiness. This proves normal graphical-session
termination; no agent stop/kill was used. The stopped container and owned run
remain as inspection evidence, and historical runs/control capsule are untouched.

**Planned next step:** merge PR #65, complete final release promotion, then
finalize the workstream under the owner's final-task scope cutoff above.

## Recursive Suite Execution (2026-09-09)

At the owner's request, ran the existing recursive suite from clean source
`b93b5e193cbb7808f701a9278474c0dfa72e6e5b` after confirming the branch already
contains fetched main. The current capsule passed Docker, host-network,
persistent-home, runtime-plan, and X11 authorization preflight.

```text
cd devcapsule-src
.venv/bin/python -m nox -s recursive_dogfood_e2e
```

Result: **2 passed, 7 deselected in 44.82 seconds**; Nox completed successfully
in 48 seconds. This executes source CLI planning, an isolated contributor
bootstrap, and the recursive clean-local-clone protocol. The clone test verifies
the current capsule's embedded PEX against its image provenance independently
of the selected source revision. Contributor bootstrap uses the actual base
under the current running capsule, not the new candidate base retained below.

Also invoked the checksum-verified published RC3 executable directly for
`project --path . recursive-e2e preflight --json` and `recursive-e2e run --json`.
Both passed. The image-revision warning correctly distinguishes the RC3 caller
from the older running capsule. The RC3 planning run
`1dbf3d31aa891c761324c1c4b97ee69c` and source planning run
`7c19ec360726b7052d1755d32ac74de7` report cleanup complete; their staging
directories were independently confirmed absent. Contributor run
`a74003586f14b0abef25fca7f3b688ee` also removed its exact container and workspace.
Local logs: `/tmp/devcapsule-rc3-recursive-nox.log` and
`/tmp/devcapsule-rc3-recursive-dry-run.json`.

Scope limitation: the current public `recursive-e2e run` implements a dry run;
the Nox wrapper adds the two tests above. Neither orchestrates successor building
or launch. No new successor IDE, GUI acceptance, or full recursive lifecycle
acceptance is claimed. The earlier full candidate-base smoke remains separate
evidence. No implementation changes were needed to execute this suite.

The original optional-scope question is superseded by the owner's correction
and the graphical successor execution recorded above.

## Full Candidate Base Smoke (2026-09-09)

The owner corrected the previous smoke scope: it had tested the RC3 executable
against an existing base, not built a candidate base. Added `--build-base` to
`nox -s e2e`, requiring an explicitly selected published PEX. Nox invokes that
executable's actual `images build --type base --recipe ubuntu-24.04` with its
embedded public source revision; it does not call the source tree's builder or
use the fixture's `install_baseline=False` as a substitute for the full recipe.

Validation completed using the existing checksum-verified RC3 download:

```text
cd devcapsule-src
DEVCAPSULE_PEX_UNDER_TEST="$PWD/dist/releases/v0.2.11-rc3/devcapsule.pex" \
  .venv/bin/python -m nox -s e2e -- --build-base --build-network host
```

Final retained local base:
`devcapsule-base-e2e:v0.2.11-rc3-3e30c6c81a91`, image ID
`sha256:90eece0d93ab9c94265efc1ac77b363e4300d345c58761ab58bc31d20667639a`.
Builder: RC3 source `94e798f1d1a7aaab93ae3e47d9636471448a8e66`, executable SHA-256
`32f900903d8a1286c62aae72b0d8e71a3e6a25e68d91fae8464595da472bd6e6`.
`dist/e2e-base-build.json` contains the latest local build's identity record.
This is a locally retained test base, not a Docker Hub publication or a lock repin.

The build executed recipe 7 from Ubuntu 24.04, including OS packages and the
real Node 22.23.1, Temurin 25.0.4+7 and Maven 3.9.16 contributions. The first
successful build installed Node in 18.3s, Temurin in 36.1s and Maven in 4.7s;
Temurin was installed once and copied to both Maven's stage and the final image.
The final rerun used cached installation stages. BuildKit's existing OS baseline
cache was reused; this was not claimed as a cold, cache-free build.

Seven Docker tests passed in 114.52s: full-base provenance/tool/agent-absence/
runtime-absence checks, component cache reuse, both fixture IDE surfaces on the
new base, unexpected container removal, supervisor sessions, and the separate
plain-Ubuntu no-Python/no-network proof. Build contexts use the unique owned tag
and verify its image ID first; Dockerfile FROM cannot use the raw `sha256:` image
ID spelling. The lifecycle/base inspection paths use the recorded image ID.
Full Nox build passed: 579 unit tests, one existing xfail, 9 packaging integration
tests and mypy on 128 files. No real GUI/login smoke is claimed.

Environment finding: the default Docker bridge cannot resolve Ubuntu repositories
on this host, while an explicit host-network probe succeeds. The stalled default
build was canceled and the new `--build-network host` option used explicitly.
It changes the build network only; runtime smoke containers retain their settings.
An initial full-base smoke exposed the Dockerfile image-ID spelling error, now
fixed. The earlier successful build is also retained locally at
`devcapsule-base-e2e:v0.2.11-rc3-8442dbf371f6` for inspection.

**Planned next step:** review/integrate the smoke-harness changes, then continue
final promotion at the accepted RC3 source commit. Candidate executable/tag and
release branch remain unchanged. The previous six-case mode remains available
without `--build-base` and is documented as existing-base compatibility only.

## Published Executable Smoke Follow-up (2026-09-09)

The owner requested adapting and running the existing E2E smoke suite against
the GitHub-published `v0.2.11-rc3` executable. Selected `nox -s e2e` as the Docker
smoke suite; the optional clarification about the longer recursive dogfood test
received no answer during this slice, so that scope was retained.

Remote state reverified: PR #63 merged the release implementation/acceptance and
PR #64 delivered the workflow naming intake. This branch was fast-forwarded to
fetched main `857035a` before editing. The previous PR-delivery blocker and next
steps in the historical checkpoint below are superseded by those merges.

`DEVCAPSULE_PEX_UNDER_TEST` now selects an existing executable without building a
local replacement. Nox reports its mnemonic, source and SHA-256, derives version
assertions, and rejects explicitly supplied expectations that disagree. This mode
runs six Docker smoke cases; contributor source-bootstrap and recursive dogfood
retain their separate paths. The ordinary local-build mode is preserved. The
removed-container test copies the selected PEX into its disposable container and
checks its checksum and identity, so it cannot accidentally test the old base
runtime. The runtime test defaults to the committed base pin instead of debug-v018.
Download/verification and invocation are documented in `devcapsule-src/README.md`.

Freshly downloaded artifact:
`devcapsule-src/dist/releases/v0.2.11-rc3/devcapsule.pex`, source
`94e798f1d1a7aaab93ae3e47d9636471448a8e66`, SHA-256
`32f900903d8a1286c62aae72b0d8e71a3e6a25e68d91fae8464595da472bd6e6`.
Both the published checksum and release manifest were checked. All six selected
E2E tests passed (105.98 seconds): contribution-cache reuse, both fixture surfaces,
unexpected removal, supervisor sessions, and no-Python/no-network execution.
Full Nox build passed: 577 unit tests, one existing xfail, 9 packaging integration
tests, and mypy on 127 files. No GUI/login or successor-workspace smoke is claimed.

**Planned next step:** review/integrate this test-harness slice, then continue the
existing final-promotion task using RC3's exact commit. The executable, candidate
tag and release branch are unchanged; these are harness/documentation changes.
The accepted source and promotion record are already on main. Final tagging was
not part of this smoke-test execution; recheck remote state before promotion.

## Current Release Experiment (2026-09-09)

Owner accepted and authorized the [candidate protocol](release-candidates-proposal.md).
**Current checkpoint:** `v0.2.11-rc3` is published as a prerelease at source
`94e798f1d1a7aaab93ae3e47d9636471448a8e66`, also the retained
`release-0.2.11` tip. [Run 34333414510](https://github.com/ccozianu/devcapsule/actions/runs/34333414510)
passed every source, packaging, Docker, staged-byte and downloaded-PEX gate.
The downloaded PEX SHA-256 is
`32f900903d8a1286c62aae72b0d8e71a3e6a25e68d91fae8464595da472bd6e6`.
Local checksum and manifest recovery verification passed. GitHub Latest remains
`v0.2.10`; **no final v0.2.11 tag or stable release exists**.

Acceptance is recorded in `engineering-docs/releases/v0.2.11.json`, generated
from the published candidate with the helper. It accepts automated release/build
validation under the owner's operator authorization; no new GUI/login or provider
acceptance is claimed. The component combination was already on main through
PR #62; this slice changes release machinery and pins its packaging backend.

**Planned next step:** deliver the intake-only outbox and the implementation plus
acceptance record through PRs. GitHub connector creation is denied with HTTP 403;
Git SSH pushes work. Once main contains the accepted source (or reviewed mapping)
and the record, tag `v0.2.11` at the exact RC3 SHA and push it, then monitor and
verify final publication. Do not tag current working-branch HEAD: its acceptance
and handoff commits intentionally follow the frozen release source. If integration
uses squash/rebase, update the record with the reviewed full-delta mapping and
actual main commits before final tagging. Do not infer ancestry from tree equality.

Branch-policy ruling: release refs are durable anchors rather than new
workstreams. `component-catalog/antigravity-cli` remains the editing selection;
release refs may outlive it and must not absorb advancing main after acceptance.
The owner directs bias for action while workflow-improvements resolves the
reusable naming rules. The intake is committed as `8c99f43` and pushed on
`component-catalog/outbox`; **main delivery is pending** because connector PR
creation still returns HTTP 403, Resource not accessible by integration. The
owner has been asked to merge the intake-only comparison or restore access.
This is the explicit owner-authorized gap handling, not a silent workflow edit.

Verified fetched main is `3f028ee`, including PR #62's previous implementation.
The branch was synchronized before this slice. Implementation now includes RC
version normalization, branch membership, exact-candidate acceptance from an
engineering JSON record on main, ancestry/reviewed/exception integration routes,
prerelease metadata, final dependency/Python fingerprint comparison, and an
acceptance-record helper. Final source must remain exactly the accepted RC SHA.

Validation so far: full Nox build passed with 574 unit tests, one existing xfail,
9 packaging integration tests (including a real RC PEX), and type checks.
Actionlint passed. `release-0.2.11` and immutable `v0.2.11-rc0` were pushed at
`04c1e935552c17ff7c262caf81573e6cd272060a`. The [RC0 run](https://github.com/ccozianu/devcapsule/actions/runs/34332187735)
failed before publication: early-exiting grep caused cut's SIGPIPE under pipefail,
falsely rejecting a public revision. The fix drains the pipeline; packaging tests
now advertise 500 refs and use annotated release tags. Inspection also found and
fixed the clean-machine test's source-baseline version assumption. Next candidate
was `v0.2.11-rc1`; RC0 stays unchanged. Preparation baseline is
`3f028eeb97d7de6bce5b9f2ac2faf0a1b940cb61`.

RC1 at `59d84f04bb54398d74e5e6972352517af9098b7d` passed every automated gate,
including both downloaded-byte verification and the downloaded PEX proof, in
[run 34332492934](https://github.com/ccozianu/devcapsule/actions/runs/34332492934).
Publication then failed because GitHub's REST by-tag lookup excludes drafts.
The complete RC1 assets remain staged as a draft; no stable release was exposed.
The fix locates the draft's ID through authenticated release listing, which the
recovery step already uses. Next candidate is RC2; tags remain immutable. The
permanent release guide is also brought up to date in this candidate.
Local validation additionally passed all five Docker tests and an actual RC1
clean-machine proof. A temporary-repository promotion dry run verified rejection
without a main acceptance record and acceptance after integration at unchanged
candidate SHA. No real GUI/login smoke or final release is claimed.

RC2 was pushed at `8e6f33128a929c354b8fb36e64977fbac09a7bc1`. Final review
found the packaging backend still used floating setuptools/wheel build-system
requirements. Pinning the already validated versions (84.0.0 and 0.47.0) makes
those packaging inputs stable across candidate/final builds as required by the
accepted contract. RC3 will carry that fix; the RC2 run is retained as additional
publication-path evidence, not the candidate chosen for final promotion.

## Previous Implementation Checkpoint (2026-09-08)

The owner resumed this branch on 2026-09-08 and explicitly authorized the
release simplification discussed here, adding independent component-install
reuse to the v0.2.11 target. This direct instruction supersedes the previous
wait for project-management's runtime-delivery disposition for this slice; no
other workstream's records are edited or its queued design items dispositioned.

Implementation on this branch: tag-derived release package versions; draft,
verify, publish workflow with retained/reused assets and a release manifest;
launcher PEX delivery identified by SHA-256 in the formation; runtime-free
base recipe 7; independent BuildKit contribution stages for tools, IDEs and
agents, assembled with COPY --link --from. v0.2.11 reuses the pinned v0.2.10
base; publishing a replacement base is not a prerequisite. Existing project
locks and sample branches are unchanged.

Validation: full Nox build passed (556 unit tests, one existing xfail, mypy,
source and PEX smokes, 8 packaging integration tests). The tag test builds
v98.7.6 from a source baseline of 0.2.10, verifies both installed metadata and
build identity, and checks source remains unchanged. Docker tests proved cache
reuse/invalidation, exact launcher delivery to both surface fixtures on Ubuntu,
and runtime sessions against the existing v0.2.10 base. Actionlint 1.7.12 and
`git diff --check` passed. Runtime metadata now overrides inherited base PEX
labels with the copied runtime's actual identity.

Delivery checkpoint: implementation commit `e6e0808` is pushed on
`component-catalog/antigravity-cli`. GitHub connector PR creation returned HTTP
403, "Resource not accessible by integration"; no alternate CLI login is
configured. **No PR was created.** Open it from
https://github.com/ccozianu/devcapsule/compare/main...component-catalog/antigravity-cli?expand=1
or restore the connector's pull-request write access. Then obtain the owner
acceptance required by *Integration Cadence* and merge. After integration the owner can apply
v0.2.11 to current remote mainline; no separate version bump or base repin is
needed. The review artifact is `devcapsule-src/dist/devcapsule.pex`, built with
verified public source revision `e6e08083f05f2540a9b950b9b3cf3672e9a100e0`.
It reports the local baseline mnemonic v0.2.10-local-linux-x86_64; the final
v0.2.11 tag supplies the released package version. The earlier local validation
artifact is `devcapsule-src/dist/devcapsule-local.pex`.

Open threads for this slice: no real GUI/login smoke is claimed; source-form
launches require an explicitly selected built PEX; base publication remains a
separate maintenance operation; a partial GitHub asset upload requires recovery
from the retained Actions artifact. No release has been tagged or published by
this session. The prior v0.2.10 smoke questions below remain unanswered.

## Goal

Make IDE surfaces and agent CLIs regular, uniformly handled catalog
components instead of special-cased launch paths. Two tracks, sharing one
generalization:

1. **VSCodium on the normal project path**: retire the bespoke
   `codium_with_claude` launcher and command tree and deliver a neutral
   `codium` interactive-surface component, the shape the PyCharm path already
   has. This executes the `in-v1` ledger row *Independent IDE Surface:
   VSCodium On The Normal Project Path* and is what makes later surfaces
   (Eclipse, IntelliJ) ordinary configuration rather than new launch code.
2. **Antigravity CLI as a curated agent component**: the Google slot of the
   `in-v1` ledger row *Curated Agent Choice*, delivered as a default-selected
   component with persistent per-checkout state, under the delivery contract
   below.

## Why This Workstream Exists

Opened by `project-management` on 2026-08-30 at the product owner's
direction. The [V1 scope ledger](../2026-08-09-project-management/v1-scope-ledger.md)
anticipated a registration for this work under the working name
`codium-surface` and ruled on 2026-08-29 that no registration happens until
the work starts; the work is now starting, and this workstream subsumes that
anticipated registration under a broader name because the same
componentization framework also carries the agent-component track.

The special-casing being retired is structural, not cosmetic. Two parallel
worlds exist today: the component path (lock → `components/catalog.py` →
`ComponentRuntimeTemplate` → runtime planning, with persistence as declared
state slots) and the legacy path
(`configurations/codium_with_claude/_launcher.py` hand-building `docker run`
with hard-coded mounts and command, plus a dedicated CLI command).
`selected_component_definitions` currently hard-codes PyCharm as the only
legal `interactive-surface`; generalizing that selection is the shared
foundation both tracks stand on.

## Branch Association

Branch prefix `component-catalog/`. The first branch is
`component-catalog/codium-surface`, forked on 2026-08-30 from the
registration merge `363f656` on `main` (`PR #48`), per *Beginning A
Workstream* in `WORKFLOW.md`. The root registry row still reads "no branch
yet"; the correction travels with this workstream's first integration rather
than alone.

Recorded latitude: registration shipped without the empty
`intake-dispositions.md` that *Beginning A Workstream* step 4 requires. The
file was added at branch opening, in this workstream's first commit. Gap
noted here; the protocol itself needs no change, only following.

## Scope

In scope, track 1 (the ledger row's scope, restated):

- Retire the `codium_with_claude` command tree; its name welds the IDE to one
  agent, contradicting agent neutrality.
- Generalize interactive-surface selection in the component catalog and add a
  `codium` `ComponentDefinition` with a vscode-family runtime adapter, the
  analogue of the existing `jetbrains` adapter.
- The embedded resolution matrix gains `codium` as a second
  `interactive-surface` value with its own pinned component table; `init`,
  the lock, and `project run` select it like any other node.
- Launch-path parity on the Codium surface: host-browser bridge, runtime
  plan, run manifest and inspection, GUID-derived cleanup.
- State the Open VSX extension-ecosystem boundary rather than discovering it.

In scope, track 2:

- The Antigravity CLI component per the delivery contract below, including
  the license and redistribution analysis the ledger requires before any
  base-or-component decision, checksum-pinned acquisition, and a
  checkout-scoped persistent state slot in the pattern Claude Code already
  uses.

Open scope question, to settle early rather than discover late: whether the
parallel `vscode_with_claude` legacy path is componentized alongside codium or
retired outright. It duplicates the same special-casing.

Not in scope:

- The supervisor core and its process model — owned by `contained-display`,
  which is paused; this workstream *consumes* the supervisor↔component
  contract and must not redesign it.
- Any change to `D-0005` agent neutrality (see the delivery contract).
- Eclipse and IntelliJ surfaces themselves; this workstream only has to leave
  them cheap.

## The Antigravity Delivery Contract

Decided 2026-08-30, by the product owner, choosing the default-selected
component reading explicitly over baking the CLI into a base image, so
`D-0005` stands unrevised: bases remain agent-neutral and the base
agent-absence tests remain correct.

- Antigravity CLI is a curated component that the default configuration
  selects; "available by default" means default-selected, not present in any
  base.
- It materializes just in time, on the first run of a project, into a cached
  local environment image — the local-materialization delivery policy Claude
  Code established.
- Installation prefix is `/opt/antigravity-cli` if at all possible: prefer
  downloading an archive, unpacking under `/opt`, and putting its `bin/` on
  `PATH`, over installing a `.deb` or similar system package.
- The default launcher arranges, as for Codium and Claude Code, for the
  component's config and state to persist between runs on the same checkout.
- The ledger's per-agent required outcomes apply: pinned identity with
  checksum verification, a license and redistribution analysis performed
  rather than assumed, a credential and state contract that grants no host
  access by mere installation, and inspection output reporting selection,
  state location, and authorization.

## Integration Cadence

Decided 2026-08-30, by the product owner: this workstream integrates with
`main` frequently — a pull request every time a component is validated, where
validated means unit tests pass plus a smoke test performed, for now, by hand
by the product owner. Do not accumulate multiple finished components on the
branch.

## State-Slot Rulings (2026-09-02)

Following the antigravity state bug, the owner ruled: the home overlay
stays, and *everything under `$HOME` is owned by the user* no matter
which mechanism (build, entrypoint, mount mechanics) touched it.
Implemented on this branch, recorded in the
[state-slots design note](../../design-notes/devcapsule/state-slots-home-overlay-and-ownership.md):
contract validation holds overlay slots to direct children of home and
rejects cross-component slot overlap; the launcher pre-creates every
home-overlay mount point inside the persistent home source as the
invoking user (and reports foreign-owned leftovers it cannot repair).
The entrypoint-side verification of the invariant is a coordination
item for `contained-display` (below).

**Passthrough ruling (2026-09-02)**: raw docker passthrough refuses
single-instance options the launcher composes (`--network`, `--memory`,
`--shm-size`, `--user`, `--pull`, lifecycle flags, …) — docker keeps
the last occurrence, so a passthrough repetition would silently
override the resolved plan; each refusal names the sanctioned lever.
Repeatable options (`-v`, `--env`, `--mount`, …) pass through as
before. Denylist and rationale live beside
`reject_launcher_owned_docker_options` in the host launcher.

## Substrate Ruling (2026-09-02, amends D-0007)

The v0.2.9 base rebuild surfaced the edge model's granularity error: the
owner tried `--authorize base-image …:v0.2.9` and the grammar could not
express it, because edges keyed on the base mnemonic made every derived
base release an unverified stranger. The owner ruled: compatibility is a
fact about the *substrate* (the shared Ubuntu/toolchain generation), not
about our derived base releases, which vary only our own layer — so
edges now verify component-on-substrate and base pins declare their
generation (`ubuntu-24.04-gen1` = v026; `-gen2` = v0.2.8 and later
rebuilds with the vscode-capable runtime). A new base on a shared
substrate inherits every edge; the substrate string bumps only on
substantial base changes. Implemented on the branch (matrix
`embedded-6`); the amendment is recorded in D-0007. Consequence: agent
smokes (resume item 3) establish gen2 edges once, covering v0.2.9 and
every later gen2 release. The v0.2.9 base pin landed the same day after
the owner pushed the image (digest `sha256:ca9f7961…734232`, read from
the registry at pinning time; matrix `embedded-7`): codium-only and
codium×antigravity formations now resolve to v0.2.9 with inherited gen2
edges, while agent-carrying formations stay on v026 pending their gen1→
gen2 smokes. From the same episode, recorded and then **ruled and fixed 2026-09-03**:
[`--authorize base-image` conflates consent with selection and explains neither](../../bugs/devcapsule/2026-09-02-authorize-base-image-conflates-consent-with-selection.md)
— init now accepts a base reference as a checkout-level selection
(daemon-inspected, metadata presented, informed consent solicited;
`--less-pedantic` skips the solicitation), completing the path the
config-verb and realization layers already carried. A second ruling
the same day retired `yes` as a base-image authorization value —
authorizations are KV pairs; the reserved keyword `default` accepts
the recommendation for a single key across the authorize family. A
third made `default` input-only: the tree stores what it resolves to
at decision time, uniformly across families (set-nodes accept the
token but declare no default yet — whether `configuration.values.*`
gains a `default` field is the owner's open follow-up). A fourth:
`unset` removes the name from the tree and therefore refuses
mandatory nodes (`node.required` — declaration-required values,
required secret inputs, base-image) instead of deferring the failure
to resolve time. A fifth ruling closed the subtree question the owner had opened: the
node namespace *stays flat*, with the `.` dot convention as the poor
man's tree — no structural subtrees, no prefix-mandate mechanism;
node-level `required` is the whole mandate story. One naming
observation stays on record: component state slots spell their grouping
with `/` (`pycharm/system`, `codium/user-data`) where the convention
is `.` — cosmetic, and any convergence is its own decision. The joint grammar
ruling with the denial bug remains open, as does the larger
base-as-config-node unification the owner asked about (it belongs with
the checkout-local-needs rebuild — same resolution-time inversion).

## Coordination With `contained-display`

`contained-display` is paused as of 2026-08-30 until this workstream shows
significant progress. A `project-management` intake item in its queue directs
it, on resume, to treat the supervisor↔component runtime contract as
load-bearing for this workstream's components and to route any deliberate
contract change through coordination rather than changing it inadvertently.
Symmetrically: if this workstream finds the contract insufficient, it records
the gap and coordinates; it does not reshape the supervisor.

Open coordination item (2026-09-02): the entrypoint half of the $HOME
ownership invariant — the runtime verifying at container start that
`$HOME` and its first-level entries are user-owned, failing loudly
otherwise — belongs to the supervisor `contained-display` owns; this
workstream implemented only the client/launcher half.

## Current Task

Track 2, the Antigravity CLI component, began 2026-09-02 on branch
`component-catalog/antigravity-cli` after track 1 merged to `main`
(PR #50). The ledger-gated
[license and redistribution analysis](antigravity-cli-license-and-redistribution-analysis.md)
is done: proprietary binary, per-user acceptance by download, no
redistribution grant, but a developer's own cached local image is not
redistribution — the delivery contract stands unmodified and the
component proceeds as `local-materialization` behind an
`antigravity-download` acquisition authorization, pinned to the
versioned GCS artifact (v1.1.24 verified: manifest sha512 matched,
sha256 computed) with state at `~/.gemini/antigravity-cli` as a
checkout-scoped slot.

A `project config need CAPABILITY` verb also landed (`46cec03`), but its
layering is **pending an owner ruling and a rebuild** — see *Open
Threads*. As shipped it edits the committed manifest and rides
`init --regenerate`; the owner ruled 2026-09-02 that the default must be
a checkout-local *experiment* that commits nothing.

On resume later on 2026-09-02 the owner directed: implement the
Antigravity CLI component now (ahead of the config-need rebuild, which
stays an open thread), and give this workstream a release target — see
*Release Target: v0.2.9*. The same session logged a third
v0.2.8-validation bug found by running `project run` against this
checkout itself:
[2026-09-02-formation-identity-claims-an-entrypoint-the-recipe-never-sets](../../bugs/devcapsule/2026-09-02-formation-identity-claims-an-entrypoint-the-recipe-never-sets.md)
— the formation identity churns on descriptor-only changes, records an
entrypoint the recipe never enforces (tini is still PID 1 on v026
formations, against `500909d`'s premise), and superseded multi-GB
canonical images accumulate with no lifecycle.

**2026-09-05, codex delivery rebuilt at the owner's direction.** The
owner's "upgrading codex left it in an incomplete state" after the
v0.2.9 rebuild root-caused to the single-member extraction: codex was
one plucked binary, missing the bundled bubblewrap, ripgrep, zsh and
code-mode host it resolves beside itself, so every sandboxed command
panicked (never a regression of the upgrade; 0.145.0 formations fail
the same way). Recorded in
[2026-09-05-codex-installed-as-a-single-plucked-binary](../../bugs/devcapsule/2026-09-05-codex-installed-as-a-single-plucked-binary.md).
The owner directed the vendor's own method — a plain local `npm install`
with `node_modules/.bin` on `PATH` — under the `/opt` convention:
`LockedArtifactDeclaration` gains the `npm-package` format, codex pins
both npm tarballs (meta package new at the component level; platform
package under its alias), materialization copies the host-verified
tarballs into `/opt/codex/<version>` and runs one offline
`npm install --ignore-scripts` with the base's node inside the build
(matrix `embedded-13`; golden locks and the dogfood lock regenerated,
so the checkout's base-image authorization goes stale by design and
re-asks at the next resolve). Verified on a scratch image built from
the rendered steps on the v0.2.9 base: launcher, binary, all helpers,
and a Landlock-sandboxed command as an unprivileged user. Two things
the owner should know: the tarballs stay beside the manifest (about
135 MB per codex-carrying formation, so the recorded `package-lock.json`
describes an install npm could repeat), and node is now a runtime
dependency of codex — assumed shipped by every base for now, per the
owner ("we'll resolve dependencies later"). The same day the owner
ruled the sandbox half (*the capsule is the sandbox*) and directed the
pin to 0.153.4: see the *Codex sandbox configuration* open thread for
the seeded `config.toml` and the new `state_seeds` contract. The
in-capsule smoke of the npm layout ran on the scratch tictactoe
checkout (codium × codex 0.153.0 on v0.2.9): build clean, launcher on
PATH, all helpers present, known-good generation `20260905T135119Z`
recorded.

## Release Target: v0.2.10 (0.2.9 withdrawn 2026-09-06)

**Superseded 2026-09-06.** v0.2.9 was tagged and published on 2026-09-05
(PEX on GitHub Releases, base on Docker Hub) with Codex effectively
broken — the single-binary extraction fixed the same day, after the tag
(PR #56). The target is **v0.2.10**; 0.2.9 is withdrawn from GitHub and
Docker Hub only after 0.2.10 is pushed and validated (order settled
2026-09-06, so no lock ever pins a digest that has vanished), with a
provision: everything is validated first on the two sample projects —
trading-research (PyCharm × three agents) and tictactoe (Codium × three
agents) — and only then is the dogfood project migrated to the
three-agent configuration. The walk follows the release note's
dependency cycle: land content → bump to 0.2.10 → build the PEX → build
and push the base as `v0.2.10` → repin (matrix bump, sample and dogfood
locks regenerated) → sample smokes → dogfood smoke → tag → withdraw
0.2.9. A release-candidate concept to make that walk routine went to
`project-management` as intake 2026-09-06.

**Walk status, 2026-09-06 afternoon.** The owner smoked trading-research
on the locally built 0.2.10 base and the local PEX ("worked nicely").
Then, from inside the dogfood capsule: a strict PEX was built from the
pushed revision `bd8283b` in a clean worktree (source verification:
public GitHub commit reachable); the base was built from it with recipe
6 and pushed as `docker.io/mycodespaceai/devcapsule-base:v0.2.10`,
registry digest `sha256:76a07cb9e72158f810b32598eb05f9a375f8e4748b80b6eac04c403798d39a45`
(13:50 UTC; the owner approved the push after seeing the image's
labels). The build needed `--network host`: the daemon's bridge network
hands containers nameservers on 100.100.x that they cannot reach, so
`apt-get update` fails under the default build network on this host —
an environment fact, not a recipe defect. The matrix pins v0.2.10 as
the newest base in the family (`embedded-17`); golden locks, both
sample locks (committed and pushed on each sample's
`three-provider-formation` branch), and the dogfood lock are on it, and
the dogfood manifest now needs `antigravity-agent` — the three-agent
configuration. Remaining: the owner's smoke of tictactoe and of the
dogfood project on the pushed base, the two PRs (workstream branch,
outbox), the `v0.2.10` tag, then the 0.2.9 withdrawal and the v0.2.9
pin's retirement. The original v0.2.9 gate list follows for the record;
its open items carry over.

**Walk status, 2026-09-06 evening.** The owner merged the workstream PR
(#59) and the outbox PR (#60), tagged `v0.2.10` at `2415029` (the #60
merge), and published the release (PEX sha256 `1b1be350…56be6b`). The
dogfood project then ran on the first v0.2.10 push with all three
agents — this workstream's resume session on 2026-09-06 evening ran
inside it (antigravity 1.1.24, codex 0.153.4, claude-code 2.1.261 all
on PATH; suite 552 green and mypy clean from inside). The owner then
rebuilt the base from the *released* PEX (`--source-revision 2415029`,
which the CLI checks against the PEX's embedded build record and
verifies as a public commit; it never checks source out) and pushed
it over the `v0.2.10` tag at 22:48 UTC, digest
`sha256:4bb691b556a2cb9acffa4c0adddd9ada66864ee3c81f4f00ca35e9df9056bf9c`,
because the first push embedded a pre-tag PEX from `bd8283b` (before
the matrix's own v0.2.10 pin). The agent repinned at the owner's
direction: matrix `embedded-18` carries the new digest; golden locks,
the dogfood lock, and both sample locks regenerated (samples pushed on
`three-provider-formation`: tictactoe `f1e2e6f`, trading-research
`687d245`). Consequence to know: the lock committed at the tag pins the
first push's digest, which stays pullable by digest on Docker Hub but
is no longer what the tag names; the release-candidate intake sent to
`project-management` describes the walk that would avoid this.
Remaining: the owner's smoke on the rebuilt base (a lock change means
the checkout's base-image authorization re-asks), the PR for this
repin, the 0.2.9 withdrawal, and the v0.2.9 pin's retirement.

**Walk status, 2026-09-06 night.** The owner withdrew 0.2.9: the GitHub
release and the Docker Hub tag are gone (verified from the capsule
against both APIs; the git tag `v0.2.9` at `f2c6818` still exists on
the remote, and the v0.2.9 manifest is still served by digest on Docker
Hub — retention, not a promise). The v0.2.9 pin is retired from the
matrix, explicitly, recorded in place and as D-0007's third 2026-09-06
amendment; `embedded-18` stands because nothing selected v0.2.9 once
v0.2.10 was pinned, so golden locks, the dogfood lock, and the sample
locks are unchanged. Suite 552 green, mypy clean. The branch was
rebased onto `main` (the #59 and #60 merges) and carries the repin and
the retirement, both awaiting the owner's PR. The 0.2.10 walk is
complete except for the owner's smoke on the rebuilt base.

**Sync question, 2026-09-06 night.** Seeing this branch's diff, the
owner asked whether the self-contained CLI and the runtime the base
embeds can ever be in absolute sync. Diagnosis: not while the CLI pins
the base digest and the base embeds the CLI, because a PEX pinning the
digest of the image that contains it is a content-hash fixed point;
what has to be in sync is narrower (the inside runtime never reads the
matrix). Three shapes and the workstream's preference (the launcher
delivers its own PEX into the formation at materialization) went to
`project-management` as intake
`2026-09-06-component-catalog-one-devcapsule-inside-and-outside.md`
(outbox `802adaf`). The owner will merge this branch to `main` as is.
Advice given on "rebuild a v0.2.10 CLI to capture the change": no; the
release workflow re-run on an existing tag compares the PEX
byte-for-byte with the published asset, so a rebuild means moving the
tag and deleting the release. The released 0.2.10 stays valid (its
pinned first-push digest is still served), the change ships with the
next version, and `main` should leave 0.2.10 behind after this merge.

Set by the product owner on 2026-09-02. v0.2.9 ships when:

1. ~~The Antigravity CLI component is implemented and owner-smoked, per
   the delivery contract and the license analysis.~~ Done 2026-09-02:
   smoke passed on the tictactoe sample (codium × antigravity,
   v0.2.8 base).
2. The open v0.2.8-validation bugs are fixed, "relatively" — meaning
   the recorded fix scopes, barring new discoveries:
   - [init/run answers not persisted as authorizations](../../bugs/devcapsule/2026-09-02-init-and-run-answers-not-persisted-as-authorizations.md)
     (**closed 2026-09-03**: the owner exercised a different-base
     selection at init with the v0.2.9 CLI — daemon-inspected local
     selection, informed consent, recorded against the image ID — and
     signed off "thoroughly as expected, no trace of previous
     behavior"; the launch path no longer prompts, so run-once answers
     travel the config grammar under a declared never-persisted
     contract)
   - [formation identity claims an entrypoint the recipe never sets](../../bugs/devcapsule/2026-09-02-formation-identity-claims-an-entrypoint-the-recipe-never-sets.md)
   - [the authorization grammar cannot express denial](../../bugs/devcapsule/2026-09-02-authorization-grammar-cannot-express-denial.md)
     (owner-triaged onto this list 2026-09-02; **ruled and fixed
     2026-09-03** by the `none` ruling — denial is a value: bool nodes
     take `false`, string nodes their deny spelling, and `none`
     resolves to the deny value at decision time. The set-family half
     of the same ruling records explicit omissions in
     `omitted-values`, absent from the runtime config, overridable at
     `project run`. Closes on the owner's hardened relaunch)
   - [the codium setuid sandbox crashes under the development-sudo posture](../../bugs/devcapsule/2026-09-02-codium-setuid-sandbox-crashes-under-development-sudo.md)
     (**closed 2026-09-03**: the owner's smoke on the v0.2.9 base
     confirmed codium launching cleanly with development sudo enabled —
     the exact posture that aborted. Fixed 2026-09-02 by superseding
     the 2026-08-31 sandbox decision — renderers run `--no-sandbox`
     under uniform full hardening for as long as we can, per the
     [renderer-sandboxing design note](../../design-notes/devcapsule/renderer-sandboxing.md);
     the narrow grant, the `setuid-helper` declaration, and the
     recipe's chrome-sandbox 4755 step are removed, `--no-sandbox`
     travels as template data, codium recipe-version 2)
   - [antigravity's state is wider than the analyzed path](../../bugs/devcapsule/2026-09-02-antigravity-state-wider-than-the-analyzed-path.md)
     (`~/.gemini/config/projects` walled off by the nested slot's
     root-owned parent; **fix applied on the branch** — the slot now
     covers `~/.gemini` whole, changing the template digest and so the
     canonical image identity — awaiting the owner's re-smoke)

New bugs found on the way join the list by owner triage rather than
automatically blocking the release. Root-caused and fixed on the
branch the same day it was logged:
[codium relaunch intermittently crashes its first renderer](../../bugs/devcapsule/2026-09-02-codium-relaunch-renderer-crash-after-clean-exit.md)
(owner-confirmed `/dev/shm` exhaustion; the surface now declares
`shared-memory-size = "1g"` and the launcher sizes the container's
shm accordingly).

## Track 1 (integrated)

Track 1 is implemented end-to-end as of 2026-08-31, on branch commits
`f886872..7c496b2`, and live-verified from inside a capsule against the
host daemon: `init --need node --need frontend-ide` derives a codium lock
from matrix `embedded-2`, materialization builds the canonical image from
the checksum-verified VSCodium 1.126.04524 release, and `project run`
launches the surface from its plan-declared state slots with a healthy
sandboxed renderer tree and persisting `user-data`. Product-owner rulings
of 2026-08-31 are executed: capability `frontend-ide` selects codium
(`python-ide` still selects PyCharm; exactly one per lock), both
`vscode_with_claude` and `codium_with_claude` trees are retired, and the
surface keeps Chromium's setuid renderer sandbox under a narrow capability
grant — see the
[setuid sandbox design note](../../design-notes/devcapsule/vscode-sandbox-setuid.md)
for the collision with default hardening that forced the ruling.
(Superseded 2026-09-02: the sandbox ruling was reversed after the
sudo-posture crash — renderers now run `--no-sandbox` under uniform full
hardening; see the
[renderer-sandboxing design note](../../design-notes/devcapsule/renderer-sandboxing.md)
and the sudo-sandbox entry under *Release Target: v0.2.9*.)

The product owner's smoke sign-off arrived 2026-09-02: codium ran the
tictactoe sample end-to-end on the **v0.2.8 base** (no runtime-PEX
override), and the D-0008 history recorded the known-good configuration
(generation `20260902T075529Z`). That run is the verified edge behind the
`embedded-3` matrix advance: the v0.2.8 base pin
(`sha256:8be27a77…f336db`) and the codium×v0.2.8 edge are in the matrix,
so codium-only needs now resolve to v0.2.8 while every formation with
still-unproven components stays on v026. The smoke also surfaced two open
init/run authorization bugs (see the 2026-09-01 and 2026-09-02 bug
records); the 2026-09-01 one is fixed, the 2026-09-02 one is scheduled
after this integration. The branch is ready for the owner to open the
codium PR.

Also on this branch, at the owner's direction on 2026-09-01 while preparing
the v0.2.8 release: the distribution version is now authored solely in
`pyproject.toml`. The checked-in `_build_info.json` and importable
`__version__` are deleted; a missing build record now *defines* a
source-form run, whose identity derives from the authored file (installed
metadata is only a fallback — editable installs freeze their metadata at
install time and go stale across bumps). Built artifacts are unchanged:
`build-pex.sh` still stamps the full record, and `read_pex_build_info`
still vets artifacts without executing them. `bump-version.py` now guards
one file, so a bump is a single edited line. The release and validation
process this serves is now recorded in
[the release process note](../../implementation-notes/devcapsule/2026-09-01-release-and-validation-process.md),
including the owner's 2026-09-01 validation that the 0.2.8 client runs
correctly against the v026 base for the surfaces that base already knew.

Also on this branch, at the owner's direction on 2026-09-01: D-0008
(known-good checkout configuration history) is decided and implemented.
`project run` exiting zero records the checkout record and its generated
resolution as a stamped generation under the XDG state home
(`config-history/<creator>/<slug>/<UTC-stamp>/`), iff no existing
generation holds identical content — success is the only writer, so every
entry is safe to restore by hand-copy. A guided `config history`/
`restore` command surface is recorded follow-on work in the decision.

## Previous Resume Checkpoint (2026-09-07)

**Paused 2026-09-07 by the product owner; everything committed, PR #61
(repin, v0.2.9 pin retirement, sync-thread record) and the outbox
(intake `one-devcapsule-inside-and-outside`) merged to `main`; working
tree clean.** The 0.2.10 walk is complete: release tagged and
published, base rebuilt from the released PEX, 0.2.9 withdrawn and its
pin retired. On resume, in this order:

1. **Re-verify external state**: `main` is at or past the #61 merge
   (`1fb34c2`); Docker Hub serves `v0.2.10` at digest `4bb691b5…56bf9c`
   and no `v0.2.9` tag; the git tag `v0.2.9` (`f2c6818`) exists unless
   the owner deleted it.
2. **Ask the owner** whether the smoke of the rebuilt v0.2.10 base ran
   (dogfood, tictactoe); it is the evidence for converting the
   provisional entries in item 2 of the earlier list below.
3. **Version on `main`**: `main` still says 0.2.10 after the tag, so a
   PEX built from it would be mislabeled; the bump to the next version
   is the owner's call and has not been made.
4. **Project-management intake awaiting disposition** (sent by this
   workstream, not this workstream's to act on): the release-candidate
   concept, internal naming, and the inside-versus-outside sync
   decision, whose outcome decides whether the matrix keeps pinning
   base digests at all. Do not start any of the three shapes here
   without that disposition.

The 2026-09-06 evening resume note follows for the record.

**Resumed 2026-09-06 evening inside the dogfood capsule on v0.2.10;
the repin to the rebuilt base is committed and pushed, working tree
clean.** The tag, the release, PR #59 and PR #60 are done (see *Walk
status, 2026-09-06 evening*); the afternoon's pause list below is
updated in place. The state to re-verify on resume, in order:

1. **Owner actions outstanding** (nothing for the agent until they
   land): smoke the rebuilt v0.2.10 base
   (`docker.io/mycodespaceai/devcapsule-base:v0.2.10`, digest
   `sha256:4bb691b5…56bf9c`, built from the released PEX) on the
   dogfood project and, if desired, tictactoe; open and merge the PR
   from this branch (the repin and the v0.2.9 pin's retirement);
   decide whether the git tag `v0.2.9` (`f2c6818`) is deleted from the
   remote or kept as history now that the release it named is
   withdrawn. ~~Withdraw 0.2.9 from GitHub and Docker Hub.~~ Done
   2026-09-06 night, verified.
2. **Agent follow-ups, gated on those**: ~~retire the `v0.2.9` pin~~
   done 2026-09-06 night (matrix comment, D-0007 third amendment);
   convert the provisional entries the smokes evidence (PyCharm,
   claude-code 2.1.236/2.1.261, codex 0.153.0/0.153.4) once the owner
   confirms which smokes ran on the rebuilt base, and close the codex
   bug record and the formation-identity record's entrypoint half on
   the "reused canonical environment" second run.
3. **Open Threads** below carry the rest; the ones the owner is most
   likely to pick up next: the `config need` layering ruling (point
   (a)), the `use_legacy_landlock` deprecation at the next codex
   advance, and `resolve`/`run` not yet reading
   `unverified-combinations` back to a collaborator.

Deliberately not preserved: the scratch checkouts
`/home/devcapsule/codium-smoke-tictactoe` and
`/home/devcapsule/codex-seed-smoke` (host-backed, reusable but
disposable), the smoke formations they built, and the session's
scratchpad. Environment fact worth remembering: base builds from this
capsule need `images build --network host`; the daemon's bridge network
cannot resolve DNS here.

Session paused 2026-09-03, everything committed and pushed. The
2026-09-02 pause state below is superseded by the day's entries above
it; the standing owner actions at this pause: open the integration PR
for the working branch (the antigravity component and the whole
v0.2.9-validation stretch are owner-smoked), and merge
`component-catalog/outbox` so its two intake items reach
`project-management` on `main`: the upgrade-experience feature
(2026-09-03) and, at the owner's direction on 2026-09-04, the brief
research/design on automated per-component version validation
(`7421a22`) — whether automated tests can stand as the verification
evidence behind matrix edges when versions advance, folded into the
upgrade story's "who verifies, what evidence gates the advance"
strand; the owner framed timely advances as a V1 concern because
running obsolete or potentially CVE-marred versions is a poor user
experience. The evidence behind it: all three agent CLIs drifted
within the two days 2026-09-03/04 (claude-code 2.1.236 stable vs
2.1.260 latest; codex 0.153.0 → 0.153.2; antigravity 1.1.24 → 1.1.26
on a latest-only channel).

Previous pause, late 2026-09-02, branch head `d8f833c`: The antigravity component is validated and
PR-ready — the owner opens the PR per the integration cadence. The
same day also executed, owner-ruled: the state-slot/home-ownership
rulings, the codium `/dev/shm` fix (640m), and the passthrough
denylist for launcher-owned docker options. Suite green (516), mypy
clean.

Resume with, in order:

1. ~~The two v0.2.9 bugs awaiting owner rulings~~ **Both ruled, fixed,
   and smoke-verified by 2026-09-03**: the codium sudo-sandbox bug
   (closed by the owner's v0.2.9 smoke — codium runs with sudo enabled)
   and the denial grammar (closed by the `none` ruling — denial is a
   value). The 2026-09-03 smoke on the v0.2.9 base also first-exercised
   the regenerated lock chain (`embedded-7`, codium recipe 2, new
   canonical identity) and the whole authorization grammar rework
   end-to-end. The 2026-09-03 five-way smoke (codium × antigravity ×
   claude-code × codex on the v0.2.9 base) then confirmed **everything
   working** — the owner's blanket sign-off closes the antigravity-state
   record (widened `~/.gemini` exercised live, no hand repair), the shm
   record (clean relaunches on the declared 640m), and the
   denial-grammar record, and converts the two provisional agent gen2
   edges into owner-smoked evidence. The runtime-PEX override is
   retired for all codium compositions. (Correction to an earlier
   over-claim in this file's history: two release-target bugs remained
   open at that pause — the scoped ones in item 2 below; the init/run
   authorizations record then closed later on 2026-09-03 on the
   owner's hands-on base-selection check.) Same day, at the owner's direction, claude-code
   advanced to 2.1.236 (the Fable 5.1 release; sha256 computed locally
   and matching the vendor manifest, binary executed hands-on) with
   provisional gen1/gen2 edges pending the next dogfood run and codium
   smoke — the repo's own dogfood lock is updated so this workstream's
   capsules get it too (matrix `embedded-9`). The owner confirmed the
   upgraded CLI working the same day ("as well as expected"); the
   provisional 2.1.236 edges convert when a recorded formation run
   names its base. The upgrade experience itself went to
   `project-management` as an intake item at the owner's direction
   (2026-09-03, via this workstream's first outbox delivery):
   upgrade-friendly messages, obsolescence warnings, and the project
   of upgrading, as an important V1 feature.
2. **The next work when the session resumes**: the release's remaining
   gate is now a single bug — the
   formation-identity/entrypoint-claim record (its enforcement half
   coordinates with `contained-display`, and its image-lifecycle half
   is now also referenced by the upgrade-experience intake sent to
   `project-management`). The init/run-authorizations record **closed
   2026-09-03**: the owner picked up a different base at init with the
   v0.2.9 CLI and signed off the UX as thoroughly as expected, no trace
   of the previous behavior — the base-selection rework covers symptom
   A, and the launch path no longer prompts (run-once answers travel
   the config grammar under a declared never-persisted contract), which
   removes symptom B's accept-and-drop prompt class by construction.
3. Agent smokes on a gen2 base (claude-code, codex) to add their
   substrate edges and retire the runtime-PEX override for combined
   formations — antigravity already carries its gen2 edge. One smoke
   per component now covers every gen2 base release (see *Substrate
   Ruling*).
4. The `config need` checkout-local rebuild (open thread below).
5. Small closers: the antigravity-state and shm records close on the
   owner's next clean relaunches; the submodule gitdir un-absorb
   (applied by hand to the tictactoe sample checkout 2026-09-02 so git
   works inside the capsule) recurs on fresh `--recurse-submodules`
   clones and gets a record if the owner wants one; the two smoke
   observations (self-update setting, `agy` alias) stay open.

Original task order for this stretch, recorded 2026-09-02 at the
owner's direction (antigravity first; the config-need rebuild keeps
its ruling thread open):

1. **Validated 2026-09-02**: the owner's smoke passed the same day —
   antigravity working the tictactoe sample on the codium surface and
   the v0.2.8 base — after three launch-path bugs surfaced and were
   triaged (sudo sandbox posture, denial grammar, state-slot
   ownership; see *Release Target*). The provisional matrix edge now
   carries the smoke as its evidence, so per the integration cadence
   the component is PR-ready. Two open smoke observations remain for
   a later pass: whether the CLI needs a do-not-self-update setting,
   and whether the `agy` alias matters. Note the smoke ran with the
   ownership repaired by hand (`chown`); the widened `~/.gemini` slot
   and the launcher pre-creation get their first live exercise on the
   next rebuild-and-run. Implementation, as delivered: the
   Antigravity CLI component per the delivery contract — catalog
   `ComponentDefinition` (`components/antigravity_cli.py`), matrix pin
   (v1.1.24; the sha256 and the archive's single `antigravity` member
   re-verified hands-on 2026-09-02, artifact sha512 recorded as
   upstream provenance), `antigravity-agent` capability,
   `antigravity-download` authorization node, `/opt/antigravity-cli`
   materialization with PATH chaining, checkout-scoped
   `antigravity-cli/home` slot for `~/.gemini/antigravity-cli`, an
   optional `gemini-api-key` secret input, and inspection output
   (all verified live via `init` + `config list`). The matrix advanced
   to `embedded-4`; golden locks regenerated. Implementation calls the
   owner should review, made under recorded latitude:
   - The acquisition gate is now *generic*: `authorization_declarations`
     and init's acquisition elicitation derive every vendor gate from a
     new `ComponentDefinition.acquisition()` contract instead of the
     claude-code special case (wording and digests preserved).
   - "Default-selected" is implemented as an interactive init question
     (Enter = yes) asked only when the fresh need omits an agent *and*
     the grown need resolves; a noninteractive `--need` list stays
     authored-explicit, and re-inits never grow an existing need.
   - The antigravity×v0.2.8 verified edge entered the branch
     provisionally (codium precedent) and now records the owner's
     2026-09-02 smoke as its evidence.
   - Two smoke-time questions: whether the CLI needs a
     do-not-self-update setting (the pin makes self-update unwanted),
     and whether the `agy` alias matters (the recipe has no symlink
     mechanism; the binary lands as `antigravity` on PATH).
   Smoke path: `init --need node --need frontend-ide --need
   antigravity-agent` then `run` — codium + antigravity on the v0.2.8
   base needs no runtime-PEX override.
2. The v0.2.9 bug list (see *Release Target: v0.2.9*), and agent
   smokes on the v0.2.8 base to retire the runtime-PEX override for
   combined formations.
3. Settle the `config need` layering (the *checkout-local needs* open
   thread below) and rebuild the verb accordingly: default =
   checkout-local experimental need in the developer-owned record
   (ancillary components only, pinned into `devcapsule.resolved.toml`,
   verified-edge-checked against the locked base, droppable); the
   shipped manifest-editing machinery becomes the explicit `--project`
   promotion path. The antigravity component is the natural first user
   of the checkout-local need once it exists.

## Open Threads

- The graphical recursive successor passed inspection and exited normally with
  code 0 and no OOM. Owner requested merge readiness and declared this the last
  task for the workstream. Only delivery, final release promotion and closure
  remain; historical feature threads below are not authorization for more work.
  This run's stopped container and support files remain as evidence; preliminary
  test resources were cleaned.

- The full-base coverage correction is complete: RC3's own builder produced a
  local recipe-7 base and all seven tests passed. Retained image references and
  exact identity are recorded above. No Docker Hub base publication, lock repin,
  final release tag or GUI/provider acceptance was performed by this smoke task.
  Keep the release candidate frozen while reviewing the test harness separately.

- The downloaded-RC3 smoke request is complete: six Docker cases passed and
  the contributor/recursive source paths were explicitly excluded in executable
  mode. The artifact path above is an ignored download cache, not a new source
  artifact. PR #63/#64 resolved the prior integration/intake delivery blockers;
  older statements about those PRs below are historical. The new harness slice
  remains on the selected working branch for review. No release tag was moved.

- v0.2.11 final promotion remains pending. RC3 is the accepted candidate;
  RC0 failed before staging, RC1 retains a fully verified draft after publication
  lookup failure, and RC2 is a published prerelease superseded by RC3's packaging
  pins. Keep their tags/assets unchanged. Re-verify remote PR, main, tag, release
  and Latest state on resume. No credentials were changed and no main integration
  exception is claimed. PR #63 integrated source/acceptance and PR #64 delivered
  the workflow intake; PR #65 carries the final smoke slice. Everything required for the next step is
  committed; temporary local build/proof artifacts are reproducible and not records.

- **One base family, named plainly** (owner direction 2026-09-06,
  implemented on the branch, matrix `embedded-16`): `postgresql-client`
  gained its validation on the current family (package identity checked
  in the v0.2.9 image: psql 16.14, the build v026 shipped), which was the
  last thing keeping v026 selectable; v026 and the validations recorded
  only against it are retired; `substrate` is renamed `base_family` on
  `_BasePin` and `_VerifiedEdge` with documentation, and the single
  family is `ubuntu-24.04`. Recorded as D-0007's second 2026-09-06
  amendment; the release note's naming bullet follows. The wider rename
  (`_VerifiedEdge` itself, "edge" in identifiers) stays with the
  resolution-matrix cleanup backlog item. Golden locks regenerated
  (`pycharm-full` moves from v026 to v0.2.9).
- **`init --regenerate` versus `config`** (owner decision 2026-09-06:
  leave current `init` as acceptable for now; settle the semantics in
  `project-management`): a systematic walk found five gaps between what
  `--regenerate` says and does — `--need` derives the lock without
  rewriting the manifest's need (silent divergence, no digest check);
  identity flags accepted and ignored on a re-init; the owner's own
  checkout record is rewritten despite the design note's "never touches
  checkout records"; the report prints a recommendation's justification
  where its value belongs; two messages still name `--regenerate` as the
  sole remedy. The owner's principle: init operates on the source tree's
  `.devcapsule`, and updates the local run configuration only as a
  convenience; `config` owns the local half. Sent as intake 2026-09-06.
  Fixed the same day without waiting for the ruling (`eb395fa`): the
  report's value/justification swap (the intake's point 4), and
  `config need` now prints its own report — need changed or unchanged,
  lock regenerated or byte-identical, and every authorization node by
  how it was settled (answered, standing from the record, or applied as
  a project recommendation) — instead of init's "Project initialized".
  The layering itself is untouched and stays with the two items.
- **Refusal UX and the matrix's vocabulary** (ruled 2026-09-06): the
  owner took stock of every refusal, its grounds, and its audience
  (recorded as the first entry of the new `engineering-docs/blog/`) and
  ruled: a missing validation is disclosed, not refused — the message
  names the elements the experiment would run and offers `--unverified`,
  which `config need` now accepts too; only a missing toolchain refuses
  outright; the lock header and `unverified-combinations` say the same
  in the same words; matrix vocabulary (edges, substrates) stays out of
  adopter-facing text. Implemented on the branch; D-0007 amended; the
  UX note gained *When Init Refuses, And When It Only Discloses*; the
  2026-09-03 refusal bug record closed. Sent to `project-management`
  (intake 2026-09-06): design how the matrix learns from adopters'
  successful experiments and, later, gate matrix changes on mainline on
  a claim that every added combination ran. Not done: `resolve`/`run`
  still do not read `unverified-combinations` back to a collaborator
  (the design says "warn the same way, for now" — owner-facing only
  today); the internal rename (edge/substrate → validation/base family)
  waits for the resolution-matrix cleanup backlog item.
- **Codex sandbox configuration** (opened and ruled 2026-09-05): with
  the npm layout in place, codex's default bubblewrap sandbox failed
  under capsule hardening for a different reason — unprivileged user
  namespaces are denied by the seccomp filter and the empty capability
  set (tested inside this capsule: `unshare -Ur` and the bundled `bwrap`
  both refuse); Landlock worked but keeps the `sandbox` subcommand's
  workspace read-only and is deprecated in codex 0.153. The owner ruled
  *the capsule is the sandbox* and chose the seeded posture: a new
  `ComponentDefinition.state_seeds` contract lets a component declare
  default files for its slots; the host launcher writes them into a
  freshly created managed slot as the invoking user, only when absent,
  never into adopted directories. Codex seeds `approval_policy =
  "never"`, `sandbox_mode = "danger-full-access"`, `use_legacy_landlock
  = true` (validated against the 0.153.0 and 0.153.4 binaries; the owner
  validated the pair by hand in the dogfood capsule). The pin advanced to
  0.153.4 (matrix `embedded-14`, provisional edges). Still open: the
  codex edges' evidence predates the npm layout and the seed; the owner's
  next smoke of a codex-carrying formation on a fresh slot is the
  evidence, and `use_legacy_landlock`'s deprecation means the sandboxed
  fallback needs re-checking at the next codex advance.
- **Base rebuild** (updated 2026-09-05): the codex and claude-code gen2
  edges entered provisionally (matrix `embedded-8`) when the owner's
  five-way formation — codium × antigravity × claude-code × codex —
  could not resolve without them; the owner's 2026-09-03 smoke of that
  formation on v0.2.9 converted them. PyCharm's gen2 edge entered
  provisionally on 2026-09-05 (matrix `embedded-15`) on the evidence
  of the owner's dogfood day: the repository's own formation (pycharm
  × claude-code × codex) ran all day on the owner's local v0.2.9
  rebuild with this workstream developing inside it. It surfaced when
  the trading-research sample's `init --regenerate` refused pycharm ×
  antigravity for want of a shared base — the owner's
  `--authorize base-image` selection could not help because init
  resolves the lock before it reads the base answer (the
  base-as-config-node thread). Every current composition now resolves
  to v0.2.9 strictly; v026 is no longer selected by any need. A
  recorded formation run naming the pinned registry digest converts
  the PyCharm edge from provisional.
- **PyCharm slot-path migration** (recorded follow-up): PyCharm still
  travels the launcher's named state fields; every other surface uses the
  generic plan-slot mounts. Migrating PyCharm onto the generic path (and
  then retiring the named fields and the `pycharm/`-named plumbing) needs
  its own owner smoke.
- **Component update mechanism** (owner-stated future work, 2026-08-31):
  warn developers when pinned components have newer releases, and advance
  matrix pins after tests. Belongs to project-wide planning; not started.
- **Resolution-matrix sustainability cleanup** (owner-directed backlog
  item, 2026-09-02): the owner judged `resolution_matrix.py` "an unholy
  mess again" — acceptable as brute force to close bugs near-term,
  unsustainable as the growth path. The evidence: 651 lines of
  data-as-code (pin literals with embedded lock fragments, edge tuples,
  substrate constants, evidence strings, rulings living in comments),
  hand-edited 8 times in this workstream's first three days; every
  change hand-bumps `_MATRIX_VERSION` and regenerates golden locks. Each new base release,
  component bump, edge, or model amendment (three model changes on
  2026-09-02 alone: recipe-version per surface, substrate keying, the
  v0.2.9 pin) lands in the same module and inflates it further. The
  cleanup's shape is deliberately *not* designed here — it waits for
  the owner's direction and should be planned together with the
  component-update-mechanism thread above, which needs the same
  data/model separation to exist. The minimum step is done (2026-09-03):
  `scripts/regenerate-golden-locks.py` is checked in and imports the
  fixture needs from the test module, so the two cannot drift.
- **Per-component layer caching** (owner-stated future work,
  2026-09-05, stated with the entrypoint ruling): optimize the
  materialization build so component contributions are cached in
  layers that provide the parts — an `npm install` or `curl … | sh`
  should run once on an adopter's machine, not once per formation
  rebuild. Dovetails with the upgrade-experience intake (cheap
  rebuilds make pin advances cheap) and the formation-identity fix's
  thin-derivative build.
- **Launcher naming**: the generic project launcher still lives in
  `configurations/pycharm/_launcher.py` and `run_pycharm` launches every
  surface. Deferred as cosmetic churn until the PyCharm slot migration
  touches the same code.
- **Demo-project three-provider conversion** (executed 2026-09-03,
  awaiting the owner's spin and merges): at the owner's direction, both
  major demo projects now author formations carrying all three curated
  agent providers (claude-code, codex, antigravity), committed on a
  `three-provider-formation` branch in each sample repository.
  - *Tictactoe* (`22afd34`): the sequenced conversion is done — the
    committed `.devcapsule/` authors `frontend-ide, node` plus the three
    agents, and the regenerated lock (embedded-9, v0.2.9 base,
    claude-code 2.1.236) is byte-identical to the owner's five-way smoke
    lock, so the spin re-exercises a verified formation. The sequencing
    condition (a base whose runtime accepts codium plans) was met by
    v0.2.9.
  - *Trading-research* (`6ee2ccb`): `antigravity-agent` joins the need;
    the lock advances from the ancient `dogfood-v1`/v026 lock to
    embedded-9 on v0.2.9 via `--unverified` (the flag's first real
    outing), with exactly one named unverified combination — pycharm
    2026.2.0.1 on the gen2 substrate. The owner's spin of this formation
    is the pending evidence for the pycharm gen2 edge; if it passes,
    that edge enters the matrix and every surface family is on v0.2.9.
  - Both regenerations ran non-interactively from the capsule; init's
    loud missing-answer refusal named the exact `--authorize` remedies
    (the reworked grammar behaving as designed). Owner actions: spin
    each project (`init` then `run` on a checkout of the branch), merge
    the sample branches, then the monorepo submodule pins advance.
  - Before the spins, the owner relayed codex's own update notice and
    directed the pin advance to **codex 0.153.0** (matrix
    `embedded-10`): tarball sha512 verified against the npm registry
    integrity, sha256 computed from the same download, member set
    unchanged since 0.145.0, extracted binary executed hands-on
    (`codex-cli 0.153.0`); acp-version metadata carried forward
    unchanged. Three provisional entries pending the spins/next dogfood
    run: gen1 and gen2 edges plus the codex×pycharm coupling pair
    (0.153.0, 2026.2.0.1) — without the coupling pair, newest-verified
    selection would strand every codex×pycharm formation. The repo's
    dogfood lock regenerated onto embedded-10 (retiring the last
    hand-authored `dogfood-v1` lock), golden fixtures regenerated via
    the newly checked-in `scripts/regenerate-golden-locks.py`, and both
    sample branches carry the bump as follow-on commits (`4fffeb1`,
    `2ba6e03`). Suite green (537), mypy clean.
  - **Coupling removal ruling (2026-09-03, matrix `embedded-11`)**: the
    owner ruled the codex×pycharm coupling removed until further notice.
    The jetbrains-ai-assistant integration it stood for is not a
    delivery we want: the IDE's AI plugin installs its *own* codex copy
    and routes usage through the developer's JetBrains-account quota on
    JetBrains backends, ignoring the logged-in codex already on PATH.
    Code reading confirmed the coupling and the `integration`/
    `acp-version` pin metadata had no consumer outside the matrix —
    DevCapsule never wired codex into PyCharm; the lock merely
    advertised an integration nothing delivered. Both are gone: codex is
    a standalone CLI component, the coupling *mechanism* stays for
    future jointly-verified integrations, and every lock regenerated
    (goldens, dogfood, both sample branches — `1bea8e5`, `858dc5d`).
    Suite green (537), mypy clean.
  - **claude-code 2.1.261 (2026-09-04, matrix `embedded-12`)**: the
    owner directed the advance to the vendor's latest (2.1.236, though
    still the vendor's `stable` tag, stays as a prior pin). The
    linux-x64 binary's sha256 and size match the vendor manifest and
    the binary ran hands-on ("2.1.261 (Claude Code)"). Provisional
    gen1/gen2 edges per precedent, converting on the next dogfood run
    and the demo spins; goldens, the dogfood lock, and both sample
    branches regenerated (`e39f04d`, `e3dd3f0`). Codex 0.153.2 and
    antigravity 1.1.26 remain available upstream, awaiting the owner's
    call on advancing before or after the spins. Suite green (537),
    mypy clean.
  - **Formation-identity fix, entrypoint half (2026-09-05)**: ruled by
    the owner ("base carries no real entrypoint; the launcher sets it
    in the derived image; an entrypoint-only rebuild is almost a
    no-op") and implemented the same day: the materialization recipe
    now emits `ENTRYPOINT`/`CMD` from the descriptor, verification
    compares the claim to the image's actual boot configuration,
    pre-enforcement images self-heal via a configuration-only rebuild
    onto the same tag (live-smoked: 0.92 s on a 7.58 GB formation),
    materialization explains *why* it runs (first formation, or the
    descriptor fields differing from the nearest existing one), and
    prior formation images are reported with sizes rather than
    silently accumulating. Reap-vs-cleanup-verb remains the bug's open
    owner decision; base-without-entrypoint lands with the next base
    release. Awaiting the owner's smoke. Suite green (542), mypy
    clean.
  - [The resolution refusal names only the last base tried and no remedy](../../bugs/devcapsule/2026-09-03-resolution-refusal-names-only-the-last-base-and-no-remedy.md)
    — logged from the owner's first spin attempt, then **ruled and
    fixed 2026-09-05** at the owner's direction: every refusal now
    lists each base's gap newest-first and names `--unverified`
    (adopters must be able to try new combinations and report back);
    an already-`--unverified` refusal says the flag cannot help
    instead of recommending it again. Closes on the owner seeing the
    new message in practice.

- **Resolution-matrix redesign** (implemented 2026-09-01): the owner
  accepted D-0006 and D-0007 and the implementation is on this branch.
  `platforms.py` owns the `Platform` enum and the unified XDG derivation
  (`platform_alias` and three duplicate derivations retired); the matrix
  resolves through `MATRICES[platform].resolve(need)` over verified
  edges/couplings, byte-identical to the pre-refactor generator (golden
  fixtures under `tests/resources/golden_locks/`) and reconstituting the
  dogfood formation from the repo's own `.devcapsule` (tested). Recorded
  implementation decision: `devcapsule-base:v0.2.8` exists but is not
  fully tested, so it has **no edges in the matrix yet** — resolution
  keeps selecting v026; once the owner's smoke verifies v0.2.8
  combinations, adding its edges (and advancing the matrix version) is a
  data change, per the model. Fresh-checkout E2E evidence (2026-09-01):
  a clean clone of branch revision `eb3fbe0` from GitHub (submodules
  included) passed the full ladder from inside the dogfood capsule —
  `nox -s build` producing a public v0.2.8 PEX from the branch, `nox -s
  e2e` (4 Docker tests), and `nox -s recursive_dogfood_e2e` (preflight
  all-pass, peer-capsule dry-run, contributor bootstrap, recursive local
  clone). The checkout remains at `/home/devcapsule/e2e-fresh-devcapsule`
  with its built artifacts for the owner's v0.2.8 smoke.

- **Checkout-local needs** (awaiting owner ruling on point (a), then
  rebuild): the owner ruled that `config need` must default to an
  *experiment* — a need recorded only in the developer-owned checkout
  record, committing nothing. Point (b) is now answered by the
  2026-09-03 `--unverified` ruling: the escape hatch exists on `init` —
  strict resolution is always tried first; only on refusal does
  `--unverified` fall back to the base with the fewest unverified
  combinations, warns gently, and names each one in the committed lock
  (scalar `unverified-combinations` plus a header warning). The local
  layer reuses the same semantics when built. Still awaiting (a):
  two-layer verb — `config need X` local by default, `--project`
  promotes via the already-shipped manifest machinery. Also proposed: local needs
  are ancillary-only (surfaces are lock-level), pins for local
  components recorded in `devcapsule.resolved.toml`, `--drop` for
  removal, and distinct labeling in inspection and the run manifest.
  Not preserved from the session: no code for the local layer exists
  yet; only the manifest-editing verb (`46cec03`) is on the branch.

## External State And Risks

- The Antigravity license and redistribution analysis is a gate, not a
  formality: Claude Code's analysis forced per-developer download after terms
  authorization. If Antigravity's terms forbid even cached local images, the
  delivery contract above needs the product owner again.
- The chess-club sample project named as the ledger row's acceptance evidence
  belongs to `sample-projects` (paused); acceptance may need that workstream
  or an interim stand-in.
- The smoke-test half of validation is manual and product-owner-bound, so
  integration pace is bounded by owner availability; plan sessions to end at
  smoke-testable points.
- Reproducing the codium smoke from a capsule: a scratch checkout of the
  `typescript_tictactoe_5inrow` sample lives at
  `/home/devcapsule/codium-smoke-tictactoe` (host-backed, so the external
  daemon can mount it), a current-tree PEX at
  `/home/devcapsule/devcapsule-smoke.pex`, and the launch is
  `devcapsule project --path . run` plus the PEX override volume from *Open
  Threads* with the pex path translated to its host form. Raw passthrough
  docker options are not bind-translated, so the override source must be
  the host path.

## Workstream Document Index

- [Release candidates and maintenance branches (proposal)](release-candidates-proposal.md)

- [Antigravity CLI: license and redistribution analysis](antigravity-cli-license-and-redistribution-analysis.md)
  (2026-09-02, the ledger gate for track 2)
