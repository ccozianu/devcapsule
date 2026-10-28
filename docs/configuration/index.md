---
description: The project, checkout and home records that define a DevCapsule launch.
weight: 1
updated: 2026-10-28
---
# Configuration

A DevCapsule configuration describes what a project needs and how you want
to work on it. The configuration lives in three places.

The project's **manifest**, `.devcapsule/devcapsule.toml`, declares required
and offered capabilities, environment inputs, and recommendations. A
capability names something the environment supplies, such as a Java runtime
or browser automation. A component supplies that capability. The **platform
lock** pins the base image and component versions. Both files travel in Git.

Your **checkout record** stays on your computer. It holds your IDE choice,
added and omitted capabilities, provider choices, and host-access answers.
It also holds your local component pins. A second checkout has its own record.

Your **configuration home** holds `settings.toml`, with default resource
limits and the vendor channels you trust. These apply across projects
launched from that home.
Trust permits acquisition through a channel; it grants no host access.

`devcapsule project run` reads these records and derives the launch each
time. Your checkout choices override recommendations. A required capability
still has to be present and meet its minimum version. The launcher asks for
missing decisions before it starts the container. The IDE owns the
container's lifetime and can use the capsule's display.

## Details

- [The configuration home](home.md): select its directory and inspect its settings.

- [Project versus personal](project-versus-personal.md): where each choice lives.
- [Capabilities](capabilities.md): requirements, minimums, resolutions and your choices.
- [Inspect configuration](inspect.md): see the next launch and pending decisions.
- [Vendor software and trust](software-approvals.md): accept or withdraw a channel.
- [Configuration nodes](../reference/configuration-nodes.md): values, access and bindings.
