from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

import pytest

from devcapsule import cli
from devcapsule.build_info import BuildInfo, BuildInfoError, current_build_info, read_pex_build_info


def test_public_build_identity_requires_canonical_github_commit_url() -> None:
    revision = "a" * 40
    info = BuildInfo(
        1,
        "1.0.0",
        "https://github.com/example/devcapsule",
        revision,
        f"https://github.com/example/devcapsule/commit/{revision}",
    )
    assert info.has_public_revision is True
    assert BuildInfo(1, "1.0.0", info.source_repository, revision, "unknown").has_public_revision is False


def test_read_pex_build_info_does_not_execute_artifact(tmp_path: Path) -> None:
    pex = tmp_path / "devcapsule.pex"
    value = {
        "schema_version": 1,
        "version": "1.0.0",
        "source_repository": "https://github.com/example/devcapsule",
        "source_revision": "b" * 40,
        "source_url": f"https://github.com/example/devcapsule/commit/{'b' * 40}",
    }
    with ZipFile(pex, "w") as archive:
        archive.writestr(".deps/package.whl/devcapsule/_build_info.json", json.dumps(value))

    assert read_pex_build_info(pex) == BuildInfo.from_mapping(value)


def test_read_pex_build_info_rejects_missing_metadata(tmp_path: Path) -> None:
    pex = tmp_path / "devcapsule.pex"
    with ZipFile(pex, "w") as archive:
        archive.writestr("PEX-INFO", "{}")
    with pytest.raises(BuildInfoError, match="exactly one"):
        read_pex_build_info(pex)


def test_source_checkout_version_command_is_machine_readable(capsys) -> None:
    assert cli.main(["version", "--json"]) == 0
    value = json.loads(capsys.readouterr().out)
    assert value == current_build_info().to_mapping()


def test_editable_install_falls_back_to_build_info_beside_module(tmp_path: Path) -> None:
    missing_resource = tmp_path / "editable-resource-root" / "_build_info.json"

    with patch("devcapsule.build_info.files") as resources:
        resources.return_value.joinpath.return_value = missing_resource
        info = current_build_info()

    assert info.version == "0.1.0"
    assert info.source_revision == "unknown"
