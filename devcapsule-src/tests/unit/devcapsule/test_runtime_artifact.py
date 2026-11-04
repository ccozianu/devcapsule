"""Unit tests of ``devcapsule.runtime_artifact``: where a launcher finds the runtime it delivers.

Every executable here is a PEX archive the test writes, behind the first bytes
of a native header, as a scie is. The launcher is a macOS executable, which runs
in no capsule, so each test chooses which Linux runtime it should deliver.
"""
from __future__ import annotations

import json
from pathlib import Path
from zipfile import ZipFile

import pytest

from devcapsule.build_info import BuildInfo
from devcapsule.compat import CliError
from devcapsule.platforms import Platform
from devcapsule.runtime_artifact import DEFAULT_RUNTIME_DIRECTORY, RUNTIME_PEX_ENV, runtime_artifact

REVISION = "a" * 40
"""The source revision of the launcher and of every runtime the tests write."""

MACH_O = b"\xcf\xfa\xed\xfe" + bytes(16)
"""The header of a 64-bit Mach-O executable."""

ELF_AMD64 = b"\x7fELF\x02\x01\x01" + bytes(11) + (0x3E).to_bytes(2, "little")
"""The header of a 64-bit x86-64 ELF executable."""


def _executable(path: Path, header: bytes) -> Path:
    """A DevCapsule 0.1.0 PEX at ``REVISION`` behind ``header``, written at ``path``."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(path, "w") as archive:
        archive.writestr(".deps/devcapsule-0.1.0-py3-none-any.whl/devcapsule/_build_info.json", json.dumps({
            "schema_version": 2, "version": "0.1.0", "build_mnemonic": "v0.1.0",
            "source_repository": "https://github.com/example/devcapsule", "source_revision": REVISION,
            "source_url": f"https://github.com/example/devcapsule/commit/{REVISION}",
        }))
    path.write_bytes(header + path.read_bytes())
    return path


@pytest.fixture
def home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """An empty home directory, and the running launcher's build is the executables' build."""
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.delenv(RUNTIME_PEX_ENV, raising=False)
    monkeypatch.delenv("PEX", raising=False)
    monkeypatch.setattr("devcapsule.runtime_artifact.current_build_info", lambda: BuildInfo(
        schema_version=2, version="0.1.0", source_repository="https://github.com/example/devcapsule",
        source_revision=REVISION, source_url="unknown"))
    return home


@pytest.fixture
def macos_launcher(home: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """The running launcher is a packaged macOS executable."""
    launcher = _executable(tmp_path / "devcapsule-macos-arm64", MACH_O)
    monkeypatch.setenv("SCIE", str(launcher))
    return launcher


def _installed(home: Path, platform: Platform) -> Path:
    """A runtime for ``platform`` in the default directory under ``home``."""
    directory = home / Path(DEFAULT_RUNTIME_DIRECTORY).relative_to("~")
    return _executable(directory / f"devcapsule-{platform}", ELF_AMD64)


def test_a_packaged_launcher_delivers_the_runtime_in_the_default_directory(home: Path, macos_launcher: Path) -> None:
    """With the variable unset and a runtime installed in the default directory, a
    linux-amd64 launch delivers that runtime."""
    installed = _installed(home, Platform.LINUX_AMD64)

    assert runtime_artifact(Platform.LINUX_AMD64) == installed.resolve()


def test_the_variable_wins_over_the_default_directory(home: Path, macos_launcher: Path, tmp_path: Path,
                                                      monkeypatch: pytest.MonkeyPatch) -> None:
    """With a runtime in the default directory and another named by the variable, a
    launch delivers the named one."""
    _installed(home, Platform.LINUX_AMD64)
    named = _executable(tmp_path / "elsewhere" / "devcapsule-linux-amd64", ELF_AMD64)
    monkeypatch.setenv(RUNTIME_PEX_ENV, str(named))

    assert runtime_artifact(Platform.LINUX_AMD64) == named.resolve()


def test_without_a_runtime_the_refusal_names_the_default_directory(home: Path, macos_launcher: Path) -> None:
    """With the variable unset and the default directory empty, a launch is refused
    with a message naming both the variable and the default directory."""
    with pytest.raises(CliError, match=rf"{RUNTIME_PEX_ENV}.*{DEFAULT_RUNTIME_DIRECTORY} as devcapsule-linux-amd64"):
        runtime_artifact(Platform.LINUX_AMD64)


def test_a_source_launcher_ignores_the_default_directory(home: Path, tmp_path: Path,
                                                         monkeypatch: pytest.MonkeyPatch) -> None:
    """A launcher running from source, with a runtime in the default directory and the
    variable unset, is refused and told to set the variable: only a packaged
    launcher, which the install script put beside its runtimes, uses the directory."""
    _installed(home, Platform.LINUX_AMD64)
    monkeypatch.delenv("SCIE", raising=False)
    source_entry = tmp_path / "devcapsule-script"
    source_entry.write_text("#!/usr/bin/env python3\n")
    monkeypatch.setattr("sys.argv", [str(source_entry)])

    with pytest.raises(CliError, match=RUNTIME_PEX_ENV):
        runtime_artifact(Platform.LINUX_AMD64)
