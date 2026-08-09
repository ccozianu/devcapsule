# DevCapsule V1 Announcement

Status: candidate v1 artifact

Audience: developers, open-source maintainers, independent builders, learners,
and small teams using AI coding agents in real projects.

## One-Sentence Positioning

DevCapsule v1 gives a project a reproducible, AI-ready workspace with durable
project memory, strong engineering defaults, and explicit host-access
boundaries.

## Why An Adopter Should Care

DevCapsule is for three common moments in the life of a developer:

1. starting a new project;
2. retrofitting an existing project;
3. setting up a learning or course project.

In all three cases, the promise is the same:

- bring up a serious development workspace quickly and predictably;
- avoid rebuilding the environment from memory every time;
- keep project knowledge with the code instead of scattering it across chat
  history, private notes, and one person's head;
- let AI agents work in a real environment without giving them broad,
  accidental access to your machine.

## Three High-Value Use Cases

### 1. Start a new project with better defaults from day one

Most projects begin with good intentions and weak setup discipline. The code
starts moving before the environment, requirements, testing conventions, and
handoff trail are stable.

DevCapsule lets you start from a better baseline:

- a reproducible development workspace comes up fast;
- the project begins with explicit boundaries instead of ambient host access;
- requirements, decisions, bugs, validation notes, and next steps already have
  a place in the repo;
- an AI agent can help maintain that project memory as part of the normal
  workflow.

The practical value is simple: you avoid accumulating setup debt and process
debt from the first week of the project.

### 2. Retrofit an existing project without rewriting everything

Many valuable projects already exist in a messy but workable state. The code
matters, but the environment lives in stale notes, local shell history,
half-installed plugins, tribal memory, and machine-specific fixes.

DevCapsule gives you a way to capture that reality and stabilize it:

- declare the working environment instead of rediscovering it;
- preserve the IDE or agent surface people actually use;
- define which host resources are intentionally exposed;
- keep engineering records with the
- code so handoff quality improves over time.

The point is not to pretend the project was always clean. The point is to make
it progressively more reproducible, resumable, and easier to hand off.

### 3. Use a clean, repeatable workspace for learning and experimentation

Learning projects often suffer from a different problem: you want a real setup,
but you do not want the learning process polluted by workstation drift, old
packages, random local configuration, or fear of breaking something.

DevCapsule makes that kind of work easier:

- course and experiment environments can be brought up cleanly and repeated;
- the workspace is easier to reset and revisit later;
- the same project can be resumed on another machine with less friction;
- AI assistance can be used inside a defined sandbox instead of your whole
  workstation.

That makes it easier to focus on learning the stack or the concept instead of
debugging your machine.

## The Problem

Most development environments still depend on local state, hand-installed
plugins, machine-specific fixes, half-remembered setup steps, and undocumented
assumptions.

That was already expensive before AI coding agents. It is worse now, because an
agent is only useful when it has:

- the right tools;
- the right project context;
- enough permission to act;
- boundaries that are explicit enough to trust.

Without that, the usual failure modes are predictable:

- the agent is too constrained to help;
- or it has broad local access that you did not mean to grant.

DevCapsule is aimed at the practical middle ground: enough capability to do
real work, with boundaries that are deliberate instead of ambient.

## What DevCapsule V1 Gives You

DevCapsule v1 is designed to let a project carry both its workspace and its
working memory.

For an adopter, that means:

- a real IDE or agentic editor surface running in a reproducible container;
- persistent IDE settings and plugins without relying on your full host home
  directory;
- explicit project mounts, state directories, and broader capability profiles;
- a development environment that an AI agent can use without depending on
  tribal knowledge;
- repo-local requirements, handoff notes, bugs, decisions, and validation
  records that survive sessions and personnel changes.

The practical outcome is simple:

```text
You can return to a project later, or bring in another human or agent, and
resume useful work faster with fewer hidden assumptions.
```

## Better Engineering Defaults, Not Just A Runtime

DevCapsule does not just give you a containerized editor. It aims to bundle
better engineering practice into the normal working environment.

That includes:

- keeping requirements, decisions, bug records, validation notes, and handoff
  docs in the repo, next to the code;
- making that project memory readable and maintainable by both humans and AI
  agents;
- expecting the AI agent to help keep structured engineering records current as
  part of normal project work;
- for supported project types, providing strong testing and coverage defaults
  that are easy to run and visible inside the IDE;
- for supported project types, making coverage useful both at the whole-project
  level and at the level of the code currently being changed.

The goal is to make good engineering hygiene the default working mode, not an
afterthought.

## Concrete V1 Project Types

To make V1 concrete rather than aspirational, DevCapsule v1 is being shaped
around a small set of explicit starter project types:

- Python command-line tooling;
- Python library projects;
- Python FastAPI web services;
- Java library projects;
- Quarkus REST services.

These are meant to be real V1 project shapes, not vague future examples.

The intended greenfield project-creation experience is one command per project
type:

```text
devcapsule new --type python-cli --name my-tool
devcapsule new --type python-lib --name my-lib
devcapsule new --type fastapi --name my-service
devcapsule new --type java-lib --name my-lib
devcapsule new --type quarkus-rest --name my-service
```

The goal is that a developer should be able to start from one of these shapes
and immediately get not only a code skeleton, but also a reproducible
workspace, explicit boundaries, and better engineering defaults from the start.

For existing projects, DevCapsule v1 is also meant to support an adoption flow,
not only greenfield creation.

The intended retrofit experience is to point DevCapsule at an existing
repository, let it detect or confirm the project type, and generate the
workspace and engineering scaffolding around the code that already exists:

```text
devcapsule adopt --path .
devcapsule adopt --path . --type fastapi
devcapsule adopt --path . --type quarkus-rest
```

The goal is not to rewrite an existing codebase. The goal is to make it
progressively more reproducible, resumable, AI-ready, and easier to hand off.

## A Concrete Before/After

Without DevCapsule, returning to a project after a few months often means
rebuilding the toolchain, guessing which secrets and ports matter, reinstalling
editor plugins, re-learning the safe commands, and reconstructing what the last
person or agent was doing.

With DevCapsule, the project can declare the IDE surface, runtime profile,
state layout, allowed host resources, and the current project memory in version
controlled files. The next person or agent starts from a known workspace and a
known handoff point instead of a scavenger hunt.

## Why This Is More Than “Just Use A Devcontainer”

Devcontainers solve an important part of the problem well. They help make the
project runtime reproducible.

DevCapsule is aimed at the broader workspace problem:

- the IDE itself;
- agent runtime behavior;
- persistent developer comfort state;
- project memory;
- engineering defaults;
- credential transport;
- Docker access policy;
- explicit host boundaries.

The point is not that devcontainers are wrong. The point is that many adopters
need the full workspace story, not only the application runtime story.

## What V1 Includes

The current V1 direction centers on:

- a Python-based `devcapsule` CLI implementation;
- a configuration-first command model;
- Dockerized PyCharm as the original proof point;
- VSCodium plus Claude Code as a second proof point;
- persistent state and project-memory conventions stored in the repo;
- explicit runtime and host-exposure controls.

## What V1 Does Not Claim

DevCapsule v1 does not claim:

- perfect isolation;
- zero setup for every possible stack;
- replacement of every local IDE workflow;
- elimination of all risk from AI agents.

It aims for something more useful:

- a reproducible default;
- explicit stronger capabilities when needed;
- enough built-in context and tooling to make real progress.

## Recommended Short Version

DevCapsule v1 helps developers and AI coding agents resume real work faster by
giving each project a reproducible IDE workspace, durable project memory,
strong engineering defaults, and explicit host-access boundaries.

## Recommended Launch Angle

Lead with the three developer-life scenarios: starting clean, stabilizing an
existing project, and creating a repeatable learning workspace. Then reinforce
the deeper value: durable project memory, better engineering defaults, and
explicit boundaries for AI-assisted development.
