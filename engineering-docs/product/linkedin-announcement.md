# LinkedIn Announcement Draft

Replace the placeholder URL after GitHub Pages is enabled for the repository.

```text
I am starting to open up a project I have been working on with a few close
friends: DevCapsule.

The idea is simple:

A software project should carry both its development environment and its
essential memory.

If I come back to a project a year from now, or invite a new developer or AI
coding agent into it, I do not want them reconstructing the setup from stale
chat history, old terminal commands, and half-remembered decisions.

The goal is one-command environment rehydration plus one-read project memory
rehydration:

- launch the right IDE or agentic editor in a reproducible container
- mount only the selected project and explicit runtime resources
- keep IDE settings and plugins persistent
- handle Git and secrets without casually mounting the host home directory
- preserve requirements, decisions, bugs, validation notes, and next steps in
  repo-local markdown

The first working target is Dockerized PyCharm. The larger v1 direction is a
profile-driven DevCapsule framework for IDEs and agentic tools, including
workflows like Node/React/Prisma projects with AI coding agents.

This is not intended to be security theater, and it is not trying to replace
every existing devcontainer workflow. It is an attempt to make AI-assisted
development more reproducible, more resumable, and more explicit about what the
agent is allowed to touch.

I wrote a working-backwards press release to explain the product direction:

https://<github-user>.github.io/<repo>/

Feedback is welcome, especially from developers using AI agents seriously in
real projects.
```

Shorter version:

```text
I am opening up DevCapsule, a project about reproducible AI-ready IDE
environments and durable project memory.

The goal: a developer or AI coding agent should be able to return to a project
months later, launch the right development environment in one command, and
recover the essential requirements, decisions, bugs, validation notes, and next
steps from the repo itself.

The first target is Dockerized PyCharm. The v1 direction is a generic,
profile-driven framework for IDEs and agentic coding tools.

Working-backwards draft:
https://<github-user>.github.io/<repo>/
```
