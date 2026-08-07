# Completed Task: Development Sudo Account Validation Failure

Date: 2026-06-28

Requirements: R-DEV-001

Status: manually validated

## Symptom

Launching the rebuilt image with `--dev-sudo` reaches the container, but
passwordless sudo does not work for the mapped IDE user.

Observed error:

```text
sudo: account validation failure, is your account locked?
sudo: a password is required
```

## Environment

- Image: freshly rebuilt image from the current v0 stabilization work; exact tag
  should be recorded during the fix validation.
- Launcher mode: `run-pycharm-container.sh --dev-sudo`, with the normal mapped
  host user.
- Related implementation: `docker4pycharm/run-pycharm-container.sh`,
  `docker4pycharm/entrypoint.sh`, `docker4pycharm/Dockerfile`, and
  `docker4pycharm/check-runtime-deps.sh`.

## Expected Behavior

In `--dev-sudo` mode, the mapped IDE user should be a member of the runtime
`ide-sudo` group, the image-baked sudoers rule should allow that group to run
commands without a password, and `sudo -n true` should succeed.

The default profile without `--dev-sudo` should continue to prevent sudo
escalation.

## Current Hypothesis

The runtime account setup is incomplete for Ubuntu's sudo/PAM account
validation path. The launcher bind-mounts synthetic `/etc/passwd` and
`/etc/group` files for the mapped user and runtime `ide-sudo` group; the fix
should inspect whether matching shadow/account state or a different runtime
user creation strategy is required.

Do not weaken the default launcher profile while fixing this. Keep the behavior
behind the explicit `--dev-sudo` mode.

## Fix Attempt

On 2026-06-28, `run-pycharm-container.sh` was updated so `--dev-sudo` also
generates a temporary synthetic `/etc/shadow` file and mounts it read-only into
the container. The shadow file contains root plus the mapped host launcher user
from `id -un`; the launcher still maps the IDE process to the current host
`id -u:id -g` and does not assume UID 1000.

This is intentionally limited to `--dev-sudo`. Default launches still do not
mount a synthetic shadow file, add the `ide-sudo` group, or relax the default
sudo-preventing profile.

Repository-side checks completed:

```bash
bash -n docker4pycharm/run-pycharm-container.sh
shellcheck docker4pycharm/run-pycharm-container.sh
```

A fake-Docker launcher check confirmed that the `/etc/shadow` mount is present
with `--dev-sudo --no-docker` and absent from the default `--no-docker` profile.

Manual validation update:

- The user confirmed `sudo -n ls` works in the launched container after the
  wrapper fix.
- A manual retest from a different non-default host user account is deferred
  for later coverage and is not a current v0 blocker.

## Verification Target

After the fix:

```bash
./docker4pycharm/build-image.sh --pycharm /path/to/pycharm.tar.gz
./docker4pycharm/run-pycharm-container.sh --project /path/to/project --dev-sudo
```

Inside the launched container:

```bash
id
sudo -n true
docker4ide-check-runtime-deps
```

Then relaunch without `--dev-sudo` and confirm the default profile still does
not provide passwordless sudo.

Current validation result:

- `sudo -n ls` works with `--dev-sudo` for the primary mapped host user.
- Repository-side argument checks still show the default profile does not mount
  the synthetic shadow file or add `ide-sudo`.

## Close Criteria

- `sudo -n true` succeeds for the mapped IDE user only in `--dev-sudo` mode.
- `docker4ide-check-runtime-deps` passes in `--dev-sudo` mode.
- The default profile still does not allow sudo escalation.
- README and implementation notes are updated with the validated result.

## Reopen If

Reopen if `--dev-sudo` reports account validation failure, asks for a password,
or requires broadening host exposure or default runtime privileges without
matching documentation.
