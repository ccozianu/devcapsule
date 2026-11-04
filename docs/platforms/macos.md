---
description: An experimental launcher runs on Apple Silicon Macs against Docker Desktop, with capsules emulated or native.
weight: 3
updated: 2026-11-04
---
# macOS

DevCapsule {{tag}} ships an experimental launcher for **Apple Silicon Macs**
(`darwin-arm64`), which runs natively against **Docker Desktop**. It is not a
supported platform in {{tag}}. There is no executable for Intel Macs.

A project runs as one of two capsule platforms:

- **`linux-arm64`, natively, the default.** Faster, but its base image is not
  published yet: you build it on your Mac once and select it for each checkout.
- **`linux-amd64`, under emulation.** The same environments Linux users get,
  with the published base, run by Docker Desktop under x86-64 emulation.

`devcapsule project init` asks which one a new project is for; Enter takes
`linux-arm64`, and `--platform PLATFORM` answers without the question. A
project runs as `linux-arm64` when it has a `linux-arm64` lock, and otherwise
as `linux-amd64`.

## What differs from Linux

- **Three executables.** On Linux the launcher copies itself into the
  capsule. A macOS executable cannot run there, so the launcher delivers the
  Linux runtime for the project's platform from `~/.local/lib/devcapsule`,
  where the install script puts one for each platform, or from the directory
  `DEVCAPSULE_RUNTIME_PEX` names instead. A launch refuses a runtime of
  another DevCapsule version, so install all three together.
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

## Install

You need Docker Desktop with several gigabytes free under **Settings →
Resources → Disk usage limit**, and about as much free on the Mac itself.
Install with the command on the [install page](../getting-started/install.md):

```bash
curl -fsSL {{download_url}}/install.sh | sh
```

It installs the launcher as `~/.local/bin/devcapsule` and the `linux-amd64`
and `linux-arm64` runtimes in `~/.local/lib/devcapsule`. If you set
`DEVCAPSULE_RUNTIME_PEX` for an earlier build, remove it from your shell
profile: it takes precedence over that directory. Add `$HOME/.local/bin` to
your `PATH`, then build the arm64 base below, or continue with [your first
session](../getting-started/first-session.md) and answer `linux-amd64` when
init asks for the platform.

### Build from source

To run a commit that is not released, you need Git and Python 3.12 as well.
From a clean checkout of a published commit:

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
build installs the web console from it. Install them where the launcher looks:

```bash
mkdir -p ~/.local/bin ~/.local/lib/devcapsule
install -m 0755 dist/devcapsule-macos-arm64 ~/.local/bin/devcapsule
install -m 0755 dist/devcapsule-linux-amd64 dist/devcapsule-linux-arm64 ~/.local/lib/devcapsule/
~/.local/bin/devcapsule version
```

Rebuild and reinstall all three together: the runtimes record no commit, so
one built from another commit of the same version is not told apart.

## Run a project natively as `linux-arm64`

Build the arm64 base once, natively, with the launcher you installed and the
revision it was built from, which `devcapsule version` shows:

```bash
revision="$(devcapsule version | sed -n 's/^Source revision: //p')"
devcapsule images build --type base --recipe ubuntu-24.04 --platform linux-arm64 \
  --tag devcapsule-base-local:arm64 --source-revision "$revision"
```

Then, in each project, create the arm64 lock, or add it beside an existing
`linux-amd64` one, and select your local base for the checkout:

```bash
devcapsule project init --platform linux-arm64 --authorize base-image default
devcapsule project config authorize base-image devcapsule-base-local:arm64
devcapsule project run
```

VSCodium, VS Code, Eclipse, PyCharm, IntelliJ IDEA and Rider have each started
natively on this base. A component no arm64 run has validated yet, such as the
.NET SDK or Playwright, needs `--unverified` on `init` or on the `config`
command that adds it; the command says so. The arm64 lock names a base that is
not published yet, so do not commit it to a shared repository: anyone without
a local arm64 base cannot run it. A change to the project's requirements made
on your Mac updates both locks.

To run the project under emulation again, delete
`.devcapsule/devcapsule.linux-arm64.lock` and select the project's base for
your checkout again with `devcapsule project config authorize base-image default`.

If something fails on your Mac, please [open an issue](https://github.com/ccozianu/devcapsule/issues/new)
with your macOS and Docker Desktop versions and the error output, omitting
private session URLs and tokens.
