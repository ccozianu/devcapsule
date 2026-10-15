---
description: Start a project from an empty folder with the IDE, language and agent you want, and commit its environment with the code.
weight: 2
updated: 2026-09-28
---
# A new project

Make the folder, initialize it with what the project needs, open it. The
environment declaration is born with the project and travels with it.

```bash
mkdir -p ~/projects/my-app
cd ~/projects/my-app
git init
~/.local/bin/devcapsule project init --need frontend-ide --need node
~/.local/bin/devcapsule project run
```

Replace the two `--need` values for Python and PyCharm with `python-ide` and
`python`. To start with an agent from the first launch, answer *yes* when
`init` offers the default agent, or add one afterwards with one command; see
[Choose an agent](../working-with-ai/choose-an-agent.md).

Commit `.devcapsule/` with your first commit. It is the project's
environment: anyone who clones the repository runs `project init` once and
gets the same tools at the same versions.

What you can declare beyond the IDE and the language, and how services such
as a database fit, are [What a project declares](declare-needs.md) and
[Services and ports](services-and-ports.md).
