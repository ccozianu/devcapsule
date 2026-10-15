---
description: What a session is, how it starts and ends, how the desktop URL works, and how to reconnect after closing the tab.
weight: 1
updated: 2026-09-28
---
# Start, stop, reconnect

A session starts with `project run` in the project folder and ends when the
IDE exits. In between, a browser tab shows the capsule's desktop.

**Start.** `~/.local/bin/devcapsule project run` builds what is missing,
starts the container, and prints a URL on your computer's loopback
interface with a token generated for this run. It tries to open the URL in
your default browser; if no tab appears, paste the whole URL yourself. The
port and the token are new for every run; the URL is the key to this
session, so keep it private.

**Reconnect.** Closing the tab leaves everything running. Reopen the URL
and the desktop is as you left it. A second `project run` in the same folder
cannot recover a running session's URL, so keep the launcher terminal open
or its output saved.

**Stop.** **File → Exit** in the IDE ends the session cleanly; the
container is removed. Ctrl+C in the launcher terminal also stops it, less
gracefully. `docker stop` on the container name that `project info` shows
does the same from outside.

What survives a stop is on [What persists](what-persists.md). Running two
projects, or the same project twice, is on [Several projects](several-projects.md).
