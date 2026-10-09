"""Redistributable language tooling for DevCapsule base images."""

from __future__ import annotations

import shlex

from devcapsule.images.build import ExecComponent

NODE_VERSION = "v22.23.1"
NODE_CURRENT_BIN = "/opt/node/current/bin"
TEMURIN_VERSION = "25.0.4+7"
TEMURIN_RELEASE = "jdk-25.0.4%2B7"
TEMURIN_CURRENT = "/opt/java/current"
TEMURIN_CURRENT_BIN = f"{TEMURIN_CURRENT}/bin"
TEMURIN_LINUX_X64_SHA256 = (
    "e58fcdcd637b25c03ca84cbbcefc70d11efb8f4b4cbd05decc9f661769d77f94"
)
TEMURIN_LINUX_AARCH64_SHA256 = (
    "621f7196f0b682fb557da58bec89bd7dfe5419811fe1c0ba75c9cc8432f084c7"
)
MAVEN_VERSION = "3.9.16"
MAVEN_CURRENT = "/opt/maven/current"
MAVEN_CURRENT_BIN = f"{MAVEN_CURRENT}/bin"
MAVEN_SHA512 = (
    "831a8591fe20c8243b1dbe7d71e3244f31d1665b0804b2e825e38cbbe5ce0caf"
    "b8338851f90780735568773e0a6cd07bbec107cda0b896b008b861075358b6f6"
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


def temurin_tooling_component() -> ExecComponent:
    """Install the pinned Eclipse Temurin JDK release for the target architecture."""
    commands = [
        'arch="$(dpkg --print-architecture)"',
        (
            'case "$arch" in '
            f'amd64) temurin_arch="x64"; temurin_sha256="{TEMURIN_LINUX_X64_SHA256}" ;; '
            f'arm64) temurin_arch="aarch64"; temurin_sha256="{TEMURIN_LINUX_AARCH64_SHA256}" ;; '
            '*) echo "Unsupported Eclipse Temurin architecture: $arch" >&2; exit 1 ;; esac'
        ),
        f'temurin_version="{TEMURIN_VERSION}"',
        'temurin_archive="OpenJDK25U-jdk_${temurin_arch}_linux_hotspot_25.0.4_7.tar.gz"',
        f'temurin_url="https://github.com/adoptium/temurin25-binaries/releases/download/{TEMURIN_RELEASE}/${{temurin_archive}}"',
        'curl -fsSL "$temurin_url" -o "$temurin_archive"',
        'printf \'%s  %s\\n\' "$temurin_sha256" "$temurin_archive" | sha256sum -c -',
        'mkdir -p /opt/java',
        'tar -xzf "$temurin_archive" -C /opt/java',
        'ln -sfn "/opt/java/jdk-${temurin_version}" /opt/java/current',
        f'export JAVA_HOME="{TEMURIN_CURRENT}"',
        f'export PATH="{TEMURIN_CURRENT_BIN}:$PATH"',
        'java -version',
        'javac -version',
        'rm -f "$temurin_archive"',
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


def maven_tooling_component() -> ExecComponent:
    """Install the pinned Apache Maven release."""

    commands = [
        f'maven_version="{MAVEN_VERSION}"',
        'maven_archive="apache-maven-${maven_version}-bin.tar.gz"',
        'maven_url="https://downloads.apache.org/maven/maven-3/${maven_version}/binaries/${maven_archive}"',
        'curl -fsSL "$maven_url" -o "$maven_archive"',
        f'printf \'%s  %s\\n\' "{MAVEN_SHA512}" "$maven_archive" | sha512sum -c -',
        'mkdir -p /opt/maven',
        'tar -xzf "$maven_archive" -C /opt/maven',
        'ln -sfn "/opt/maven/apache-maven-${maven_version}" /opt/maven/current',
        f'export JAVA_HOME="{TEMURIN_CURRENT}"',
        f'export MAVEN_HOME="{MAVEN_CURRENT}"',
        f'export PATH="{MAVEN_CURRENT_BIN}:{TEMURIN_CURRENT_BIN}:$PATH"',
        'mvn --version',
        'rm -f "$maven_archive"',
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


WEBCONSOLE_ROOT = "/opt/devcapsule-webconsole"
"""Where the base installs the capsule web console: its venv and the package.

The runtime starts it from here (``container_runtime/console.py``); keep the
two in step.
"""
WEBCONSOLE_VENV_PYTHON = f"{WEBCONSOLE_ROOT}/venv/bin/python"


def webconsole_tooling_component(source_repository: str, source_revision: str) -> ExecComponent:
    """Install the capsule web console from the verified public revision.

    The console is the ``devcapsule-webconsole/`` subproject of the source
    revision the runtime PEX was built from. Git fetches that exact commit,
    which verifies the content against the commit hash. Its dependencies
    come from the subproject's hash-pinned ``requirements.txt``, the build
    toolchain from ``requirements-build.txt``, and the package itself is
    installed from the checkout without build isolation, so nothing is
    fetched that is not pinned by hash. The checkout is removed afterwards.
    """

    python = WEBCONSOLE_VENV_PYTHON
    pip = f"{python} -m pip install --no-cache-dir --disable-pip-version-check"
    commands = [
        f"source_repository={shlex.quote(source_repository)}",
        f"source_revision={shlex.quote(source_revision)}",
        'checkout="$(mktemp -d)"',
        'git -C "$checkout" init -q',
        'git -C "$checkout" fetch -q --depth 1 "$source_repository" "$source_revision"',
        'git -C "$checkout" checkout -q --detach FETCH_HEAD',
        'test "$(git -C "$checkout" rev-parse HEAD)" = "$source_revision"',
        'subproject="$checkout/devcapsule-webconsole"',
        f'python3 -m venv "{WEBCONSOLE_ROOT}/venv"',
        f'{pip} --require-hashes -r "$subproject/requirements.txt"',
        f'{pip} --require-hashes -r "$subproject/requirements-build.txt"',
        f'{pip} --no-deps --no-build-isolation "$subproject"',
        f'{python} -c "import devcapsule_webconsole, fastapi, uvicorn"',
        f'{python} -m devcapsule_webconsole --help >/dev/null',
        'rm -rf "$checkout"',
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
