---
description: DevCapsule does not run on macOS yet; what is missing and what would change that.
weight: 3
updated: 2026-09-28
---
# macOS

Not yet. The executable is Linux-only and the launcher assumes a Linux
Docker host with the project folder on the same filesystem. A macOS port
needs a native executable, Docker Desktop's file sharing and networking
verified end to end, and a browser desktop that behaves the same. None of
that has been started; it is the largest untested platform, and the project
says so rather than guessing.
