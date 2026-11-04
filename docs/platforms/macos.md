---
description: DevCapsule ships no macOS executable; an experimental launcher built from source runs on Apple Silicon Macs against Docker Desktop, with capsules under emulation or, per project, natively as linux-arm64. What works, what differs, and how to build it.
weight: 3
updated: 2026-11-04
---
# macOS

DevCapsule {{tag}} ships no macOS executable. The release executable is for
64-bit Intel/AMD Linux and does not run on macOS.

The launcher in the source tree runs natively on **Apple Silicon Macs**
(`darwin-arm64`) against **Docker Desktop**, built by you. This is
experimental and not a supported platform in {{tag}}. Intel Macs are untested.

A project runs as one of two capsule platforms:

- **`linux-amd64`, the default.** The same environments Linux users get, run by
  Docker Desktop under x86-64 emulation. Every new project starts here.
- **`linux-arm64`, natively, per project.** Faster, but its base image is not
  published yet: you build it on your Mac and select it for each checkout.

A project runs as `linux-arm64` when it has a `linux-arm64` lock, and
otherwise as `linux-amd64`. `devcapsule project --platform PLATFORM ...` names
one for a single command.

## What differs from Linux

- **Two executables, or three.** On Linux the launcher copies itself into the
  capsule. A macOS executable cannot run there, so you build the Linux runtime
  for each capsule platform you use and put them in one directory that
  `DEVCAPSULE_RUNTIME_PEX` names. Each launch delivers the one for its
  project's platform and refuses a runtime from another build, so rebuild
  them whenever you rebuild the launcher.
- **Emulation.** Under `linux-amd64`, the first launch of an IDE builds its
  image under emulation: about ten minutes for PyCharm on a 14-core Mac. Later
  launches reuse the image. The IDE runs slower than on a native host.
- **Networking.** Docker Desktop's host network belongs to its virtual machine,
  out of your Mac's reach. A project authorized for `network host` launches on
  bridge networking instead, with a warning. The contained desktop and the
  [web console](../sessions/web-console.md) are published to `127.0.0.1` as on
  Linux, and the capsule reaches services on your Mac as `host.docker.internal`.
- **No host-browser bridge.** Docker Desktop cannot share a Mac socket with a
  container, so links the IDE opens cannot reach your Mac's browser. The launch
  warns and continues. The contained desktop still opens in your browser.
- **Docker inside the capsule.** With `docker-daemon` authorized, the capsule's
  Docker client reaches Docker Desktop's daemon, whose engine is `arm64` on
  either capsule platform: an image you run from inside the capsule is the ARM
  variant unless you pass `--platform linux/amd64`.
- **File sharing.** Keep projects under a directory Docker Desktop shares, by
  default `/Users`, `/Volumes`, `/private`, `/tmp` and `/var/folders`. Files the
  capsule writes there belong to your user.

## Build and install

You need Docker Desktop with several gigabytes free under **Settings →
Resources → Disk usage limit**, and about as much free on the Mac itself, plus
Git and Python 3.12. From a clean checkout of a published commit:

```bash
git clone https://github.com/ccozianu/devcapsule.git
cd devcapsule/devcapsule-src
python3.12 -m venv .venv
.venv/bin/pip install -r dev-requirements.txt
.venv/bin/pip install -e . --no-deps
revision="$(git rev-parse HEAD)"
DEVCAPSULE_SCIE_PLATFORM=macos-aarch64 PYTHON=.venv/bin/python \
  scripts/build-pex.sh --source-revision "$revision" --allow-unpublished-revision \
  --output dist/devcapsule-macos-arm64
for target in amd64:linux-x86_64 arm64:linux-aarch64; do
  git -C .. archive HEAD | docker run --rm -i --platform "linux/${target%%:*}" \
    -v "$PWD/dist:/out" python:3.12-slim sh -c "
      mkdir /build && tar -x -C /build && cd /build/devcapsule-src &&
      python -m venv /venv && /venv/bin/pip install -q -r dev-requirements.txt &&
      /venv/bin/pip install -q -e . --no-deps &&
      DEVCAPSULE_SCIE_PLATFORM=${target#*:} PYTHON=/venv/bin/python scripts/build-pex.sh \
        --allow-local-source --output /out/devcapsule-linux-${target%%:*}"
done
```

This writes the macOS launcher and a Linux runtime for each capsule platform,
all from the same commit. `--allow-unpublished-revision` skips only the check
that the commit is a branch tip; the commit itself must be public, since a base
build installs the web console from it. Install them:

```bash
mkdir -p ~/.local/bin ~/.local/lib/devcapsule
install -m 0755 dist/devcapsule-macos-arm64 ~/.local/bin/devcapsule
install -m 0755 dist/devcapsule-linux-amd64 dist/devcapsule-linux-arm64 ~/.local/lib/devcapsule/
export DEVCAPSULE_RUNTIME_PEX="$HOME/.local/lib/devcapsule"
~/.local/bin/devcapsule version
```

Add the `export` line, and `$HOME/.local/bin` on your `PATH`, to your shell
profile. Then continue with [your first session](../getting-started/first-session.md);
its projects run as `linux-amd64`.

## Run a project natively as linux-arm64

Build the arm64 base once, natively, with the launcher you installed and the
revision it was built from (`devcapsule version` shows it):

```bash
devcapsule images build --type base --recipe ubuntu-24.04 --platform linux-arm64 \
  --tag devcapsule-base-local:arm64 --source-revision "$revision"
```

Then, in each project, add the arm64 lock and select your local base for the
checkout:

```bash
devcapsule project --platform linux-arm64 init --unverified --authorize base-image default
devcapsule project config authorize base-image devcapsule-base-local:arm64
devcapsule project run
```

`--unverified` is needed while no arm64 combination of IDE and base has
recorded validation evidence; init says so. The arm64 lock names a base that is
not published yet, so do not commit it to a shared repository: anyone without
a local arm64 base cannot run it. To run the project under emulation again for
one launch, use `devcapsule project --platform linux-amd64 run`.

If something fails on your Mac, please [open an issue](https://github.com/ccozianu/devcapsule/issues/new)
with your macOS and Docker Desktop versions and the error output, omitting
private session URLs and tokens.
