# Workstream Final Status: Eclipse Interactive Surface

Mnemonic: `eclipse-surface`

Start date: 2026-09-09

End date: 2026-10-01

State: concluded unsuccessfully; folded into `component-catalog` by owner decision

Integration target: `main`

Delivery method: pull request

Requirements: `R-PRODUCT-001`, `R-PRODUCT-002`, `R-SCOPE-001`, `R-DOCKER-001`

## Conclusion (2026-10-01)

**Ended at the product owner's direction on 2026-10-01, without implementing
anything.** The owner ruled that an IDE is a component, that
`component-catalog` is where new components are accepted and tested, and
that `component-upgrades` owns the code that wires components (orchestration,
upgrades). A workstream per surface therefore has no place, and this one,
registered for scoping that never came, concludes rather than waits.

- **Last task:** the entry survey below, completed 2026-09-09. Its final
  status: delivered to the owner; no scoping instruction followed.
- **Branches and revisions:** none. No `eclipse-surface/` or
  `ws-eclipse-surface/` branch was ever forked, locally or on the remote; the
  registration merged to `main` on 2026-09-09 and this is the only record.
- **Intake:** one item, the 2026-09-21 fan-out notice, taken and acknowledged
  today; nothing forwarded, nothing owed.
- **Where the work went:** Eclipse as a surface is `component-catalog`
  content whenever the owner schedules it, and the survey below (licence,
  shared-installation mechanism, the files an Eclipse integration touches)
  is its starting material. The first new JetBrains surface, IntelliJ IDEA,
  was targeted at release 0.2.16 the same day and is also
  `component-catalog`'s; see the
  [0.2.16 planning proposal](../../wip/2026-08-09-project-management/2026-09-27-0216-release-planning.md).
- **Reconsideration:** none needed. A surface workstream is not the shape
  the owner wants; the capability name `java-ide` and the package choice
  remain open questions for whoever implements Eclipse.
- **Custody record:** the [custody record](2026-09-09-outbox-reset-loss-record.md)
  held here stays with this archive. `project-management` recorded on
  2026-09-22 that the recovered mail and patch are historical custody
  evidence, not outstanding delivery, and the outbox mechanism it describes
  was retired with the coordination branch.

## Goal

Add the Eclipse IDE — specifically its Java Development Tools (JDT) — as a
third interactive surface alongside PyCharm and VSCodium, as an ordinary
catalog component rather than a special-cased path.

Eclipse is the first surface whose natural capability is `java-ide`. The base
already carries the language tooling that surface needs: Eclipse Temurin JDK
`25.0.4+7` at `/opt/java/current` and Apache Maven `3.9.16` at
`/opt/maven/current` are installed by base recipe 7 and are on `PATH`.

## Branch Association

Branch prefix: `eclipse-surface/`. No working branch exists yet; the first one
is forked from this registration's merge commit on `main`, per *Beginning A
Workstream* in `WORKFLOW.md`. The standing `eclipse-surface/outbox` is created
on first use.

This workstream was opened at the product owner's direction on 2026-09-09,
while `project-management` was explicitly left in place and untouched. Its
registration therefore travelled `project-management/outbox`.

## Current State

Nothing is implemented. What exists is the entry survey below, performed on
2026-09-09 against `main` at `857035a`, which answers the two questions the
product owner asked before scoping: whether Eclipse may be redistributed, and
whether the newly landed shared-installation mechanism is what it was believed
to be.

### Finding 1 — Redistribution is permitted, and DevCapsule does not do it

Two separate answers, and the second is the one that governs.

**The licence permits it.** The Eclipse IDE is published under the Eclipse
Public License 2.0. The Eclipse Foundation's own EPL FAQ states that an
unmodified EPL program may be compiled and commercially licensed under EPL
terms, and that redistributing object code does not oblige the distributor to
bundle source — only to state that source is available from them and how to
obtain it. Redistributing a *modified* program does oblige the distributor to
make the modified source available. Two caveats apply to a shipped Docker
image and would need a real review before anyone relied on them: an Eclipse
package is not purely EPL content (it carries third-party bundles under EDL,
Apache-2.0 and others, each with its own notice obligations), and the Eclipse
Foundation's trademark usage policy restricts use of the Eclipse name and logo
independently of the copyright licence.

**DevCapsule does not redistribute either existing surface, and Eclipse should
follow the same path.** PyCharm and VSCodium are acquired, not shipped. The
resolution matrix pins an upstream URL and a SHA-256 per surface version
(`resolution_matrix.py`, `_PYCHARM_2026_2_0_1` and `_CODIUM_1_126_04524`);
`materialization.py::acquire_artifact` downloads that exact URL onto the
developer's workstation, verifies the digest, caches it under XDG, and the
archive is unpacked and baked into a workstation-local image. No DevCapsule
artifact contains IDE bytes and nothing is pushed to a registry. Under that
model the redistribution question is moot for the default path — the developer
obtains Eclipse from the Eclipse Foundation, exactly as they obtain PyCharm
from JetBrains. Recommendation: keep it that way and do not open the
redistribution question at all unless a future prebuilt-image product needs it.

### Finding 2 — The shared-installation mechanism exists, with one correction

It landed on `main` in `e6e0808` ("Automate tag releases and reuse independent
component installations") and is documented under *Shared component
installations* in `devcapsule-src/README.md`. The description the product owner
carried into this session is accurate on the mechanism and optimistic on the
sharing.

What is real, in `devcapsule-src/devcapsule/image_build.py`:

- `ContributionComponent` declares a named installation with an explicit list
  of exported filesystem paths and its own base.
- `render_build_context` renders a synthetic `devcapsule-baseline` stage
  carrying the parent image and its apt packages, then one `FROM ... AS <name>`
  stage per contribution, then the final stage, which assembles the exports
  with `COPY --link --from=<stage> <path> <path>`.
- Contribution names are validated (`[a-z][a-z0-9-]*`, no repeats) and nesting
  is rejected.

`materialization.py` already routes both surfaces and every ancillary component
through it: `surface_materialization_spec` wraps the surface's installation
directory and post-install steps in one `ContributionComponent`, and
`_ancillary_contributions` builds one per ancillary component id. Node, Temurin
and Maven install as separate stages when building a base. The stage's BuildKit
cache key covers its parent, its commands and its copied inputs — not the final
image's name, labels, or sibling contributions — so changing the surface, a
sibling component, or the launcher PEX does not rerun an unchanged installer.
`tests/e2e/test_component_cache.py` covers this.

**The correction.** This is not a mechanism for *distributing* component bits.
`devcapsule-src/README.md` is explicit: "Reuse is per Docker builder and lasts
while its BuildKit cache is retained… Component cache images are not
published." A fresh host or a pruned cache rebuilds the stage from scratch, and
acquisition authorization plus checksum verification still run before any
installation. So the benefit to Eclipse is real but local: an Eclipse
installation stage will be built once per builder and then reused across every
formation that differs only in its agent components, its launcher PEX, or its
labels. It does not let the project ship an Eclipse layer to adopters.

A second change from the same commit is worth knowing before touching
materialization: base recipe 7 no longer embeds the DevCapsule PEX. The
launcher supplies its own PEX at `/opt/devcapsule/bin/devcapsule.pex` during
materialization (`runtime_artifact.py`), and that PEX's SHA-256 is now part of
the formation identity. Source-form launches need `nox -s pex` and either the
built artifact or `DEVCAPSULE_RUNTIME_PEX`.

### Finding 3 — What integrating Eclipse will actually touch

Surveyed, not decided. The `codium` integration is the model to follow, since
it was the neutral-surface path `component-catalog` built.

- `devcapsule/components/eclipse.py` — a `ComponentDefinition` with
  `id = "eclipse"`, a capability (`java-ide` is the obvious candidate; it does
  not exist yet), a `ComponentRuntimeTemplate`, and its persistent state slots.
  Eclipse's state shape differs from both existing families: a workspace
  directory holding `.metadata`, plus a separate configuration/p2 area if
  installed features are to persist.
- `devcapsule/components/catalog.py` — add to `INTERACTIVE_SURFACES` and
  `COMPONENTS`.
- `devcapsule/container_runtime/entrypoint.py` — currently dispatches on
  `adapter` for exactly `"jetbrains"` and `"vscode"` and raises otherwise. An
  `"eclipse"` adapter is new runtime-side code, and the runtime template ships
  inside the image, so the frozen-runtime compatibility question that shaped
  the codium template applies here too.
- `devcapsule/materialization.py` — a `SurfaceMaterialization` profile:
  installation path, `archive_probes` against the unpacked tarball, whether a
  variant discriminator is needed, and any post-install steps.
- `devcapsule/resolution_matrix.py` — a `_ComponentPin` with the pinned
  upstream URL, version and SHA-256, the `java-ide` capability mapping, and a
  verified-combination row once a formation is smoke-tested.

Open technical questions for scoping, not yet investigated: which Eclipse
package to pin (the Java-developers package versus a platform plus JDT
assembly), whether to take the no-JRE variant so the base's Temurin 25 is the
only JDK present, and how Eclipse's SWT/GTK stack behaves under the launcher's
forced llvmpipe software rendering — VSCodium needed `--no-sandbox` and a 640m
`/dev/shm` before it was stable, and Eclipse's failure modes will be its own.

## Planned Next Step

None; concluded. Historically: return to the product owner with these
findings and take scoping instructions. No Eclipse package was chosen, no
capability name was ruled, and no branch was forked.

## Open Threads

- The mnemonic `eclipse-surface` and the `java-ide` capability name are the
  agent's proposals, not owner rulings. The mnemonic is immutable once this
  registration merges; the capability name is not.
- `project-management` was deliberately left as-is at the owner's instruction,
  so this workstream's opening is not yet reflected in that workstream's own
  handoff or its coordination backlog, and it has not been placed in the V1
  scope ledger. Whether Eclipse is a V1 surface or a post-V1 addition is an
  open project-level question that `project-management` owns.
- The custody record above is unrouted. Occurrence 4 was recovered and delivered
  to `main` on 2026-09-09 through `PR #66`, byte-identical. Occurrence 5 is
  preserved but still undelivered: it belongs in `project-management`'s intake
  and only `workflow-improvements` can send it.
  Dispositioning them and fixing the protocol are open and belong elsewhere. The
  outbox audit itself is complete: all five were checked, and the other three are
  clean.
- `index.md` on `main` at `857035a` lists four WIP workstream status files but
  omits `component-catalog`. This registration adds its own row and leaves that
  pre-existing gap alone rather than editing another workstream's routing.

## Documents

- [Custody record: two live outbox-reset losses](2026-09-09-outbox-reset-loss-record.md)
  — held here temporarily at the product owner's direction and **not owned by
  this workstream**; see *Held In Custody* below.
- [Intake](intake/README.md)
- [Disposition log](intake-dispositions.md)

## Held In Custody

Opening this workstream required delivering its registration through
`project-management/outbox`, and the send protocol begins by hard-resetting that
branch from `main`. The branch was found carrying an undelivered item from
2026-08-19 that has never reached `main` and that contains a ratified
product-owner decision on coordination storage — the fourth recorded instance of
the outbox-reset loss, and the first caught before the reset destroyed anything.
Auditing the remaining four outboxes then found a fifth, stranded on
`workflow-improvements/outbox` since 2026-08-17 and alive only because that
workstream is idle.

At the owner's explicit direction on 2026-09-09, the mechanism, the audit that
found the fifth, and both items' full verbatim content are recorded in
[the custody record](2026-09-09-outbox-reset-loss-record.md) so that neither can
be lost by a branch operation. That document belongs to `project-management`
(the communication record) and `workflow-improvements` (the protocol fix). It
should be moved and deleted from here once the owner assigns it. Nothing about
it is `eclipse-surface` work, and this workstream is not tracking it.
