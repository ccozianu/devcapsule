---
description: Check prerequisites, then install DevCapsule with one command that downloads the executable for your computer, verifies its SHA-256 checksum, and installs it under ~/.local/bin.
weight: 1
updated: 2026-11-04
---
# Install DevCapsule

DevCapsule ships as a single executable for **Linux (`x86_64` / Intel-AMD
64-bit)**, with experimental executables for **Apple Silicon Macs** and **ARM
Linux (`aarch64`)**. It requires a web browser and a working Docker daemon on
the same machine. **On Windows, read [Windows via WSL2](../platforms/windows-wsl2.md)
first** and run every command below inside your WSL2 Linux terminal. **On a
Mac, read [macOS](../platforms/macos.md) first**: it runs against Docker
Desktop, and what differs from Linux is listed there.

## Check your computer

In a terminal:

```bash
uname -sm
docker info
docker buildx version
```

Expect `Linux x86_64` (or `Darwin arm64` on a Mac, `Linux aarch64` on ARM
Linux), Docker server details, and a Buildx version. If Docker is missing or
prints a connection or permission error, complete [Docker Engine
installation](https://docs.docker.com/engine/install/) first, or Docker
Desktop on a Mac. Docker must work for your ordinary user account—never run
`devcapsule` with `sudo`.

You also need `curl`, and `sha256sum` or `shasum`. Allow several gigabytes of
free disk space for the base image and IDE on your first launch; subsequent
launches reuse those cached layers.

## Install

Paste this into your terminal:

```bash
curl -fsSL {{download_url}}/install.sh | sh
```

The script downloads the release's executable for your computer and the
release's `SHA256SUMS`, checks the executable against it, and installs it as
`~/.local/bin/devcapsule`. On a Mac it also installs the Linux executables your
capsules run, in `~/.local/lib/devcapsule`, where the launcher finds them. If a
checksum does not match, the script stops and installs nothing: run it again,
and never install an unverified binary. It ends by printing the installed
version.

To read the script before it runs, download it first:

```bash
curl -fsSLO {{download_url}}/install.sh
less install.sh
sh install.sh
```

On Linux `x86_64` you can also install by hand. This is the same download and
check the script makes:

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

Check the installed version:

```bash
~/.local/bin/devcapsule version
```

Expect `{{tag}}` (release notes: [{{tag}}]({{release_url}})). The release
executable includes its own Python runtime. You do not need host Python, a
virtual environment, `pip`, or a source checkout.

The onboarding walkthroughs spell out `~/.local/bin/devcapsule` so they work
immediately even before `~/.local/bin` is on your shell's `PATH`. Add
`$HOME/.local/bin` to `PATH` in your shell profile (`export
PATH="$HOME/.local/bin:$PATH"`) to run `devcapsule` directly as shown in the
rest of the documentation.

**Next: [your first session](first-session.md).**
