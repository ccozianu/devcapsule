"""Run the release's install script against a release the test writes, with no network.

The release is a directory of small shell scripts standing in for the
executables, served to the script as a ``file://`` URL. ``uname`` and
``sysctl`` are stubs ahead of the real tools on ``PATH``, so each test chooses
the computer the script installs on, whatever runs the suite.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import subprocess

import pytest

from devcapsule.platforms import Platform
from devcapsule.runtime_artifact import DEFAULT_RUNTIME_DIRECTORY

pytestmark = pytest.mark.integration

INSTALL_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "install.sh"
EXECUTABLES = ("devcapsule.pex", "devcapsule-linux-arm64", "devcapsule-macos-arm64")
"""The executables a release publishes and lists in its SHA256SUMS."""


@pytest.fixture
def release(tmp_path: Path) -> Path:
    """A release whose executables each print their own name, with a matching SHA256SUMS."""
    release = tmp_path / "release"
    release.mkdir()
    for name in EXECUTABLES:
        (release / name).write_text(f'#!/bin/sh\necho "{name} $*"\n')
    _write_checksums(release)
    return release


def _write_checksums(release: Path) -> None:
    lines = [f"{hashlib.sha256((release / name).read_bytes()).hexdigest()}  {name}\n" for name in EXECUTABLES]
    (release / "SHA256SUMS").write_text("".join(lines))


def _install(tmp_path: Path, release: Path | None, system: str, machine: str,
             apple_silicon: bool = False) -> tuple[subprocess.CompletedProcess[str], Path]:
    """Run the install script as ``system``/``machine`` with an empty home; return the run and the home."""
    stubs = tmp_path / "stubs"
    stubs.mkdir(exist_ok=True)
    (stubs / "uname").write_text(f'#!/bin/sh\ncase "$1" in -s) echo {system};; -m) echo {machine};; esac\n')
    (stubs / "sysctl").write_text(f"#!/bin/sh\necho {1 if apple_silicon else 0}\n")
    for stub in stubs.iterdir():
        stub.chmod(0o755)
    home = tmp_path / "home"
    home.mkdir()
    environment = {key: value for key, value in os.environ.items()
                   if key not in ("DEVCAPSULE_RELEASE_URL", "DEVCAPSULE_RUNTIME_PEX")}
    environment.update(HOME=str(home), PATH=f"{stubs}{os.pathsep}{os.environ['PATH']}")
    if release is not None:
        environment["DEVCAPSULE_RELEASE_URL"] = release.as_uri()
    run = subprocess.run(["sh", str(INSTALL_SCRIPT)], env=environment, capture_output=True, text=True,
                         check=False, timeout=60)
    return run, home


def _installed_files(home: Path) -> set[str]:
    return {str(path.relative_to(home)) for path in home.rglob("*") if path.is_file()}


@pytest.mark.parametrize("system,machine,executable", [
    ("Linux", "x86_64", "devcapsule.pex"),
    ("Linux", "aarch64", "devcapsule-linux-arm64"),
])
def test_a_linux_computer_gets_its_own_executable_and_nothing_else(
    tmp_path: Path, release: Path, system: str, machine: str, executable: str,
) -> None:
    """On Linux the script installs the executable for the machine as
    ~/.local/bin/devcapsule, runs its version command, and installs no runtimes."""
    run, home = _install(tmp_path, release, system, machine)

    assert run.returncode == 0, run.stderr
    assert _installed_files(home) == {".local/bin/devcapsule"}
    assert (home / ".local/bin/devcapsule").read_text() == (release / executable).read_text()
    assert f"{executable} version" in run.stdout


def test_an_apple_silicon_mac_gets_the_launcher_and_both_linux_runtimes_where_the_launcher_looks(
    tmp_path: Path, release: Path,
) -> None:
    """On an Apple Silicon Mac the script installs the macOS launcher and each Linux
    executable as devcapsule-<platform> in the directory the launcher reads by default,
    even from a shell under Rosetta that reports x86_64."""
    run, home = _install(tmp_path, release, "Darwin", "x86_64", apple_silicon=True)

    runtimes = home / Path(DEFAULT_RUNTIME_DIRECTORY).relative_to("~")
    assert run.returncode == 0, run.stderr
    assert (home / ".local/bin/devcapsule").read_text() == (release / "devcapsule-macos-arm64").read_text()
    assert (runtimes / f"devcapsule-{Platform.LINUX_AMD64}").read_text() == (release / "devcapsule.pex").read_text()
    assert (runtimes / f"devcapsule-{Platform.LINUX_ARM64}").read_text() == (
        release / "devcapsule-linux-arm64").read_text()
    assert all(os.access(home / path, os.X_OK) for path in _installed_files(home))


def test_a_download_that_does_not_match_its_checksum_installs_nothing(tmp_path: Path, release: Path) -> None:
    """When one executable differs from the release's SHA256SUMS the script fails,
    names the file, and installs nothing at all, not even the files already verified."""
    with (release / "devcapsule-linux-arm64").open("a") as tampered:
        tampered.write("# changed\n")

    run, home = _install(tmp_path, release, "Darwin", "arm64", apple_silicon=True)

    assert run.returncode != 0
    assert "devcapsule-linux-arm64 does not match its SHA-256 checksum" in run.stderr
    assert _installed_files(home) == set()


@pytest.mark.parametrize("system,machine", [("Darwin", "x86_64"), ("FreeBSD", "amd64")])
def test_a_computer_without_an_executable_is_refused(
    tmp_path: Path, release: Path, system: str, machine: str,
) -> None:
    """An Intel Mac or an operating system with no executable is refused before any
    download, and nothing is installed."""
    run, home = _install(tmp_path, release, system, machine)

    assert run.returncode != 0
    assert run.stderr.startswith("devcapsule install: ")
    assert _installed_files(home) == set()


def test_the_unreleased_template_names_no_release(tmp_path: Path) -> None:
    """The script as it is in the repository, before a release writes its URL in,
    refuses to run rather than download from a placeholder."""
    run, home = _install(tmp_path, None, "Linux", "x86_64")

    assert run.returncode != 0
    assert "names no release" in run.stderr
    assert _installed_files(home) == set()
