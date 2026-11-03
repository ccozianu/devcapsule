# Workstream Current Status: macOS Launcher

Mnemonic: `macos-launcher`

Start date: 2026-11-03

State: active; registered 2026-11-03; slice 1, the capsule-platform split, in progress

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

## Next Resumable Task

Slice 1: separate the capsule platform, which keys locks and matrices, from the host
operating system, and pass `--platform linux/amd64` to Docker when they differ.

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
