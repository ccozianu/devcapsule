from __future__ import annotations

import hashlib
from pathlib import Path

from devcapsule.base_image import BaseImageBuildOptions, build_base_image_spec
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
    assert 'ENTRYPOINT ["/usr/bin/tini", "--", "/opt/devcapsule/bin/devcapsule.pex", "runtime"]' in dockerfile
    assert 'CMD ["/etc/devcapsule/runtime-plan.json"]' in dockerfile
    assert ("devcapsule.pex.sha256", hashlib.sha256(b"pex fixture").hexdigest()) in plan.labels
