# Working Backwards Press Release: DevCapsule

Status: positioning draft

Audience: open-source contributors, developers adopting AI coding agents, and
teams that want reproducible project onboarding without giving every tool broad
host access.

## Press Release Draft

For immediate internal use.

### DevCapsule gives every project a reproducible AI-ready development environment and a durable project memory

Developers can now reopen a project months later, launch the right IDE runtime
in one command, and recover the essential context a human or coding agent needs
to continue work safely.

Modern software projects are increasingly developed with AI agents that can edit
files, run commands, inspect logs, use browsers, call CLIs, install packages,
make commits, and coordinate across tasks. That power is useful, but a normal
local workstation gives those tools too much ambient access and too little
memory. Project setup drifts over time, onboarding instructions decay, and
important decisions disappear into chat history, private notes, or the memory
of whoever was last working on the code.

DevCapsule is an open-source project that combines reproducible IDE runtimes
with repo-local project memory. A project can declare how it should be opened,
which IDE or agent surface it uses, which host resources are allowed, which
secrets are required by name, which ports and services are expected, and which
checks prove that the project is healthy. The same repository also carries its
requirements register, handoff notes, bug records, decisions, validation
history, and current next step.

The result is a practical middle ground between a loose local IDE setup and a
locked-down container that no one wants to use. Developers get a real editor,
persistent settings, plugins, project tools, Git workflows, and optional Docker
access. AI agents get enough capability to make progress. The host machine
keeps clearer boundaries.

"AI-assisted development only works well when the agent has tools, context, and
permission to act," said the founding maintainer. "The missing piece is making
that permission explicit and making the project memory durable. DevCapsule is
our attempt to make coming back to a project feel less like archaeology and more
like resuming a paused session."

The first implementation target is Dockerized PyCharm, which is currently in
v0/MVP stabilization. It already demonstrates the core pattern: run a full IDE
inside Docker, mount only the selected project and narrowly scoped runtime
resources, keep IDE settings and plugins persistent outside the image, support
Git without mounting the host home directory, and preserve project state in
markdown files that future humans and agents can read.

The next product step is to generalize this into DevCapsule v1: a
profile-driven framework for IDEs and agentic editors such as PyCharm, IntelliJ,
VS Code-family editors, and agent-first tools. A Node/React/Prisma project
could declare its package manager, Node version, Prisma/database strategy, dev
server ports, browser needs, credential names, Docker/Compose mode, and
validation commands. A future developer or agent would run one command and get
both the environment and the essential project memory back.

DevCapsule is being developed in the open so other developers can adapt the
pattern, challenge the defaults, and help define what responsible AI-ready
developer onboarding should look like.

## Customer

DevCapsule is for developers and small teams who:

- use or expect to use AI coding agents inside real development projects;
- want faster onboarding and better project resumption after long gaps;
- care about avoiding broad host mounts such as `$HOME`, `~/.ssh`, and
  credential-manager directories;
- want an IDE experience, not only a terminal container;
- need project knowledge to survive beyond chat history.

## Customer Problem

Today, a returning developer or new agent often has to reconstruct:

- the correct runtime and toolchain;
- which commands are safe to run;
- which secrets exist and where they should come from;
- how Git identity and remote credentials are supposed to work;
- what decisions were made and why;
- which bugs are active, validated, retired, or intentionally deferred;
- what the next useful task actually is.

At the same time, many AI coding tools are most useful when they can operate
inside the same environment a developer uses. The obvious local setup gives
them too much implicit access. The obvious locked-down setup makes them too weak
to help.

## Product Promise

A project using DevCapsule should be able to offer:

```text
open this project in its declared Dockerized IDE environment
```

That command should launch the declared IDE or agent surface, attach it to the
selected project, apply the declared runtime profile, preserve IDE comfort
state, expose only documented host resources, and point the human or agent at
the current project memory.

In V1, the one-command promise describes routine launch. The first use of a
checkout, and any later change to configuration inputs, has a separate
CLI-driven local resolution step. The developer iteratively supplies required
choices and may change optional defaults through commands or the local TOML,
then explicitly declares those choices complete. Resolution combines the
project's committed environment with the developer's workstation choices into
an inspectable plan. Launch consumes that plan; it does not silently rewrite
it. This gives the developer a review point before downloads, local image
formation, host-resource exposure, or process startup, while returning to an
unchanged project remains one command.

The V2 direction makes launch the main interactive mechanism. If choices are
missing or stale, it presents a graphical configuration experience—initially
envisioned as an embedded local web application opened in the browser—that
clearly separates required decisions from optional choices and defaults. Once
the user confirms the plan, launch performs resolution and continues. The
interface becomes one flow, while the review and authorization boundary
remains intact.

## Core Principles

- One selected project is the primary workspace.
- Host exposure is explicit, narrow, and documented.
- Secrets are declared by name or transport, not stored in the repo or image.
- IDE settings and plugins persist without mounting the host home directory.
- Runtime dependencies are reproducible enough for real development work.
- Project memory lives in repository files.
- Active tasks, completed tasks, bugs, and decisions are separate records.
- Every broader capability, including Docker, GPU access, browser bridging, or
  extra mounts, is an intentional profile choice.

## What Exists Today

The first proof point demonstrates the pattern with a full desktop IDE:

- persistent IDE state, plugins, caches, logs, and project workspace state;
- documented host-resource exposure for productive local development;
- explicit profiles for broader or narrower container capability;
- credential transport without mounting broad host credential directories;
- rendering and GUI choices documented as part of the environment contract;
- repo-local requirements, workflow, bug, decision, and handoff documents.

## What v1 Should Add

DevCapsule v1 should generalize the v0 pattern into a profile-driven framework:

- IDE profiles: PyCharm, IntelliJ, VS Code-family editors, Antigravity-style
  agentic editors, and future IDE targets.
- Stack profiles: Python, Node/React/Prisma, JVM, and other common project
  types.
- Declarative ports, services, secrets, runtime tools, and validation commands.
- Consistent state layout for IDE settings, extensions, agent memory, caches,
  logs, and per-project runtime data.
- A reusable project-memory bootstrap for new repositories.
- A migration path from the first proof point to the generic framework without
  losing validated behavior.

## FAQ

### Is this just a devcontainer?

No. Devcontainers solve an important part of the problem: reproducible project
tooling. DevCapsule is focused on the full IDE and agent runtime boundary,
including GUI/editor state, AI-agent permissions, credential transport,
persistent plugins, and durable project memory.

The two approaches can coexist. A future DevCapsule profile may use a
devcontainer-like project runtime while still managing the outer IDE and agent
surface.

### Why not just use the IDE locally?

For simple solo work, a local IDE is often fine. DevCapsule is aimed at the
point where the IDE also hosts autonomous or semi-autonomous agents. At that
point, local convenience starts to conflict with host safety, reproducibility,
and handoff quality.

### Why preserve memory in markdown?

Markdown is boring in the best way: it is versioned, reviewable, editable in any
tool, and readable by humans and agents. Requirements, active tasks, decisions,
bug evidence, validation notes, and next steps should not depend on a model's
conversation history.

### Does this prevent all risk from AI agents?

No. It reduces accidental ambient authority and makes powerful capabilities
visible. If a profile mounts the host Docker socket, enables GPU devices, opens
ports, or passes credentials, that is still meaningful host access. The goal is
to make those choices explicit and reviewable.

### Why start with PyCharm?

PyCharm is a demanding first target: it is a full desktop IDE with plugins,
state, Git workflows, rendering requirements, and AI integration. Making that
work proves more than a terminal-only prototype would. The project should not
remain PyCharm-only.

### What would a Node/React/Prisma profile need?

It should declare the Node version, package manager, install command, Prisma
engine and database expectations, dev server ports, browser/test automation
needs, Docker or Compose policy, secret names, file-watcher behavior, and
validation commands.

### What does success look like?

A new contributor, or the same contributor returning a year later, can open the
repo, run the project entry command, read the handoff, and understand what is
working, what is risky, what is next, and how to prove progress.
