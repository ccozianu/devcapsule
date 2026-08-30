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

Track 1's shared foundation is implemented as of 2026-08-30 (commit
`f886872`): the catalog selects the interactive surface from an explicit
`INTERACTIVE_SURFACES` registry, the `codium` `ComponentDefinition` declares
durable `user-data` and `extensions` slots plus the shared home-overlay
cache slot, and the `vscode` family adapter reproduces the legacy launcher's
proven foreground command (the Electron binary at the installation root —
the retired `codium-foreground` symlink target — with `--user-data-dir`,
`--extensions-dir`, then the project path). The generic entrypoint
dispatches on the adapter name. Unit tests and mypy are green.

What remains before the component is validatable end-to-end, in dependency
order; each stage carries a design question for the product owner noted
under *Open Threads*:

1. Materialization: generalize `parse_locked_environment` and the
   jetbrains-specific recipe/spec in `materialization.py` so a codium lock
   materializes into a cached canonical image (including the setuid
   `chrome-sandbox` fix-up the legacy image build performed).
2. The embedded resolution matrix: a pinned codium table and the selection
   mechanism that lets `init` produce a codium lock.
3. `project run` and the host launcher: drop the `pycharm`-only guards in
   `project_operations.py` and `commands/project.py`, and feed the
   component's declared slots to the launcher generically instead of by
   `pycharm/...` name.
4. Retire the `codium_with_claude` command tree and settle the
   `vscode_with_claude` question (found to be a never-implemented stub that
   only raises "not implemented yet"; retirement looks free).

## Next Resumable Task

After the `codium` component validates and integrates: track 2, the
Antigravity CLI component, starting with the license and redistribution
analysis the ledger gates on. Settle the `vscode_with_claude` scope question
in whichever session it first becomes relevant — at the latest, when the
`codium_with_claude` command tree is retired.

## Open Threads

Design questions awaiting the product owner, mapped to the remaining stages
above:

- **Surface selection mechanism** (stage 2): the matrix demands the
  `python-ide` capability and hard-codes `interactive-surface = "pycharm"`.
  How does a checkout choose codium — a distinct capability name, a manifest
  configuration value, or a resolution-time choice? The codium definition
  provisionally declares capability `python-ide` (nothing consumes the
  property yet), matching the reading that the surface is a selection within
  one capability.
- **Codium pin** (stage 2): which VSCodium version/URL/sha256 the matrix
  pins, and from where (GitHub release tarball is the natural archive-shaped
  source; the legacy path accepted either the apt repository or a local
  archive).
- **Sandbox posture** (stage 1): the legacy image made `chrome-sandbox`
  setuid root; the materialization recipe should reproduce that rather than
  fall back to `--no-sandbox`. Confirming that posture is wanted.
- **`vscode_with_claude` retirement** (stage 4): it is a stub that raises
  "not implemented yet"; proposing outright retirement alongside the
  `codium_with_claude` tree rather than componentization.

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

## Workstream Document Index

None yet.
