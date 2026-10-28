---
status: closed
severity: minor
target: 0.3.0
owner: maintenance
opened: 2026-10-22
requirements: [R-PRODUCT-001]
---

# A healthy launch looks unhealthy in the terminal

## Symptom

Reported by `user-docs` on 2026-09-15 from a fresh VSCodium project on the
published v0.2.12, item 2 of the first-session intake, and carried as C10
into the 0.3.0 plan. Once the desktop opens, the terminal that printed the
private desktop URL fills with the display stack's and the IDE's own
output: DBus and socket notices, Electron and GPU complaints, panel
diagnostics, many labelled ERROR. The IDE works. A first-time user cannot
tell, and the link scrolls away.

## Cause

The capsule's supervisor tees every child's combined output into its log
file and, unchanged, onto its own standard error, which `docker run`
attaches to the terminal (`logs.Tee` in `devcapsule/logs.py`, used by
`devcapsule/container_runtime/supervisor.py`). The copy to the terminal
predates the session logs of 0.3.0 (#207, #209, #216), which made the
files the record; after them the terminal copy was redundant and still on.

## Expected

The terminal carries what the launcher and the supervisor say: the
desktop and console links, the ready line, the supervisor's warnings when
a component dies or a stop runs out of time, and at the end one result
line and the path of every log file of the session on the host. The
components' output is in the files, in full, and nowhere else. A file
that cannot be written still sends its output to the terminal, so nothing
is lost.

## Fix, 2026-10-22

On `ws-maintenance/0.3.0-first-session-summary`, a slice of the 0.3.0
cycle into `release-0.3.0`. The tee writes to its file only; the console
copy remains the fallback when the file cannot be opened or a write fails,
from the failed piece on. The launcher ends every session with
`session_result_text`: `Session ended`, `Session failed` with the
supervisor's log named, or `Session interrupted`, then `Session logs on
this computer:` and each file in the session directory. The infrastructure
exit code moved from the supervisor into the runtime contract so both
sides read one constant. The diagnostics page says what the terminal
carries. Unit tests: the tee copies nothing to the console with a file and
everything after a write failure; the supervisor's console carries its own
statements only; the result text for each outcome with the file listing.

## Verification target

A fresh-workspace launch on a candidate: the terminal shows the links, the
ready line and the result with the log paths, and none of the IDE's
output; the files hold it.

## Close criteria

The unit tests pass on a 0.3.0 candidate and the fresh-workspace launch
shows the terminal as expected. Reopen if a component's output reaches the
terminal while its file is being written.

## Closed, 2026-10-23

Verified by the owner on the downloaded `v0.3.0-rc2`: the terminal
carried the launcher's and the supervisor's lines and the result with the
log paths, and none of the IDE's output; the check worked as expected.
The owner's word of 2026-10-23 closes the record.
