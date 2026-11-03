# Design: The Launcher On macOS

Workstream: `macos-launcher`. Written 2026-11-03 from a read of the launcher and probes on
an Apple Silicon Mac with Docker Desktop 29.3.1. Statements marked *to verify* are read from
code or recalled Docker Desktop behaviour, not yet observed on this host.

## 1. The two platforms

Today one value plays two roles. `Platform.current()` (`devcapsule/platforms.py`) derives a
key from the host's `system` and `machine`, and every caller uses it to name and select the
platform lock and the resolution matrix:

- `configuration/storage.py`: the lock path `devcapsule.<platform>.lock`, and the refusal of a
  version set recorded for another platform;
- `configuration/derivation.py`, `configuration/operations.py`,
  `configuration/owner_commands.py`, `version_sets.py`: `MATRICES[Platform.current()]`.

None of those callers asks about the host. They ask which platform the capsules run as. On
Linux the two coincide. On a Mac the host is `darwin-arm64` and the capsules are Linux.

Design:

1. `Platform` keeps its meaning, the wire format of a lock: a capsule platform. Its members
   stay append-only; no `darwin-*` member is added, because no lock is ever for macOS.
2. `Platform.current()` keeps its name and its callers, and its contract becomes *the
   platform this host runs capsules as*. On Linux it is the host's own platform, as now. On
   macOS it is `linux-amd64` on both architectures: Intel natively, Apple Silicon under
   Docker's emulation. When `linux-arm64` exists, Apple Silicon maps to it and emulation
   becomes the fallback, not the rule. The mapping lives in `platforms.py` alone.
3. A new `HostOs` (`linux`, `darwin`) names the host's operating system for the host-side
   mechanisms of section 2. Feature code asks `HostOs.current()`, never `sys.platform`.
4. `Platform.docker_platform` gives Docker's spelling (`linux/amd64`), and
   `Platform.emulated()` says whether this host's CPU differs from the capsule platform's.
   When it does, every `docker run` and every buildx build the launcher composes carries
   `--platform`, so that Docker does not pick the host's architecture for a multi-platform
   image or warn on a single-platform one.

Rejected: renaming `current()` to `for_capsules()`. The name is accurate once the contract is
written down, and the rename touches 27 call and test sites for no behaviour.

## 2. Host mechanisms that assume Linux

Found by reading the launch path from `run_pycharm` (`launch/pycharm/_launcher.py`) outward.

| Mechanism | Where | On macOS | Plan |
|---|---|---|---|
| Lock and matrix key | section 1 | refuses `darwin-arm64` | slice 1 |
| Docker `--platform` | `_launcher.py` `docker run`; `images/build.py` buildx | Docker picks arm64 or warns | slice 1 |
| Host-browser bridge | `host_open.py` | peer check used `SO_PEERCRED`, Linux only; the broker socket is a host Unix socket bind-mounted into the capsule, which Docker Desktop refuses (section 2.1) | slice 2: unavailable on macOS with a warning, per R-CONFIG-001; the peer check also reads macOS `LOCAL_PEERCRED`; a TCP transport is a later decision. The contained desktop's own opener is Python's `webbrowser`, which already uses `open` |
| Host Docker socket | `_launcher.py` `host_docker_socket`, `write_user_files` | both socket paths bind; `--group-add` took the host file's gid (`staff`), but the socket is `0:0 0660` inside (section 2.1) | slice 3: on macOS the capsule user joins group 0; the capsule already holds the daemon, root on the VM, so the root group adds no authority beyond it |
| Container identity | `current_host_user`, `write_user_files` | 501:20; the generated `/etc/group` avoids the image's `dialout`; ownership round-trips (section 2.1) | none found; re-check in the live launch |
| Container detection | `host_daemon.py` | a marker file, not `/proc`; already correct (section 2.1) | none |
| Runtime artifact | `runtime_artifact.py` | the launcher delivers its own executable into the capsule; a macOS binary cannot run there | slice 1: deliver `DEVCAPSULE_RUNTIME_PEX` when the launcher's own binary is foreign, refuse with the remedy otherwise; how a release ships the Linux runtime beside the macOS launcher is slice 4 |
| Executable | `scripts/build-pex.sh` | `DEVCAPSULE_SCIE_PLATFORM=macos-aarch64` | slice 4 |
| Ports | `--publish 127.0.0.1:<port>` | Docker Desktop forwards loopback publishes (*to verify*) | slice 3, by a live launch |
| Project's host networking rule | `WORKFLOW-LOCAL.md` *Local Launch Networking* | Docker Desktop's host networking is an opt-in setting (*to verify*) | record the fallback when a launch needs it |

### 2.1 Observed on this Mac, 2026-11-03

Docker Desktop 29.3.1, macOS 27.0, arm64, `desktop-linux` context.

- **Host Unix sockets.** A host socket as a bind source fails with `invalid mount config for
  type "bind": bind source path does not exist: /socket_mnt/<host path>`, for a socket in the
  session scratch, in `$TMPDIR` (`/var/folders/…/T/devcapsule-host-open.*/broker.sock`, where
  the broker would bind it, 90 bytes) and in `~/.cache`. Docker Desktop rewrites the source to
  `/socket_mnt/…` and does not find it. The host-browser bridge cannot reach a capsule.
- **The Docker socket** is the exception: `/var/run/docker.sock` on the Mac is a symlink to
  `~/.docker/run/docker.sock`, and binding either path gives the capsule a socket owned
  `0:0`, mode `0660`. The host file's group means nothing inside.
- **Ownership.** A capsule process running as `501:20` writes files that the Mac shows as
  owned by uid 501; the group is the parent directory's, as macOS assigns it.
- **Identity.** The launcher writes the capsule's `/etc/passwd` and `/etc/group` whole, so the
  host's `staff` (20) does not collide with the image's `dialout` (20).
- **`/proc`.** `host_daemon.in_container()` tests a marker file; nothing on the host path reads
  `/proc`. The row above is void.
- **Test suite.** Before slice 1: 411 failed and 461 errors of 2,743. After the platform
  split: 30 failed and 24 errors, in four groups: the supervisor (container-side,
  `signal.sigwaitinfo` is Linux only); Unix socket paths beyond macOS's 104 bytes under the
  per-user temporary directory; the recursive dogfood, which validates a host X11 socket
  directory; the host-browser bridge.

## 3. Slices

1. **Capsule platform.** Section 1, `--platform` on run and build, `/proc` absence. Done when
   `project config show` and `project run --print-command` answer on this Mac, and the unit
   tests pass here and keep passing on Linux.
2. **Browser bridge.** Unavailable-with-warning on macOS; `open` as the opener for when a
   transport exists.
3. **Live launch.** A real `project run` of this repository on this Mac: Docker socket,
   identity, ownership of written files, ports, the contained desktop in a Mac browser.
   Findings decide the code; this slice is mostly evidence.
4. **Executable and documentation.** A `macos-aarch64` scie, smoke-tested here; the macOS
   platform page and the install page rewritten for what works; release automation is the
   owner's call.

## 4. What this does not decide

- Whether macOS becomes a *supported* platform in a release. That is the owner's ruling;
  this workstream produces the evidence for it.
- Signing and notarization of a macOS executable.
- `linux-arm64` capsules.
