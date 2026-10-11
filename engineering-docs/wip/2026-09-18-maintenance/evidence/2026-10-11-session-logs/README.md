# Session logs acceptance, 2026-10-11

Superseded in part later on 2026-10-11: the owner asked for rotation in the
writer itself, with no overshoot, so PR2 no longer runs logrotate and no
longer needs base recipe 12. The base build and the e2e session below
remain valid evidence of the branch at `174480f`; the rotation they show,
by logrotate, is replaced by `devcapsule.logs.SegmentedFile`, which the
unit suite proves with a real child process.

Slices 1 and 2 of persistent session diagnostics, PR #207 and PR #209,
proven on a real capsule. The base is recipe 12, built from the public PEX
of PR2's branch at `174480f9ba2c99b7f0348f7da0e097db6179afd6`.

## The base

- `base-build.json`: the tag, image id and builder identity the e2e session
  recorded. Built over host networking from a clean clone of the branch in
  `~/.local/share/devcapsule/e2e-workspaces/logs-accept`.
- `e2e-session.txt`: `nox -s e2e -- --build-base --build-network host`,
  nine tests passed: the built base (recipe-version 12, `logrotate
  --version` answers, no embedded runtime), the component cache (5), the
  successor lifecycle, the runtime image, the self-contained PEX.

## The session

A fresh codium project, initialized against the built base and launched
through the real launcher with `DEVCAPSULE_LOG_BUDGET=16M`, so each file
rotates at 1 MiB. Session `20261011-085622-321e`, container
`devcapsule-e2e-logs-1974aad7`.

- `listings.txt`: the session directory at start, after the padding and two
  logrotate ticks, and at the end. At start: one file per component,
  `logrotate.conf` and `session.json`, all owned by the launching user.
  After: `devcapsule-panel.log.1` of 1,500,956 bytes, the rotated segment,
  and `.logrotate.state`.
- `logrotate.conf`: the stanza the entrypoint wrote, `size 1048576`,
  `rotate 4`, `compress`, `delaycompress`, `nocreate`.
- `logrotate.state`: logrotate's own record; the panel's file was rotated at
  08:56:54 UTC, the others were seen and left alone.
- `devcapsule-logrotate.log` was empty: no complaint from any run.
- `devcapsule-supervisor.log`: logrotate started as the first child, every
  child's start and readiness, the SIGTERM at stop forwarded to all seven,
  every exit attributed, the session's end with exit code 133 (codium's
  SIGTRAP on stop, as before this work).
- `devcapsule-launcher.log`: the session's start, the exact `docker run`
  (staging paths shortened to `<staging>` here), and the end with the exit
  code.
- `session.json`: the manifest with `ended-at` and `exit-code`, the budget,
  the segment and the rotations.
- `processes.txt`: the process table inside the capsule during the session,
  with the rotation loop as pid 34 and its `sleep 30` child, and Xvnc with
  `-Log *:stderr:10`.

## What this run does not show

- Compression: it needs a second rotation of the same file; not reached.
- A writer's reopen after its file was rotated: the padded panel printed
  nothing afterwards, so its file was not recreated; the window manager and
  the IDE did print later and their files grew. Both are pinned by the unit
  tests of `devcapsule.logs`.
- The padding was written into the file directly through `docker exec`, not
  through the panel's own output; what it proves is logrotate's trigger,
  rename and state keeping on the bind mount, not the tee.

The tokens of the run were in files, never in these records. The fixture
project's records were removed after the run.

## Second session, the in-process rotation, 2026-10-11

Under `second-session/`: a fresh codium project launched through the real
launcher built from the public PEX of `b86b899`, on the recommended base
(recipe 9, no web console and no logrotate on it), with
`DEVCAPSULE_LOG_BUDGET=16M`. The session directory held one user-owned
file per component present on that base, the launcher's and the
supervisor's, and `session.json` with the segment of 1 MiB and the end
record. No padding this time: rotation in the writer is proven by the unit
suite with a real child writing 4000 lines through the tee. The supervisor's
record shows the same lifecycle as before, without a rotation child.
