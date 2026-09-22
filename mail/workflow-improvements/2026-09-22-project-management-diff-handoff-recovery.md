# Proposal: recover accidentally misplaced work by mailing a diff

From: project-management
To: workflow-improvements
Date: 2026-09-22

The owner proposes a practical alternative to committing another workstream's
implementation on the selected branch: send the owning workstream the diff and
restore the source checkout. Please review and incorporate a suitable rule in
the generic workflow. This is your scope because it changes cross-workstream
recovery and coordination-mail semantics, not DevCapsule product behavior.

## Concrete case

On `project-management/coordination`, the owner settled removal of
`project run-image` in favor of diagnostic `project run --print-command` and
assigned maintenance the implementation. The apparent committed implementation
was actually just the design and assignment; no implementation commit existed.
The owner explicitly authorized a diff handoff. We prepared the bounded change
without a source commit, validated it, and sent maintenance the full patch in
`2026-09-22-project-management-run-image-tested-patch.md`, superseding
`2026-09-22-project-management-retire-run-image-print-command.md`.

The implementation patch is based on `44166ebf9a801db4341aea9306a6267f7bd8ec60`
and also passes `git apply --cached --check` against main
`20336d80b47165dfd4a5e557b54689cd2b74804c`. Its SHA-256 is
`79794674807cbd3c1784599ac1ed0ae8e03995c0958917fb0e4347e60b0cbea9`.
The receiving workstream owns review, application and integration. This case
uses the owner's explicit exception; it does not silently amend current policy.

## Gap and acceptance

The existing definition requires workstream changes to be owner-directed,
and says coordination carries records/mail, never work. It lacks a clear way
to hand over useful uncommitted work without a branch switch or an inappropriate
source commit. A diff inside mail needs an express, narrow allowance: a review
proposal may travel there, while source commits and integration still belong to
the recipient. No new transport, editor integration or attachment service is
needed; a fenced unified diff fits existing Markdown mail.

Below is proposed wording against the current definition, not an applied change.
Preserve unrelated dirty state; do not reset muddled commits or delete previous
mail. Explicit human direction may instead authorize finishing on the current
branch when patch separation would cost more or be unsafe. Patch conflicts and
recipient validation remain real costs; this should be a recovery option, not
a mandatory detour for every cross-workstream discussion.

Accepting means deciding and documenting the generic recovery rule, keeping
packaged definition and agent guidance consistent as appropriate, and recording
the ordinary intake disposition. The source change here is a worked example,
not a request to take maintenance's feature ownership.

## Proposed definition diff

```diff
--- a/WORKFLOW.md
+++ b/WORKFLOW.md
@@ -1268,10 +1268,32 @@
 identical at every publish and the copy on `main` is one of them, older. Two
 versions of one record is the failure this whole mechanism exists to avoid.
 
-**This is not a way to put deliverable content anywhere early.** The test is
+**This is not a way to integrate deliverable content early.** The test is
 whether anyone would review it as part of the workstream's work. If yes, it is
-deliverable, and it travels the working branch under review; the coordination
-branch carries records and mail, never work.
+deliverable, and it travels the owning workstream's branch under review. Mail
+may carry a proposed patch under the recovery rule below; sending that patch
+is neither applying it nor integrating the deliverable.
+
+**A misplaced change can travel as a patch.** When a pair discovers that a
+bounded change belongs to another workstream, stop expanding that work. If
+separable, uncommitted changes already exist, send the owning workstream an
+ordinary intake item containing the diff, its base revision, affected paths,
+reason for the handoff, and validation performed or still missing. Include new
+files. The human may authorize bounded completion before this handoff; this is
+not permission to silently start another workstream's implementation.
+
+Verify delivery before removing the sender's changes. Restore only the changes
+represented by the delivered patch, preserving unrelated work. Record the
+handoff in the sender's status. Do not switch workstreams, commit the source
+change on the sender's branch, or rewrite shared history to manufacture a clean
+handoff. If committed or intertwined changes cannot be separated safely, ask
+the human to choose the recovery, which may be to finish on the current branch.
+
+The recipient decides the item through ordinary intake, reviews the patch,
+checks its applicability to its current branch, and owns any application,
+validation, source commit, and integration. A patch is a proposal, not evidence
+that the recipient has accepted or shipped the change. Supersede any earlier
+assignment with a new message; the append-only mail rule remains in force.
 
 **The deliverable may still land in slices.** Integrating a finished slice
 through an ordinary pull request before the workstream is done is permitted
```
