# Workstream Current Status: Capsule Web Console

Mnemonic: `capsule-webconsole`

Start date: 2026-10-09

State: active; selected 2026-10-09 at the owner's direction, synchronized with `main`, the work order and its two amendments taken into intake; the owner's further instructions are awaited before the first slice

Definition read: WORKFLOW.md@9593256c1f36, WORKFLOW-LOCAL.md@94e091bf2579

Branch association: `ws-capsule-webconsole/first-slice`

Integration target: `main`

Delivery method: pull request, merge commit

Requirements: `R-CONSOLE-001`

Work order: [the capsule web console](../../work-orders/2026-10-09-capsule-webconsole.md), issued 2026-10-09 by `project-management`; its DOT and materialized-views amendments are in intake, and the amended text is on `project-management`'s branch until its next integration

## Goal And Scope

Every capsule serves a web console on a token-gated loopback port, whenever
the runtime runs, with or without a display. The console shows what the
`devcapsule` commands report, as HTML: the configuration, the versions, the
project information, and live process and resource data from inside the
capsule. Later slices render the repository's records and workflow state and
host the decision pages the workflow's human-input rules allow.

Owner decisions of 2026-10-09 that shape the work:

1. The console lives in the base image for every adopter. It is not a
   component and not a selectable capability. A headless user reaches it
   with an SSH port forward.
2. Architecture: a static web structure plus a FastAPI application for
   dynamic data. The console is a separate process, not part of the runtime
   PEX. It reads the mounted project and calls the runtime CLI's `--json`
   outputs as its API.
3. No existing open-source console is adopted as the framework. Glances or a
   similar tool may become an optional component later, linked from the
   console, but the configuration, records and workflow pages are ours and
   no product renders them.

## Current State

Registered 2026-10-09 from `project-management` at the owner's direction.
Later the same day the owner directed the switch to this workstream. This
checkout selected it, merged `origin/main` at `d8a1aa4` into the branch, and
took the three waiting mail items into intake: the work order, the DOT
amendment and the materialized-views amendment. They are undecided until the
owner's further instructions, announced for this session, are heard.

Definition changes read with that merge: work orders start workstreams
(topic 12.11), materialized views (topic 12.12), diagrams first in DOT
(topic 9.6 rule 6), recorded visual end-to-end tests (topic 9.6 rule 7).
No implementation yet.

## Planned Next Step

First slice, in order:

1. Runtime: a plan field for the console; a supervised child that starts it
   beside websockify or alone in a headless capsule; host-side loopback port
   and token wiring mirroring the contained display; URL printed and opened
   when a browser exists; `--json` on `config list` and `versions show`.
2. New subproject `devcapsule-webconsole/`: FastAPI application; static tree
   with `markdown-it` vendored; pages for configuration, info and versions;
   one dynamic panel for processes and resources from `/proc` and the
   cgroup; the run token required on every request; paths confined to the
   project mount.
3. Base recipe 10: the console's dependencies in a hash-pinned venv and the
   console wheel installed from the verified public revision, as the runtime
   PEX is; a local base build proves it.
4. Development mount of the checkout's console source over the image's copy,
   under the recorded self-hosting exception, so edits show on the next run.
5. Tests: unit for routing, token refusal and traversal refusal; a smoke that
   starts the console in a fresh capsule and fetches the home page; the IDE
   smoke rows gain a "console answers" check.

Later slices: records rendered from the mounted project, workflow state from
root `CURRENT-STATUS.md` and the status files, Mermaid, and the decision pages
of the human-input rule.

## Validation And External State

Nothing built or run yet. No containers, images or ports in use.

## Open Threads

- Awaiting the owner: the further instructions announced for the switch,
  before the first slice is planned and the intake items are decided.
- Base-release cadence: a console change reaches adopters only with a base
  image rebuild and publication, which the release runbook treats as rare.
  Development iterates through the mounted source; the owner may want a
  console release trigger named in the release policy.
- Dependencies in the base: Ubuntu's `python3-fastapi` and friends are old;
  a hash-pinned venv at image build is the recommendation, like Playwright's.
- API contract: the console calls the runtime CLI with `--json`. Which
  commands gain `--json` beyond `config list` and `versions show`, and whether
  the JSON shape is declared stable, is decided when the first page needs it.
- Deliberately not preserved: the exploration of adopting Glances, Netdata,
  Cockpit or a Docker dashboard as the framework; the reasons are summarized
  in decision 3 above.

## Workstream Document Index

- [Intake decisions](intake-dispositions.md) and [intake](intake/README.md) — coordination
