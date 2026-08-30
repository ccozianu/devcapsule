from __future__ import annotations

import json
import hashlib
import io
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import tarfile
import time
import uuid

import pytest

from devcapsule.base_image import BaseImageBuildOptions, build_base_image_spec, file_sha256
from devcapsule.components.pycharm import runtime_template as pycharm_runtime_template
from devcapsule.container_runtime.contract import Identity, RuntimePlan
from devcapsule.image_build import render_build_context
from devcapsule.materialization import ArtifactSpec, ImageDetails, ensure_materialized_pycharm

DEFAULT_BASE_IMAGE = "mycodespace.ai/pycharm:debug-v018"


def command(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, check=check, text=True, capture_output=True)


def create_jetbrains_fixture(path: Path) -> bytes:
    # The fixture "IDE" reports its own parentage so the supervised run can
    # assert the process tree, then exits, which ends the session.
    launcher = b'#!/bin/sh\necho "pycharm-fixture pid=$$ ppid=$PPID"\n'
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
    built_supervised_image: str | None = None
    spec = build_base_image_spec(
        BaseImageBuildOptions(
            pex=built_pex,
            image=image,
            root_image=base_image,
            allow_local_source=True,
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

        def inspect_image(candidate: str) -> ImageDetails | None:
            inspected = command(docker, "image", "inspect", candidate, check=False)
            if inspected.returncode != 0:
                return None
            value = json.loads(inspected.stdout)[0]
            return ImageDetails(
                reference=candidate,
                identity=value["Id"],
                labels=value["Config"].get("Labels") or {},
                operating_system=value["Os"],
                architecture=value["Architecture"],
            )

        def build_materialized(materialization_spec) -> None:
            nonlocal build_count
            build_count += 1
            context = tmp_path / f"materialization-context-{build_count}"
            context.mkdir()
            render_build_context(materialization_spec.build_plan(), context)
            command(docker, "build", "--pull=false", "--tag", materialization_spec.image, str(context))

        materialized_image, created = ensure_materialized_pycharm(
            base_reference=image,
            base_identity=inspection["Id"],
            platform=f"{inspection['Os']}-{inspection['Architecture']}",
            artifact=artifact,
            cache_root=cache,
            inspect_image=inspect_image,
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
        command(
            docker,
            "run",
            "--rm",
            "--entrypoint",
            "test",
            materialized_image,
            "-r",
            "/etc/devcapsule/component-runtime-template.json",
        )
        command(
            docker,
            "run",
            "--rm",
            "--entrypoint",
            "test",
            materialized_image,
            "!",
            "-e",
            "/etc/devcapsule/runtime-plan.json",
        )

        archive.unlink()
        reused_image, created = ensure_materialized_pycharm(
            base_reference=image,
            base_identity=inspection["Id"],
            platform=f"{inspection['Os']}-{inspection['Architecture']}",
            artifact=artifact,
            cache_root=cache,
            inspect_image=inspect_image,
            build=build_materialized,
        )
        assert reused_image == materialized_image
        assert created is False
        assert build_count == 1

        # --- Supervised sessions against the materialized image ---
        # The runtime plan is baked into a derived image rather than
        # bind-mounted: the suite may run inside a capsule against the host
        # Docker daemon, where a local temporary path cannot be mounted.
        plan = RuntimePlan.for_component(
            pycharm_runtime_template(),
            project_path="/workspace/project",
            home="/home/devcapsule",
            identity=Identity(1000, 1000),
        )
        supervised_context = tmp_path / "supervised-context"
        supervised_context.mkdir()
        (supervised_context / "runtime-plan.json").write_text(
            plan.to_json() + "\n", encoding="utf-8"
        )
        (supervised_context / "Dockerfile").write_text(
            f"FROM {materialized_image}\n"
            "COPY runtime-plan.json /etc/devcapsule/runtime-plan.json\n"
            "RUN mkdir -p /workspace/project && chown 1000:1000 /workspace/project\n",
            encoding="utf-8",
        )
        supervised_image = f"devcapsule-supervised-e2e:{identifier}"
        command(docker, "build", "--pull=false", "--tag", supervised_image, str(supervised_context))
        built_supervised_image = supervised_image
        run_prefix = (docker, "run", "--rm", supervised_image)

        # Interactive shape: the supervisor is PID 1, the IDE is its child,
        # and the IDE exiting ends the session with its exit code.
        interactive = command(*run_prefix, check=False)
        assert interactive.returncode == 0, interactive.stderr
        parentage = re.search(r"pycharm-fixture pid=(\d+) ppid=(\d+)", interactive.stdout)
        assert parentage is not None, interactive.stdout
        assert parentage.group(1) != "1"
        assert parentage.group(2) == "1"

        # Headless mode: the job takes the same distinguished slot, runs in
        # the project, sees the supervisor as PID 1, finds no zombies after an
        # orphan died (PID 1 reaped it), and its exit code is the session's.
        job = """
set -eu
test "$$" -ne 1
test "$PPID" -eq 1
tr '\\0' ' ' </proc/1/cmdline | grep -q ' runtime /etc/devcapsule/runtime-plan.json'
test "$(pwd)" = /workspace/project
( sleep 0.2 & )
sleep 0.7
for stat in /proc/[0-9]*/stat; do
  state=$(cut -d" " -f3 "$stat" 2>/dev/null) || continue
  if [ "$state" = Z ]; then exit 21; fi
done
exit 9
"""
        headless = command(
            *run_prefix,
            "/etc/devcapsule/runtime-plan.json",
            "--",
            "sh",
            "-c",
            job,
            check=False,
        )
        assert headless.returncode == 9, (headless.stdout, headless.stderr)

        # Explicit session end: `docker stop` reaches the supervisor as
        # SIGTERM, the child is terminated within the grace period, and the
        # session exit code reports the forwarded signal honestly (128+15).
        started = command(
            docker,
            "run",
            "--detach",
            supervised_image,
            "/etc/devcapsule/runtime-plan.json",
            "--",
            "sh",
            "-c",
            "echo supervisor-e2e-ready; exec sleep 300",
        )
        container_id = started.stdout.strip()
        try:
            deadline = time.monotonic() + 30
            while "supervisor-e2e-ready" not in command(docker, "logs", container_id).stdout:
                assert time.monotonic() < deadline, "headless job never became ready"
                time.sleep(0.2)
            command(docker, "stop", container_id)
            stopped = command(docker, "wait", container_id)
            assert stopped.stdout.strip() == str(128 + signal.SIGTERM)
            logs = command(docker, "logs", container_id)
            assert "session end requested (SIGTERM)" in logs.stderr
        finally:
            command(docker, "rm", "--force", container_id, check=False)
    finally:
        if built_supervised_image is not None:
            command(docker, "image", "rm", "--force", built_supervised_image, check=False)
        if materialized_image is not None:
            command(docker, "image", "rm", "--force", materialized_image, check=False)
        command(docker, "image", "rm", "--force", image, check=False)
