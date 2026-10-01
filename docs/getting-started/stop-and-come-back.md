---
description: How a session ends, what closing the browser tab does, and how you return to exactly where you left off.
weight: 3
updated: 2026-09-28
---
# Stop and come back

A capsule session is the IDE, the terminal you launched it from, and a
browser tab showing the capsule's desktop. Each has its own way of ending,
and only one of them ends the session.

## Ending a session

Choose **File → Exit** in the IDE. The capsule stops, the launcher terminal
returns to its prompt, and the container is removed. Your project folder and
your persistent state are untouched: they never lived in the container.

Pressing Ctrl+C in the launcher terminal also stops the capsule, after a
short shutdown interval. The launcher may then print a Python traceback
ending in `KeyboardInterrupt`; that is noise, not damage. Prefer the IDE's
exit for an ordinary stop.

## Closing the tab

Closing the browser tab leaves the capsule running. Reopen the URL the
launcher printed to return to the same desktop, with every window as you
left it. Each run prints a new URL; a second `project run` cannot recover
the URL of a session that is already running, so keep the terminal output.

## Coming back

From the project folder, in any terminal:

```bash
~/.local/bin/devcapsule project run
```

The IDE opens with your files, its settings, extensions and window layout,
and your agents' sign-ins. Processes you had running, servers or watchers,
restart. You do not initialize again, and you are not asked the same
questions again unless the project itself changed what it needs; see
[Recover after a project change](../configuration/project-versus-personal.md#when-the-project-changes).

What persists, and where it lives on your computer, is in
[What persists](../sessions/what-persists.md).
