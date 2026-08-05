# Current Status

This file is the project handoff point. Future agents should update it when
completing a stage, changing the project state materially, or ending a session.

Current stage: `docker4pycharm` v0/MVP checkpoint complete; `devcapsule`
Python MVP is the active post-MVP refactoring stage.

Current status:

- The canonical public source repository is now
  `https://github.com/ccozianu/devcapsule`. GitHub redirects the former
  `ccozianu/ChatGpt_Codex` name, but current source links, dogfood clone
  defaults, checkout `origin`, and newly built artifact metadata use the
  canonical name directly. Historical/current workspace mount paths retaining
  `ChatGPT_Codex` remain literal filesystem paths rather than repository URLs.
  Live HTTPS checks confirmed the renamed repository and a known commit return
  HTTP 200; the full dirty-tree Nox gate rebuilt the local PEX with
  `https://github.com/ccozianu/devcapsule` as its source repository and passed
  128 fast tests, clean mypy, command smokes, and three packaging integrations.
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
  `vscode_with_claude` placeholder remains separate and is explicitly marked
  WIP in its user-facing command help.

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
  paths. D-0005 later supersedes the ambient Gemini portion of this historical
  checkpoint.

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
  persistent Gemini state root is required. D-0005 later removes this
  agent-specific ambient host mount from active launchers; optional components
  must use persistent home or declared state.

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
- The former D-0003 Gemini-default reservation is retired by accepted D-0005,
  which makes the base agent-neutral and agent CLIs optional components.
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

- D-0004, `Configuration Resolution And Guided Run Experience`, is now a
  proposed decision record preserving the current product-design discussion.
  Its working direction keeps V1 CLI/TOML configuration iterative, uses
  `project config resolve` as the explicit completion and validation boundary,
  treats state and secrets as typed configuration with distinct safety
  semantics, and makes a browser-based guided `project run` the V2 direction.
  It records fourteen unanswered questions, including state-command migration,
  secret providers, vendor acknowledgement, progress and inspection UX, local
  alternatives, client installation, workflow bootstrap, and local-web-app
  security. The record remains `proposed`; only the human may adopt it after
  review.
- D-0004 now proposes `devcapsule project [--path PATH] SUBCOMMAND` as the V1
  project/checkout command subtree. `list`, `init`, checkout registration,
  `config`, `state`, `lock`, and `run` share this mental model. Omitted `--path`
  discovers the nearest `.devcapsule/devcapsule.toml` upward from the current
  directory; an explicit path may be the root or a descendant. The ambiguous
  positional `project . SUBCOMMAND` form is excluded. If D-0004 is adopted,
  `project run` deliberately supersedes D-0001's top-level `run` spelling and
  `project run-image IMAGE` becomes the lock-independent expert escape hatch.
  The transitional top-level project commands are removed without aliases.
- `devcapsule project list` reads valid developer-owned checkout records only
  from `$XDG_CONFIG_HOME/devcapsule/projects/`, normally
  `~/.config/devcapsule/projects/`. It does not scan source trees. A clone or
  `project init` is not registered until initializing `project config list` or
  the first persistent `project config set|bind|authorize|resolve` operation
  creates its checkout record. Missing checkout paths remain visible for
  deliberate cleanup.
- The specified project command tree is now implemented. Top-level `init`,
  `lock`, `config`, `state`, `run`, and `run-image` modules were removed without
  aliases. `project --path PATH` supplies one lazy shared context to `init`,
  checkout registration, `config resolve`, `state adopt`, `lock`, `run`, and
  `run-image`; omitted paths use current-directory discovery where a
  declaration is required. `project run-image` also accepts a plain source
  directory without a declaration. The first `project config resolve` creates
  a safe default checkout record, while `project checkout register NAME`
  creates a distinct named record when the portable project identity already
  belongs to another canonical checkout.
- `project list` now enumerates the XDG registry without scanning source trees
  and reports `ready`, `missing`, or `uninitialized`. Focused tests cover clean
  registration, upward discovery, named second-checkout selection, missing
  paths, lack of source scanning, expert `run-image`, and rejection of the old
  top-level commands. The full Nox build gate passed with clean mypy over 57
  source files, 95 fast tests at 79% coverage, source and rebuilt-PEX help
  smokes for the project tree, PEX construction, and the PEX integration test.
  No host container was launched for this CLI-only refactor.
- D-0004 review has now settled the conceptual V1 configuration loop: a clean
  checkout performs zero or more typed `project config set`, `bind`, and
  `authorize` operations, each with immediate value/provider validation,
  followed by holistic `project config resolve` and then `project run`.
  Persistent operations write the developer-owned `devcapsule.checkout.toml`
  under the XDG project-identity directory and must show the actual path
  written.
- `set` is for ordinary values such as a checkout memory limit; `bind` maps a
  declared logical resource to a developer-owned provider; and `authorize`
  records security-sensitive host decisions such as Docker-daemon access,
  host networking, or development sudo. The next clean-clone dogfood milestone
  deliberately supports only existing-host-directory bindings for component
  state. Secret, host-file, socket, profile, and alternative-storage providers
  remain later contract work, while devices, Docker, networking, privilege,
  and port publication remain authorization rather than generic binding.
- At that checkpoint, the next implementation was grounded by an executable,
  intentionally not-yet-passing manual user test (retired on 2026-08-05 after
  manual acceptance). On the dogfood laptop it cloned the repository to
  `~/work/provisional/costin3/myProjects/devcapsule`, registers the distinct
  `costin3-devcapsule` checkout, preserves the existing default checkout
  record, applies an 8 GiB memory setting, binds shared home/config/plugins and
  new checkout-specific PyCharm system/log/cache directories, persists the
  observed Docker/network/sudo authorizations, resolves, inspects the live
  container plan, and launches twice for persistence validation. It now treats
  `devcapsule-local-pycharm:debug-v020` as an explicit prerequisite and verifies
  its embedded PEX, runtime plan, materialization labels, and generic Python
  entrypoint before launching.
- Inspection of running container `322ca969a6d9` established the grounding
  values: image `mycodespace.ai/pycharm:debug-v018`, unprivileged `1000:1000`,
  project destination `/workspace/301e4208ef81-ChatGPT_Codex`, explicit host
  Docker and development sudo, six legacy state mounts, foreground auto-remove
  lifecycle, and the known temporary host-network relaxation. X11, generated
  account files, Docker group IDs, and the selected NVIDIA runtime are launcher
  outputs rather than developer configuration values.
- `debug-v018` is sufficient as the known-good legacy comparison but not as the
  image under test for the next slice: it is a 5.54 GB monolithic image whose
  OCI entrypoint is still `/usr/local/bin/entrypoint.sh`, with no embedded PEX
  or runtime-plan command. The v020 checkpoint is allowed to evolve the
  container runtime contract for dynamic checkout configuration, explicit
  development sudo, and the new launch plan before the final content-addressed
  `devcapsule-local-pycharm:<materialization-identity>` naming becomes the V1
  user-facing realization model.
- D-0004 now locks the advertised canonical local-image pattern as
  `devcapsule-local-<component>:<materialization-identity>`. Project identity is
  intentionally absent so identical immutable formation inputs can be reused
  without sharing project configuration or state. The proposed developer CLI
  separates `devcapsule images build --type base` for a JetBrains-free runtime
  base from project-aware
  `devcapsule images build --type environment --project PATH` for combining a
  locked component with either its locked base or an explicit local/registry
  base. Optional aliases such as `devcapsule-local-pycharm:debug-v020` are
  conspicuous local debugging names, never the canonical reproducible identity.
- Cross-project image reuse is now specified as automatic content-addressed
  sharing. Each project lock selects a normalized formation descriptor rather
  than owning an image; platform, immutable base identity, all component
  identities/digests, materialization recipe parameters, and the generic
  runtime-template contract determine its RFC 8785/SHA-256 identity. Project
  and lock-file identities, checkout paths, resolution, mounts, UID/GID, state,
  credentials, authorization, and aliases are excluded. A matching canonical
  local image is reused only after full metadata verification; conflicts fail
  rather than being silently used or overwritten. Checkout-specific launch
  plans are supplied outside the shared image at `project run`. The current
  materialization primitive is narrower: it hashes a simple base/artifact list,
  bakes a runtime plan, and trusts `image_exists`. Implementing `--type
  environment` must replace that shortcut with the specified descriptor,
  metadata verification, and external checkout launch plan.
- The advertised `devcapsule images build --type base` contract is now
  explicit. It produces
  one reusable, JetBrains-free OCI development-runtime image: Ubuntu 24.04,
  Python 3.12, compiler/debug/network/process tooling, Docker client/buildx/
  Compose/daemon binaries, GUI runtime libraries, `tini`, `gosu`, non-authorized
  sudo, the recipe-selected Node/npm baseline, and one digest-labelled
  DevCapsule PEX. Its OCI command invokes `devcapsule.pex runtime` with the
  materialization-owned plan path. The base contains no runtime plan, IDE,
  project, personal state, credentials, host authorization, or vendor license
  acceptance and therefore is not a runnable project environment by itself.
- V1 DevCapsule images are identified authoritatively by
  `devcapsule.image.managed=true`, `devcapsule.metadata.version=1`, and
  `devcapsule.image.kind=base|materialized` labels. `devcapsule images list`
  reads only the local Docker store, deduplicates aliases by image ID, and does
  not infer ownership from repository/tag prefixes. Unknown or malformed
  metadata remains visible, while old `devcapsule.configuration` images require
  `--include-legacy`. Labels classify rather than establish trust; lock and
  formation identities are still verified before reuse.
- The proposed `images build` commands no longer expose a `--pull` policy.
  They use the selected base from the local Docker store when present and
  otherwise obtain its registry reference. This removes a low-value option
  while retaining immutable-identity reporting and digest-pin protection.
- The first `images` implementation slice is complete. `devcapsule images
  list [--include-legacy]` reads the local Docker store, selects V1 images by
  the managed/version/kind label contract, keeps unknown or malformed managed
  metadata visible, groups tags by image ID, and optionally shows transitional
  `devcapsule.configuration` images. Live source and built-PEX checks hide the
  legacy v018 image by default and show it correctly with `--include-legacy`.
- `devcapsule images build --type base --tag IMAGE` now builds through the
  Python-owned base planner. It supports `--from`, `--pex`, and
  `--source-revision`; a running PEX embeds itself by default, while source or
  editable execution requires an explicit PEX. Bases now receive managed,
  metadata-version, kind, canonical-name, recipe, PEX-digest, and source labels.
  Materialized PyCharm planning was aligned with the same metadata contract and
  records formation, base, component, artifact, and canonical-name identities.
- Validation on 2026-08-01 passed the full
  `cd devcapsule && .venv/bin/python -m nox -s build` gate: compilation and
  shell syntax checks, clean mypy over 62 source files, 87 fast tests at 79%
  statement/branch coverage, source and built-PEX command smoke tests, PEX
  construction, and the PEX integration test. The actual large base image has
  not yet been built; that host build is the next minimal manual validation
  before proceeding to `--type environment`.
- `devcapsule images build` now accepts
  `--network [default|host|none]`. The selected mode is forwarded through the
  base builder to Docker buildx; `host` follows the existing explicit path that
  also grants BuildKit's `network.host` entitlement. This affects build-time
  networking only and does not authorize host networking for runtime
  containers. Focused tests, clean mypy, 88 fast tests, the full Nox build
  gate, and the rebuilt PEX help surface all passed after the change.
- `devcapsule images build --type base` now exposes two curated recipes through
  `--recipe`. `ubuntu-24.04` is the ready default and retains the existing
  Ubuntu 24.04 developer-tooling plan. `nvidia-cuda-devel` is a WIP recipe that
  starts from `nvidia/cuda:12.8.1-devel-ubuntu24.04`, installs the same
  developer baseline, records NVIDIA/CUDA/WIP labels, and emits a warning. Its
  specialized host validation is a V1 release blocker recorded in
  `devcapsule/implementation-notes/2026-08-01-nvidia-cuda-base-recipe-validation.md`.
  NVIDIA CUDA E2E is available on the maintainer's laptops, but this container
  session has no GPU access. AMD ROCm and other GPU families require an
  interested partner or cloud test infrastructure and remain outside required
  V1 scope. GPU image formation remains separate from explicit runtime device
  authorization. The CUDA registry tag was confirmed to publish amd64 and
  arm64 manifests. Focused tests passed, followed by the full Nox build gate:
  clean mypy across 62 source files, 92 fast tests at 79% coverage, source and
  rebuilt-PEX command smokes, PEX construction, and the PEX integration test.
  No real base image or GPU workload was run in this container session.
- The user subsequently reported that the first external NVIDIA recipe test
  succeeded: `images build --type base --recipe nvidia-cuda-devel` produced a
  local NVIDIA GPU base image on an NVIDIA laptop. The exact image inspection,
  `nvcc`, positive/negative device authorization, CUDA workload, and
  materialized-environment checks remain open in the V1-blocking specialized
  validation task.
- The obsolete top-level `build-base` compatibility command was removed.
  `devcapsule images build --type base` is now the sole base-build command and
  no compatibility layer is promised. The full Nox build gate passed after
  removal with clean mypy over 61 source files, 92 fast tests, source and
  rebuilt-PEX command smokes, PEX construction, and the PEX integration test;
  neither help surface advertises `build-base`.
- Research also confirmed an optional low-administration NVIDIA CI path:
  GitHub-hosted Linux GPU larger runners provide one Tesla T4 and can run CUDA
  Docker job containers with `--gpus all`, as demonstrated by LightGBM's
  current workflow. The runner costs $0.052/minute, but requires a GitHub Team
  or Enterprise Cloud organization and is billed even for public repositories.
- At the user's explicit request, the development ritual now supports durable
  session records under `implementation-notes/session-records/`. Recording is
  opt-in only; detailed sanitized reconstruction is the default, summaries are
  available on request, and `verbatim` requires a user/IDE-supplied export.
  Session records supplement rather than replace decisions, requirements,
  current status, bugs, and user docs. This session is preserved at
  `devcapsule/implementation-notes/session-records/2026-08-01-d-0004-configuration-and-images-cli.md`.
- `devcapsule images build --type environment` is now implemented. It requires
  a fresh project resolution, parses the lock-selected base and PyCharm
  formation inputs, validates the selected image as a managed metadata-v1 base
  for the locked platform, and obtains a missing registry reference without
  launching a container. `--base` remains an explicit developer override and
  `--alias` adds only a secondary local tag.
- Materialization now hashes a versioned canonical formation descriptor that
  includes platform, immutable inspected base ID, exact PyCharm component and
  artifact digest, recipe parameters, and the generic runtime-template and
  entrypoint contracts. The full digest is the reuse authority. Existing
  canonical tags are reused only after their descriptor is parsed,
  canonicalized, re-hashed, and matched against the base, recipe, and complete
  component metadata; malformed or conflicting tags fail instead of being
  overwritten.
- Artifact acquisition and each formation identity use filesystem locks under
  the XDG DevCapsule cache. The verified archive remains checksum-addressed;
  extraction and the large Docker build context live in cache-backed temporary
  directories rather than the system `/tmp`, and are removed after the build.
  The shared image embeds a generic component template but deliberately omits
  the checkout-specific `/etc/devcapsule/runtime-plan.json`.
- On 2026-08-02, the user successfully pushed dogfood base tag
  `docker.io/mycodespaceai/devcapsule-base:ubuntu-24.04-v019`. Docker Hub
  assigned digest
  `sha256:637f646a9de962cb399025c2bf3817b08e242d2a4416b49a202cf06763852feb`,
  which resolves to the validated local image ID
  `sha256:7e81e49d7b9c3a82faae8af4de4e3eed927f13261d8f0040af0aa23f64963dee`.
  The committed Linux dogfood lock now uses that globally resolvable digest
  reference plus PyCharm Professional 2026.2.0.1 and the vendor-published
  artifact SHA-256. The v019 tag remains a dogfood checkpoint, not an official
  V1 release version. An isolated `project config resolve` followed by the
  rebuilt PEX `images build --type environment` resolved the committed digest
  to the same immutable base and strictly reused the existing canonical
  PyCharm environment without downloading, rebuilding, or launching. A direct
  digest pull also succeeded from this credential-isolated capsule, confirming
  anonymous registry access and digest resolution; a genuinely clean Docker
  store pull remains part of release-candidate validation.
- Real PEX validation downloaded and verified the 1.28 GB JetBrains archive,
  built canonical environment
  `devcapsule-local-pycharm:d3240f8fbbb362a0d298` with full formation identity
  `d3240f8fbbb362a0d2985299ef13f3289340c8dc23218c470d3de16adc4a05b2`,
  and added alias `devcapsule-local-pycharm:debug-v019`. Inspection confirmed
  the generic PEX entrypoint/CMD, PyCharm launcher, component template, absent
  checkout runtime plan, labels, descriptor, base identity, and identical
  canonical/alias image ID. A second invocation strictly reused the image in
  under one second without downloading or rebuilding. No IDE container was
  launched.
- Final validation passed the full Nox build gate: compilation and shell
  syntax checks, clean mypy over 57 source files, 104 fast tests at 79%
  statement/branch coverage, source and rebuilt-PEX command smokes, PEX
  construction, and the PEX integration test. The explicit Docker E2E also
  passed after the formation changes, in addition to the real vendor-image
  build and inspection above.
- On 2026-08-02, the user selected two expedient V1 base-trust paths. A
  developer may build and explicitly select a managed base, or may record
  developer-owned authorization for one exact published digest recommended by
  the project after reviewing its checksum and basic security scan. The lock
  cannot authorize itself; mutable tags and blanket publisher/repository trust
  are excluded. Verifiable provenance, signed SBOMs, artifact signatures,
  attestations, automated scan/policy evaluation, and client-side evidence
  verification are an explicit V2 task rather than V1 blockers.
- V1 user documentation now discloses the default base in plain language:
  Ubuntu 24.04 plus Python/native development and debugging tools, Git/SSH,
  diagnostics, Docker tooling, GUI runtime libraries, non-authorized
  Docker/sudo capabilities, pinned Node.js/npm tooling, and the embedded
  DevCapsule PEX. It links directly to the repository-owned Python recipe,
  exact apt-package tuple, pinned public-tool installer, build-context renderer,
  and generic runtime, and separately states what materialization and runtime
  authorization add. This documentation-only checkpoint required no new test
  run; all links and `git diff --check` were validated.
- On 2026-08-02, accepted D-0005 replaced D-0001's ambient Gemini assumption
  with an agent-neutral base and explicit optional agent components. Active
  base, PyCharm, and Codium build plans now retain verified Node.js/npm but do
  not install Gemini CLI; shared runtime planning no longer creates or directly
  mounts host `~/.gemini`; and this dogfood manifest no longer requests a
  `gemini` capability. User docs explain that agent CLIs have independent
  release, licensing, authentication, state, and trust lifecycles. The current
  then-published v019 digest still contained Gemini and required replacement
  before the committed dogfood lock could satisfy D-0005; the v020 publication
  recorded below closes that replacement. Antigravity remains a later optional
  V1 component task; no
  Antigravity artifact was downloaded or installed in this slice. Focused
  agent-neutral build/launcher tests passed, followed by the full Nox gate:
  clean mypy over 57 source files, 104 fast tests at 79% coverage, source and
  rebuilt-PEX command smokes, PEX construction, and the PEX integration test.
  A replacement base image was not built or published in this capsule.
- On 2026-08-02, component persistence was moved behind a generic declared
  interface rather than shared runtime fields. The versioned component
  template now declares persistent-home and home-relative XDG use plus any
  exceptional component-local slots, including lifecycle, sensitivity, scope,
  storage, concurrency, ownership/permissions, deletion, reconstruction, and
  explicit home-overlay semantics. Generic planning namespaces those slots,
  allocates directory storage beneath the matching XDG data/state/cache root,
  honors developer-owned adopted bindings, orders home before overlays, and
  produces the component-neutral in-container runtime plan. PyCharm owns its
  config, plugins, system, log, and cache declarations; its JetBrains adapter
  maps local slot names to IDE properties. Shared runtime code has no Gemini,
  Antigravity, PyCharm, or other tool-named state option. A component using
  only standard `HOME`/XDG locations declares zero custom slots.
- This persistence-interface change alters the hashed component template, so
  the prior canonical PyCharm environment remains an accurate old formation
  but is not reusable for the new formation identity; the next environment
  build will create a new canonical local image. The full Nox build gate
  passed: compilation and shell checks, clean mypy over 61 source files, 113
  fast tests at 79% coverage, source and rebuilt-PEX command smokes, PEX
  construction, and the built-PEX integration test. Docker E2E and a real
  environment rebuild were not run for this contract-only formation change.
- On 2026-08-02, V1 public source traceability was implemented before the v020
  dogfood build. PEX packaging now creates an isolated source staging tree and
  embeds a versioned build-information record containing the package version,
  normalized public repository, full source revision, and canonical GitHub
  commit URL. `devcapsule version --json` exposes that record without a source
  checkout. Packaging now requires clean PEX inputs, a full checkout-HEAD
  commit, an HTTPS GitHub repository, and an exact revision advertised by that
  public repository by default. `--allow-local-source` is the explicit dirty
  or unpublished development escape hatch and records an unknown revision.
- Base-image planning reads the selected PEX metadata without executing the
  artifact. `--source-revision` is now required by default, acts as an
  assertion, and a mismatch or non-public PEX fails before Docker build. The
  default base-image execution path also performs a live HTTP `HEAD` check of
  the exact embedded canonical GitHub commit URL before invoking Docker
  buildx; a missing revision or unavailable verification service fails closed.
  `--allow-local-source` explicitly permits a local unknown or unpublished
  source PEX and bypasses the live check for local-only images. The
  matching values populate `devcapsule.source.repository`, `.revision`, and
  `.url` plus OCI `org.opencontainers.image.source` and `.revision` labels.
  Successful CLI output now states whether the public GitHub check passed or
  was explicitly bypassed for local source.
  Live validation passed against a known public repository commit and rejected
  the current unpublished `da9f92a...` commit with GitHub HTTP 404. The full
  dirty-tree Nox gate passed with clean mypy over 65 files, 128 fast tests at
  80% coverage, local-PEX command smokes, and all three packaging integration
  tests; no Docker build was run by the gate.
  This closes the implementation part of the V1 disclosure task while making
  no provenance, reproducibility, signature, attestation, or SBOM claim. The
  full Nox gate passed with clean mypy over 64 files, 122 fast tests at 80%
  coverage, source and PEX command smokes, PEX construction, and two PEX
  integration tests. Strict public-revision success awaits pushing this exact
  implementation commit, after which it is the required v020 packaging path.
- The first external v020 attempt exposed a packaging-handoff gap: the full
  Nox gate had written its deliberate unknown-revision development PEX to the
  same `dist/devcapsule.pex` path later used for publication. The base builder
  correctly rejected the mismatch, but tests had not distinguished artifact
  roles. The local Nox PEX step writes and tests only
  `dist/devcapsule-local.pex` and asserts its unknown/local identity at the
  packaging boundary. `dist/devcapsule.pex` remains reserved for the strict
  public-source build. Mismatch diagnostics identify both filenames and the
  exact rebuild/inspection commands.
- The full `nox -s build` contract now combines those roles safely. It always
  builds and tests `dist/devcapsule-local.pex`. On a dirty repository it
  explicitly reports that `dist/devcapsule.pex` was not built and that any
  existing file there may be stale. On a clean repository it builds and
  smoke-tests `dist/devcapsule.pex` with the exact local `HEAD`, without
  requiring GitHub to advertise the revision yet. The dedicated
  `--allow-unpublished-revision` source policy preserves clean inputs, full
  revision identity, canonical repository metadata, and the commit URL while
  omitting only the remote revision-existence check. The standalone default
  `scripts/build-pex.sh` remains strict for publication, and `nox -s pex`
  remains deliberately local-only. Focused integration coverage proved that
  a clean synthetic commit absent from GitHub builds with its exact revision
  and canonical commit URL. The full dirty-tree gate passed with clean mypy
  over 65 files, 124 fast tests at 80% coverage, local-PEX command smokes, and
  all three packaging integration tests.
- The user published the agent-neutral recipe-v2 dogfood base as
  `docker.io/mycodespaceai/devcapsule-base:ubuntu-24.04-v020`. Its immutable
  Linux/amd64 manifest digest is
  `sha256:d1fa4a5ea1ca3f2b9408dd1347cfb4651115fc4d77ebc1f24877b32b83fadbec`;
  registry inspection confirmed the managed base labels, embedded PEX digest,
  and canonical public source revision `e414aa1...`. The committed Linux lock
  now selects that global digest directly, replacing the v019 Gemini-bearing
  bridge.
- V1 exact-base trust is now implemented. Formation locks reject local image
  IDs, daemon aliases, implicit registries, mutable tags, and malformed digest
  references; committed bases must be globally named OCI repositories pinned
  by a full SHA-256 digest. `project config authorize base-image REFERENCE`
  accepts only the current lock's exact digest, writes the decision beneath
  this checkout's XDG-owned input, and binds it to the canonical full lock
  digest. A changed lock or base is stale and requires explicit review and
  reauthorization. Normal environment materialization requires this decision
  before pulling; explicit `--base IMAGE` remains the run-once developer-owned
  path for an inspected managed local base. Resolution exposes the accepted
  exact reference without turning the committed recommendation into trust.
- The real isolated-XDG dogfood flow registered this checkout, resolved the
  lock, authorized the exact v020 digest, resolved again, and materialized the
  next canonical environment without launching a container. It built
  `devcapsule-local-pycharm:e46ad1abe76b37aa8533`, full formation identity
  `e46ad1abe76b37aa85335e5078d672b23c33a5d323efc46ef8b9d519a6ff77b9`,
  image ID
  `sha256:d6ab215ac8e0712e5474dcd2f17808554ad9d5630a595762fe49b50b3aeab0fd`,
  and alias `devcapsule-local-pycharm:debug-v020`. Inspection confirmed the
  exact v020 base config identity, PyCharm 2026.2.0.1 artifact digest, generic
  PEX entrypoint/runtime-plan command, canonical descriptor, and identical
  canonical/alias image IDs. The full Nox gate passed with clean mypy over 65
  files, 135 fast tests at 80% coverage, source/local-PEX command smokes, and
  all three packaging integration tests. A second fresh-XDG authorization and
  resolution pass strictly reused the same canonical environment in about one
  second without downloading, rebuilding, or launching.
- `devcapsule project config set NAME VALUE` now implements D-0004 ordinary
  values generically. Projects declare value metadata in `devcapsule.toml`;
  the command accepts only declared keys, validates the metadata-selected
  `string`, `integer`, `boolean`, or `memory-size` type, and writes the
  normalized value to developer-owned checkout input while preserving state
  and authorization. Runtime effects are a curated metadata catalog rather
  than arbitrary Docker arguments.
- This dogfood manifest now declares `runtime.memory-limit` with the
  `docker.memory-limit` effect. Resolution converts `8GiB` to `8589934592`,
  retains the ordinary value for inspection, and the current `project run`
  launcher forwards the resolved byte count through Docker's `--memory`
  option. The manifest-bound Linux lock digest was refreshed. Focused tests
  passed, followed by the full Nox build gate: clean mypy over 65 files, 136
  fast tests at 79% statement/branch coverage, source and rebuilt local-PEX
  command smokes including `project config set`, PEX construction, and all
  three packaging integration tests. No host container was launched;
  automatic formation and generic runtime-plan delivery from `project run`
  remain the next slice.
- `devcapsule project config bind NAME --host-directory PATH` now implements
  the first D-0004 provider generically. It derives `home` and the five
  namespaced PyCharm resources from the locked component's persistence
  metadata, rejects undeclared names and missing directories, reports the
  exact checkout file written, and warns about the read-write exposure,
  sensitivity, and exclusive concurrency contract. Checkout input records the
  provider separately from transitional state adoption; resolution revalidates
  and emits the bindings, and the current `project run` mount path consumes
  them. Set, bind, authorize, and adopt mutations preserve one another.
  The full Nox build gate passed with clean mypy over 65 files, 137 fast tests
  at 79% statement/branch coverage, source and rebuilt local-PEX command smokes
  including `project config bind`, PEX construction, and all three packaging
  integration tests. No host directory was mounted and no project container
  was launched by this validation.
- `devcapsule project config authorize NAME VALUE` now implements the agreed
  V1 catalog as one generic command: the exact lock-selected `base-image`,
  `docker-daemon host-socket`, `network host`, and `development-sudo true`.
  The lock supplies base metadata; this dogfood manifest now carries the three
  explicit host recommendations and justifications. Each checkout record binds
  the developer's decision to the exact value and relevant recommendation
  digest. Unknown values fail, and a changed recommendation becomes stale
  rather than silently retaining authority.
- Resolution keeps authorizations distinct and inspectable. The current
  `project run` path consumes Docker socket, network, and sudo decisions;
  without them it selects no host Docker, Docker bridge networking, and no
  development sudo. The PyCharm launcher now accepts an explicit network plan
  so normal project launch no longer inherits its legacy ambient host-network
  default. The full Nox build gate passed with clean mypy over 65 files, 138
  fast tests at 80% statement/branch coverage, source and rebuilt local-PEX
  command smokes for generic `config authorize`, PEX construction, and all
  three packaging integration tests. No host container was launched.
- `devcapsule project config list` now completes Stage 0 of the active dogfood
  plan as an initializing readiness view. On first use it creates the selected
  checkout's XDG project-identity directory, a valid minimal checkout input,
  and a valid unresolved generated-plan placeholder, all without overwriting
  existing choices or a resolved plan. It explicitly reports the default or
  registered checkout name and both workstation-owned file paths. A second
  checkout collision still requires `project checkout register NAME`.
- The readiness table covers declared ordinary values, persistent home and
  all five PyCharm state bindings, exact recommended authorizations, and
  unresolved/fresh/stale resolution state. Focused tests cover default and
  named initialization, mode `0600`, byte-for-byte idempotence, incomplete and
  complete configuration, explicit bindings, authorized and stale decisions,
  and fresh and stale plans. The full dirty-tree Nox gate passed with clean
  mypy over 65 files, 141 fast tests at 80% statement/branch coverage, source
  and local-PEX `project config list` help smokes, PEX construction, and all
  three packaging integration tests. No host container was launched.
- `project config authorize --all-recommended` adds an explicitly interactive
  convenience for the current authorization catalog. It previews every exact
  recommended value, justification, and recommendation digest, then uses the
  `readchar` terminal-key package and accepts only a literal lowercase `y`.
  Every other key cancels without changing checkout input, and non-interactive
  use fails without reading or writing; automation retains the exact
  `authorize NAME VALUE` form. Focused tests cover acceptance, uppercase and
  non-affirmative cancellation, preservation of an existing checkout record,
  and rejection without a terminal. The full dirty-tree Nox gate passed with
  clean mypy over 65 files, 146 fast tests at 80% statement/branch coverage,
  source and local-PEX help smokes exposing `--all-recommended`, PEX
  construction with the pinned `readchar` dependency, and all three packaging
  integration tests. No host authorization or container launch occurred.
- Stage 0 plus interactive bulk authorization was committed as `3608ffc`
  (`Add project configuration readiness workflow`). The unrelated
  `.idea/devcapsule.iml` newline-only working-tree change was deliberately
  excluded.
- Stage 1 of the active dogfood plan is implemented. A new
  host-side environment realization service consumes one loaded resolved
  project, enforces exact locked-base authorization, obtains the digest-pinned
  base only when absent, validates managed base metadata/platform/identity,
  and delegates strict canonical reuse or checksum-verified materialization to
  the existing locked formation primitives. It returns the verified canonical
  image without creating an alias, printing command UI, or launching a
  container.
- `images build --type environment` now uses that service while retaining its
  optional alias and inspection output. Formation-based `project run` uses the
  same service automatically, so it no longer requires a pre-created debug
  alias or a completed-image field in the resolution. Legacy completed-image
  locks retain their existing path. Realization failure prevents the launcher
  from being called.
- The Stage 1 full dirty-tree Nox gate passed with clean mypy over 67 files,
  155 fast tests at 80% statement/branch coverage, source and local-PEX command
  smokes, PEX construction, and all three packaging integration tests. Tests
  cover local base reuse, missing-base pull, canonical reuse/materialization,
  exact authorization, explicit override, metadata conflict, shared images
  command behavior, automatic run realization, and no launch after a
  realization error. No real image was pulled, built, or launched.
- Stage 1 was committed as `c07ae3b` (`Share project environment
  realization`). Stage 2 of the active dogfood plan is implemented.
  Formation-based `project run` now generates a version-1
  checkout runtime plan from the exact component template used by formation.
  It contains only the established in-container project destination,
  `/home/devcapsule`, host UID/GID/runtime username, component adapter and
  configuration, and the five namespaced in-container PyCharm slot
  destinations. Serialization excludes checkout paths, host state paths,
  authorization evidence, secrets, and credentials.
- The launcher writes the plan to a mode-`0644` launcher-owned temporary file,
  bind-mounts it read-only at `/etc/devcapsule/runtime-plan.json`, and tracks it
  with the existing Xauthority/passwd/group temporary files. All are removed
  after the foreground Docker process exits, Docker-plan preparation fails, or
  plan serialization fails. Formation-based runs add no command after the
  canonical image name, preserving its generic `tini -- devcapsule.pex
  runtime` OCI entrypoint and runtime-plan CMD; legacy image runs retain the
  PyCharm command override.
- The Stage 2 full dirty-tree Nox gate passed with clean mypy over 69 files,
  161 fast tests at 80% statement/branch coverage, source and local-PEX command
  smokes, PEX construction, and all three packaging integration tests. Tests
  cover canonical serialization and parsing, redaction boundaries, component
  template/formation agreement, exact slot destinations, mode `0644`, the
  read-only external mount, unchanged OCI process behavior, normal and failure
  cleanup, and the existing assertion that no checkout runtime plan is baked
  into a materialized image. No real image was pulled, built, or launched.
- Stage 3 explicit runtime effects are complete. Focused tests prove that the
  resolved 8 GiB memory value and authorized Docker daemon, host network, and
  development sudo reach the concrete Docker plan together. Negative coverage
  proves bridge networking, no Docker socket, no sudo group, a read-only root,
  dropped capabilities, and `no-new-privileges` when those authorizations are
  absent. The full dirty-tree Nox gate passed with clean mypy over 73 source
  files, 178 fast tests at 81% statement/branch coverage, source and rebuilt-
  PEX command smokes, PEX construction, and all three packaging integrations.
- Inspection from the running formation-based dogfood capsule confirmed the
  generic PEX entrypoint/runtime-plan CMD, external plan, unprivileged
  `1000:1000` identity, host networking, host Docker socket and matching group,
  persistent component mounts, foreground `tini` lifecycle, selected Codex
  state, and absence of Gemini and privileged/SYS_ADMIN relaxation. That
  already-running instance predated the 8 GiB checkout setting and initially
  reported `memory.max=max`. A live Docker update applied an 8 GiB memory and
  memory-plus-swap limit to the exact running container; Docker inspect now
  reports `8589934592` for both values, while cgroup v2 reports
  `memory.max=8589934592` and `memory.swap.max=0`. The verified fresh plan
  emits `--memory 8589934592` when the checkout value is configured. The
  project declaration remains optional until the later-V1 ordinary-value
  default contract is implemented.
  The pre-Stage-4 v021 launch showed `sudo -n true` failing even though the
  launcher claimed passwordless sudo was enabled, because the temporary
  sudoers policy had not yet been implemented. This now-closed
  misleading-success bug is tracked in
  `devcapsule/implementation-notes/bugs/2026-08-03-authorized-development-sudo-misreported.md`.
- Stage 4 authorized development sudo is implemented without rebuilding the
  v022-derived environment. The launcher creates a group-scoped mode-`0440`
  policy under a mode-`0700` temporary directory, uses the selected local image
  in a no-network, read-only, `CHOWN`-only helper invocation to make that one
  file root-owned, verifies it, mounts it read-only under `/etc/sudoers.d/`,
  and cleans both file and directory after success or failure. The enabled
  banner now follows successful policy and Docker-plan preparation.
- Focused tests cover policy content/modes, constrained ownership, positive and
  negative plans, helper failure, truthful disclosure, and cleanup. The full
  dirty-tree Nox gate passed with clean mypy over 73 source files, 182 fast
  tests at 81% statement/branch coverage, source and rebuilt-PEX smokes, PEX
  construction, and all three packaging integrations. A disposable container
  using exact v022-derived image
  `devcapsule-local-pycharm:1bae0035566680103826` passed `sudo -n true` and
  `sudo -n id -u` with the policy mounted read-only, then proved cleanup. The
  already-running authorized v022 capsule was repaired ephemerally with the
  same policy and passed both checks. The later v023 full `project run`
  completed this Stage 4 host validation as recorded below.
- Historical merge checkpoint `5401ce3506c0a8a63bfef40f4f9ef18d2b987436`
  was the selected source revision for the v021 dogfood base. It is that
  published base's embedded PEX revision and the base build's
  `--source-revision` assertion. The v021 image was built, inspected, scanned,
  and published as discovery tag `ubuntu-24.04-v021` and immutable digest
  `sha256:cd1a0e713e515234ef438c0502786353ec1678d2efd67b61a0bae6baf9fdc51e`.
  The committed Linux lock now selects that digest. Existing checkouts must
  explicitly refresh their base-image authorization and resolve again before
  launch; `config authorize --all-recommended` previews and accepts the new
  exact digest.
- External v021 dogfood exposed the first accepted V1 follow-up backlog item:
  the pinned Node.js `v22.23.1` installation exists under
  `/opt/node/current`, but `/opt/node/current/bin` is absent from runtime
  `PATH`, so `node`, `npm`, and `npx` are unusable by name. This is not a
  regression from v018, but it violates the intended usable development
  baseline. Implement generic, schema-validated component runtime-path
  metadata that participates in formation identity and is applied by the
  generic runtime; do not add a Node-specific launcher path. The reproduction,
  security constraints, verification target, and close criteria are recorded
  in
  `devcapsule/implementation-notes/bugs/2026-08-03-component-tooling-runtime-path.md`.
- The same external dogfood session exposed a second accepted V1 onboarding
  backlog item: a fresh checkout still required manual `python -m venv`,
  activation, and dependency installation before normal development. Add a
  resolved, versioned ecosystem-bootstrap adapter contract so Python, Java,
  Node.js, and later ecosystems receive distinct curated preparation and
  readiness behavior. Plans must be inspectable, idempotent, checkout-scoped,
  safe to retry, and explicitly accepted before first executing dependency or
  project-controlled code. Runtime and IDE processes should consume the
  prepared environment without manual activation. The detailed contract and
  close criteria are recorded in
  `devcapsule/implementation-notes/bugs/2026-08-03-ecosystem-aware-project-bootstrap.md`.
- The v021 PyCharm 2026.2.0.1 session also suspended JCEF Markdown preview and
  misleadingly offered to install a host AppArmor profile from inside the
  container. Research and live logs show that JetBrains maps a failed
  `unshare` probe to Ubuntu's AppArmor guidance, while this host's immediate
  denial is Docker's default seccomp profile. The offered install failed, and
  the fallback persisted `ide.browser.jcef.sandbox.enable=false`, weakening
  embedded-web isolation. The product owner accepted an intentionally
  unsandboxed JCEF browser for V1: configure it before IDE startup so preview
  works without the misleading prompt, disclose that embedded content
  inherits the IDE user's project/state and separately authorized access, and
  keep Docker's outer seccomp/AppArmor/capability boundary unchanged. Do not
  add `SYS_ADMIN`, unconfined profiles, privileged mode, or host AppArmor
  installation. Evidence, rationale, disclosure requirements, later
  sandbox-hardening direction, and close criteria are recorded in
  `devcapsule/implementation-notes/bugs/2026-08-03-jcef-sandbox-container-preview.md`.
- The accepted V1 JCEF workaround is now implemented in the PyCharm component
  contract. It supplies `ide.browser.jcef.sandbox.enable=false` through both
  generated JetBrains properties and a JVM startup option, so the setting is
  applied before JCEF probes namespaces and remains compatible with v021's
  embedded runtime. The launcher discloses that embedded content inherits the
  IDE user's project/state/network and separately authorized Docker access.
  Focused tests prove the property and startup option are present while
  `SYS_ADMIN`, privileged mode, and unconfined seccomp/AppArmor remain absent.
  The combined dirty-tree full Nox gate passed with clean Python and shell
  compilation, clean mypy over 73 source files, 171 fast tests at 80%
  statement/branch coverage, source and local-PEX command smokes, PEX
  construction, and all three packaging integrations. Fresh external
  Markdown/SVG preview and log validation remain pending.
- The Stage 4 development-sudo gap is closed. On 2026-08-05, Docker inspection
  of a fresh formation-based `project run` from exact source revision
  `a33988a24a91ef382c1c5c6265ba2a34762ba115` confirmed the mapped `1000:1000`
  user, supplementary group `44000`, writable root without privileged mode,
  and a generated read-only sudoers-policy mount. The policy was `root:root`
  mode `0440`; `sudo -n true` returned zero and `sudo -n id -u` printed `0`.
  A disposable run of the same image under the unauthorized read-only,
  capability-dropped, `no-new-privileges` profile had no policy and rejected
  noninteractive sudo. Together with the passing positive/negative plan and
  cleanup tests, Stage 4 is fully validated.
- On 2026-08-05, the product owner manually accepted the functional dogfood
  outcome after sustained satisfactory work from the second checkout in the
  private monorepo. Stage 5's laptop-specific script implementation is waived,
  and `devcapsule/tests/manual/v1-second-checkout-dogfood.sh` was removed. Its
  intended portable coverage is now a substantial later V1 task for a
  disposable multi-project E2E orchestrator.
- The Stage 6 fast-test audit found no missing mocked-test category for Stages
  1 through 4. Canonical realization, project-run handoff, runtime-plan
  redaction/delivery/cleanup, authorized and unauthorized Docker effects,
  memory propagation, and sudo preparation/failure/cleanup are covered. The
  Docker-free `nox -s tests` gate passed all 182 selected tests at 81% coverage.
  The closeout changes documentation and removes an obsolete host-only script,
  so it does not require rebuilding the PEX, v023 base, or materialized image.
- The accepted live container reported `HostConfig.Memory=0`, not 8 GiB.
  Memory defaults and live propagation are explicitly deferred to later V1:
  add ordinary-value defaults, declare `runtime.memory-limit = "8GiB"` for
  this project, preserve checkout override precedence, and inspect both Docker
  and cgroup limits in the future E2E.
- The product owner externally tagged and pushed the validated v023 base as
  `docker.io/mycodespaceai/devcapsule-base:ubuntu-24.04-v023`. Registry
  inspection and the local image's `RepoDigests` both resolve it to
  `sha256:e8ec48fa1f45f566e997735ac5e8ce8086a2512681db0e8a22696ee0801a8aa1`;
  the committed Linux dogfood lock now selects that immutable digest. Lock
  parsing and manifest-digest validation passed, as did 182 fast tests, source
  command smokes, and clean mypy over 73 source files. No PEX, base, or
  materialized-image rebuild was warranted because the validated runtime
  remains exact source revision `a33988a24a91ef382c1c5c6265ba2a34762ba115`.
- The same external run printed JetBrains Runtime's slow-X11 warning and
  automatically disabled image alpha compositing. No visual or performance
  symptom has been reported, so this is a low-priority review rather than a V1
  blocker. Keep `-Dremote.x11.workaround=auto` until a controlled comparison
  of `auto`, `true`, and `false` demonstrates a reason to override the vendor
  heuristic. The review and escalation criteria are recorded in
  `devcapsule/implementation-notes/bugs/2026-08-03-jbr-slow-x11-alpha-compositing.md`.
- PyCharm also warned that DevCapsule launches `bin/pycharm.sh` instead of the
  preferred native `bin/pycharm`. The pinned archive's `product-info.json`
  declares the native path and the executable is present; current
  materialization and tests deliberately select the script. Record this as a
  low-priority V1 review: a switch must preserve foreground ownership under
  `tini`, signals, restart/exit behavior, project arguments, runtime
  properties, and canonical formation identity. Details and close criteria
  are in
  `devcapsule/implementation-notes/bugs/2026-08-03-jetbrains-native-launcher.md`.
- The product owner reported that `devcapsule project run` is substantially
  more comfortable than the historical launch workflow and nearly ready to
  become the primary development entry point from the new checkout. At that
  checkpoint this was a strong positive signal rather than final completion;
  the later acceptance and landed status are recorded above.
  The requested detailed, sanitized session reconstruction is
  `devcapsule/implementation-notes/session-records/2026-08-03-v021-external-dogfood-and-v1-backlog.md`.
- JetBrains AI Assistant's Codex ACP integration failed in the fresh v021 home
  even though API-key connection testing succeeded. OpenAI's current manual
  says an explicitly set `CODEX_HOME` must already exist. The PyCharm launcher
  unconditionally exports `/home/devcapsule/.codex`, while the agent-neutral
  generic runtime correctly does not create that directory; preserved home and
  ACP logs confirmed the exact mismatch. Remove the ambient override and let
  Codex use its default `~/.codex` beneath persistent home. A future explicit
  Codex component may declare/create a custom path, but do not add agent state
  to every runtime or mount host Codex state. The immediate dogfood workaround,
  official source, evidence, tests, and close criteria are in
  `devcapsule/implementation-notes/bugs/2026-08-03-codex-acp-missing-home.md`.
- The product owner created the missing `$CODEX_HOME` mode `0700` inside the
  external capsule and confirmed the workaround unblocked Codex ACP. Exact
  installed-artifact inspection also confirmed Apache-2.0 metadata for
  JetBrains `@agentclientprotocol/codex-acp` 1.1.9, ACP SDK 1.3.0, OpenAI
  `@openai/codex` 0.145.0, and its Linux x64 package; the adapter ships an
  Apache 2.0 LICENSE naming JetBrains, and OpenAI's official Codex repository
  ships Apache 2.0. This license applies to those local software artifacts,
  not automatically to JetBrains AI Assistant, hosted OpenAI models/API
  service terms, or every transitive dependency. Any future DevCapsule
  redistribution still requires pinning, checksums, complete notices, and
  service/auth disclosure.
- The product owner then selected Codex as the first optional V1 agent
  component. The current worktree advertises `codex-agent` in the dogfood
  manifest and locks JetBrains ACP 1.1.9 plus Codex CLI 0.145.0 and its exact
  Linux x64 npm tarball SHA-256. The trusted component contract declares
  checkout-scoped credential state `codex/home` at
  `/home/devcapsule/.codex`, mode `0700`, and contributes `CODEX_HOME` only
  when selected. The runtime contract now supports ancillary component slots
  and validated environment contributions generically. For compatibility with
  v021's embedded parser, the checkout plan carries the additive ancillary
  declaration but leaves its slot out of the legacy `state_slots` array; the
  generic host launcher applies the declared state mount and environment, and
  newer runtimes consume the same contribution directly before starting the
  IDE. The former unconditional launcher environment override is removed.
- The initial host-side `project component codex login` design was removed
  after UX review. Curated components now explicitly inherit a formal trusted
  abstract Python contract with runtime-template, state-to-environment,
  optional-secret, and lock-pinned artifact declarations. Codex uses that
  interface to request one credential-bearing state directory exposed as
  `CODEX_HOME`, advertise the
  optional `OPENAI_API_KEY` secret and its container-environment exposure, and
  contribute its verified CLI executable to `/usr/local/bin/codex` during
  ordinary local environment materialization. Users authenticate naturally
  with `codex login` inside the running capsule, and the mounted component
  state retains the result. No host API key is imported automatically. The
  existing generic `project config bind` command now also accepts
  `--host-environment-variable` for declared secret inputs, records only the
  source name, requires the host value at launch, passes Docker `--env NAME`
  without placing the value in argv, and warns that container processes and
  Docker inspection can observe an explicitly delivered environment secret.
- Focused validation for the refined component design covers explicit abstract
  contract inheritance, rejection of incomplete implementations,
  state-derived environment delivery, optional-secret inspection, exact
  archive-member extraction, formation identity, executable image delivery,
  legacy v021 runtime-plan compatibility, managed state, and the PyCharm
  mount. The refined design's full dirty-tree gate passed with clean Python and
  shell compilation, clean mypy over 73 source files, 172 fast tests at 80%
  coverage, source and local-PEX command smokes, PEX construction, and all
  three packaging integrations. Automated tests used a tiny checksum-pinned
  fixture rather than downloading the real Codex artifact; real
  materialization, login, and GUI/ACP restart remain external checks.
- Local-base dogfood no longer requires pretending a mutable daemon tag is the
  project's published recommendation. `project config authorize base-image
  LOCAL_NAME` accepts an already-local managed metadata-v1 base after platform
  validation, and records its immutable Docker image ID plus the current lock
  digest in developer-owned checkout input. `config list` reports
  `authorized-local`; resolution and realization re-inspect the alias and
  reject deletion or retagging rather than pulling or silently selecting a
  different image. Alternative published digests remain rejected unless the
  project lock recommends them. Local base `devcapsule-local-base:v022`, image
  ID `sha256:a259badeb0ad750ca44131c60b6dc9e06c0743f072b95f446333ba61e8dbac9b`,
  embeds committed revision `43073361c8bb11fecece7913b3a511b47dd2778a` for
  this external dogfood path; it is not yet a published lock input. An
  isolated-XDG smoke against that real local image passed authorization,
  resolution, and the `authorized-local` readiness view without touching the
  developer's checkout records. The full dirty-tree Nox gate passed with clean
  mypy over 73 source files, 176 fast tests at 80% coverage, source and
  local-PEX command smokes, PEX construction, and all three packaging
  integrations.
- WIP checkpoint validation on 2026-07-30 passed the full
  `cd devcapsule && .venv/bin/python -m nox -s build` gate: compilation and
  shell syntax checks, clean mypy over 59 source files, 79 fast tests, source
  and PEX smoke tests, PEX construction, and the built-PEX integration test.
  Docker E2E was not rerun for this documentation and checkpoint commit; its
  latest successful evidence remains the expanded materialization E2E recorded
  below.

- On 2026-07-29, the first Python-runtime package slice was implemented as
  `devcapsule.container_runtime`. It provides a strict version-1 JSON runtime-plan
  contract, generic persistent-home/XDG/state-slot planning, conservative
  graphics defaults, a `gosu` privilege-drop command boundary, a parameterized
  JetBrains adapter, and a thin entrypoint that writes the product properties
  file and execs the foreground IDE process. The adapter does not embed a
  PyCharm installation or launcher default; those values and the state-slot
  mapping come from the runtime plan. The package is exposed as the
  `devcapsule-runtime` console script.
- Automated coverage includes the container runtime through the main
  `devcapsule` package. Contract validation, generic filesystem planning,
  JetBrains property/command generation, graphics overrides, privilege-drop
  planning, and the final property-write/exec boundary are tested. The full
  `cd devcapsule && .venv/bin/python -m nox -s build` gate passed with 73
  tests, type checking, source smoke tests, PEX construction, and PEX smoke
  tests.
- This is only the entrypoint/package foundation. The next implementation
  slice remains the JetBrains-free redistributable base image plus the lock
  delivery fields, vendor notice, direct pinned download and digest failure
  handling, and deterministic workstation-local PyCharm materialization.
- The single-file PEX now exposes `devcapsule runtime [...]` and forwards the
  remaining arguments without interpretation to
  `devcapsule.container_runtime.entrypoint.main(...)`. This establishes the
  intended container distribution boundary: images can carry Python 3.12 and
  the normal `devcapsule.pex`, rather than separately installing a runtime
  package, while host-side and container-side code share the same packaged
  contracts and object model. Source and PEX smoke gates exercise the runtime
  dispatch path.
- The active implementation note now specifies the proposed redistributable
  default-base packaging for human review: Ubuntu 24.04, Python 3.12, the
  existing curated Linux development/public-tooling baseline, and the normal
  `devcapsule.pex` at `/opt/devcapsule/bin/devcapsule.pex`. The proposed OCI
  wiring is `tini -- devcapsule.pex runtime` as `ENTRYPOINT` with the generic
  runtime-plan path as `CMD`. It also defines PEX cache behavior, labels,
  license/inventory obligations, separation from PyCharm assets, and automated
  plus host inspection evidence. No image implementation was changed for this
  documentation review checkpoint.
- The first explicit integration/E2E test structure is now present and
  documented in `devcapsule/tests/README.md`. Fast tests remain Docker-free;
  the `integration` Nox session builds and executes the PEX; the explicit
  `e2e` session builds a uniquely tagged disposable image from a selected
  already-local Python-3.12-capable base, inspects its generic OCI process
  configuration, runs `devcapsule.pex runtime --help` with networking disabled,
  and cleans up the image. The normal build gate includes integration but not
  Docker E2E. Runtime `--help` is owned by and forwarded to the container
  entrypoint so these tests cross the intended dispatch boundary.
- Validation passed on 2026-07-29: the full Nox build gate passed with 75 fast
  tests plus the new built-PEX integration test, and the explicit `nox -s e2e`
  session passed against local `mycodespace.ai/pycharm:debug-v018`. The E2E run
  rebuilt the PEX, built and inspected a disposable wrapper image, executed
  runtime-owned help through `tini` and the in-image PEX with `--network none`,
  and removed the test image successfully.
- Initial default-base and local-materialization implementation now exists.
  The base-image planner builds an Ubuntu 24.04 image using the established
  development/tooling baseline, embeds the exact PEX at
  `/opt/devcapsule/bin/devcapsule.pex`, records its digest and recipe/source
  labels, and configures generic `ENTRYPOINT` plus runtime-plan `CMD`.
  Host-side materialization provides content-addressed acquisition with
  mandatory SHA-256 verification, safe archive extraction, deterministic local
  image naming from base/artifact/recipe identities, a generated parameterized
  JetBrains runtime plan, and reuse before acquisition when the local image
  already exists.
- The expanded Docker E2E passed with 79 fast tests and clean mypy. It uses the
  production base specification over the already-provisioned dogfood root for
  speed, verifies Python 3.12, PEX identity, labels and OCI configuration, then
  materializes a checksum-pinned JetBrains-shaped fixture and proves a second
  call performs neither download nor rebuild. Both uniquely named images are
  cleaned up. The official JetBrains metadata currently identifies PyCharm
  2026.2.0.1 at a roughly 1.28 GB Linux archive plus vendor checksum endpoint;
  this real download is reserved for a separately explicit vendor E2E.
- The acquisition/materialization primitives are not yet wired into
  capability-first `devcapsule run` or the committed lock schema. That is the
  next implementation step; current `run` still expects an already-local image
  reference.
- A product-facing V1 user-experience draft now traces the clean-clone journey,
  explains the distinct roles of the committed declaration, platform lock,
  developer-owned checkout state, and workstation-local image, and separates
  the batteries-included default from personal state, host authorization,
  alternative environments, and the expert image path. It is explicitly a
  design draft rather than current CLI instructions and records the remaining
  installation, vendor-notice, progress, inspection, alternative-resolution,
  and workflow-bootstrap questions.
- The draft now makes local resolution a deliberate planning and review phase
  separate from realization and launch. `config resolve` owns safe checkout
  bootstrap, input and authorization validation, and the inspectable generated
  plan without acquisition or container side effects; `run` requires that plan
  to be fresh, then materializes and launches it. Routine return-to-work remains
  one command, while first use and configuration changes retain an explicit
  review boundary.
- The interaction roadmap now distinguishes V1 from V2. In V1, users make
  required and optional configuration choices iteratively through the CLI or
  by editing developer-owned checkout TOML, then use `config resolve` as the
  explicit completion and validation signal before `run`. In V2,
  `devcapsule run` becomes the main interactive mechanism and subsumes ordinary
  resolution through a graphical experience, initially envisioned as an
  embedded local web application opened in the browser. V2 removes the command
  boundary for interactive users but preserves logical review and explicit
  authorization before materialization and launch.
- The previous capability-first manual test is now explicitly classified as a
  dogfood state-migration test. Its six `state adopt` commands are required to
  preserve six existing PyCharm state directories before `config resolve`;
  they are not clean-checkout onboarding requirements. Fresh V1 users should
  be able to accept checkout-scoped managed state defaults without adoption.
  The current dependency on `state adopt` to create the checkout record is
  recorded as a transitional implementation gap.
- The V1 user-experience draft now includes project-required runtime values and
  secret bindings, using a development database as the motivating example.
  Projects declare required names, sensitivity, defaults, and delivery shape;
  developers supply ordinary values and secret-source bindings; secret values
  are retrieved at launch and must not enter committed files, checkout TOML,
  generated resolution, images, build caches, or diagnostics. The exact V1
  input and secret-provider grammar remains open.

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

4. Complete the V1-blocking release-artifact publication task. The
   organization namespace `mycodespaceai`, repository
   `mycodespaceai/devcapsule-base`, and first authenticated push path are
   validated. Official artifacts must use semantic product versions such as
   `ubuntu-24.04-1.0.0-rc.1` and `ubuntu-24.04-1.0.0`, plus versioned PEX names
   such as `devcapsule-1.0.0.pex`, rather than internal `v019` checkpoints.
   They must record a real source revision, publish checksums/digests and a
   basic security-scan result, and pass clean pull/download validation.
   Committed platform locks must use globally resolvable,
   digest-pinned OCI distribution references such as
   `docker.io/ORGANIZATION/devcapsule-base@sha256:DIGEST`; they must reject
   workstation-local image IDs, daemon-local aliases, and mutable tag-only
   references. Local bases remain available only through developer-owned or
   run-once `--base` overrides.
   Notes: `devcapsule/implementation-notes/2026-07-15-docker-hub-namespace-and-publication-plan.md`
   Requirements: root `R-PRODUCT-001`, root `R-DOCS-002`,
   `devcapsule/REQUIREMENTS.md` R-PYTHON-MVP-002 and R-DOCS-002.
   Verification: build from the intended V1 source revision, publish at least
   one release candidate and the accepted V1 artifacts, verify their labels and
   checksums/digests, and prove clean pull/download from the documented release
   locations.

Next task:

Review the current gaps to V1, and decide on a project plan to take us to V1.

The active execution plan for the next functional dogfood stage is
`devcapsule/implementation-notes/2026-08-03-next-functional-dogfood-stage-plan.md`.
It started from branch `wip/local-pycharm-materialization` at committed
revision `b5d42e8` and is now landed and closed by product-owner manual
acceptance.

The product owner has made the executive decision that DevCapsule will not
support Gemini CLI. This retires D-0005's former open possibility of a later
optional Gemini component without changing D-0005's accepted agent-neutral
base direction. Active work must not install, select, configure, mount state
for, or advertise Gemini CLI. A negative absence check is only a regression
guard.

The local v023 base and running canonical materialized environment carry exact
source revision `a33988a24a91ef382c1c5c6265ba2a34762ba115`. The product owner
tagged and pushed that exact base as
`docker.io/mycodespaceai/devcapsule-base:ubuntu-24.04-v023`; registry inspection
and the local image's `RepoDigests` agree on immutable digest
`sha256:e8ec48fa1f45f566e997735ac5e8ce8086a2512681db0e8a22696ee0801a8aa1`.
The committed Linux dogfood lock now selects that digest. Normal run reuses or
automatically materializes the authorized image without baking project, state,
credential, authorization, UID/GID, or mount choices into it. The retired
second-checkout script is not a remaining task.

Later V1 backlog:

1. Build an explicitly invoked, disposable multi-project E2E orchestrator. It
   should create exact-revision DevCapsule and representative project checkouts
   under a temporary root, isolate all XDG state, build or strictly reuse the
   selected managed base, configure/authorize/resolve/run through production
   commands, and inspect running containers. Cover authorized and safe
   unauthorized cases, canonical materialization, generic OCI/runtime-plan
   boundaries, mounts, identity, network, memory, Docker, sudo, lifecycle, and
   persistence. Use unique ownership labels, sanitized evidence, and
   deterministic cleanup without touching real checkouts, personal state,
   credentials, or unrelated Docker resources.
2. Add schema-validated defaults for ordinary configuration values. A project
   default must apply when the checkout has no override, appear distinctly in
   `config list`, participate in resolution and curated runtime effects, and
   become stale when its manifest declaration changes. Checkout `config set`
   remains the higher-precedence override. Defaults must never imply host
   authorization, secret delivery, or host-resource binding. Once supported,
   this repository should declare `default = "8GiB"` for
   `runtime.memory-limit`. Prove the effective value through
   `HostConfig.Memory` and `/sys/fs/cgroup/memory.max` in the E2E while retaining
   checkout-override precedence. This is explicitly later V1 and does not
   reopen the manually accepted dogfood checkpoint.
3. Finish shared runtime-option parity without weakening bridge networking or
   no-host-access defaults.
4. Complete external Codex CLI, JetBrains ACP, authentication, and persistence
   validation using component-owned `CODEX_HOME`. Keep Antigravity optional and
   do not acquire it without a separate artifact, license, state,
   authentication, and update-policy decision.
5. Complete external GUI validation of the accepted JCEF workaround and review
   the component runtime-path and ecosystem-aware project-bootstrap follow-ups.

The V1 gap review may reorder, combine, or explicitly defer these backlog
items; their presence here does not prejudge the resulting project plan.

V2 candidate task:

1. Add safe, reversible image and cache lifecycle management. Users should be
   able to inspect DevCapsule ownership and disk usage, preview removals,
   remove selected materialized images and aliases, and prune unreferenced
   artifacts/build caches. Running or lock-referenced images require explicit
   handling, and cleanup must never touch project source, persistent state,
   credentials, or unrelated Docker resources. If V1 closes early, this is a
   candidate to pull forward deliberately rather than an implicit V1 blocker.
2. Add verifiable software supply-chain provenance for published DevCapsule
   artifacts: generated SBOMs, artifact signatures, public build provenance
   and attestations tied to source and recipe inputs, automated vulnerability
   scanning and policy evaluation, and client-side verification of the expected
   publisher and evidence before execution. This supersedes V1's expedient
   exact-digest authorization plus published checksum/basic-scan evidence; it
   is not an implicit V1 blocker.

Standing rule:

1. Keep any isolation relaxation explicit and documented.
   Requirements: `devcapsule/REQUIREMENTS.md` R-SCOPE-001, R-DOCKER-001 and
   root R-PRODUCT-002.
   Reopen if: a change adds host access, credentials, networking, devices, or
   filesystem mounts without matching documentation.
