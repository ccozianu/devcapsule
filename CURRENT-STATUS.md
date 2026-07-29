# Current Status

This file is the project handoff point. Future agents should update it when
completing a stage, changing the project state materially, or ending a session.

Current stage: `docker4pycharm` v0/MVP checkpoint complete; `devcapsule`
Python MVP is the active post-MVP refactoring stage.

Current status:

- `docker4pycharm/` preserves the original working PyCharm shell/Docker
  prototype, including historical design context now stored in
  `docker4pycharm/historical-root-README.md`.
- `devcapsule/` contains the active Python package, transitional
  configuration-first CLI, distribution path, tests, and the PyCharm
  configuration package.
- `devcapsule pycharm build` now uses a Python-owned `python-on-whales` /
  Docker buildx backend plus
  packaged PyCharm runtime assets under `devcapsule/`, instead of delegating
  image construction to `docker4pycharm/build-image.sh`.
- D-0001 adopts capability-first project declarations, platform locks, and
  `devcapsule run` as the target end-user model. The currently implemented
  `devcapsule CONFIGURATION ACTION [options]` paths are transitional.
- `codium_with_claude` is the active next proof-point configuration. It is a
  distinct VSCodium plus Claude Code environment; the earlier
  `vscode_with_claude` placeholder remains separate.

Recent documentation cleanup:

- Implementation-specific future refactoring history moved to
  `docker4pycharm/FUTURE_AGENT_REFACTORING_BRIEF.md`.
- PyCharm AI plugin setup moved to `docker4pycharm/user.md`.
- The Click command parsing brief moved to
  `devcapsule/implementation-notes/click_based_cli_parsing_brief.md`.
- Detailed Python/PyCharm implementation requirements moved to
  `devcapsule/REQUIREMENTS.md`.
- Root `README.md`, root markdown files, and top-level `docs/` are now meant to
  stay implementation-agnostic.

Recent workflow refinement:

- Root `WORKFLOW.md` now defines a tighter turn-level collaboration loop for
  human plus agent work: frame a narrow slice, define closure and evidence
  first, execute one coherent slice, report the result succinctly, and choose
  the next branch explicitly.
- Root requirements are now split between an overview/index in
  `REQUIREMENTS.md` and one-file-per-item detailed records under
  `docs/requirements/`, with frontmatter metadata for future machine-readable
  use while keeping the repo as source of truth.
- `devcapsule` requirements now follow the same pattern: overview/index in
  `devcapsule/REQUIREMENTS.md`, canonical per-item files under
  `devcapsule/docs/requirements/`, and a clearer separation between already
  met requirements, active V1 requirements, and explicitly later work.
- Root product requirements now include a concrete go-to-market artifact
  requirement for a compelling V1 adopter announcement, with the first draft
  recorded in `docs/v1-announcement.md`.

Recent positioning refinement:

- On 2026-07-15, `docs/v1-announcement.md` was tightened from an exploratory
  draft into a candidate V1 announcement artifact. It now leads with adopter
  value, states the plain-language problem earlier, adds a concrete before/after
  framing, and replaces open-ended refinement questions with a recommended
  launch angle.
- On 2026-07-15, the GitHub project was renamed to `DevCapsule` and the
  product-facing documentation started shifting to `DevCapsule`.
- On 2026-07-15, the active Python CLI/framework directory, package, entry
  point, documentation paths, Nox gate, and PEX artifact were renamed from
  `docker4ides` to `devcapsule`. The local validation gate passed after the
  rename.

Recent implementation fix:

- `devcapsule` PEX artifacts now package the legacy PyCharm helper assets
  needed by delegated `pycharm build`, `pycharm check-runtime`, and
  `bootstrap project` commands, so those commands no longer require a sibling
  source checkout at runtime.
- `devcapsule` now has a real `mypy` typecheck gate wired into contributor
  dependencies, a dedicated `nox -s typecheck` session, and the default
  `nox -s build` gate. The initial gate runs cleanly on the current tree and
  covers the Python package, tests, and `noxfile.py`.
- `codium_with_claude run` now shares the first extracted runtime-layout slice
  with PyCharm: `--profile`, `--project-state-root`, and `--project-mount`
  are backed by a common planner module while broader Git/Docker/debug/sudo
  parity remains open.
- The active `devcapsule` PyCharm and Codium image-build paths now bundle
  a pinned Node.js archive under `/opt/node/node-{version}` plus pinned npm and
  Gemini CLI tooling as the public-default developer CLI baseline. The old
  PyCharm-specific `--ai-agent` image-build toggle was removed in favor of a
  shared active-tooling baseline across the current Python-owned IDE build
  paths.

Recent manual validation:

- On 2026-07-10, the user confirmed the rebuilt PEX path successfully built a
  new `codex-debug-v012` PyCharm image from the PEX command line and launched
  this environment successfully. Treat the PEX-packaged `pycharm build` fix as
  manually validated.
- On 2026-07-12, the user confirmed the Python-owned,
  `python-on-whales`-backed PyCharm image builder was built and launched
  successfully on the host. Its outstanding host-level validation is complete.

Current proof-point implementation:

- On 2026-07-12, implementation started for the user-selected
  `codium_with_claude` configuration. It composes an Ubuntu 24.04 image with
  VSCodium, Claude Code CLI, Python 3.12, and the current Node.js/npm release
  channels, plus an X11 launcher with explicit project and state mounts.
- This target intentionally does not reuse the registered
  `vscode_with_claude` stub. A local host-network build produced
  `codium-with-claude:latest` and container checks confirmed VSCodium
  1.126.04524, Python 3.12.3, Node.js 26.5.0, npm 12.0.1, and Claude Code
  2.1.207. GUI/X11 and Claude integration were manually validated on
  2026-07-13.
- A build-verified Vite, React, and TypeScript five-in-a-row project now lives
  under `devcapsule/tests/resources/sample_projects/` as a realistic manual
  IDE workload and a future end-to-end-test fixture.
- `codium_with_claude build` accepts `--ide-archive` for a local VSCodium tar
  archive, avoiding the VSCodium apt repository when that option is used.
- The Codium image development baseline now includes `xterm` for direct X11
  validation and `strace` for diagnosing silent process exits.
- `codium_with_claude run --debug-shell` provides interactive Bash through the
  normal entrypoint with the same mounts and X11 environment for host-level
  diagnosis.
- Host debugging confirmed X11 with `xterm`, then traced the silent VSCodium
  exit to Chromium sandbox startup: Docker denies the user-namespace path and
  the archive-installed `/opt/codium/chrome-sandbox` has mode `0755` instead
  of the required root-owned `4755`. The completed validation record is
  `devcapsule/implementation-notes/completed-tasks/2026-07-13-vscodium-sandbox-and-foreground-launch.md`.
- The local-archive build now verifies the sandbox helper and restores its
  root ownership and mode `4755`. The user confirmed `--no-sandbox` opens the
  IDE as a diagnostic; the supported launcher remains sandboxed.
- A command-surface audit found that `codium_with_claude run` lacks most of
  PyCharm's developer runtime profiles. Git transport, Docker modes, native
  debugging, sudo, writable-root, project mount, and profile/state-root
  controls are broadly useful across IDEs and should move into shared runtime
  planning. IDEA lock handling remains PyCharm-specific. The active parity bug
  is `devcapsule/implementation-notes/bugs/2026-07-13-codium-run-option-parity.md`.
- Codium now accepts an opt-in run-time `--network MODE` for both normal and
  debug-shell launches. The default remains Docker bridge networking;
  `--network host` is an explicit host-network isolation relaxation intended
  for development and diagnosis.
- The normal Codium launcher now invokes the Electron binary directly through
  `codium-foreground` instead of the detaching `bin/codium` CLI wrapper, so the
  IDE remains attached to the container lifecycle.
- On 2026-07-13, the user confirmed the rebuilt VSCodium foreground launch and
  Claude integration work. This accepts the Codium plus Claude MVP proof point.
  The validating command explicitly used host networking and `SYS_ADMIN` for
  Chromium sandbox namespaces; neither is an ambient default.
- On 2026-07-16, shared runtime planning was extended so the active PyCharm and
  Codium launchers bind-mount a host Gemini CLI state directory into the
  container home at `~/.gemini`. By default that source is the host
  `~/.gemini`; `DEVCAPSULE_GEMINI_STATE_DIR` overrides it when a different
  persistent Gemini state root is required.

Current architectural direction:

- On 2026-07-11, the user made Python-native, reusable image building the
  current priority. The supported `devcapsule` image-build path must stop
  delegating to or copying build implementation from `docker4pycharm`. The
  active Python package should own build planning and execution, with
  composable inputs for base images, IDEs, and AI-agent options.
- On 2026-07-12, the user selected a Docker CLI-backed Python backend for the
  active image-build path. `devcapsule` should use `python-on-whales` to drive
  local Docker buildx while keeping image planning, configuration composition,
  and CLI behavior in repository-owned Python code.
- `docker4pycharm/` remains useful as historical reference material, but it is
  not the implementation source for the target Python image-build path.

Current validation workflow:

- `devcapsule` uses Nox as the main developer validation entry point. Nox
  reuses its managed virtual environments by default for faster iteration.
  Use `cd devcapsule && python -m nox -s tests` for Python compile checks plus
  pytest, and `cd devcapsule && python -m nox -s build` for the full local
  gate: Python compile checks, shell syntax checks, pytest, CLI smoke tests,
  PEX build, and PEX smoke tests.
- When a clean slate is required, run
  `cd devcapsule && python -m nox --no-reuse-existing-virtualenvs -s build`.
  Removing `devcapsule/.nox/` before the command is also acceptable when
  deliberately discarding cached Nox environments.
- Prefer adding automated Nox-covered checks over relying on one-off manual
  smoke tests. Manual validation is still useful for host Docker/image/IDE
  behavior that cannot yet be exercised in repository automation.

Session checkpoint, 2026-07-22:

- Added the V1 state and persistence specification at
  `docs/specifications/state-and-persistence.md`. It defines a
  checkout-scoped persistent container home, dynamic component-owned state
  slots, XDG-separated configuration/data/state/cache roots, directory and
  Docker-volume storage, collision and concurrency rules, developer-owned
  authorization, state-management commands, and `run-image` behavior.
- D-0001 now uses persistent home as the universal fallback instead of a fixed
  IDE-state/config/plugins model. Components may declare namespaced slots such
  as `pycharm/plugins`, `codium/extensions`, or `postgres/data` only when they
  need lifecycle or storage behavior beyond `HOME`.
- The state specification includes a concrete migration from the current
  PyCharm dogfood command: its existing home, config, plugins, system, logs,
  and caches are adopted once, while the local debug image is launched through
  `run-image` with checkout-owned Docker and sudo decisions.
- D-0001 remains `proposed`. The next step is human review of the completed
  state specification. The user has prioritized a narrow PyCharm dogfood
  implementation of persistent home and component state before settling the
  remaining generic privilege and implementation-constraint grammar.
- This checkpoint changed documentation only. No implementation validation was
  run or warranted.

Session checkpoint, 2026-07-21:

- D-0001 sections 4 through 9 are now settled for the V1 working
  specification. One IDE owns the container lifecycle; curated base images may
  be materialized locally with certified worry-free add-ons such as Node.js
  and OpenJDK; locks pin all materialization inputs and carry update advisories;
  tools do not imply host permissions; DevCapsule is independent of the Dev
  Container specification; and the command grammar is capability-first.
- Committed project files live under `.devcapsule/`. `devcapsule run-image`
  provides an expert, lock-independent path for local images without bypassing
  host-access authorization.
- D-0001 remains `proposed`. The next task is to specify the exact host-backed
  state and configuration directory layout, mount points, lifecycles,
  authorization, inspection, relocation, and cleanup behavior. This must
  confirm the state model before the human adopts D-0001.
- This checkpoint changed documentation only. No implementation validation was
  run or warranted.

Superseded session checkpoint, 2026-07-19:

- D-0001 Option C is the selected direction. Sections 1 through 3 have been
  reviewed and settled for the working specification: hierarchical
  configuration overlays, developer-owned authorization for project
  recommendations, XDG/local-checkout configuration, project and checkout
  identity, durable project-scoped IDE and runtime state, abstract
  capabilities with concrete platform-locked components, and deprecation of
  configuration-first `run` commands in favor of `devcapsule run`.
- D-0001 remains `proposed` while sections 4 through 9 await review. Resume at
  section 4, "Two IDE capabilities resolve to one interactive surface."
- This checkpoint changed documentation only. No implementation validation was
  run or warranted.

Session close, 2026-07-16:

Changed:

- Added a design-decision ceremony. Root product/architecture decisions now
  live in `docs/decisions/` with `_template.md`, and `WORKFLOW.md` documents
  the two tiers, the promotion rule from lightweight implementation notes, the
  propose/review/adopt/propagate/supersede steps, and the triggers. An agent
  may propose; only the human adopts. Accepted records are immutable and are
  replaced by superseding records rather than edited.
- Wrote `docs/decisions/d-0001-capability-first-cli-model.md`, status
  `proposed`. It recommends capability declaration plus a curated resolution
  matrix over both the configuration-first status quo and a full composition
  engine, splits declaration (`devcapsule.toml`) from platform-specific
  resolution locks and personal state, retains `pycharm` as an
  implementation-pinning compatibility alias, and rejects devcontainer
  Features as the top-level capability format.
- Added a capability-first CLI specification task as current task 1, ahead of
  the Codium parity and extended-logging work.
- Opened `devcapsule/implementation-notes/bugs/2026-07-16-codium-ambient-sudo-default.md`.

Requirements:

- If D-0001 is adopted it reinterprets R-IDE-CONFIG-001, which is currently
  `implemented`. No requirement record has been changed yet. D-0001 also bears
  on R-FRAMEWORK-001, R-IMAGE-BUILD-001, root R-PRODUCT-001, and root
  R-PRODUCT-002.

Validated:

- Nothing. This session was documentation-only; no Python changed and no test
  gate was run, because none was warranted.

Not validated:

- D-0001 is unadopted and its Option C recommendation is unreviewed.
- The Codium ambient-sudo bug was found by reading
  `devcapsule/assets/codium_with_claude/entrypoint.sh` and the launcher, not by
  reproducing it on a host. Confirm before fixing.
- D-0001 assumes that requesting a Python IDE and a JavaScript IDE means one
  IDE understanding both languages, not two editor processes. If that reading
  is wrong, section 4 of D-0001 needs rework.

External state:

- Unchanged. No images built, pushed, or pulled this session.

Uncommitted changes:

- Everything above is uncommitted, on top of the pre-existing uncommitted
  `docker4ides` to `devcapsule` rename churn.

Open decisions referenced by D-0001 but not yet written:

- D-0002 agent autonomy inside the capsule.
- D-0003 Gemini CLI as the default agent capability. The redistribution
  rationale currently survives only in chat history and should be recorded.
- A later decision may consider curated internal use or import compatibility
  for devcontainer Features; D-0001 now rejects them as the project-facing
  capability format.

Loose ends:

- D-0001 remains proposed until the host-backed state specification confirms
  its state model and the human adopts it.
- Because D-0001 reinterprets implemented requirement R-IDE-CONFIG-001, the
  corresponding proposed requirement record still needs to be added.

Implementation checkpoint, 2026-07-22:

- The first PyCharm dogfood slice is implemented. The launcher now mounts
  persistent home at `/home/devcapsule`, separates PyCharm config, plugins,
  system, logs, and tool cache, and maps the existing dogfood directory roots
  into those component locations.
- Added top-level `devcapsule run-image IMAGE` with explicit
  `--docker-daemon host-socket` and `--development-sudo`; it uses
  `--pull=never` so this expert path cannot silently fetch a missing image.
- The full Nox build gate passes with 60 tests, mypy, source smoke tests, PEX
  build, and PEX smoke tests. The local image label was confirmed as
  `devcapsule.configuration=pycharm`.
- Manual GUI validation must run on the host because the host directory names
  supplied by the current dogfood command are intentionally not visible inside
  this capsule. Use the command in `devcapsule/README.md`.

Manual validation checkpoint, 2026-07-23:

- The user confirmed that the updated codebase successfully built
  `mycodespace.ai/pycharm:debug-v018`. Image construction for this dogfood slice
  is therefore validated.
- The user then launched `debug-v018` through `run-image` with the existing
  dogfood state directories and confirmed the dogfood slice is validated.
  Inspection from the running capsule confirmed that the existing dogfood host home is
  mounted at `/home/devcapsule`, the intended checkout is mounted as the
  project, existing agent state is active from the persistent home, Docker and
  passwordless development sudo are available after being explicitly
  requested, and PyCharm remains foreground-attached beneath PID 1 so its exit
  owns the container lifecycle.
- The narrow PyCharm persistence implementation supporting D-0001 is therefore
  manually validated. No additional automated gate was run for this
  documentation-only checkpoint; the implementation's full Nox build gate had
  already passed with 60 tests.
- Docker-daemon inspection of the live container confirmed `AutoRemove=true`,
  no restart policy, an unprivileged `1000:1000` container user, the expected
  persistent-home and nested component mounts, explicit Docker-socket and sudo
  group exposure, and `tini` supervising the foreground PyCharm process.
  Inspection also found `NetworkMode=host`. The current PyCharm launcher
  hard-codes this legacy relaxation even though the `run-image` invocation did
  not authorize it explicitly. This does not reopen the narrow persistence
  result. D-0001 now settles the required behavior, and the implementation fix
  is tracked in the dedicated ambient-host-network bug.
- PyCharm prompted for JetBrains Account login, license validation, and terms
  acceptance on the first `debug-v018` dogfood launch. Inspection found that
  the expected state was not missing: the persistent config contains the
  pre-existing JetBrains account token, KeePass database, license trace, and
  PyCharm key files, while persistent home contains earlier JetBrains consent
  and Java preference records. The IDE log specifically reports that login is
  required to continue using the JetBrains Account license. The image also has
  a newly generated `/etc/machine-id` and no desktop keyring/session bus.
  Therefore persistence of the known files is validated, but uninterrupted
  reuse of third-party authentication and licensing is not. A changed machine
  identity, unusable password-store secret, expired server-side session, or
  changed JetBrains terms may legitimately require reauthentication. Do not
  persist the host machine identity or promise login continuity until this is
  tested across another launch and checked against JetBrains licensing and
  credential-storage behavior.
- On two subsequent restarts, the user confirmed that Help -> About continued
  to show the retained license token, but PyCharm prompted for the JetBrains
  User License Agreement every time. Inspection confirmed that the persistent
  home contains JetBrains's `consentOptions`, `PrivacyPolicy`, and Java user
  preference trees. However, the PyCharm 2026.1
  `noncommerciallicense/prefs.xml` remains an empty preference map after
  acceptance, while `/etc/machine-id` remains container-local. This separates
  durable license-token persistence from agreement acceptance. The user
  classified the repeated prompt as annoying but survivable, so it is now a
  documented PyCharm limitation on the backlog rather than a blocker for the
  state-model review. Do not mount the host machine identity as a workaround.
- Follow-up dogfood use exposed a project-path migration regression:
  `run-image` did launch PyCharm through Docker, but it did not expose
  `--project-mount` and therefore selected a newly generated container path.
  Adopted PyCharm state still refers to
  `/workspace/301e4208ef81-ChatGPT_Codex`, including the saved project virtual
  environment. The expert command now accepts an explicit project mount, and
  the dogfood migration command preserves that established path.
- Both PyCharm launch paths generated an `/etc/passwd` entry whose home remained
  `/ide-global-settings/home` after the persistence migration. That stale
  account home caused Java preferences, IDE filesystem probes, and apparently
  JetBrains license state lookup to target an unmounted directory. The shared
  launcher now declares `/home/devcapsule`, matching `HOME` and the persistent
  home mount. Restart validation indicates this also restores license
  continuity; the full pytest suite passes with 61 tests.

Engineering cleanup checkpoint, 2026-07-28:

- The task-0 test and coverage foundation is complete. Normal pytest runs now
  measure statement and branch coverage across the `devcapsule` source package;
  the establishing run passed all 62 tests at 76% total coverage.
- GitHub Actions runs the test suite automatically for `main`, supports manual
  branch/tag/commit runs, and coalesces rapid pushes through cancellation plus
  a short debounce window. Coverage is published in the job summary and as XML
  and HTML workflow artifacts.
- The repository welcome page now shows GitHub-native test status and a
  repository-owned coverage SVG. After a successful `main` run, a separate
  least-privilege job regenerates that SVG locally from `coverage.xml` and
  commits it only when its value changes. The user confirmed the workflow,
  tests, and both badges work on GitHub.
- This closes the initial basic-engineering cleanup slice. The active
  implementation task returns to the shared runtime-options cleanup below.

Current task:

- On 2026-07-29, the first Python-runtime package slice was implemented as
  `devcapsule_runtime`. It provides a strict version-1 JSON runtime-plan
  contract, generic persistent-home/XDG/state-slot planning, conservative
  graphics defaults, a `gosu` privilege-drop command boundary, a parameterized
  JetBrains adapter, and a thin entrypoint that writes the product properties
  file and execs the foreground IDE process. The adapter does not embed a
  PyCharm installation or launcher default; those values and the state-slot
  mapping come from the runtime plan. The package is exposed as the
  `devcapsule-runtime` console script.
- Automated coverage now includes `devcapsule_runtime`, and the Nox compile and
  mypy scopes include it. Contract validation, generic filesystem planning,
  JetBrains property/command generation, graphics overrides, privilege-drop
  planning, and the final property-write/exec boundary are tested. The full
  `cd devcapsule && .venv/bin/python -m nox -s build` gate passed with 73
  tests, type checking, source smoke tests, PEX construction, and PEX smoke
  tests.
- This is only the entrypoint/package foundation. The next implementation
  slice remains the JetBrains-free redistributable base image plus the lock
  delivery fields, vendor notice, direct pinned download and digest failure
  handling, and deterministic workstation-local PyCharm materialization.

- On 2026-07-29, the user prioritized image formation ahead of the reopened
  network and Docker-option parity work. The active next slice replaces the
  `mycodespace.ai/pycharm:debug-v018` local-image bridge with a distributable
  base containing a generic tested Python runtime entrypoint plus a
  workstation-local, checksum-verified PyCharm materialization downloaded
  directly from JetBrains. The detailed architecture, licensing notice,
  delivery policies, and dogfood closure criteria are recorded in
  `devcapsule/implementation-notes/2026-07-29-local-pycharm-materialization-and-python-entrypoint.md`.
- The published/base image must contain no JetBrains binaries. The final local
  image uses a parameterized JetBrains adapter, leaves EULA acceptance and
  licensing to the user, and must reproduce or improve the validated dogfood
  behavior. The generic runtime contract should accommodate later shared
  Docker/network work without pulling all option-parity work into this slice.

- On 2026-07-26, the user confirmed that the capability-first dogfood path
  launches this checkout successfully through `devcapsule run`. This manually
  validates the manifest, platform lock, developer-owned checkout and adopted
  state, generated resolution, project mount, and foreground IDE path as an
  integrated workflow. The manual test is not fully closed: the current
  PyCharm launcher still contains the temporary ambient host-network
  workaround, so bridge-by-default and the negative Docker/sudo authorization
  checks remain outstanding.

- On 2026-07-25, the PyCharm ambient-host-network bug was reopened and widened
  to cover `run-image` Docker-option parity. Removing the ambient default also
  removed the explicit host-network behavior required by dogfood, so the user
  temporarily restored the legacy launcher argument. `run-image` also lacks
  the previous PyCharm surface for a custom Docker socket, Docker-in-Docker,
  native debugging, writable root, and raw Docker arguments. Keep the bug open
  until a shared runtime-options model restores explicit `--network host` and
  the accepted expert Docker controls without making host networking ambient.
  Capability-first dogfood validation waits on that correction.
- On 2026-07-24, the first executable capability-first dogfood slice was
  implemented. Top-level `init`, `lock`, `state adopt`, `config resolve`, and
  `run` now create and consume the adopted manifest, platform-lock,
  developer-owned checkout, generated-resolution, and state-slot shapes. The
  repository now carries its own `.devcapsule/devcapsule.toml` and
  `devcapsule.linux-amd64.lock`, selecting the already validated local
  `mycodespace.ai/pycharm:debug-v018` image. PyCharm no longer receives ambient
  `--network=host`; bridge networking is the default. Automated tests cover
  the complete configuration-to-Docker-plan path.
- This first lock implementation deliberately accepts an existing local image
  tag. Immutable image digest capture, the general curated capability matrix,
  workstation configuration overlays, persistent host-choice commands, and
  manual host GUI validation of `devcapsule run` remain open.

- On 2026-07-23, Costin Cozianu adopted D-0001 after final review of the
  capability-first CLI and supporting state specification. The adopted model
  uses committed manifests and platform locks, developer-owned checkout input,
  generated local resolution, explicit host authorization, and a broad expert
  `run-image` escape hatch. R-IDE-CONFIG-001 now records the capability-first
  target; the existing configuration-first commands are transitional.
- D-0001 final review has settled `run-image` as the legacy, compatibility,
  dogfood, and recovery escape hatch. It may use discovered
  `.devcapsule/devcapsule.toml` values, command-line values take precedence as
  run-once choices, and missing required effective values cause an actionable
  failure. It never reads the lock or turns committed recommendations into
  host authorization.
- D-0001 final review has also settled initialization safety: `devcapsule init`
  is create-only and fails without modifying files when a project is already
  initialized. It never silently merges or overwrites an existing declaration.
- D-0001 final review has settled lock platform scope. Generated locks are
  committed as `.devcapsule/devcapsule.<platform-alias>.lock`, initially
  `devcapsule.linux-amd64.lock`. `devcapsule lock` generates only for its
  execution platform; cross-target lock generation and cross-platform IDE
  execution are outside V1 scope.
- D-0001 final review has settled manifest versioning. The required top-level
  key is `devcapsule-schema-version = 1`; missing or unsupported versions fail
  explicitly, compatible additions retain the version, and breaking schema
  changes increment it. Locks use an independent format version.
- D-0001 final review has settled developer-owned checkout input and generated
  resolution. The default checkout uses `devcapsule.checkout.toml` plus
  `devcapsule.resolved.toml` beneath its XDG project-identity directory and
  needs no checkout name; additional checkouts use named pairs. Generated
  locks and resolved files carry SHA-256 digests over schema-validated RFC 8785
  canonical JSON. Stale artifacts fail with regeneration instructions, while
  `devcapsule run --force` may use them once without rewriting or bypassing
  workstation policy.
- D-0001 final review has settled expert Docker control. `run-image` permits
  broad explicit mount and Docker-specific choices, performs structural and
  conflict validation, and warns rather than enforcing a broad forbidden list;
  restrictive workstation policy remains the upper boundary. The existing
  implicit PyCharm host network is tracked separately as
  `devcapsule/implementation-notes/bugs/2026-07-23-pycharm-ambient-host-network.md`.

1. Fix the reopened PyCharm `run-image` network and Docker-option parity bug,
   beginning with explicit `--network host` support required for dogfood and a
   shared runtime-options model for the accepted expert Docker controls.
   Preserve bridge networking as the default and remove the temporary ambient
   host-network workaround. Then manually validate the first capability-first
   dogfood launch on the host:
   adopt the six existing PyCharm state directories, resolve local checkout
   configuration, and launch `mycodespace.ai/pycharm:debug-v018` with
   `devcapsule run --docker-daemon host-socket --development-sudo`. Inspect the
   resulting container to confirm the existing project mount and state, bridge
   network, Docker access, sudo, foreground lifecycle, and IDE usability.
   Follow
   `devcapsule/implementation-notes/2026-07-24-capability-first-dogfood-manual-test.md`.

2. Address the shared run-option parity gap recorded in
   `devcapsule/implementation-notes/bugs/2026-07-13-codium-run-option-parity.md`,
   beginning with a shared runtime-options model rather than copying PyCharm
   flags into the Codium launcher.
   Requirements: `devcapsule/REQUIREMENTS.md` R-PYTHON-MVP-003,
   R-FRAMEWORK-001, R-SCOPE-001, R-DOCKER-001.
   Verification: add shared option-planning tests, retain explicit isolation
   boundaries, run `cd devcapsule && python -m nox -s build`, and manually
   validate security-sensitive profiles.

3. Add a sensible shared extended-logging option for configuration `run`
   subcommands. It should print a sanitized runtime/Docker plan, enable
   configuration-specific verbose IDE logging, keep the foreground process
   attached, preserve actionable failure evidence, and never expose Git,
   agent, or other credential values.
   Requirements: `devcapsule/REQUIREMENTS.md` R-FRAMEWORK-001,
   R-PYTHON-MVP-003, R-SCOPE-001.
   Verification: cover PyCharm and Codium command planning, credential
   redaction, source and PEX help surfaces, and at least one manual failing IDE
   startup that leaves useful diagnostics.

4. Claim and prepare the Docker Hub publication namespace for V1 release
   images, then validate a real push/pull path for user-facing prebuilt
   images.
   Notes: `devcapsule/implementation-notes/2026-07-15-docker-hub-namespace-and-publication-plan.md`
   Requirements: root `R-PRODUCT-001`, root `R-DOCS-002`,
   `devcapsule/REQUIREMENTS.md` R-PYTHON-MVP-002 and R-DOCS-002.
   Verification: confirm the chosen Docker Hub namespace exists under the
   intended account/organization, document the repository naming scheme, push
   at least one release-candidate image, and verify a clean pull from that
   namespace.

Next task:

1. Implement the local PyCharm materialization and Python-entrypoint task in
   `devcapsule/implementation-notes/2026-07-29-local-pycharm-materialization-and-python-entrypoint.md`.
   Finish by building a JetBrains-free redistributable base, downloading and
   verifying the lock-pinned current PyCharm artifact on the workstation,
   materializing the final image locally, passing the full Nox gate, and
   manually running the existing dogfood environment successfully through
   `devcapsule run`.
2. Resume the reopened PyCharm network and Docker-option parity work after the
   new materialized-image dogfood path is established.

Standing rule:

1. Keep any isolation relaxation explicit and documented.
   Requirements: `devcapsule/REQUIREMENTS.md` R-SCOPE-001, R-DOCKER-001 and
   root R-PRODUCT-002.
   Reopen if: a change adds host access, credentials, networking, devices, or
   filesystem mounts without matching documentation.
