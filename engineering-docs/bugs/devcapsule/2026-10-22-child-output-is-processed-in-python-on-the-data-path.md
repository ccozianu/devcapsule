---
status: confirmed
severity: minor
target: 1.0
owner: maintenance
opened: 2026-10-22
requirements: [R-PRODUCT-001]
---

# Child output is processed in Python on the data path

## Symptom

Filed by the owner's direction on 2026-10-22, after the review of the
first-session summary (PR #244): the session-logs design of 0.3.0 puts
Python on the data path of every byte a capsule component writes. The
supervisor, PID 1 of the capsule, reads each child's combined output
through a pipe on a thread per child (`logs.Tee`), splits it on newlines,
prefixes a timestamp per line, writes it into a `SegmentedFile` that
rotates and gzip-compresses in the same thread, and falls back to a
console copy when the file fails. A component that starts writing at a
high rate makes the supervisor do Python work per chunk on every byte,
under the GIL shared by all tees; while a tee compresses a segment it does
not drain its pipe, so the child blocks on a full pipe. The owner's
judgment: a substitute for `tee` should not exist in a Python codebase,
and the approach can grind the capsule's runtime to a halt under a chatty
child. Acceptable for 0.3, not for V1.

## What the records say, so the review starts from the facts

- The launcher on the host is not on this path: it logs its own events
  through `logging` to its own file. The exposure is the capsule's
  supervisor and, through PID 1, every child in it.
- The pressure is CPU under the GIL and the pipe's backpressure rather
  than garbage collection: `bytes` objects are reference-counted and never
  cyclic, so the collector does not run for them; the cost is the
  per-chunk Python work and the synchronous compression, documented in
  `Tee`'s docstring and the diagnostics page.
- The Python writer exists because of the rotation ruling of 2026-10-11:
  every writer rotates its own file on the write that would overshoot,
  with no external rotator and no overshooting, after `logrotate` as a
  supervised child was tried and set aside (PR #209, #210, #211, #212). A
  child redirected straight to a file cannot rotate in place that way, so
  the writer became Python. The per-line timestamp and the console
  fallback followed from the same decision.

## Expected

For V1, no Python on the data path of a component's output. Candidates
the review weighs, none chosen here:

1. Redirect each child's streams directly to its file and rotate from
   outside: a rotator that renames and signals (`SIGHUP` or reopen on the
   next write, which the IDEs do not do) or copies and truncates
   (`copytruncate`, with the known loss window), or a size-bounded sink
   such as `multilog`-style or `svlogd`-style tools from the base image.
2. Keep one process on the path but not Python: a small C tool from the
   base, `tee` with a rotating sink, with timestamps from `ts` or the
   sink itself.
3. Let the engine do it: Docker's `json-file` driver with `max-size` and
   `max-file` bounds the container's own stdout, but it does not give one
   file per component on the host, which the session-logs requirement
   wants, so it is a fallback for the whole, not a replacement.
4. Keep the in-process rotation but take the timestamps and the console
   fallback out of the hot path, measured first: if the review finds the
   cost is in compression and not in the per-line work, the fix is to
   compress off the thread, not to remove Python.

The review measures before it chooses: a child writing at 50 MB/s and at
one line per millisecond, the supervisor's CPU, the time the pipe blocks
the child, and whether the IDE stalls.

## Verification target

A design note under `engineering-docs/implementation-notes/devcapsule/`
with the measurements and the chosen candidate, reviewed with the owner;
then the implementation on a V1 release line, with the session-logs
requirements kept: one file per component on the host, a bound per
checkout, survival across the tab, Ctrl+C and the container's removal.

## Close criteria

No Python code handles the bytes of a child's output in the capsule, or
the measurements show the Python path is not the bottleneck and the owner
accepts them. `logs.Tee` is gone or reduced to configuration. Reopen if a
chatty child is shown to stall the supervisor or the IDE.
