---
description: Why DevCapsule does not run on macOS yet, and what a native macOS port would require.
weight: 3
updated: 2026-10-30
---
# macOS

DevCapsule {{tag}} does not run on macOS (`darwin-arm64` or `darwin-amd64`).

Today, both the release executable and the locked component catalog target
`linux-amd64` only, and the launcher expects a Linux Docker host sharing a
native Linux filesystem with the checkout. Supporting macOS properly will
require:

- Native macOS launcher builds and `linux-arm64` / `linux-amd64` container
  resolution rules for Apple Silicon and Intel Macs.
- End-to-end verification of Docker Desktop (or Lima/Colima) bind-mount
  semantics, permissions, and loopback port forwarding.
- Contained-desktop and [web console](../sessions/web-console.md) validation in
  macOS browsers.

None of that work is in {{tag}}; when macOS support begins, the supported
platforms in `.devcapsule/devcapsule.<platform>.lock` and [Install](../getting-started/install.md)
will announce it explicitly.
