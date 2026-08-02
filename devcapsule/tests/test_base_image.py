from __future__ import annotations

import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

import pytest
from unittest.mock import Mock

from devcapsule.base_image import (
    NVIDIA_CUDA_ROOT_IMAGE,
    BaseImageBuildOptions,
    build_base_image,
    build_base_image_spec,
)
from devcapsule.compat import CliError
from devcapsule.image_build import render_build_context


def pex_fixture(path: Path, *, revision: str = "a" * 40, public: bool = True) -> Path:
    repository = "https://github.com/example/devcapsule" if public else "unknown"
    source_url = f"{repository}/commit/{revision}" if public else "unknown"
    with ZipFile(path, "w") as archive:
        archive.writestr(
            ".deps/devcapsule-0.1.0-py3-none-any.whl/devcapsule/_build_info.json",
            json.dumps(
                {
                    "schema_version": 1,
                    "version": "0.1.0",
                    "source_repository": repository,
                    "source_revision": revision,
                    "source_url": source_url,
                }
            ),
        )
    return path


def test_base_image_packages_pex_with_generic_runtime_configuration(tmp_path: Path) -> None:
    pex = pex_fixture(tmp_path / "devcapsule.pex")
    options = BaseImageBuildOptions(pex, "test-base:latest", source_revision="a" * 40)

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
    assert ("devcapsule.pex.sha256", hashlib.sha256(pex.read_bytes()).hexdigest()) in plan.labels
    assert ("devcapsule.source.repository", "https://github.com/example/devcapsule") in plan.labels
    assert ("devcapsule.source.revision", "a" * 40) in plan.labels
    assert (
        "devcapsule.source.url",
        f"https://github.com/example/devcapsule/commit/{'a' * 40}",
    ) in plan.labels
    assert ("org.opencontainers.image.source", "https://github.com/example/devcapsule") in plan.labels
    assert ("org.opencontainers.image.revision", "a" * 40) in plan.labels


def test_nvidia_cuda_recipe_keeps_developer_baseline_and_is_marked_wip(tmp_path: Path) -> None:
    pex = pex_fixture(tmp_path / "devcapsule.pex")
    options = BaseImageBuildOptions(
        pex, "test-cuda-base:latest", source_revision="a" * 40, recipe="nvidia-cuda-devel"
    )

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
    pex = pex_fixture(tmp_path / "devcapsule.pex")
    options = BaseImageBuildOptions(
        pex,
        "test-cuda-base:latest",
        root_image="local/cuda:test",
        source_revision="a" * 40,
        recipe="nvidia-cuda-devel",
    )

    plan = build_base_image_spec(options).build_plan()

    assert plan.base_image == "local/cuda:test"
    assert ("devcapsule.base.recipe", "nvidia-cuda-devel") in plan.labels


def test_base_image_build_forwards_host_network_to_buildx(tmp_path: Path) -> None:
    pex = pex_fixture(tmp_path / "devcapsule.pex")
    options = BaseImageBuildOptions(pex, "test-base:latest", source_revision="a" * 40)
    builder = Mock()

    build_base_image(options, builder=builder, network="host")

    builder.build.assert_called_once()
    assert builder.build.call_args.args[0].image == "test-base:latest"
    assert builder.build.call_args.kwargs == {"network": "host"}


def test_base_image_rejects_revision_that_disagrees_with_pex(tmp_path: Path) -> None:
    pex = pex_fixture(tmp_path / "devcapsule.pex")
    options = BaseImageBuildOptions(pex, source_revision="b" * 40)

    with pytest.raises(CliError, match="devcapsule-local.pex"):
        build_base_image_spec(options)


def test_base_image_requires_explicit_source_revision_by_default(tmp_path: Path) -> None:
    pex = pex_fixture(tmp_path / "devcapsule.pex")

    with pytest.raises(CliError, match="--source-revision is required"):
        build_base_image_spec(BaseImageBuildOptions(pex))


def test_base_image_requires_public_pex_revision_by_default(tmp_path: Path) -> None:
    pex = pex_fixture(tmp_path / "devcapsule.pex", revision="unknown", public=False)
    options = BaseImageBuildOptions(pex, source_revision="unknown")

    with pytest.raises(CliError, match="does not embed a full public GitHub revision"):
        build_base_image_spec(options)


def test_base_image_allows_explicit_local_source_escape_hatch(tmp_path: Path) -> None:
    pex = pex_fixture(tmp_path / "devcapsule.pex", revision="unknown", public=False)
    plan = build_base_image_spec(BaseImageBuildOptions(pex, allow_local_source=True)).build_plan()

    assert ("devcapsule.source.revision", "unknown") in plan.labels
