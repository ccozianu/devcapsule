# Intake: Schedule The `ws-` Branch Rename Across Open Workstreams

Delivered: 2026-09-18

From: `workflow-improvements`, recording a product-owner decision of the same
day and asking you to sequence its migration.

## What Is Being Handed Over

Branch names become a closed vocabulary once the pending `workflow-improvements`
pull request merges: `main`; `ws-<workstream>/<sub>` for workstream branches,
with `ws-<workstream>/outbox` reserved; `release-<version>` for release
branches. Any other ref is outside the workflow. The migration step, recorded
under *Changes* in `WORKFLOW.md`: each open workstream renames its own
branches, updates its registry row through its own outbox, and retargets any
open pull request, **before the next release candidate is tagged**. After that
a branch outside the vocabulary is not a workstream branch.

`workflow-improvements` has renamed its own two branches and its rows. Six
rows remain, each its owner's to change under the registry-row ownership this
project already practices:

- `project-management/coordination` and `project-management/outbox` (yours)
- `sample-projects/fastapi-webapp`
- `contained-display/display-transport` and `contained-display/outbox`
- `component-catalog/antigravity-cli` and `component-catalog/outbox`
- `user-docs/first-session` and `user-docs/outbox`
- `website/initial-cut`
- `eclipse-surface` has no branch yet and needs no rename.

Legacy refs that predate the workflow are untouched; the owner has said they
will be migrated separately.

## Why It Belongs Here

You own sequencing and lifecycle across workstreams, and several of these are
paused; whoever resumes them, or you on their behalf if they conclude first,
performs the rename. Sending six identical items would say the same thing six
times.

## Also In The Same Round

The `[workflow]` table in `.devcapsule/devcapsule.toml` now declares
`definition`, `version`, and `mode`; the definition's frontmatter carries the
same version; bootstrap and the bump script keep them equal. The version is
the DevCapsule release, stamped `0.2.12` now and advanced by the release bump.
This is a delivered slice of the *One Workflow, Many Projects* question on how
an update is recognized; the umbrella review should treat it as done rather
than redesign it.

## Also: The Version-Bump Timing Is Relaxed

The owner stamped the workflow and the package as 0.2.14 on 2026-09-18,
mid-cycle, and ruled that a product-owner version bump is accommodated at any
point in the cycle, by any jump. The workflow's *Releases* section now says
the release branch's first commit confirms the version rather than owning it.
The operator guide's 2026-09-13 rule, "bump it in the first commit on the
release branch", should read the same way: set no later than that commit,
and a no-op when the owner has already set it. Fold this into the runbook
edit the 2026-09-16 item asks for.

## What Accepting Would Mean

Scheduling the renames so they complete before the next release candidate,
and renaming your own two branches when convenient. Nothing here needs doing
before the pull request merges.
