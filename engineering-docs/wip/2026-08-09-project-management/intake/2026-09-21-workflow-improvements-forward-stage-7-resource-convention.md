# Forwarded: Stage 7 Is Ready For The Resource-Ownership Convention

Delivered: 2026-09-21

From: `workflow-improvements`, forwarding an item it cannot own any longer.

## The Original Item

Sent by `recursive-e2e` on 2026-08-22, verbatim:

> # Intake: Stage 7 Is Ready For The Resource-Ownership Convention
>
> Delivered: 2026-08-22
>
> From: `recursive-e2e`
>
> ## What Is Needed
>
> Stage 7 persistence and deterministic cleanup are now active. Please
> prioritize and publish the external-resource ownership convention that
> `workflow-improvements` retained ownership of when it handed this
> workstream the implementation.
>
> The implementation needs the agreed owner/run identity and safe
> enumeration and removal boundaries for containers, images, volumes, host
> ports, and state roots. A narrow implementable contract is sufficient;
> Stage 7 will report any practical defect back through intake.
>
> ## Why Now
>
> The original handoff explicitly asked `recursive-e2e` to signal if Stage
> 7 became ready before the convention. Stages 0 through 6 and the
> v026/v026.1 publication boundary are complete. Both retained successor
> containers and their run-root paths remain available for classification
> and exact cleanup.
>
> ## Requested Outcome
>
> Publish the convention or identify the specific blocker and what clears
> it. Until then, `recursive-e2e` can classify retained evidence and refine
> the Stage 7 proof, but must not invent a competing ownership protocol.

Recoverable at `engineering-docs/wip/2026-08-09-workflow-improvements/intake/2026-08-22-recursive-e2e-stage-7-resource-convention.md`
on `main` at the revision before this workstream's next integration.

## Why It Is Forwarded

The product owner directed on 2026-09-21 that Stage 7 is done away with and
has no work in progress. That was already so: on 2026-08-27 the owner
dissolved Stage 7 into decision entries in your coordination backlog, and
your *External-Resource Ownership And Reaping* entry says this notice is
overtaken if reaping is deferred or rejected and that this workstream should
decide the item against that entry's outcome. The requester is archived, the
stage it named no longer exists, and the outcome the item waits on is yours
to decide, so acknowledging it here would keep a queue entry alive for a
consumer that is gone.

## What This Workstream Releases With It

The external-resource ownership convention itself, item 4 of this
workstream's acknowledged work since 2026-08-17. The owner's direction ends
this workstream's claim on it. Analysis, not a routing decision: the
convention is only worth writing against an implementation that exercises
it, and the one live consumer is the detached-successor cleanup bug, whose
`owner` field is now `maintenance`. Whoever you assign the reaping entry to
should write the convention as part of that work, narrowly, as the original
item asked. If the reaping entry is rejected, the convention is rejected with
it and nothing further is owed.
