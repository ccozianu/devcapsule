---
status: fixed
severity: minor
target: 0.3.0
owner: maintenance
opened: 2026-10-22
requirements: [R-PRODUCT-001]
---

# Ctrl+C ends the launcher with a traceback instead of a result

## Symptom

Reported by `user-docs` on 2026-09-15 on the published v0.2.12, item 3 of
the first-session intake, carried as C10 into the 0.3.0 plan, and seen by
the owner on every candidate since. Ctrl+C in the launcher terminal stops
the capsule after its shutdown interval, as it should, and then the
launcher prints a Python traceback ending in `KeyboardInterrupt` from
`subprocess.run` and exits 1. The user-facing pages explained the
traceback as noise.

## Cause

The launcher ran `docker run` through `subprocess.run`, which on a
`KeyboardInterrupt` waits a quarter of a second, kills the client and
re-raises; nothing above the launcher caught the exception, so Python
printed it. The capsule itself stops because the terminal's SIGINT reaches
the docker client before the kill and the client forwards it into the
capsule, whose supervisor ends its children; but the client's exit code,
the capsule's end, was lost with the kill.

## Expected

Ctrl+C is an ordinary way to end a session. The launcher announces the
interrupt, waits for the capsule to stop, prints the result and the log
paths, and returns 130, as shells report an interrupted command. A capsule
that does not stop in a generous time is stopped through the daemon. A
second Ctrl+C stops the waiting and names the container to stop.

## Fix, 2026-10-22

On `ws-maintenance/0.3.0-first-session-summary`, a slice of the 0.3.0
cycle into `release-0.3.0`. `run_attached` in the launcher runs the client
under `Popen` and waits for it explicitly: the first interrupt is announced
and waited through, up to `INTERRUPT_STOP_SECONDS`; then `docker stop` is
asked and waited for; a second interrupt kills the client and reports that
the capsule may still run, with the command to stop it. The launcher
records the interrupted end in the session manifest with exit code 130,
prints the result line with the log paths, and returns 130. Unit tests
cover the four paths of `run_attached` with a fake client and the
launcher's end with the recorded exit code and the printed result. The
getting-started, sessions and troubleshooting pages describe the result
in place of the traceback.

## Verification target

A fresh-workspace launch on a candidate, interrupted with SIGINT from
another process as a terminal would: the launcher prints the interrupt
line, the result line and the log paths, exits 130, and the container is
gone.

## Close criteria

The unit tests pass on a 0.3.0 candidate and the interrupted
fresh-workspace launch ends as described. Reopen if a traceback follows
Ctrl+C or the capsule is left running without the launcher saying so.
