from __future__ import annotations

import io
import tarfile
from pathlib import Path
from unittest.mock import patch

from devcapsule import cli
from devcapsule.configurations.codium_with_claude import (
    CodiumWithClaudeConfiguration,
    CodiumImageBuildOptions,
    CodiumRunOptions,
    build_codium_image_spec,
    build_codium_run_command,
    normalize_codium_archive,
)
from devcapsule.image_build import render_build_context


def test_configuration_is_distinct_from_vscode_stub(capsys) -> None:
    assert cli.main(["codium_with_claude", "--help"]) == 0
    output = capsys.readouterr().out
    assert "build" in output
    assert "run" in output
    assert "VSCodium" in output


def test_build_command_uses_python_buildx_builder() -> None:
    with patch(
        "devcapsule.configurations.codium_with_claude.configuration.build_codium_image"
    ) as build_image:
        build_image.return_value = 0
        assert cli.main(["codium_with_claude", "build", "--image", "test-codium:latest"]) == 0

    options = build_image.call_args.args[0]
    assert options.image == "test-codium:latest"
    assert options.base_image == "ubuntu:24.04"


def test_image_spec_contains_requested_sdks_and_node_tooling_without_ambient_gemini(tmp_path: Path) -> None:
    entrypoint = tmp_path / "entrypoint.sh"
    entrypoint.write_text("#!/bin/sh\n", encoding="utf-8")
    spec = build_codium_image_spec(CodiumImageBuildOptions(), assets_root=tmp_path)
    plan = spec.build_plan()

    assert "python3.12" in plan.apt_packages
    assert "strace" in plan.apt_packages
    assert "xterm" in plan.apt_packages
    install_script = "\n".join(" ".join(step.args) for step in plan.exec_steps)
    assert "nodejs.org/dist/${node_version}" in install_script
    assert "@google/gemini-cli" not in install_script
    assert "apt-get install -y --no-install-recommends codium" in install_script
    assert "mkdir -p /opt/node" in install_script
    assert "sha256sum -c -" in install_script
    assert 'export PATH="/opt/node/current/bin:$PATH"' in install_script
    assert "node --version" in install_script
    assert "npm --version" in install_script
    assert "gemini --version" not in install_script
    assert "/usr/share/codium/codium /usr/local/bin/codium-foreground" in install_script
    assert ("devcapsule.configuration", "codium_with_claude") in plan.labels
    assert ("PATH", "/opt/node/current/bin:${PATH}") in plan.env
    context = tmp_path / "context"
    context.mkdir()
    dockerfile = render_build_context(plan, context).read_text(encoding="utf-8")
    assert "download.vscodium.com/debs vscodium main" in dockerfile
    assert "https://nodejs.org/dist/${node_version}" in dockerfile
    assert "RUN 'bash' '-euxo' 'pipefail' '-c'" in dockerfile


def test_build_command_accepts_local_ide_archive(tmp_path: Path) -> None:
    archive = tmp_path / "codium.tar.gz"
    archive.write_bytes(b"placeholder")
    with patch(
        "devcapsule.configurations.codium_with_claude.configuration.build_codium_image"
    ) as build_image:
        build_image.return_value = 0
        assert cli.main(["codium_with_claude", "build", "--ide-archive", str(archive)]) == 0

    assert build_image.call_args.args[0].ide_archive == archive.resolve()


def test_archive_image_spec_skips_vscodium_repository(tmp_path: Path) -> None:
    entrypoint = tmp_path / "entrypoint.sh"
    entrypoint.write_text("#!/bin/sh\n", encoding="utf-8")
    codium_root = tmp_path / "codium"
    (codium_root / "bin").mkdir(parents=True)
    (codium_root / "bin" / "codium").write_text("#!/bin/sh\n", encoding="utf-8")
    spec = build_codium_image_spec(
        CodiumImageBuildOptions(ide_archive=tmp_path / "codium.tar.gz"),
        assets_root=tmp_path,
        codium_root=codium_root,
    )
    plan = spec.build_plan()
    install_script = "\n".join(" ".join(step.args) for step in plan.exec_steps)

    assert "paulcarroty" not in install_script
    assert "download.vscodium.com" not in install_script
    assert "apt-get install -y --no-install-recommends codium" not in install_script
    assert any(copy.source == codium_root and copy.destination == "/opt/codium" for copy in plan.directories)
    assert "/opt/codium/bin/codium" in install_script
    assert "VSCodium archive is missing /opt/codium/chrome-sandbox" in install_script
    assert "chown root:root /opt/codium/chrome-sandbox" in install_script
    assert "chmod 4755 /opt/codium/chrome-sandbox" in install_script
    assert "/opt/codium/codium /usr/local/bin/codium-foreground" in install_script


def test_normalize_codium_archive_finds_executable_launcher(tmp_path: Path) -> None:
    archive_path = tmp_path / "codium-linux-x64.tar.gz"
    launcher = b"#!/bin/sh\n"
    info = tarfile.TarInfo("VSCodium-linux-x64/bin/codium")
    info.mode = 0o755
    info.size = len(launcher)
    with tarfile.open(archive_path, "w:gz") as archive:
        archive.addfile(info, io.BytesIO(launcher))

    normalized = normalize_codium_archive(archive_path, tmp_path / "extracted")

    assert normalized.name == "VSCodium-linux-x64"
    assert (normalized / "bin" / "codium").is_file()


def test_run_command_mounts_only_explicit_state_and_x11(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    state = tmp_path / "global-state"
    project_state = tmp_path / "project-state"
    command = build_codium_run_command(
        CodiumRunOptions(project=project, state=state, project_state=project_state),
        {"DISPLAY": ":0", "HOME": str(tmp_path)},
    )

    assert f"{project.resolve()}:/workspace/project" in command
    assert f"{state.resolve()}:/ide-global-settings" in command
    assert f"{project_state.resolve()}:/ide-project-state" in command
    assert not any(argument.endswith(":/ide-global-settings/home/.gemini") for argument in command)
    assert "/tmp/.X11-unix:/tmp/.X11-unix:ro" in command
    assert "/var/run/docker.sock" not in " ".join(command)
    assert command[-1] == "/workspace/project"
    assert "codium-foreground" in command
    assert "codium" not in command


def test_run_command_supports_shared_profile_and_project_state_root(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    state_root = tmp_path / "state-root"
    command = build_codium_run_command(
        CodiumRunOptions(project=project, profile="codex", project_state_root=state_root),
        {"DISPLAY": ":0", "HOME": str(tmp_path)},
    )

    expected_state = tmp_path / ".config" / "devcapsule-codium-with-claude-codex" / "state"
    expected_project_state = state_root / project.name
    assert f"{expected_state.resolve()}:/ide-global-settings" in command
    assert f"{expected_project_state.resolve()}:/ide-project-state" in command
    assert not any(argument.endswith(":/ide-global-settings/home/.gemini") for argument in command)


def test_run_command_supports_explicit_project_mount(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    command = build_codium_run_command(
        CodiumRunOptions(project=project, project_mount="/workspace/custom-project"),
        {"DISPLAY": ":0", "HOME": str(tmp_path)},
    )

    assert f"{project.resolve()}:/workspace/custom-project" in command
    assert command[-1] == "/workspace/custom-project"


def test_debug_shell_runs_interactive_bash_through_entrypoint(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    command = build_codium_run_command(
        CodiumRunOptions(project=project, debug_shell=True),
        {"DISPLAY": ":0", "HOME": str(tmp_path)},
    )

    assert "--interactive" in command
    assert "--tty" in command
    assert command[-2:] == ["codium-with-claude:latest", "bash"]
    assert "--entrypoint" not in command


def test_run_network_mode_applies_to_normal_and_debug_shell(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()

    for debug_shell in (False, True):
        command = build_codium_run_command(
            CodiumRunOptions(project=project, network="host", debug_shell=debug_shell),
            {"DISPLAY": ":0", "HOME": str(tmp_path)},
        )

        network_index = command.index("--network")
        assert command[network_index + 1] == "host"


def test_codium_run_command_exposes_shared_state_layout_options(capsys) -> None:
    assert cli.main(["codium_with_claude", "run", "--help"]) == 0
    output = capsys.readouterr().out

    assert "--profile" in output
    assert "--project-state-root" in output
    assert "--project-mount" in output
