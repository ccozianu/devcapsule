from __future__ import annotations

import hashlib
import io
from pathlib import Path
import tarfile

import pytest

from devcapsule.compat import CliError
from devcapsule.materialization import (
    ArtifactSpec,
    acquire_artifact,
    ensure_materialized_pycharm,
    materialization_identity,
    pycharm_materialization_spec,
)


def fixture_archive(path: Path) -> bytes:
    content = b"#!/bin/sh\n"
    with tarfile.open(path, "w:gz") as archive:
        info = tarfile.TarInfo("pycharm-test/bin/pycharm.sh")
        info.mode = 0o755
        info.size = len(content)
        archive.addfile(info, io.BytesIO(content))
    return path.read_bytes()


def test_acquisition_verifies_digest_and_reuses_cache(tmp_path: Path) -> None:
    source = tmp_path / "source.tar.gz"
    payload = fixture_archive(source)
    spec = ArtifactSpec("test", source.as_uri(), hashlib.sha256(payload).hexdigest())

    first = acquire_artifact(spec, tmp_path / "cache")
    second = acquire_artifact(spec, tmp_path / "cache")

    assert first.downloaded is True
    assert second.downloaded is False
    assert second.path == first.path


def test_acquisition_rejects_digest_mismatch(tmp_path: Path) -> None:
    source = tmp_path / "source.tar.gz"
    fixture_archive(source)
    spec = ArtifactSpec("test", source.as_uri(), "0" * 64)
    with pytest.raises(CliError, match="digest mismatch"):
        acquire_artifact(spec, tmp_path / "cache")


def test_materialization_skips_download_and_build_when_image_exists(tmp_path: Path) -> None:
    spec = ArtifactSpec("test", (tmp_path / "missing.tar.gz").as_uri(), "1" * 64)
    builds: list[object] = []
    image, created = ensure_materialized_pycharm(
        base_image="base@sha256:abc",
        artifact=spec,
        cache_root=tmp_path / "cache",
        image_exists=lambda _image: True,
        build=builds.append,
    )
    assert image.startswith("devcapsule-local-pycharm:")
    assert created is False
    assert builds == []


def test_materialized_image_has_managed_identity_labels(tmp_path: Path) -> None:
    pycharm = tmp_path / "pycharm"
    pycharm.mkdir()
    runtime_plan = tmp_path / "runtime-plan.json"
    runtime_plan.write_text("{}\n", encoding="utf-8")
    artifact = ArtifactSpec("2026.2", "https://example.test/pycharm.tar.gz", "a" * 64)
    image = "devcapsule-local-pycharm:0123456789abcdef0123"

    plan = pycharm_materialization_spec(
        base_image="base@sha256:abc",
        image=image,
        pycharm_root=pycharm,
        runtime_plan=runtime_plan,
        artifact=artifact,
    ).build_plan()

    assert ("devcapsule.image.managed", "true") in plan.labels
    assert ("devcapsule.metadata.version", "1") in plan.labels
    assert ("devcapsule.image.kind", "materialized") in plan.labels
    assert ("devcapsule.image.canonical-name", image) in plan.labels
    assert ("devcapsule.materialization.base-identity", "base@sha256:abc") in plan.labels
    assert ("devcapsule.materialization.identity", materialization_identity("base@sha256:abc", artifact)) in plan.labels
    assert ("devcapsule.component.id", "pycharm") in plan.labels
    assert ("devcapsule.component.version", "2026.2") in plan.labels
    assert ("devcapsule.component.sha256", "a" * 64) in plan.labels
