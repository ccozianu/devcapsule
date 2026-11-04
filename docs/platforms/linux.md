---
description: What DevCapsule needs from a Linux computer, and which distributions and Docker setups are supported.
weight: 1
updated: 2026-11-04
---
# Linux

DevCapsule {{tag}} ships as a single executable for **64-bit Intel/AMD Linux
(`x86_64` / `linux-amd64`)**. You need:

- **Docker Engine with Buildx**, usable directly by your ordinary user account
  (never run `devcapsule` under `sudo`).
- **A modern web browser** to open the capsule's contained desktop and
  [web console](../sessions/web-console.md) on `127.0.0.1`.
- **`curl` and `sha256sum`** to download and verify the release executable,
  plus several gigabytes of free disk space for base and IDE image layers.

[Install](../getting-started/install.md) starts with three commands to check
the architecture, Docker daemon, and Buildx.
ARM Linux (`aarch64` / `linux-arm64`) has an experimental executable in {{tag}},
which the install command picks on an ARM computer. It has not been tried on an
ARM Linux host yet, and its capsules need an arm64 base you build yourself
until one is published, as [macOS](macos.md#run-a-project-natively-as-linux-arm64)
describes.

DevCapsule is developed and tested on Ubuntu-family desktops using Docker
Engine from [Docker's official repository](https://docs.docker.com/engine/install/).
Other current `x86_64` Linux distributions with a standard Docker Engine and
Buildx setup are expected to work without special flags; if yours hits a
platform-specific failure, please [open an issue](https://github.com/ccozianu/devcapsule/issues/new)
with your distribution, Docker version, and error output (omitting private
session URLs and tokens).
