---
description: Open a repository you already have in a capsule, whether or not it carries a DevCapsule configuration, and what gets shared with it.
role: your-project
aliases:
  - /docs/guides/your-project/
weight: 1
updated: 2026-10-28
---
# An existing repository

[Install DevCapsule](../getting-started/install.md) first. The commands here
run in your computer's terminal, from the project folder. Use a project you
trust: its source folder is shared read/write with the capsule, and tools or
agents running there can change it. Commit or back up work you care about
before experimenting.

## A project that already has a DevCapsule configuration

If the repository carries `.devcapsule/devcapsule.toml`, someone has
already declared what the project needs. From its root:

```bash
~/.local/bin/devcapsule project run
```

`run` reads the shared manifest and lock, then derives this checkout's plan.
At a terminal, it asks for missing required inputs, an IDE when none is
selected or recommended, and any needed consent. A host-access recommendation
is a question; it grants nothing. See
[Granting and withdrawing access](../containment/granting-and-withdrawing.md).

The first successful review registers this path on your computer. A second
checkout gets a separate record with a name derived from its directory.
It inherits no answers from the first checkout. Use `project checkout
register NAME` before the first run if you need a specific name.
For a second checkout, commands that record configuration answers can require
this explicit registration before the first run.
The register command cannot rename an existing record.

To inspect before answering, use `devcapsule project config show` or
`devcapsule project config check`. Both leave an unregistered checkout unchanged.
Without a manifest, `run` exits 2 and names `project init` as the remedy.

## A project without one

Choose one IDE and initialize from the project root:

| Work you want to do | Initialize with |
|---|---|
| Python, PyCharm | `~/.local/bin/devcapsule project init --require python --ide python-ide` |
| JavaScript or TypeScript, VSCodium | `~/.local/bin/devcapsule project init --require node --ide frontend-ide` |
| Any language, Visual Studio Code | `~/.local/bin/devcapsule project init --require node --ide vscode-ide` |
| Java, IntelliJ IDEA | `~/.local/bin/devcapsule project init --require java --ide java-ide` |

IntelliJ uses the unified vendor distribution with free core functionality;
paid features require your JetBrains license. Add `--offer browser-automation`
to include Python Playwright and Chromium for browser-driven tests. The
component provides `DEVCAPSULE_PLAYWRIGHT_PYTHON` as its Python executable and
`PLAYWRIGHT_BROWSERS_PATH` for its installed browser.

The prompts are the ones [your first session](../getting-started/first-session.md#1-make-a-first-workspace)
explains. Then `~/.local/bin/devcapsule project run` opens the IDE.

The capsule supplies the selected development tools. The project's own
dependencies, databases and test commands still come from its README: run
those setup commands in the IDE's terminal, inside the capsule, where they
belong. A maintained project configuration can declare more of that setup;
see [What a project declares](declare-needs.md).

## What goes where

`.devcapsule/` holds the manifest and the platform lock: what the project
needs and which exact versions satisfy it. They belong in Git with the
project, so the next person gets the same environment. Your host
permissions, private agent sign-ins and IDE state live outside the checkout,
in your local DevCapsule storage; [Project versus personal](../configuration/project-versus-personal.md)
draws the line.

**Next: [add a coding agent](../working-with-ai/choose-an-agent.md).**
