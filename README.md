# DevCapsule

[![Tests](https://github.com/ccozianu/devcapsule/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/ccozianu/devcapsule/actions/workflows/tests.yml)
[![Coverage](docs/badges/coverage.svg)](https://github.com/ccozianu/devcapsule/actions/workflows/tests.yml)

<!-- website:hero -->
## Start working on a project right away!

A real IDE and a coding agent of your choice, inside a capsule that shares
your project folder and nothing else on your computer unless you say so.
Ready in minutes, persistent across sessions, honest about its edges.
**[Start here: open your first workspace](docs/getting-started/first-session.md)**
on Linux x86-64; on Windows, [read the WSL2 notes first](docs/platforms/windows-wsl2.md).

- Pre-V1
- Linux x86-64
- Windows via WSL2
- Open source, Apache-2.0

<!-- website:benefits -->
- **A real IDE in a capsule.** PyCharm, IntelliJ IDEA, Rider or VSCodium with the editing, debugging,
  testing, plugins and persistent settings you expect, and the project's
  tools already in place. Zero time spent installing things per project.
  [Your first session](docs/getting-started/first-session.md)
- **Agents at full speed, behind a boundary you control.** Claude Code, Codex
  or the Antigravity CLI work in "YOLO" mode, no approval per step, because
  the worst they can reach is your project folder, which Git protects.
  [What the capsule can touch](docs/containment/the-boundary.md)
- **Leave and come back.** Stop for an hour or a month; your IDE state,
  your agents' sign-ins and your extra tools are there when you return.
  [Sessions](docs/sessions/start-stop-reconnect.md)
- **People and agents on one repository.** A workflow that records status,
  decisions and next steps in files, so any person or any agent resumes cold.
  We use it to build DevCapsule. [Collaboration](docs/collaboration/working-in-workstreams.md)

<!-- website:fit -->
## Is it for you?

### Good fit today

- You develop on Linux x86-64, or on Windows through WSL2, with Docker and
  Git already on your command line.
- You run one or more coding agents on real projects and want them fast
  without giving them your home directory.
- You like knowing exactly what a tool can touch, and you would rather read
  a bug record than guess.

### Not yet

- macOS: the executable is Linux-only and a port has not been started.
- ARM: not covered by this release.
- A polished experience: this is pre-V1. Expect edges, and expect every edge
  to have a file.

<!-- website:dogfood -->
DevCapsule is developed inside DevCapsule, by one person and several agents,
and the journal is the transcript. **We DO eat our own dog food.**

<!-- website:why -->
## Why DevCapsule?

Gone are the days of spending hours onboarding, following complicated setup
instructions, and debugging your development environment. For supported project
types, DevCapsule gives you a ready-to-use, reproducible workspace with the tools
and dependencies already in place.

No more “it works on my laptop” excuses.

**Work in a full-fledged IDE.** Choose from supported leading IDEs, paired with
an AI coding agent of your choice, with the
editing, navigation, debugging, testing, plugins, and persistent settings you
expect for serious development. ZERO time spent installing new things every
other project. As a bona fide hacker, let's assume you already have Docker
and Git on the command line in your pocket :)

**Let your coding agent work at full speed.** DevCapsule supports major coding
agents, running in “YOLO” mode inside an isolated workspace. Let them edit files,
run tests, and use development tools without approving every routine step.

**YOLO, you said?** Just last week I read another `rm -rf $HOME` story.

Access to host resources beyond that boundary requires your explicit opt-in.
You decide what to grant and can withdraw it when it’s no longer needed.
By default, an AI mishap can only destroy your checked-out source code.
But that's why you have Git: your project is backed up on GitHub, GitLab,
or some other remote. There's no excuse not to.

### Aim for engineering excellence. Keep the fun.

From hobbyists to seasoned professionals, DevCapsule puts good engineering
within reach. Your AI helps with the minutiae: testing your code, tracking
requirements, preserving design decisions, and keeping the next step clear.

Switch tasks, change agents, or put a project aside for months—then return with
its environment and essential context preserved. You keep the judgment; AI
helps with the bookkeeping.

**Less engineering envy. More satisfaction in what you build.**

<!-- website:comparison -->
### But is it really needed?

Others solve parts of this; we tried them and found they fell a bit short of
our expectations. We’re building the combination we want—and using
DevCapsule to build DevCapsule. [See the detailed comparison](engineering-docs/design-notes/devcapsule/competitive-comparison.md).

<!-- website:contribute -->
## Contribute

Every open bug is a file under [engineering-docs/bugs](engineering-docs/bugs/)
with its evidence, and every workstream a status file that says what is next.
Pick a bug, work it with an agent inside DevCapsule, and send it back as a
pull request; the [developer brief](DEVELOPING.md) and the
[workflow](WORKFLOW.md) tell you what to read first. A one-page front door for
first contributions is coming; until then, an issue saying what you tried is
the right first message.

<!-- website:end -->

---

[Documentation](docs/README.md) · [For developers](DEVELOPING.md) · [Apache-2.0 license](LICENSE)
