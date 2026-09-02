# Bug: Codium Relaunch Intermittently Crashes Its First Renderer After A Clean Exit

Date opened: 2026-09-02

Status: root-caused and fixed on the branch, 2026-09-02. The owner ran
the recorded discriminating diagnostic: raw-passthrough `--shm-size`
of at least 512m stops the crashes entirely — candidate 1
(`/dev/shm` exhaustion) confirmed, candidate 2 (stale caches) not
implicated. The codium surface now declares
`shared-memory-size = "1g"` in its runtime configuration and the
launcher passes it through as `--shm-size` (validated, same
declaration pattern as the setuid-sandbox grant). The template change
advances the formation identity, so the next run re-materializes.
Closes on the owner seeing a run of clean relaunches without the
passthrough flag.

Requirements: R-PRODUCT-001

## Symptom

Roughly half the time (owner's estimate: more than 50%, less than 60%)
after exiting codium cleanly — which ends the container — the next
`project run` opens the IDE and a crash-report dialog appears within a
few seconds, offering a restart. The restart succeeds. Container log
tail before the dialog:

```
[127:…] ERROR:gpu/ipc/client/command_buffer_proxy_impl.cc:285] ContextResult::kTransientFailure: Failed to send GpuControl.CreateCommandBuffer.
[64:…]  ERROR:gpu/command_buffer/service/context_group.cc:146] ContextResult::kFatalFailure: WebGL2 blocklisted
[main …] Extension host with pid 171 exited with code: 0, signal: unknown.
[main …] CodeWindow: renderer process gone (reason: crashed, code: 133)
Error sending from webFrameMain: Error: Render frame was disposed before WebFrameMain could be accessed
```

(dbus `login1.Manager.Inhibit` / "Failed to connect to the bus" errors
also appear; a capsule has no session bus, so these are ambient noise
expected on every launch, crashing or not — to be confirmed by the
clean-launch comparison below.)

## Environment

- Formation: codium 1.126.04524 + antigravity-cli 1.1.24 on the
  v0.2.8 base; X11 bind-through; software GL forced by the launcher
  (`LIBGL_ALWAYS_SOFTWARE=1`, `MESA_LOADER_DRIVER_OVERRIDE=llvmpipe`,
  `LIBGL_DRI3_DISABLE=1`).
- The launcher passes no `--shm-size`, so the container runs with
  Docker's default 64 MB `/dev/shm`.
- Codium's durable `user-data` slot (`/ide-user-data`) persists
  Chromium's renderer caches (`GPUCache`, `Code Cache`) across
  container instances; the `cache` slot covers only `~/.cache`.

## Candidate Mechanisms (unconfirmed — discriminate before fixing)

Exit code 133 is SIGTRAP: a Chromium renderer aborting on an internal
CHECK, not an OOM kill. Two capsule-shaped candidates fit the
evidence; the dbus noise fits neither and is likely irrelevant.

1. **`/dev/shm` exhaustion at first paint.** 64 MB is the classic
   Chromium-in-Docker renderer killer, and llvmpipe makes it worse:
   software rendering pushes whole frames through shared memory, with
   allocation size depending on window and restore timing — matching
   intermittency and the crash landing seconds after the window opens.
   The `kTransientFailure` on `CreateCommandBuffer` is consistent with
   a GPU-process channel dying around the same allocation pressure.
2. **Stale persisted renderer caches.** `GPUCache`/`Code Cache` live in
   the *durable* user-data slot and outlive the container; Chromium
   invalidates them poorly across changed runtime environments. A
   corrupt/stale cache entry SIGTRAPs the renderer exactly once — the
   crash rewrites it — which matches "the restart always succeeds"
   suspiciously well. If confirmed, the state model has the deeper
   lesson: volatile caches are sitting in a durable slot.

## Discriminating Diagnostics (cheap, in order)

1. Capture the log of a *clean* launch and diff against the crashing
   one — establishes which ERROR lines are ambient (dbus, WebGL2
   blocklist) versus crash-correlated.
2. During a session, `df /dev/shm` and watch usage at window open; or
   relaunch with `--shm-size=1g` via raw docker passthrough — if the
   crash rate collapses, candidate 1.
3. Alternatively wipe `GPUCache`/`Code Cache`/`DawnCache` from the
   user-data slot source between runs — if the crash never reproduces
   from a clean cache, candidate 2.

## Fix Scope (after discrimination)

- Candidate 1: the launcher sizes `/dev/shm` explicitly for
  Chromium-family surfaces (`--shm-size`, on the declaration pattern
  the setuid-sandbox grant already uses).
- Candidate 2: route Chromium's volatile caches out of the durable
  user-data slot (cache-kind state or fresh-per-run), aligning the
  slot contents with their declared kinds.
- Either way the fix carries a regression observation: N consecutive
  relaunches without the crash dialog on the checkout that reproduces
  it.

## Reproducibility

Intermittent, ~50–60% of relaunches after a clean exit, on the owner's
workstation; always recovered by the offered restart.
