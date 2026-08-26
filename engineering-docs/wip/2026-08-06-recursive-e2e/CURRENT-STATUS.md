# Workstream Current Status: Recursive Dogfood E2E

Mnemonic: `recursive-e2e`

Start date: 2026-08-06

State: resumed 2026-08-26. The v027 preparation is merged to `main` through
PR #41; the distribution version is advanced to 0.2.1 and the complete e2e
and recursive-dogfood-e2e suites pass against the new argparse CLI. On
2026-08-26 the owner re-sequenced: the engineering improvements (including
the `project_configuration.py` Hoare remediation) move past v027 to v028 or
later, and the owner is trying a local build first. The release identity is now unified
with the package version (0.2.7, tag `v0.2.7`). Next are the owner's
release acts, then Stage 7 per the owner's sequencing

Integration target: `main`

Requirements: `R-PRODUCT-002`, `R-SCOPE-001`, `R-DOCKER-001`

## Goal

From the accepted running v024 dogfood container, use a clean clone of a later
DevCapsule revision to build and launch a successor environment while proving
source identity, host-boundary authorization, persistence, and safe cleanup;
also own the v026 base and executable deliverables delegated on 2026-08-16.

## Branch Association

The active branch is `recursive-e2e/stage-4`, created from remote `main`
revision `432d2b4` after the multiple-stream workflow bootstrap was archived
successfully. The original `milestone/recursive-dogfood-e2e` branch predates
adoption and remains the documented historical exception; it is no longer the
active continuation branch.

## Current State

- Stages 0 through 5 are complete. Stage 4 was reopened and completed again
  after the v025 redistribution-license remediation.
- On 2026-08-12 the product owner explicitly closed Stage 5. The unexecuted
  authorization-negative Docker/network/sudo plan proof was transferred to the
  V1 backlog and does not reopen Stage 5.
- The Stage 6 live launch slice succeeded: the production planner launched a
  detached v025 successor and the independent inspector passed. The later
  hardening and scoped failure-path work described below completed the stage.
- The Stage 6 inspector is now hardened and proven live. It compares a launched
  successor against a complete machine-readable expected plan instead of four
  spot-checked fields, and the retained plan is bound to the run manifest by
  digest so a later independent inspection cannot be relaxed silently. The
  external-removal behavior now has a real-Docker E2E: it starts the v026
  embedded PEX runtime, removes the exact test-owned capsule with `docker rm
  --force`, and proves independent inspection reports failure rather than
  stale success. Recovery of support resources after launcher loss is now an
  explicit V2 task and is not a Stage 6 or V1 closure condition.
  The product owner replaced the remaining cleanup-proof proposal with a
  simpler GUID-derived naming rule: cleanup accepts the random run ID and
  derives the exact Docker name rather than accepting an arbitrary target or
  re-proving labels. That rule is implemented and tested. The launcher also
  injects the same value as `DEVCAPSULE_RUN_ID` so the successor can identify
  its own run. Stage 6 is complete.
- Work resumed on the conforming `recursive-e2e/stage-4` branch from current
  remote `main`.
- Stage 3 proved an exact, independent, credential-free local clone and a clean
  contributor bootstrap in recursive and laptop contexts.
- The first Stage 4 image embedded Claude Code. Its tag and exact manifest were
  removed after Anthropic's current license and terms were found not to clearly
  grant public binary redistribution. A verified agent-neutral replacement now
  owns the v025 tag.
- Base recipe version 4 keeps Node.js on `PATH` and adds Eclipse Temurin JDK 25
  LTS and Apache Maven with `JAVA_HOME`, `MAVEN_HOME`, and both `bin`
  directories on executable `PATH`.
- Claude Code is now an agent-neutral component input: after explicit
  checkout-owned terms authorization, local materialization downloads the
  checksum-pinned binary directly from Anthropic into `/opt/claude`. The public
  base and PEX do not contain the binary.
- The repository documentation was reorganized under `engineering-docs/`, and
  the Python distribution project moved from `devcapsule/` to
  `devcapsule-src/`.
- The recursive E2E now runs current-source readiness checks separately from
  immutable v024 PEX revision and checksum verification.
- On 2026-08-17 the product owner made a matched v026 base/CLI pair the current
  priority, with a directly executable, fully self-contained `devcapsule.pex`
  first. End users must not need Conda, Python, pip, or a virtualenv merely to
  run DevCapsule. This instruction was supplied directly because the earlier
  `project-management` delivery containing two v026 items never reached this
  workstream's intake on `main`.
- The self-contained implementation and exact-revision pair proof are
  complete. The PEX builder now emits a 39 MiB eager PEX scie containing
  stripped CPython 3.12.14 from Python Build Standalone release 20260814. A
  network-disabled `ubuntu:24.04` container with no Python installed ran both
  the local candidate and exact-revision artifacts successfully. Docker tag
  `mycodespaceai/devcapsule-base:ubuntu-24.04-v026` is published at registry
  digest `sha256:695f9eb6dd269dc694b3367f6a2570d500b938998d6f7aa3aa00e5d04cc7394a`.
  On 2026-08-17 the product owner selected GitHub Releases as the initial PEX
  download channel and required the official artifact to be built by the
  GitHub backend rather than uploaded from a contributor machine. The release
  automation is implemented. The first `v026` run
  (`32051615110`) built the PEX successfully but failed before publication
  because a job-scoped source-repository override contaminated a nested
  packaging test. The corrected replacement tag points to integrated commit
  `91d50b1`; backend run `32054479485` completed successfully and published the
  verified PEX and checksum. The base rebuilt from those exact released bytes
  was published and independently pulled by digest. The product owner also
  verified post-exit host-broker cleanup, completing the v026 acceptance.
- The proven v026 registry digest is now selected in the branch's committed
  Linux platform lock as the dogfood and development recommendation. Current
  guidance uses the immutable digest rather than the mutable discovery tag.
  Existing checkout authorization becomes stale intentionally so each
  developer must review and authorize the new exact formation input.
- On 2026-08-20 the product owner found that digest-only base authorization was
  not meaningful to a human reviewer. Commit `2152c81` adds build-information
  schema 2: official PEX builds carry their exact release tag, contributor PEX
  builds carry `local-v026`, base builds propagate the mnemonic into OCI
  labels, and locks may present `v026` beside the immutable digest without
  weakening what authorization records. The existing `v026` GitHub Release is
  immutable; publishing labeled official bytes requires a new patch tag such
  as `v026.1` after integration.
- The product owner then observed that both artifacts built by `nox -s build`
  still carried Python distribution version `0.1.0`. The distribution version
  is now an independently managed identity: `nox -s bump -- patch`, `minor`,
  `major`, or an explicit greater numeric version updates all checked-in
  version sources together. Builds reject disagreement. The workflow was used
  to advance the current candidate to `0.1.1`; release mnemonic and immutable
  source revision remain separate fields.
- On 2026-08-21 the trading-research adopter exposed that `devcapsule
  bootstrap` still delegated to a shell asset and did not install
  `WORKFLOW.md` from the self-contained PEX. Commit `f4ce952` makes bootstrap
  native, packages reusable `AGENTS.md` and `WORKFLOW.md` definitions
  separately from project-instance templates, and initializes either a
  single-stream handoff or a multiple-stream registry and reserved
  project-management workstream. Existing project state is preserved;
  reusable definitions change only through the explicit
  `--refresh-workflow-definition` option.
- On 2026-08-22 the corrected `v026.1` tag resolved to `main` revision
  `489642e`; the backend published the package-version `0.1.1` PEX and checksum
  after source, packaging, and clean-machine validation. The release PEX is
  40,274,243 bytes with SHA-256
  `353b98b62fa1cd30bc0f2da17effd8981e044d2f2fd91c306e6fa4092c70c493`.
- The native-X11 hyperlink bug is implemented at commit `6d8f53c`. An explicit
  `--host-browser` launch starts a same-user, URL-only Unix-socket broker on the
  physical host; the capsule's `xdg-open` dispatches through the matching PEX,
  and recursive launchers propagate only the inherited fixed socket. The
  bridge accepts absolute HTTP(S) URLs, never invokes a shell, does not expose
  the desktop session bus, is disabled by default, and is represented in the
  runtime and expected plans. Automated, packaging, read-only Docker-mount,
  and local recursive-dogfood validation pass. On 2026-08-17 the product owner
  confirmed that a hyperlink opened from the v026-derived PyCharm shell reached
  the physical host's default browser. On 2026-08-18 the product owner also
  confirmed that the v026 PEX removed its broker socket and associated runtime
  resources after exit.
- The current checkout's ignored `devcapsule-src/.venv` was found to predate
  the Python distribution rename: its activation scripts still prepended the
  removed `devcapsule/.venv/bin`, so `python` fell through to
  `/usr/bin/python`. The environment was rebuilt at its final path from
  `dev-requirements.txt` and the editable package. Developer instructions now
  use `.venv/bin/python -m nox` as the activation-independent primary path,
  retain ordinary activation as a supported option, and explain that a moved
  virtualenv must be recreated rather than reused.
- An audit request was pushed on `recursive-e2e/outbox` at `ebad342`, asking
  `project-management` to inventory promised work for this workstream and
  determine from its conversation/session evidence whether delivery failed
  because the communication protocol was incomplete, because the later outbox
  rule was not followed, or for another reason.

## Current Priority And Status

Current task: v027 preparation (directed item 2). Directed item 1 is
complete: PR #40 merged, tag `v026.2` points at `7920945`, and the backend
published the release on 2026-08-23 with `devcapsule.pex` (40,274,852 bytes,
SHA-256 `1210ad1cdf89b41e0562f289bc80a8804a4d0e26d236733a9f0795cdb91296c0`)
plus its checksum; verified against the live GitHub release on 2026-08-24.

v027 preparation status on 2026-08-24 (commits `466a202` through `a2eae96`
on this branch): the CLI moved from Click to an owned argparse framework;
the configuration-node registry, one-elicitation engine, and embedded
resolution matrix exist; `init` reaches the full settled postcondition with
three entry states and `--regenerate`; the config family speaks the settled
`VERB NAME VALUE` grammar (`bind NAME PROVIDER:VALUE`,
`authorize NAME VALUE [JUSTIFICATION]`, new `unset`); the `lock` stub is
retired; `run` gained run-once carriers and the `--` docker passthrough while
its bespoke flags dropped; `host-browser`, `docker-daemon`, and
`development-sudo` are always-available authorization nodes; click and
readchar left the product dependency set; the `R-COMPAT-001` fixture proves
the current client reads genuine released-v026.2 artifacts and v026-era
formation artifacts with no user action; user docs and the release-notes
draft carry the changed surface. Grammar and argparse decisions of
2026-08-23/24 are recorded in the v1-user-experience design note, and the
Click CLI brief is marked superseded.

Remaining before the release: only the owner's release acts — integrate the
branch, tag `v0.2.7`, backend publication. On 2026-08-26 the owner unified
the release identity with the package version, replacing the planned `v027`
mnemonic: `[tool.devcapsule].release-series` is deleted, the package version
was advanced to 0.2.7 so the patch digit echoes the old series ordinal, and
the mnemonic is now derived — official builds report `v<version>` and must
match the Git tag exactly, contributor binaries report
`v<version>-local-<platform>` (the build script's scie platform, today
`linux-x86_64`), and editable source installs report `v<version>-local`,
kept in lockstep with the version by the bump tool. v026-era mnemonics stay
readable and the build-information schema remains 2. The v027 preparation
itself reached `main` through PR #41 on 2026-08-25.

Unification validation on 2026-08-26: the full `nox -s build` gate passed
with mypy clean over 115 source files, 434 fast tests (12 deselected, 1
xfailed), all seven packaging integrations, and a local PEX reporting
version `0.2.7` with mnemonic `v0.2.7-local-linux-x86_64`. The release
workflow needed no change: its tag trigger and guards already accept
`v0.2.7`, and it already requires mnemonic equal to tag.

Re-sequenced by the owner on 2026-08-26: the `project_configuration.py`
Hoare remediation (directed item 3) and the other engineering improvements
below no longer gate v027. They are deferred to v028 or v029 — or v030 if
v027 proves flaky and stabilization fixes crowd them out — because the CLI
replacement was itself a large change and release experience should come
first. Stage 7 sequencing remains the product owner's call.

Deferred engineering improvements (v028 and later):

1. The `project_configuration.py` Hoare remediation, directed item 3 below:
   the four-owner module split and moving checkout-record creation out of
   `config list` into the resolve path. Its scope and the 2026-08-23
   diagnosis remain recorded in the directed-work section.
2. A testability seam at the Docker launch boundary, diagnosed 2026-08-26:
   argument construction is pure and well tested (`build_docker_args`,
   `build_codium_run_command`), but each launcher then calls
   `subprocess.run` directly (`configurations/pycharm/_launcher.py`,
   `configurations/codium_with_claude/_launcher.py`,
   `recursive_successor.py`), so no test between the unit and real-Docker
   e2e levels can assert what command a CLI invocation would execute. An
   injectable runner would close that gap. Diagnosis only; no design is
   settled.
3. Done — promoted by the owner the same day it was proposed. The release
   identity is unified with the package version; the settled value
   vocabulary is `v<version>` official, `v<version>-local` editable
   source, `v<version>-local-<platform>` contributor binary. See the
   unification entry in *Current Priority And Status*.

The list stays open: defects and cleanups surfaced while shaking out v027
join it rather than growing the v027 scope, unless the owner promotes one.

E2E validation on 2026-08-26, closing the gap that the new argparse CLI had
never run the real-Docker suites: from a pristine clone of `a684529` under
persistent home (the `checkout-mount` preflight check requires the checkout
to be Docker-mount-backed, so a `/tmp` clone cannot serve), `nox -s e2e`
passed 4 of 4 (contributor bootstrap, successor lifecycle, runtime image,
self-contained PEX) and `nox -s recursive_dogfood_e2e` passed 2 of 2
(recursive local clone, contributor bootstrap) with preflight READY,
`cleanup_complete` true, and no Docker mutation. The contributor-bootstrap
test also enforces a fully clean source checkout including untracked files,
so it cannot run from the owner's working checkout while `.idea` and
submodule-pointer drift are present; the clean-clone route is the way to run
it without disturbing that state.

Status: Stages 0 through 6, the backend-built standalone PEX releases, matching
Docker publication, immutable-digest pull and offline proof, functional
host-browser GUI acceptance including cleanup, and the v026 mainline
recommendation are complete. `origin/main` contains the completed follow-ups at
`489642e`, and `v026.1` is published from that exact revision. Stage 7 is now
active; the external-removal E2E and GUID-derived failed-launch cleanup provide
its starting boundary. Changed:

- PEX build metadata now distinguishes the official release mnemonic from its
  package version and source revision. `[tool.devcapsule].release-series`
  selects `v026`; local builds emit `local-v026`; the release backend passes
  and verifies its exact tag. Base images inherit
  `devcapsule.pex.build-mnemonic` and `org.opencontainers.image.version`.
- Platform locks may carry presentation-only `base.build-mnemonic`. The
  configuration and authorization UI leads with `v026` beside the full digest,
  while normalization, stored authorization, and freshness remain bound to the
  immutable reference and complete lock digest.
- The new `bump` Nox session gives developers an explicit package-version
  transition. It accepts `major`, `minor`, `patch`, or a greater
  `MAJOR.MINOR.PATCH`, updates package metadata, `devcapsule.__version__`, and
  editable-source build information together, and rejects invalid,
  non-advancing, or inconsistent versions. The PEX builder and full Nox gate
  verify that those sources agree before building. The current distribution
  was advanced from `0.1.0` to `0.1.1` through that command.
- `devcapsule bootstrap` and `devcapsule bootstrap project` now install the
  workflow through Python-native package resources. Reusable definitions live
  under `devcapsule.assets.project_workflow/definition`; separately rendered
  templates initialize adopter-owned status, requirements, index, bug, and
  multiple-stream coordination files. Bare bootstrap uses the process's
  current directory rather than ambient container `PROJECT_PATH`.
- `scripts/build-pex.sh` now emits only an eager native PEX scie, pinning Linux
  x86-64, CPython 3.12.14, and Python Build Standalone release 20260814. The
  embedded interpreter is stripped and makes no first-run download.
- Nox smoke checks execute the artifact directly instead of passing it to a
  host interpreter.
- `pex_clean_machine` builds the artifact and proves it in a network-disabled
  Ubuntu container after checking that no `python`, `python3`, or `python3.12`
  exists there.
- Packaging integration checks assert the native ELF boundary, retained ZIP
  metadata/provenance, eagerly embedded interpreter, and direct execution.
- User documentation now presents `devcapsule.pex` as the end-user path and
  makes Python-tool installation an optional developer alternative.
- `.github/workflows/release-pex.yml` builds from an exact numeric `v*` tag,
  runs source and packaging checks, proves the resulting PEX with networking
  disabled in Ubuntu with no Python, and only then creates a GitHub Release
  containing `devcapsule.pex` plus its SHA-256. It downloads the published
  assets and repeats the checksum, byte-identity, and clean-machine proof.
  Manual reruns fail if an existing Release does not byte-match instead of
  replacing published assets silently.
- The release workflow scopes `DEVCAPSULE_SOURCE_REPOSITORY` only to the PEX
  construction step. Packaging tests no longer inherit canonical release
  provenance, and the nested-repository integration test explicitly removes
  ambient source-repository and source-revision overrides before proving Git
  remote discovery. A source-level regression test pins the workflow scope.
- `DEVCAPSULE_PEX_UNDER_TEST` lets packaging and clean-machine tests select the
  exact backend-built or downloaded artifact without rebuilding it locally.
- `host-open` is a hidden PEX client for a launcher-owned physical-host broker.
  `project run`, `run-image`, and `pycharm run` expose the explicit
  `--host-browser` capability; `--no-host-browser` can override it. The broker
  uses same-UID peer credentials, a private mode-0600 Unix socket, an
  HTTP(S)-only JSON protocol, bounded frames and timeouts, rate limiting, and
  argument-vector host `xdg-open` execution. Recursive launches can translate
  and propagate the inherited read-only socket but cannot manufacture one.

Validation on 2026-08-17: full `nox -s build` succeeded; mypy reported no
issues in 96 files; 319 tests passed with 9 deselected; five packaging
integrations passed; the separate clean-machine Nox proof passed against the
exact revision-bearing artifact selected through `DEVCAPSULE_PEX_UNDER_TEST`.
The release workflow YAML and each embedded shell block passed local syntax
validation. Two independent strict builds from pushed workflow commit
`c27b45ad65e95ccc62c609ed8f153846a4b060ec` were byte-identical at SHA-256
`8e05e7f721e72cea5f8fcdc77f37a048c323201b3107ac18323347fcb741879e`,
validating the workflow's fail-closed rerun rule; that exact artifact also
passed the network-disabled clean-machine proof. Candidate
PEX SHA-256 `b7e2fd81818f141bd8dad99c9e41eeb6db58a6f31cf1b287f75a901f0e352fdb`
matches both the candidate image label and the bytes at
`/opt/devcapsule/bin/devcapsule.pex`.

Host-browser validation on 2026-08-17: the full `nox -s build` gate passed with
340 tests and 10 deselected; mypy reported no issues over 99 files; six
packaging integrations passed. The built eager PEX crossed the real
`xdg-open` path and delivered a metacharacter-heavy URL unchanged as one host
opener argument. A separate `ubuntu:24.04` Docker proof used networking
disabled, the mapped unprivileged UID/GID, the PEX mounted read-only, and the
broker socket mounted read-only; the exact URL arrived successfully. Local
recursive dogfood run `24b3fd2dfb2d58f010b7d1652967c007` reported ready and
passed both selected E2Es in 28.81 seconds, with cleanup complete and no Docker
mutation. The final physical-host launch used v026-derived environment image
`devcapsule-local-pycharm:5dfa686ce5dc74688955`, image ID
`sha256:df1384478c44e0b2cb06864912878f9674a3495cefbd9e0d47bf9cd18b8ced7b`,
whose source revision and embedded PEX digest match the v026 Release. Runtime
plan version 1 named the `browser-open` integration and the same-user broker
socket was mounted read-only at `/run/devcapsule-host-open.sock` with mode
0600. The product owner then confirmed that a hyperlink opened from the
PyCharm shell reached the physical host's default browser. Functional GUI
acceptance therefore passes; cleanup of this live broker remains to be
observed after IDE exit.

Developer-environment repair validation on 2026-08-17: after rebuilding the
ignored environment, activation sets both `VIRTUAL_ENV` and the first `PATH`
entry to the exact `devcapsule-src/.venv` directory; `command -v python`,
`sys.executable`, and `sys.prefix` all resolve inside it while
`sys.base_prefix` remains `/usr`. The locked Nox installation reports version
`2026.4.10`. The user's exact activated `python -m nox -s build` command then
passed the full dirty-tree gate: mypy found no issues over 99 files, 340 tests
passed with 10 deselected, six packaging integrations passed, and the local
self-contained PEX plus CLI smoke checks passed. Direct
`.venv/bin/python -m nox` invocation was separately resolved and enumerated
the expected sessions without consulting system Python.

Release-run repair validation on 2026-08-17: failed GitHub run `32051615110`,
job `95452067400`, passed source tests and type checks, built the standalone PEX
for `cdf1b5b`, then failed one of six packaging integrations because the nested
fake repository received `https://github.com/ccozianu/devcapsule` from the
job environment instead of discovering its own origin. The focused test now
passes with that exact contaminating variable deliberately present. The full
dirty-tree `nox -s build` gate also passed under the same ambient condition:
mypy found no issues over 99 files, 341 tests passed with 10 deselected, all six
packaging integrations passed, and the local PEX and CLI smoke checks passed.
The product owner replaced the failed tag after integration. Replacement
backend run `32054479485` succeeded and published
`https://github.com/ccozianu/devcapsule/releases/tag/v026` on 2026-08-17.

Exact-revision evidence: release tag `v026` points to integrated source commit
`91d50b1dd15468a706f5f965ae0dd6197ffd9ab7`. The published
`devcapsule.pex` is 40,227,530 bytes with SHA-256
`b7959c52f90b0e6c5043be787045968f94416e0b0faf75465696d47e53bab11c`;
its downloaded checksum verifies and `version --json` reports that exact
repository and revision. Published image
`mycodespaceai/devcapsule-base:ubuntu-24.04-v026`, image ID
`sha256:cf72aa7b7926ff480f3b4fbec1b2e5c02e43044519d3679104dda1e7430dfdb2`,
was rebuilt from those released bytes and published at immutable registry
digest `sha256:695f9eb6dd269dc694b3367f6a2570d500b938998d6f7aa3aa00e5d04cc7394a`.
Pulling that digest resolved to the exact image ID above. Its labels and
embedded PEX digest match the Release, and a network-disabled container passed
embedded checksum, `version --json`, Python, Node.js `v22.23.1`, `javac
25.0.4`, and Maven `3.9.16` probes.

Recommendation-transition validation on 2026-08-17: an isolated developer
configuration root authorized the new lock-selected digest, generated a fresh
resolution, and reported `base-image` as `authorized`; no real checkout-owned
authorization was changed. The full `nox -s build` gate passed with mypy clean
over 99 files, 341 tests passing with 10 deselected, all six packaging
integrations passing, and the local self-contained PEX plus CLI smoke checks
passing. The dirty-tree gate correctly skipped only the revision-bearing public
PEX.

Build-mnemonic validation on 2026-08-20: schema-v1 PEX reading remains
compatible; schema-v2 unit and authorization-display coverage passes. The full
source gate passed with 348 tests and 11 deselected, mypy clean over 100 files,
and shell/source syntax clean. A freshly built PEX reported `local-v026` in
plain and JSON output; all six packaging integrations passed against those
bytes, and the network-disabled clean-machine proof passed without host Python.
The release guard rejected combining an official mnemonic with a local or
unpublished build.

Package-version validation on 2026-08-20: the focused version-management,
Nox, and build-information suite passed 22 tests. The complete dirty-tree
`nox -s build` gate passed with mypy clean over 102 source files, 358 tests
passing with 11 deselected, all six packaging integrations passing, and the
local self-contained artifact reporting `local-v026` with package version
`0.1.1`. The dirty-tree gate correctly preserved any prior public artifact.
After commit, the complete clean-tree gate passed again and built both
`dist/devcapsule-local.pex` and the exact-revision `dist/devcapsule.pex`; both
reported package version `0.1.1` and mnemonic `local-v026`.

Workflow-bootstrap validation on 2026-08-21: the complete clean-tree Nox gate
passed at commit `f4ce952`; mypy found no issues over 105 source files, 366
fast tests passed with 12 deselected, and all seven packaging integrations
passed. Both local and exact-revision PEX artifacts were built and directly
smoke-tested. The PEX integration invoked bare `devcapsule bootstrap` from an
empty adopter directory and verified that its installed `WORKFLOW.md` exactly
matches the packaged reusable definition and that a single-stream
`CURRENT-STATUS.md` exists. Seven focused workflow-bootstrap tests cover
definition refresh, instance preservation, legacy handoff migration,
single-/multiple-stream initialization, idempotence, invalid declarations, and
incomplete multiple-stream rejection.

Host-browser cleanup acceptance on 2026-08-18: after the accepted v026 IDE
exited, the product owner verified that the PEX removed the broker socket and
the associated private runtime resources. This closes the final v026 GUI
cleanup boundary; a socket belonging to a later active IDE session is expected
to exist until that session exits.

External-removal E2E validation on 2026-08-18: a unique test-owned container
started the lock-recommended v026 image through its real embedded PEX runtime.
The test removed that exact container by its GUID-derived name with `docker rm
--force`; independent successor inspection then failed with `cannot inspect the
exact successor container` and retained the vanished ID as diagnostic evidence.
The focused real-Docker E2E passed. Failed-launch cleanup now accepts only the
run ID, derives `devcapsule-e2e-RUN_ID-successor`, and issues removal for that
name rather than an arbitrary or inspection-selected target. The full `nox -s
build` gate also passed with mypy clean over 100 files, 343
fast tests passing with 11 deselected, all six packaging integrations passing,
and the local self-contained PEX plus CLI smoke checks passing.

Run-ID self-reflection validation on 2026-08-18: the recursive successor plan
now injects `DEVCAPSULE_RUN_ID` with the exact random run ID used by the
container name, workspace, and cleanup API. Independent inspection requires
the in-container probe to return that exact value. The focused plan and
inspection suite passed with 65 tests, and the real-Docker E2E passed after
reading the value inside the running v026 container with `printenv`. The full
`nox -s build` gate passed with mypy clean over 100 files, 346 fast tests
passing with 11 deselected, all six packaging integrations passing, and the
local self-contained PEX plus CLI smoke checks passing.

## Last Task And Status

Last task: v027 preparation on 2026-08-24. Validation: every commit passed
the fast suite and mypy; the complete dirty-tree `nox -s build` gate passed
twice during the session (50 seconds each), including all seven packaging
integrations and the local self-contained PEX smoke checks, with a final
full-gate run after the Click retirement. The `R-COMPAT-001` fixture (three
tests) passed against artifacts generated by the actual downloaded and
checksum-verified v026.2 release PEX. Fast-suite totals grew from 366 to 433
tests across the session.

Product decisions taken with the owner during the session, all recorded in
the v1-user-experience design note: the settled configuration grammar
(provider-in-value bind, optional trailing justification, unset, carriers on
init and run), argparse replacing Click, silent no-recommendation for
unflagged noninteractive init intent questions, the `--` docker passthrough,
and the three host capabilities as always-available authorization nodes.

The previous task record follows.

Previous task: expose the launcher's random run ID inside the running
successor as `DEVCAPSULE_RUN_ID` and independently prove exact agreement.

Status: complete and proven through a real-Docker `printenv` probe, exact-plan
comparison, and an in-container readiness probe that rejects a different run
ID. The preceding inspector work remains proven live: on 2026-08-14 run
`482c34f24fc5c438da7b24ff172a619b` launched a successor through the
clean-clone PEX and passed the hardened inspection twice. A new
`devcapsule/recursive_successor_plan.py` derives an
`ExpectedSuccessorPlan` from exactly the translated `docker run` arguments that
a launch issues. `launch_successor` retains that plan as mode-0600
`expected-plan.json` beside the run manifest and records its SHA-256 in the
manifest; `inspect_successor` reloads it, refuses a digest or identity
mismatch, and compares it against `docker inspect`. The comparison covers
container and image identity, the container's inherited `devcapsule.*` image
labels, runtime user and working directory, every planned environment value,
exact mount-set equality including read-only mode and daemon-side source,
tmpfs, network and IPC mode, `Privileged`, `ReadonlyRootfs`, `CapAdd`,
`CapDrop`, `SecurityOpt`, `GroupAdd`, memory and PID limits, restart policy,
and restart count. The in-container probe now returns the SHA-256 of
`/etc/devcapsule/runtime-plan.json` and its mount options, so a substituted or
writable runtime plan fails the inspection.

The earlier live-launch result stands: run `b2093d85912fa34ac1324e1da26a9dcd`
authorized the exact v025 local image plus Claude acquisition, materialized and
strictly reused the canonical environment, and launched exact container
`7e92dcba38685c1b1cf508c6b26e8312454746ec51f186ed4043a510d9d51c93`. On
2026-08-12 the user confirmed that the new PyCharm window is visible and
usable. That inspection predates the hardening and used the weaker four-field
check.

## Evidence

- Live hardened-inspector proof on 2026-08-14, run
  `482c34f24fc5c438da7b24ff172a619b`. Its clone is detached at
  `c26d877acd006d1a05666696c5c672c70f5d2cd6`, has no remote, and imported no
  credentials. Clean-clone PEX SHA-256:
  `744f7805389769f78e006afb4ec5d0ebbde629877060aff389602a8dbc56873b`. Its
  provenance was built with `--allow-unpublished-revision` against
  `https://github.com/ccozianu/devcapsule` because that revision is committed
  locally but not yet published.
- The isolated checkout authorized the exact local base
  `sha256:9c806703213bc280b6378e52e037bc55df85b585b662e20ef06ad3bb1ae48173`,
  host Docker, host networking, development sudo, and the Claude Code
  download, all under the run root's own XDG configuration. No
  developer-owned checkout record was read or modified.
- Realization strictly reused the canonical environment
  `devcapsule-local-pycharm:2145e28bc7b8aca0eee0`, image ID
  `sha256:f3fa500c3811d2f838a56af224e61f15524de014fa4270174b14ec36e894dbee`.
  This confirms in practice that a devcapsule source change does not alter the
  formation identity, so neither a new base image nor a new materialized image
  was required for the hardened inspector.
- Successor container
  `9a2c3c787f2ea0577d2f95a117b986084a9e0a55e9852b4e3d0b558c69ad32f6`, name
  `devcapsule-e2e-482c34f24fc5c438da7b24ff172a619b-successor`, started
  `2026-08-14T10:12:46Z`. The launch-time comparison passed all eleven
  daemon-side checks: container and image identity, ownership labels,
  formation identity, runtime identity, environment, mounts, resource limits,
  security settings, restart policy, and running state.
- The independent `inspect-successor` boundary passed the same eleven checks
  plus `runtime_plan`, proving the in-container SHA-256 of
  `/etc/devcapsule/runtime-plan.json` equals the digest recorded at launch and
  that its mount is read-only in `/proc/self/mountinfo`. Tool probes returned
  Claude Code `2.1.227`, Codex `0.145.0`, Node.js `v22.23.1`, `javac 25.0.4`,
  and Apache Maven `3.9.16` with the expected `JAVA_HOME` and `MAVEN_HOME`.
- Bounded second-inspection stability result: a repeat independent inspection
  after a 90-second window returned the identical container ID, image ID, and
  full pass set, with `Running=true` and `RestartCount=0`.
- Retained `expected-plan.json` is mode 0600 and pins 17 mounts, 27
  `devcapsule.*` image labels, and 26 compared environment values, with
  `DISPLAY` classified as the sole pass-through value that is never compared
  or recorded. The run manifest contains no occurrence of the host workspace
  path, so redaction holds in production and not only under test.
- The development container `pycharm-isolated-costin-1786657961` was neither
  stopped nor modified during the launch or either inspection.
- Inspector hardening gate on 2026-08-13: full fast suite `290 passed` with
  `8 deselected`; mypy reports no issues over 90 source/test files; the
  `nox -s build` gate succeeded, including five packaging integrations. The
  public PEX was deliberately not rebuilt because the tree is dirty.
- The hardening adds 60 focused public-interface tests in
  `tests/test_recursive_successor_plan.py` and
  `tests/test_recursive_successor.py`. They cover plan derivation from the real
  launcher's arguments under both sudo and no-sudo shapes, retained-plan round
  trip and digest tampering, host-source redaction, and rejection of a missing
  mount, an unplanned bind/volume/tmpfs mount, a relaxed read-only mount, a
  substituted mount source, a substituted or writable runtime plan, label and
  formation-identity mismatch, environment drift, every modelled security and
  limit deviation, a nonzero restart count, malformed and ambiguous Docker
  output, and manifest/plan identity disagreement.
- The plan parser fails closed on any Docker flag it does not model, and a
  launcher-coupled test pins that model to `build_docker_args`, so a new launch
  flag cannot silently escape comparison.
- The comparator's field readers were validated against real daemon output
  from the running development container: `.Mounts` carries only `bind`
  entries with `Type`/`Source`/`Destination`/`RW`, tmpfs appears only under
  `HostConfig.Tmpfs`, absent capability and security lists are `null`, and the
  materialized image's 27 `devcapsule.*` labels are inherited into
  `Config.Labels`. All eleven daemon-side checks passed against that real
  inspection with no host source in the redacted evidence.
- Recursive dogfood E2E: `2 passed`, `1 deselected` in 30.74 seconds on
  2026-08-07.
- Commit `44fbe34` restored the recursive E2E after the Python distribution
  directory rename while retaining embedded-PEX build identity and SHA-256
  checks.
- The multiple-workflow finalization procedure completed successfully on
  remote `main` at revision `432d2b4`; the active branch starts at that exact
  revision.
- Focused recursive-preflight tests: `14 passed`.
- Mypy: no issues over 57 source files.
- Successor-content focused tests: `45 passed`; mypy reports no issues over 85
  source files.
- Full dirty-tree Nox gate: `226 passed`, `8 deselected`; PEX integration:
  `5 passed`. The expected local-only PEX was built and smoke-tested.
- The then-current v024 container still passed the two Stage 3 recursive E2Es
  when the missing launcher marker was scoped explicitly to the test process:
  `2 passed`, `1 deselected` in 82.95 seconds. That workaround was specific to
  the retired v024-derived control; later environments carry the marker.
- Successor source commits `da38cd7`, `0761940`, and `20b2ee1` are published on
  `origin/recursive-e2e/stage-4`. The last commit fixes public PEX provenance
  forwarding without exposing that override to nested integration tests.
- Retained Stage 4 run ID:
  `25f664fb3629f51be8e3894a0df8ffa7`. Its clone is detached at full revision
  `20b2ee1e7d2aa3b07f94270da624b882df1e3215`, has no remote, and imported no
  credentials.
- The clean retained-run gate passed mypy over 85 source files, `227 passed`
  with `8 deselected`, five packaging integrations, and public-PEX smoke tests.
- Public successor PEX SHA-256:
  `d52c6b9d6296c6b683e64e8ac130d7a4eb21bd33c7742f888e8d6244e1759a8b`.
- The unsafe superseded v025 had local image ID
  `sha256:c8f6dddbfaab7e412079cd89f9a5bdf631dd9c3b7ab963375a8f3302c1e7b066`
  and registry digest
  `sha256:7093cea8f1e06c10a437f3946dc7e3dd643271f071d17b6a140e4df763598fd3`.
  Both its tag and exact registry manifest were deleted on 2026-08-11; neither
  the tag nor old digest resolved before replacement publication.
- Replacement source revision:
  `c933ec38202719fbe1879846e5de48200136f9e3`. Clean Nox gate: mypy over 87
  source/test files, `229 passed` with `8 deselected`, five packaging
  integrations, and local/public PEX smoke tests.
- Replacement public PEX SHA-256:
  `976aa0708f0a247550cc8b594c461272af1b20dbc6146bfda54baba918a82f61`.
- Replacement v025 tag:
  `docker.io/mycodespaceai/devcapsule-base:ubuntu-24.04-v025`.
  Immutable local image ID:
  `sha256:9c806703213bc280b6378e52e037bc55df85b585b662e20ef06ad3bb1ae48173`.
  Published registry digest:
  `sha256:b8d355b497a9aa2fc5b2420db0c07227721e3cf7d3388b2ca81f3ed40fb86a7f`.
- Strict pull-by-digest inspection confirmed recipe `ubuntu-24.04@4`, Node.js
  `v22.23.1`, npm `10.9.8`, Eclipse Temurin/JDK `25.0.4+7`, Apache Maven
  `3.9.16`, `JAVA_HOME=/opt/java/current`, `MAVEN_HOME=/opt/maven/current`,
  correct executable `PATH`, retained JDK/Maven legal files, exact PEX/source
  lineage, generic runtime contract, and no Claude or Gemini CLI in the base.
- The authorization CLI recorded `claude-code-download = true` in a mode-0600
  test-owned checkout record. Production realization against the published
  v025 downloaded Claude Code `2.1.227` directly from Anthropic, verified
  SHA-256 `6832dc3f1797b890b71116e5f2dbbf9a83fd3d0498c235b4b0f9cd0e6e499ad6`,
  installed `/opt/claude/bin/claude` only in the local formation, set
  `DISABLE_UPDATES=1`, and preserved the Node/Java/Maven toolchain. The
  disposable probe image and caches were removed afterward.
- Stage 5 retained run ID:
  `b2093d85912fa34ac1324e1da26a9dcd`. Its isolated checkout resolution
  authorizes the exact local v025 identity, direct Claude acquisition, host
  Docker, host networking, and development sudo. No credentials were imported.
- Stage 5 closure exception: the separate absence-of-authorization plan and
  non-GUI probe were not run. The product owner accepted closure and transferred
  that precise obligation to the V1 test backlog.
- Canonical successor environment:
  `devcapsule-local-pycharm:2145e28bc7b8aca0eee0`, formation identity
  `2145e28bc7b8aca0eee0a839050d626b5186aa57463045fb85abe8003581fb77`,
  immutable image ID
  `sha256:f3fa500c3811d2f838a56af224e61f15524de014fa4270174b14ec36e894dbee`.
  A second production realization strictly reused that exact image.
- Detached successor source revision:
  `600c085228884112e8860c3e6cdc4fb7b6674c0b`; public-provenance PEX SHA-256:
  `aee9346f1766aa10260da2d879a4049ff838f92642240a9d54f5b183ec0e59a0`.
  The clean build gate passed mypy over 88 source/test files, `230 passed` with
  `8 deselected`, five packaging integrations, and source/public-PEX smoke
  tests.
- Detached successor container:
  `7e92dcba38685c1b1cf508c6b26e8312454746ec51f186ed4043a510d9d51c93`,
  deterministic name
  `devcapsule-e2e-b2093d85912fa34ac1324e1da26a9dcd-successor`. Exact name,
  E2E labels, image ID, running state, zero-restart stability, PyCharm process,
  runtime plan, Docker access, and noninteractive sudo all passed.
- Successor tool probes passed: Claude Code `2.1.227`, Codex `0.145.0`, Node.js
  `v22.23.1`, `javac 25.0.4`, Maven `3.9.16`,
  `JAVA_HOME=/opt/java/current`, and `MAVEN_HOME=/opt/maven/current`.
- The original v024-derived control container
  `pycharm-isolated-costin-1786394284` remained running and unchanged during
  launch and inspection.
- Manual GUI handoff evidence: on 2026-08-12 the user confirmed that the v025
  successor's new PyCharm window is visible and usable. A subsequent daemon
  inspection still showed the successor running with zero restarts and the
  v024 control running independently.
- The accepted v024 bootstrap source revision remains
  `e2dae20abcd2b60fde8f4f7901e6b88b40f097df`.
- Embedded v024 PEX SHA-256 remains
  `fb278f145a583faba12df9c4a663b41cb60b0b508a769b050cfa4e088f13febc`.
- `main` now selects the proven v026 base as the repository's dogfood and
  development recommendation:
  `docker.io/mycodespaceai/devcapsule-base@sha256:695f9eb6dd269dc694b3367f6a2570d500b938998d6f7aa3aa00e5d04cc7394a`.

## Next Resumable Task

Stage 6 is complete:

1. **Done — externally removed capsule.** A real-Docker E2E starts the v026 PEX
   runtime, removes its exact test-owned container externally by its
   GUID-derived name, and proves independent inspection reports failure rather
   than stale success.
2. **Filed for V2 — launcher-loss recovery.** The product owner accepted that
   V1 allocates few, low-impact transient resources and does not justify a
   crash-recovery mechanism. A V2 task now specifies idempotent GUID-based
   reconciliation after the original launcher misses its cleanup path. This is
   not a Stage 6 or V1 closure condition.
3. **Done — GUID-derived cleanup.** The recursive launcher generates a random
   128-bit run ID. Its container is named
   `devcapsule-e2e-RUN_ID-successor`; its workspace and staging path contain the
   same ID. Failed-launch cleanup accepts only that run ID, derives the Docker
   name, and removes by name. The running successor receives the value as
   `DEVCAPSULE_RUN_ID` for self-reflection. Labels remain useful evidence but
   are not a second deletion proof.

No further product-owner GUI validation is required for Stage 6. The GUID is a
collision-free ownership key, not a secret from processes already authorized
to enumerate the host Docker daemon.

Stage 7 must also choose its persistence subject explicitly. Two successors are
retained and both are now exited. The newer `482c34f2…` run carries an
`expected-plan.json` and is the only one the hardened inspector can re-verify;
the older `b2093d85…` run predates the retained plan. Prefer the newer run as
the Stage 7 subject where possible, launch a fresh successor if the persistence
proof requires one, and keep the older run as historical evidence only.

## Directed Follow-On Work (2026-08-23)

Ordered by the product owner on 2026-08-23, after the first-run UX design
sessions and the stale-lock fix (`054df4e`). Re-sequenced the same day: the
owner is the only current user of the trading-research sample project and is
blocked by the stale-lock failure in released clients, so an expedient patch
release comes first.

1. **Done — v026.2 carrying the stale-lock fix.** Published 2026-08-23 from
   tag `v026.2` at `7920945`; the release PEX and checksum verified against
   the live GitHub release on 2026-08-24. The trading-research checkout is
   unblocked on a released client.
2. **Prepare v027, the replacement for v026.1.** Not a patch release: it
   carries the significantly changed command-line shape and behavior settled
   in `engineering-docs/design-notes/devcapsule/v1-user-experience.md` —
   `init` with the full postcondition (manifest, platform lock, owner
   checkout record, fresh resolution), the canonical-node-name option
   vocabulary shared with the `config` family, the one-elicitation order with
   `ssh-keygen`-style prompting, and the retirement of the standalone lock
   stub. The mnemonic jump (no v026.2) is deliberate: it marks the CLI shape
   boundary. Release notes must state the changed surface; `R-COMPAT-001`
   governs everything the new client reads from existing projects.
3. **Remediate `project_configuration.py` to the Hoare standard —
   re-sequenced 2026-08-26: deferred past the v027 release to v028 or
   later; see the deferred-improvements list above.** From the 2026-08-23
   diagnosis:
   1072 lines, 43 module-level names, none underscore-private, no
   `__all__`, 3 comment lines; at least 11 names are de-facto private. The
   buried `lock_for` policy that caused the stale-lock failure is the
   canonical cost. Scope: (a) declare the public surface (`__all__`,
   underscore-prefix the de-facto privates); (b) comment every policy point —
   each `raise` states what it defends and whose remedy applies; (c) split
   the module along the four-owner boundary of *Four Things With Different
   Owners* (manifest / platform lock / checkout / resolution); (d) settled
   by the product owner: `config list` must stop initializing checkout
   records — inspection does not mutate — with the record creation moving to
   the resolve path that already owns it. Items (a) and (b) may land earlier
   inside ordinary v027 work under the standing Hoare directive; (c) and (d)
   are this task.

Sequencing of this pair relative to Stage 7 persistence remains the product
owner's call and is not decided here.

## Acknowledged Work

1. **Implement external-resource ownership and reaping in Stage 7.**
   Acknowledged 2026-08-17 from `workflow-improvements`. It fits this
   workstream's existing persistence and deterministic-cleanup stage and is
   ordered after the current v026 publication boundary and Stage 6 completion.
   Stage 7 will implement against the convention owned by
   `workflow-improvements`, covering ownership/run identity for containers,
   images, volumes, host ports, and state roots; collision-resistant naming;
   enumeration by owner; and safe removal boundaries. Closing the detached
   successor cleanup bug is a consequence of this task, not a separate
   implementation.
2. **The two delegated v026 deliverables.** Acknowledged from
   `project-management` and completed: the self-contained executable plus
   clean-machine proof and the host-browser URL-open bridge are published and
   accepted.
3. **Widen the registered goal to reflect delivered product work.** Accepted
   from `project-management`. The goal now records ownership of the v026 base
   and executable deliverables rather than describing only recursive launch.

## Open Threads

- The release is prepared but not cut: the branch carries the 0.2.7 version
  advance and the release-identity unification, and only the owner's acts
  remain — integrate, tag `v0.2.7`, backend publication. The Hoare
  remediation does not gate the release; it leads the deferred-improvements
  list for v028+. The owner is exercising a local 0.2.7 build
  (`dist/devcapsule-local.pex`) before the release acts. The release-notes
  draft is [v027-release-notes-draft.md](v027-release-notes-draft.md).
- Run-once carrier answers can enable a capability but not disable a
  persistent authorization (each node has one authorizable V1 value); if
  per-run disabling is ever wanted, it is a value-vocabulary decision, not a
  grammar change. Raised with the owner on 2026-08-24 and left open.
- Resume Stage 7 persistence and deterministic cleanup after the directed
  pair, using the random run ID as the common name in every exclusive run
  resource.
- The session's nine commits (`466a202`..`04df047` plus this pause commit)
  are pushed on `origin/recursive-e2e/stage-4`; no pull request to `main` is
  open yet, deliberately, because the Hoare remediation is ranked ahead of
  the v027 release and should ride the same integration.
- Pause-protocol gap, exercised latitude: the pause rule says the outbox
  carries the handoff so main's registry link stays readable, but
  `origin/recursive-e2e/outbox` (`2f9c364`) still holds deliveries that have
  not reached `main`'s project-management intake (the promised-work audit
  request and the non-interactive-runs item), and the outbox rule says a send
  carries only what is being sent. Resetting the outbox would destroy the
  pending deliveries, so the handoff was not sent; it is current on the
  pushed workstream branch. The conflict between "reset from main, carry only
  the new send" and "the outbox still holds unreceived mail" recurs for any
  workstream and belongs to `workflow-improvements`.
- Deliberately not preserved: the local checkout's `.idea/` drift and the
  trading-research submodule pointer drift are the owner's working state and
  were left uncommitted.
- Prefer the retained `482c34f2…` run when its evidence is sufficient, but use
  a fresh launch for behavior that requires a running successor or the new
  `DEVCAPSULE_RUN_ID` environment contract.
- Do not remove either retained successor or its run workspace before Stage 7
  has classified the evidence and exercised exact GUID-derived cleanup.
- Recovery after abnormal loss of the original launcher is deliberately not
  preserved as V1 work. It is filed for V2 in
  `2026-08-18-v2-launch-resource-reconciliation.md` and does not reopen Stage
  6.
- Stage 7 is ready before `workflow-improvements` has finalized the external-
  resource ownership convention. A readiness notice is being sent through the
  recursive outbox so that dependency can be reordered explicitly.

## Workflow Latitude Used

The protocol does not assign a newly discovered adopter-facing product defect
to a workstream when that defect interrupts active dogfood across two existing
workstreams. The product owner explicitly made the defect the immediate task.
It was implemented on `recursive-e2e/stage-4` because it is a v026 executable
distribution defect discovered while using the v026 PEX; `sample-projects`
owns only the adopter repository update, and `workflow-improvements` owns
protocol conventions rather than the product bootstrap implementation. This
routing decision is recorded here because the gap can recur and should later
be considered by `workflow-improvements`.

## External State And Risks

- Re-verified 2026-08-22: both retained successors still exist and remain
  `Exited (0)`. Docker inspection still exposes their exact ownership-derived
  names and the host-side run-root mount paths for `482c34f2…` and `b2093d85…`.
  Neither container nor either run root was removed during resumption.
- Re-verified 2026-08-17 at session start, correcting the entry below it: the
  Stage 6 successor
  `9a2c3c787f2ea0577d2f95a117b986084a9e0a55e9852b4e3d0b558c69ad32f6` is
  `Exited (0)` as of 2026-08-14T10:15Z. It is the second retained successor to
  stop while its handoff described it as running, which makes the pattern
  structural rather than incidental: no recorded successor has stayed up across
  a pause, and both `docker ps` observations were correct only on the day they
  were written. The bounded second-inspection stability result therefore cannot
  be produced from either retained container and needs a fresh launch.
- The Stage 6 successor
  `9a2c3c787f2ea0577d2f95a117b986084a9e0a55e9852b4e3d0b558c69ad32f6` was
  running with zero restarts when last observed, and its run root
  `482c34f24fc5c438da7b24ff172a619b` holds the owner marker, manifest,
  `expected-plan.json`, clone, build environment, and retained staging. Do not
  remove any of it before Stage 7. Its clone additionally contains a `buildenv`
  virtualenv created only to build the clean-clone PEX.
- Observed on 2026-08-13, correcting the previous entry: the v025 successor
  `7e92dcba38685c1b1cf508c6b26e8312454746ec51f186ed4043a510d9d51c93` is
  `Exited (0)` and has been stopped for about 39 hours. It still exists and
  must not be removed before Stage 7. The earlier "continued health after
  return" claim therefore covers only the observation window recorded on
  2026-08-12; the bounded second-inspection stability result in the next-step
  list is still outstanding and now needs a fresh running successor.
- The v024-derived control container `pycharm-isolated-costin-1786394284` is no
  longer present on this host. Development now runs in
  `pycharm-isolated-costin-1786657961`, itself built from the canonical
  environment `devcapsule-local-pycharm:2145e28bc7b8aca0eee0`. The recursive
  claim that a v024-derived control was left untouched during the v025 launch
  remains valid as historical Stage 6 evidence but can no longer be
  re-observed live.
- Corrected on 2026-08-14: the earlier claim that the successor launch lacks
  `DEVCAPSULE_RECURSIVE_E2E=1` is wrong, and no launcher metadata mismatch
  remains to be fixed. Direct inspection shows the retained successor
  `7e92dcba3868` carries `DEVCAPSULE_RECURSIVE_E2E=1` and all four
  `devcapsule.e2e.*` ownership labels, and the current development container
  carries the marker as well. The missing-marker workaround applied to the
  retired v024-derived control `pycharm-isolated-costin-1786394284`, which
  predates the marker and no longer exists on this host. The historical Stage 3
  evidence recorded against that container stands as written.
- The project base authorization and generated local resolution are stale by
  deliberate developer-owned choices. Do not reauthorize a base implicitly.
- The bare v024 base does not add `/opt/node/current/bin` to `PATH`; recipe
  version 4 corrects this and adds the Java/Maven toolchain only in the
  successor.
- Host Docker, host networking, development sudo, X11, and persistent-home
  access remain explicit security boundaries.
- The retained successful run and its mode-0600 Stage 4 evidence remain under
  the ownership-marked recursive-E2E workspace. Earlier failed diagnostic runs
  remain retained as failure evidence and must not be removed broadly.

## Workstream Document Index

This workstream owns:

- [Intake disposition log](intake-dispositions.md)
- [v026 local migration and acceptance](v026-local-migration-acceptance.md)
- [v027 release notes draft](v027-release-notes-draft.md)

Its established execution and evidence records predate the WIP convention and
remain permanent engineering records:

- [Milestone plan](../../implementation-notes/devcapsule/2026-08-06-recursive-dogfood-e2e-milestone-plan.md)
- [Stage 2 execution checklist](../../implementation-notes/devcapsule/2026-08-06-recursive-dogfood-stage-2-execution-checklist.md)
- [V1 test backlog](../../implementation-notes/devcapsule/2026-08-07-v1-test-backlog.md)
- [V2 launcher-loss resource reconciliation](../../implementation-notes/devcapsule/2026-08-18-v2-launch-resource-reconciliation.md)
- [V1 gap plan](../../design-notes/devcapsule/2026-08-06-v1-gap-review.md)
