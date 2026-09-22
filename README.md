# Coordination Branch

This branch carries workstream mail: intake items in flight between
workstreams. It is never merged into the integration branch, and its history
is append-only. A sender adds one file under `mail/<recipient>/`; the
recipient deletes only its own files after copying them into its intake
directory; nobody resets or force-pushes this branch.

Read and write it with `devcapsule workflow mail check|send|take`, or with
plain git: `git fetch origin coordination` and
`git show origin/coordination:mail/<name>/`. See *The Coordination Branch* in
`WORKFLOW.md`.
