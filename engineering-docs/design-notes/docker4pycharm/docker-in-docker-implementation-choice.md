# What's here

This describes the current Docker capability choice and rationale for the
containerized PyCharm development environment.

The companion
[Docker in containerized development environments](docker-in-containerized-development-environments.md)
note summarizes the two general implementation patterns.

# Docker Capability Security TLDR

Implemented default: host Docker daemon passthrough, with true
Docker-in-Docker available only as an explicit launcher option.

## Default: Host Docker Daemon Passthrough

The default launcher mode is Docker-outside-of-Docker:

```bash
./run-pycharm-container.sh --project /path/to/project --ssh-agent
```

or explicitly:

```bash
./run-pycharm-container.sh --project /path/to/project --docker
```

## How It Works

- The image installs `docker.io`, `docker-buildx`, `docker-compose-v2`, `gosu`,
  and `shellcheck`.
- `run-pycharm-container.sh` defaults to `DOCKER_MODE=host`.
- The launcher mounts the host Docker socket at `/run/host-docker.sock`.
- The launcher sets `DOCKER_HOST=unix:///run/host-docker.sock`.
- The launcher reads the host socket group ID and adds that numeric group as a
  supplemental group for the mapped IDE user with `--group-add`.
- PyCharm still runs as the mapped non-root IDE user.
- The outer IDE container keeps the stricter non-DinD posture: read-only root
  filesystem by default, `--cap-drop ALL`, and `no-new-privileges`.

Developer-facing behavior:

```text
docker ps inside PyCharm == docker ps on the host
```

Containers started from inside PyCharm/Codex are host Docker sibling containers,
not children of the IDE container.

Validation status: the default host Docker passthrough check was removed from
the active v0 stabilization task list on 2026-06-20. Treat the default mode as
documented current behavior unless a later image or launcher change affects this
path. Retrospective note:
`completed-tasks/2026-06-20-default-host-docker-passthrough-validation-retired.md`.

## Explicit Docker-in-Docker

Use true Docker-in-Docker only when separate Docker state is wanted:

```bash
./run-pycharm-container.sh --project /path/to/project --docker-in-docker
```

or:

```bash
./run-pycharm-container.sh --project /path/to/project --dind
```

When enabled, the outer PyCharm container starts with:

- `--privileged`
- a writable root filesystem
- a Docker volume mounted at `/var/lib/docker`
- `ENABLE_DIND=1`

`entrypoint.sh` runs as root, starts an inner `dockerd`, waits for `docker info`
to succeed, then uses `gosu UID:GID` to launch PyCharm as the normal mapped
user. The Docker socket stays inside the container at `/var/run/docker.sock`.

Because the outer container uses `--network=host`, the inner `dockerd` starts
with bridge/iptables management disabled. For inner builds needing network
access, use `--network host`.

Validation status: explicit Docker-in-Docker was manually tested in the latest
built VM on 2026-06-20 and worked as expected. Treat this as complete unless a
later image or launcher change affects the DinD path. Retrospective note:
`completed-tasks/2026-06-20-explicit-docker-in-docker-validation.md`.

## No Docker

For the strictest profile, disable Docker access:

```bash
./run-pycharm-container.sh --project /path/to/project --no-docker
```

or:

```bash
DOCKER_MODE=none ./run-pycharm-container.sh --project /path/to/project
```

Compatibility with the previous launcher behavior is preserved:

```bash
DOCKER_IN_DOCKER=1 ./run-pycharm-container.sh --project /path/to/project
DOCKER_IN_DOCKER=0 ./run-pycharm-container.sh --project /path/to/project
```

The first command selects explicit DinD; the second selects no-Docker.

## Security Tradeoffs

- Host Docker socket passthrough is convenient and matches local developer
  expectations, but it gives tools inside PyCharm/Codex broad control over the
  host Docker daemon.
- With the host socket mounted, malicious or buggy IDE-side code can start
  privileged host containers, mount host paths, delete images/containers, and
  otherwise mutate host Docker state.
- True DinD avoids direct access to the host Docker daemon and gives separate
  Docker images/containers/volumes, but it requires `--privileged`, a writable
  outer root filesystem, and a nested daemon.
- `--no-docker` keeps the stricter old profile: non-root user, `--read-only`,
  `--cap-drop ALL`, `no-new-privileges`, and no Docker daemon access.

Practical framing: default host Docker passthrough is the local developer
convenience mode. Use `--docker-in-docker` for isolated Docker state, and use
`--no-docker` for higher-isolation sessions where Docker builds/runs are not
needed.
