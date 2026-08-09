# Workstream Current Status: Workflow Improvements

Mnemonic: `workflow-improvements`

Start date: 2026-08-09

State: active

Integration target: `main`

Delivery method: pull request

Requirements: `R-PRODUCT-003`, `R-PRODUCT-004`, `R-PRODUCT-005`,
`R-PRODUCT-006`

## Goal

Improve the multiple-stream human/agent workflow from concrete problems,
ambiguities, and avoidable mechanical friction found while dogfooding it during
the recursive E2E cycle. Keep each correction narrow and evidence-based, and
conclude this workstream when that dogfood cycle's accepted findings have been
fixed, explicitly deferred, or rejected.

## Branch Association

The initial branch is `workflow-improvements/intake`, forked from the
registration commit on `main`. The existing recursive E2E checkout remains
selected on `recursive-e2e/stage-4`; work on this track requires an explicit
switch to this branch or a separate clean worktree.

## Current State

- The completed `multi-workflow` workstream established and successfully
  exercised the first multiple-stream lifecycle.
- This follow-up workstream is registered as the bounded home for improvements
  discovered while the recursive E2E work exercises that lifecycle further.
- No workflow correction has been implemented yet.
- Findings observed from another checkout must be implemented only after
  switching to this workstream's clean branch or worktree; the other
  workstream's dirty state must not be mixed with this one.

## Last Task And Status

Last task: register the follow-up workstream without changing the workstream
selected by the existing recursive E2E checkout.

Status: complete. The registry, handoff, documentation index, and conforming
initial branch association are defined from current `main`.

## Next Resumable Task

Clarify the main-first workstream registration procedure when another
workstream is selected in the current checkout and repository policy requires
changes to reach `main` through a pull request.

Done means:

- the locally observed registration sequence and its protected-main/PR case
  are described precisely;
- `WORKFLOW.md`, agent routing instructions, or supporting automation are
  updated where the current contract is ambiguous or unnecessarily manual;
- the rule still guarantees that a new workstream branch starts from its
  registration commit and does not mix state with the selected checkout; and
- repository documentation checks pass.

## Evidence

- The earlier `multi-workflow` workstream completed successfully and is
  archived at
  [its final status](../../archive/2026-08-08-multi-workflow/CURRENT-STATUS.md).
- Registration of this workstream was prepared from current `main` in a
  separate temporary worktree while the primary checkout remained on
  `recursive-e2e/stage-4`.

## External State And Risks

- The environment has no Git publication credentials; the human may need to
  publish registration or integration changes.
- Repository policy defaults workstream delivery to pull requests, while the
  current beginning procedure says registration is committed on `main`. The
  next task must make the protected-main case deterministic rather than infer
  direct-main authority.
- This track may overlap `CURRENT-STATUS.md`, `WORKFLOW.md`, `AGENTS.md`, and
  workflow requirements. Synchronize with current `main` before integrating
  and do not edit the recursive E2E WIP directory from this workstream.

## Workstream Document Index

This workstream currently owns only this WIP status file.
