# Gap: Fresh Clones Require Manual Ecosystem Bootstrap

Date opened: 2026-08-03

Status: reproduced; accepted V1 backlog item

Requirements: root R-PRODUCT-001, root R-PRODUCT-004, R-DEV-001,
R-FRAMEWORK-001

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
