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
| `frontend-ide` | VSCodium | Node.js from the base |
| `dotnet-ide` | JetBrains Rider | .NET SDK selected automatically |

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
