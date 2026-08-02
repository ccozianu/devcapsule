from __future__ import annotations

import hashlib
from pathlib import Path

from unittest.mock import Mock

from devcapsule.base_image import (
    NVIDIA_CUDA_ROOT_IMAGE,
    BaseImageBuildOptions,
    build_base_image,
    build_base_image_spec,
)
from devcapsule.image_build import render_build_context


def test_base_image_packages_pex_with_generic_runtime_configuration(tmp_path: Path) -> None:
    pex = tmp_path / "devcapsule.pex"
    pex.write_bytes(b"pex fixture")
    options = BaseImageBuildOptions(pex, "test-base:latest", source_revision="abc123")

    plan = build_base_image_spec(options).build_plan()
    context = tmp_path / "context"
    context.mkdir()
    dockerfile = render_build_context(plan, context).read_text(encoding="utf-8")

    assert plan.base_image == "ubuntu:24.04"
    assert "python3" in plan.apt_packages
    assert "tini" in plan.apt_packages
    assert "gosu" in plan.apt_packages
    assert "/opt/pycharm" not in dockerfile
    assert "JetBrains" not in dockerfile
    assert "nodejs.org/dist/${node_version}" in dockerfile
    assert "@google/gemini-cli" not in dockerfile
    assert "gemini --version" not in dockerfile
    assert 'ENTRYPOINT ["/usr/bin/tini", "--", "/opt/devcapsule/bin/devcapsule.pex", "runtime"]' in dockerfile
    assert 'CMD ["/etc/devcapsule/runtime-plan.json"]' in dockerfile
    assert ("devcapsule.image.managed", "true") in plan.labels
    assert ("devcapsule.metadata.version", "1") in plan.labels
    assert ("devcapsule.image.kind", "base") in plan.labels
    assert ("devcapsule.image.canonical-name", "test-base:latest") in plan.labels
    assert ("devcapsule.base.recipe", "ubuntu-24.04") in plan.labels
    assert ("devcapsule.base.recipe-version", "2") in plan.labels
    assert ("devcapsule.base.recipe-status", "ready") in plan.labels
    assert ("devcapsule.pex.sha256", hashlib.sha256(b"pex fixture").hexdigest()) in plan.labels


def test_nvidia_cuda_recipe_keeps_developer_baseline_and_is_marked_wip(tmp_path: Path) -> None:
    pex = tmp_path / "devcapsule.pex"
    pex.write_bytes(b"pex fixture")
    options = BaseImageBuildOptions(pex, "test-cuda-base:latest", recipe="nvidia-cuda-devel")

    plan = build_base_image_spec(options).build_plan()

    assert plan.base_image == NVIDIA_CUDA_ROOT_IMAGE
    assert "python3" in plan.apt_packages
    assert "gdb" in plan.apt_packages
    assert "tini" in plan.apt_packages
    install_script = "\n".join(" ".join(step.args) for step in plan.exec_steps)
    assert "@google/gemini-cli" not in install_script
    assert ("devcapsule.base.recipe", "nvidia-cuda-devel") in plan.labels
    assert ("devcapsule.base.recipe-status", "wip") in plan.labels
    assert ("devcapsule.base.gpu.vendor", "nvidia") in plan.labels
    assert ("devcapsule.base.cuda.version", "12.8.1") in plan.labels


def test_recipe_root_image_can_be_overridden(tmp_path: Path) -> None:
    pex = tmp_path / "devcapsule.pex"
    pex.write_bytes(b"pex fixture")
    options = BaseImageBuildOptions(
        pex,
        "test-cuda-base:latest",
        root_image="local/cuda:test",
        recipe="nvidia-cuda-devel",
    )

    plan = build_base_image_spec(options).build_plan()

    assert plan.base_image == "local/cuda:test"
    assert ("devcapsule.base.recipe", "nvidia-cuda-devel") in plan.labels


def test_base_image_build_forwards_host_network_to_buildx(tmp_path: Path) -> None:
    pex = tmp_path / "devcapsule.pex"
    pex.write_bytes(b"pex fixture")
    options = BaseImageBuildOptions(pex, "test-base:latest")
    builder = Mock()

    build_base_image(options, builder=builder, network="host")

    builder.build.assert_called_once()
    assert builder.build.call_args.args[0].image == "test-base:latest"
    assert builder.build.call_args.kwargs == {"network": "host"}
