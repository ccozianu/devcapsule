---
description: Install tools the project does not declare, such as a cloud CLI, under /opt/xtras, and keep them across container replacements.
weight: 3
updated: 2026-09-28
---
# Extra tools

The project declares the tools everyone needs. Tools only you need, a cloud
CLI, a database client, a language you are trying, go under `/opt/xtras`
inside the capsule.

- `/opt/xtras` is writable by the capsule's user without sudo.
- It survives stopping, removing and recreating the capsule: it is an alias
  of `$HOME/xtras` in the capsule's persistent home, so anything you already
  installed there is still available.
- `/opt/xtras/bin` is on `PATH` for the IDE, the terminals and the agents.

Install as the vendor describes, into a directory under `/opt/xtras`, then
put the launcher on the path:

```bash
ln -s /opt/xtras/gcloud/bin/gcloud /opt/xtras/bin/gcloud
```

These tools belong to this checkout, like the rest of its persistent home;
another checkout of the same project gets its own `/opt/xtras` unless you
bound the home directory explicitly. You manage their installation and
updates. They are not recorded in the project's lock, not installed on
another computer, and not guaranteed to run on a future base image.
`project info` lists `/opt/xtras` with its backing directory.
