---
description: DevCapsule ships no macOS executable; an experimental launcher built from source runs on Apple Silicon Macs against Docker Desktop. What works, what differs, and how to build it.
weight: 3
updated: 2026-11-03
---
# macOS

DevCapsule {{tag}} ships no macOS executable. The release executable is for
64-bit Intel/AMD Linux and does not run on macOS.

The launcher in the source tree runs natively on **Apple Silicon Macs**
(`darwin-arm64`) against **Docker Desktop**, built by you. This is
experimental and not a supported platform in {{tag}}. Capsules stay the same
`linux-amd64` environments Linux users get, run by Docker Desktop under x86-64
emulation. Intel Macs are untested.

## What differs from Linux

- **Two executables.** On Linux the launcher copies itself into the capsule. A
  macOS executable cannot run there, so you build a Linux runtime beside it and
  name it in `DEVCAPSULE_RUNTIME_PEX`. The launcher delivers that file instead,
  and stops with that remedy when the variable is unset. Build both from the
  same commit.
- **Emulation.** The first launch of an IDE builds its image under emulation:
  about ten minutes for PyCharm on a 14-core Mac. Later launches reuse the
  image and start in seconds. The IDE itself runs slower than on a native host.
- **Networking.** Docker Desktop's host network belongs to its virtual machine,
  out of your Mac's reach. A project authorized for `network host` launches on
  bridge networking instead, with a warning. The contained desktop and the
  [web console](../sessions/web-console.md) are published to `127.0.0.1` as on
  Linux, and the capsule reaches services on your Mac as `host.docker.internal`.
- **No host-browser bridge.** Docker Desktop cannot share a Mac socket with a
  container, so links the IDE opens cannot reach your Mac's browser. The launch
  warns and continues. The contained desktop still opens in your browser.
- **Docker inside the capsule.** With `docker-daemon` authorized, the capsule's
  Docker client reaches Docker Desktop's daemon, whose engine is `arm64`: an
  image you run from inside the capsule is the ARM variant unless you pass
  `--platform linux/amd64`.
- **File sharing.** Keep projects under a directory Docker Desktop shares, by
  default `/Users`, `/Volumes`, `/private`, `/tmp` and `/var/folders`. Files the
  capsule writes there belong to your user.

## Build and install

You need Docker Desktop with several gigabytes free under **Settings →
Resources → Disk usage limit**, Git, and Python 3.12. From a clean checkout:

```bash
git clone https://github.com/ccozianu/devcapsule.git
cd devcapsule/devcapsule-src
python3.12 -m venv .venv
.venv/bin/pip install -r dev-requirements.txt
.venv/bin/pip install -e . --no-deps
DEVCAPSULE_SCIE_PLATFORM=macos-aarch64 PYTHON=.venv/bin/python \
  scripts/build-pex.sh --allow-local-source --output dist/devcapsule-macos-arm64
git -C .. archive HEAD | docker run --rm -i --platform linux/amd64 \
  -v "$PWD/dist:/out" python:3.12-slim sh -c '
    mkdir /build && tar -x -C /build && cd /build/devcapsule-src &&
    python -m venv /venv && /venv/bin/pip install -q -r dev-requirements.txt &&
    /venv/bin/pip install -q -e . --no-deps &&
    PYTHON=/venv/bin/python scripts/build-pex.sh --allow-local-source \
      --output /out/devcapsule-linux-amd64'
```

The first build writes the macOS launcher. The second builds the Linux runtime
from the same commit inside an emulated Linux container. Install both:

```bash
mkdir -p ~/.local/bin ~/.local/lib/devcapsule
install -m 0755 dist/devcapsule-macos-arm64 ~/.local/bin/devcapsule
install -m 0755 dist/devcapsule-linux-amd64 ~/.local/lib/devcapsule/
export DEVCAPSULE_RUNTIME_PEX="$HOME/.local/lib/devcapsule/devcapsule-linux-amd64"
~/.local/bin/devcapsule version
```

Add the `export` line, and `$HOME/.local/bin` on your `PATH`, to your shell
profile. Then continue with [your first session](../getting-started/first-session.md).

If something fails on your Mac, please [open an issue](https://github.com/ccozianu/devcapsule/issues/new)
with your macOS and Docker Desktop versions and the error output, omitting
private session URLs and tokens.
