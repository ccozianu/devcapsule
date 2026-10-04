---
status: closed
severity: blocking
target: 0.2.16
owner: component-catalog
opened: 2026-10-04
closed: 2026-10-04
requirements: [R-PRODUCT-001, R-PRODUCT-002]
---

# IntelliJ relaunch mistakes a reused container PID for the previous IDE

Branch: `ws-component-catalog/intellij-idea`.

## Evidence and impact

IntelliJ 2026.2.3 starts, accepts an editor interaction and persists font size
17, but after `docker stop` a fresh launch of the same project displays
`Start Failed`. Its `DirectoryLock` reports that Java PID 42 is still running;
the new container reused that PID. The stale `system/.port` Unix socket refuses
connections, and `config/.lock` still names the previous PID.

Run `20261004T003852Z-d50716`, executable source `0a928cf`, reproduces this in
`devcapsule-src/dist/e2e-evidence/ide-smoke/`. The relaunch screenshot and log
are the evidence. The initial persistence assertion incorrectly passed because
the error dialog has the IDE's window class and the configuration file still
contains 17. Review of the captured screenshot invalidated that pass.

The pinned distribution's `DirectoryLock.class` confirms that failed socket
connection is followed by process lookup in the current PID namespace. When
the new JVM has the old PID, waiting for its own exit fails. Its IPC files are
`system/.port` and `config/.lock`; they are separate from saved IDE preferences.

## Fix and verification

IntelliJ opts into a shared JetBrains adapter hook. The runtime holds advisory
exclusive locks on both profile directories for the session lifetime, then
recovers only a Unix socket that refuses connections and its regular numeric
PID file. Live endpoints, unrecognized files and symlinks remain intact.
This avoids interpreting an old PID through a new container's process namespace.
PyCharm's runtime declaration is unchanged.

The test rejects `Start Failed` windows and requires another model-driven
saved edit after relaunch, in addition to retained font size and the first
saved marker. Socket recovery, live-owner preservation, profile exclusion and
unexpected-file handling have focused tests.

Closed by validation on 2026-10-04: run `20261004T005804Z-c554e8`, runtime
source `d6d3566` and harness `c5e0535`, passed the component-browser scenario
and a real `docker stop`/relaunch. The relaunch log records stale-socket
recovery, font size remains 17, the first marker remains, and Codex/Astra
saves and visually recognizes a second marker in the working editor. Both
containers and the run-owned project records were removed. The build gate
passes with 1,117 tests and nine packaging integration tests. Branch delivery
and owner PR integration are tracked in the workstream status.
