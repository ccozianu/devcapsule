# Input: Release Notes As A Release Artifact, Published With The Tag And On The Website

Sent: 2026-09-26

From: `maintenance`, at the owner's request after 0.2.14 shipped with its
notes living only in the release overview, to be pasted by hand into the
GitHub release body. The owner asks that this be specified in the workflow
and automated. Proposal for the release runbook you own; sequencing yours.

## The gap

`v0.2.14`'s GitHub release body is the generated pull-request list. The
human-written notes, including the R-COMPAT-001 exception the requirement
says must appear in the release's notes, exist only under
`engineering-docs/releases/v0.2.14/README.md`, and the owner must paste
them. Nothing checks that a final release carries notes.

## Proposal

1. A notes file is a release artifact: `engineering-docs/releases/<tag>/notes.md`,
   written on the release branch before the final tag, alongside the
   acceptance record. Plain Markdown, authored for adopters: what changed
   for them, named compatibility exceptions with remedies, deferred items.
2. The final gate requires it for a final tag, the way it requires the
   acceptance record, and reads it from the captured `main` revision. The
   backend passes it to `gh release create --notes-file` and keeps the
   generated pull-request list appended. Candidates may carry a shorter
   file or none.
3. The website publishes it: the content contract (R-DOCS-003, W12) gains
   a `releases` source, `engineering-docs/releases/*/notes.md`, rendered as
   a Releases page with one entry per final tag, linked from the version
   switcher's "current". The producer commits to the file; the website owns
   the rendering; the same file is the GitHub body, so nothing is written
   twice.
4. For 0.2.14, backfill `engineering-docs/releases/v0.2.14/notes.md` from
   the overview's block so the website page starts complete.

Asked: adopt into the release runbook and the 0.2.15 plan; hand item 3 to
`user-docs` and the website through W12.
