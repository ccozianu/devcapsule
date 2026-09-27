# 0.2.15: Persistent extra tools and project information

Status: accepted by the owner, 2026-09-27; implementation pending.

Release: 0.2.15. Driver: maintenance, with these two bounded additions to its
release scope explicitly approved by the owner. Project-management owns this
scope decision; this does not make maintenance a general feature workstream.

## Owner decision and purpose

The owner successfully used 0.2.14 for a website prototype and installed
gcloud under `$HOME/xtras/gcloud`. It survived subsequent runs, as intended,
but the persistence contract was not discoverable. The owner approved both
a supported `/opt/xtras` installation location and `devcapsule project info`.
The location matters even though persistent home can provide its storage.

This supersedes the 2026-09-26 restriction that 0.2.15 contain only the init
answer-loss fix. That fix remains required. These are the two approved small
additions; no third addition is selected. Previously deferred cleanup,
optimization, IDE surfaces and release-notes automation remain outside 0.2.15.

## Persistent `/opt/xtras`

- Available and writable by the capsule user without sudo.
- Contents survive stopping, removing and recreating the capsule for the
  same local checkout, including ordinary subsequent project runs.
- Storage is checkout-scoped by default, following the existing persistent
  home's explicitly selected storage and sharing rules. A fresh independent
  checkout does not automatically receive these installations.
- `/opt/xtras/bin` is on PATH for IDEs, agents and terminals.
- Backing it with `$HOME/xtras` is permitted and preferred for the small
  slice. Existing `$HOME/xtras/gcloud` must remain usable without manual
  migration. Choose the link or mount mechanism after checking root-filesystem
  writability, existing destinations and startup ownership; do not overwrite
  existing content to establish the mapping.
- DevCapsule preserves files; the developer manages tool installation and
  updates. Persistence is not a claim of reproducibility on another machine
  or binary compatibility with every future base.

## Read-only `devcapsule project info`

One discoverable overview for the user and their agent:

- Project and checkout identity, and whether the report describes host-side
  configuration or the running capsule.
- Selected components and versions. Inside a capsule, report running software
  from launch evidence and distinguish a changed next-launch selection.
  Do not infer running versions from a subsequently edited project lock.
- DevCapsule-provided environment variables, their values and purpose.
  Omit secret values. Host output describes the capsule's configured
  environment, not the host shell's unrelated environment; label unavailable
  runtime-only facts rather than inventing them.
- Persistent container paths and their backing storage, scope and lifecycle,
  including project source, home, `/opt/xtras` and declared component slots.
  Explain that managed state may live outside the Git checkout.
- Temporary locations and what is lost when the container is removed.

Discover the project from its root or a descendant on the host. Inside a
running capsule, the command must identify its project even when invoked from
outside the source tree, such as `/opt`. Honor explicit project selection
without confusing another nested project with the containing capsule.
Inspection must not initialize, resolve, repair or otherwise mutate records.
It must not require new host privileges to inspect its own running context.

Arbitrary installed-tool inventory and version probing are outside this
slice. gcloud under xtras is covered by the persistence explanation, not
misrepresented as a catalog component. No new component publication flow,
package manager or cross-machine synchronization is requested.

## Accepted deferral

The owner can live with the general in-capsule `devcapsule project <command>`
failure for 0.2.15. The report says it occurs regardless of working directory;
that breadth has not been independently reproduced in this coordination slice.
The existing [guard bug](../bugs/devcapsule/2026-09-26-project-group-guard-hides-unknown-subcommand-in-capsule.md)
establishes the narrower unknown-subcommand diagnostic defect. Keep it open,
outside the 0.2.15 gate, for later maintenance triage. No fixed later release
is assigned by this decision.

This deferral does not waive the new `project info` contract. Its own runtime
dispatch and discovery must work; a general repair of other subcommands is
not required for this release.

## Acceptance and delivery

1. Preserve the init fix's candidate acceptance. Do not publish the former
   fix-only tree as the accepted final scope after this decision.
2. Start with an existing `$HOME/xtras` installation; expose it through
   `/opt/xtras`, add an executable through its bin directory, replace the
   container and prove both data survival and command discovery. Check a
   fresh checkout's default isolation and ordinary no-sudo operation.
3. Run `project info` from a host project directory and descendant, then
   inside the capsule from the project and `/opt`. Check the actual persisted
   paths and component versions against the report. Exercise a next-launch
   configuration change and verify that it does not relabel running software.
4. Cover read-only behavior and secret omission with focused regression
   checks; run the required release gate and downloaded-candidate acceptance.
   Update CLI help, user documentation and release notes alongside delivery.
5. Maintenance records implementation and main disposition under the existing
   release policy, and updates its release overview before the next candidate.

## Evidence informing the scope

- Owner's successful `$HOME/xtras/gcloud` persistence on 0.2.14.
- [State and persistence specification](../specifications/product/state-and-persistence.md):
  persistent home is the fallback for tools without component state contracts.
- The v0.2.14 shared launcher mounts persistent home at `/home/devcapsule`.
- Main at `0cb4b0a` has configuration inspection and launch-context/version
  reporting foundations, but no `project info` command. This is inspection
  evidence, not proof of the new feature or an implementation estimate.
