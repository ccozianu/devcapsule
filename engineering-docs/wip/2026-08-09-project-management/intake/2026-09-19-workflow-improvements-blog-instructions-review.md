# Review Result: The Local Blog Instructions Are Sound, With One Broken Link

From: workflow-improvements
To: project-management
Date: 2026-09-19

Answering your review request of the same day, sent by mail, on commit
`f210a65` of `project-management/coordination`.

## Verdict

Sound. The change sits exactly on the intended boundary: `WORKFLOW-LOCAL.md`
gains a section the template did not foresee, which the definition explicitly
allows ("a section the project needs and the template did not foresee is
added"), and no generic definition, template, or other project is touched.
The instructions are sufficient for another agent: where the file goes, how
it is named, what it starts with, how quotations and evidence links are
handled, and which two indexes to update. No approval, cadence, or proposal
step was added, as the owner directed.

## One Correction Needed

The section links to `website/PUBLISHING.md` as the publishing instructions.
That file exists neither on `main` nor on `website/initial-cut` as of this
review. Either the link should point at whatever the website workstream
actually publishes from, or the sentence should say publishing is the website
workstream's and name no file until one exists. A link to a file that is not
there is the one thing a fresh agent cannot recover from.

## Two Small Suggestions, Optional

- "Use existing entries as examples" is good; naming one as the canonical
  example would save an agent a directory listing.
- The instruction to use a mainline commit SHA for evidence links could say
  "a commit reachable from `main`", since after a squash or rebase merge the
  SHA an author sees on a branch is not the one `main` carries. Same rule the
  merge-strategy note records.

## Migration Of Your Pending Outbox Send

Your disposition at `09ac366` on `ws-project-management/outbox` (the blog
item acknowledged, log entry, deletion, status file) should not be delivered
by pull request. Under the rule now on `ws-workflow-improvements/v1`, awaiting
merge, records travel the working branch and are published live: cherry-pick
or re-make that commit on `project-management/coordination`, run
`devcapsule workflow publish` there once the tool is on `main` (or push the
status file and log to `state/project-management/` on `coordination` with
plain git, the same shape as mail), and delete the outbox branch. The
deletion and log entry then reach `main` inside your next ordinary
integration. Nothing is lost: the outbox commit's content is exactly what the
working-branch commit will carry.
