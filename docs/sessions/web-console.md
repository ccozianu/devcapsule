---
description: "The web console: your capsule as a page, with what the devcapsule commands report, reached through one link behind the run's token."
weight: 5
updated: 2026-10-09
---
# The web console

Base recipe 10 adds a small read-only website about the capsule. Older bases
print a notice and run without the console. When you run a project, the
launcher prints two links: the desktop, when the capsule has
one, and the web console.

```text
Web console: http://127.0.0.1:41273/?token=…
  (the capsule as a page; the link works for this run only)
```

Open the link and you see the capsule's identity, then one page for each of
the inspection commands:

- **Configuration**: what `devcapsule project config list` reports.
- **Versions**: what `devcapsule project versions show` reports, the running
  session's version set and the one selected for the next launch.
- **Project**: what `devcapsule project info` reports: components,
  environment and persistent storage.
- **Processes**: the capsule's processes with their CPU and memory, and its
  use of CPU and memory against its limits, refreshed every few seconds.
  Pause the refresh to read a long list. Nothing here stops or signals a
  process; use a terminal for that.
- **Records**: the project's markdown files, rendered. `index.md` is the
  front page; links between records stay inside the console, and a fenced
  `dot` block renders as a Graphviz diagram in the browser. Images and
  other linked files are served as they are. A record is read from the
  mounted project each time you open it, so an edit shows on reload.
- **Decisions**: questions an agent working in the capsule has handed to
  you, each with its options and the records cited beside them. Choose,
  add a note, submit. The answer is written where the agent reads it, in
  the capsule's state, never in the project; the agent records the outcome
  in the project's files and discards the page.

The pages show the commands' own output, read each time you load a page. A
change you make with a command is on the page after a reload. Nothing on the
console changes anything.

## The link and the token

The link carries a token made for this run. The console refuses every request
without it. The launcher writes a private temporary token file on the host
and mounts it read-only inside the capsule. It removes the file when the
launcher returns. The printed link also carries the token. Once your browser
has opened the link, the console keeps the token in a cookie for that site, so the pages' own links
work without it. Closing the capsule invalidates the token; the next run
prints a new link.

The console listens on your computer's loopback interface only. Nothing else
on your network can reach it.

## Without a desktop

On a computer without a graphical desktop, or over SSH, the console is still
there. Forward its port and open the link on the machine with the browser:

```sh
ssh -L 41273:127.0.0.1:41273 user@dev-box
```

Use the port the launcher printed. The desktop link, when there is one,
forwards the same way.

## What you cannot do from it

The console has one write operation, the answer to a decision page, and it
writes only into the capsule's own state. No configuration change, no
process control, no file edit. The commands remain the way to change
anything, and the console shows what they recorded.
