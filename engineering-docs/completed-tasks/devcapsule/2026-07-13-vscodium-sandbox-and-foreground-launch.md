# Completed Task: VSCodium Sandbox And Foreground Launch

Date opened: 2026-07-13

Date closed: 2026-07-13

Status: manually validated

Requirements: R-IMAGE-BUILD-001, R-PYTHON-MVP-003, R-FRAMEWORK-001,
R-SCOPE-001

## Symptom

`devcapsule codium_with_claude run` exits without opening VSCodium, prints no
useful diagnostic to the host console, and reports container exit status zero.
An `xterm` started from `--debug-shell` works, showing that the forwarded
`DISPLAY` and X11 socket are sufficient on the validating host.

## Environment

- Configuration: `codium_with_claude`
- Base image: Ubuntu 24.04
- IDE payload: local VSCodium archive installed under `/opt/codium`
- Observed VSCodium version: 1.126.04524
- Container user: host UID/GID mapped by the normal image entrypoint
- Workload: `devcapsule-src/tests/resources/sample_projects/typescript_tictactoe_5inrow`

The exact host kernel, Docker Engine, and Docker seccomp versions were not
captured and remain useful validation metadata.

## Reproduction

1. Build the configuration with a local VSCodium archive.
2. Launch the sample project with `devcapsule codium_with_claude run`.
3. Observe that no window appears and Docker reports exit status zero.
4. Enter the same image with `--debug-shell`.
5. Confirm `xterm` opens successfully.
6. From the mounted sample project, run:

   ```bash
   strace -f codium . >codium.log 2>&1
   ```

## Expected Behavior

VSCodium should open the selected project and remain attached to the container
process. If startup fails, the launcher should return a nonzero status and
leave an actionable diagnostic on standard error.

## Actual Behavior

VSCodium does not open. Chromium's sandbox subprocess fails, but the detached
CLI parent exits zero and the fatal diagnostic is redirected to `/dev/null`.
Docker therefore reports a clean container exit with no useful console output.

## Evidence

The local `codium.log` trace captured the following decisive sequence:

```text
clone(... flags=CLONE_NEWUSER|SIGCHLD) = -1 EPERM (Operation not permitted)
stat("/opt/codium/chrome-sandbox", {st_mode=S_IFREG|0755, ...}) = 0
access("/opt/codium/chrome-sandbox", X_OK) = 0
write(2, "[...:FATAL:sandbox...", 302) = 302
--- SIGTRAP {si_signo=SIGTRAP, si_code=SI_KERNEL, si_addr=NULL} ---
+++ killed by SIGTRAP (core dumped) +++
recvmsg(...) = -1 ECONNRESET (Connection reset by peer)
exit_group(0)
+++ exited with 0 +++
```

Immediately before starting the failing process, the VSCodium CLI forks,
creates a new session, and redirects descriptors 0, 1, and 2 to `/dev/null`.
That explains both the missing fatal message and why the CLI wrapper can mask
the sandbox subprocess failure.

The numerous `ENOENT` results while the dynamic loader searches `/opt/codium`
before finding libraries under `/lib/x86_64-linux-gnu` are normal lookup
fallbacks and are not the cause.

## Root Cause

Docker denies the unprivileged user-namespace sandbox attempt. Chromium then
tries its setuid sandbox helper, but `/opt/codium/chrome-sandbox` has mode
`0755`; Chromium requires that helper to be owned by root with mode `4755`.

The likely source is local archive normalization. Python's safe tar extraction
filter intentionally removes special permission bits, including setuid. The
normalized VSCodium directory is then copied into the build context without a
component that restores the helper's required ownership and mode.

## Security Constraint

Do not make `--no-sandbox` the supported default. It is useful only as a
one-time confirmation because it disables an Electron/Chromium isolation
boundary. Do not relax the entire container seccomp profile or add broad
capabilities when the narrowly scoped setuid helper is sufficient.

The proposed setuid permission is security-sensitive and must remain limited
to the vendor-provided `/opt/codium/chrome-sandbox` binary.

## Proposed Fix

For the local-archive installation path, add an image-build step after copying
VSCodium that verifies the helper exists and then applies:

```text
chown root:root /opt/codium/chrome-sandbox
chmod 4755 /opt/codium/chrome-sandbox
```

The build should fail clearly if the expected helper is absent. Add a focused
build-plan or rendered-Dockerfile regression test for its ownership and mode.
Also consider preventing the VSCodium CLI wrapper from detaching, or enabling
verbose foreground diagnostics, so future startup failures propagate a useful
exit status.

## Fix Implemented

On 2026-07-13, the local-archive build plan was updated to fail with a clear
message when `/opt/codium/chrome-sandbox` is absent, then apply root ownership
and mode `4755` after copying the normalized archive. A focused build-plan test
asserts the presence of the validation, `chown`, and `chmod` operations.

The user confirmed that `codium --no-sandbox .` opens successfully, validating
the sandbox diagnosis. That flag was not added to the supported launcher.

Further host testing found a second lifecycle defect: after sandbox startup
was enabled with an explicit `SYS_ADMIN` diagnostic capability, the normal
container briefly displayed a window and then stopped. The `bin/codium` CLI
wrapper forks and detaches the Electron process, so the wrapper exits and
Docker terminates the container. The launcher now uses a packaged
`codium-foreground` link to the Electron binary (`/opt/codium/codium` for a
local archive and `/usr/share/codium/codium` for the apt package). This keeps
the IDE attached as the foreground container process. Rebuilt host validation
was initially pending.

## Manual Validation

On 2026-07-13, the user rebuilt and launched the image successfully. VSCodium
remained open as the foreground container process, and the Claude integration
worked sufficiently to accept the Codium plus Claude MVP proof point.

The validating launch explicitly used host networking and added `SYS_ADMIN` so
Chromium could create its sandbox namespaces. These remain explicit isolation
relaxations rather than ambient defaults. The `--no-sandbox` diagnostic was
not retained in the supported launch command.

## Verification Target

1. Confirm `codium --no-sandbox .` opens once as diagnosis only.
2. Rebuild without making `--no-sandbox` part of the launcher.
3. In the rebuilt image, verify:

   ```bash
   stat -c '%U:%G %a %n' /opt/codium/chrome-sandbox
   ```

   Expected result: `root:root 4755 /opt/codium/chrome-sandbox`.
4. Launch the sample project through the normal configuration command and
   confirm VSCodium opens and remains running.
5. Confirm the normal command does not include `--no-sandbox`, `--privileged`,
   or a relaxed seccomp profile, and that any required capability such as
   `SYS_ADMIN` remains an explicit opt-in launch argument.
6. Run `cd devcapsule-src && python -m nox -s build`.

## Close Criteria

Close this bug only after the focused regression test passes and a rebuilt
local-archive image launches VSCodium successfully on the host with Chromium's
sandbox enabled. Preserve the result as a completed-task record if later
sessions would benefit from the validation history.

The criteria were satisfied on 2026-07-13. Reopen if a rebuilt image again
loses the helper ownership/mode, the normal launcher detaches from Electron,
the window immediately disappears, or sandbox startup fails under the
documented capability profile.
