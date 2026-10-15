# Component upgrade and recovery validation

Date: 2026-09-21. Requirements: R-UPGRADE-001, R-COMPAT-001, R-PRODUCT-002.
Scope: the [work order](../../work-orders/2026-09-21-component-upgrades.md).

## Result and boundaries

A bounded real ordinary-CLI journey ran Codex **0.153.4 → 0.155.1 → 0.153.4**
through upgrade and rollback. The committed project lock remained byte-for-byte
unchanged. History, a reviewable upstream proposal, and explicit return to the
project recommendation also succeeded. `git apply --check` accepted the exported
patch against the fixture's actual lock bytes.

The IDE was an explicitly labelled tiny fixture archive whose launcher executed
`codex --version` and wrote the result into the fixture project. Codex itself,
its npm platform package, checksum verification, environment construction,
contained display and ordinary `project run` were real. No agent account was
used. This does not establish interactive IDE behavior, authenticated agent
operation, all vendor helper functionality, or owner acceptance of the UX.
Downgrading executables does not establish reversibility of vendor state migrations.

## Observed real environment

- Isolated root: `devcapsule-src/dist/component-upgrades-smoke/`, with its own
  project and XDG config/data/cache/state trees. No everyday checkout input,
  account state or earlier acceptance environment was altered.
- Existing pinned base:
  `docker.io/mycodespaceai/devcapsule-base@sha256:8837edd36720763796ab9fe1dbeb66f1aa7ca2db0dabc8d73a58716440f42f7c`.
  No new base was built.
- Launcher/runtime PEX SHA-256:
  `8d51c2b1d2423a1f49381dc660f80945bd987ce6555de1f387729a1b75c40ca8`.
  This was a local artifact built during implementation, before the final npm
  OS/CPU admission, local-base recovery and candidate-consent refinements. Final source is checked
  by the repository gate and focused tests; no second real image journey is
  claimed for those refinements.
- Baseline/recovery image:
  `devcapsule-local-pycharm:9b4f99e2dfd17f772fbf`.
- Candidate image:
  `devcapsule-local-pycharm:b8871ba38fa275afad91`.
- The fixture exited after each version probe. No fixture session remains
  running. Images and approximately 654 MiB of fixture downloads/state were
  deliberately retained for review. No Docker-wide pruning was performed.
- Local evidence: `result.json`, sanitized `commands.log`, `upstream.patch` and
  the checkout's successful-use records under that isolated root. Display tokens
  are redacted from the command log. Later local PEX builds may replace the
  distribution-level `dist/devcapsule-local.pex`; the hash above identifies the
  actual tested bytes embedded in the two retained environments.

Reproduce with a freshly built PEX and a **new** fixture root:

```sh
cd devcapsule-src
.venv/bin/python scripts/smoke-component-upgrades.py \
  --pex dist/devcapsule-local.pex \
  --root dist/component-upgrades-review \
  --candidate 0.155.1
```

The script now copies its selected PEX into the fixture root before running,
so concurrent later development builds cannot replace the executable under test.
The version above is the observed candidate, not a promise that a future registry
will retain it. Choose another exact version deliberately if needed.

## Repository evidence

Original work-order gate: 954 tests passed; interactive critical-upgrade gate:
988 passed. After the runtime-inspection correction, `nox -s build`:
1,009 tests passed, 18 deselected, one existing xfail;
nine packaged-executable tests passed.
It includes compilation, shell syntax, mypy, the full non-host suite, source
CLI smoke, PEX construction and nine packaged-executable tests. Existing
released-input fixtures remain passing.

The 91 cases in `test_version_sets.py` and
`test_distribution_channels.py` cover:

- Real Codex metadata adaptation and an unrelated widget through the same
  generic orchestration; malformed/unavailable metadata, omission, exact package
  pinning, platform/Node/dependency contracts and checksum failures.
- A successful A, prepared/failed B, rollback, and actual ordinary launch
  consuming A's exact formation descriptor; repeated explicit rollback.
- Build failure, interruption before checkout commit and after checkout commit;
  readers recover the correct choice and resolution.
- An old session finishing after B is selected certifies only A and snapshots
  A's pre-launch configuration.
- Retained artifacts rebuild A after both cache and its environment are removed,
  with vendor access disabled. Missing resources refuse without replacing B;
  explicit exact reacquisition restores the path.
- Current Docker denial survives rollback; adopted state, fixture credentials
  and project work remain intact. A moved local base tag cannot replace the
  recorded immutable base identity.
- Upstream divergence does not alter a complete local set; following the project
  is explicit; proposal export requires successful local use and writes a patch.
- Remembered dismissal, seven-day quiet periods, a newly discovered candidate,
  offline launch and refusal of an unsatisfied companion-version constraint.
- Ordinary launch with a controlled terminal and channel-reported security or
  support notice: review, confirmation, acquisition consent where required,
  same-launch B, accurate success history, then rollback and ordinary launch A.
- Decline, stop, Enter and EOF; remembered later/keep; missing replacement;
  failed preparation followed by an explicit decision to launch the old set;
  noninteractive input never being consumed as consent.
- Daily discovery, the explicit refresh skip, offline first launch, retained
  prior notice and timestamp after a failed refresh, new critical notices after
  ordinary dismissal, and no duplicate routine reminder after a decision.
- Actual npm adapter consuming fixture deprecation metadata and driving the
  prompt; no notice invented from missing versions or unsupported platforms.

These cases retain production configuration and materialization logic while
substituting Docker image operations and the launched process. They establish
contract behavior across those boundaries, not the subjective quality of an
upgrade experience. The real CLI check above supplies separate delivery evidence.
The new prompting cases use the production `Elicitor` with a controlled terminal
stream; no new real Docker/account session or live security advisory is claimed
for this refinement. The earlier real Codex journey predates it.

## Runtime inspection correction

The owner reported that `versions show` inside dogfood tried to read the host's
checkout record from the runtime's XDG home. The fix supplies a read-only record
directory and a separate launch snapshot, with explicit runtime dispatch.
Additional tests cover different host/runtime paths, exact named-checkout
selection, A running while B is selected, host atomic replacement, host path
disclosure without filesystem validation, mutation refusal, identity mismatch,
old-capsule relaunch guidance and inspection during interrupted activation without
performing recovery. Launcher tests check directory/snapshot read-only mounts,
private snapshot permissions and cleanup. Released-input tests remain unchanged.

A bounded Docker probe also passed with networking disabled, using the retained
baseline image `devcapsule-local-pycharm:9b4f99e2dfd17f772fbf` and a copy of the
fixture configuration. The packaged CLI showed running **0.153.4**, initially the
same next-launch set, then next-launch **0.155.1** after host atomic replacement
with retained candidate metadata. `config list` worked, `versions rollback` was
refused with a launcher command, and a direct write failed with the kernel's
read-only filesystem error. This probe tested inspection and mount semantics;
it did not perform another upgrade, IDE session or account acceptance.

Retained evidence: `devcapsule-src/dist/runtime-configuration-smoke-2/`, including
`result.json`, `probe.py`, the private fixture records, immutable context and
`evidence/{before,after,config,mutation,write}.txt`. The tested PEX is retained there;
SHA-256: `4d6b9ed8c82d9728dca05797b2edcb94ca7d843c1f591ad9fae2c949bd5a3684`.
The probe's only container was removed. No everyday configuration was mounted.
Its initial attempt stopped before CLI execution because the test tmpfs was
non-executable; allowing execution in that disposable tmpfs resolved it.

Code review also found and repaired a pre-existing corrupted import in
`scripts/smoke-component-upgrades.py`; its `--help` now passes. That repair does
not imply the full earlier upgrade smoke was rerun.

## Limits retained for review

Codex is the only implemented selection channel. All six catalog components now
have read-only discovery; other definitions explain their installation limits. Candidate acquisition consent is explicit through `--authorize` and
cannot grant host permissions; the licensed-widget journey verifies selection,
revocation, recovery and following a changed recommendation. Companion
requirements are checked and reported, not solved by silently upgrading tools.
Interactive launches attempt a daily channel refresh with cached offline fallback;
noninteractive launches never check online. The npm adapter reports vendor
deprecation, not independently sourced security advisories. No vulnerability
database integration or comprehensive security/support coverage is claimed.

Personal state is never backed up or automatically migrated. Manual deletion
of both retained artifacts and images can defeat offline recovery. Serialized
configuration access remains a precondition. The activation journal protects
interrupted file replacement, not arbitrary concurrent writers or guaranteed
power-loss durability. Release publication and GitHub PR creation/merge remain
with the owner under this work order.

## Vendor discovery and compatibility service extension

Owner-approved 2026-09-21. A source-form publisher run against live primary
vendor metadata succeeded for all six components. It observed PyCharm 2026.2.3,
VSCodium 1.135.06055, Codex 0.155.1, Claude Code latest 2.1.278 and Antigravity CLI
1.2.7. PostgreSQL 16's feed reported 16.15 and support through 2028-11-09;
the major-only lock cannot establish the installed minor or distro backports.
No executable payload, installer, account or container was used by this probe.
Generated local preview: `/tmp/devcapsule-component-status-preview/` (JSON and
GitHub-renderable Markdown). This was an uncommitted source-tree observation;
the revision argument is not evidence of an exact released executable.

Focused suite: 115 passing cases across component status, distribution channels
and version sets. Cases include fixed-version guidance, known issues, exact
adapter/CLI/platform applicability, unknown format, invalid URLs/control text,
expired/future feed timestamps, expired diagnoses, 404 and truncated-HTTP fallback,
offline cache, and preservation of the selected lock/configuration and the prior
successful-check timestamp through the ordinary CLI. Existing offline and
noninteractive launch cases still pass. Discovery-only candidates do not become
executable preview/upgrade choices. Backend partial failure preserves other
observations and last-successful times without authoring a diagnosis.

The actual publication shell from the workflow was executed twice against a
local bare Git remote. It created and fast-forwarded only `component-status`,
published the generated files together, and left `main` and the working branch
unchanged. This validates Git mechanics, not GitHub permissions or scheduling.
The standard-library publisher runs with `python -S`; no site packages are
needed by the hosted probe job.

The first full gate found three launcher-list tests depended on the enclosing
capsule cwd and its now-real configuration mount. A broad fixture override was
rejected when it changed a mount-path assertion. The final correction gives only
those three launcher tests their own temporary cwd. All four affected tests
(including the runtime mount contract) passed before the full gate was rerun.

No hosted action was dispatched and no status branch, release, production site
or GitHub issue was published. Owner PR merge enables the prepared action;
first hosted run and a released client's retrieval of its public endpoint remain
acceptance work. Source policy has no invented diagnoses or hypothetical fixes.

Final extension gate: `nox -s build` succeeded with 1,033 tests passed,
18 host-sensitive cases deselected, one existing xfail; mypy checked 165 files;
source smoke, local PEX construction/smoke and nine packaged tests passed.
Build log: `/tmp/component-status-build.log`. The dirty-tree gate intentionally
built `dist/devcapsule-local.pex`, not a revision-bearing public release artifact.
