"""Install packaged workflow definitions and initialize project memory."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import click

from devcapsule.commands.base import BaseCommand
from devcapsule.compat import CliError
from devcapsule.workflow_bootstrap import WorkflowBootstrapError, bootstrap_project


class BootstrapCommand(BaseCommand):
    name = "bootstrap"
    help = "Bootstrap project workflow files."

    @classmethod
    def to_click_command(cls) -> click.Command:
        @click.group(
            name=cls.name,
            help=cls.help,
            invoke_without_command=True,
        )
        @click.option(
            "--project",
            "project_path",
            type=click.Path(path_type=Path, file_okay=False, dir_okay=True),
            help="Project directory. Defaults to PROJECT_PATH or the current directory.",
        )
        @click.option(
            "--refresh-workflow-definition",
            is_flag=True,
            help="Replace reusable AGENTS.md and WORKFLOW.md; preserve project-owned state.",
        )
        @click.pass_context
        def group(
            ctx: click.Context,
            project_path: Path | None,
            refresh_workflow_definition: bool,
        ) -> int | None:
            if ctx.invoked_subcommand is not None:
                return None
            return cls._bootstrap(project_path, refresh_workflow_definition)

        group.add_command(cls._project_command())
        return group

    @classmethod
    def _project_command(cls) -> click.Command:
        @click.command("project", help="Install workflow files and initialize project memory.")
        @click.option(
            "--project",
            "project_path",
            type=click.Path(path_type=Path, file_okay=False, dir_okay=True),
            help="Project directory. Defaults to PROJECT_PATH or the current directory.",
        )
        @click.option(
            "--refresh-workflow-definition",
            is_flag=True,
            help="Replace reusable AGENTS.md and WORKFLOW.md; preserve project-owned state.",
        )
        def command(
            project_path: Path | None, refresh_workflow_definition: bool
        ) -> int:
            return cls._bootstrap(project_path, refresh_workflow_definition)

        return command

    @staticmethod
    def _bootstrap(
        project_path: Path | None, refresh_workflow_definition: bool
    ) -> int:
        selected = project_path or Path(".")
        try:
            report = bootstrap_project(
                selected,
                refresh_workflow_definition=refresh_workflow_definition,
            )
        except WorkflowBootstrapError as exc:
            raise CliError(str(exc)) from exc
        click.echo(report.render())
        return 0

    def run(self) -> Any:
        raise NotImplementedError("Bootstrap is a Click command group.")


COMMAND = BootstrapCommand
