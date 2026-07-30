from __future__ import annotations

import hashlib
import io
from pathlib import Path
import tarfile

import pytest

from devcapsule.compat import CliError
from devcapsule.materialization import ArtifactSpec, acquire_artifact, ensure_materialized_pycharm


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
