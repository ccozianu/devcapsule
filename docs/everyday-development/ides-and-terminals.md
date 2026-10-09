---
description: The IDEs DevCapsule offers, the terminal inside them, and how the capsule's shell differs from your computer's.
updated: 2026-10-04
weight: 1
---
# IDEs and terminals

Select one IDE capability in your project's `.devcapsule/devcapsule.toml`:

| Capability | IDE | Development tools |
|---|---|---|
| `python-ide` | PyCharm | Python from the base |
| `java-ide` | IntelliJ IDEA | Java and Maven from the base |
| `eclipse-ide` | Eclipse IDE for Java Developers | Bundled Eclipse runtime; Java and Maven from the base |
| `frontend-ide` | VSCodium | Node.js from the base |
| `dotnet-ide` | JetBrains Rider | .NET SDK selected automatically |

For Eclipse, run `devcapsule project init --need eclipse-ide --need java`, then
`devcapsule project run`. Open the printed desktop link. In Eclipse, choose
**File > Open Projects from File System** to import the mounted project folder
(or **File > Import > Maven > Existing Maven Projects** for a Maven project).
Keep source files in the mounted project folder; Eclipse's workspace at
`/ide-workspace` stores preferences, project references and local history.
It persists per checkout, along with Eclipse's user configuration in the
capsule home. The complete Java Developers package includes JDT, Git, Maven
and Gradle integration. Existing `java-ide` projects continue to use IntelliJ.

For a new Rider project, run `devcapsule project init --need dotnet-ide`, then
`devcapsule project run`. Open the desktop link printed by the launcher in
your browser. Rider handles its own JetBrains license or sign-in flow.
DevCapsule does not activate a trial or supply a license.

The `dotnet` capability also adds the SDK to another IDE. The pinned SDK
includes the runtime, MSBuild and targeting packs; use `dotnet build` and
`dotnet run` in the IDE's terminal. Additional workloads are not included.
SDK telemetry is disabled by default.

That terminal runs inside the capsule. Its tools and SDK are installed there;
your host's SDK, shell configuration and credentials are not imported.
NuGet packages and user tools live in the capsule's persistent home. IDE
settings and plugins also persist, with a separate namespace for each IDE.
See [what persists](../sessions/what-persists.md) and
[IDE preferences](../configuration/ide-preferences.md).
