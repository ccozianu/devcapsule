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

- Stages 0 through 4 are complete.
- Work resumed on the conforming `recursive-e2e/stage-4` branch from current
  remote `main`.
- Stage 3 proved an exact, independent, credential-free local clone and a clean
  contributor bootstrap in recursive and laptop contexts.
- Stage 4 produced and strictly verified the successor base from a retained,
  origin-free clean clone. The successor environment has not been materialized
  or launched yet.
- Base recipe version 3 exposes the pinned Node.js installation through
  `/opt/node/current/bin` on the image `PATH`.
- The v025 exercise will explicitly include checksum-verified Claude Code
  2.1.227 under `/opt/claude`; the default base remains agent-neutral unless
  `--include-claude-code` is selected.
- The repository documentation was reorganized under `engineering-docs/`, and
  the Python distribution project moved from `devcapsule/` to
  `devcapsule-src/`.
- The recursive E2E now runs current-source readiness checks separately from
  immutable v024 PEX revision and checksum verification.

## Last Task And Status

Last task: execute the retained Stage 4 run and build, inspect, and publish its
v025 successor base.

Status: complete. Revision `20b2ee1e7d2aa3b07f94270da624b882df1e3215`
passed the clean, origin-free contributor gate and produced the public PEX used
to build v025. The resulting image exposes Node.js and Claude Code through
image-level `PATH`, passed the strict base probe, and was published without
overwriting an existing tag.

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
- v025 tag: `docker.io/mycodespaceai/devcapsule-base:ubuntu-24.04-v025`.
  Immutable local image ID:
  `sha256:c8f6dddbfaab7e412079cd89f9a5bdf631dd9c3b7ab963375a8f3302c1e7b066`.
  Published registry digest:
  `sha256:7093cea8f1e06c10a437f3946dc7e3dd643271f071d17b6a140e4df763598fd3`.
- Strict v025 inspection confirmed Ubuntu 24.04 root-layer identity, managed
  base metadata, recipe `ubuntu-24.04@3`, generic entrypoint and command,
  embedded PEX digest and source lineage, Node.js `v22.23.1`, npm `10.9.8`,
  Claude Code `2.1.227` under `/opt/claude`, and no Gemini CLI, project source,
  checkout configuration, developer state, credentials, runtime authorization,
  or baked runtime plan. Failure and interrupt cleanup probes also passed.
- The accepted v024 bootstrap source revision remains
  `e2dae20abcd2b60fde8f4f7901e6b88b40f097df`.
- Embedded v024 PEX SHA-256 remains
  `fb278f145a583faba12df9c4a663b41cb60b0b508a769b050cfa4e088f13febc`.
- Published base recommendation remains
  `docker.io/mycodespaceai/devcapsule-base@sha256:0c9ebc0c9744a525c160bba1a0f75dacd27cd16cb5dfee769f69bc2c3165fb81`.

## Next Resumable Task

Continue with Stage 5 from the milestone plan:

1. initialize and list checkout readiness from the retained clean clone using
   run-owned configuration roots;
2. bind only test-owned persistent state and authorize the exact local v025
   image ID without changing the committed published-base lock;
3. resolve and inspect the generated plan without acquisition or launch side
   effects; and
4. materialize or strictly reuse the canonical PyCharm/Codex successor through
   the production realization path.

## External State And Risks

- Development is running in the accepted v024-derived PyCharm container
  `pycharm-isolated-costin-1786394284`.
- That launch lacks `DEVCAPSULE_RECURSIVE_E2E=1`. Current-source preflight
  classifies the missing marker as a warning because Docker socket, container
  identity, mounts, network mode, and runtime-plan authorization are inspected
  independently. Tests requiring the marker used a process-scoped value; the
  launcher metadata mismatch remains to be corrected in a later launch.
- The project base authorization and generated local resolution are stale by
  deliberate developer-owned choices. Do not reauthorize a base implicitly.
- The bare v024 base does not add `/opt/node/current/bin` to `PATH`; recipe
  version 3 corrects this only in the successor.
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
