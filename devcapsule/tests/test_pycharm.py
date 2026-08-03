from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import cast
from unittest.mock import patch

import pytest

from devcapsule.components.pycharm import runtime_template as pycharm_runtime_template
from devcapsule.components.codex import runtime_template as codex_runtime_template
from devcapsule.configurations.pycharm import DockerMode, IdeConfigMode, PycharmRunOptions, build_run_config
from devcapsule.configurations.pycharm._launcher import (
    HostUser,
    PycharmRunError,
    PycharmRunConfig,
    TempRuntimeFiles,
    build_docker_args,
    cleanup_temp_runtime_files,
    prepare_temp_runtime_files,
    print_storage_summary,
    run_pycharm,
    write_user_files,
)
from devcapsule.container_runtime.contract import Identity, RuntimePlan
from devcapsule.materialization import RUNTIME_PLAN_PATH
from devcapsule.project import plan_project


def base_env(tmp_path: Path) -> dict[str, str]:
    return {
        "DISPLAY": ":1",
        "HOME": str(tmp_path / "home"),
        "XDG_DATA_HOME": str(tmp_path / "data"),
        "PYCHARM_GIT_IDENTITY_FROM_HOST": "0",
    }


def external_runtime_plan() -> RuntimePlan:
    return RuntimePlan.for_component(
        pycharm_runtime_template(),
        project_path="/workspace/project",
        home="/home/devcapsule",
        identity=Identity(1000, 1000, "developer"),
    )


def test_external_runtime_plan_is_readable_and_mounted_read_only(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    env = base_env(tmp_path)
    env["XDG_RUNTIME_DIR"] = str(tmp_path / "runtime")
    config = build_run_config(
        PycharmRunOptions(
            project=project,
            project_mount="/workspace/project",
            docker_mode=DockerMode.none,
            network_mode="bridge",
            runtime_plan=external_runtime_plan(),
            use_image_process=True,
        ),
        env,
    )
    with (
        patch("devcapsule.configurations.pycharm._launcher.write_xauthority"),
        patch("devcapsule.configurations.pycharm._launcher.write_user_files"),
    ):
        files = prepare_temp_runtime_files(config, env)
    try:
        assert files.runtime_plan_file is not None
        assert files.runtime_plan_file.stat().st_mode & 0o777 == 0o644
        assert RuntimePlan.from_file(files.runtime_plan_file) == external_runtime_plan()
        args = build_docker_args(config, files, env)
        assert "JAVA_TOOL_OPTIONS=-Dide.browser.jcef.sandbox.enable=false" in args
        assert "SYS_ADMIN" not in args
        assert "seccomp=unconfined" not in args
        assert "apparmor=unconfined" not in args
        assert (
            f"type=bind,src={files.runtime_plan_file},dst={RUNTIME_PLAN_PATH},ro"
            in args
        )
    finally:
        cleanup_temp_runtime_files(files)
    assert files.runtime_plan_file is not None
    assert not files.runtime_plan_file.exists()


def test_jcef_disclosure_is_printed_for_component_policy(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    config = build_run_config(
        PycharmRunOptions(
            project=project,
            project_mount="/workspace/project",
            docker_mode=DockerMode.none,
            network_mode="bridge",
            runtime_plan=external_runtime_plan(),
            use_image_process=True,
        ),
        base_env(tmp_path),
    )

    print_storage_summary(config)

    disclosure = capsys.readouterr().err
    assert "JCEF's inner Chromium sandbox is disabled" in disclosure
    assert "Docker's outer isolation is unchanged" in disclosure


def test_selected_codex_state_and_explicit_secret_are_delivered(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    env = base_env(tmp_path)
    env["XDG_RUNTIME_DIR"] = str(tmp_path / "runtime")
    env["OPENAI_API_KEY"] = "sk-test-never-in-docker-args"
    runtime = RuntimePlan.for_component(
        pycharm_runtime_template(),
        project_path="/workspace/project",
        home="/home/devcapsule",
        identity=Identity(1000, 1000, "developer"),
        ancillary_templates=(codex_runtime_template(),),
    )
    state = tmp_path / "codex-home"
    config = build_run_config(
        PycharmRunOptions(
            project=project,
            project_mount="/workspace/project",
            docker_mode=DockerMode.none,
            network_mode="bridge",
            runtime_plan=runtime,
            use_image_process=True,
            additional_state_mounts={"codex/home": (state, "/home/devcapsule/.codex")},
            secret_environment=("OPENAI_API_KEY",),
        ),
        env,
    )
    with (
        patch("devcapsule.configurations.pycharm._launcher.write_xauthority"),
        patch("devcapsule.configurations.pycharm._launcher.write_user_files"),
    ):
        files = prepare_temp_runtime_files(config, env)
    try:
        args = build_docker_args(config, files, env)
    finally:
        cleanup_temp_runtime_files(files)

    assert "CODEX_HOME=/home/devcapsule/.codex" in args
    assert "OPENAI_API_KEY" in args
    assert "sk-test-never-in-docker-args" not in args
    assert f"type=bind,src={state.resolve()},dst=/home/devcapsule/.codex" in args


def test_bound_secret_must_exist_on_host(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    with pytest.raises(PycharmRunError, match="is not set on the host"):
        build_run_config(
            PycharmRunOptions(
                project=project,
                docker_mode=DockerMode.none,
                secret_environment=("OPENAI_API_KEY",),
            ),
            base_env(tmp_path),
        )


def test_image_process_uses_oci_command_and_cleans_all_temporary_files(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    env = base_env(tmp_path)
    env["XDG_RUNTIME_DIR"] = str(tmp_path / "runtime")
    image = "devcapsule-local-pycharm:canonical"
    with (
        patch("devcapsule.configurations.pycharm._launcher.shutil.which", return_value=None),
        patch("devcapsule.configurations.pycharm._launcher.subprocess.run") as run,
    ):
        run.return_value.returncode = 0
        assert (
            run_pycharm(
                PycharmRunOptions(
                    project=project,
                    project_mount="/workspace/project",
                    image=image,
                    docker_mode=DockerMode.none,
                    network_mode="bridge",
                    runtime_plan=external_runtime_plan(),
                    use_image_process=True,
                ),
                env,
            )
            == 0
        )

    command = run.call_args.args[0]
    assert command[-1] == image
    assert "/opt/pycharm/bin/pycharm.sh" not in command
    temporary_sources = [
        Path(next(part.removeprefix("src=") for part in argument.split(",") if part.startswith("src=")))
        for argument in command
        if argument.startswith("type=bind,src=")
        and any(
            destination in argument
            for destination in (
                "dst=/tmp/.docker.xauth",
                "dst=/etc/passwd",
                "dst=/etc/group",
                f"dst={RUNTIME_PLAN_PATH}",
            )
        )
    ]
    assert len(temporary_sources) == 4
    assert all(not path.exists() for path in temporary_sources)


def test_launch_preparation_failure_cleans_runtime_and_identity_files(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    env = base_env(tmp_path)
    env["XDG_RUNTIME_DIR"] = str(tmp_path / "runtime")
    with (
        patch("devcapsule.configurations.pycharm._launcher.shutil.which", return_value=None),
        patch(
            "devcapsule.configurations.pycharm._launcher.cleanup_temp_runtime_files",
            wraps=cleanup_temp_runtime_files,
        ) as cleanup,
    ):
        with pytest.raises(PycharmRunError, match="variable is empty or unset"):
            run_pycharm(
                PycharmRunOptions(
                    project=project,
                    project_mount="/workspace/project",
                    image="devcapsule-local-pycharm:canonical",
                    docker_mode=DockerMode.none,
                    network_mode="bridge",
                    git_token_env="MISSING_TOKEN",
                    runtime_plan=external_runtime_plan(),
                    use_image_process=True,
                ),
                env,
            )

    files = cleanup.call_args.args[0]
    assert files.runtime_plan_file is not None
    assert all(
        path is None or not path.exists()
        for path in (
            files.xauth_file,
            files.passwd_file,
            files.group_file,
            files.runtime_plan_file,
        )
    )


def test_runtime_plan_serialization_failure_leaves_no_temporary_files(tmp_path: Path) -> None:
    runtime_directory = tmp_path / "runtime"
    config = cast(
        PycharmRunConfig,
        SimpleNamespace(enable_sudo=False, runtime_plan=external_runtime_plan()),
    )
    with (
        patch("devcapsule.configurations.pycharm._launcher.write_xauthority"),
        patch("devcapsule.configurations.pycharm._launcher.write_user_files"),
        patch.object(RuntimePlan, "to_json", side_effect=ValueError("serialization failed")),
    ):
        with pytest.raises(ValueError, match="serialization failed"):
            prepare_temp_runtime_files(
                config,
                {"XDG_RUNTIME_DIR": str(runtime_directory)},
            )

    assert runtime_directory.is_dir()
    assert list(runtime_directory.iterdir()) == []


def test_generated_passwd_home_matches_persistent_container_home(tmp_path: Path) -> None:
    files = TempRuntimeFiles(
        xauth_file=tmp_path / "xauth",
        passwd_file=tmp_path / "passwd",
        group_file=tmp_path / "group",
    )
    config = cast(PycharmRunConfig, SimpleNamespace(host_docker_gid=None, enable_sudo=False))

    with patch(
        "devcapsule.configurations.pycharm._launcher.current_host_user",
        return_value=HostUser(uid=1000, gid=1000, name="developer", group_name="developer"),
    ):
        write_user_files(config, files)

    assert "developer:x:1000:1000:PyCharm Docker User:/home/devcapsule:/bin/bash" in files.passwd_file.read_text()
    assert "/ide-global-settings/home" not in files.passwd_file.read_text()


def test_ide_config_option_implies_custom_config_mode(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    custom_config = tmp_path / "custom-config"

    config = build_run_config(
        PycharmRunOptions(
            project=project,
            ide_config=custom_config,
            docker_mode=DockerMode.none,
        ),
        base_env(tmp_path),
    )

    assert config.ide_config_mode == "custom"
    assert config.ide_config == custom_config.resolve()


def test_explicit_shared_config_mode_ignores_env_ide_config_dir(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    env = base_env(tmp_path)
    env["PYCHARM_IDE_CONFIG_DIR"] = str(tmp_path / "env-config")

    config = build_run_config(
        PycharmRunOptions(
            project=project,
            config_mode=IdeConfigMode.shared,
            docker_mode=DockerMode.none,
        ),
        env,
    )

    assert config.ide_config_mode == "shared"
    project_id = plan_project(project).project_id
    assert config.ide_config == (
        tmp_path / "data" / "devcapsule" / "projects" / "by-path" / project_id / "components" / "pycharm" / "config"
    ).resolve()


def test_env_ide_config_dir_implies_custom_when_mode_is_unset(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    env = base_env(tmp_path)
    env["PYCHARM_IDE_CONFIG_DIR"] = str(tmp_path / "env-config")

    config = build_run_config(PycharmRunOptions(project=project, docker_mode=DockerMode.none), env)

    assert config.ide_config_mode == "custom"
    assert config.ide_config == (tmp_path / "env-config").resolve()


def test_profile_sets_global_settings_and_plugins_defaults(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    env = base_env(tmp_path)
    env["XDG_CONFIG_HOME"] = str(tmp_path / "config")

    config = build_run_config(
        PycharmRunOptions(
            project=project,
            profile="codex",
            docker_mode=DockerMode.none,
        ),
        env,
    )

    profile_root = tmp_path / "config" / "docker-pycharm-codex"
    assert config.global_settings == (profile_root / "state").resolve()
    assert config.plugins == (profile_root / "plugins").resolve()


def test_project_state_root_mirrors_project_path_under_root_parent(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    project = workspace / "myProjects" / "example"
    project.mkdir(parents=True)

    config = build_run_config(
        PycharmRunOptions(
            project=project,
            project_state_root=workspace / ".state",
            docker_mode=DockerMode.none,
        ),
        base_env(tmp_path),
    )

    assert config.project_state == (workspace / ".state" / "myProjects" / "example").resolve()


def test_explicit_project_state_overrides_project_state_root(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()

    config = build_run_config(
        PycharmRunOptions(
            project=project,
            project_state=tmp_path / "explicit-state",
            project_state_root=tmp_path / ".state",
            docker_mode=DockerMode.none,
        ),
        base_env(tmp_path),
    )

    assert config.project_state == (tmp_path / "explicit-state").resolve()


def test_dogfood_legacy_roots_map_to_persistent_home_and_component_slots(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    global_settings = tmp_path / "docker-pycharm-codex" / "state"
    plugins = tmp_path / "docker-pycharm-codex" / "plugins"
    project_state = tmp_path / ".state" / "project"

    config = build_run_config(
        PycharmRunOptions(
            project=project,
            global_settings=global_settings,
            plugins=plugins,
            project_state=project_state,
            docker_mode=DockerMode.none,
        ),
        base_env(tmp_path),
    )

    assert config.persistent_home == (global_settings / "home").resolve()
    assert config.ide_config == (global_settings / "config").resolve()
    assert config.plugins == plugins.resolve()
    assert config.ide_system == (project_state / "system").resolve()
    assert config.ide_log == (project_state / "log").resolve()
    assert config.tool_cache == (project_state / "home" / ".cache").resolve()


def test_persistent_home_defaults_to_checkout_scoped_xdg_data(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()

    config = build_run_config(
        PycharmRunOptions(
            project=project,
            docker_mode=DockerMode.none,
        ),
        base_env(tmp_path),
    )

    project_id = plan_project(project).project_id
    assert config.persistent_home == (
        tmp_path / "data" / "devcapsule" / "projects" / "by-path" / project_id / "home"
    ).resolve()
