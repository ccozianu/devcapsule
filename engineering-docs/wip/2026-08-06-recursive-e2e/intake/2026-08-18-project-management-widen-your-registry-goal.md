# Intake: Consider Widening Your Registered Goal

Delivered: 2026-08-18

From: `project-management`, returning a change it should not have made directly.

## What Is Being Handed Over

Your registry row's goal cell reads "Build and launch a successor DevCapsule
from inside the accepted dogfood environment". The 2026-08-16 portfolio
checkpoint judged that this understates what the workstream actually carries,
and proposed widening it to add "; also owns the v026 base and its deliverables
by the 2026-08-16 decision".

`project-management` wrote that change straight into the registry on its own
branch. Your own outbox updated the same row in `PR #26`, and the two collided
in `PR #28`. The conflict was resolved by taking your version, so the widening
is not on `main` and is offered here instead.

## Why It Belongs Here

A registry row is a workstream's account of itself. Restriction 11's carve-outs
name directories rather than the registry, so the direct edit was not a rule
violation, but it was the wrong shape: `project-management` observed something
about this workstream and restated its record instead of reporting it. The
underlying protocol gap has been delivered to `workflow-improvements`
separately.

Whether the goal cell is accurate is yours to judge, and applying any change to
it is yours to do, through your own outbox.

## The Reasoning Behind The Proposal

A self-contained tool entry point and the URL-open browser shim are product
work, not recursive-E2E evidence, and both were delegated here on 2026-08-16.

The [V1 readiness assessment](../../2026-08-09-project-management/2026-08-16-v1-readiness-assessment.md)
argued this is a delivery risk rather than a naming preference: when product
work lands with no milestone home, nothing updates the V1 gap list as gaps
close. The 2026-08-15 checkpoint recorded the same pattern for
`sample-projects`, so this is the second instance rather than a one-off.

## The Case Against, Which You May Prefer

`project-management`'s own open threads record the widening as "a registry
patch, not a settled shape". The alternative is registering a separate
workstream for the product work, which keeps this workstream's goal honest and
gives that work a milestone home of its own. That option was left open
deliberately, and choosing it is a lifecycle decision to raise back to
`project-management` rather than something to decide alone.

## What Accepting Would Mean

Either the goal cell is widened through your outbox, or the alternative is
raised back, or the proposal is declined with the reason recorded — in which
case `project-management` still owns finding the product work a milestone home.
