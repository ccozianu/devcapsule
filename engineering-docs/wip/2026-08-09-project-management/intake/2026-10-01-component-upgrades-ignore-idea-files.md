# Owner ruling: ignore `.idea` in the source tree; document the rule in 0.2.16

Sent: 2026-10-01

From: `component-upgrades`, to `project-management`. Owner ruling taken in
this checkout while resuming component-upgrades; it belongs in the 0.2.16
proposal, which lives on your branch.

## What is handed over

The owner ruled that this repository simply ignores IDE project files
under `.idea/` in the source tree, and that 0.2.16 addresses the matter
with documentation and clear rules rather than with tooling. The owner
also noted that other projects may choose differently, so the rule is this
repository's and the product's guidance to project owners should say the
choice is theirs.

## Why it belongs to you

It is a 0.2.16 scope item for the release proposal, and the rule's home is
`WORKFLOW-LOCAL.md` or `DEVELOPING.md`, which you steward; the
implementation is a repository change, not component wiring.

## Evidence

Ten files under `.idea/` are tracked on `main` today (`devcapsule.iml`,
`fixture.iml`, `fixture@1.iml`, `fixture@2.iml`, `modules.xml`,
`project.iml`, the inspection profile and `.idea/.gitignore`), while root
`.gitignore` already excludes two others. Switching this checkout from
project-management to component-upgrades on 2026-10-01 was blocked three
times by local differences in those files; they were set aside in the
session scratchpad, not committed. The agent memory rule "IDE project
files are noise" was the working practice; the owner has now made it the
repository's rule.

## What accepting means

Add a 0.2.16 candidate: untrack the `.idea/` files on `main` with a
`git rm --cached` and a root `.gitignore` entry, and write the rule in the
developer brief or local workflow, including the sentence that other
projects may track theirs. Ordinary integration; no release gate.
