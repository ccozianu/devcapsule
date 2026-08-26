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
    package = root / "devcapsule"
    package.mkdir(parents=True)
    (root / "pyproject.toml").write_text(
        f'[build-system]\nrequires = ["setuptools"]\n\n[project]\n'
        f'name = "devcapsule"\nversion = "{version}"\n',
        encoding="utf-8",
    )
    (package / "__init__.py").write_text(
        f'"""Test package."""\n\n__version__ = "{version}"\n', encoding="utf-8"
    )
    (package / "_build_info.json").write_text(
        f'{{"build_mnemonic":"v{version}-local","schema_version":2,"version":"{version}"}}\n',
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
def test_bump_updates_every_distribution_version_source(
    tmp_path: Path, requested: str, expected: str
) -> None:
    root = project(tmp_path)

    assert VERSION_MODULE.bump_version(requested, root) == ("1.2.3", expected)

    assert VERSION_MODULE.checked_version(root) == expected
    assert f'version = "{expected}"' in (root / "pyproject.toml").read_text(
        encoding="utf-8"
    )
    assert f'__version__ = "{expected}"' in (
        root / "devcapsule" / "__init__.py"
    ).read_text(encoding="utf-8")
    build_info = (root / "devcapsule" / "_build_info.json").read_text(encoding="utf-8")
    assert f'"version":"{expected}"' in build_info
    assert f'"build_mnemonic":"v{expected}-local"' in build_info


@pytest.mark.parametrize("requested", ["1.2.3", "1.2.2", "v1.2.4", "banana"])
def test_bump_rejects_non_advancing_or_invalid_versions(
    tmp_path: Path, requested: str
) -> None:
    root = project(tmp_path)

    with pytest.raises(VERSION_MODULE.VersionError):
        VERSION_MODULE.bump_version(requested, root)

    assert VERSION_MODULE.checked_version(root) == "1.2.3"


def test_check_rejects_disagreeing_version_sources(tmp_path: Path) -> None:
    root = project(tmp_path)
    (root / "devcapsule" / "__init__.py").write_text(
        '__version__ = "9.9.9"\n', encoding="utf-8"
    )

    with pytest.raises(VERSION_MODULE.VersionError, match="versions disagree"):
        VERSION_MODULE.checked_version(root)


def test_check_rejects_stale_editable_build_mnemonic(tmp_path: Path) -> None:
    root = project(tmp_path)
    (root / "devcapsule" / "_build_info.json").write_text(
        '{"build_mnemonic":"local-v026","schema_version":2,"version":"1.2.3"}\n',
        encoding="utf-8",
    )

    with pytest.raises(VERSION_MODULE.VersionError, match="build_mnemonic"):
        VERSION_MODULE.checked_version(root)
