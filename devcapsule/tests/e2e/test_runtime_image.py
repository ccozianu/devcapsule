from __future__ import annotations

import json
import hashlib
import io
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import uuid

import pytest

from devcapsule.base_image import BaseImageBuildOptions, build_base_image_spec, file_sha256
from devcapsule.image_build import render_build_context
from devcapsule.materialization import ArtifactSpec, ensure_materialized_pycharm

DEFAULT_BASE_IMAGE = "mycodespace.ai/pycharm:debug-v018"


def command(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, check=check, text=True, capture_output=True)


def create_jetbrains_fixture(path: Path) -> bytes:
    launcher = b"#!/bin/sh\n"
    with tarfile.open(path, "w:gz") as archive:
        info = tarfile.TarInfo("pycharm-fixture/bin/pycharm.sh")
        info.mode = 0o755
        info.size = len(launcher)
        archive.addfile(info, io.BytesIO(launcher))
    return path.read_bytes()


@pytest.mark.e2e
def test_pex_runtime_help_inside_disposable_image(tmp_path: Path, built_pex: Path) -> None:
    docker = shutil.which("docker")
    assert docker is not None, "Docker CLI is required for the explicit E2E suite"
    command(docker, "version")

    base_image = os.environ.get("DEVCAPSULE_E2E_BASE_IMAGE", DEFAULT_BASE_IMAGE)
    inspected_base = command(docker, "image", "inspect", base_image, check=False)
    assert inspected_base.returncode == 0, (
        f"E2E base image {base_image!r} is not available locally; pull it explicitly "
        "or set DEVCAPSULE_E2E_BASE_IMAGE"
    )

    identifier = uuid.uuid4().hex
    image = f"devcapsule-runtime-e2e:{identifier}"
    materialized_image: str | None = None
    spec = build_base_image_spec(
        BaseImageBuildOptions(
            pex=built_pex,
            image=image,
            root_image=base_image,
            source_revision="e2e",
            install_baseline=False,
        )
    )
    render_build_context(spec.build_plan(), tmp_path)

    try:
        command(
            docker,
            "build",
            "--pull=false",
            "--tag",
            image,
            str(tmp_path),
        )
        inspection = json.loads(command(docker, "image", "inspect", image).stdout)[0]
        assert inspection["Config"]["Entrypoint"] == [
            "/usr/bin/tini",
            "--",
            "/opt/devcapsule/bin/devcapsule.pex",
            "runtime",
        ]
        assert inspection["Config"]["Cmd"] == ["/etc/devcapsule/runtime-plan.json"]
        assert inspection["Config"]["Labels"]["devcapsule.image.kind"] == "base"
        assert inspection["Config"]["Labels"]["devcapsule.pex.sha256"] == file_sha256(built_pex)

        python = command(docker, "run", "--rm", "--entrypoint", "python3.12", image, "--version")
        assert python.stdout.startswith("Python 3.12")
        in_image_digest = command(
            docker,
            "run",
            "--rm",
            "--entrypoint",
            "sha256sum",
            image,
            "/opt/devcapsule/bin/devcapsule.pex",
        ).stdout.split()[0]
        assert in_image_digest == file_sha256(built_pex)

        completed = command(docker, "run", "--rm", "--network", "none", image, "--help", check=False)
        assert completed.returncode == 0, completed.stderr
        assert "usage: devcapsule runtime RUNTIME_PLAN.json" in completed.stdout

        archive = tmp_path / "pycharm-fixture.tar.gz"
        payload = create_jetbrains_fixture(archive)
        artifact = ArtifactSpec("fixture-1", archive.as_uri(), hashlib.sha256(payload).hexdigest())
        cache = tmp_path / "materialization-cache"
        build_count = 0

        def image_exists(candidate: str) -> bool:
            return command(docker, "image", "inspect", candidate, check=False).returncode == 0

        def build_materialized(materialization_spec) -> None:
            nonlocal build_count
            build_count += 1
            context = tmp_path / f"materialization-context-{build_count}"
            context.mkdir()
            render_build_context(materialization_spec.build_plan(), context)
            command(docker, "build", "--pull=false", "--tag", materialization_spec.image, str(context))

        materialized_image, created = ensure_materialized_pycharm(
            base_image=image,
            artifact=artifact,
            cache_root=cache,
            image_exists=image_exists,
            build=build_materialized,
        )
        assert created is True
        assert build_count == 1
        command(
            docker,
            "run",
            "--rm",
            "--entrypoint",
            "test",
            materialized_image,
            "-x",
            "/opt/jetbrains/pycharm/bin/pycharm.sh",
        )

        archive.unlink()
        reused_image, created = ensure_materialized_pycharm(
            base_image=image,
            artifact=artifact,
            cache_root=cache,
            image_exists=image_exists,
            build=build_materialized,
        )
        assert reused_image == materialized_image
        assert created is False
        assert build_count == 1
    finally:
        if materialized_image is not None:
            command(docker, "image", "rm", "--force", materialized_image, check=False)
        command(docker, "image", "rm", "--force", image, check=False)
