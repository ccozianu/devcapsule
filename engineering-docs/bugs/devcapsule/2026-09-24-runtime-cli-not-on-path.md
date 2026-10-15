---
status: closed
severity: blocking
target: 0.2.14
owner: maintenance
opened: 2026-09-24
requirements: [R-RUNTIME-001, R-PRODUCT-001, R-PRODUCT-006]
---

# DevCapsule command is unavailable inside the delivered environment

The owner designated this the first 0.2.14 release blocker on 2026-09-24.
A user opens the website capsule and tries to install its missing workflow,
but cannot invoke `devcapsule` by name. Release acceptance and the smoke
campaign are paused for triage. An internal absolute-path workaround does
not satisfy the normal CLI experience or close this blocker.

## Evidence and reproduction

Observed read-only in the owner's running website capsule:
`pycharm-isolated-costin-1790207368`, project `/workspace/devcapsule-website`,
image `devcapsule-local-codium:939b4bc8cedc2b3440f9`, image ID
`sha256:b832f8c6c52551dbfb356d347837e741efaf9dfddbded4a85d431a999621d37d`.
Network mode is host. This is the owner's later session, not runner attempt 4.

1. Open the IDE terminal and invoke `command -v devcapsule`, then
   `devcapsule version --json` or the workflow installation command.
2. Expected: the installed public CLI is available without setting PATH,
   adding an alias, installing another package or knowing its internal path.
3. Actual: the owner reports command-not-found. An independent process in
   that container confirms `shutil.which("devcapsule")` is null; the IDE's
   own environment also lacks `/opt/devcapsule/bin` in PATH. There is no
   `/usr/local/bin/devcapsule` file or symlink.
4. `/opt/devcapsule/bin/devcapsule.pex version --json` succeeds and identifies
   `v0.2.14-rc0`, source `d078b879469c1790647e32db75005d0fa4369b27`.
   Its SHA-256 is exactly the published RC0:
   `2a425a39d2ed5319d1945dd91e34f693c299fa2c53acdf70a205024eea45d513`.

The binary is present and works; this is command installation/discoverability,
not failure to deliver the runtime. Adding its directory to PATH alone would
still expose `devcapsule.pex`, not necessarily the promised `devcapsule` name.

## Implementation evidence and test gap

`devcapsule/materialization.py` installs the artifact only as
`/opt/devcapsule/bin/devcapsule.pex`. That formation contribution supplies no
public command alias. The materialization is shared across IDE families;
PyCharm's symptom must be tested, not assumed from VSCodium's observation.

`tests/e2e/test_component_cache.py` verifies runtime bytes and version by
invoking the internal absolute path. It does not establish that a user can
run the ordinary CLI from the IDE terminal. Preserve that identity test and
add coverage for the public command contract.

## Required fix and close criteria

- Install a public `devcapsule` command backed by the exact delivered runtime
  in newly materialized environments, without a manual shell/alias repair.
- Ensure formation identity/cache invalidation cannot reuse an environment
  missing the repaired entrypoint. Do not change immutable RC0 artifacts.
- Verify `devcapsule version --json` and `devcapsule --help` by name as the
  normal capsule user and from actual VSCodium/PyCharm terminal environments.
- Install the workflow through the public CLI in a disposable project from
  inside the capsule, verify its documented files, and check it after resume.
  Do not mutate the owner's website as a diagnostic test.
- Confirm delivered runtime identity still matches the launcher; record the
  main disposition and validate a new candidate before owner closure.

## Separate onboarding issue

The website has a DevCapsule declaration but no WORKFLOW.md. The owner wants
new users helped into an installed workflow; this is explicitly non-blocking
and is tracked in the [onboarding work item](../../work-orders/2026-09-24-workflow-installation-onboarding.md).
Its initialization history was not reconstructed. Missing workflow files do
not excuse the unavailable command needed to install them.

## Implemented repair and validation

Implementation on `release-0.2.14`: expose the delivered PEX through
`/usr/local/bin/devcapsule` normally. Owner refinement: opt-in development
checkouts select the name `devcapsule0`, leaving `devcapsule` for the source
installation. This repository declares an ordinary configuration value
`runtime.devcapsule-command`, with runtime effect `devcapsule.command-name`
and `recommended = "devcapsule0"`; other projects default to the normal name.
A checkout's explicit answer or omission wins over the recommendation.
The command is executable from scripts as well as interactive shells, with no
shell startup modification. Internal PEX paths remain unchanged. Include the
chosen public command in formation identity so old cached images and the two
command modes cannot be confused, even with identical runtime bytes.
The existing real-Docker test now invokes `devcapsule` by name as UID 1000,
checks version/help and installs a workflow in a disposable project.
Before the repair it reproduced command-not-found (exit 127) for the PyCharm
formation as well as the owner's VSCodium observation. No live image patched.

Validation on 2026-09-24:

- 311 focused configuration/materialization/CLI checks passed, including
  default recommendation, explicit override/omission, invalid command rejection
  without writes, and unchanged runtime identity across command-name choices.
- Four real-Docker variants passed: PyCharm and VSCodium materialization, each
  with normal and development command names. As UID 1000 with ordinary PATH,
  version/help and workflow installation succeeded. Runtime bytes still match.
  Development variants verified no shipped `devcapsule` fallback and that a
  separate development command can coexist with `devcapsule0`.
- A subsequent cleanup refinement removes only an inherited symlink to the
  shipped PEX, preserving another development script or symlink. All eight
  runtime-artifact checks passed, including those three filesystem cases.
- The initial follow-up Docker run reached the public command successfully but
  failed a test's lowercase `usage` expectation against capitalized `Usage`.
  Correcting that assertion allowed the four variants above; no product change
  was made to satisfy that capitalization.

Logs: `/tmp/runtime-cli-regression-before.log`,
`/tmp/runtime-cli-config-focused.log`, `/tmp/runtime-cli-command-modes-e2e.log`,
`/tmp/runtime-cli-link-preservation.log`, `/tmp/maintenance-runtime-cli-build-final.log`.
The full gate's unrelated website Git-pointer issue remains recorded in the
maintenance status; do not describe that overall gate as passing.

Owner acceptance, 2026-09-24: "Everything works" for the real recursive
PyCharm session at `9cc0868`, run `29fb2abc530735da1ebd625acd991622`.
The agent verified `devcapsule0`, exact runtime bytes and workflow installation
inside that capsule. This accepts that local development-command session; it
does not imply every IDE/mode, resume story or published candidate was tested.

Status is fixed, not closed. PR #136 integrated the repair into main at
`c6bea96cfbbb15a428c86bde6924df8ff3db1c15`, verified by fetched ancestry and
matching runtime sources. RC1 at `cec7a0c` is public and its downloaded checksum/version/source are
verified; exact-candidate IDE validation remains pending. Carry the local acceptance into that validation.
RC0 and the owner's running containers were not modified. Normal merge to main
is the intended disposition; no conflicting main implementation was identified.

Published-RC1 follow-up, 2026-09-24: recursive run
`0edc6f491291f0d5ffa4e31b0238863b` uses exact published RC1 bytes and the new
local RC1 base. Independent inspection passed; PyCharm JVM is running. Agent
checks as UID 1000 verify public `devcapsule0`, absence of shipped `devcapsule`,
exact RC1 version/hash, and workflow installation. Owner GUI acceptance of this
new session remains pending; the bug is not closed by these checks alone.

## Closure, 2026-09-24

Owner verification on the published v0.2.14-rc3 in a real capsule launched
from the `devcapsule-2` checkout: `devcapsule0` is on the PATH, as the
repository's reserved-name recommendation intends, with `devcapsule` left
for the development build. This closes the blocker as verified on an exact
candidate; the earlier local-build acceptance at `9cc0868` and the rc1
agent checks were preliminary.
