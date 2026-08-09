# Bug: Concurrent Projects Sharing Global Settings Bail On Lock

Date opened: 2026-06-24

Status: closed as documented PyCharm/IDEA-family limitation

Requirements:

- R-CONC-001
- R-STATE-001
- R-PROJECT-001

## Symptom

Two different projects cannot currently run concurrently when both launched
PyCharm containers share the same IDE global settings directory. Part of the
global state includes a lock file or equivalent single-instance guard, and the
second IDE launch bails out instead of opening independently.

## Environment

- Image: current manually tested image after the 2026-06-24 Python-project UX changes, exact tag to record during validation
- Launcher command: default `run-pycharm-container.sh` shape with shared `--global-settings`; exact command to record during validation
- Project path/mount: two different host projects with distinct default `/workspace/<project-id>` mounts
- Host assumptions: same user, same shared global settings root, X11 launcher
- Relevant package/app versions: PyCharm version and image tag still to record

## Reproduction

Manual steps:

1. Launch PyCharm for project A with the default shared global settings root, or an explicit shared `--global-settings DIR`.
2. Leave the first PyCharm instance running.
3. Launch PyCharm for project B with the same shared global settings root, while keeping the default per-project state and per-project mount behavior.
4. Observe the second launch.

Expected:

Both IDE windows either open concurrently with isolated lock-bearing runtime
state, or the launcher fails before Docker startup with a clear explanation and
a suggested workaround.

Original actual:

The second IDE bails out because the shared global settings state contains a
lock file or equivalent single-instance guard.

Reproducibility: reproduced during manual testing; follow-up validation of the
launcher fix was completed at repository level, and the user accepted the
remaining shared-config concurrency behavior as a documented limitation.

## Evidence

Initial evidence is the user's manual report on 2026-06-24, plus the stack
trace below showing JetBrains locking `/ide-global-settings/config/.lock`.
Capture exact stderr/stdout and PyCharm log lines again only if this issue is
reopened.

Do not include secrets.

## Hypothesis

The stack trace identifies the locked path as JetBrains `idea.config.path`, not
the per-project system/log path:

```text
Cannot lock config directory /ide-global-settings/config
FileAlreadyExistsException: /ide-global-settings/config/.lock
```

JetBrains config directories are therefore single-live-process runtime
directories. They are useful for settings continuity, but not safe as a shared
concurrent config path across separate Docker containers. The attempted
DirectoryLock activation also cannot be relied on because the first IDE process
is inside another container namespace and only has the first project mounted.

Project requirement interpretation:

- Shared user preference intent remains required: one user should be able to
  carry common PyCharm preferences across unrelated projects.
- Sharing one live `idea.config.path` across concurrent IDE processes is not
  required because JetBrains stores a lock in that directory.
- Current workaround: use shared config for continuity when only one PyCharm
  process is live, and use `--project-config` for concurrent sessions.
- Future workaround family: maintain a global per-IDE settings profile that
  seeds new per-project config directories without sharing the same live
  lock-bearing config directory.

## Verification

Cheapest checks that should catch this later:

- Automated test: if feasible, create a launcher-level smoke test for the
  shared-config `.lock` preflight.
- Script/check: create `<global-settings>/config/.lock` before launch and
  confirm the launcher fails before Docker startup with the documented
  `--project-config` workaround.
- Optional manual validation: launch project A with default shared config, then
  launch project B with `--project-config` and confirm both open independently.

## Fix Notes

Implemented in repository files on 2026-06-24:

- `run-pycharm-container.sh` now selects a host-side JetBrains config directory
  separately from shared IDE-local home and per-project system/log state.
- Default behavior remains shared config at `<global-settings>/config`.
- New `--project-config` maps JetBrains `idea.config.path` to
  `<project-state>/config` for concurrent sessions.
- New `--ide-config DIR` allows an explicit config directory.
- New `--shared-config` makes the default explicit.
- New `--ignore-config-lock` bypasses the launcher preflight for stale-lock
  recovery attempts.
- The launcher mounts the selected config directory at `/ide-config` and passes
  `IDE_CONFIG_PATH=/ide-config`.
- `entrypoint.sh` writes `idea.config.path=$IDE_CONFIG_PATH`.
- Shared/custom config modes fail before Docker startup when `.lock` already
  exists and suggest `--project-config`.

Full GUI validation of a second live project with `--project-config` remains
useful, but is no longer a blocker for closing this bug as a documented
upstream IDE limitation with a launcher-level fail-fast policy.

Repository-side validation completed:

```bash
bash -n docker4pycharm/run-pycharm-container.sh docker4pycharm/entrypoint.sh docker4pycharm/check-runtime-deps.sh docker4pycharm/build-image.sh docker4pycharm/bootstrap-project.sh
shellcheck docker4pycharm/run-pycharm-container.sh docker4pycharm/entrypoint.sh docker4pycharm/check-runtime-deps.sh docker4pycharm/build-image.sh docker4pycharm/bootstrap-project.sh
git diff --check
./docker4pycharm/run-pycharm-container.sh --help
```

Entrypoint smoke test confirmed that `IDE_CONFIG_PATH=<temp>/config` is written
to `idea.config.path` in the generated `PYCHARM_PROPERTIES` file.

Launcher preflight smoke test created `<global-settings>/config/.lock` and
confirmed the shared-config path fails before Docker startup with a diagnostic
that suggests `--project-config`.

Launcher path-selection smoke test used a fake `docker` executable and confirmed
that `--project-config` selects `<project-state>/config` and reaches Docker even
when the shared config directory contains `.lock`.

## Close Criteria

Done means: the launcher and docs have an explicit concurrent-project policy,
and either concurrent launches with shared user-facing settings work or the
launcher fails early with a clear diagnostic and documented workaround.

Verification: repository-side checks confirm the launcher writes
`idea.config.path` through `/ide-config`, fails fast when a shared/custom config
directory contains `.lock`, and selects per-project config with
`--project-config`. The user accepted the remaining shared-config concurrency
limitation as documented on 2026-06-24.

Reopen if: a later change again lets the second IDE bail out with an opaque
JetBrains lock/config error, or if the documented workaround stops working.

## Logs, stack traces etc

## (1) logs reported by pycharm 
```
Internal error

com.intellij.platform.ide.bootstrap.DirectoryLock$CannotActivateException: Process "/opt/pycharm/jbr/bin/java" (7) is still running and does not respond.

If the IDE is starting up or shutting down, please try again later.
If the process seems stuck, please try killing it (WARNING: unsaved data might be lost).

Stacktrace:
    at com.intellij.platform.ide.bootstrap.DirectoryLock.cannotActivate(DirectoryLock.java:251)
    at com.intellij.platform.ide.bootstrap.DirectoryLock.lockOrActivate(DirectoryLock.java:200)
    at com.intellij.platform.ide.bootstrap.StartupUtil.lockSystemDirs(startup.kt:543)
    at com.intellij.platform.ide.bootstrap.StartupUtil.access$lockSystemDirs(startup.kt:1)
    at com.intellij.platform.ide.bootstrap.StartupUtil$startApplication$lockSystemDirsJob$1$1.invokeSuspend(startup.kt:141)
    at com.intellij.platform.ide.bootstrap.StartupUtil$startApplication$lockSystemDirsJob$1$1.invoke(startup.kt)
    at com.intellij.platform.ide.bootstrap.StartupUtil$startApplication$lockSystemDirsJob$1$1.invoke(startup.kt)
    at kotlinx.coroutines.intrinsics.UndispatchedKt.startUndspatched(Undispatched.kt:67)
    at kotlinx.coroutines.intrinsics.UndispatchedKt.startUndispatchedOrReturn(Undispatched.kt:43)
    at kotlinx.coroutines.BuildersKt__Builders_commonKt.withContext(Builders.common.kt:165)
    at kotlinx.coroutines.BuildersKt.withContext(Unknown Source)
    at com.intellij.platform.diagnostic.telemetry.impl.TracerKt.span(tracer.kt:62)
    at com.intellij.platform.diagnostic.telemetry.impl.TracerKt.span$default(tracer.kt:55)
    at com.intellij.platform.ide.bootstrap.StartupUtil$startApplication$lockSystemDirsJob$1.invokeSuspend(startup.kt:140)
    at kotlin.coroutines.jvm.internal.BaseContinuationImpl.resumeWith(ContinuationImpl.kt:34)
    at kotlinx.coroutines.DispatchedTask.run(DispatchedTask.kt:100)
    at kotlinx.coroutines.scheduling.CoroutineScheduler.runSafely(CoroutineScheduler.kt:610)
    at kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.runDefaultDispatcherTask(CoroutineScheduler.kt:1194)
    at kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.executeTask(CoroutineScheduler.kt:906)
    at kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.runWorker(CoroutineScheduler.kt:775)
    at kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.run(CoroutineScheduler.kt:762)
    Suppressed: java.io.IOException: Cannot lock config directory /ide-global-settings/config
        at com.intellij.platform.ide.bootstrap.DirectoryLock.tryListen(DirectoryLock.java:313)
        at com.intellij.platform.ide.bootstrap.DirectoryLock.lockOrActivate(DirectoryLock.java:180)
        ... 19 more
    Caused by: java.nio.file.FileAlreadyExistsException: /ide-global-settings/config/.lock
        at java.base/sun.nio.fs.UnixException.translateToIOException(UnixException.java:96)
        at java.base/sun.nio.fs.UnixException.rethrowAsIOException(UnixException.java:108)
        at java.base/sun.nio.fs.UnixException.rethrowAsIOException(UnixException.java:114)
        at java.base/sun.nio.fs.UnixFileSystemProvider.newFileChannel(UnixFileSystemProvider.java:213)
        at java.base/sun.nio.fs.UnixFileSystemProvider.newByteChannel(UnixFileSystemProvider.java:244)
        at java.base/java.nio.file.spi.FileSystemProvider.newOutputStream(FileSystemProvider.java:426)
        at com.intellij.platform.core.nio.fs.DelegatingFileSystemProvider.newOutputStream(DelegatingFileSystemProvider.java:92)
        at java.base/java.nio.file.Files.newOutputStream(Files.java:215)
        at java.base/java.nio.file.Files.write(Files.java:3174)
        at java.base/java.nio.file.Files.writeString(Files.java:3368)
        at java.base/java.nio.file.Files.writeString(Files.java:3315)
        at com.intellij.platform.ide.bootstrap.DirectoryLock.tryListen(DirectoryLock.java:308)
        ... 20 more
    Suppressed: java.net.SocketException: No such file or directory
        at java.base/sun.nio.ch.UnixDomainSockets.connect0(Native Method)
        at java.base/sun.nio.ch.UnixDomainSockets.connect(UnixDomainSockets.java:138)
        at java.base/sun.nio.ch.UnixDomainSockets.connect(UnixDomainSockets.java:134)
        at java.base/sun.nio.ch.SocketChannelImpl.connect(SocketChannelImpl.java:950)
        at com.intellij.platform.ide.bootstrap.DirectoryLock.tryConnect(DirectoryLock.java:341)
        at com.intellij.platform.ide.bootstrap.DirectoryLock.lockOrActivate(DirectoryLock.java:188)
        ... 19 more

-----
JRE: 25.0.2+10-b329.117 amd64 (JetBrains s.r.o.)
/opt/pycharm/jbr
```
