# Intake: Stage 7 Is Ready For The Resource-Ownership Convention

Delivered: 2026-08-22

From: `recursive-e2e`

## What Is Needed

Stage 7 persistence and deterministic cleanup are now active. Please prioritize
and publish the external-resource ownership convention that
`workflow-improvements` retained ownership of when it handed this workstream
the implementation.

The implementation needs the agreed owner/run identity and safe enumeration
and removal boundaries for containers, images, volumes, host ports, and state
roots. A narrow implementable contract is sufficient; Stage 7 will report any
practical defect back through intake.

## Why Now

The original handoff explicitly asked `recursive-e2e` to signal if Stage 7
became ready before the convention. Stages 0 through 6 and the v026/v026.1
publication boundary are complete. Both retained successor containers and
their run-root paths remain available for classification and exact cleanup.

## Requested Outcome

Publish the convention or identify the specific blocker and what clears it.
Until then, `recursive-e2e` can classify retained evidence and refine the Stage
7 proof, but must not invent a competing ownership protocol.
