"""Focused tests for the v027 ``project init`` postcondition and entry states."""

from __future__ import annotations

import io
import os
from pathlib import Path
import tomllib
from unittest.mock import patch

import pytest

from devcapsule import cli
from devcapsule.elicitation import ElicitationIncomplete
from devcapsule.project_operations import (
    InitializeRequest,
    ProvidedAnswer,
    initialize_project,
)
from devcapsule.project_configuration import ProjectConfigurationError
from devcapsule.platforms import Platform
from devcapsule.resolution_matrix import MATRICES


def isolated_env(tmp_path: Path) -> dict[str, str]:
    return {
        "HOME": str(tmp_path / "home"),
        "XDG_CONFIG_HOME": str(tmp_path / "config"),
        "XDG_DATA_HOME": str(tmp_path / "data"),
    }


def read_toml(path: Path) -> dict:
    with path.open("rb") as stream:
        return tomllib.load(stream)


def matrix_reference_lock() -> dict:
    content = MATRICES[Platform.LINUX_AMD64].resolve(["python-ide"]).render_lock()
    return tomllib.loads(content)


def matrix_base_reference() -> str:
    return str(matrix_reference_lock()["base"]["reference"])


def test_noninteractive_init_reaches_the_full_postcondition(tmp_path: Path, capsys) -> None:
    project = tmp_path / "fresh-project"
    project.mkdir()
    with patch.dict(os.environ, isolated_env(tmp_path), clear=False):
        assert (
            cli.main(
                [
                    "project",
                    "--path",
                    str(project),
                    "init",
                    "--need",
                    "python",
                    "--need",
                    "python-ide",
                    "--creator",
                    "https://github.com/example",
                    "--authorize",
                    "base-image",
                    "yes",
                ]
            )
            == 0
        )
        output = capsys.readouterr().out

        manifest = read_toml(project / ".devcapsule" / "devcapsule.toml")
        assert manifest["project"] == {
            "name": "fresh-project",
            "slug": "fresh-project",
            "creator": "https://github.com/example",
            "mount": "/workspace/fresh-project",
        }
        assert manifest["capabilities"]["need"] == ["python", "python-ide"]

        lock = read_toml(project / ".devcapsule" / "devcapsule.linux-amd64.lock")
        assert lock["resolution-matrix-version"] == (
            matrix_reference_lock()["resolution-matrix-version"]
        )
        assert lock["base"]["reference"] == matrix_base_reference()

        config_root = tmp_path / "config" / "devcapsule" / "projects"
        records = list(config_root.rglob("devcapsule.checkout.toml"))
        assert len(records) == 1
        checkout = read_toml(records[0])
        assert checkout["authorization"]["base-image"]["reference"] == matrix_base_reference()
        resolution = read_toml(records[0].with_name("devcapsule.resolved.toml"))
        assert resolution["devcapsule-resolved-schema-version"] == 1
        assert resolution["runtime"]["component"] == "pycharm"

        assert "Created" in output
        assert "Project initialized" in output


def test_missing_base_authorization_batch_fails_with_the_exact_remedy(
    tmp_path: Path, capsys
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    with patch.dict(os.environ, isolated_env(tmp_path), clear=False):
        assert (
            cli.main(
                [
                    "project",
                    "--path",
                    str(project),
                    "init",
                    "--need",
                    "python-ide",
                    "--creator",
                    "dev@example.test",
                ]
            )
            == 2
        )
    message = capsys.readouterr().err
    assert f"--authorize base-image {matrix_base_reference()}" in message
    # The silent no-recommendation decision: unflagged intent questions do not
    # appear in the failure and record no recommendation.
    assert "docker-daemon" not in message


def test_missing_creator_fails_before_writing_any_artifact(tmp_path: Path, capsys) -> None:
    project = tmp_path / "project"
    project.mkdir()
    with patch.dict(os.environ, isolated_env(tmp_path), clear=False):
        assert (
            cli.main(["project", "--path", str(project), "init", "--need", "python-ide"])
            == 2
        )
    assert "--creator CREATOR" in capsys.readouterr().err
    assert not (project / ".devcapsule").exists()


def test_email_creator_is_normalized_to_mailto(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    with patch.dict(os.environ, isolated_env(tmp_path), clear=False):
        assert (
            cli.main(
                [
                    "project",
                    "--path",
                    str(project),
                    "init",
                    "--need",
                    "python-ide",
                    "--creator",
                    "dev@example.test",
                    "--authorize",
                    "base-image",
                    "yes",
                ]
            )
            == 0
        )
    manifest = read_toml(project / ".devcapsule" / "devcapsule.toml")
    assert manifest["project"]["creator"] == "mailto:dev@example.test"


def test_recommendation_answer_authors_manifest_and_owner_authorization(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    with patch.dict(os.environ, isolated_env(tmp_path), clear=False):
        assert (
            cli.main(
                [
                    "project",
                    "--path",
                    str(project),
                    "init",
                    "--need",
                    "python-ide",
                    "--creator",
                    "https://github.com/example",
                    "--authorize",
                    "docker-daemon",
                    "host-socket",
                    "Required to run peer capsules in the test suite.",
                    "--authorize",
                    "base-image",
                    "yes",
                ]
            )
            == 0
        )
        manifest = read_toml(project / ".devcapsule" / "devcapsule.toml")
        recommended = manifest["host"]["docker"]["mode"]["recommended"]
        assert recommended["value"] == "host-socket"
        assert recommended["justification"] == "Required to run peer capsules in the test suite."

        config_root = tmp_path / "config" / "devcapsule" / "projects"
        record = read_toml(next(config_root.rglob("devcapsule.checkout.toml")))
        assert record["authorization"]["docker-daemon"]["value"] == "host-socket"
        resolution = read_toml(
            next(config_root.rglob("devcapsule.resolved.toml"))
        )
        assert resolution["authorization"]["docker-daemon"] == "host-socket"


def test_recommendation_without_justification_batch_fails(tmp_path: Path, capsys) -> None:
    project = tmp_path / "project"
    project.mkdir()
    with patch.dict(os.environ, isolated_env(tmp_path), clear=False):
        assert (
            cli.main(
                [
                    "project",
                    "--path",
                    str(project),
                    "init",
                    "--need",
                    "python-ide",
                    "--creator",
                    "https://github.com/example",
                    "--authorize",
                    "docker-daemon",
                    "host-socket",
                ]
            )
            == 2
        )
    message = capsys.readouterr().err
    assert "docker-daemon (justification)" in message


def test_repair_completes_a_hand_authored_manifest(tmp_path: Path, capsys) -> None:
    project = tmp_path / "project"
    (project / ".devcapsule").mkdir(parents=True)
    (project / ".devcapsule" / "devcapsule.toml").write_text(
        "\n".join(
            [
                "devcapsule-schema-version = 1",
                "",
                "[capabilities]",
                'need = ["python", "python-ide"]',
                "",
                "[project]",
                'name = "Hand Authored"',
                'slug = "hand-authored"',
                'creator = "https://github.com/example"',
                'mount = "/workspace/hand-authored"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    original = (project / ".devcapsule" / "devcapsule.toml").read_bytes()
    with patch.dict(os.environ, isolated_env(tmp_path), clear=False):
        assert (
            cli.main(
                [
                    "project",
                    "--path",
                    str(project),
                    "init",
                    "--authorize",
                    "base-image",
                    "yes",
                ]
            )
            == 0
        )
    output = capsys.readouterr().out
    assert "Honored existing" in output
    # The authored manifest is byte-identical: repair completed the missing
    # derived artifacts without rewriting authored content.
    assert (project / ".devcapsule" / "devcapsule.toml").read_bytes() == original
    assert (project / ".devcapsule" / "devcapsule.linux-amd64.lock").is_file()


def test_fully_initialized_project_fails_loudly_naming_regenerate(
    tmp_path: Path, capsys
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    arguments = [
        "project",
        "--path",
        str(project),
        "init",
        "--need",
        "python-ide",
        "--creator",
        "https://github.com/example",
        "--authorize",
        "base-image",
        "yes",
    ]
    with patch.dict(os.environ, isolated_env(tmp_path), clear=False):
        assert cli.main(arguments) == 0
        capsys.readouterr()
        assert cli.main(arguments) == 2
        assert "--regenerate" in capsys.readouterr().err
        assert cli.main([*arguments, "--regenerate"]) == 0


def test_conflicting_recommendation_answer_is_rejected(tmp_path: Path, capsys) -> None:
    project = tmp_path / "project"
    project.mkdir()
    with patch.dict(os.environ, isolated_env(tmp_path), clear=False):
        assert (
            cli.main(
                [
                    "project",
                    "--path",
                    str(project),
                    "init",
                    "--need",
                    "python-ide",
                    "--creator",
                    "https://github.com/example",
                    "--authorize",
                    "network",
                    "host",
                    "Reach host-bound services.",
                    "--authorize",
                    "base-image",
                    "yes",
                ]
            )
            == 0
        )
        capsys.readouterr()
        assert (
            cli.main(
                [
                    "project",
                    "--path",
                    str(project),
                    "init",
                    "--regenerate",
                    "--authorize",
                    "network",
                    "none",
                ]
            )
            == 2
        )
    assert "never" in capsys.readouterr().err


def test_interactive_init_prompts_in_the_settled_order(tmp_path: Path) -> None:
    project = tmp_path / "interactive-project"
    project.mkdir()
    prompts = io.StringIO()
    # creator; need; four recommendations (Enter = none); base (Enter = yes).
    answers = io.StringIO(
        "https://github.com/example\npython python-ide\n\n\n\n\n\n"
    )
    with patch.dict(os.environ, isolated_env(tmp_path), clear=False):
        report = initialize_project(
            InitializeRequest(directory=project, interactive=True),
            input_stream=answers,
            output_stream=prompts,
        )
    transcript = prompts.getvalue()
    assert "Project creator" in transcript
    assert "Capabilities the project needs" in transcript
    assert "[none]" in transcript
    assert "[yes]" in transcript
    manifest = read_toml(project / ".devcapsule" / "devcapsule.toml")
    assert "host" not in manifest
    assert report.authorized == ("base-image",)
    assert report.capabilities == ("python", "python-ide")


def test_interactive_decline_of_the_base_is_a_clean_failure(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    answers = io.StringIO("https://github.com/example\npython-ide\n\n\n\n\nno\n")
    with patch.dict(os.environ, isolated_env(tmp_path), clear=False):
        with pytest.raises(ProjectConfigurationError, match="declined"):
            initialize_project(
                InitializeRequest(directory=project, interactive=True),
                input_stream=answers,
                output_stream=io.StringIO(),
            )


def test_claude_capability_requires_the_acquisition_answer(tmp_path: Path, capsys) -> None:
    project = tmp_path / "project"
    project.mkdir()
    base_arguments = [
        "project",
        "--path",
        str(project),
        "init",
        "--need",
        "python-ide",
        "--need",
        "claude-code-agent",
        "--creator",
        "https://github.com/example",
        "--authorize",
        "base-image",
        "yes",
    ]
    with patch.dict(os.environ, isolated_env(tmp_path), clear=False):
        assert cli.main(base_arguments) == 2
        assert "--authorize claude-code-download true" in capsys.readouterr().err
        assert (
            cli.main([*base_arguments, "--authorize", "claude-code-download", "true"]) == 0
        )
        config_root = tmp_path / "config" / "devcapsule" / "projects"
        record = read_toml(next(config_root.rglob("devcapsule.checkout.toml")))
        assert record["authorization"]["claude-code-download"]["value"] is True


def test_unknown_authorize_answer_is_reported_not_ignored(tmp_path: Path, capsys) -> None:
    project = tmp_path / "project"
    project.mkdir()
    with patch.dict(os.environ, isolated_env(tmp_path), clear=False):
        assert (
            cli.main(
                [
                    "project",
                    "--path",
                    str(project),
                    "init",
                    "--need",
                    "python-ide",
                    "--creator",
                    "https://github.com/example",
                    "--authorize",
                    "base-image",
                    "yes",
                    "--authorize",
                    "quantum-tunnel",
                    "open",
                ]
            )
            == 2
        )
    assert "matched no question" in capsys.readouterr().err


def test_set_and_bind_extras_are_applied_through_the_registry(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    bound_home = tmp_path / "bound-home"
    bound_home.mkdir()
    manifest_extra = ProvidedAnswer("bind", "home", f"host-directory:{bound_home}")
    with patch.dict(os.environ, isolated_env(tmp_path), clear=False):
        initialize_project(
            InitializeRequest(
                directory=project,
                need=("python-ide",),
                creator="https://github.com/example",
                answers=(
                    ProvidedAnswer("authorize", "base-image", "yes"),
                    manifest_extra,
                ),
                interactive=False,
            )
        )
        config_root = tmp_path / "config" / "devcapsule" / "projects"
        record = read_toml(next(config_root.rglob("devcapsule.checkout.toml")))
        assert record["configuration"]["bindings"]["host-directory"]["home"] == str(
            bound_home
        )


def test_operation_batch_failure_is_an_elicitation_incomplete(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    with patch.dict(os.environ, isolated_env(tmp_path), clear=False):
        with pytest.raises(ElicitationIncomplete):
            initialize_project(
                InitializeRequest(
                    directory=project, need=("python-ide",), interactive=False
                )
            )
