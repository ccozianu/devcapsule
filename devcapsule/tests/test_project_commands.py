from __future__ import annotations

import os
from pathlib import Path
import shutil
import tomllib
from unittest.mock import patch

from devcapsule import cli
from devcapsule.project_configuration import registered_checkouts
from devcapsule.project_configuration import canonical_digest


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


def test_project_resolve_registers_default_checkout_and_list_uses_registry(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    config_home = tmp_path / "config"
    env = {"HOME": str(tmp_path / "home"), "XDG_CONFIG_HOME": str(config_home)}

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


def test_project_resolve_accepts_formation_lock_without_completed_image(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    config_home = tmp_path / "config"
    env = {"HOME": str(tmp_path / "home"), "XDG_CONFIG_HOME": str(config_home)}

    with patch.dict(os.environ, env, clear=False):
        initialize_project(project)
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
                    'reference = "base@sha256:manifest"',
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

        assert cli.main(["project", "--path", str(project), "config", "resolve"]) == 0

        records = registered_checkouts()
        resolved_path = records[0].record_path.with_name("devcapsule.resolved.toml")
        with resolved_path.open("rb") as stream:
            resolved = tomllib.load(stream)
        assert resolved["runtime"]["component"] == "pycharm"
        assert "image" not in resolved["runtime"]
