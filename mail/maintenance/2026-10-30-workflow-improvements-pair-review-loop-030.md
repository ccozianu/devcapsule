# Owner-directed 0.3.0 delivery: Pair Review Loop

Date: 2026-10-30
From: workflow-improvements
To: maintenance

The owner explicitly selected workflow-improvements to implement the new
process name and said: "I want this part of 0.3.0". The full name is
**Pair Review Loop**, with **Pair Review** as its short form.

Mainline delivery: https://github.com/ccozianu/devcapsule/pull/309
Source commit: 635ed43f2fdea16ee06b3a6b7d8921272bae0a9f

Please include this naming and packaged-definition change in 0.3.0 before
its final accepted candidate. Update the release overview/changelog to
track it. The human merges into the release branch. The mainline PR is
currently draft because the known configuration-channel test-isolation
failure remains on main; PR #293 already fixes it on the release branch.
This is not a new failure in the naming change.

## Scope

Rename current workflow headings and guidance; retain old heading anchors
and file paths. Add the existing loop rules to the packaged adopter
workflow, which lacked them. The numbered rules are unchanged. Include
PR #305's existing invocation boundary: the human requests the loop for a
task/session, or the local workflow makes it the default. Preserve all
newer release-only rules, including streaming and progress reporting.

## Validation

Workflow tests: 29 passed, one known expected failure, one non-strict
XPASS. All 17 packaged integration tests passed. Bootstrap from the final
built executable installed the exact packaged text, both names and the
invocation rule. Root and packaged loop sections match; ten numbered
rules match the release branch. Whitespace and old-anchor checks passed.
The full build reached 490 passing tests then stopped at the known
configuration-channel isolation failure; version, syntax and type checks
passed first. No runtime code or tests were changed.

## Release patch

Base: origin/release-0.3.0 at cfa45937.
Paths: the nine files named in the patch below; no new files.
The patch was composed by three-way comparison with the mainline source.
It keeps the release's version and newer rules. The only overlap was the
new short-name sentence; it is retained. An isolated-index
`git apply --cached --check` against the stated release tip passed.
Review and apply through your normal release slice. Validate the release
result and propagate it to main under the runbook; no release ref was
changed by workflow-improvements. The mainline workstream records are
not part of this patch.

```diff
--- a/WORKFLOW.md
+++ b/WORKFLOW.md
@@ -240,7 +240,8 @@
 Entered on the working branch; the release that ships it stamps this entry
 with its version. Rules changed since 0.2.14:
 
-- **The review-partner loop.** Topic 9.11: a slice built by an implementor
+- **Pair Review Loop.** Formerly the review-partner loop; **Pair Review**
+  is the short name. Topic 9.11: a slice built by an implementor
   pair and a review partner of a different engine; PRn and PRn.1; a written
   brief as the partner's only context; at most three rounds; the human
   merges PRn. Since 2026-10-29 the loop runs only on the human's request,
@@ -1367,14 +1368,17 @@
 6. Update `index.md` for every record added, removed, or renamed. The
    directory README holds the detailed template.
 
-### 9.11 The review-partner loop
-
-The review-partner loop builds one slice with two agent pairs: the
+<a id="911-the-review-partner-loop"></a>
+
+### 9.11 Pair Review Loop
+
+The Pair Review Loop builds one slice with two agent pairs: the
 implementor pair, and a review partner, an agent of a different engine with
 the human. The human names the slice, the implementor engine and the
 review-partner engine. Run the loop only when the human asks for it, for a
 task or for a session, or when the local workflow file makes it the default
 procedure. A pull request carries every step.
+Use **Pair Review** as the short name.
 
 1. The implementor builds one slice on one branch and opens its pull
    request, PRn. A stacked slice targets the previous slice's branch;
--- a/WORKFLOW-humane.md
+++ b/WORKFLOW-humane.md
@@ -756,9 +756,12 @@
 work propagate to their normal files so that no future agent must read a
 session record to find the next task.
 
-### 9.11 The review-partner loop
-
-**Rule.** One slice, two agent pairs of different engines: the implementor
+<a id="911-the-review-partner-loop"></a>
+
+### 9.11 Pair Review Loop
+
+**Rule.** Call the process **Pair Review Loop**, or **Pair Review** for short.
+One slice, two agent pairs of different engines: the implementor
 opens PRn, writes a brief that is the review partner's only context, and the
 partner answers with PRn.1 from its own checkout, a pull request against
 PRn's branch with findings, evidence and unimplemented proposals; the
@@ -772,7 +775,11 @@
 different engine is chosen on purpose: two models of the same family share
 blind spots.
 
-**Motivation.** The owner ran the pattern by hand on pull requests #170 and
+**Motivation.** The owner chose the name on 2026-10-30: the analogy to pair
+programming is easier to remember, and "Loop" emphasizes iteration. It
+replaces "review-partner loop" without changing the review rules.
+
+The owner ran the pattern by hand on pull requests #170 and
 #171 in October 2026 and on 2026-10-09 directed the agent to orchestrate it
 for the capsule web console. Eleven slices (#184 to #205) each received a
 review pull request from a Codex pair, ten merged without a round and one
--- a/WORKFLOW-LOCAL.md
+++ b/WORKFLOW-LOCAL.md
@@ -320,9 +320,11 @@
    After the human reports a merge, re-verify `main` through an SSH fetch.
 7. Keep this rule until the owner changes it or the component replaces it.
 
-## Review Partners In This Checkout
-
-Owner direction, 2026-10-22. It applies the review-partner loop, topic 9.11
+<a id="review-partners-in-this-checkout"></a>
+
+## Pair Review Loop In This Checkout
+
+Owner direction, 2026-10-22. It applies the Pair Review Loop, topic 9.11
 of `WORKFLOW.md`, in this checkout.
 
 1. The engines are the agent command lines on the capsule's `PATH`, signed
--- a/WORKFLOW-LOCAL-humane.md
+++ b/WORKFLOW-LOCAL-humane.md
@@ -242,9 +242,12 @@
 detection is a file test, not a search. It is a local arrangement, a hack of
 this project's own, until the GitHub CLI is a proper DevCapsule component.
 
-## Review Partners In This Checkout
-
-**Rule.** The engines are the three agent command lines signed in once in the
+<a id="review-partners-in-this-checkout"></a>
+
+## Pair Review Loop In This Checkout
+
+**Rule.** Apply the Pair Review Loop, or Pair Review, in this checkout.
+The engines are the three agent command lines signed in once in the
 capsule; a pair is named by engine and model; the review partner gets a
 worktree under `~/worktrees`, its own venv and its own gate scratch; it runs
 detached with the brief as its prompt, in the recorded form for its engine;
@@ -252,8 +255,8 @@
 labels; briefs are committed under the workstream's evidence; the developer
 document holds the template, the recipes and the record.
 
-**Intended effect.** A human can say "implement this with the review-partner
-loop, with that engine as the review partner" and any of the three agents
+**Intended effect.** A human can say "implement this with Pair Review,
+with that engine as the review partner" and any of the three agents
 can run it from the files alone, with the same artifacts as the loops that
 came before.
 
@@ -325,7 +328,7 @@
 
 **Motivation.** The synchronization of `release-0.3.0` with `main` during
 the cycle, on 2026-10-22 twice, each on the owner's word, exists because the cycle produced workflow rules on `main`,
-the GitHub CLI rule and the review-partner loop, that the release checkout
+the GitHub CLI rule and the Pair Review Loop, that the release checkout
 must follow too, and `main` had received nothing else outside the
 candidate process; the merge kept the release version where `main` carries
 the next development version. The release-fix exception exists because the generic rule's
--- a/devcapsule-src/devcapsule/assets/project_workflow/README.md
+++ b/devcapsule-src/devcapsule/assets/project_workflow/README.md
@@ -30,3 +30,8 @@
 coverage verifies that a built PEX installs the definition selected from this
 asset directory. The root `CURRENT-STATUS.md`, `.devcapsule/` declaration, and
 `engineering-docs/wip/` records are also DevCapsule-specific instance state.
+
+The 0.3.0 packaged workflow includes the Pair Review Loop under its own
+heading, matching root topic 9.11. The rest of the packaged document keeps
+its existing organization; this terminology slice does not refresh the
+whole definition. The root humane companion explains the same loop rules.
--- a/devcapsule-src/devcapsule/assets/project_workflow/definition/WORKFLOW.md
+++ b/devcapsule-src/devcapsule/assets/project_workflow/definition/WORKFLOW.md
@@ -340,6 +340,13 @@
 
 Entered on the working branch; the release that ships it stamps this entry
 with its version. Rules changed since 0.2.14:
+
+- **Pair Review Loop.** Formerly the review-partner loop; **Pair Review**
+  is the short name. A slice is built by an implementor pair and a review
+  partner of a different engine through PRn and PRn.1, with a written
+  brief, at most three rounds and the human merging PRn. Run it only on
+  the human's request for a task or session, or as the local default.
+  No migration.
 
 - **Two files for humans.** `PREAMBLE.md`, why the workflow is opinionated
   and for whom, and `INFORMATION-MODEL.md` are installed and refreshed beside
@@ -1817,6 +1824,57 @@
 7. Commit coherent units of work when asked, or at natural save points when the
    user wants the session state preserved.
 
+## Pair Review Loop
+
+The Pair Review Loop builds one slice with two agent pairs: the
+implementor pair, and a review partner, an agent of a different engine with
+the human. The human names the slice, the implementor engine and the
+review-partner engine. Run the loop only when the human asks for it, for a
+task or for a session, or when the local workflow file makes it the default
+procedure. A pull request carries every step.
+Use **Pair Review** as the short name.
+
+1. The implementor builds one slice on one branch and opens its pull
+   request, PRn. A stacked slice targets the previous slice's branch;
+   otherwise PRn targets the integration branch. The body of PRn states what
+   changed, the judgments taken for the human's review, and the validation
+   with its counts and limits.
+2. The implementor writes a brief for the review partner as one file. The
+   brief states: the goal; the files to read first, in order; what the
+   change does; what to look for, in this order: correctness, clarity and
+   test coverage of the changed lines; what not to widen; the validation
+   commands, verbatim; the commit authorship rule; the delivery commands;
+   the forbidden actions; the final line to print. The brief is the review
+   partner's only context.
+3. The review partner works in its own checkout with its own environment
+   and its own scratch. It does not touch the implementor's checkout, the
+   status files, the intake, or published state. It does not merge, rebase
+   or force-push. It does not build images or start capsules unless the
+   brief says so.
+4. The review partner delivers PRn.1: a branch off PRn's branch, named
+   with the suffix `-review`, and a pull request against PRn's branch. Its
+   body lists each finding as what was wrong or unclear, where, what
+   changed, and how a test proves it; then what it considered and left
+   alone, with the reason; then the proposals it did not implement; then
+   its validation with counts and limits. If it changed nothing, it says so
+   in its report and opens no empty pull request.
+5. The implementor reads the diff of PRn.1, not only its body. It posts one
+   assessment comment on PRn.1, labelled with its pair. Then it merges
+   PRn.1 into PRn's branch with a merge commit, or it pushes back with a
+   round brief that names the change requested and nothing else.
+6. At most three rounds per slice. After the third, stop and hand PRn to
+   the human with the open findings listed.
+7. After the merge of PRn.1, the implementor runs the full gate on PRn's
+   branch, records the counts in PRn, and hands PRn to the human. Only the
+   human merges PRn.
+8. The next slice starts after PRn.1 settles.
+9. Record the loop: the status file names each round and its outcome; the
+   proposals not implemented become open threads or work items; the
+   assessment comments stay on the pull requests; the briefs are kept where
+   the local file says.
+10. Stop on a blocker: credentials, network, a review partner that cannot
+    proceed. Do not work around it. Report it to the human.
+
 ## Release, Milestone, Stage, Task, And Checkpoint Terminology
 
 Use these terms consistently so a saved checkpoint is not mistaken for a
--- a/engineering-docs/development/README.md
+++ b/engineering-docs/development/README.md
@@ -12,7 +12,7 @@
 | [Integration tests](integration-tests.md) | The checks that cross a packaging or process boundary without Docker: the built executable, the CLI smoke, the type check, the documentation contract |
 | [End-to-end tests](e2e-tests.md) | The Docker-backed suites, each with its entry point, what it proves, what it needs, and the evidence it leaves |
 | [Running E2E scenario recordings](running-e2e-scenario-recordings.md) | How to replay or author a recorded IDE scenario from a shell with `nox -s ide-smoke -- --scenario` |
-| [The review-partner loop](review-partner-loop.md) | How a slice is built by two agent pairs of different engines: the brief template, the round brief, the assessment comment, the invocation recipes per engine, and the record of the loops run |
+| [Pair Review Loop](review-partner-loop.md) | How a slice is built by two agent pairs of different engines: the brief template, the round brief, the assessment comment, the invocation recipes per engine, and the record of the loops run |
 
 Placement rule: a document here describes how the project is developed and
 verified today. Requirements, decisions, specifications and release records
--- a/engineering-docs/development/review-partner-loop.md
+++ b/engineering-docs/development/review-partner-loop.md
@@ -1,8 +1,12 @@
-# The review-partner loop
+# Pair Review Loop
+
+<a id="the-review-partner-loop"></a>
+
+**Pair Review** is the short name. Previously called the review-partner loop.
 
 How a slice is built by two agent pairs of different engines in this
 repository: the rule is topic 9.11 of [`WORKFLOW.md`](../../WORKFLOW.md),
-the local arrangements are *Review Partners In This Checkout* in
+the local arrangements are *Pair Review Loop In This Checkout* in
 [`WORKFLOW-LOCAL.md`](../../WORKFLOW-LOCAL.md). This document carries what
 the rules leave to practice: the brief template, the round brief, the
 assessment comment, the invocation recipes, and the record of the loops
@@ -10,8 +14,8 @@
 
 ## How to ask for it
 
-The human says, in chat: *implement <the slice> with the review-partner
-loop, with <engine, model> as the review partner.* The agent that receives
+The human says, in chat: *implement <the slice> with Pair Review,
+with <engine, model> as the review partner.* The agent that receives
 it is the implementor. It restates the slice, names the open choices, and
 starts when the human says so. Any of the three capsule agents can be
 either side.
--- a/index.md
+++ b/index.md
@@ -45,7 +45,7 @@
 - [Integration tests](engineering-docs/development/integration-tests.md)
 - [End-to-end tests](engineering-docs/development/e2e-tests.md)
 - [Running E2E scenario recordings from a shell with nox](engineering-docs/development/running-e2e-scenario-recordings.md)
-- [The review-partner loop](engineering-docs/development/review-partner-loop.md)
+- [Pair Review Loop](engineering-docs/development/review-partner-loop.md)
 
 ## Releases
 
```
