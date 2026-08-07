# DevCapsule V1 Gap Review

Status: review in progress; first engineering milestone selected on 2026-08-06

Applies as of: 2026-08-06

Repository revision reviewed:
`0a0ff09e767d38ecec4c92cb21cfd7afa6acffc9`
(`Clarify V1 IDE configuration sequencing`)

Branch reviewed: `wip/local-pycharm-materialization`

Requirements: root `R-PRODUCT-001`, `R-PRODUCT-002`, `R-PRODUCT-004`,
`R-DOCS-002`; DevCapsule `R-STATE-001`, `R-SCOPE-001`, `R-DOCKER-001`,
`R-IDE-CONFIG-001`, `R-PYTHON-MVP-001`, `R-PYTHON-MVP-002`,
`R-PYTHON-MVP-003`, `R-IMAGE-BUILD-001`, and `R-FRAMEWORK-001`.

## Purpose And Scope

This is the consolidated review of the known gaps between the accepted v023
functional dogfood checkpoint and the DevCapsule V1 release. It is a snapshot
at the date and revision above, not a requirement register or an immutable
design decision. Later implementation, validation, product-owner decisions,
or newly discovered defects may change it.

The review separates two kinds of release work:

- **Functional gaps** are behavior an adopter can directly use or observe.
- **Engineering gaps** are the build, validation, dogfood, and release
  machinery needed to prove and safely ship that behavior.

An engineering need can produce useful public functionality. For example,
recursive dogfood needs sanitized launch inspection; the recursive test
orchestrator belongs to engineering, while a generally useful `doctor` or
effective-plan command belongs to the functional product surface.

## Terminology Used In This Review

- **Release:** an externally meaningful product version with a defined product
  contract, artifacts, documentation, and acceptance evidence. V1 and V2 are
  releases.
- **Milestone:** a coherent, outcome-based checkpoint on the path to a release.
  A milestone has explicit closure criteria and evidence and normally contains
  several tasks.
- **Stage:** a sequential subdivision inside a plan or milestone. A stage helps
  execution but is not itself an externally promised release boundary.
- **Task:** a bounded implementation, documentation, investigation, or
  validation unit within a milestone.
- **Slice:** the narrow unit executed in one human/agent work cycle.
- **Checkpoint:** a durable state snapshot or handoff. A checkpoint may record
  partial work and does not by itself claim milestone completion.
- **Release candidate:** an actual candidate set of versioned release artifacts
  and documentation subjected to release acceptance, not a synonym for an
  ordinary milestone.

## Baseline Already Closed

This review does not reopen the accepted functional dogfood checkpoint. That
checkpoint established:

- a capability-first project declaration and immutable digest-pinned base;
- developer-owned values, state bindings, and explicit Docker, network, and
  development-sudo authorization;
- automatic canonical PyCharm materialization and strict reuse;
- checkout-neutral images with an external read-only runtime plan;
- persistent PyCharm and component-owned Codex state;
- safe unauthorized Docker and sudo behavior;
- a revision-bearing PEX embedded in the managed base; and
- a manually accepted second-checkout PyCharm/Codex dogfood environment.

The retired laptop-specific second-checkout script is not a missing deliverable.
Its portable coverage belongs to the engineering E2E work below.

## Part 1: Functional, User-Visible V1 Gaps

### F1. Clean Checkout To Ready Development Environment

A supported project should not require the user to manually create and
activate a virtual environment, install dependencies, or repair tool paths
before ordinary development.

Required outcome:

- a versioned, curated, inspectable ecosystem-bootstrap adapter contract;
- explicit consent before first execution of dependency or project-controlled
  code;
- idempotent readiness detection, retry, repair, and actionable sanitized
  failure evidence;
- a Python adapter and at least one non-Python adapter proving that the
  contract is ecosystem-generic;
- project-specific interpreter and tool selection shared by the IDE, terminal,
  build processes, and agents; and
- generic component runtime-path contributions so locked tools such as the
  curated Node.js installation are usable by name in all supported processes.

The source records are the ecosystem-bootstrap and component-runtime-path bug
notes. They should be closed against this combined user outcome rather than by
adding another one-off Python or Node launcher workaround.

### F2. Complete The PyCharm Reference Experience

PyCharm is the reference path for settling V1 user experience and reusable
contracts.

Required outcome:

- schema-validated ordinary-value defaults;
- checkout overrides plus an explicit reset-to-default operation;
- `config list` distinction between defaults and overrides;
- manifest changes making prior resolution stale;
- this repository declaring an 8 GiB default memory limit;
- Docker `HostConfig.Memory` and cgroup enforcement for the effective default
  or override;
- final Codex CLI, JetBrains ACP, authentication, and restart-persistence
  validation through component-owned `CODEX_HOME`;
- fresh-state Markdown and SVG preview validation for the accepted unsandboxed
  JCEF workaround; and
- sanitized extended runtime/IDE logging that preserves useful failure
  evidence without exposing credentials.

The JetBrains native-launcher recommendation and slow-X11 alpha-compositing
warning remain reviews rather than release blockers unless validation finds a
repeatable user-visible defect.

### F3. Finish The Reusable Configuration And Component Model

A new configuration should primarily declare behavior through supported
contracts rather than require another hard-coded command tree or launcher.

The V1 authoring model must cover:

- one interactive IDE component and optional ancillary components;
- pinned artifacts and license/trust metadata;
- materialization and formation identity;
- IDE-specific installation, entrypoint, and configuration behavior;
- runtime environment and ordered `PATH` contributions;
- persistent, cache, and credential-bearing state slots;
- project bootstrap adapters;
- ordinary runtime effects and safe defaults;
- project recommendations versus developer-owned host authorization; and
- schema validation, inspection, documentation, and actionable unsupported-set
  failures.

V1 needs a documented and testable supported authoring path. The proof is that
later IDE configurations use these contracts without copying PyCharm's private
implementation or reviving v0 configuration-specific shortcuts.

### F4. Reimplement The VSCodium Proof Point And Revalidate Old Bugs

Repairing or replacing the VSCodium proof point represented by
`codium_with_claude` is a must-have V1 outcome, but it follows the PyCharm-led
abstraction work.

Required outcome:

- at least one VSCodium-based configuration implemented through the V1
  component/configuration contracts;
- safe defaults with no ambient sudo, writable root, Docker access, host
  network, credentials, or other unapproved isolation relaxation;
- persistent editor, extension, cache, and selected agent state with validated
  concurrency behavior;
- working project bootstrap, terminal tooling, IDE lifecycle, and selected
  agent integration; and
- fresh reproduction of the historical Codium bug reports against the V1
  implementation.

Behavior that still fails is a V1 defect. A report tied only to a removed v0
launcher can be closed as obsolete with evidence. Literal flag-for-flag parity
with the transitional PyCharm launcher is not itself the product goal; shared
capabilities and consistent safety semantics are.

### F5. Ship A Small Starter Configuration And Demo-Project Catalog

V1 should include a handful of curated IDE configurations with matching demo
projects so a new user can perform a quick, low-commitment experiment before
authoring an advanced configuration.

Each selected entry should demonstrate:

- a meaningful IDE/component combination rather than a cosmetic variation;
- a small project with a supported bootstrap strategy;
- safe defaults and clearly explained optional host integrations;
- persistence and repeat-launch behavior;
- a short configure, resolve, run, and inspect journey; and
- how the same abstractions can be used for a user-authored configuration.

The exact entries and number remain a product-owner choice for the V1 plan.
The catalog is successful when it proves self-service configuration authoring,
not when it claims exhaustive IDE support.

### F6. Provide Coherent Inspection And Limited Lifecycle UX

Before materialization or launch, a user should be able to understand what
DevCapsule selected and what it will expose.

Required V1 inspection includes:

- every effective value and its source;
- defaults versus checkout overrides;
- recommendations versus persistent or run-once authorization;
- selected components, artifacts, source revision, and formation identity;
- state roots, paths, destination, lifecycle, sensitivity, ownership, and
  whether a slot is in use;
- sanitized acquisition, materialization, bootstrap, runtime, and Docker plans;
- stale-resolution and readiness explanations; and
- environment diagnostics suitable for both a human and an agent.

The accepted state specification currently promises a larger management
surface than the implementation provides. The recommendation for V1 is to
implement read-only roots/list/path/inspect plus the already needed safe
binding/adoption behavior, and to defer destructive move/remove/clean and
profiles unless onboarding demonstrates that they are required. Changing that
promise requires an explicit specification or decision update rather than
silent omission.

### F7. Close Safe Expert Runtime Control

The ordinary capability-first path remains safe and simple. The accepted
`project run-image` recovery/expert path still needs its promised explicit
runtime controls.

Required outcome:

- bridge networking by default and explicit host-network selection;
- explicit Docker-daemon and custom-socket selection;
- explicit development sudo, writable-root, native-debugging, and
  Docker-in-Docker behavior where supported;
- structurally validated repeatable advanced Docker arguments;
- sanitized explanation of every isolation relaxation; and
- restrictive workstation policy as the upper boundary.

The open multiline Dockerfile rendering bug on transitional `pycharm build`
must either be fixed and manually validated or the command must be explicitly
removed from the supported V1 surface in favor of `images build`.

### F8. Make V1 Installable And Consumable

From an adopter's perspective, V1 requires:

- a downloadable, versioned `devcapsule-1.0.0.pex`;
- a supported base available through an immutable registry digest;
- clean-machine/clean-clone installation and first-run instructions;
- `devcapsule version` reporting the product version, exact public source
  revision, and canonical source URL; and
- committed locks using globally resolvable immutable references.

The publication, checksum, scan, and clean-download machinery that proves these
claims belongs to the engineering section.

### Functional Scope Decisions Still Required

The V1 plan must explicitly decide:

1. whether the NVIDIA/CUDA recipe is supported V1 functionality or an
   experimental/post-V1 recipe;
2. whether D-0001's catalog freshness, security-advisory warning, and explicit
   update-preview contract ships in 1.0 or is superseded/deferred explicitly;
3. the exact starter configurations and demo projects;
4. which transitional configuration commands remain supported in V1; and
5. the final minimum state-management surface.

## Part 2: Engineering V1 Gaps

### E1. Bootstrap And Build A Clean Source Clone Inside Dogfood

The existing checkout is build-ready because it already has its contributor
virtual environment and has repeatedly passed the Nox gate. The gap is more
specific: a newly cloned checkout inside dogfood does not yet have a
product-owned automated path from source files alone to a ready isolated build
environment.

Required outcome:

- create an exact-revision clean clone without inheriting the existing
  checkout's `.venv` or unrecorded setup;
- bootstrap its contributor environment through a documented, reproducible
  path;
- run the full Nox build gate;
- produce a revision-bearing PEX;
- build a uniquely tagged managed base containing that PEX; and
- verify the image inventory, labels, source revision, PEX digest, and OCI
  process contract.

The base image does not need ambient contributor dependencies. Isolation of
project dependencies remains desirable; the missing feature is automated
bootstrap, not global installation of `nox`, `click`, or the repository's
entire contributor environment.

### E2. Support Safe Recursive Host-Docker Orchestration

A DevCapsule running inside Docker needs an explicit delegation context before
it can correctly build and launch a successor through an authorized host Docker
daemon.

Required engineering capability:

- detect and report that the selected Docker endpoint is the host daemon;
- translate only approved in-capsule paths to their host-daemon source paths;
- provide a separately authorized host workspace root for test clones rather
  than nesting another clone in the current source tree;
- prepare successor display/Xauthority state without leaking the cookie in
  Docker environment metadata;
- launch a successor detached while retaining IDE-owned container lifecycle;
- make mutable IDE and credential-state sharing explicit and avoid it by
  default; and
- never stop the current capsule automatically.

Host Docker access is already a broad security authorization. It does not make
unrelated host filesystem roots, Git credentials, or shared agent/IDE state
implicit.

### E3. Build A Disposable Recursive Dogfood E2E Orchestrator

The target engineering flow is:

```text
inspect current capsule
-> create exact-revision local clone
-> bootstrap clone
-> run full build gate
-> build and verify new PEX
-> build and inspect new base
-> configure clone beneath isolated XDG roots
-> authorize exact local base and required host capabilities
-> resolve and materialize successor
-> launch successor container
-> inspect runtime behavior and persistence
-> clean only test-owned resources
```

Automated assertions must cover:

- base and materialized formation identities;
- PEX/image source-revision agreement;
- generic OCI entrypoint and command;
- external read-only runtime plan and absence of baked checkout data;
- project, persistent-home, and component-state mounts;
- runtime UID/GID and supplementary groups;
- network and memory behavior;
- authorized and safe unauthorized Docker/sudo cases;
- absence of unintended privileged mode, capabilities, and host access;
- IDE process and container lifecycle; and
- second-launch persistence where it is part of the contract.

### E4. Make E2E Isolation, Evidence, And Cleanup Deterministic

The orchestrator must:

- use unique temporary checkout and XDG configuration/data/state/cache/runtime
  roots;
- use unique resource names and explicit test-ownership labels;
- never read or mutate personal checkout records, state, or credentials;
- never delete unrelated containers, images, volumes, or build caches;
- clean test-owned resources on success, failure, and interruption;
- emit sanitized evidence and preserve useful diagnostics on failure; and
- support an explicit keep-on-failure or equivalent diagnostic mode.

### E5. Add A Shared Configuration Conformance Suite

Every starter configuration should run against common tests for:

- schema and lock validation;
- formation identity and strict image reuse;
- artifact acquisition and checksum rejection;
- state, environment, and runtime-path contributions;
- safe default and explicitly authorized runtime plans;
- secret redaction and temporary-file cleanup;
- bootstrap readiness and repeat launch;
- foreground/detached lifecycle as applicable; and
- source-install and PEX command equivalence.

IDE-specific tests should cover only genuine vendor differences. Historical
Codium bugs should be re-evaluated through this suite plus focused VSCodium
tests after the new implementation exists.

### E6. Define The Automated Versus Manual GUI Boundary

Docker inspection, logs, process state, generated files, and repeat launches
should automate all machine-observable behavior. The remaining human check may
be deliberately small:

1. confirm that the successor IDE window appears and is usable;
2. exercise representative editing, terminal, preview, and agent behavior;
3. close the previous IDE when ready to complete the handoff; and
4. report the result so the handoff and validation evidence can be updated.

Pixel-level GUI automation is not a V1 prerequisite unless a concrete defect
cannot be validated through process/runtime evidence plus this manual check.

### E7. Complete Release Engineering And Publication Validation

Required outcome:

- build from the intended clean V1 source revision;
- produce semantically versioned PEX and base artifacts;
- verify embedded source-revision agreement;
- publish PEX checksums and immutable OCI digests;
- run and record the required basic security scan;
- perform a clean PEX download and base pull;
- run functional smoke/E2E checks against the published candidates;
- confirm current documentation and announcement artifact identities; and
- preserve sanitized release evidence.

Signed SBOMs, signatures, attestations, automated policy enforcement, and
stronger verifiable provenance remain post-V1 unless separately pulled forward.

### E8. Validate Every Platform Feature Actually Included In V1

Required validation is limited to advertised V1 platforms and features:

- supported Linux architecture and Docker-host behavior;
- safe Docker/no-Docker and authorized runtime profiles;
- supported X11 GUI workstation behavior; and
- CUDA compiler/runtime, positive device authorization, negative no-device
  behavior, and a real workload only if CUDA remains a supported V1 feature.

## Selected Milestone Sequence Toward The V1 Release

The product owner selected recursive dogfood engineering as the first milestone
so agents can build, launch, inspect, and validate later V1 work from inside the
real dogfood environment. This deliberately changes the initially proposed
functional-first order without changing the gap classification.

### Milestone 1: Recursive Dogfood E2E

Primary gaps: E1 through E4, initially using the accepted PyCharm reference
path. The executable plan is
`devcapsule/implementation-notes/2026-08-06-recursive-dogfood-e2e-milestone-plan.md`.

Closure means an agent in the accepted dogfood capsule can create a clean
clone, build and validate the next PEX/base, materialize and start a successor
on the authorized host daemon, inspect all machine-visible acceptance criteria,
and clean only test-owned resources. One final IDE usability/handoff action may
remain manual.

### Milestone 2: PyCharm Functional Closure

Primary gaps: F1, F2, F3, and the user-facing inspection portion of F6.

Closure means a fresh supported project reaches a ready, inspectable,
persistent PyCharm workspace through the V1 abstractions without undocumented
manual environment setup.

### Milestone 3: Self-Service Configuration Catalog

Primary gaps: F4, F5, F7, E5, and E6.

Closure means the VSCodium proof point and the selected additional starter
configurations use the shared contracts, pass conformance and focused tests,
and provide useful demo journeys with safe defaults.

### Milestone 4: V1 Publication And Acceptance

Primary gaps: F8, E7, E8, final documentation, and final requirement/status
audit.

Closure means the actual versioned V1 candidate artifacts pass clean
consumption, security-scan, functional, engineering, and selected manual
acceptance checks and are ready for the V1 release decision.

## Explicitly Outside The Current V1 Gap Set

- Gemini CLI support of any kind;
- Antigravity or another agent component unless deliberately selected later;
- general secret-provider and SSH-agent catalogs;
- broader IDE/platform coverage beyond the selected starter catalog;
- destructive image/cache lifecycle management unless pulled forward;
- signed SBOMs, signatures, attestations, and automated supply-chain policy;
  and
- alternative GUI transports.

## Next Planning Step

The first milestone is now selected and its executable plan is linked above.
Review that plan, then begin its Stage 0 recursive preflight after product-owner
acceptance. The unresolved functional scope decisions remain open for their
later milestones; selecting recursive dogfood first does not decide or silently
defer them. `CURRENT-STATUS.md` remains the active handoff.
