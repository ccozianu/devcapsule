# Workstream Current Status: linux-arm64 Capsules

Mnemonic: `linux-arm64`

Start date: 2026-11-04

State: active; registered 2026-11-04; slice 1, the second capsule platform, next

Branch association: `ws-linux-arm64/capsules`, forked from local `main` at b3f10b7d, with
`ws-macos-launcher/host-port` merged in as its foundation

Integration target: `main`, after `macos-launcher`'s pull request

Delivery method: pull request, merge commit; the human opens and merges it

Requirements: R-RUNTIME-001 (the runtime delivered matches the capsule); R-COMPAT-001
(projects locked for `linux-amd64` keep working); R-CONFIG-001

## Goal And Scope

Run capsules as `linux-arm64` as well as `linux-amd64`: natively on Apple Silicon Macs
through the `macos-launcher` work, and on ARM Linux hosts.

In scope, by the human's answers of 2026-11-04:

- every component the `linux-amd64` matrix offers, pinned for `linux-arm64` in one
  workstream: PyCharm, IntelliJ IDEA, Rider and the .NET SDK, Eclipse and its native
  package closure, VSCodium, VS Code, the Codex, Claude Code and Antigravity CLIs, and
  Playwright;
- an arm64 base image built locally from the existing recipe and approved per checkout as a
  local base; publishing it, and pinning its digest, is the owner's;
- on an Apple Silicon Mac, a project runs as `linux-arm64` when it has a `linux-arm64` lock,
  and otherwise as `linux-amd64` under emulation, as today;
- a `linux-aarch64` runtime executable for arm64 capsules.

Out of scope: publishing images or executables; release automation.

## Current State

**2026-11-04, opened.** The human, running capsules on the Mac under emulation, directed
native ARM capsules: "ok we need linux arm64", then answered four questions: everything at
once; build the base locally now; arm64 when locked, else amd64; a new workstream built on
the macOS branch. Two read-only surveys mapped the work; the plan is in the
[design note](2026-11-04-design-linux-arm64.md).

## Next Resumable Task

Slice 1 of the design note: the second capsule platform.

## Open Threads

- The SSH agent on this Mac holds no identity, so the workstream cannot be published or
  pushed; registration is local, as is `macos-launcher`'s.
- This branch builds on `ws-macos-launcher/host-port`, which is not yet on `main`. The
  registration commit is forked from `main` as topic 7.5 requires, and the macOS branch is
  merged after it; this pull request follows that one.
- An arm64 base on `docker.io/mycodespaceai`, and its digest in the matrix, need the owner.

## Document Index

- [2026-11-04-design-linux-arm64.md](2026-11-04-design-linux-arm64.md): what the second
  platform needs, the decisions, and the slices. Open before each slice.
