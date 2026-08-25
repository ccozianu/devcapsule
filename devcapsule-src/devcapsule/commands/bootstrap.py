"""Install packaged workflow definitions and initialize project memory."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Mapping

from devcapsule.commands.framework import Command, Group
from devcapsule.compat import CliError
from devcapsule.workflow_bootstrap import WorkflowBootstrapError, bootstrap_project


def _add_bootstrap_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--project",
        dest="project_path",
        type=Path,
        help="Project directory. Defaults to PROJECT_PATH or the current directory.",
    )
    parser.add_argument(
        "--refresh-workflow-definition",
        action="store_true",
        help="Replace reusable AGENTS.md and WORKFLOW.md; preserve project-owned state.",
    )


def _bootstrap(project_path: Path | None, refresh_workflow_definition: bool) -> int:
    selected = project_path or Path(".")
    try:
        report = bootstrap_project(
            selected,
            refresh_workflow_definition=refresh_workflow_definition,
        )
    except WorkflowBootstrapError as exc:
        raise CliError(str(exc)) from exc
    print(report.render())
    return 0


class BootstrapProjectCommand(Command):
    name = "project"
    help = "Install workflow files and initialize project memory."

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        _add_bootstrap_options(parser)

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        return _bootstrap(arguments.project_path, arguments.refresh_workflow_definition)


class BootstrapCommand(Group):
    name = "bootstrap"
    help = "Bootstrap project workflow files."

    @classmethod
    def subcommands(cls) -> Mapping[str, type[Command] | type[Group]]:
        return {BootstrapProjectCommand.name: BootstrapProjectCommand}

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        _add_bootstrap_options(parser)

    # Bare ``devcapsule bootstrap`` acts on the current project rather than
    # printing group help; the ``project`` subcommand is the explicit spelling.
    @classmethod
    def handle_empty(
        cls, arguments: argparse.Namespace, context: object | None, parser: argparse.ArgumentParser
    ) -> int:
        return _bootstrap(arguments.project_path, arguments.refresh_workflow_definition)


COMMAND = BootstrapCommand
