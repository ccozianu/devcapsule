# Playwright, IntelliJ IDEA and a reusable agent-driven IDE smoke test

Date: 2026-10-03

Status: proposed execution work order; requested outcomes recorded, awaiting
the owner's marching order before implementation.

Owner: `component-catalog`, branch `ws-component-catalog/intellij-idea`.
IntelliJ's assigned release target remains 0.2.16. This order does not cut or
publish a release.

Requirements: `R-PRODUCT-001`, `R-PRODUCT-002`, `R-DOCS-002`, and the existing
component, persistence and recursive-test contracts. Map the new concrete
behavior into the appropriate requirement/specification records during design.

## Outcome

A DevCapsule developer can select Playwright as a component, build a new
DevCapsule from changed source and component definitions, and have an agent
drive its graphical desktop through Playwright to prove its IDE is usable.
IntelliJ IDEA becomes an ordinary selectable IDE component and is the first
acceptance run for this order. The driving tool is **Codex** and the driving
model is **`gpt-6-astra`**, selected explicitly and recorded in the evidence.

This must work in future instances of the DevCapsule development environment.
The current capsule may bootstrap Playwright under `/opt/xtras/` as explicitly
authorized by the owner; that installation alone does not deliver the component.

## Mainline evidence read before planning

Source inspected: `origin/main` at `69ced649db27d65fbd8d5f4139845174a6432d56`.
The continuation branch includes that source without a synchronization gap.

- [IDE smoke test](../../devcapsule-src/tests/e2e/test_ide_comes_alive.py):
  one parametrized test over the supported surfaces; asserts the desktop HTTP
  response and an IDE-owned X11 window, with optional browser pixel evidence.
- [IDE session helper](../../devcapsule-src/tests/e2e/ide_session.py):
  initializes a fresh project through the selected executable, launches a
  real capsule, reads its ready URL, and cleans up test-owned resources.
  Inside a capsule it places the project on a host-backed workspace. Its
  Playwright helper records a screenshot and WebM from the noVNC canvas;
  absent Playwright or Chromium currently returns no pixel evidence.
- [Nox entry points](../../devcapsule-src/noxfile.py): `ide-smoke -- --display`
  installs the Python Playwright package and Chromium into the test environment.
  Playwright is pinned there, outside the component catalog.
- [Recursive clone protocol](../../devcapsule-src/tests/e2e/test_recursive_local_clone.py)
  and [successor lifecycle test](../../devcapsule-src/tests/e2e/test_recursive_successor_lifecycle.py):
  existing foundations for exact source/runtime identity, isolated workspaces,
  ownership and cleanup. These are distinct from the IDE smoke entry point;
  neither test's name alone establishes the requested graphical acceptance.
- [E2E guide](../development/e2e-tests.md): local Docker-backed testing,
  artifact selection and evidence locations; these runs are opt-in.

The inspected graphical path contains no LLM-driver abstraction or Claude
invocation. The owner's recollection of Claude may refer to an interactive
agent session; that history is not claimed as a checked-in automated driver.
Preserve the existing deterministic checks and extend the shared path.

## Deliverable 1: Playwright as a component

1. Add a selectable catalog component using the project's normal declaration,
   acquisition, version, materialization and dependency mechanisms. Include
   the browser binary and operating-system dependencies needed for a working
   headless browser, not just an importable package.
2. Prefer the Python Playwright binding and Chromium already used by the smoke
   helper. Verify supported vendor versions and installation behavior before
   choosing pins. Record any reason to introduce a different binding or agent
   transport; avoid two independent browser installations merely for two callers.
3. Make the runtime discoverable to tests, terminals and agent tools. Reconcile
   the current Nox installation path with the component so the test does not
   silently download another version or depend on an unrelated virtualenv.
4. Add Playwright to this repository's development-environment requirements
   and regenerate affected configuration through supported tooling. Prove a
   freshly materialized development capsule can launch its browser without
   repeating the manual `/opt/xtras` bootstrap.
5. Keep managed components, browser caches and developer-owned `/opt/xtras`
   content distinct. Preserve existing files, use explicit versions, and document
   discovery, selection, cache/persistence behavior and the bootstrap route.

## Deliverable 2: IntelliJ IDEA as a component

1. Add IntelliJ as an optional IDE surface through ordinary project selection
   and launch, reusing the JetBrains adapter and component contracts. Inspect
   edition/distribution, acquisition terms, launcher, JDK requirements, state
   slots and first-run behavior before choosing the implementation.
2. Prefer a supported distribution whose basic smoke can run without buying a
   license. If edition or licensing changes the intended product experience,
   bring that concrete choice to the owner before committing to it.
3. Keep IntelliJ settings, plugins, caches and logs separate from PyCharm and
   preserve the normal persistence and host-access rules. Verify a relaunch
   retains a harmless IntelliJ setting without altering another IDE's profile.
4. Extend the shared surface table and smoke scenario for IntelliJ, expecting
   the `jetbrains-idea` window class. Preserve PyCharm and VSCodium behavior.

## Deliverable 3: shared browser scenario and agent driver

Separate three responsibilities in the existing harness:

- **Session orchestration:** source/artifact selection, successor launch,
  desktop readiness, browser connection, evidence and cleanup.
- **Smoke scenario:** IDE identity, test project, observable task and success
  conditions, parametrized by the surface rather than copied into test classes.
- **Agent driver:** tool/provider and model selection, observation/action loop,
  limits and structured result. The first implementation invokes Codex with
  `gpt-6-astra`; changing driver configuration must not duplicate the scenario.

Use one small driver contract carrying the task, browser-tool access, evidence
destination and limits, and returning actions, observed results, model identity
and a success/failure/inconclusive outcome. Exact interfaces follow inspection.
Do not build a general agent platform or a second full provider integration
merely to demonstrate extensibility; a fake driver can test the contract.

The model must actually observe and act through Playwright against the
successor's graphical desktop. A scripted screenshot followed by an LLM saying
"passed" is insufficient. The noVNC desktop is a canvas: expose screenshots
and mouse/keyboard actions where the IDE has no browser DOM controls.
The real run must include a bounded, harmless interaction, such as opening the
known fixture file in the editor, entering a unique test marker and saving it.
Check the saved marker independently in the test-owned workspace.

Each smoke invocation launches one test-owned successor; there is no unbounded
chain of recursive self-tests. The driver and browser may run in the parent
development capsule, observing the child, so agent credentials need not enter
the IntelliJ capsule.

Keep the HTTP and window-class checks as independent facts. Require browser
evidence and a real configured-model run in the agent acceptance mode; missing
Playwright, Chromium, model access or credentials must produce an explicit
failure or blocked result, never a silent fallback or passing skip. Retain the
lighter deterministic mode for ordinary development.

Record finite launch, browser, agent and overall timeouts, a maximum action
count and bounded retries. Report actual usage when exposed by the driver;
do not claim an exact cost that the provider does not report. Missing access
to `gpt-6-astra` is a blocker, not authorization to substitute another model.

## Acceptance ladder

1. **Component checks:** focused tests of declarations, dependency resolution,
   installation identity, selection and state separation; confirm Playwright
   can launch its installed browser. Exercise driver failures and limits through
   the shared contract, without paid-model calls in unit tests.
2. **Required gate:** run the repository gate. First correct the scratch-location
   setup recorded in this workstream's status; distinguish setup failures from
   product regressions rather than weakening assertions.
3. **Fresh development capsule:** from an identified source commit, build the
   executable and materialize a test-owned successor with the updated component
   definitions. Prove the successor uses those bytes and provides Playwright
   through its selected components, independently of this capsule's bootstrap.
4. **Graphical acceptance:** from the development capsule, launch a fresh
   IntelliJ project using the updated executable through the ordinary launcher.
   Codex with `gpt-6-astra` drives the Playwright browser against that successor.
   Pass the desktop/window checks and the visible interaction with its independent
   saved-file check. Capturing an old container or using the embedded old
   executable is not acceptance of the new code.
5. **Regression and lifecycle:** run the shared deterministic smoke on PyCharm
   and VSCodium and the IntelliJ persistence check. Capture exit/cleanup results;
   remove only resources owned by the run and retain useful failure evidence.
6. **Repeatability:** document one command and its explicit prerequisites for
   a future developer/agent pair to repeat the Codex-driven smoke. Repeat once
   from the component-equipped environment to establish that no ad hoc install
   or unexplained manual click was necessary.

Evidence per run includes source SHA, executable checksum, component/browser
versions, image and container identities, selected and reported tool/model
identity, launch logs, independent readiness facts, screenshots/video or trace,
  agent actions and verdict, the unique marker result, timeouts and cleanup.
Separate facts from the model's interpretation. Keep credentials and desktop
access tokens out of shareable records; use the existing evidence locations.

## Execution authority and stopping points

This turn prepares the order. The owner's subsequent marching order starts
implementation. Under that grant, routine design choices, component acquisition,
the authorized `/opt/xtras` bootstrap, local builds, recursive launches, bounded
model-driven tests, fixes, commits and branch delivery proceed without repeated
permission. Use the existing host-Docker and host-network authorization and
the owner's authorized Codex authentication; do not copy broad credential state
into disposable successors. Record how the agent driver accesses its credentials.

Ask only when product intent remains consequential, required credentials/model
access are unavailable, a paid license or new host boundary is required, or the
work must change workstreams. Changes necessary for these components and their
test harness belong in this slice; a general orchestration/upgrade redesign
still belongs to `component-upgrades` and is coordinated with its owner.

No website gitlink update belongs to this workstream. Opening/merging pull
requests, release publication and production changes remain with the owner
under the local policy. Finish with committed and pushed changes, current
published status, runnable instructions and honest acceptance evidence; the
deliverable reaches `main` through the owner's normal PR integration.
