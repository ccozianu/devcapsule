#!/usr/bin/env bash
set -euo pipefail

uid="${HOST_UID:-1000}"
gid="${HOST_GID:-1000}"

if ! getent group "${gid}" >/dev/null; then
  groupadd --gid "${gid}" developer
fi
group_name="$(getent group "${gid}" | cut -d: -f1)"

if existing_user="$(getent passwd "${uid}" | cut -d: -f1)" && [[ -n "${existing_user}" ]]; then
  user_name="${existing_user}"
  usermod --home /ide-global-settings/home --gid "${gid}" "${user_name}"
else
  user_name=developer
  useradd --uid "${uid}" --gid "${gid}" --home-dir /ide-global-settings/home --shell /bin/bash "${user_name}"
fi

mkdir -p /ide-global-settings/home /ide-project-state/home/.cache
chown "${uid}:${gid}" /ide-global-settings/home /ide-project-state/home /ide-project-state/home/.cache
printf '%s ALL=(ALL) NOPASSWD:ALL\n' "${user_name}" > /etc/sudoers.d/devcapsule-developer
chmod 0440 /etc/sudoers.d/devcapsule-developer

export HOME=/ide-global-settings/home
export USER="${user_name}"
export LOGNAME="${user_name}"
exec gosu "${user_name}:${group_name}" "$@"
