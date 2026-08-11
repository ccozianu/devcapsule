"""Shared language and optional agent tooling for DevCapsule images."""

from __future__ import annotations

from devcapsule.image_build import ExecComponent

NODE_VERSION = "v22.23.1"
NODE_CURRENT_BIN = "/opt/node/current/bin"
CLAUDE_CODE_VERSION = "2.1.227"
CLAUDE_CODE_PREFIX = "/opt/claude"
CLAUDE_CODE_BIN = f"{CLAUDE_CODE_PREFIX}/bin"
CLAUDE_CODE_RELEASE_ROOT = "https://downloads.claude.ai/claude-code-releases"
CLAUDE_CODE_LINUX_X64_SHA256 = (
    "6832dc3f1797b890b71116e5f2dbbf9a83fd3d0498c235b4b0f9cd0e6e499ad6"
)
CLAUDE_CODE_LINUX_ARM64_SHA256 = (
    "db47335532cbcab67a4b3ab16d8f3f77976bf85d53c7d79f8296538aa22bfce6"
)


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


def claude_code_component() -> ExecComponent:
    """Install one pinned Claude Code release in the image-owned prefix."""

    commands = [
        'arch="$(dpkg --print-architecture)"',
        (
            'case "$arch" in '
            f'amd64) claude_platform="linux-x64"; claude_sha256="{CLAUDE_CODE_LINUX_X64_SHA256}" ;; '
            f'arm64) claude_platform="linux-arm64"; claude_sha256="{CLAUDE_CODE_LINUX_ARM64_SHA256}" ;; '
            '*) echo "Unsupported Claude Code architecture: $arch" >&2; exit 1 ;; esac'
        ),
        f'claude_version="{CLAUDE_CODE_VERSION}"',
        f'claude_release_root="{CLAUDE_CODE_RELEASE_ROOT}"',
        'claude_work="$(mktemp -d)"',
        'trap \'rm -rf "$claude_work"\' EXIT',
        'curl -fsSL "${claude_release_root}/${claude_version}/${claude_platform}/claude" '
        '-o "${claude_work}/claude"',
        'printf \'%s  %s\\n\' "$claude_sha256" "${claude_work}/claude" | sha256sum -c -',
        f'install -d -m 0755 "{CLAUDE_CODE_BIN}" "{CLAUDE_CODE_PREFIX}/versions/${{claude_version}}"',
        f'install -m 0755 "${{claude_work}}/claude" "{CLAUDE_CODE_PREFIX}/versions/${{claude_version}}/claude"',
        f'ln -sfn "../versions/${{claude_version}}/claude" "{CLAUDE_CODE_BIN}/claude"',
        f'HOME="${{claude_work}}/home" DISABLE_AUTOUPDATER=1 "{CLAUDE_CODE_BIN}/claude" --version',
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
