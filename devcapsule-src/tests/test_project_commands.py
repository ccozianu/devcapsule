from __future__ import annotations

import os
from pathlib import Path
import shutil
import tomllib
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from devcapsule import cli
from devcapsule.configurations.pycharm import DockerMode
from devcapsule.materialization import ImageDetails, parse_locked_environment
from devcapsule.project_configuration import (
    ProjectConfigurationError,
    canonical_digest,
    immutable_registry_reference,
    registered_checkouts,
)
from devcapsule.project import project_namespace


LOCKED_BASE = f"docker.io/example/devcapsule-base@sha256:{'b' * 64}"


def initialize_project(project: Path) -> None:
    assert (
        cli.main(
            [
                "project",
                "--path",
                str(project),
                "init",
                "--creator",
                "dev@example.test",
                "--need",
                "python",
                "--need",
                "python-ide",
            ]
        )
        == 0
    )
    assert (
        cli.main(
            [
                "project",
                "--path",
                str(project),
                "lock",
                "--image",
                "local/pycharm:dogfood",
            ]
        )
        == 0
    )


def write_formation_lock(project: Path, reference: str = LOCKED_BASE) -> Path:
    manifest_path = project / ".devcapsule" / "devcapsule.toml"
    with manifest_path.open("rb") as stream:
        manifest = tomllib.load(stream)
    lock_path = project / ".devcapsule" / "devcapsule.linux-amd64.lock"
    lock_path.write_text(
        "\n".join(
            [
                "devcapsule-lock-format-version = 1",
                'resolution-matrix-version = "formation-v1"',
                f'manifest-digest = "{canonical_digest(manifest)}"',
                'platform = "linux-amd64"',
                "",
                "[base]",
                f'reference = "{reference}"',
                'build-mnemonic = "v026"',
                "",
                "[components]",
                'interactive-surface = "pycharm"',
                "",
                "[components.pycharm]",
                'version = "2026.2.0.1"',
                'variant = "professional"',
                'delivery-policy = "local-materialization"',
                'url = "https://example.test/pycharm.tar.gz"',
                f'sha256 = "{"a" * 64}"',
                "",
                "[materialization]",
                'recipe = "jetbrains-local-materialization"',
                'recipe-version = "1"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    return lock_path


def select_codex_component(project: Path) -> None:
    lock_path = project / ".devcapsule" / "devcapsule.linux-amd64.lock"
    with lock_path.open("a", encoding="utf-8") as stream:
        stream.write(
            """
[components.codex]
version = "0.145.0"
delivery-policy = "local-materialization"

[components.codex.artifacts.linux-amd64]
url = "https://example.test/codex.tgz"
sha256 = "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
archive-member = "package/vendor/x86_64-unknown-linux-musl/bin/codex"
"""
        )


def append_manifest_metadata(project: Path, declaration: str) -> None:
    manifest_path = project / ".devcapsule" / "devcapsule.toml"
    with manifest_path.open("a", encoding="utf-8") as stream:
        stream.write(f"\n{declaration.strip()}\n")
    with manifest_path.open("rb") as stream:
        manifest = tomllib.load(stream)
    lock_path = project / ".devcapsule" / "devcapsule.linux-amd64.lock"
    lines = lock_path.read_text(encoding="utf-8").splitlines()
    lines = [
        f'manifest-digest = "{canonical_digest(manifest)}"'
        if line.startswith("manifest-digest = ")
        else line
        for line in lines
    ]
    lock_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_project_resolve_registers_default_checkout_and_list_uses_registry(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    config_home = tmp_path / "config"
    env = {
        "HOME": str(tmp_path / "home"),
        "XDG_CONFIG_HOME": str(config_home),
        "XDG_DATA_HOME": str(tmp_path / "data"),
    }

    with patch.dict(os.environ, env, clear=False):
        initialize_project(project)
        nested = project / "src" / "package"
        nested.mkdir(parents=True)
        monkeypatch.chdir(nested)

        assert cli.main(["project", "config", "resolve"]) == 0
        records = registered_checkouts()
        assert len(records) == 1
        assert records[0].checkout_name == "default"
        assert records[0].checkout_path == project.resolve()
        assert records[0].status == "ready"

        capsys.readouterr()
        assert cli.main(["project", "list"]) == 0
        output = capsys.readouterr().out
        assert "PROJECT" in output
        assert "mailto:dev@example.test/project" in output
        assert str(project.resolve()) in output
        assert "ready" in output


def test_named_checkout_registration_selects_distinct_record_and_reports_missing(
    tmp_path: Path,
    capsys,
) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.mkdir()
    second.mkdir()
    config_home = tmp_path / "config"
    env = {"HOME": str(tmp_path / "home"), "XDG_CONFIG_HOME": str(config_home)}

    with patch.dict(os.environ, env, clear=False):
        initialize_project(first)
        shutil.copytree(first / ".devcapsule", second / ".devcapsule")
        assert cli.main(["project", "--path", str(first), "config", "resolve"]) == 0

        assert (
            cli.main(
                [
                    "project",
                    "--path",
                    str(second),
                    "checkout",
                    "register",
                    "second-checkout",
                ]
            )
            == 0
        )
        assert cli.main(["project", "--path", str(second), "config", "resolve"]) == 0

        records = registered_checkouts()
        assert [(record.checkout_name, record.checkout_path) for record in records] == [
            ("default", first.resolve()),
            ("second-checkout", second.resolve()),
        ]

        shutil.rmtree(second)
        capsys.readouterr()
        assert cli.main(["project", "list"]) == 0
        output = capsys.readouterr().out
        assert "default" in output
        assert "second-checkout" in output
        assert "missing" in output


def test_project_list_does_not_scan_unregistered_source_trees(tmp_path: Path, capsys) -> None:
    project = tmp_path / "unregistered"
    project.mkdir()
    config_home = tmp_path / "config"
    env = {"HOME": str(tmp_path / "home"), "XDG_CONFIG_HOME": str(config_home)}

    with patch.dict(os.environ, env, clear=False):
        initialize_project(project)
        capsys.readouterr()
        assert cli.main(["project", "list"]) == 0

    assert "No registered DevCapsule project checkouts" in capsys.readouterr().out


def test_project_config_list_materializes_default_checkout_and_reports_readiness(
    tmp_path: Path, capsys
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    config_home = tmp_path / "config"
    env = {"HOME": str(tmp_path / "home"), "XDG_CONFIG_HOME": str(config_home)}

    with patch.dict(os.environ, env, clear=False):
        initialize_project(project)
        append_manifest_metadata(
            project,
            """
            [configuration.values."runtime.memory-limit"]
            type = "memory-size"
            runtime-effect = "docker.memory-limit"

            [host.docker.mode.recommended]
            value = "host-socket"
            justification = "Run peer development containers."
            """,
        )
        write_formation_lock(project)
        select_codex_component(project)

        assert cli.main(["project", "--path", str(project), "config", "list"]) == 0
        output = capsys.readouterr().out
        assert "Checkout name: default" in output
        assert "Checkout input:" in output
        assert "Generated plan:" in output
        assert "runtime.memory-limit" in output
        assert "unset-optional" in output
        assert "managed-default" in output
        assert "codex/openai-api-key" in output
        assert "optional-unbound" in output
        assert "OPENAI_API_KEY" in output
        assert "missing-required" in output
        assert "v026" in output
        assert LOCKED_BASE in output
        assert "missing-recommended" in output
        assert "unresolved" in output

        records = registered_checkouts()
        assert len(records) == 1
        record = records[0].record_path
        resolved_path = record.with_name("devcapsule.resolved.toml")
        with record.open("rb") as stream:
            checkout = tomllib.load(stream)
        assert checkout == {
            "devcapsule-checkout-schema-version": 1,
            "project": {"creator": "mailto:dev@example.test", "slug": "project"},
            "checkout": {"path": str(project.resolve())},
        }
        with resolved_path.open("rb") as stream:
            placeholder = tomllib.load(stream)
        assert placeholder == {
            "devcapsule-resolved-schema-version": 1,
            "status": "unresolved",
        }
        assert record.stat().st_mode & 0o777 == 0o600
        assert resolved_path.stat().st_mode & 0o777 == 0o600
        original_input = record.read_bytes()
        original_resolution = resolved_path.read_bytes()

        assert cli.main(["project", "--path", str(project), "config", "list"]) == 0
        assert record.read_bytes() == original_input
        assert resolved_path.read_bytes() == original_resolution


def test_project_config_list_materializes_named_checkout_placeholder(
    tmp_path: Path, capsys
) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.mkdir()
    second.mkdir()
    config_home = tmp_path / "config"
    env = {"HOME": str(tmp_path / "home"), "XDG_CONFIG_HOME": str(config_home)}

    with patch.dict(os.environ, env, clear=False):
        initialize_project(first)
        shutil.copytree(first / ".devcapsule", second / ".devcapsule")
        assert cli.main(["project", "--path", str(first), "config", "list"]) == 0
        assert cli.main(["project", "--path", str(second), "config", "list"]) == 2
        assert "checkout register NAME" in capsys.readouterr().err
        assert (
            cli.main(
                ["project", "--path", str(second), "checkout", "register", "second-checkout"]
            )
            == 0
        )
        capsys.readouterr()
        assert cli.main(["project", "--path", str(second), "config", "list"]) == 0
        output = capsys.readouterr().out
        assert "Checkout name: second-checkout" in output
        records = {record.checkout_name: record for record in registered_checkouts()}
        named = records["second-checkout"].record_path
        assert named.with_name("second-checkout.resolved.toml").is_file()


def test_project_config_list_reports_complete_and_stale_readiness(
    tmp_path: Path, capsys
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    bound_home = tmp_path / "persistent-home"
    bound_home.mkdir()
    config_home = tmp_path / "config"
    env = {"HOME": str(tmp_path / "home"), "XDG_CONFIG_HOME": str(config_home)}

    with patch.dict(os.environ, env, clear=False):
        initialize_project(project)
        append_manifest_metadata(
            project,
            """
            [configuration.values."runtime.memory-limit"]
            type = "memory-size"
            required = true
            runtime-effect = "docker.memory-limit"

            [host.network.mode.recommended]
            value = "host"
            justification = "Reach host-bound development services."
            """,
        )
        write_formation_lock(project)

        assert cli.main(["project", "--path", str(project), "config", "list"]) == 0
        assert "missing-required" in capsys.readouterr().out
        assert (
            cli.main(
                [
                    "project",
                    "--path",
                    str(project),
                    "config",
                    "set",
                    "runtime.memory-limit",
                    "8GiB",
                ]
            )
            == 0
        )
        assert (
            cli.main(
                [
                    "project",
                    "--path",
                    str(project),
                    "config",
                    "bind",
                    "home",
                    "--host-directory",
                    str(bound_home),
                ]
            )
            == 0
        )
        for name, value in (("base-image", LOCKED_BASE), ("network", "host")):
            assert (
                cli.main(
                    [
                        "project",
                        "--path",
                        str(project),
                        "config",
                        "authorize",
                        name,
                        value,
                    ]
                )
                == 0
            )
        assert cli.main(["project", "--path", str(project), "config", "resolve"]) == 0
        capsys.readouterr()

        assert cli.main(["project", "--path", str(project), "config", "list"]) == 0
        output = capsys.readouterr().out
        assert "runtime.memory-limit" in output and "configured" in output
        assert "home" in output and "bound" in output
        assert "base-image" in output and "authorized" in output
        assert "network" in output and "authorized" in output
        assert "generated" in output and "fresh" in output

        record = registered_checkouts()[0].record_path
        checkout_text = record.read_text(encoding="utf-8")
        with record.open("rb") as stream:
            checkout = tomllib.load(stream)
        recommendation_digest = checkout["authorization"]["network"]["recommendation-digest"]
        record.write_text(
            checkout_text.replace(recommendation_digest, "0" * 64),
            encoding="utf-8",
        )

        assert cli.main(["project", "--path", str(project), "config", "list"]) == 0
        output = capsys.readouterr().out
        network_row = next(line for line in output.splitlines() if "network" in line)
        assert "stale" in network_row
        resolution_row = next(line for line in output.splitlines() if "resolution" in line)
        assert "stale" in resolution_row
        assert "checkout-input" in resolution_row


def test_project_resolve_accepts_formation_lock_without_completed_image(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    config_home = tmp_path / "config"
    env = {"HOME": str(tmp_path / "home"), "XDG_CONFIG_HOME": str(config_home)}

    with patch.dict(os.environ, env, clear=False):
        initialize_project(project)
        write_formation_lock(project)

        assert cli.main(["project", "--path", str(project), "config", "resolve"]) == 0

        records = registered_checkouts()
        resolved_path = records[0].record_path.with_name("devcapsule.resolved.toml")
        with resolved_path.open("rb") as stream:
            resolved = tomllib.load(stream)
        assert resolved["runtime"]["component"] == "pycharm"
        assert "image" not in resolved["runtime"]


def test_project_run_realizes_formation_and_launches_canonical_image(
    tmp_path: Path, capsys
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    config_home = tmp_path / "config"
    env = {
        "HOME": str(tmp_path / "home"),
        "XDG_CONFIG_HOME": str(config_home),
        "XDG_DATA_HOME": str(tmp_path / "data"),
        "OPENAI_API_KEY": "sk-test-never-persist",
    }
    canonical = "devcapsule-local-pycharm:0123456789abcdef0123"

    with patch.dict(os.environ, env, clear=False):
        initialize_project(project)
        (project / "devcapsule-src").mkdir()
        (project / "devcapsule-src" / "pyproject.toml").write_text(
            '[project]\nname = "devcapsule"\nversion = "0.0.0"\n',
            encoding="utf-8",
        )
        lock_path = write_formation_lock(project)
        select_codex_component(project)
        assert (
            cli.main(
                [
                    "project",
                    "--path",
                    str(project),
                    "config",
                    "authorize",
                    "base-image",
                    LOCKED_BASE,
                ]
            )
            == 0
        )
        assert (
            cli.main(
                [
                    "project",
                    "--path",
                    str(project),
                    "config",
                    "bind",
                    "codex/openai-api-key",
                    "--host-environment-variable",
                    "OPENAI_API_KEY",
                ]
            )
            == 0
        )
        assert cli.main(["project", "--path", str(project), "config", "resolve"]) == 0
        capsys.readouterr()

        realized = SimpleNamespace(
            image=SimpleNamespace(reference=canonical),
            created=False,
            locked=parse_locked_environment(tomllib.loads(lock_path.read_text(encoding="utf-8"))),
        )
        with (
            patch("devcapsule.commands.project.realize_environment", return_value=realized) as realize,
            patch("devcapsule.commands.project.run_pycharm", return_value=0) as launch,
        ):
            assert (
                cli.main(
                    [
                        "project",
                        "--path",
                        str(project),
                        "run",
                        "--docker-daemon",
                        "host-socket",
                        "--host-browser",
                    ]
                )
                == 0
            )

        selected = realize.call_args.args[0]
        assert selected.root == project.resolve()
        assert selected.checkout_path == registered_checkouts()[0].record_path
        assert selected.resolution_path == selected.checkout_path.with_name(
            "devcapsule.resolved.toml"
        )
        assert "sk-test-never-persist" not in selected.checkout_path.read_text(encoding="utf-8")
        assert selected.resolution["secret"]["bindings"]["host-environment"] == {
            "codex/openai-api-key": "OPENAI_API_KEY"
        }
        options = launch.call_args.args[0]
        assert options.image == canonical
        assert options.use_image_process is True
        assert options.runtime_plan.project_path == "/workspace/project"
        assert options.runtime_plan.home == "/home/devcapsule"
        assert options.runtime_plan.slots_by_name()["pycharm/config"] == "/ide-config"
        codex_state, codex_destination = options.additional_state_mounts["codex/home"]
        assert codex_state == (
            tmp_path
            / "data"
            / "devcapsule"
            / "projects"
            / "by-path"
            / project_namespace(project.resolve())
            / "components"
            / "codex"
            / "home"
        ).resolve()
        assert codex_destination == "/home/devcapsule/.codex"
        assert options.runtime_plan.component_environment() == {
            "CODEX_HOME": "/home/devcapsule/.codex",
            "JAVA_TOOL_OPTIONS": "-Dide.browser.jcef.sandbox.enable=false",
        }
        assert options.secret_environment == ("OPENAI_API_KEY",)
        assert options.additional_environment == {"DEVCAPSULE_RECURSIVE_E2E": "1"}
        assert options.enable_host_browser is True
        assert "Reused canonical environment" in capsys.readouterr().out

        with (
            patch("devcapsule.commands.project.realize_environment", return_value=realized),
            patch("devcapsule.commands.project.run_pycharm", return_value=0) as downgraded_launch,
        ):
            assert (
                cli.main(
                    [
                        "project",
                        "--path",
                        str(project),
                        "run",
                        "--docker-daemon",
                        "host-socket",
                        "--development-sudo",
                        "--no-recursive-e2e",
                    ]
                )
                == 0
            )

        downgraded = downgraded_launch.call_args.args[0]
        assert downgraded.docker_mode is DockerMode.none
        assert downgraded.enable_sudo is False
        assert downgraded.network_mode == "bridge"
        assert downgraded.additional_environment == {"DEVCAPSULE_RECURSIVE_E2E": "0"}
        assert downgraded.enable_host_browser is False
        assert "were downgraded" in capsys.readouterr().out


def test_project_run_does_not_launch_when_environment_realization_fails(
    tmp_path: Path, capsys
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    config_home = tmp_path / "config"
    env = {"HOME": str(tmp_path / "home"), "XDG_CONFIG_HOME": str(config_home)}

    with patch.dict(os.environ, env, clear=False):
        initialize_project(project)
        write_formation_lock(project)
        assert (
            cli.main(
                [
                    "project",
                    "--path",
                    str(project),
                    "config",
                    "authorize",
                    "base-image",
                    LOCKED_BASE,
                ]
            )
            == 0
        )
        assert cli.main(["project", "--path", str(project), "config", "resolve"]) == 0
        capsys.readouterr()

        with (
            patch(
                "devcapsule.commands.project.realize_environment",
                side_effect=ProjectConfigurationError("canonical image metadata conflict"),
            ),
            patch("devcapsule.commands.project.run_pycharm") as launch,
        ):
            assert cli.main(["project", "--path", str(project), "run"]) == 2

        launch.assert_not_called()
        assert "canonical image metadata conflict" in capsys.readouterr().err


def test_project_config_set_uses_declared_metadata_and_resolves_runtime_effect(
    tmp_path: Path, capsys
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    config_home = tmp_path / "config"
    env = {"HOME": str(tmp_path / "home"), "XDG_CONFIG_HOME": str(config_home)}

    with patch.dict(os.environ, env, clear=False):
        initialize_project(project)
        append_manifest_metadata(
            project,
            """
            [configuration.values."editor.theme"]
            type = "string"

            [configuration.values."runtime.memory-limit"]
            type = "memory-size"
            runtime-effect = "docker.memory-limit"
            """,
        )

        assert (
            cli.main(
                [
                    "project",
                    "--path",
                    str(project),
                    "config",
                    "set",
                    "editor.theme",
                    "dark",
                ]
            )
            == 0
        )
        assert "Checkout input:" in capsys.readouterr().out
        assert (
            cli.main(
                [
                    "project",
                    "--path",
                    str(project),
                    "config",
                    "set",
                    "runtime.memory-limit",
                    "8GiB",
                ]
            )
            == 0
        )
        assert (
            cli.main(
                ["project", "--path", str(project), "config", "set", "undeclared", "value"]
            )
            == 2
        )
        assert "is not declared" in capsys.readouterr().err
        assert (
            cli.main(
                [
                    "project",
                    "--path",
                    str(project),
                    "config",
                    "set",
                    "runtime.memory-limit",
                    "eight",
                ]
            )
            == 2
        )
        assert "positive memory size" in capsys.readouterr().err

        assert cli.main(["project", "--path", str(project), "config", "resolve"]) == 0
        record = registered_checkouts()[0].record_path
        with record.open("rb") as stream:
            checkout = tomllib.load(stream)
        assert checkout["configuration"]["values"] == {
            "editor.theme": "dark",
            "runtime.memory-limit": "8GiB",
        }
        with record.with_name("devcapsule.resolved.toml").open("rb") as stream:
            resolved = tomllib.load(stream)
        assert resolved["configuration"]["values"] == checkout["configuration"]["values"]
        assert resolved["runtime"]["memory-limit-bytes"] == 8 * 1024**3


def test_project_config_bind_uses_component_metadata_and_resolves_host_directories(
    tmp_path: Path, capsys
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    config_home = tmp_path / "config"
    env = {"HOME": str(tmp_path / "home"), "XDG_CONFIG_HOME": str(config_home)}
    slots = (
        "home",
        "pycharm/config",
        "pycharm/plugins",
        "pycharm/system",
        "pycharm/log",
        "pycharm/cache",
    )
    directories = {slot: tmp_path / slot.replace("/", "-") for slot in slots}
    for directory in directories.values():
        directory.mkdir()

    with patch.dict(os.environ, env, clear=False):
        initialize_project(project)
        for slot, directory in directories.items():
            assert (
                cli.main(
                    [
                        "project",
                        "--path",
                        str(project),
                        "config",
                        "bind",
                        slot,
                        "--host-directory",
                        str(directory),
                    ]
                )
                == 0
            )
            warning = capsys.readouterr().err
            assert "exposing host directory read-write" in warning
            assert "Concurrency: exclusive" in warning

        assert (
            cli.main(
                [
                    "project",
                    "--path",
                    str(project),
                    "config",
                    "bind",
                    "pycharm/unknown",
                    "--host-directory",
                    str(directories["home"]),
                ]
            )
            == 2
        )
        assert "is not declared" in capsys.readouterr().err
        assert (
            cli.main(
                [
                    "project",
                    "--path",
                    str(project),
                    "config",
                    "bind",
                    "home",
                    "--host-directory",
                    str(tmp_path / "missing"),
                ]
            )
            == 2
        )
        assert "not an existing directory" in capsys.readouterr().err

        assert cli.main(["project", "--path", str(project), "config", "resolve"]) == 0
        record = registered_checkouts()[0].record_path
        with record.open("rb") as stream:
            checkout = tomllib.load(stream)
        expected = {slot: str(path.resolve()) for slot, path in directories.items()}
        assert checkout["configuration"]["bindings"]["host-directory"] == expected
        with record.with_name("devcapsule.resolved.toml").open("rb") as stream:
            resolved = tomllib.load(stream)
        assert resolved["state"]["bindings"] == expected


def test_project_config_authorize_uses_exact_recommendations_and_drives_run(
    tmp_path: Path, capsys
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    config_home = tmp_path / "config"
    env = {"HOME": str(tmp_path / "home"), "XDG_CONFIG_HOME": str(config_home)}

    with patch.dict(os.environ, env, clear=False):
        initialize_project(project)
        append_manifest_metadata(
            project,
            """
            [configuration.values."runtime.memory-limit"]
            type = "memory-size"
            runtime-effect = "docker.memory-limit"

            [host.docker.mode.recommended]
            value = "host-socket"
            justification = "Run peer development containers."

            [host.network.mode.recommended]
            value = "host"
            justification = "Reach host-bound development services."

            [host.privilege.development-sudo.recommended]
            value = true
            justification = "Perform reviewed development administration."
            """,
        )

        commands = (
            ("docker-daemon", "host-socket"),
            ("network", "host"),
            ("development-sudo", "true"),
        )
        for name, value in commands:
            assert (
                cli.main(
                    [
                        "project",
                        "--path",
                        str(project),
                        "config",
                        "authorize",
                        name,
                        value,
                    ]
                )
                == 0
            )
            output = capsys.readouterr().out
            assert f"Authorized {name} for this checkout" in output
            assert "Checkout input:" in output

        assert (
            cli.main(
                [
                    "project",
                    "--path",
                    str(project),
                    "config",
                    "set",
                    "runtime.memory-limit",
                    "8GiB",
                ]
            )
            == 0
        )

        assert (
            cli.main(
                [
                    "project",
                    "--path",
                    str(project),
                    "config",
                    "authorize",
                    "network",
                    "bridge",
                ]
            )
            == 2
        )
        assert "exactly 'host'" in capsys.readouterr().err
        assert (
            cli.main(
                [
                    "project",
                    "--path",
                    str(project),
                    "config",
                    "authorize",
                    "device",
                    "gpu",
                ]
            )
            == 2
        )
        assert "is not declared" in capsys.readouterr().err

        assert cli.main(["project", "--path", str(project), "config", "resolve"]) == 0
        record = registered_checkouts()[0].record_path
        with record.open("rb") as stream:
            checkout = tomllib.load(stream)
        assert checkout["authorization"]["docker-daemon"]["value"] == "host-socket"
        assert checkout["authorization"]["network"]["value"] == "host"
        assert checkout["authorization"]["development-sudo"]["value"] is True
        with record.with_name("devcapsule.resolved.toml").open("rb") as stream:
            resolved = tomllib.load(stream)
        assert resolved["authorization"] == {
            "development-sudo": True,
            "docker-daemon": "host-socket",
            "network": "host",
        }

        with patch("devcapsule.commands.project.run_pycharm", return_value=0) as run:
            assert cli.main(["project", "--path", str(project), "run"]) == 0
        options = run.call_args.args[0]
        assert options.docker_mode.value == "host"
        assert options.network_mode == "host"
        assert options.enable_sudo is True
        assert options.memory_limit_bytes == 8 * 1024**3

        manifest_path = project / ".devcapsule" / "devcapsule.toml"
        manifest_path.write_text(
            manifest_path.read_text(encoding="utf-8").replace(
                "Reach host-bound development services.",
                "Changed host-network justification.",
            ),
            encoding="utf-8",
        )
        with manifest_path.open("rb") as stream:
            manifest = tomllib.load(stream)
        lock_path = project / ".devcapsule" / "devcapsule.linux-amd64.lock"
        lock_path.write_text(
            "\n".join(
                f'manifest-digest = "{canonical_digest(manifest)}"'
                if line.startswith("manifest-digest = ")
                else line
                for line in lock_path.read_text(encoding="utf-8").splitlines()
            )
            + "\n",
            encoding="utf-8",
        )
        assert cli.main(["project", "--path", str(project), "config", "resolve"]) == 2
        assert "authorization 'network' is stale" in capsys.readouterr().err


def test_project_config_authorize_accepts_inspected_local_base_and_pins_image_id(
    tmp_path: Path, capsys
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    config_home = tmp_path / "config"
    env = {"HOME": str(tmp_path / "home"), "XDG_CONFIG_HOME": str(config_home)}
    local_reference = "devcapsule-local-base:v022"
    local_identity = f"sha256:{'c' * 64}"
    local_base = ImageDetails(
        reference=local_reference,
        identity=local_identity,
        labels={
            "devcapsule.image.managed": "true",
            "devcapsule.metadata.version": "1",
            "devcapsule.image.kind": "base",
        },
        operating_system="linux",
        architecture="amd64",
    )

    with patch.dict(os.environ, env, clear=False):
        initialize_project(project)
        write_formation_lock(project)
        with patch(
            "devcapsule.commands.project.required_local_image",
            return_value=local_base,
        ) as inspect_local:
            assert (
                cli.main(
                    [
                        "project",
                        "--path",
                        str(project),
                        "config",
                        "authorize",
                        "base-image",
                        local_reference,
                    ]
                )
                == 0
            )
        inspect_local.assert_called_once_with(local_reference)
        output = capsys.readouterr().out
        assert f"Authorized base-image for this checkout: {local_reference}" in output
        assert f"Local image ID: {local_identity}" in output
        assert "overrides the published base recommendation" in output

        record = registered_checkouts()[0].record_path
        with record.open("rb") as stream:
            checkout = tomllib.load(stream)
        assert checkout["authorization"]["base-image"] == {
            "reference": local_reference,
            "lock-digest": canonical_digest(
                tomllib.loads(
                    (project / ".devcapsule" / "devcapsule.linux-amd64.lock").read_text(
                        encoding="utf-8"
                    )
                )
            ),
            "image-id": local_identity,
        }

        with patch(
            "devcapsule.commands.project.required_local_image",
            return_value=local_base,
        ) as inspect_resolved_local:
            assert cli.main(["project", "--path", str(project), "config", "resolve"]) == 0
        inspect_resolved_local.assert_called_once_with(local_reference)
        with record.with_name("devcapsule.resolved.toml").open("rb") as stream:
            resolved = tomllib.load(stream)
        assert resolved["authorization"]["base-image"] == {
            "reference": local_reference,
            "lock-digest": checkout["authorization"]["base-image"]["lock-digest"],
            "image-id": local_identity,
        }

        assert cli.main(["project", "--path", str(project), "config", "list"]) == 0
        base_row = next(
            line for line in capsys.readouterr().out.splitlines() if "base-image" in line
        )
        assert "authorized-local" in base_row
        assert local_reference in base_row


def test_project_config_authorize_all_recommended_previews_and_requires_lowercase_y(
    tmp_path: Path, capsys
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    config_home = tmp_path / "config"
    env = {"HOME": str(tmp_path / "home"), "XDG_CONFIG_HOME": str(config_home)}

    with patch.dict(os.environ, env, clear=False):
        initialize_project(project)
        append_manifest_metadata(
            project,
            """
            [host.docker.mode.recommended]
            value = "host-socket"
            justification = "Run peer development containers."

            [host.network.mode.recommended]
            value = "host"
            justification = "Reach host-bound development services."

            [host.privilege.development-sudo.recommended]
            value = true
            justification = "Perform reviewed development administration."
            """,
        )
        write_formation_lock(project)
        assert cli.main(["project", "--path", str(project), "config", "list"]) == 0
        capsys.readouterr()

        with (
            patch("devcapsule.commands.project.sys.stdin") as terminal,
            patch("devcapsule.commands.project.readchar.readkey", return_value="y") as readkey,
        ):
            terminal.isatty.return_value = True
            assert (
                cli.main(
                    [
                        "project",
                        "--path",
                        str(project),
                        "config",
                        "authorize",
                        "--all-recommended",
                    ]
                )
                == 0
            )
        readkey.assert_called_once_with()
        output = capsys.readouterr().out
        assert output.index("- base-image:") < output.index("Press y to authorize")
        assert output.index("- docker-daemon: host-socket") < output.index("Press y to authorize")
        assert output.index("- network: host") < output.index("Press y to authorize")
        assert output.index("- development-sudo: true") < output.index("Press y to authorize")
        assert "Justification: Run peer development containers." in output
        assert "Recommendation digest:" in output
        assert "Authorized 4 recommendations for this checkout." in output

        record = registered_checkouts()[0].record_path
        with record.open("rb") as stream:
            checkout = tomllib.load(stream)
        assert set(checkout["authorization"]) == {
            "base-image",
            "development-sudo",
            "docker-daemon",
            "network",
        }
        assert checkout["authorization"]["base-image"]["reference"] == LOCKED_BASE
        assert checkout["authorization"]["docker-daemon"]["value"] == "host-socket"
        assert checkout["authorization"]["network"]["value"] == "host"
        assert checkout["authorization"]["development-sudo"]["value"] is True


@pytest.mark.parametrize("key", ["Y", "n", "\n"])
def test_project_config_authorize_all_recommended_cancels_without_lowercase_y(
    tmp_path: Path, capsys, key: str
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    config_home = tmp_path / "config"
    env = {"HOME": str(tmp_path / "home"), "XDG_CONFIG_HOME": str(config_home)}

    with patch.dict(os.environ, env, clear=False):
        initialize_project(project)
        write_formation_lock(project)
        assert cli.main(["project", "--path", str(project), "config", "list"]) == 0
        record = registered_checkouts()[0].record_path
        original_input = record.read_bytes()
        capsys.readouterr()
        with (
            patch("devcapsule.commands.project.sys.stdin") as terminal,
            patch("devcapsule.commands.project.readchar.readkey", return_value=key),
        ):
            terminal.isatty.return_value = True
            assert (
                cli.main(
                    [
                        "project",
                        "--path",
                        str(project),
                        "config",
                        "authorize",
                        "--all-recommended",
                    ]
                )
                == 1
            )
        assert "Authorization cancelled; no changes written." in capsys.readouterr().out
        assert record.read_bytes() == original_input


def test_project_config_authorize_all_recommended_rejects_noninteractive_input(
    tmp_path: Path, capsys
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    config_home = tmp_path / "config"
    env = {"HOME": str(tmp_path / "home"), "XDG_CONFIG_HOME": str(config_home)}

    with patch.dict(os.environ, env, clear=False):
        initialize_project(project)
        write_formation_lock(project)
        capsys.readouterr()
        with (
            patch("devcapsule.commands.project.sys.stdin") as terminal,
            patch("devcapsule.commands.project.readchar.readkey") as readkey,
        ):
            terminal.isatty.return_value = False
            assert (
                cli.main(
                    [
                        "project",
                        "--path",
                        str(project),
                        "config",
                        "authorize",
                        "--all-recommended",
                    ]
                )
                == 2
            )
        readkey.assert_not_called()
        captured = capsys.readouterr()
        assert "The following authorizations will be granted" in captured.out
        assert "requires an interactive terminal" in captured.err
        assert registered_checkouts() == ()


def test_project_authorizes_only_exact_locked_base_and_lock_change_stales_it(
    tmp_path: Path, capsys
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    config_home = tmp_path / "config"
    env = {"HOME": str(tmp_path / "home"), "XDG_CONFIG_HOME": str(config_home)}

    with patch.dict(os.environ, env, clear=False):
        initialize_project(project)
        lock_path = write_formation_lock(project)
        assert cli.main(["project", "--path", str(project), "config", "resolve"]) == 0

        wrong = f"docker.io/example/devcapsule-base@sha256:{'c' * 64}"
        assert (
            cli.main(
                ["project", "--path", str(project), "config", "authorize", "base-image", wrong]
            )
            == 2
        )
        assert "Project recommendation 'base-image' is exactly" in capsys.readouterr().err

        assert (
            cli.main(
                [
                    "project",
                    "--path",
                    str(project),
                    "config",
                    "authorize",
                    "base-image",
                    LOCKED_BASE,
                ]
            )
            == 0
        )
        authorization_output = capsys.readouterr().out
        assert "Checkout input:" in authorization_output
        record = registered_checkouts()[0].record_path
        with record.open("rb") as stream:
            checkout = tomllib.load(stream)
        assert checkout["authorization"]["base-image"]["reference"] == LOCKED_BASE

        home = tmp_path / "persistent-home"
        home.mkdir()
        assert (
            cli.main(
                [
                    "project",
                    "--path",
                    str(project),
                    "state",
                    "adopt",
                    "home",
                    "--from",
                    str(home),
                ]
            )
            == 0
        )
        with record.open("rb") as stream:
            checkout = tomllib.load(stream)
        assert checkout["authorization"]["base-image"]["reference"] == LOCKED_BASE

        assert cli.main(["project", "--path", str(project), "config", "resolve"]) == 0
        resolved_path = record.with_name("devcapsule.resolved.toml")
        with resolved_path.open("rb") as stream:
            resolved = tomllib.load(stream)
        assert resolved["authorization"]["base-image"]["reference"] == LOCKED_BASE

        lock_path.write_text(
            lock_path.read_text(encoding="utf-8").replace("formation-v1", "formation-v2"),
            encoding="utf-8",
        )
        assert cli.main(["project", "--path", str(project), "config", "resolve"]) == 2
        assert "authorization is stale" in capsys.readouterr().err


@pytest.mark.parametrize(
    "reference",
    [
        "devcapsule-local-base:v020",
        "sha256:" + "a" * 64,
        "docker.io/example/devcapsule-base:latest",
        "localhost:5000/example/devcapsule-base@sha256:" + "a" * 64,
    ],
)
def test_committed_base_reference_rejects_local_or_mutable_names(reference: str) -> None:
    with pytest.raises(ProjectConfigurationError):
        immutable_registry_reference(reference)
