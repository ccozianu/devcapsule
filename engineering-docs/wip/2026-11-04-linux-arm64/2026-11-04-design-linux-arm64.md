# Design: linux-arm64 Capsules

Workstream: `linux-arm64`. Written 2026-11-04 from two read-only surveys of the launcher and
the base recipe, on top of `macos-launcher`'s platform split. File references are to
`devcapsule-src/`.

## 1. What exists

- **Resolution is already per platform.** `MATRICES` (`resolution_matrix.py`) maps each
  `Platform` to one matrix of base pins, component pins, verified edges, capabilities and
  materialization recipes. Locks are `devcapsule.<platform>.lock`; a project may commit one
  per platform, and a checkout holds one version set.
- **The base recipe is arch-neutral.** `images/base.py` renders a Dockerfile from
  `ubuntu:24.04` and Ubuntu packages, which exist for arm64; Node and Temurin choose their
  archive by `dpkg --print-architecture`, and Temurin's arm64 digest is already pinned.
- **Discovery already speaks arm64.** `components/discovery.py` and `npm_channel.py` map
  `linux-arm64` for JetBrains, Eclipse, VSCodium, VS Code, Claude Code and npm packages.
- **What is amd64-only.** `Platform` has one member; every component pin is an amd64
  archive; Eclipse refuses other platforms (`components/eclipse.py`); Codex's npm alias map
  names only `linux-amd64` (`components/codex.py`); the JetBrains runtime check names
  `libskiko-linux-x64.so` (`assets/*/check-runtime-deps.sh`); `build-pex.sh` defaults to a
  `linux-x86_64` scie; the published base is a single-platform amd64 manifest.

## 2. Decisions taken by the human, 2026-11-04

1. Every component at once, not a first slice.
2. The arm64 base is built locally and approved per checkout; the owner publishes later.
3. On Apple Silicon, a project runs as `linux-arm64` when it has a `linux-arm64` lock, and
   otherwise as `linux-amd64` under emulation.
4. A new workstream on the macOS branch.

## 3. Design

1. **`Platform.LINUX_ARM64`.** The capsule platform a host can run, in preference order:
   `linux-amd64` hosts run amd64; `linux-arm64` hosts run arm64; Apple Silicon prefers arm64
   and can emulate amd64; Intel Macs run amd64. A project's platform is the first preferred
   platform it has a lock for; a project with no lock yet takes the first. Where callers now
   ask `Platform.current()` without a project, the design keeps one answer per process,
   chosen when the project is known; slice 1 settles the mechanism after reading the callers.
2. **The runtime.** An arm64 capsule needs a `linux-aarch64` executable. A launcher whose own
   binary runs on the capsule platform delivers itself (R-RUNTIME-001). Otherwise the user
   names the runtime: `DEVCAPSULE_RUNTIME_PEX` keeps naming one file, and a directory holding
   `devcapsule-linux-amd64` and `devcapsule-linux-arm64` serves both platforms from one
   setting.
3. **The base.** Built natively on this Mac by `devcapsule images build --type base`, and
   approved per checkout by the documented local-base path. Whether the `linux-arm64` matrix
   can resolve without a published base pin is slice 2's first question.
4. **Pins.** The same versions as the amd64 matrix, each with its arm64 archive's URL and a
   sha256 computed from the downloaded bytes, never copied from a page alone. Eclipse's
   native closure comes from `ports.ubuntu.com`. Playwright's Chromium has no
   Chrome-for-Testing arm64 build; its arm64 source is slice 3's open question, and
   `browser-automation` is unavailable on arm64 with a warning (R-CONFIG-001) if none passes.

## 4. Slices

1. **Second platform.** `LINUX_ARM64`, the per-project selection, the runtime directory, the
   `linux-aarch64` scie, the Eclipse, Codex and skiko hard-codes, tests. Done when the unit
   suite passes here and on Linux, and `project init` on this Mac writes an arm64 lock
   against a stub matrix.
2. **Base.** Build the arm64 base here; settle how the arm64 matrix and a local base meet.
3. **Pins.** Every component, by script: download, hash, record.
4. **Live and documentation.** `nox -s ide-smoke` for every surface natively on this Mac;
   the Linux, macOS and install pages.

## 5. What this does not decide

- Publishing an arm64 or multi-platform base, or arm64 release executables: the owner's.
- Whether ARM Linux becomes a supported release platform: the owner's.
