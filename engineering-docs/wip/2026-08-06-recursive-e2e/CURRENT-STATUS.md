# Workstream Current Status: Recursive Dogfood E2E

Mnemonic: `recursive-e2e`

Start date: 2026-08-06

State: paused

Integration target: `main`

Requirements: `R-PRODUCT-002`, `R-SCOPE-001`, `R-DOCKER-001`

## Goal

From the accepted running v024 dogfood container, use a clean clone of a later
DevCapsule revision to build and launch a successor environment while proving
source identity, host-boundary authorization, persistence, and safe cleanup.

## Branch Association

The active branch is `milestone/recursive-dogfood-e2e`. It predates adoption of
the multiple-stream workflow and is the explicit exception to the normal
`recursive-e2e/` prefix and main-first registration rules. Any later branch
created for this workstream must use the `recursive-e2e/` prefix and start from
then-current `main`.

## Current State

- Stages 0 through 3 are complete.
- Stage 3 proved an exact, independent, credential-free local clone and a clean
  contributor bootstrap in recursive and laptop contexts.
- Stage 4 has not started. No successor base or environment has been built.
- The repository documentation was reorganized under `engineering-docs/`, and
  the Python distribution project moved from `devcapsule/` to
  `devcapsule-src/`.
- The recursive E2E now runs current-source readiness checks separately from
  immutable v024 PEX revision and checksum verification.

## Last Task And Status

Last task: restore the recursive E2E after the Python distribution directory
rename without weakening v024 bootstrap-lineage verification.

Status: complete. Commit `44fbe34` changed readiness preflight to
`python -m devcapsule`, retained embedded-PEX build identity and SHA-256 checks,
and passed the complete recursive E2E.

## Evidence

- Recursive dogfood E2E: `2 passed`, `1 deselected` in 30.74 seconds on
  2026-08-07.
- Focused recursive-preflight tests: `14 passed`.
- Mypy: no issues over 57 source files.
- The accepted v024 bootstrap source revision remains
  `e2dae20abcd2b60fde8f4f7901e6b88b40f097df`.
- Embedded v024 PEX SHA-256 remains
  `fb278f145a583faba12df9c4a663b41cb60b0b508a769b050cfa4e088f13febc`.
- Published base recommendation remains
  `docker.io/mycodespaceai/devcapsule-base@sha256:0c9ebc0c9744a525c160bba1a0f75dacd27cd16cb5dfee769f69bc2c3165fb81`.

## Next Resumable Task

Begin Stage 4 from the milestone plan:

1. compose the accepted clone and contributor-bootstrap protocols into one
   retained, ownership-marked milestone run;
2. run the full clean Nox gate from the clone;
3. build and verify a revision-bearing PEX; and
4. use that PEX to build and inspect the successor base through the authorized
   host Docker daemon.

## External State And Risks

- Development is running in the accepted v024 PyCharm container
  `pycharm-isolated-costin-1786072465`.
- The project base authorization and generated local resolution are stale by
  deliberate developer-owned choices. Do not reauthorize a base implicitly.
- The bare v024 base does not add `/opt/node/current/bin` to `PATH`; this is a
  usability follow-up, not a recursive-E2E blocker.
- Host Docker, host networking, development sudo, X11, and persistent-home
  access remain explicit security boundaries.

## Workstream Document Index

This workstream currently owns only this WIP status file. Its established
execution and evidence records predate the WIP convention and remain permanent
engineering records:

- [Milestone plan](../../implementation-notes/devcapsule/2026-08-06-recursive-dogfood-e2e-milestone-plan.md)
- [Stage 2 execution checklist](../../implementation-notes/devcapsule/2026-08-06-recursive-dogfood-stage-2-execution-checklist.md)
- [V1 test backlog](../../implementation-notes/devcapsule/2026-08-07-v1-test-backlog.md)
- [V1 gap plan](../../design-notes/devcapsule/2026-08-06-v1-gap-review.md)
