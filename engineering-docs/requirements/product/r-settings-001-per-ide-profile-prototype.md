---
id: R-SETTINGS-001
title: Per-IDE Profile Prototype
type: requirement
kind: concrete-requirement
status: accepted
priority: later
source_of_truth: repo
verification:
  - doc-review
  - implementation-review
  - manual
external_refs: []
---

# R-SETTINGS-001: Per-IDE Profile Prototype

## Statement

DevCapsule must let a developer establish one default prototype for each
supported IDE and use independent copies of that prototype's configuration and
plugins to seed new project environments. A developer must also be able to
start a project with empty IDE configuration and plugin directories.

The first successful foreground session for an IDE establishes its prototype
after the IDE exits and the state passes minimal validity checks. Once a
prototype exists, DevCapsule never replaces it implicitly. When a later
project's eligible IDE state differs meaningfully, the launcher reports that
fact on standard error after exit and shows the explicit command that would
promote the project's state to the new prototype.

## Why This Exists

Developers normally carry a familiar IDE configuration and plugin set from one
project to the next. Reinstalling and reconfiguring those components for every
DevCapsule project is avoidable toil. Mounting one live, writable IDE directory
into several capsules is not an acceptable substitute because IDE locks and
concurrent writes compromise project isolation.

Independent copies preserve the familiar starting point while allowing
projects to run concurrently and diverge safely. The accepted initial tradeoff
is ordinary full copying: IDE configuration and plugin directories are small
enough that predictable isolation is worth the duplicated storage. Copy-on-write
and filesystem-specific cloning are outside this requirement.

## Acceptance Criteria

- The prototype is developer-owned workstation state, scoped to one compatible
  IDE identity, and never committed to a project or baked into an image.
- A normal first foreground session creates the initial prototype only after a
  clean IDE exit and successful validity checks.
- A crash, interrupted launch, active IDE lock, invalid directory, or failed
  copy does not create or replace a prototype.
- A new project normally receives independent physical copies of the
  prototype's eligible configuration and plugin state before its first IDE
  launch.
- An explicit launch or initialization choice creates empty project-local IDE
  configuration and plugin directories and does not modify an existing
  prototype.
- Prototype updates after initial creation happen only through an explicit
  developer command and replace the prior snapshot atomically.
- After later foreground IDE exits, meaningful eligible changes produce a
  concise standard-error notice containing the exact supported update command.
- The prototype excludes project indexes, caches, logs, general container home,
  agent state, credentials managed outside the IDE profile, and volatile IDE
  files.
- Two running project capsules never attach the same writable prototype or
  project IDE-state directory.
- The baseline implementation uses an ordinary full copy. Copy-on-write,
  hard-link sharing, and filesystem-specific cloning are not required.

## Verification

This requirement is satisfied when repository and manual validation show:

- the first successful IDE session creates a valid prototype;
- failure and crash cases leave any existing prototype unchanged;
- two new projects start from equivalent but independently writable copies;
- the explicit empty-state path starts without prototype contents;
- a later changed project emits the update notice but does not update the
  prototype automatically;
- the explicit update command changes what subsequent projects receive; and
- concurrently running projects cannot corrupt or lock one another's copied
  IDE state.

## Related

- `engineering-docs/specifications/product/ide-profile-prototypes.md`
- `engineering-docs/specifications/product/state-and-persistence.md`
- `R-PRODUCT-001`
- `R-PRODUCT-002`
- `R-STATE-001`
- `R-CONC-001`
