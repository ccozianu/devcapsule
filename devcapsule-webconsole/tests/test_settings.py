"""Start-up values: arguments, environment, and their refusals."""

from __future__ import annotations

from pathlib import Path

import pytest

from devcapsule_webconsole import __main__ as entry
from devcapsule_webconsole.settings import (
    CLI_ENV, DEFAULT_CLI, PROJECT_ENV, TOKEN_FILE_ENV, SettingsError, read_token, settings_from_arguments,
)


@pytest.fixture
def token_file(tmp_path: Path) -> Path:
    path = tmp_path / "token"
    path.write_text("abc123\n", encoding="utf-8")
    return path


def test_arguments_name_everything(project: Path, token_file: Path):
    settings = settings_from_arguments(
        ["--project", str(project), "--cli", "/opt/devcapsule/bin/devcapsule.pex", "--token-file", str(token_file),
         "--listen", "0.0.0.0", "--port", "6090"], {})
    assert settings.project == project.resolve()
    assert settings.cli == ("/opt/devcapsule/bin/devcapsule.pex",)
    assert settings.token == "abc123"
    assert (settings.listen, settings.port) == ("0.0.0.0", 6090)
    assert (settings.static_root / "index.html").is_file()


def test_the_environment_fills_the_capsule_defaults(project: Path, token_file: Path):
    settings = settings_from_arguments([], {PROJECT_ENV: str(project), TOKEN_FILE_ENV: str(token_file)})
    assert settings.project == project.resolve()
    assert settings.cli == (DEFAULT_CLI,)
    assert (settings.listen, settings.port) == ("127.0.0.1", 8080)
    assert settings_from_arguments([], {PROJECT_ENV: str(project), TOKEN_FILE_ENV: str(token_file),
                                        CLI_ENV: "devcapsule0"}).cli == ("devcapsule0",)


@pytest.mark.parametrize("argv, environ, message", [
    ([], {}, "no project"),
    (["--project", "{tmp}/absent"], {}, "not a DevCapsule project"),
    (["--project", "{project}"], {}, "no token"),
    (["--project", "{project}", "--token-file", "{tmp}/missing"], {}, "cannot read the console token"),
    (["--project", "{project}", "--token-file", "{tmp}/empty"], {}, "empty or malformed"),
    (["--project", "{project}", "--token-file", "{tmp}/spaced"], {}, "empty or malformed"),
    (["--project", "{project}", "--token-file", "{token}", "--port", "70000"], {}, "port must be between"),
])
def test_refusals_name_the_missing_value(project: Path, token_file: Path, tmp_path: Path, argv, environ, message):
    (tmp_path / "empty").write_text("\n", encoding="utf-8")
    (tmp_path / "spaced").write_text("ab cd\n", encoding="utf-8")
    substitutions = {"tmp": str(tmp_path), "project": str(project), "token": str(token_file)}
    with pytest.raises(SettingsError, match=message):
        settings_from_arguments([item.format(**substitutions) for item in argv], environ)


def test_read_token_strips_the_newline_only(tmp_path: Path):
    path = tmp_path / "token"
    path.write_text("  deadbeef\n", encoding="utf-8")
    assert read_token(path) == "deadbeef"


def test_main_reports_a_settings_error_and_exits_2(capsys, monkeypatch):
    monkeypatch.delenv(PROJECT_ENV, raising=False)
    monkeypatch.delenv(TOKEN_FILE_ENV, raising=False)
    assert entry.main([]) == 2
    assert "devcapsule-webconsole: no project" in capsys.readouterr().err


def test_main_serves_the_application_with_the_settings(project: Path, token_file: Path, monkeypatch, capsys):
    monkeypatch.delenv(CLI_ENV, raising=False)
    served: dict[str, object] = {}

    def fake_run(app, *, host, port, log_level):
        served.update(app=app, host=host, port=port, log_level=log_level)

    monkeypatch.setattr(entry.uvicorn, "run", fake_run)
    assert entry.main(["--project", str(project), "--token-file", str(token_file), "--port", "7000"]) == 0
    assert (served["host"], served["port"], served["log_level"]) == ("127.0.0.1", 7000, "warning")
    assert served["app"].state.settings.token == "abc123"  # type: ignore[attr-defined]
    assert "serving" in capsys.readouterr().err
