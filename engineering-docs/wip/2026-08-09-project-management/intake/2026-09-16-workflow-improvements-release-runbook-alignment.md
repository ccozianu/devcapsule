# Intake: The Release Runbook Must Follow The New Release Rule

Delivered: 2026-09-16

From: `workflow-improvements`, completing the acceptance of the 2026-09-15
item *One Branch Per Release* that `contained-display` sent it on the product
owner's behalf. That item asked, as part of accepting, that `project-management`
be told what the runbook must say.

## What Is Being Handed Over

The workflow now defines releases: `WORKFLOW.md` gains a *Releases* section
with *Release Refs* and *Taking A Release Over*, drafted on
`workflow-improvements/v1` on 2026-09-16 and reaching `main` by pull request
after the owner's review. The
[operator guide for releasing a new version](../../../implementation-notes/devcapsule/2026-09-01-release-and-validation-process.md)
is `project-management`'s and is not edited by this workstream. Its steps must
follow from the rule once the rule lands. The consequences, so the edit starts
from them:

1. **Cut point.** The driving workstream merges its working branch to `main`
   first; `release-X.Y.Z` starts at that merge commit on `main`, never at the
   workstream branch's tip. Step 1 of the checklist currently says "keep source
   edits on the selected workstream branch" and calls the release branch "not a
   change of editing workstream". Under the new rule the opposite holds for the
   driving workstream: its working branch is closed, the release branch is its
   selection, and its registry row names it.
2. **First commit.** The version baseline bump is the release branch's first
   commit. The guide already says this (2026-09-13 rule); it now follows from
   the workflow rather than only from the guide.
3. **Merge, then tag.** Before every candidate tag, the release branch merges
   to `main` by pull request. Cherry-picking between the release branch and a
   workstream branch is out. The candidate gate passes by ancestry, and the
   acceptance record's normal integration method is `ancestry`; `reviewed`
   becomes the exception it was meant to be.
4. **Registry row during a release.** State `active; releasing X.Y.Z`, branch
   association `release-X.Y.Z`. The handoff is edited on the release branch and
   reaches `main` with the pre-candidate merges. The guide should say where the
   operator records the cut commit, each candidate, acceptance, and final tag:
   the workflow says the handoff, and leaves any further record to the guide.
5. **Afterwards.** The workstream resumes on a fresh `<mnemonic>/...` branch
   from `main` or concludes; the release branch stays behind, closed. The guide
   step 7 "retain the release branch and candidate tags" is unchanged.
6. **Who drives.** The workstream whose deliverable is the release's headline;
   otherwise, and for a maintenance release of an old version,
   `project-management`. The maintenance case keeps the guide's documented
   integration exception; the workflow names its four fields (authorizer,
   rationale, forward-port owner, follow-up) without fixing the file format.

## Why It Belongs Here

The guide is the project's release policy, which the workflow's *Releases*
section explicitly leaves to the project, and `project-management` adopted and
owns it on 2026-09-11.

## What Accepting Would Mean

Editing the guide's checklist so that an operator following it performs the
release the way the workflow now describes, once the *Releases* section is on
`main`. Until then the guide as written remains operative, and the two
documents disagree on step 1 only.

## Sequencing

Nothing here needs doing before the pull request carrying *Releases* merges.
The next release is the deadline that matters; the owner said the design
continues in `workflow-improvements` before the next release is prepared.
