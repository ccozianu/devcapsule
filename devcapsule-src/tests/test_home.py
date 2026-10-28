"""The project-independent home command contract."""
import io
from pathlib import Path
import tomllib

import pytest

from devcapsule import cli, runtime_configuration
from devcapsule.configuration.storage import load_workstation, settings_path
from devcapsule.configuration.trust import channels_for, WorkstationTrust
from devcapsule.configuration.home_channels import known_channels
from devcapsule.platforms import Platform
from devcapsule.resolution_matrix import MATRICES


@pytest.fixture
def home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    empty = tmp_path / "empty"
    empty.mkdir()
    monkeypatch.chdir(empty)
    root = tmp_path / "chosen"
    monkeypatch.setenv("DEVCAPSULE_CONFIG_HOME", str(root))
    return root


def test_empty_show_and_list_do_not_create_home(home: Path, capsys) -> None:
    assert cli.main(["home", "show"]) == 0
    output = capsys.readouterr().out
    assert str(home) in output and "DEVCAPSULE_CONFIG_HOME" in output
    assert "minimum-devcapsule: (not recorded)" in output
    assert "Defaults: none" in output and "No accepted channels" in output
    assert cli.main(["home", "trust", "list"]) == 0
    assert not home.exists()


def test_setup_show_and_withdraw(home: Path, capsys) -> None:
    for channel in ("devcapsule-base", "claude-code"):
        assert cli.main(["home", "trust", "accept", channel, "--yes"]) == 0
    for name, value in (("memory", "8GiB"), ("cpus", "4")):
        assert cli.main(["home", "default", name, value]) == 0
    capsys.readouterr()
    assert cli.main(["home", "show"]) == 0
    output = capsys.readouterr().out
    assert "minimum-devcapsule: 0.3.0" in output and "devcapsule-settings-schema-version: 1" in output
    assert "memory = 8GiB" in output and "cpus = 4" in output
    assert "claude-code: Anthropic — Claude Code; from https://downloads.claude.ai; accepted " in output
    assert cli.main(["home", "trust", "list"]) == 0
    assert "claude-code" in capsys.readouterr().out
    assert cli.main(["home", "trust", "withdraw", "claude-code"]) == 0
    before = settings_path().read_bytes(), settings_path().stat().st_mtime_ns
    assert cli.main(["home", "trust", "withdraw", "claude-code"]) == 0
    assert "No acceptance recorded" in capsys.readouterr().out
    assert (settings_path().read_bytes(), settings_path().stat().st_mtime_ns) == before
    assert load_workstation()["defaults"] == {"cpus": 4, "memory": "8GiB"}


def test_accept_confirmation_and_unknown_channel(home: Path, monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO("N\n"))
    assert cli.main(["home", "trust", "accept", "devcapsule-base"]) == 0
    output = capsys.readouterr().out
    assert "Accept for this DevCapsule home? [y/N]" in output
    assert str(home) in output and "Anyone who uses this home" in output
    assert not home.exists()
    assert cli.main(["home", "trust", "accept", "unknown", "--yes"]) == 2
    error = capsys.readouterr().err
    assert "Unknown channel" in error and "devcapsule-base" in error and "claude-code" in error
    assert not home.exists()
    monkeypatch.setattr("sys.stdin", io.StringIO("y\n"))
    assert cli.main(["home", "trust", "accept", "claude-code"]) == 0
    assert "https://www.anthropic.com/legal/commercial-terms" in capsys.readouterr().out
    assert "claude-code" in load_workstation()["trust"]["channels"]


def test_matrix_channel_equals_rendered_lock_and_saved_acceptance(home: Path) -> None:
    matrix = MATRICES[Platform.current()]
    lock = tomllib.loads(matrix.resolve(["python-ide", "claude-code-agent"]).render_lock())
    channel = channels_for(lock)["claude-code"]
    assert known_channels()["claude-code"] == channel
    assert cli.main(["home", "trust", "accept", "claude-code", "--yes"]) == 0
    assert WorkstationTrust.read(load_workstation()).covers(channel)


def test_default_replace_remove_and_invalid_values(home: Path) -> None:
    assert cli.main(["home", "default", "cpus", "2"]) == 0
    assert cli.main(["home", "default", "cpus", "4"]) == 0
    assert load_workstation()["defaults"]["cpus"] == 4
    before = settings_path().read_bytes()
    for name, value in (("cpus", "0"), ("memory", "bad"), ("other", "2")):
        assert cli.main(["home", "default", name, value]) == 2
        assert settings_path().read_bytes() == before
    assert cli.main(["home", "default", "cpus", "none"]) == 0
    assert load_workstation()["defaults"] == {}


@pytest.mark.parametrize("arguments", [["default", "cpus", "2"], ["trust", "accept", "devcapsule-base"],
                                       ["trust", "withdraw", "devcapsule-base"]])
def test_capsule_reads_and_refuses_mutation(home: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys, arguments: list[str]) -> None:
    assert cli.main(["home", "default", "cpus", "4"]) == 0
    context = tmp_path / "context.json"
    context.write_text('{"format": 1}')
    monkeypatch.setattr(runtime_configuration, "CONTEXT_PATH", context)
    monkeypatch.setattr(runtime_configuration, "HOME_PATH", home)
    before = settings_path().read_bytes()
    assert cli.main(["home", "show"]) == 0
    assert cli.main(["home", "trust", "list"]) == 0
    assert cli.main(["home", *arguments]) == 2
    error = capsys.readouterr().err
    assert "configuration is read-only" in error
    assert "devcapsule home " + " ".join(arguments) in error
    assert settings_path().read_bytes() == before
    monkeypatch.setenv("DEVCAPSULE_CONFIG_HOME", str(tmp_path / "nested"))
    assert cli.main(["home", "default", "cpus", "2"]) == 0
    assert (home / "settings.toml").read_bytes() == before


@pytest.mark.parametrize("arguments", [["default", "cpus", "2"], ["trust", "accept", "devcapsule-base"],
                                       ["trust", "withdraw", "devcapsule-base"]])
def test_deleted_project_spellings(home: Path, capsys, arguments: list[str]) -> None:
    assert cli.main(["project", "config", *arguments]) == 2
    assert "unknown command" in capsys.readouterr().err.lower()


@pytest.mark.parametrize("arguments", [["show"], ["trust", "list"], ["default", "cpus", "2"],
                                       ["trust", "accept", "devcapsule-base", "--yes"], ["trust", "withdraw", "devcapsule-base"]])
def test_malformed_settings_refuse_every_home_command(home: Path, arguments: list[str], capsys) -> None:
    home.mkdir()
    path = home / "settings.toml"
    path.write_text('minimum-devcapsule = "9.0.0"\ndefaults = false\n')
    before = path.read_bytes()
    assert cli.main(["home", *arguments]) == 2
    assert "requires DevCapsule 9.0.0" in capsys.readouterr().err
    assert path.read_bytes() == before


@pytest.mark.parametrize("content", ['broken = [', 'minimum-devcapsule = "0.3.0"\ndevcapsule-settings-schema-version = 1\ndefaults = false',
                                     'minimum-devcapsule = "0.3.0"\ndevcapsule-settings-schema-version = 1\ntrust = false'])
def test_malformed_settings_stop_run_before_project_discovery(home: Path, content: str, capsys) -> None:
    home.mkdir()
    path = home / "settings.toml"
    path.write_text(content)
    assert cli.main(["project", "run", "--print-command"]) == 2
    assert str(path) in capsys.readouterr().err
    assert list(home.iterdir()) == [path] and path.read_text() == content
