# Draft Pitch: Batteries Included, Boundaries Explicit

Status: working draft

Audience: developers, open-source contributors, students, hobbyists, and small
teams adopting AI coding agents in real projects.

## Short Thesis

Developers build polished software for finance, commerce, healthcare,
education, and almost every other domain, but their own development environments
are often fragile, slow to recreate, under-documented, and unsafe by default.

The problem gets sharper with AI coding agents. A modern coding agent is not
just autocomplete. It can edit files, run commands, inspect logs, install
packages, call CLIs, use Docker, touch credentials, and change project state.
That power is useful only when the agent has a real working environment,
durable project context, and explicit boundaries.

This project is about making development workspaces product-quality:
batteries included, reproducible, resumable, and explicit about what the IDE,
developer tools, and AI agent are allowed to touch.

## Origin Story

Programming culture has long valued "batteries included" tools: systems that
arrive with enough standard capability to let developers do real work without
spending days assembling the basics.

Development environments often still fail that test. A developer may be able to
build sophisticated software for other industries, while their own coding setup
depends on stale notes, machine-local configuration, fragile shell history,
hand-installed plugins, missing libraries, undocumented secrets, and tribal
memory.

There is a Romanian saying: "croitorul umbla cu pantalonii rupti in fund" - the
tailor walks around with torn trousers. That is the shape of the problem. The
people who build software for everyone else often tolerate poor tooling,
especially outside elite internal engineering environments.

This is not only a problem for professional teams. It affects students,
hobbyists, open-source contributors, independent developers, and commercial
teams that do not have a dedicated internal developer-infrastructure group.

## The Devcontainer/Codespaces Gap

Devcontainers and cloud codespaces address a real need: making project runtimes
more reproducible. They are useful and should not be dismissed.

The gap is that they usually solve only part of the workspace problem. They
often focus on the application runtime or a VS Code remote-container workflow,
not the full development surface:

- the IDE or editor experience;
- persistent plugins and settings;
- AI-agent permissions;
- credential transport;
- Docker access policy;
- GUI or browser needs;
- project memory;
- current task state;
- validation history;
- explicit host-exposure boundaries.

The first-open experience can also be painful. A user opens a project, waits
for an image build, waits for container startup, then waits again while editor
server components and extensions are installed inside the running container.
Even when the design is sound, the lived experience can feel like the tool is
still provisioning itself long after the developer expected to be working.

The critique is not that devcontainers failed. The critique is that a
devcontainer is not the whole product. A high-quality development workspace
should treat the IDE, agent runtime, project tools, state, memory, and
boundaries as first-class parts of the system.

## Product Point Of View

Devcontainers made app runtimes reproducible. This project aims to make the
whole coding workspace reproducible:

- full IDE or agentic editor;
- common development tools;
- selected project mount;
- persistent IDE settings and plugins;
- per-project runtime state;
- explicit Docker capability profiles;
- Git identity and credentials without mounting host credential directories;
- repo-local requirements, bugs, decisions, validation notes, and next steps;
- documented host exposure for every broader capability.

The core product promise:

```text
A project should be able to carry the environment and memory needed for a human
developer or AI coding agent to resume useful work quickly and safely.
```

## Positioning Sentence

DevCapsule gives each project a batteries-included, AI-ready coding workspace:
a reproducible IDE runtime, durable project memory, persistent developer
comfort state, and explicit host-access boundaries.

## Alternative Taglines

- Batteries included. Boundaries explicit.
- Reproducible coding spaces for humans and AI agents.
- Product-quality workspaces for the people who build products.
- A real IDE, a remembered project, and a clear permission boundary.
- Stop rebuilding your development environment from memory.

## Critical Framing

Avoid saying:

- Devcontainers failed.
- Codespaces is bad.
- This is perfect security.
- This replaces every local IDE workflow.
- Batteries included means every possible dependency is preinstalled.

Prefer saying:

- Devcontainers solve an important part of the problem, but not the whole
  workspace.
- This project focuses on the full IDE and agent runtime boundary.
- The goal is practical isolation and explicit host exposure, not perfect
  containment.
- The default should be useful, and every stronger capability should be a
  visible profile choice.
- Batteries included means enough tools, state, and context to make progress
  without turning the host into an undocumented dependency.

## Naming Notes

The domain `mycodespace.ai` is useful, but "CodeSpace" as a primary standalone
product name risks confusion with GitHub Codespaces and the broader codespace
concept.

A safer structure may be:

```text
Code Capsule by MyCodeSpace.ai
DevCapsule by MyCodeSpace.ai
DevCapsule by MyCodeSpace.ai
```

The chosen product-facing name is `DevCapsule`. The current technical Python
package name `devcapsule` remains accurate for the implementation, but the
public brand should emphasize contained, reproducible, AI-ready workspaces
without depending entirely on "codespace" as the brand.

## Open Questions

- Is "batteries included, boundaries explicit" strong enough to become the core
  message?
- Should the first public pitch lead with AI-agent safety, development
  environment reproducibility, or project-memory rehydration?
- How strongly should the story contrast with devcontainers and Codespaces
  without alienating users who like those tools?
- Should `mycodespace.ai` be used as the umbrella site while the project name
  avoids direct "codespace" branding?
