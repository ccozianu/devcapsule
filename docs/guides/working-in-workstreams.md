# Work in workstreams with humans and agents

This guide is for a project that uses the DevCapsule workflow in
`multiple-streams` mode: several people and several coding agents, each on
their own workstream, coordinating through git alone. It explains what a day
looks like and which command does what. The rules themselves are in the
project's `WORKFLOW.md`, which this guide explains and never redefines; when
the two seem to differ, `WORKFLOW.md` is right and this guide has a bug.

Commands run in the terminal inside the capsule, from the project's root, on
the branch of the workstream you are working in. Every command works the
same for a person and for an agent.

## The idea in one paragraph

Your project has a `main` branch that is the record, and one extra branch,
`coordination`, that is the live view. Nobody ever merges `coordination` into
`main`, and nobody ever opens a pull request for it. Each workstream keeps a
short status file describing what it is doing; publishing pushes a copy of it
to `coordination` so everyone sees it at once. Messages between workstreams
travel the same branch as small files. Nothing about coordination ever waits
for a human to click merge, and everything about it is plain git and
markdown, so it works against any remote, including a bare directory on a
shared disk.

## A session, start to finish

**1. Get your bearings.** One command prints what you need before acting:

```text
devcapsule workflow brief
```

It shows your workstream's state and next task, who else is working on what
right now, how many messages wait for you, which rules changed since you
last read the workflow, and whether your branch should catch up with `main`.
The last line is a suggestion; you or your agent make the call.

**2. Take your mail.** Items other workstreams sent you become files in your
workstream's `intake/` directory, staged and ready to commit:

```text
devcapsule workflow mail take
```

Commit them on your working branch. Each item is decided later in one
commit: a line in the decision log plus the file's deletion.

**3. Catch up with `main` if the brief says so.** A changed `WORKFLOW.md` or
`WORKFLOW-LOCAL.md` is a must; otherwise weigh it. Rebase what only you have.

**4. Say what you are on.** A claim tells the other checkouts, human or agent,
what you are working on. It expires after twelve hours by default and never
stops anyone; it informs.

```text
devcapsule workflow claim "fix the upgrade recovery"
```

**5. Work.** Edit, commit, run your checks, as always.

**6. Publish at checkpoints and before you stop.** This pushes your status
file and decision log, as they are in your working tree, to the live view:

```text
devcapsule workflow publish
```

Publishing also stamps your status file with which version of the workflow
you read, which is how the brief knows what changed for you next time.

**7. Release your claim when you pause.**

```text
devcapsule workflow claim --release
```

## Send work to another workstream

Write the item as a markdown file named `YYYY-MM-DD-<your-workstream>-<slug>.md`,
anywhere outside the repository, then:

```text
devcapsule workflow mail send maintenance /tmp/2026-09-21-alpha-upgrade-bug.md
```

Several recipients are a comma-separated list; `all` sends to every
workstream that has published. Sent mail is never edited: to correct an item,
send a new one under a new name that says what it supersedes. Only the
recipient removes an item, by taking it.

## See everyone at once

```text
devcapsule workflow status
```

One block per workstream: its state, its branch, how far behind `main` it
is, whether the workflow changed since it last read it, when it last
published, who has claimed it, and its next step. A workstream that never
published is not shown; ask its owner to publish once.

## Where things live

| What | Where | Reaches `main` how |
|---|---|---|
| a workstream's status file, decision log, intake | `engineering-docs/wip/<date>-<name>/` on its working branch | inside its ordinary pull request |
| the live copy of each status file and its claim | `state/<name>/` on `coordination` | never; it is the live view |
| a message in flight | `mail/<recipient>/` on `coordination` | never; the recipient takes it |
| the list of open workstreams | root `CURRENT-STATUS.md` on `main` | each workstream edits its own row |
| the reusable workflow | `WORKFLOW.md`, installed and versioned | refreshed by `devcapsule bootstrap --refresh-workflow-definition` |
| your project's own rules | `WORKFLOW-LOCAL.md`, yours | edited like any file |

The declaration `.devcapsule/devcapsule.toml` says which workflow and version
the project runs, in its `[workflow]` table. The version is the DevCapsule
release the definition came from; `WORKFLOW.md` carries the same version in
its frontmatter, and the tool keeps the two equal.

## Without the tool

Everything above is ordinary git on the `coordination` branch, so a person
without the executable can still take part:

```text
git fetch origin coordination
git show origin/coordination:mail/<your-workstream>/          # your mail
git show origin/coordination:state/<name>/CURRENT-STATUS.md   # anyone's live status
```

To send or take by hand, commit the file under `mail/<recipient>/` (or delete
your own) on that branch and push; never rebase or force-push it.

## If something gets in the way

- **"no workstream given and the current branch is not ws-<name>/..."**: you
  are not on a workstream branch. Pass `--workstream <name>` or switch to your
  `ws-<name>/...` branch.
- **A push is rejected while sending or publishing.** Someone else wrote to
  `coordination` at the same moment; the tool retries from a fresh fetch by
  itself, five times. If it still fails, run the command again.
- **"is already in flight with different content".** You are re-sending an
  item under a name that is already in the recipient's mailbox with different
  text. Send it under a new name.
- **Your workstream is missing from `status`.** Publish once.
- **The brief says the definition changed.** Read the *Changes* section at
  the top of `WORKFLOW.md`, newest entry first; each rule change names its
  migration step, if any.
