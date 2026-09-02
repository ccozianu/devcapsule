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
every later gen2 release. The v0.2.9 base pin awaits the owner's push
of the image (a registry digest is needed to pin; the built image is
local-only). Still open from the same episode: the `--authorize
base-image` error message offers "the exact value" as if the value were
choosable — consent and selection read as one verb.

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

## Release Target: v0.2.9

Set by the product owner on 2026-09-02. v0.2.9 ships when:

1. ~~The Antigravity CLI component is implemented and owner-smoked, per
   the delivery contract and the license analysis.~~ Done 2026-09-02:
   smoke passed on the tictactoe sample (codium × antigravity,
   v0.2.8 base).
2. The open v0.2.8-validation bugs are fixed, "relatively" — meaning
   the recorded fix scopes, barring new discoveries:
   - [init/run answers not persisted as authorizations](../../bugs/devcapsule/2026-09-02-init-and-run-answers-not-persisted-as-authorizations.md)
   - [formation identity claims an entrypoint the recipe never sets](../../bugs/devcapsule/2026-09-02-formation-identity-claims-an-entrypoint-the-recipe-never-sets.md)
   - [the authorization grammar cannot express denial](../../bugs/devcapsule/2026-09-02-authorization-grammar-cannot-express-denial.md)
     (owner-triaged onto this list 2026-09-02, found during the
     antigravity smoke triage)
   - [the codium setuid sandbox crashes under the development-sudo posture](../../bugs/devcapsule/2026-09-02-codium-setuid-sandbox-crashes-under-development-sudo.md)
     (the failure the antigravity smoke actually hit; **ruled and fixed
     on the branch 2026-09-02**: the owner superseded the 2026-08-31
     sandbox decision — renderers run `--no-sandbox` under uniform full
     hardening for as long as we can, per the new
     [renderer-sandboxing design note](../../design-notes/devcapsule/renderer-sandboxing.md).
     The narrow grant, the `setuid-helper` declaration, and the recipe's
     chrome-sandbox 4755 step are removed; `--no-sandbox` travels as
     template data so the frozen v0.2.8 runtime launches it unchanged;
     codium recipe-version is 2 and the matrix advanced to `embedded-5`,
     golden locks regenerated. Closes on the owner's next sudo-enabled
     relaunch)
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

## Next Resumable Task

Session paused late 2026-09-02, everything committed and pushed
(branch head `d8f833c`). The antigravity component is validated and
PR-ready — the owner opens the PR per the integration cadence. The
same day also executed, owner-ruled: the state-slot/home-ownership
rulings, the codium `/dev/shm` fix (640m), and the passthrough
denylist for launcher-owned docker options. Suite green (516), mypy
clean.

Resume with, in order:

1. The two v0.2.9 bugs awaiting owner rulings — **one down 2026-09-02**:
   the codium sudo-sandbox bug is ruled and fixed (`--no-sandbox` under
   uniform hardening; see *Release Target* and the renderer-sandboxing
   design note). Remaining: the authorization denial grammar (explicit
   deny vs `unset` semantics). Note for the next rebuild-and-run: the
   sandbox change advances the matrix to `embedded-5` and codium's
   recipe to version 2, so existing codium locks (including the
   tictactoe sample checkout's committed lock) fail loudly until
   `init --regenerate`, and the canonical codium image rebuilds under a
   new identity — the same relaunch that first-exercises the widened
   `~/.gemini` slot.
2. The two scoped v0.2.9 bugs: init/run answers persisted as
   authorizations, and the formation-identity/entrypoint-claim record
   (its enforcement half coordinates with `contained-display`).
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

- **Base rebuild** (updated 2026-09-02): resolved for codium-only needs —
  the v0.2.8 base is published, owner-smoked with codium, and pinned in
  matrix `embedded-3`, so those locks launch with no override. Formations
  combining codium with agents still resolve to v026 (the agents have no
  v0.2.8 edges yet) and therefore still need the runtime-PEX override
  volume; smoking the agents on v0.2.8 and adding their edges retires the
  override entirely.
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

- **Checkout-local needs** (awaiting owner ruling, then rebuild): the
  owner ruled that `config need` must default to an *experiment* — a
  need recorded only in the developer-owned checkout record, committing
  nothing. Proposed design, awaiting the owner's answer on two points:
  (a) two-layer verb — `config need X` local by default, `--project`
  promotes via the already-shipped manifest machinery; (b) strict
  verified-edge checking against the locked base for local needs, or a
  loudly-labeled `--unverified` escape hatch. Also proposed: local needs
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

- [Antigravity CLI: license and redistribution analysis](antigravity-cli-license-and-redistribution-analysis.md)
  (2026-09-02, the ledger gate for track 2)
