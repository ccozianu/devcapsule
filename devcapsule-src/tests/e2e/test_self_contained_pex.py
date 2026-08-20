from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest

from devcapsule import __version__

DEFAULT_CLEAN_MACHINE_IMAGE = "ubuntu:24.04"


def command(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, check=check, text=True, capture_output=True)


@pytest.mark.e2e
def test_self_contained_pex_runs_without_python_or_network(built_pex: Path) -> None:
    docker = shutil.which("docker")
    assert docker is not None, "Docker CLI is required for the clean-machine PEX proof"
    command(docker, "version")

    base_image = os.environ.get(
        "DEVCAPSULE_PEX_CLEAN_MACHINE_IMAGE", DEFAULT_CLEAN_MACHINE_IMAGE
    )
    inspected = command(docker, "image", "inspect", base_image, check=False)
    assert inspected.returncode == 0, (
        f"Clean-machine image {base_image!r} is not available locally; pull it explicitly "
        "or set DEVCAPSULE_PEX_CLEAN_MACHINE_IMAGE"
    )

    script = """
set -eu
for candidate in python python3 python3.12; do
    if command -v "${candidate}" >/dev/null 2>&1; then
        echo "unexpected host interpreter: ${candidate}" >&2
        exit 1
    fi
done
/devcapsule.pex --help >/tmp/devcapsule-help.txt
/devcapsule.pex version --json
"""
    created = command(
        docker,
        "create",
        "--network",
        "none",
        "--entrypoint",
        "/bin/sh",
        base_image,
        "-c",
        script,
    )
    container = created.stdout.strip()
    assert container

    try:
        command(docker, "cp", str(built_pex), f"{container}:/devcapsule.pex")
        completed = command(docker, "start", "--attach", container, check=False)
        assert completed.returncode == 0, completed.stderr
        version = json.loads(completed.stdout)
        assert version["schema_version"] == 2
        assert version["version"] == __version__
        assert version["build_mnemonic"] == os.environ.get(
            "DEVCAPSULE_EXPECTED_BUILD_MNEMONIC", "local-v026"
        )
    finally:
        command(docker, "rm", "--force", container, check=False)
