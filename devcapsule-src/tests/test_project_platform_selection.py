"""The capsule platform a project runs as: its locks decide, or --platform names one."""

from __future__ import annotations

from pathlib import Path

import pytest

from devcapsule import cli, platforms
from devcapsule.configuration.storage import project_platform
from devcapsule.platforms import Platform


def _host(monkeypatch: pytest.MonkeyPatch, system: str, machine: str) -> None:
    monkeypatch.setattr(platforms.host_platform, "system", lambda: system)
    monkeypatch.setattr(platforms.host_platform, "machine", lambda: machine)


def _project(root: Path, *locked: str) -> Path:
    (root / ".devcapsule").mkdir(parents=True)
    (root / ".devcapsule" / "devcapsule.toml").write_text("")
    for platform in locked:
        (root / ".devcapsule" / f"devcapsule.{platform}.lock").write_text("")
    return root


@pytest.mark.own_host_patches
@pytest.mark.parametrize("locked,expected", [
    ((), "linux-amd64"),
    (("linux-amd64",), "linux-amd64"),
    (("linux-arm64",), "linux-arm64"),
    (("linux-amd64", "linux-arm64"), "linux-arm64"),
])
def test_apple_silicon_runs_a_project_as_the_platform_it_is_locked_for(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, locked: tuple[str, ...], expected: str,
) -> None:
    # The human's ruling of 2026-11-04: natively when the project has an
    # arm64 lock, else its amd64 lock under emulation; a new project amd64.
    _host(monkeypatch, "Darwin", "arm64")
    assert project_platform(_project(tmp_path / "project", *locked)) is Platform.parse(expected)


@pytest.mark.own_host_patches
def test_a_host_runs_a_project_only_as_a_platform_it_runs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # An amd64 Linux host cannot run an arm64-only project; it keeps its own
    # platform, and the missing lock is reported where the lock is read.
    _host(monkeypatch, "Linux", "x86_64")
    assert project_platform(_project(tmp_path / "project", "linux-arm64")) is Platform.LINUX_AMD64
    assert project_platform(None) is Platform.LINUX_AMD64


def _platform_seen_by(arguments: list[str], monkeypatch: pytest.MonkeyPatch) -> Platform:
    seen: list[Platform] = []

    def record(cls: object, arguments: object, context: object) -> int:
        seen.append(project_platform(Path(str(getattr(context, "selected_path")))))
        return 0

    monkeypatch.setattr("devcapsule.commands.project.ProjectInfoCommand.run", classmethod(record))
    assert cli.main(arguments) == 0
    return seen[0]


@pytest.mark.own_host_patches
def test_platform_option_names_the_platform_for_one_command(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # `project --platform linux-arm64 init` is how an amd64 project gains an
    # arm64 lock; `--platform linux-amd64` runs it under emulation on purpose.
    _host(monkeypatch, "Darwin", "arm64")
    amd64_only = _project(tmp_path / "amd64", "linux-amd64")
    both = _project(tmp_path / "both", "linux-amd64", "linux-arm64")
    assert _platform_seen_by(["project", "--path", str(both), "info"], monkeypatch) is Platform.LINUX_ARM64
    assert _platform_seen_by(["project", "--platform", "linux-arm64", "--path", str(amd64_only), "info"],
                             monkeypatch) is Platform.LINUX_ARM64
    assert _platform_seen_by(["project", "--platform", "linux-amd64", "--path", str(both), "info"],
                             monkeypatch) is Platform.LINUX_AMD64


def test_platform_option_refuses_a_platform_this_host_cannot_run(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    # The suite's host runs linux-amd64 only.
    project = _project(tmp_path / "project", "linux-amd64")
    assert cli.main(["project", "--platform", "linux-arm64", "--path", str(project), "info"]) != 0
    assert "This host runs linux-amd64 capsules, not linux-arm64." in capsys.readouterr().err
    assert cli.main(["project", "--platform", "windows-amd64", "--path", str(project), "info"]) != 0
    assert "Unsupported platform 'windows-amd64'" in capsys.readouterr().err
