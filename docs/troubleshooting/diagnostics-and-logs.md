---
description: Where every component of a session writes its log, what the files are called, how to raise the verbosity, and what to include when asking for help.
weight: 2
updated: 2026-10-11
---
# Diagnostics and logs

Every launch gets its own log directory on your computer. Every critical
component of the session writes one file there, named after itself. Nothing
depends on a flag you had to set before the problem happened: the files are
there by default, and they survive the browser tab, Ctrl+C in the launcher,
the IDE's exit and the container's removal.

If the session directory cannot be created, or an external Docker daemon
cannot see its backing mount, the launcher reports that and continues with
console output only.

## Where the logs are

The launcher prints the directory at every start, on the line `Session logs:`
of the storage summary. Inside the capsule the same directory is mounted at
`/var/log/devcapsule`, and the environment variable `DEVCAPSULE_LOG_DIR`
names it, so a tool or an agent in the capsule finds it without guessing.

On your computer the directory lives in your DevCapsule state storage, per
checkout, one directory per session:

```text
$XDG_STATE_HOME/devcapsule/projects/by-path/<checkout id>/logs/<session id>/
```

`$XDG_STATE_HOME` is `~/.local/state` unless you set it. The session id is
the start time in UTC and a short random suffix, `20261011-041533-3f9a`, so
the directories sort by time. `devcapsule project info` lists the `logs` row
with the exact path for your checkout.

## What is in a session directory

| File | Written by | What it holds |
|---|---|---|
| `session.json` | the launcher | The session id, start time, launcher version and source revision, image, container name, project path and mount, the IDE |
| `devcapsule-launcher.log` | the launcher, on your computer | The session's start and end, the `docker run` command, warnings |
| `devcapsule-supervisor.log` | the capsule's process supervisor | Every child's start, readiness, exit and signal, with the exit code or signal name; warnings |
| `devcapsule-xvnc.log` | Xvnc, the capsule's X server | Errors and connection events: a viewer accepted or closed |
| `devcapsule-window-manager.log`, `devcapsule-panel.log` | openbox, tint2 | Their standard output and error, as they print it |
| `devcapsule-novnc.log` | websockify, the browser bridge | Connections opened and closed, handshake failures |
| `devcapsule-console.log` | the web console | Warnings and errors of the console and its server |
| `devcapsule-<ide>.log`, for example `devcapsule-pycharm.log` | the IDE's standard output and error | What the IDE prints when it starts and fails; its own log stays in its log directory, see below |
| `devcapsule-job.log` | a headless job | The job's output |

Every file of the capsule side is also what you see on the launcher's
terminal: the supervisor copies each child's output to its file and to the
console, with a UTC timestamp in front of each line in the file. Partial
lines reach the console without waiting for a newline.
The launcher's and the supervisor's own records carry the level and the
process id as well.

The IDE keeps its own log where it always did, in its persistent log
directory: `idea.log` for the JetBrains IDEs, under the log slot listed by
`devcapsule project info`; the `logs` directory of VSCodium's user data;
`.metadata/.log` of the Eclipse workspace. Those logs are not copied; the
session directory holds the IDE's standard streams only.

## Levels and the verbosity override

The baseline is the equivalent of WARNING: each component records warnings
and errors, and the session's lifecycle events, which are recorded whatever
the baseline says, because they are what reconstructs an incident. For Xvnc
the baseline is its status level, errors plus connection and server state
changes.

To see more for one launch, set `DEVCAPSULE_LOG_LEVEL` on the launcher's
shell. It accepts `DEBUG`, `INFO`, `WARNING` and `ERROR` and reaches every
component: the launcher, the supervisor, the web console, and Xvnc, which
logs everything under `DEBUG`.

```bash
DEVCAPSULE_LOG_LEVEL=DEBUG devcapsule project run
```

A value the variable does not accept is reported once, and the session logs
at WARNING.

## How much disk this takes

- The launcher's and the supervisor's files rotate at 10 MiB, keeping five
  older segments each.
- A copied child's payload stops at 50 MiB, including timestamps. One extra
  line in the file says so,
  and the console keeps showing the rest.
- A checkout keeps its newest 20 session directories. Older ones are removed
  at the next launch, and the launcher's log names what was removed.

These bounds are the first edition; compression and an aggregate budget per
checkout are planned and tracked in the project's work orders.

## When asking for help

Attach, from the session directory:

1. `session.json`, which ties the logs to the exact launcher and image.
2. `devcapsule-launcher.log` and `devcapsule-supervisor.log`.
3. The file of the component that misbehaved, for example
   `devcapsule-novnc.log` for a browser that could not connect, or the IDE's
   file for an IDE that did not come up.
4. What you did, in order, and what you expected to see.

The web console's request access log is disabled, so raising verbosity does
not record run tokens from request URLs. Child output, custom Docker
arguments and the IDE's own log can contain credentials or project content;
read the files before sharing them.
