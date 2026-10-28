"""Admission and persistence of the configuration home's one document."""
from pathlib import Path
import stat

import pytest

from devcapsule import cli
from devcapsule.configuration import storage
from devcapsule.configuration.file_formats import ProjectConfigurationError


def test_empty_and_legacy_files_are_not_read(tmp_path: Path) -> None:
    env = {"DEVCAPSULE_CONFIG_HOME": str(tmp_path / "home")}
    assert storage.load_workstation(env) == {}
    assert not (tmp_path / "home").exists()
    root = tmp_path / "home"
    root.mkdir()
    old = root / ("work" + "station.toml")
    old.write_text("not valid TOML")
    (root / "trust.toml").write_text("not valid TOML")
    assert storage.load_workstation(env) == {}
    storage.write_settings({"defaults": {"cpus": 4}}, env)
    assert old.read_text() == "not valid TOML"
    assert (root / "trust.toml").read_text() == "not valid TOML"


def test_round_trip_and_no_rewrite(tmp_path: Path) -> None:
    env = {"DEVCAPSULE_CONFIG_HOME": str(tmp_path / "home")}
    document = {"defaults": {"cpus": 4, "memory": "8GiB"},
                "trust": {"channels": {"example": {"vendor": "Example", "origins": ["https://example.test"],
                                                  "integrity": "SHA-256", "accepted": "2026-10-28T00:00:00Z"}}}}
    path = storage.write_settings(document, env)
    assert stat.S_IMODE(path.stat().st_mode) == 0o600
    assert stat.S_IMODE(path.parent.stat().st_mode) == 0o700
    assert storage.load_workstation(env) == {"devcapsule-settings-schema-version": 1,
                                            "minimum-devcapsule": "0.3.0", **document}
    path.write_text("# Keep this comment\n" + path.read_text())
    before = path.read_bytes(), path.stat().st_mtime_ns, path.stat().st_ino
    storage.write_settings(document, env)
    assert (path.read_bytes(), path.stat().st_mtime_ns, path.stat().st_ino) == before
    storage.write_settings({"defaults": {"cpus": 2}}, env)
    assert storage.load_workstation(env)["trust"] == document["trust"]


@pytest.mark.parametrize("schema", [2, True, "1"])
def test_unsupported_schema(tmp_path: Path, schema: object) -> None:
    from devcapsule.configuration.file_formats import render_toml
    env = {"DEVCAPSULE_CONFIG_HOME": str(tmp_path)}
    storage.settings_path(env).write_text(render_toml({"minimum-devcapsule": "0.3.0", "devcapsule-settings-schema-version": schema}))
    with pytest.raises(ProjectConfigurationError, match="unsupported schema version"):
        storage.load_workstation(env)


def test_minimum_refusal_precedes_content_and_command_diagnoses(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    monkeypatch.setenv("DEVCAPSULE_CONFIG_HOME", str(tmp_path))
    path = storage.settings_path()
    path.write_text('minimum-devcapsule = "9.0.0"\ndevcapsule-settings-schema-version = 2\ndefaults = false\n')
    before = path.read_bytes(), path.stat().st_mtime_ns
    assert cli.main(["project", "config", "default", "cpus", "2"]) == 2
    message = capsys.readouterr().err
    assert all(value in message for value in (str(tmp_path), "9.0.0", "0.3.0", "https://github.com/ccozianu/devcapsule/releases"))
    assert "unsupported schema" not in message
    with pytest.raises(ProjectConfigurationError, match="requires DevCapsule 9.0.0"):
        storage.write_settings({"defaults": {"cpus": 2}})
    assert (path.read_bytes(), path.stat().st_mtime_ns) == before
    assert list(tmp_path.iterdir()) == [path]


def test_candidate_creates_release_minimum(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("importlib.metadata.version", lambda name: "0.3.0rc8+local")
    env = {"DEVCAPSULE_CONFIG_HOME": str(tmp_path)}
    storage.write_settings({"defaults": {"cpus": 2}}, env)
    assert storage.load_workstation(env)["minimum-devcapsule"] == "0.3.0"
