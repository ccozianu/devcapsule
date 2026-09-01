from __future__ import annotations

from importlib.metadata import version as distribution_version
import json
from pathlib import Path
import tomllib
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


def test_build_information_accepts_release_and_local_mnemonics() -> None:
    common = {
        "schema_version": 2,
        "version": "1.0.0",
        "source_repository": "unknown",
        "source_revision": "unknown",
        "source_url": "unknown",
    }

    # Current derived forms: an official tag, an editable-source label, and a
    # contributor binary label carrying its target platform.
    for mnemonic in ("v0.2.7", "v0.2.7-local", "v0.2.7-local-linux-x86_64"):
        assert BuildInfo.from_mapping({**common, "build_mnemonic": mnemonic}).build_mnemonic == mnemonic
    # v026-era artifacts remain readable (R-COMPAT-001).
    assert BuildInfo.from_mapping({**common, "build_mnemonic": "v026"}).build_mnemonic == "v026"
    assert (
        BuildInfo.from_mapping({**common, "build_mnemonic": "local-v026"}).build_mnemonic
        == "local-v026"
    )


def test_build_information_rejects_unrecognizable_mnemonic() -> None:
    with pytest.raises(BuildInfoError, match="build_mnemonic"):
        BuildInfo.from_mapping(
            {
                "schema_version": 2,
                "version": "1.0.0",
                "build_mnemonic": "development",
                "source_repository": "unknown",
                "source_revision": "unknown",
                "source_url": "unknown",
            }
        )


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


def test_absent_build_record_means_source_form(tmp_path: Path) -> None:
    # Only build-pex.sh creates _build_info.json, so its absence is the
    # definition of a source-form run: identity derives from the version
    # pyproject.toml alone authors.
    missing_resource = tmp_path / "editable-resource-root" / "_build_info.json"
    authored = tomllib.loads(
        (Path(__file__).parents[1] / "pyproject.toml").read_text(encoding="utf-8")
    )["project"]["version"]

    with patch("devcapsule.build_info.files") as resources:
        resources.return_value.joinpath.return_value = missing_resource
        info = current_build_info()

    assert info.version == authored
    assert info.build_mnemonic == f"v{authored}-local"
    assert info.source_revision == "unknown"
    assert info.source_repository == "unknown"
    assert info.source_url == "unknown"


def test_source_form_without_a_checkout_uses_installed_metadata(
    tmp_path: Path,
) -> None:
    # Outside a source checkout (no authored pyproject.toml beside the
    # package) the installed distribution metadata answers instead.
    missing_resource = tmp_path / "editable-resource-root" / "_build_info.json"

    with (
        patch("devcapsule.build_info.files") as resources,
        patch(
            "devcapsule.build_info._SOURCE_PYPROJECT",
            tmp_path / "absent" / "pyproject.toml",
        ),
    ):
        resources.return_value.joinpath.return_value = missing_resource
        info = current_build_info()

    package_version = distribution_version("devcapsule")
    assert info.version == package_version
    assert info.build_mnemonic == f"v{package_version}-local"


def test_malformed_build_record_stays_an_error(tmp_path: Path) -> None:
    # A present record marks a built artifact; corruption must surface, not
    # quietly demote the artifact to source form.
    malformed = tmp_path / "_build_info.json"
    malformed.write_text("not json", encoding="utf-8")

    with patch("devcapsule.build_info.files") as resources:
        resources.return_value.joinpath.return_value = malformed
        with pytest.raises(BuildInfoError, match="not valid JSON"):
            current_build_info()
