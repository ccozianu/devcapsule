---
id: R-CONFIG-001
title: Conservative Configuration Writers And Tolerant Readers
type: requirement
kind: concrete-requirement
status: accepted
priority: wanted
source_of_truth: repo
verification: [tests, manual]
external_refs: []
---

# R-CONFIG-001: Conservative Configuration Writers And Tolerant Readers

## Statement

Owner direction, 2026-10-05, for 0.3 planning: be liberal in what DevCapsule
accepts and conservative in what it produces. A contribution to a shared
repository must not prevent a collaborator with a less capable local launcher
from working merely because an optional enhancement is unavailable to them.
This requirement applies to adopter projects as well as DevCapsule itself.

### Configuration is written through commands

DevCapsule commands provide the supported operations for writing project
configuration and its derived documents. They maintain consistency across the
manifest, locks, checkout configuration and resolution. Missing operations
must be implemented as commands, not worked around by agent-authored file edits.
Commands validate the starting configuration and proposed change before promoting
it, and expose a validation path that does not require applying the change first.

Writers preserve unrelated choices and use compatible representations rather
than introducing a newer requirement incidentally. Unknown optional declarations
must survive a supported round trip; when a writer cannot safely preserve them,
it explains the limitation and refuses that mutation without destroying the
existing documents or unnecessarily preventing their usable runtime subset.
Compatibility validation must include the consumer that will use the output,
not just the producer's newer implementation.

### Mandatory needs and optional enhancements are distinct

The project explicitly distinguishes capabilities essential to its usable
baseline from optional enhancements. The consumer resolves the usable subset
against its own implementation and the checkout's environment.

An unsupported or unavailable optional capability produces a clear warning
naming the omission, why it occurred and the functionality that will be missing.
If all mandatory needs can still be met, ordinary launch continues with that
reduced environment. A missing mandatory capability receives an actionable
explanation and prevents a launch falsely claiming to satisfy the project.
An optional dependency of a mandatory capability cannot be silently omitted
when doing so would break that mandatory capability.

Graceful degradation is local runtime behavior. It does not delete declarations
from the shared manifest, rewrite its lock to the local launcher's subset, or
silently reduce the project's mandatory needs. A more capable collaborator can
still use the enhancement from the same shared project. Tolerant reading does
not authorize ignoring constraints needed for integrity or host-access boundaries.

### Project scope and developer ownership

Owner refinement, 2026-10-06: the project describes the ideal developer
experience. Do not introduce capability profiles per task or workstream.
Required/optional describes necessity; project/developer describes ownership.
The required Python SDK and its major version are a shared contract. Playwright
is an optional project enhancement. IDE and coding-agent/provider selections
belong to each developer, with local exact-version pins; they must not impose
the original author's preferred agents on collaborators. Local choices cannot
waive mandatory project constraints. Installing a tool grants no host access.

### Self-hosting requires a deliberate transition

DevCapsule developed inside DevCapsule creates a circular dependency. This is
an allowed, managed exception. Before this project's configuration changes,
validate it using at least the running instance's identifiable `devcapsule0`;
validate the candidate and resulting configuration as well. Testing only with
the new code is insufficient. Preserve a known working tool and an independent
host-side restart/recovery path when intentionally adopting a development build.
An inspection listing does not count as complete configuration validation.

## Acceptance scenarios

- A newer contributor adds an optional capability through a DevCapsule command.
  A less capable supported launcher reads the updated project, warns about the
  omitted capability and launches the mandatory environment. Shared documents
  are unchanged by that degraded launch; a capable launcher provides the extra.
- The equivalent addition marked mandatory cannot be satisfied silently. The
  diagnostic names what is missing and an actionable path forward.
- Dependency handling never reports mandatory functionality satisfied after
  removing something it requires.
- A command preserves unknown optional declarations when modifying an unrelated
  supported value, or safely refuses that mutation while retaining the prior
  documents and usable launch path.
- Invalid or incompatible proposed changes are caught before replacing working
  configuration. Failed/interrupted changes retain a recoverable consistent state.
- The self-hosting path validates with the recorded `devcapsule0` baseline as
  well as the candidate. Evidence identifies both executables and distinguishes
  parsing, resolution/runtime planning and an actual next-session launch.

## Implementation and rollout

The implementation uses project `required`, `optional` and `sdk-major`
declarations, with developer selections in the local checkout record. The
[configuration guide](../../../docs/configuration/capabilities.md) describes
`init --required`, `config capabilities`, read-only `config check`, preview,
omission and recovery. Legacy `need` inputs remain readable. Capability policy
is project-scoped; no task/workstream profile is introduced.

Existing shipped binaries cannot retroactively learn this contract. Adoption
requires a reader containing the implementation; release sequencing remains
project-management's responsibility. Inspection on 2026-10-05 established that
the running `devcapsule0` lacked read-only candidate checking and classification
commands. The implementation does not replace that executable or migrate this
self-hosting checkout's manifest/lock. Such migration still requires the
baseline/candidate validation and independent restart path above.

## Related

- [R-COMPAT-001](../devcapsule/r-compat-001-client-upgrades-require-no-user-action.md)
  protects old project inputs when the client upgrades. This requirement also
  covers newer shared-project contributions reaching a less capable client.
- [R-UPGRADE-001](r-upgrade-001-component-version-sets.md) governs local selections,
  consent and recovery; the new contract must compose with those decisions.
- [Playwright regression](../../bugs/devcapsule/2026-10-04-unreleased-playwright-breaks-checkout-launch.md)
  supplied the concrete failure; removing the component was only a containment fix.
- [Local workflow](../../../WORKFLOW-LOCAL.md#keep-the-development-checkout-launchable)
  applies the owner's command-only and baseline-validation rules immediately.
