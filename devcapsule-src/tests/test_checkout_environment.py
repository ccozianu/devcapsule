from __future__ import annotations
import fcntl
import json
import os
from pathlib import Path
import shutil
import threading
from types import SimpleNamespace
from unittest.mock import patch
import pytest
from devcapsule import cli
from devcapsule.configuration.environment import environment_path, environment_docker_args, read_environment, update_environment
from devcapsule.configuration.file_formats import ProjectConfigurationError
from devcapsule.configuration.execution import ExecutionConfiguration
from devcapsule.configuration.storage import registered_checkouts, config_root
from devcapsule.platforms import XdgHomes
from devcapsule.materialization import parse_locked_environment
from tests.test_project_commands import initialize_project, initialize_codium_project, LOCKED_BASE

@pytest.fixture
def project(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    root.mkdir()
    initialize_project(root)
    assert cli.main(["project", "--path", str(root), "config", "resolve"]) == 0
    return root

def config(project: Path, *args: str) -> int:
    return cli.main(["project", "--path", str(project), "config", *args])

def test_cli_environment_lifecycle_and_isolation(project, tmp_path, capsys):
    record = registered_checkouts()[0].record_path
    before = record.read_bytes()
    path = environment_path(record)
    assert config(project, "unset-env", "PASSWORD") == 0  # idempotent: nothing to remove, no file written
    assert not path.exists()
    capsys.readouterr()
    assert config(project, "list-env") == 0
    assert capsys.readouterr().out == f"Environment file: {path}\nNo saved environment variables.\n"
    secret = 'literal # $HOME = "quoted" \\ trailing '
    assert config(project, "set-env", "PASSWORD", secret) == 0
    assert not path.is_relative_to(record.parent)
    assert path.stat().st_mode & 0o777 == 0o600
    assert path.parent.stat().st_mode & 0o777 == 0o700
    assert read_environment(path) == {"PASSWORD": secret}
    assert secret not in str(capsys.readouterr())
    assert config(project, "set-env", "EMPTY", "") == 0
    assert config(project, "set-env", "PASSWORD", "replacement") == 0
    capsys.readouterr()
    assert config(project, "list-env", "--json") == 0
    assert json.loads(capsys.readouterr().out) == {"path": str(path), "names": ["EMPTY", "PASSWORD"]}
    assert config(project, "list-env") == 0
    assert capsys.readouterr().out == f"Environment file: {path}\nEMPTY\nPASSWORD\n"
    assert record.read_bytes() == before
    second = tmp_path / "second"
    shutil.copytree(project, second)
    assert cli.main(["project", "--path", str(second), "checkout", "register", "second"]) == 0
    assert config(second, "set-env", "PASSWORD", "other") == 0
    assert read_environment(path)["PASSWORD"] == "replacement"
    assert config(project, "unset-env", "PASSWORD") == 0
    assert config(project, "unset-env", "PASSWORD") == 0
    assert config(project, "unset-env", "EMPTY") == 0
    assert environment_docker_args(record) == []

@pytest.mark.parametrize("operation", [("set-env", "PASSWORD", "value"), ("unset-env", "PASSWORD"), ("list-env",)])
def test_unregistered_checkout_is_refused_before_any_file(tmp_path, capsys, operation):
    root = tmp_path / "unregistered"
    root.mkdir()
    initialize_project(root)  # a manifest, but no checkout record for this path
    assert config(root, *operation) == 2
    assert "register this checkout" in capsys.readouterr().err
    assert not (config_root() / "environments").exists()
    assert not (config_root() / "projects").exists()


def test_prompt_and_nonterminal_refusal(project, monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    assert config(project, "set-env", "PASSWORD") != 0
    assert not environment_path(registered_checkouts()[0].record_path).exists()
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    with patch("getpass.getpass", return_value="hidden-value") as prompt:
        assert config(project, "set-env", "PASSWORD") == 0
        prompt.assert_called_once_with("Value: ")
    assert "hidden-value" not in str(capsys.readouterr())

@pytest.mark.parametrize("key,value", [("bad-name", "sensitive"), ("A", "secret\nB=injected"), ("A", "secret\r"), ("A", "secret\x00")])
def test_invalid_input_does_not_write_or_echo(project, key, value, capsys):
    assert config(project, "set-env", key, value) != 0
    assert value not in str(capsys.readouterr())
    assert not environment_path(registered_checkouts()[0].record_path).exists()

def test_atomic_failure_keeps_previous_values(tmp_path, monkeypatch):
    path = tmp_path / "private" / "secrets.env"
    update_environment(path, "A", "old")
    def fail(*args):
        raise OSError("simulated replace error")
    monkeypatch.setattr(os, "replace", fail)
    with pytest.raises(ProjectConfigurationError):
        update_environment(path, "A", "new")
    assert read_environment(path) == {"A": "old"}
    assert not list(path.parent.glob(".incoming-*"))

@pytest.mark.parametrize("content", [b"A=secret\nA=other\n", b"secret-without-key\n", b"A=\xff\n", b"A=secret\r\n",
                                     b"A=secret\x00\n", b"1A=secret\n", b"# secret\n", b"A\n"])
def test_bad_file_never_echoes_contents(tmp_path, content):
    record = config_root() / "projects" / "creator" / "project" / "devcapsule.checkout.toml"
    path = environment_path(record)
    path.parent.mkdir(parents=True)
    path.write_bytes(content)
    with pytest.raises(ProjectConfigurationError) as error:
        environment_docker_args(record)
    assert str(error.value) == f"Invalid managed environment file: {path}"


@pytest.mark.skipif(os.geteuid() == 0, reason="root ignores file modes")
def test_unreadable_file_names_the_file_and_the_reason(tmp_path):
    record = config_root() / "projects" / "creator" / "project" / "devcapsule.checkout.toml"
    path = environment_path(record)
    update_environment(path, "A", "secret")
    path.chmod(0)
    try:
        with pytest.raises(ProjectConfigurationError, match=f"Cannot read managed environment file {path}: Permission denied"):
            environment_docker_args(record)
        with pytest.raises(ProjectConfigurationError, match=f"Cannot read managed environment file {path}: Permission denied"):
            update_environment(path, "B", "value")
    finally:
        path.chmod(0o600)
    assert read_environment(path) == {"A": "secret"}


def test_concurrent_updates_wait_for_the_lock_and_keep_every_key(tmp_path):
    path = tmp_path / "private" / "secrets.env"
    update_environment(path, "A", "first")
    held = threading.Event()
    release = threading.Event()

    def holder():
        with (path.parent / ".lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            held.set()
            release.wait(timeout=10)

    thread = threading.Thread(target=holder)
    thread.start()
    assert held.wait(timeout=10)
    writer = threading.Thread(target=update_environment, args=(path, "C", "third"))
    writer.start()
    writer.join(timeout=0.5)
    assert writer.is_alive(), "the update must wait for the lock holder"
    assert read_environment(path) == {"A": "first"}
    release.set()
    thread.join(timeout=10)
    writer.join(timeout=10)
    assert not writer.is_alive() and not thread.is_alive()
    assert read_environment(path) == {"A": "first", "C": "third"}

def test_launch_consumes_file_without_snapshotting_values(tmp_path, capsys):
    root = tmp_path / "codium"
    initialize_codium_project(root)
    assert config(root, "authorize", "base-image", LOCKED_BASE) == 0
    assert config(root, "resolve") == 0
    selected = ExecutionConfiguration.load(root).project
    before = selected.resolution_path.read_bytes()
    assert config(root, "set-env", "POSTGRES_PASSWORD", "fake-password-sentinel") == 0
    realized = SimpleNamespace(image=SimpleNamespace(labels={}, reference="devcapsule-local-codium:fixture"), created=False, locked=parse_locked_environment(selected.lock))
    with patch("devcapsule.commands.project.realize_environment", return_value=realized), patch("devcapsule.commands.project.run_pycharm", return_value=0) as launch:
        assert cli.main(["project", "--path", str(root), "run", "--", "--env", "OTHER=public"]) == 0
    assert launch.call_args.args[0].extra_docker_args == ["--pull=never", "--env-file", str(environment_path(selected.checkout_path)), "--env", "OTHER=public"]
    assert selected.resolution_path.read_bytes() == before
    assert "fake-password-sentinel" not in str(capsys.readouterr())
    homes = XdgHomes.from_environment()
    for base in (homes.config / "projects", homes.state, homes.data, homes.cache, root):
        assert all(b"fake-password-sentinel" not in p.read_bytes() for p in base.rglob("*") if p.is_file())
    assert b"fake-password-sentinel" in environment_path(selected.checkout_path).read_bytes()
    # A corrupt managed file refuses the launch by its file, before the upgrade
    # offer could ask anything and before any launcher work.
    environment_path(selected.checkout_path).write_bytes(b"POSTGRES_PASSWORD=fake-password-sentinel\n# edited by hand\n")
    with patch("devcapsule.commands.project.offer_upgrades") as upgrades, \
            patch("devcapsule.commands.project.realize_environment") as realize, \
            patch("devcapsule.commands.project.run_pycharm") as launch:
        assert cli.main(["project", "--path", str(root), "run"]) == 2
    output = capsys.readouterr()
    assert f"Invalid managed environment file: {environment_path(selected.checkout_path)}" in output.err
    assert "fake-password-sentinel" not in output.out + output.err
    assert not upgrades.called and not realize.called and not launch.called

@pytest.mark.parametrize("failure", [EOFError(), __import__("getpass").GetPassWarning("echo unavailable")])
def test_hidden_prompt_never_falls_back_to_echo(project, monkeypatch, failure):
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    with patch("getpass.getpass", side_effect=failure):
        assert config(project, "set-env", "PASSWORD") != 0
    assert not environment_path(registered_checkouts()[0].record_path).exists()
