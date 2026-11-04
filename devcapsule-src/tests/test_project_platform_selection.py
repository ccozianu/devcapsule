"""The capsule platform a project command runs as, chosen by the project's locks or by --platform."""

from __future__ import annotations

from pathlib import Path

import pytest

from devcapsule import cli
from devcapsule.platforms import Platform


def _apple_silicon(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(Platform, "runnable", classmethod(lambda cls: (Platform.LINUX_ARM64, Platform.LINUX_AMD64)))


def _project(root: Path, *platforms: str) -> Path:
    (root / ".devcapsule").mkdir(parents=True)
    (root / ".devcapsule" / "devcapsule.toml").write_text("")
    for platform in platforms:
        (root / ".devcapsule" / f"devcapsule.{platform}.lock").write_text("")
    return root


def _selected_by(arguments: list[str], monkeypatch: pytest.MonkeyPatch) -> Platform:
    seen: list[Platform] = []

    def record(cls: object, arguments: object, context: object) -> int:
        seen.append(Platform.current())
        return 0

    monkeypatch.setattr("devcapsule.commands.project.ProjectInfoCommand.run", classmethod(record))
    assert cli.main(arguments) == 0
    return seen[0]


def test_a_project_command_runs_as_the_platform_the_project_is_locked_for(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    _apple_silicon(monkeypatch)
    amd64_only = _project(tmp_path / "amd64", "linux-amd64")
    both = _project(tmp_path / "both", "linux-amd64", "linux-arm64")
    assert _selected_by(["project", "--path", str(amd64_only), "info"], monkeypatch) is Platform.LINUX_AMD64
    assert _selected_by(["project", "--path", str(both), "info"], monkeypatch) is Platform.LINUX_ARM64


def test_platform_option_names_the_platform_for_one_command(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # `project --platform linux-arm64 init` is how an amd64 project gains an
    # arm64 lock; `--platform linux-amd64` runs it under emulation on purpose.
    _apple_silicon(monkeypatch)
    amd64_only = _project(tmp_path / "amd64", "linux-amd64")
    both = _project(tmp_path / "both", "linux-amd64", "linux-arm64")
    assert _selected_by(["project", "--platform", "linux-arm64", "--path", str(amd64_only), "info"],
                        monkeypatch) is Platform.LINUX_ARM64
    assert _selected_by(["project", "--platform", "linux-amd64", "--path", str(both), "info"],
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
