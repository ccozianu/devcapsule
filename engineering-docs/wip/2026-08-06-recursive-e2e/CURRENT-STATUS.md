# Workstream Current Status: Recursive Dogfood E2E

Mnemonic: `recursive-e2e`

Start date: 2026-08-06

State: active

Integration target: `main`

Requirements: `R-PRODUCT-002`, `R-SCOPE-001`, `R-DOCKER-001`

## Goal

From the accepted running v024 dogfood container, use a clean clone of a later
DevCapsule revision to build and launch a successor environment while proving
source identity, host-boundary authorization, persistence, and safe cleanup.

## Branch Association

The active branch is `recursive-e2e/stage-4`, created from remote `main`
revision `432d2b4` after the multiple-stream workflow bootstrap was archived
successfully. The original `milestone/recursive-dogfood-e2e` branch predates
adoption and remains the documented historical exception; it is no longer the
active continuation branch.

## Current State

- Stages 0 through 5 are complete. Stage 4 was reopened and completed again
  after the v025 redistribution-license remediation.
- The Stage 6 live launch slice is successful: the production planner launched
  a detached v025 successor, the independent inspector passed, and both the
  successor and the untouched v024 control remain running. Stage 6 hardening
  and exhaustive expected-plan/failure-path coverage remain open before the
  stage is declared complete.
- Work resumed on the conforming `recursive-e2e/stage-4` branch from current
  remote `main`.
- Stage 3 proved an exact, independent, credential-free local clone and a clean
  contributor bootstrap in recursive and laptop contexts.
- The first Stage 4 image embedded Claude Code. Its tag and exact manifest were
  removed after Anthropic's current license and terms were found not to clearly
  grant public binary redistribution. A verified agent-neutral replacement now
  owns the v025 tag.
- Base recipe version 4 keeps Node.js on `PATH` and adds Eclipse Temurin JDK 25
  LTS and Apache Maven with `JAVA_HOME`, `MAVEN_HOME`, and both `bin`
  directories on executable `PATH`.
- Claude Code is now an agent-neutral component input: after explicit
  checkout-owned terms authorization, local materialization downloads the
  checksum-pinned binary directly from Anthropic into `/opt/claude`. The public
  base and PEX do not contain the binary.
- The repository documentation was reorganized under `engineering-docs/`, and
  the Python distribution project moved from `devcapsule/` to
  `devcapsule-src/`.
- The recursive E2E now runs current-source readiness checks separately from
  immutable v024 PEX revision and checksum verification.

## Last Task And Status

Last task: materialize and launch the v025 dogfood successor with checkout-local
Claude Code acquisition while retaining the v024 control.

Status: live slice complete. Run `b2093d85912fa34ac1324e1da26a9dcd`
authorized the exact v025 local image plus Claude acquisition, materialized and
strictly reused the canonical environment, and launched exact container
`7e92dcba38685c1b1cf508c6b26e8312454746ec51f186ed4043a510d9d51c93`.
The independent inspector passed and the successor remains stable with no
restart. On 2026-08-12 the user confirmed that the new PyCharm window is
visible and usable. The detailed Stage 6 hardening slices remain open.

## Evidence

- Recursive dogfood E2E: `2 passed`, `1 deselected` in 30.74 seconds on
  2026-08-07.
- Commit `44fbe34` restored the recursive E2E after the Python distribution
  directory rename while retaining embedded-PEX build identity and SHA-256
  checks.
- The multiple-workflow finalization procedure completed successfully on
  remote `main` at revision `432d2b4`; the active branch starts at that exact
  revision.
- Focused recursive-preflight tests: `14 passed`.
- Mypy: no issues over 57 source files.
- Successor-content focused tests: `45 passed`; mypy reports no issues over 85
  source files.
- Full dirty-tree Nox gate: `226 passed`, `8 deselected`; PEX integration:
  `5 passed`. The expected local-only PEX was built and smoke-tested.
- The current v024 container still passes the two Stage 3 recursive E2Es when
  the missing launcher marker is scoped explicitly to the test process:
  `2 passed`, `1 deselected` in 82.95 seconds.
- Successor source commits `da38cd7`, `0761940`, and `20b2ee1` are published on
  `origin/recursive-e2e/stage-4`. The last commit fixes public PEX provenance
  forwarding without exposing that override to nested integration tests.
- Retained Stage 4 run ID:
  `25f664fb3629f51be8e3894a0df8ffa7`. Its clone is detached at full revision
  `20b2ee1e7d2aa3b07f94270da624b882df1e3215`, has no remote, and imported no
  credentials.
- The clean retained-run gate passed mypy over 85 source files, `227 passed`
  with `8 deselected`, five packaging integrations, and public-PEX smoke tests.
- Public successor PEX SHA-256:
  `d52c6b9d6296c6b683e64e8ac130d7a4eb21bd33c7742f888e8d6244e1759a8b`.
- The unsafe superseded v025 had local image ID
  `sha256:c8f6dddbfaab7e412079cd89f9a5bdf631dd9c3b7ab963375a8f3302c1e7b066`
  and registry digest
  `sha256:7093cea8f1e06c10a437f3946dc7e3dd643271f071d17b6a140e4df763598fd3`.
  Both its tag and exact registry manifest were deleted on 2026-08-11; neither
  the tag nor old digest resolved before replacement publication.
- Replacement source revision:
  `c933ec38202719fbe1879846e5de48200136f9e3`. Clean Nox gate: mypy over 87
  source/test files, `229 passed` with `8 deselected`, five packaging
  integrations, and local/public PEX smoke tests.
- Replacement public PEX SHA-256:
  `976aa0708f0a247550cc8b594c461272af1b20dbc6146bfda54baba918a82f61`.
- Replacement v025 tag:
  `docker.io/mycodespaceai/devcapsule-base:ubuntu-24.04-v025`.
  Immutable local image ID:
  `sha256:9c806703213bc280b6378e52e037bc55df85b585b662e20ef06ad3bb1ae48173`.
  Published registry digest:
  `sha256:b8d355b497a9aa2fc5b2420db0c07227721e3cf7d3388b2ca81f3ed40fb86a7f`.
- Strict pull-by-digest inspection confirmed recipe `ubuntu-24.04@4`, Node.js
  `v22.23.1`, npm `10.9.8`, Eclipse Temurin/JDK `25.0.4+7`, Apache Maven
  `3.9.16`, `JAVA_HOME=/opt/java/current`, `MAVEN_HOME=/opt/maven/current`,
  correct executable `PATH`, retained JDK/Maven legal files, exact PEX/source
  lineage, generic runtime contract, and no Claude or Gemini CLI in the base.
- The authorization CLI recorded `claude-code-download = true` in a mode-0600
  test-owned checkout record. Production realization against the published
  v025 downloaded Claude Code `2.1.227` directly from Anthropic, verified
  SHA-256 `6832dc3f1797b890b71116e5f2dbbf9a83fd3d0498c235b4b0f9cd0e6e499ad6`,
  installed `/opt/claude/bin/claude` only in the local formation, set
  `DISABLE_UPDATES=1`, and preserved the Node/Java/Maven toolchain. The
  disposable probe image and caches were removed afterward.
- Stage 5 retained run ID:
  `b2093d85912fa34ac1324e1da26a9dcd`. Its isolated checkout resolution
  authorizes the exact local v025 identity, direct Claude acquisition, host
  Docker, host networking, and development sudo. No credentials were imported.
- Canonical successor environment:
  `devcapsule-local-pycharm:2145e28bc7b8aca0eee0`, formation identity
  `2145e28bc7b8aca0eee0a839050d626b5186aa57463045fb85abe8003581fb77`,
  immutable image ID
  `sha256:f3fa500c3811d2f838a56af224e61f15524de014fa4270174b14ec36e894dbee`.
  A second production realization strictly reused that exact image.
- Detached successor source revision:
  `600c085228884112e8860c3e6cdc4fb7b6674c0b`; public-provenance PEX SHA-256:
  `aee9346f1766aa10260da2d879a4049ff838f92642240a9d54f5b183ec0e59a0`.
  The clean build gate passed mypy over 88 source/test files, `230 passed` with
  `8 deselected`, five packaging integrations, and source/public-PEX smoke
  tests.
- Detached successor container:
  `7e92dcba38685c1b1cf508c6b26e8312454746ec51f186ed4043a510d9d51c93`,
  deterministic name
  `devcapsule-e2e-b2093d85912fa34ac1324e1da26a9dcd-successor`. Exact name,
  E2E labels, image ID, running state, zero-restart stability, PyCharm process,
  runtime plan, Docker access, and noninteractive sudo all passed.
- Successor tool probes passed: Claude Code `2.1.227`, Codex `0.145.0`, Node.js
  `v22.23.1`, `javac 25.0.4`, Maven `3.9.16`,
  `JAVA_HOME=/opt/java/current`, and `MAVEN_HOME=/opt/maven/current`.
- The original v024-derived control container
  `pycharm-isolated-costin-1786394284` remained running and unchanged during
  launch and inspection.
- Manual GUI handoff evidence: on 2026-08-12 the user confirmed that the v025
  successor's new PyCharm window is visible and usable. A subsequent daemon
  inspection still showed the successor running with zero restarts and the
  v024 control running independently.
- The accepted v024 bootstrap source revision remains
  `e2dae20abcd2b60fde8f4f7901e6b88b40f097df`.
- Embedded v024 PEX SHA-256 remains
  `fb278f145a583faba12df9c4a663b41cb60b0b508a769b050cfa4e088f13febc`.
- Published base recommendation remains
  `docker.io/mycodespaceai/devcapsule-base@sha256:0c9ebc0c9744a525c160bba1a0f75dacd27cd16cb5dfee769f69bc2c3165fb81`.

## Next Resumable Task

Finish Stage 6 before beginning Stage 7:

1. harden the inspector to compare the complete expected Docker plan, mounts,
   identity, security settings, and runtime-plan digest;
2. add public-interface tests for malformed Docker output, early exit,
   ownership/label mismatch, redaction, staging lifetime, and cleanup refusal;
3. record a bounded second-inspection stability result in retained evidence;
   and
4. keep both exact containers and the run-owned staging until Stage 7 proves
   persistence and deterministic cleanup.

## External State And Risks

- Development is running in the accepted v024-derived PyCharm container
  `pycharm-isolated-costin-1786394284`.
- The v025 successor is also running under exact ID
  `7e92dcba38685c1b1cf508c6b26e8312454746ec51f186ed4043a510d9d51c93`.
  Do not remove it or run-owned staging before Stage 7 persistence checks.
- That launch lacks `DEVCAPSULE_RECURSIVE_E2E=1`. Current-source preflight
  classifies the missing marker as a warning because Docker socket, container
  identity, mounts, network mode, and runtime-plan authorization are inspected
  independently. Tests requiring the marker used a process-scoped value; the
  launcher metadata mismatch remains to be corrected in a later launch.
- The project base authorization and generated local resolution are stale by
  deliberate developer-owned choices. Do not reauthorize a base implicitly.
- The bare v024 base does not add `/opt/node/current/bin` to `PATH`; recipe
  version 4 corrects this and adds the Java/Maven toolchain only in the
  successor.
- Host Docker, host networking, development sudo, X11, and persistent-home
  access remain explicit security boundaries.
- The retained successful run and its mode-0600 Stage 4 evidence remain under
  the ownership-marked recursive-E2E workspace. Earlier failed diagnostic runs
  remain retained as failure evidence and must not be removed broadly.

## Workstream Document Index

This workstream currently owns only this WIP status file. Its established
execution and evidence records predate the WIP convention and remain permanent
engineering records:

- [Milestone plan](../../implementation-notes/devcapsule/2026-08-06-recursive-dogfood-e2e-milestone-plan.md)
- [Stage 2 execution checklist](../../implementation-notes/devcapsule/2026-08-06-recursive-dogfood-stage-2-execution-checklist.md)
- [V1 test backlog](../../implementation-notes/devcapsule/2026-08-07-v1-test-backlog.md)
- [V1 gap plan](../../design-notes/devcapsule/2026-08-06-v1-gap-review.md)
