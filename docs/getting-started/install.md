---
description: Check your computer, download the DevCapsule executable for this version, verify its checksum and install it in your own home directory.
weight: 1
updated: 2026-09-28
---
# Install DevCapsule

DevCapsule is one executable for **Linux, Intel/AMD 64-bit**. It needs a web
browser and Docker running on the same computer. It does not run natively on
macOS, on Windows, or on ARM. **On Windows, read
[Windows via WSL2](../platforms/windows-wsl2.md) before installing** and run
every command below in your Linux terminal.

## Check your computer

In a terminal:

```bash
uname -sm
docker info
docker buildx version
```

Expect `Linux x86_64`, Docker server information, and a Buildx version. If
Docker is missing or reports a connection or permission error, complete
[Docker's installation instructions](https://docs.docker.com/engine/install/)
first. Docker must work as your ordinary user; never run DevCapsule with
`sudo`.

You also need `curl` and `sha256sum`. The first launch downloads a base image
and an IDE: allow several GB of disk space and some minutes. Later launches
reuse them.

## Download, verify, install

Paste this block into the same terminal. It checks the download against its
published checksum before installing the executable in your own
`~/.local/bin`:

```bash
(
  set -eu
  download_dir="$(mktemp -d)"
  cd "$download_dir"
  release_url="{{download_url}}"
  curl --fail --location --output devcapsule.pex "$release_url/devcapsule.pex"
  curl --fail --location --output devcapsule.pex.sha256 "$release_url/devcapsule.pex.sha256"
  sha256sum --check devcapsule.pex.sha256
  mkdir -p "$HOME/.local/bin"
  install -m 0755 devcapsule.pex "$HOME/.local/bin/devcapsule"
)
```

You should see `devcapsule.pex: OK`. If the block reports an error, stop and
retry the failed download; do not continue with an unverified file.

```bash
~/.local/bin/devcapsule version
```

Expect `{{tag}}`. The guides use the full path `~/.local/bin/devcapsule` so
they work even when `~/.local/bin` is not on your shell's search path. No
Python, pip, or source checkout is needed. The release page for this version
is [{{tag}}]({{release_url}}).

**Next: [your first session](first-session.md).**
