# Workstream Current Status: Component Catalog

Mnemonic: `component-catalog`

Start date: 2026-08-30

State: open; first session started 2026-08-30

Integration target: `main`

Delivery method: pull request, one per validated component (see *Integration
Cadence*)

Requirements: `R-PRODUCT-001`, `R-PRODUCT-002`, `R-SCOPE-001`, `R-DOCKER-001`

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

## Coordination With `contained-display`

`contained-display` is paused as of 2026-08-30 until this workstream shows
significant progress. A `project-management` intake item in its queue directs
it, on resume, to treat the supervisor↔component runtime contract as
load-bearing for this workstream's components and to route any deliberate
contract change through coordination rather than changing it inadvertently.
Symmetrically: if this workstream finds the contract insufficient, it records
the gap and coordinates; it does not reshape the supervisor.

## Current Task

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

Remaining before the codium PR: the product owner's smoke sign-off (unit
tests, mypy, and the live launch are done; the launch put a VSCodium window
with the tictactoe sample on the owner's display). The smoke currently
needs the runtime-PEX override described under *External State And Risks*.

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

## Next Resumable Task

After the `codium` component integrates: track 2, the Antigravity CLI
component, starting with the license and redistribution analysis the
ledger gates on.

## Open Threads

- **Base rebuild** (coordination fact): the v026 base's embedded runtime
  PEX predates the `vscode` adapter, so codium containers reject their plan
  under the stock base. Until a base built from a revision including this
  branch ships, launches need
  `-- --volume <host-path-to-current-pex>:/opt/devcapsule/bin/devcapsule.pex:ro`.
  This gates codium for adopters, not the PR.
- **PyCharm slot-path migration** (recorded follow-up): PyCharm still
  travels the launcher's named state fields; every other surface uses the
  generic plan-slot mounts. Migrating PyCharm onto the generic path (and
  then retiring the named fields and the `pycharm/`-named plumbing) needs
  its own owner smoke.
- **Component update mechanism** (owner-stated future work, 2026-08-31):
  warn developers when pinned components have newer releases, and advance
  matrix pins after tests. Belongs to project-wide planning; not started.
- **Launcher naming**: the generic project launcher still lives in
  `configurations/pycharm/_launcher.py` and `run_pycharm` launches every
  surface. Deferred as cosmetic churn until the PyCharm slot migration
  touches the same code.
- **Tictactoe devcapsule conversion** (sequenced): on 2026-08-31 the
  `typescript_tictactoe_5inrow` sample became a submodule like its sibling
  samples, at `git@github.com:ccozianu/devcapsule-sample-typescript-tictactoe.git`;
  the owner created the repository and the pinned import commit is pushed,
  so the submodule stands complete. Converting the sample into a
  devcapsule project (committed `.devcapsule/`) deliberately waits for the
  post-codium release that repins the base, so its lock never names a
  base whose runtime PEX rejects codium plans.

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

None yet.
