# Input: Four Workflow Gaps Met During The 0.2.14 Release

Sent: 2026-09-25

From: `maintenance`. Observed while releasing 0.2.14 and cleaning up after
it; recorded in the maintenance and user-docs status files, none fixed.
Each would recur in any project.

1. **The packaged definition is thinner than the root `WORKFLOW.md` at the
   same version.** Version 0.2.14 shipped without the rule on changing
   workstreams during a task and the longer selection section that the
   root file carries. Adopters on multiple streams get less than this
   repository follows. Decide whether the root additions are generic and
   propagate them, or record why they are DevCapsule-specific.
2. **`nox -s bump` does not update the `[workflow] version` declaration.**
   After reopening `main` at 0.2.15.dev0, `WORKFLOW.md` and the packaged
   definition say 0.2.15.dev0 while `.devcapsule/devcapsule.toml` still
   declares 0.2.14.dev0, as it already lagged before the release; bootstrap
   refuses that disagreement on adopter projects.
3. **`devcapsule bootstrap project` appends Python ignore defaults to every
   project's `.gitignore`**, Node projects included, seen when installing
   the definition into the website repository.
4. **No cross-project delivery.** Requests from DevCapsule to the website
   project, a separate repository, had to travel as a pointer commit
   appended to that project's status file under an owner exception, because
   `devcapsule workflow mail` does not cross repositories. The mycodespace
   design note (with project-management) makes several repositories per
   person the normal case; the workflow will need a delivery path.
