---
status: confirmed
severity: minor
target: 0.9
owner: maintenance
opened: 2026-08-03
requirements: [R-PRODUCT-001, R-PRODUCT-004, R-DEV-001, R-FRAMEWORK-001]
---

# Gap: Fresh Clones Require Manual Ecosystem Bootstrap

Date opened: 2026-08-03

Status note (pre-vocabulary, kept as evidence): reproduced; accepted V1 backlog item

Requirements: root R-PRODUCT-001, root R-PRODUCT-004, R-DEV-001,
R-FRAMEWORK-001

## Retargeted, 2026-10-18: 0.9, behind project-type templating

Applied by `maintenance` with the 0.3.0 cut, from the owner's decision of
2026-10-11 in the project-management release-scope review
([the decision record](../../wip/2026-08-09-project-management/2026-10-11-decision-project-operations-and-bootstrap.md)).
The record stays a confirmed minor bug owned by `maintenance`; what changes
is its timing and direction. Target **0.9**, and out of 0.3.0, whose
[release overview](../../releases/v0.3.0/README.md) names it among the
exclusions. Revisit at the 0.9 planning, with the dependency made explicit:
bootstrap needs a way to express the project type or ecosystem the user
intends, through project templating (Java with Maven, Scala with sbt, Python
with nox as in this repository, Node with npm or Yarn are the examples, not
a chosen format), and discovers tooling from that intended type.
Project-management sequences the templating dependency; its implementation
owner and design are not selected by the decision.

The direction the owner set: the capsule is bootstrapped so the project's
tools are on `PATH` by default throughout, for the developer, the IDE, the
terminals and the agent processes, without installing project dependencies
into a shared system environment; for project types that need it, the
documented exception is an activated shell, `devcapsule project shell`,
which belongs to the 0.9 direction and is not promised for 0.3.0. The
versioned-adapter design and the Python and non-Python proof below remain
design input for that slice. The 2026-10-05 triage that follows is history:
its target 0.3.0 is superseded by this ruling.

## Triage, 2026-10-05: a bug after all, target 0.3, behind the bigger fish

Owner ruling during the 0.2.16 triage. The proposed reclassification as a
feature (no requirement names ecosystem bootstrap, nothing released broke)
is rejected: the product carries an implicit promise that a developer is
onboarded in minutes, and a fresh clone that opens its IDE but cannot run
its own tests breaks that promise. The owner's evidence is the 2026-10-03
incident, where a capable agent pair in the dogfood capsule failed to bring
`nox` into scope and run the unit tests; a student in a first programming
course would be more lost still. The record stays a bug. Target **0.3.0**,
the next release, named so by the owner's decision of the same day (it was
to be 0.2.16). It is deliberately sequenced after the larger items of that
release: the recursive-successor test, the installed-IDE reuse and reaping
design, the in-capsule project-command fix.

## Symptom

A developer cloned the DevCapsule repository and successfully launched its
v021-backed PyCharm environment, but the checkout was not ready for normal
development. The developer still had to create `.venv`, activate it, and
install Python dependencies manually.

That sequence is familiar to an experienced Python developer, but it breaks
the expected clean-clone DevCapsule experience. It also cannot be generalized
by hard-coding Python commands: Java, Node.js, and other project ecosystems
have different toolchains, dependency managers, caches, generated state, and
readiness checks.

The existing `devcapsule bootstrap project` path bootstraps reusable workflow
documentation. It does not prepare a project's language-specific development
environment and must not be confused with this backlog item.

## Expected Behavior

A project can declare the development ecosystems and bootstrap strategies it
supports. Resolution selects curated, versioned ecosystem adapters and emits
an inspectable workspace-bootstrap plan. On first run, DevCapsule can prepare
the selected environment, install dependencies, configure the IDE/runtime to
use it, and verify readiness without requiring users to know ecosystem setup
commands.

Examples of distinct adapter behavior include:

- Python: create a selected virtual environment, install through the declared
  pip/requirements/packaging strategy, and expose its interpreter and scripts;
- Java: select the locked JDK and use the declared Maven or Gradle wrapper and
  dependency/bootstrap policy; and
- Node.js: select the locked runtime/package manager and use the declared
  lockfile-based installation strategy.

These examples are not permission to infer an arbitrary command from the
presence of one file. Ambiguous or unsupported repository shapes must produce
an actionable choice instead of silently guessing.

## Security And Lifecycle Constraints

Dependency installation and build-system initialization can execute code from
the checkout and the network. Therefore:

- `config resolve` must show the selected adapter, inputs, intended writes,
  network requirement, and commands or equivalent structured operations;
- the first execution requires explicit developer consent, which can be
  recorded against the exact bootstrap-plan/input digest for routine reruns;
- non-interactive operation must require an explicit prior authorization or
  fail with the command needed to grant it;
- bootstrap runs as the unprivileged development identity and does not imply
  Docker, sudo, host-network, credential, or host-filesystem authorization;
- secrets and credentials must not be embedded in the committed declaration,
  lock, resolution, image, or logs; and
- failures must preserve sanitized, actionable logs and leave the operation
  safely retryable.

## Proposed V1 Direction

1. Add a versioned ecosystem-bootstrap adapter contract selected by committed
   project capabilities and the platform lock.
2. Keep adapter operations structured and curated for V1. Do not introduce an
   unrestricted project-defined host hook disguised as bootstrap metadata.
3. Give every plan a canonical digest derived from the adapter version,
   relevant dependency/lock files, toolchain identity, and configuration.
4. Record successful readiness per checkout and rerun only when the plan or
   declared inputs change, the environment is missing, or the developer asks
   for repair/rebuild.
5. Define where generated environments and dependency caches live. They must
   remain checkout-scoped or deliberately shared, must not enter committed
   source, and must obey persistence and concurrency rules.
6. Apply declared runtime environment contributions so users do not manually
   activate a Python virtual environment. The IDE, terminal, and child build or
   agent processes should resolve the same interpreter and tools.
7. Expose status and explicit maintenance actions such as inspect, retry,
   repair, and rebuild without deleting source or unrelated persistent state.

The generic runtime-path metadata backlog item is related but distinct: it
exposes selected tools such as Node.js. This item creates and maintains the
project-specific development environment that consumes those tools.

## Verification Target

1. A clean Python fixture reaches a working interpreter and dependency import
   through the declared adapter without manual `venv` creation, activation, or
   installation commands.
2. Repeating `project run` is idempotent and does not reinstall unchanged
   dependencies.
3. Changing a declared dependency input makes readiness stale and triggers the
   documented review/reconciliation path.
4. Tests cover refused consent, offline/network failure, partial installation,
   repair, invalid or ambiguous project metadata, and sanitized logs.
5. At least one Java fixture proves that the contract is ecosystem-generic
   rather than Python commands hidden behind a generic name.
6. The external DevCapsule dogfood checkout builds and runs its normal test
   workflow after first launch without the reported manual setup sequence.

## Close Criteria

Close this item when a fresh supported checkout can move from resolved project
configuration to a ready IDE workspace through a reviewed, idempotent,
ecosystem-specific bootstrap adapter; Python and at least one non-Python
adapter demonstrate the generic contract; repeated launches remain fast; and
the security, persistence, failure, and external dogfood checks pass.

Reopen if normal onboarding again requires undocumented language setup, if
DevCapsule guesses and executes an unsafe bootstrap strategy, or if the
implementation treats every ecosystem as a Python virtual environment.

## Disposition, 2026-09-25

Owner ruling during 0.2.14 acceptance: deferred beyond 0.2.14 and marked
minor; no functional failure was reported on any 0.2.14 candidate.
