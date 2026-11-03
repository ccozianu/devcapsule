---
description: Work on a repository that is not yours, and carries no DevCapsule configuration, by wrapping it as a submodule of a small project of your own.
weight: 3
updated: 2026-11-02
---
# Someone else's repository

The first slice provides the declaration, `project wrap`, and generated
guidance. The base image's additional JDK, automatic session selection,
and capsule acceptance are planned for slice 2. The commands below describe
the intended workflow; the complete capsule workflow is not yet validated.

A project you want to read, build or debug is not yours to configure: an
open-source project with an afternoon of setup instructions, or a robotics
team's public code you want to learn from. Do not send them a pull request
with a DevCapsule configuration. Wrap the repository instead: a small
repository of your own holds the configuration, and theirs is a Git submodule
of it. Nothing is written into their tree.

```bash
mkdir frc-learning && cd frc-learning && git init
~/.local/bin/devcapsule project wrap https://github.com/Mechanical-Advantage/RobotCode2025Public
~/.local/bin/devcapsule project run
```

`wrap` adds the submodule, reads what the code needs, writes the manifest and
the lock, and writes an `AGENTS.md` and a `README.md` that say what is foreign,
how to build it and which Java to use. `run` opens the capsule with the IDE on
the wrapper; the code is in the submodule. Commit what `wrap` produced; anyone
who clones the wrapper must initialize its submodules before running it.

## What `wrap` reads off the code

| Found in the repository | Declared |
|---|---|
| A Gradle wrapper with WPILib's GradleRIO plugin | `java` required, `java-ide` recommended, the Java line of that WPILib season: 17 for 2025 and 2026 |
| A Gradle wrapper without it | `java` required, `java-ide` recommended; Java 17 for Gradle 8.x and 9.0, Java 25 from 9.1 onward |
| Anything else | Nothing; `wrap` says so and names `project config require` |

The Java line matters because a build such as GradleRIO's refuses any other
JDK. The generated `AGENTS.md` names the line to select before building in
that directory. The matching JDK must exist under `/opt/java/<line>`.
Slice 2 supplies the additional JDK and session-wide selection.

Detection reads literal GradleRIO plugin declarations. It ignores comments
and string examples. Plain Gradle detection reads only `distributionUrl` in
`gradle/wrapper/gradle-wrapper.properties`. It does not execute build scripts.

## Learning or changing

`wrap URL` with the upstream's URL means you intend to learn: the submodule
is read-only in intent, and nothing is pushed. `wrap URL --upstream UPSTREAM`
means `URL` is your fork of `UPSTREAM`: your changes and pull requests go to
the fork, and the upstream is never written to unless its maintainers ask.
The `AGENTS.md` carries the same rule for the agent.

## Several repositories

Run `wrap` once per repository. The second run extends the manifest and
regenerates the two files. `--path NAME` picks the directory when the
repository's name will not do. A run interrupted by a network failure is
finished by running it again when Git registered the submodule from the same
URL. A registered source with a missing directory is initialized again.
A registered path with another URL is refused, even when its directory is
missing. Paths through symlinks are refused.

Git can leave a partial clone before it registers the submodule. In that
case, inspect the path, `.gitmodules`, and Git's modules directory before
retrying. `wrap` reports the failure and removes no files. If initialization
stops at a prompt, the added submodule remains for a rerun.

The generated guidance escapes repository names, paths, and URLs as text.
`wrap` replaces a guidance file only when its entire first line equals the
generated marker. It keeps the owner's other files.

## What `wrap` does not do

It does not install the project workflow; `project bootstrap` remains
available. It does not run the foreign project's build, tests or setup; those
run inside the capsule, from the submodule's directory, with its own tools.
It does not add the project's dependencies to the lock; the Gradle cache
lives in the capsule's persistent home, so the first build's downloads are
paid once per checkout.

**Next: [choose a coding agent](../working-with-ai/choose-an-agent.md) or
[declare project needs](declare-needs.md).**
