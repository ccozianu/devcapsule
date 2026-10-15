"""Start-up values: arguments, environment, and their refusals."""

from __future__ import annotations

import logging
from pathlib import Path

import pytest

from devcapsule_webconsole import __main__ as entry
from devcapsule_webconsole.settings import (
    CLI_ENV, DEFAULT_CLI, LOG_LEVEL_ENV, PROJECT_ENV, TOKEN_FILE_ENV, SettingsError, log_level_from_environment,
    read_token, settings_from_arguments,
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


def test_read_token_strips_surrounding_whitespace(tmp_path: Path):
    path = tmp_path / "token"
    path.write_text("  deadbeef\n", encoding="utf-8")
    assert read_token(path) == "deadbeef"


@pytest.mark.parametrize("contents", [b"\xff", b"abc;def", b'abc"def', b"abc\\def", b"abc,def",
                                    b"abc\x00def", "snowman-\u2603".encode()])
def test_token_files_must_be_utf8_and_safe_for_an_unquoted_cookie(tmp_path, contents):
    path = tmp_path / "token"
    path.write_bytes(contents)
    with pytest.raises(SettingsError, match="malformed"):
        read_token(path)


def test_arguments_override_environment(project, token_file, tmp_path):
    settings = settings_from_arguments(
        ["--project", str(project), "--token-file", str(token_file), "--cli", "explicit-cli"],
        {PROJECT_ENV: str(tmp_path / "absent"), TOKEN_FILE_ENV: str(tmp_path / "missing"), CLI_ENV: "env-cli"},
    )
    assert settings.project == project.resolve()
    assert settings.token == "abc123"
    assert settings.cli == ("explicit-cli",)


@pytest.mark.parametrize("port", ["0", "-1"])
def test_nonpositive_ports_are_refused(project, token_file, port):
    with pytest.raises(SettingsError, match="port must be between"):
        settings_from_arguments(["--project", str(project), "--token-file", str(token_file), "--port", port], {})


def test_main_reports_a_settings_error_and_exits_2(capsys, monkeypatch):
    monkeypatch.delenv(PROJECT_ENV, raising=False)
    monkeypatch.delenv(TOKEN_FILE_ENV, raising=False)
    assert entry.main([]) == 2
    assert "devcapsule-webconsole: no project" in capsys.readouterr().err


def test_main_serves_the_application_with_the_settings(project: Path, token_file: Path, monkeypatch, capsys):
    monkeypatch.delenv(CLI_ENV, raising=False)
    served: dict[str, object] = {}

    def fake_run(app, *, host, port, log_level, log_config, access_log):
        served.update(app=app, host=host, port=port, log_level=log_level, log_config=log_config, access_log=access_log)

    monkeypatch.setattr(entry.uvicorn, "run", fake_run)
    assert entry.main(["--project", str(project), "--token-file", str(token_file), "--port", "7000"]) == 0
    assert (served["host"], served["port"], served["log_level"], served["log_config"]) == ("127.0.0.1", 7000, "warning", None)
    assert served["app"].state.settings.token == "abc123"  # type: ignore[attr-defined]
    assert served["access_log"] is False
    assert "serving" in capsys.readouterr().err


def test_the_log_level_is_warning_unless_the_session_override_says_otherwise():
    assert log_level_from_environment({}) == logging.WARNING
    assert log_level_from_environment({LOG_LEVEL_ENV: "debug"}) == logging.DEBUG
    assert log_level_from_environment({LOG_LEVEL_ENV: " Info "}) == logging.INFO
    with pytest.raises(SettingsError, match="DEBUG, INFO, WARNING, ERROR, not 'loud'"):
        log_level_from_environment({LOG_LEVEL_ENV: "loud"})


def test_main_configures_logging_and_runs_uvicorn_at_the_session_level(project, token_file, monkeypatch, capsys):
    calls: dict[str, object] = {}
    monkeypatch.setattr(entry.uvicorn, "run", lambda app, **keywords: calls.update(keywords))
    arguments = ["--project", str(project), "--token-file", str(token_file)]
    monkeypatch.setenv(LOG_LEVEL_ENV, "info")
    assert entry.main(arguments) == 0
    assert calls["log_level"] == "info" and calls["log_config"] is None
    assert calls["access_log"] is False
    assert logging.getLogger().level == logging.INFO
    monkeypatch.setenv(LOG_LEVEL_ENV, "loud")
    assert entry.main(arguments) == 0
    assert calls["log_level"] == "warning"
    assert "$DEVCAPSULE_LOG_LEVEL must be one of DEBUG, INFO, WARNING, ERROR, not 'loud'; logging at WARNING" in capsys.readouterr().err
    logging.basicConfig(level=logging.WARNING, force=True)


def test_uvicorn_records_use_the_console_handler_without_logging_request_tokens(project, token_file, monkeypatch, capsys):
    def configure_server(app, **options):
        # Exercise uvicorn's real logging configuration without opening a
        # listener. A mocked run alone cannot prove log_config=None routing.
        entry.uvicorn.Config(app, **options)
        logging.getLogger("uvicorn.error").warning("server warning")
        logging.getLogger("uvicorn.error").info("server diagnostic")
        logging.getLogger("uvicorn.access").info("GET /?token=private-token")

    monkeypatch.setattr(entry.uvicorn, "run", configure_server)
    monkeypatch.setenv(LOG_LEVEL_ENV, "INFO")
    try:
        assert entry.main(["--project", str(project), "--token-file", str(token_file)]) == 0
        stderr = capsys.readouterr().err
        assert stderr.count("server warning") == 1
        assert stderr.count("server diagnostic") == 1
        assert "private-token" not in stderr
    finally:
        logging.basicConfig(level=logging.WARNING, force=True)
