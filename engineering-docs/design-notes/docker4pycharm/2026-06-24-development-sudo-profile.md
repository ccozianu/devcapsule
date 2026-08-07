# Decision: Development Sudo Profile

Date: 2026-06-24

Status: implemented and manually validated for the current mapped-user path

Requirements: R-DEV-001

## Context

The PyCharm container is meant to be useful for day-to-day development and
IDE-side agent work. The user requested `sudo` in the next Docker image because
it is useful during development activities.

The default launcher profile deliberately runs the IDE as the mapped non-root
user with a read-only root filesystem, dropped capabilities, and
`no-new-privileges`. Installing the `sudo` binary alone would not make sudo
usable under that profile, and silently removing those constraints from the
default would weaken the documented isolation posture.

## Decision

Install `sudo` in the image and add an explicit launcher profile:

```text
--dev-sudo
--sudo
PYCHARM_ENABLE_SUDO=1
```

When enabled, the launcher:

- adds the mapped IDE user to a runtime-only `ide-sudo` group;
- uses an image-baked sudoers rule for passwordless sudo by that group;
- implies a writable root filesystem;
- skips the default `--cap-drop ALL` and `no-new-privileges` restrictions in
  host-Docker and no-Docker modes so container-local package installs can work;
- prints a warning before starting Docker.

The default host-Docker and no-Docker profiles still keep sudo escalation
disabled. Docker-in-Docker remains its own explicit privileged profile; when
combined with `--dev-sudo`, the IDE-side user also receives the sudo group.

## Verification

Repository-side checks completed:

```bash
bash -n docker4pycharm/run-pycharm-container.sh docker4pycharm/entrypoint.sh docker4pycharm/check-runtime-deps.sh
shellcheck docker4pycharm/run-pycharm-container.sh docker4pycharm/entrypoint.sh docker4pycharm/check-runtime-deps.sh
git diff --check
./docker4pycharm/run-pycharm-container.sh --help
```

Fake-Docker launcher argument checks confirmed:

- the default host-Docker profile still includes `--cap-drop ALL`,
  `--security-opt no-new-privileges`, and `--read-only`;
- `--dev-sudo` adds the sudo group, omits `--cap-drop ALL` /
  `no-new-privileges`, and omits `--read-only`.

Pending validation:

- rebuild the image and confirm `sudo` is installed;
- launch with `--dev-sudo` and confirm `sudo -n true` works as the mapped IDE
  user;
- optionally confirm a temporary package install works inside the writable
  container root.

Validation update on 2026-06-28:

- The user reported that the rebuilt image baseline is good except for
  `--dev-sudo`.
- In the launched container, `sudo -n true` fails with:

```text
sudo: account validation failure, is your account locked?
sudo: a password is required
```

- `run-pycharm-container.sh` was updated to generate and mount a synthetic
  `/etc/shadow` only for `--dev-sudo`, matching the mapped host launcher user.
- The user then confirmed `sudo -n ls` works in the launched container.
- A manual retest from a different non-default host user account is deferred
  for later coverage and is not a current v0 blocker.

The retrospective record is:
`completed-tasks/2026-06-28-dev-sudo-account-validation.md`.

## Reopen If

Reopen if `--dev-sudo` fails to provide passwordless sudo to the mapped IDE
user, if the default profile unexpectedly permits sudo escalation, or if sudo
support is made implicit without matching security documentation.
