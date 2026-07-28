from __future__ import annotations

import os
import subprocess
from pathlib import Path
from unittest.mock import patch

import click

from devcapsule import cli, compat
from devcapsule.configurations.pycharm._image_build import PycharmImageBuildOptions
from devcapsule.configurations.vscode_with_claude import VscodeWithClaudeConfiguration


def test_top_level_help_returns_success(capsys) -> None:
    result = cli.main(["--help"])

    assert result == 0
    output = capsys.readouterr().out
    assert "pycharm" in output
    assert "vscode_with_claude" in output
    assert "codium_with_claude" in output


def test_run_pycharm_uses_translated_python_launcher(tmp_path: Path) -> None:
    project = tmp_path / "example"
    project.mkdir()
    data_home = tmp_path / "data"

    with (
        patch("devcapsule.configurations.pycharm._launcher.shutil.which", return_value=None),
        patch("devcapsule.configurations.pycharm._launcher.subprocess.run") as run,
        patch.dict(
            os.environ,
            {
                "DISPLAY": ":1",
                "XDG_DATA_HOME": str(data_home),
                "PYCHARM_GIT_IDENTITY_FROM_HOST": "0",
            },
            clear=False,
        ),
    ):
        run.return_value.returncode = 0

        result = cli.main(["pycharm", "run", "--project", str(project), "--no-docker"])

    assert result == 0
    command = run.call_args.args[0]
    assert command[:2] == ["docker", "run"]
    assert "docker4pycharm/run-pycharm-container.sh" not in command[0]
    assert any(arg.startswith(f"type=bind,src={project.resolve()},dst=") for arg in command)
    assert "--cap-drop" in command
    assert "--read-only" in command
    assert "HOME=/home/devcapsule" in command
    assert any(arg.endswith(",dst=/home/devcapsule") for arg in command)
    assert any(arg.endswith(",dst=/ide-project-state/system") for arg in command)
    assert any(arg.endswith(",dst=/ide-project-state/log") for arg in command)
    assert any(arg.endswith(",dst=/home/devcapsule/.cache") for arg in command)
    assert not any(arg.endswith(",dst=/ide-global-settings/home/.gemini") for arg in command)


def test_run_image_uses_pycharm_persistence_adapter(tmp_path: Path) -> None:
    project = tmp_path / "example"
    project.mkdir()
    global_settings = tmp_path / "global-settings"
    plugins = tmp_path / "plugins"
    project_state = tmp_path / "project-state"

    with (
        patch("devcapsule.configurations.pycharm._launcher.shutil.which", return_value=None),
        patch("devcapsule.configurations.pycharm._launcher.subprocess.run") as run,
        patch.dict(
            os.environ,
            {
                "DISPLAY": ":1",
                "HOME": str(tmp_path / "host-home"),
                "XDG_DATA_HOME": str(tmp_path / "data"),
                "PYCHARM_GIT_IDENTITY_FROM_HOST": "0",
            },
            clear=False,
        ),
    ):
        run.return_value.returncode = 0
        result = cli.main(
            [
                "run-image",
                "mycodespace.ai/pycharm:debug-v017",
                "--project",
                str(project),
                "--project-mount",
                "/workspace/existing-checkout",
                "--global-settings",
                str(global_settings),
                "--plugins",
                str(plugins),
                "--project-state",
                str(project_state),
            ]
        )

    assert result == 0
    command = run.call_args.args[0]
    assert "mycodespace.ai/pycharm:debug-v017" in command
    assert "--pull=never" in command
    assert "--workdir" in command
    assert command[command.index("--workdir") + 1] == "/workspace/existing-checkout"
    assert f"type=bind,src={project.resolve()},dst=/workspace/existing-checkout" in command
    assert f"type=bind,src={(global_settings / 'home').resolve()},dst=/home/devcapsule" in command
    assert f"type=bind,src={(global_settings / 'config').resolve()},dst=/ide-config" in command
    assert f"type=bind,src={plugins.resolve()},dst=/ide-plugins" in command


def test_run_pycharm_defaults_project_to_current_directory(tmp_path: Path, monkeypatch) -> None:
    project = tmp_path / "current-project"
    project.mkdir()
    monkeypatch.chdir(project)

    with (
        patch("devcapsule.configurations.pycharm._launcher.shutil.which", return_value=None),
        patch("devcapsule.configurations.pycharm._launcher.subprocess.run") as run,
        patch.dict(
            os.environ,
            {
                "DISPLAY": ":1",
                "XDG_DATA_HOME": str(tmp_path / "data"),
                "PYCHARM_GIT_IDENTITY_FROM_HOST": "0",
            },
            clear=False,
        ),
    ):
        run.return_value.returncode = 0

        result = cli.main(["pycharm", "run", "--no-docker"])

    assert result == 0
    command = run.call_args.args[0]
    assert any(arg.startswith(f"type=bind,src={project.resolve()},dst=") for arg in command)


def test_run_pycharm_rejects_conflicting_config_mode_options(tmp_path: Path) -> None:
    project = tmp_path / "example"
    project.mkdir()

    result = cli.main(
        [
            "pycharm",
            "run",
            "--project",
            str(project),
            "--config-mode",
            "shared",
            "--ide-config",
            str(tmp_path / "custom-config"),
        ]
    )

    assert result == 2


def test_run_pycharm_rejects_multiple_config_shorthands(tmp_path: Path) -> None:
    project = tmp_path / "example"
    project.mkdir()

    result = cli.main(
        [
            "pycharm",
            "run",
            "--project",
            str(project),
            "--project-config",
            "--shared-config",
        ]
    )

    assert result == 2


def test_build_pycharm_uses_python_buildx_builder(tmp_path: Path) -> None:
    source = tmp_path / "pycharm"
    (source / "bin").mkdir(parents=True)
    (source / "bin" / "pycharm.sh").write_text("#!/usr/bin/env bash\n", encoding="utf-8")

    with patch("devcapsule.configurations.pycharm.configuration.build_pycharm_image") as build_image:
        build_image.return_value = 0
        result = cli.main(
            [
                "pycharm",
                "build",
                "--pycharm",
                str(source),
                "--image",
                "custom:latest",
                "--base-image",
                "ubuntu:24.04",
                "--extra-apt-package",
                "rsync",
            ]
        )

    assert result == 0
    options = build_image.call_args.args[0]
    assert options == PycharmImageBuildOptions(
        pycharm=source.resolve(),
        image="custom:latest",
        base_image="ubuntu:24.04",
        network="default",
        extra_apt_packages=("rsync",),
    )


def test_build_pycharm_accepts_host_network(tmp_path: Path) -> None:
    source = tmp_path / "pycharm"
    (source / "bin").mkdir(parents=True)
    (source / "bin" / "pycharm.sh").write_text("#!/usr/bin/env bash\n", encoding="utf-8")

    with patch("devcapsule.configurations.pycharm.configuration.build_pycharm_image") as build_image:
        build_image.return_value = 0
        result = cli.main(["pycharm", "build", "--pycharm", str(source), "--network", "host"])

    assert result == 0
    assert build_image.call_args.args[0].network == "host"


def test_runtime_check_pycharm_delegates_to_current_script() -> None:
    with patch.object(compat.subprocess, "run") as run:
        run.return_value.returncode = 0

        result = cli.main(["pycharm", "check-runtime"])

    assert result == 0
    command = run.call_args.args[0]
    assert command[0].endswith("docker4pycharm/check-runtime-deps.sh")
    assert command[1:] == []


def test_bootstrap_project_delegates_to_current_script() -> None:
    with patch.object(compat.subprocess, "run") as run:
        run.return_value.returncode = 0

        result = cli.main(["bootstrap", "project", "--project", "/tmp/example"])

    assert result == 0
    command = run.call_args.args[0]
    assert command[0].endswith("docker4pycharm/bootstrap-project.sh")
    assert command[1:] == ["--project", "/tmp/example"]


def test_repo_root_can_be_overridden(tmp_path: Path) -> None:
    with patch.dict(os.environ, {"DOCKER4IDES_REPO_ROOT": str(tmp_path)}):
        assert cli.repo_root() == tmp_path.resolve()


def test_top_level_commands_are_discovered() -> None:
    commands = cli.cli.list_commands(click.Context(cli.cli))

    assert "bootstrap" in commands
    assert "pycharm" in commands
    assert "vscode_with_claude" in commands
    assert "codium_with_claude" in commands
    assert "init" in commands
    assert "lock" in commands
    assert "config" in commands
    assert "state" in commands
    assert "run" in commands
    assert "bootstrap-project" not in commands
    assert "build" not in commands
    assert "check" not in commands


def test_capability_first_dogfood_init_resolve_and_run(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    config_home = tmp_path / "config"
    state_roots = {slot: tmp_path / slot.replace("/", "-") for slot in (
        "home", "pycharm/config", "pycharm/plugins", "pycharm/system", "pycharm/log", "pycharm/cache"
    )}
    for path in state_roots.values():
        path.mkdir()

    env = {
        "DISPLAY": ":1",
        "HOME": str(tmp_path / "host-home"),
        "XDG_CONFIG_HOME": str(config_home),
        "XDG_DATA_HOME": str(tmp_path / "data"),
        "PYCHARM_GIT_IDENTITY_FROM_HOST": "0",
    }
    with patch.dict(os.environ, env, clear=False):
        assert cli.main([
            "init", str(project), "--creator", "dev@example.test",
            "--project-mount", "/workspace/existing", "--need", "python", "--need", "python-ide",
        ]) == 0
        manifest = project / ".devcapsule" / "devcapsule.toml"
        original = manifest.read_bytes()
        assert cli.main(["init", str(project), "--creator", "dev@example.test", "--need", "python"]) == 2
        assert manifest.read_bytes() == original
        assert cli.main(["lock", "--project", str(project), "--image", "local/pycharm:dogfood"]) == 0
        for slot, path in state_roots.items():
            assert cli.main(["state", "adopt", slot, "--from", str(path), "--project", str(project)]) == 0
        assert cli.main(["config", "resolve", "--project", str(project)]) == 0

        with (
            patch("devcapsule.configurations.pycharm._launcher.shutil.which", return_value=None),
            patch("devcapsule.configurations.pycharm._launcher.subprocess.run") as run,
        ):
            run.return_value.returncode = 0
            assert cli.main(["run", "--project", str(project)]) == 0

    command = run.call_args.args[0]
    assert "local/pycharm:dogfood" in command
    assert "--network=host" not in command
    assert f"type=bind,src={state_roots['home'].resolve()},dst=/home/devcapsule" in command
    assert f"type=bind,src={state_roots['pycharm/system'].resolve()},dst=/ide-project-state/system" in command


def test_noun_first_pycharm_command_order_is_not_supported() -> None:
    assert cli.main(["run", "pycharm"]) == 2
    assert cli.main(["build", "pycharm"]) == 2
    assert cli.main(["check", "runtime", "pycharm"]) == 2


def test_bootstrap_project_alias_is_not_supported() -> None:
    assert cli.main(["bootstrap-project", "--project", "/tmp/example"]) == 2


def test_vscode_with_claude_configuration_is_registered(capsys) -> None:
    result = cli.main(["vscode_with_claude", "--help"])

    assert result == 0
    output = capsys.readouterr().out
    assert "run" in output
    assert "build" in output


def test_vscode_with_claude_configuration_identity() -> None:
    config = VscodeWithClaudeConfiguration()

    assert config.name == "vscode_with_claude"
    assert config.ide == "vscode"
    assert config.agent == "claude"
    assert not config.implemented


def test_vscode_with_claude_run_fails_explicitly(capsys) -> None:
    result = cli.main(["vscode_with_claude", "run"])

    assert result == 1
    assert "not implemented yet" in capsys.readouterr().err


def test_build_pex_script_is_available() -> None:
    script = Path(__file__).resolve().parents[1] / "scripts" / "build-pex.sh"

    assert script.exists()
    assert os.access(script, os.X_OK)

    completed = subprocess.run(
        [str(script), "--help"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    assert completed.returncode == 0
    assert "dist/devcapsule.pex" in completed.stdout
