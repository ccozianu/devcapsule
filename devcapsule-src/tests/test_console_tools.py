"""``project checkout decisions``: the console's decision tools from the runtime CLI, inside a capsule only."""
from __future__ import annotations

from pathlib import Path

import pytest

from devcapsule import cli
from devcapsule.configuration.file_formats import ProjectConfigurationError
from devcapsule.console_tools import DECISIONS_MODULE, console_decisions_command
from devcapsule.components.pycharm import runtime_template as pycharm_runtime_template
from devcapsule.container_runtime.contract import ConsolePlan, Identity, RuntimePlan


def plan_with_source() -> str:
    """A runtime plan as the launcher writes one under the self-hosting exception."""
    plan = RuntimePlan.for_component(pycharm_runtime_template(), project_path="/workspace/p", home="/home/devcapsule",
                                     identity=Identity(1000, 1000, "developer"))
    console = ConsolePlan("0.0.0.0", 6081, "/run/devcapsule-console-token", source_path="/workspace/p/devcapsule-webconsole")
    return plan.with_console(console).to_json()


def test_outside_a_capsule_the_command_names_the_module_to_run_instead(tmp_path: Path) -> None:
    with pytest.raises(ProjectConfigurationError, match=f"python -m {DECISIONS_MODULE}"):
        console_decisions_command(["check", "x.json"], environ={}, console_python=tmp_path / "python")


def test_a_base_without_the_console_is_named(tmp_path: Path) -> None:
    with pytest.raises(ProjectConfigurationError, match="no web console at /opt/devcapsule-webconsole"):
        console_decisions_command(["check", "x.json"], environ={"DEVCAPSULE_CONTAINER_NAME": "c"},
                                  console_python=tmp_path / "absent", runtime_plan_path=tmp_path / "plan.json")


def test_the_installed_console_runs_the_module_with_the_arguments_verbatim(tmp_path: Path) -> None:
    python = tmp_path / "python"
    python.write_text("", encoding="utf-8")
    command = console_decisions_command(["hand-off", "d/x.json", "--token-file", "t"],
                                        environ={"DEVCAPSULE_CONTAINER_NAME": "c"}, console_python=python,
                                        runtime_plan_path=tmp_path / "no-plan.json")
    assert command == (str(python), "-m", DECISIONS_MODULE, "hand-off", "d/x.json", "--token-file", "t")


def test_a_mounted_console_source_goes_first_on_the_path_as_the_console_child_does(tmp_path: Path) -> None:
    python = tmp_path / "python"
    python.write_text("", encoding="utf-8")
    plan = tmp_path / "plan.json"
    plan.write_text(plan_with_source(), encoding="utf-8")
    command = console_decisions_command(["check", "x.json"], environ={"DEVCAPSULE_CONTAINER_NAME": "c"},
                                        console_python=python, runtime_plan_path=plan)
    assert command == ("env", "PYTHONPATH=/workspace/p/devcapsule-webconsole", str(python), "-m", DECISIONS_MODULE,
                       "check", "x.json")
    plan.write_text("{", encoding="utf-8")  # an unreadable plan: the installed console serves
    assert console_decisions_command(["check", "x.json"], environ={"DEVCAPSULE_CONTAINER_NAME": "c"},
                                     console_python=python, runtime_plan_path=plan)[0] == str(python)


def test_the_command_line_runs_the_console_module_and_returns_its_status(tmp_path: Path, capsys, monkeypatch) -> None:
    fake = tmp_path / "fake-console-python"
    fake.write_text("#!/bin/sh\necho \"console-args: $*\"\nexit 3\n", encoding="utf-8")
    fake.chmod(0o755)
    monkeypatch.setattr("devcapsule.container_runtime.console.CONSOLE_PYTHON", str(fake))
    monkeypatch.setattr("devcapsule.recursive_dogfood.RUNTIME_PLAN_PATH", tmp_path / "no-plan.json")
    monkeypatch.setenv("DEVCAPSULE_CONTAINER_NAME", "capsule-fixture")
    monkeypatch.chdir(tmp_path)
    assert cli.main(["project", "checkout", "decisions", "from-table", "t.md", "--id", "pass", "--title", "Pass"]) == 3
    assert capsys.readouterr().out == "", "the module's own output goes to the terminal, not through the CLI"
    monkeypatch.delenv("DEVCAPSULE_CONTAINER_NAME")
    assert cli.main(["project", "checkout", "decisions", "check", "x.json"]) == 2
    assert "runs inside a capsule" in capsys.readouterr().err
