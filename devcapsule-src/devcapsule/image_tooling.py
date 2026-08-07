"""Shared Node.js install plan for active DevCapsule images."""

from __future__ import annotations

from devcapsule.image_build import ExecComponent

NODE_VERSION = "v22.23.1"
NODE_CURRENT_BIN = "/opt/node/current/bin"


def node_tooling_component() -> ExecComponent:
    commands = [
        'arch="$(dpkg --print-architecture)"',
        'case "$arch" in amd64) node_arch="x64" ;; arm64) node_arch="arm64" ;; *) echo "Unsupported Node.js architecture: $arch" >&2; exit 1 ;; esac',
        f'node_version="{NODE_VERSION}"',
        'node_dist="node-${node_version}-linux-${node_arch}"',
        'node_archive="${node_dist}.tar.xz"',
        'node_base_url="https://nodejs.org/dist/${node_version}"',
        'curl -fsSLO "${node_base_url}/${node_archive}"',
        'curl -fsSLO "${node_base_url}/SHASUMS256.txt"',
        'grep " ${node_archive}$" SHASUMS256.txt | sha256sum -c -',
        'mkdir -p /opt/node',
        'tar -xJf "${node_archive}" -C /opt/node',
        'ln -sfn "/opt/node/${node_dist}" /opt/node/current',
        f'export PATH="{NODE_CURRENT_BIN}:$PATH"',
        'node --version',
        'npm --version',
        'npm cache clean --force',
        'rm -f "${node_archive}" SHASUMS256.txt',
    ]
    return ExecComponent(
        args=(
            "bash",
            "-euxo",
            "pipefail",
            "-c",
            " && ".join(commands),
        ),
    )
