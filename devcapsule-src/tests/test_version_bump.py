from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "bump-version.py"
SPEC = importlib.util.spec_from_file_location("devcapsule_bump_version", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
VERSION_MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERSION_MODULE)


def project(tmp_path: Path, *, version: str = "1.2.3") -> Path:
    root = tmp_path / "devcapsule-src"
    root.mkdir(parents=True)
    (root / "pyproject.toml").write_text(
        f'[build-system]\nrequires = ["setuptools"]\n\n[project]\n'
        f'name = "devcapsule"\nversion = "{version}"\n',
        encoding="utf-8",
    )
    return root


@pytest.mark.parametrize(
    ("requested", "expected"),
    [
        ("patch", "1.2.4"),
        ("minor", "1.3.0"),
        ("major", "2.0.0"),
        ("1.4.2", "1.4.2"),
    ],
)
def test_bump_updates_the_single_authored_version(
    tmp_path: Path, requested: str, expected: str
) -> None:
    root = project(tmp_path)

    assert VERSION_MODULE.bump_version(requested, root) == ("1.2.3", expected)

    assert VERSION_MODULE.checked_version(root) == expected
    assert f'version = "{expected}"' in (root / "pyproject.toml").read_text(
        encoding="utf-8"
    )


@pytest.mark.parametrize("requested", ["1.2.3", "1.2.2", "v1.2.4", "banana"])
def test_bump_rejects_non_advancing_or_invalid_versions(
    tmp_path: Path, requested: str
) -> None:
    root = project(tmp_path)

    with pytest.raises(VERSION_MODULE.VersionError):
        VERSION_MODULE.bump_version(requested, root)

    assert VERSION_MODULE.checked_version(root) == "1.2.3"


def test_check_rejects_malformed_version(tmp_path: Path) -> None:
    root = project(tmp_path, version="1.2.3rc1")

    with pytest.raises(VERSION_MODULE.VersionError, match="MAJOR.MINOR.PATCH"):
        VERSION_MODULE.checked_version(root)


def test_check_rejects_ambiguous_version_authorship(tmp_path: Path) -> None:
    root = project(tmp_path)
    path = root / "pyproject.toml"
    path.write_text(
        path.read_text(encoding="utf-8") + 'version = "9.9.9"\n', encoding="utf-8"
    )

    with pytest.raises(VERSION_MODULE.VersionError, match="exactly one"):
        VERSION_MODULE.checked_version(root)
