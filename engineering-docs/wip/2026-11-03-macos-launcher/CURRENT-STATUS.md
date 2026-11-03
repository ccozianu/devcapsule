# Workstream Current Status: macOS Launcher

Mnemonic: `macos-launcher`

Start date: 2026-11-03

State: active; slices 1 and 2 and the slice-3 fixes committed 2026-11-03; the live launch waits on the human's Docker disk decision

Branch association: `ws-macos-launcher/host-port`, forked from local `main` at b3f10b7d

Integration target: `main`

Delivery method: pull request, merge commit; the human opens and merges it

Requirements: R-PRODUCT-002 (host boundaries stay explicit on the new host); R-CONFIG-001

## Goal And Scope

Run the DevCapsule launcher natively on an Apple Silicon Mac (`darwin-arm64`) against
Docker Desktop, with capsules running as `linux-amd64` under Docker's x86 emulation.

In scope: the launcher on macOS, the existing `linux-amd64` lock, pins and base image used
unchanged, the host-side mechanisms that assume Linux, a `macos-aarch64` executable, and the
macOS platform page.

Out of scope, by the human's direction of 2026-11-03 ("do stage 2 no need for stage 1"):
`linux-arm64` capsules, their resolution matrix, pins and base image. Native-speed
capsules on Apple Silicon need that work later; this workstream leaves room for it.

## Current State

**2026-11-03, opened.** The human asked whether DevCapsule builds for ARM, then for native
macOS on Apple Silicon, and directed the macOS host port without ARM capsules. Evidence on
the human's Mac (macOS 27.0, arm64, Docker Desktop 29.3.1, `desktop-linux` context at
`~/.docker/run/docker.sock`, 14 CPUs, 47 GiB):

- `docker run --platform linux/amd64 ubuntu:24.04 uname -m` prints `x86_64`: emulation works.
- The locked base `devcapsule-base@sha256:8c97d308…` is a single-platform manifest.
- The development CLI runs (`version --json` answers), and every project command stops at
  `Unsupported platform 'darwin-arm64'; supported platforms: linux-amd64.`

The work plan, one slice each, is in the
[design note](2026-11-03-design-macos-host-port.md).

**2026-11-03, slices 1 and 2.** `Platform.current()` now means the platform this host runs
capsules as (`linux-amd64` on a Mac), with `HostOs` for host mechanisms. Every `docker run`,
buildx build and base pull carries `--platform linux/amd64` when the host emulates it, and a
native Linux launch composes the same command as before. A launcher whose own binary cannot
run in the capsule delivers `DEVCAPSULE_RUNTIME_PEX` instead, or refuses with that remedy.
The host-browser bridge is unavailable on macOS with a warning; its peer check reads
`LOCAL_PEERCRED`, and two macOS socket races in its protocol are fixed (an early rejection
closed with unread input; `shutdown` after the broker closed). The capsule user joins group 0
for Docker Desktop's socket. `project config show` answers on this Mac.

Validation on this Mac: the unit suite, 2,725 passed, 19 skipped (the container-side
supervisor and the X11-dependent recursive dogfood, by marker), from 411 failed and 461 errors
before; the host-open module 20 runs clean; `mypy --platform linux` clean over 269 files. `nox`
cannot run its sessions here, having no `python3.12` on `PATH`, so the commands were run from
`.venv` directly. The unit suite on Linux is still to run, inside an amd64 container.

**2026-11-03, slice 3 so far.** Host networking falls back to bridge on macOS with a warning:
under `--network host` the contained desktop and console would listen on the VM's loopback,
out of the Mac's reach. The unit suite pins the host OS to Linux by default, as it pins the
host-not-container default, and the macOS tests opt in; `real_host_os` opts a test out.

Both executables exist: `devcapsule-src/dist/devcapsule-macos-arm64`, built natively, and the
`linux-x86_64` runtime, built in an amd64 container from an export of 062782bf. In that
container the unit suite ran on Linux: 2,738 passed, 1 failed,
`test_recursive_host.py::test_staging_cleans_up_after_preparation_failure`, which expects a
`chmod 0500` directory to refuse a write and runs as root there; not caused by this change.
On this Mac after the fallback: 2,727 passed, 19 skipped; `mypy --platform linux` clean.

The live launch is not run. Docker Desktop's disk has 5.9 GB free and eight of the human's
containers are running; the base (0.89 GB compressed) and a PyCharm formation would likely
fill it. The decision is the human's.

## Next Resumable Task

Slice 3, the live launch, once the human has made Docker disk room:
`DEVCAPSULE_PEX_UNDER_TEST=devcapsule-src/dist/devcapsule-macos-arm64`,
`DEVCAPSULE_RUNTIME_PEX=<the linux-x86_64 runtime>`, `PATH` with a `python3.12`, then
`.venv/bin/python -m nox -s ide-smoke -- --surface pycharm`, and record what it shows. The
smoke initializes with `--authorize network host`, which now falls back to bridge on macOS.

## Open Threads

- The SSH agent on this Mac holds no identity, so `git fetch`, `workflow claim` and
  `workflow publish` fail with `Permission denied (publickey)`. The human loads the key;
  until then the registration is local only and `main` could not be re-verified.
- No `python3.12` exists on this Mac. `.venv` was created with `uv venv --python 3.12`
  (CPython 3.12.12) instead of `python3.12 -m venv`; the executable still embeds 3.12.14.
- Adding a supported host platform is a product commitment. The repository owner has not
  yet ruled on it; the human started the work.

## Document Index

- [2026-11-03-design-macos-host-port.md](2026-11-03-design-macos-host-port.md): the host
  assumptions found, the design of the platform split, and the slice plan. Open before
  each slice.
