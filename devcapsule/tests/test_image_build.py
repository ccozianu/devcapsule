from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from devcapsule.compat import CliError
from devcapsule.configurations.pycharm._image_build import (
    PycharmImageBuildOptions,
    build_pycharm_image_spec,
    parse_pycharm_build_options,
)
from devcapsule.image_build import BuildxImageBuilder, ImageBuildSpec, normalize_pycharm_source, render_build_context


def test_parse_pycharm_build_options_rejects_missing_source(tmp_path: Path) -> None:
    with pytest.raises(CliError, match="does not exist"):
        parse_pycharm_build_options(
            pycharm=tmp_path / "missing.tar.gz",
            image="pycharm-isolated:latest",
            base_image="ubuntu:24.04",
            network="default",
            extra_apt_packages=(),
        )


def test_parse_pycharm_build_options_accepts_host_network(tmp_path: Path) -> None:
    source = tmp_path / "pycharm"
    source.mkdir()

    options = parse_pycharm_build_options(
        pycharm=source,
        image="pycharm-isolated:latest",
        base_image="ubuntu:24.04",
        network="host",
        extra_apt_packages=(),
    )

    assert options.network == "host"


def test_build_pycharm_image_spec_includes_runtime_assets_and_node_tooling(tmp_path: Path) -> None:
    source = tmp_path / "pycharm"
    source.mkdir()
    assets = tmp_path / "assets"
    (assets / "image-assets").mkdir(parents=True)
    for filename in ("entrypoint.sh", "bootstrap-project.sh", "check-runtime-deps.sh"):
        (assets / filename).write_text("#!/usr/bin/env bash\n", encoding="utf-8")
    (assets / "image-assets" / "vibe-coding-process.md").write_text("vibe\n", encoding="utf-8")

    spec = build_pycharm_image_spec(
        PycharmImageBuildOptions(
            pycharm=source,
            image="example:latest",
            base_image="ubuntu:24.04",
            network="default",
            extra_apt_packages=("rsync",),
        ),
        pycharm_root=source,
        assets_root=assets,
    )
    plan = spec.build_plan()

    assert plan.base_image == "ubuntu:24.04"
    assert plan.image == "example:latest"
    assert "rsync" in plan.apt_packages
    assert any(copy.destination == "/opt/pycharm" and copy.source == source for copy in plan.directories)
    assert any(copy.destination == "/usr/local/bin/entrypoint.sh" for copy in plan.files)
    assert plan.entrypoint == ("/usr/bin/tini", "--", "/usr/local/bin/entrypoint.sh")
    assert ("devcapsule.builder", "python-on-whales") in plan.labels
    install_script = "\n".join(" ".join(step.args) for step in plan.exec_steps)
    assert "nodejs.org/dist/${node_version}" in install_script
    assert 'export PATH="/opt/node/current/bin:$PATH"' in install_script
    assert "@google/gemini-cli" not in install_script
    assert "SHASUMS256.txt" in install_script
    assert "gemini --version" not in install_script
    assert ( "PATH", "/opt/node/current/bin:${PATH}") in plan.env


def test_normalize_pycharm_source_requires_executable_launcher(tmp_path: Path) -> None:
    source = tmp_path / "pycharm"
    (source / "bin").mkdir(parents=True)
    launcher = source / "bin" / "pycharm.sh"
    launcher.write_text("#!/usr/bin/env bash\n", encoding="utf-8")

    with pytest.raises(CliError, match="executable bin/pycharm.sh"):
        normalize_pycharm_source(source, tmp_path / "work")


def test_render_build_context_includes_network_host_compatible_dockerfile_content(tmp_path: Path) -> None:
    source = tmp_path / "pycharm"
    source.mkdir()
    assets = tmp_path / "assets"
    (assets / "image-assets").mkdir(parents=True)
    for filename in ("entrypoint.sh", "bootstrap-project.sh", "check-runtime-deps.sh"):
        (assets / filename).write_text("#!/usr/bin/env bash\n", encoding="utf-8")
    (assets / "image-assets" / "vibe-coding-process.md").write_text("vibe\n", encoding="utf-8")

    spec = build_pycharm_image_spec(
        PycharmImageBuildOptions(
            pycharm=source,
            image="example:latest",
            base_image="ubuntu:24.04",
            network="host",
            extra_apt_packages=("rsync",),
        ),
        pycharm_root=source,
        assets_root=assets,
    )

    dockerfile = render_build_context(spec.build_plan(), tmp_path / "context").read_text(encoding="utf-8")

    assert "FROM ubuntu:24.04" in dockerfile
    assert "COPY copy-dir-0/ /opt/pycharm/" in dockerfile
    assert 'LABEL devcapsule.builder="python-on-whales"' in dockerfile
    assert 'ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/entrypoint.sh"]' in dockerfile


def test_buildx_builder_can_place_large_context_outside_system_tmp(tmp_path: Path) -> None:
    context_root = tmp_path / "large-contexts"
    with patch("devcapsule.image_build.docker.build") as build:
        BuildxImageBuilder(temporary_root=context_root).build(
            ImageBuildSpec(image="result:test", base_image="sha256:base"),
            network="none",
        )

    used_context = build.call_args.args[0]
    assert used_context.parent == context_root
    assert build.call_args.kwargs["network"] == "none"
