---
description: What DevCapsule needs from a Linux computer, and the distributions and Docker setups it has been used on.
weight: 1
updated: 2026-09-28
---
# Linux

DevCapsule ships as a Linux, Intel/AMD 64-bit executable and needs Docker
Engine with Buildx, working as your ordinary user, and a web browser. That
is the whole requirement; [Install](../getting-started/install.md) checks it
in three commands. ARM Linux is not covered by this release.

The project is developed and released on Ubuntu-family desktops with Docker
Engine from Docker's own repository. Other distributions with a current
Docker Engine are expected to work and are not individually verified; if
yours does not, [an issue](https://github.com/ccozianu/devcapsule/issues/new)
with the distribution and the error is welcome.
