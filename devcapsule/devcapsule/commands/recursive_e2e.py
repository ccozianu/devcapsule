"""Explicit recursive-dogfood engineering validation commands."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import click

from devcapsule.commands.base import BaseCommand
from devcapsule.recursive_dogfood import preflight_json, render_preflight, run_recursive_preflight


class RecursiveE2ECommand(BaseCommand):
    name = "recursive-e2e"
    help = "Run explicit recursive-dogfood engineering validation."

    @classmethod
    def to_click_command(cls) -> click.Command:
        group = click.Group(name=cls.name, help=cls.help, no_args_is_help=True)
        group.add_command(cls._preflight_command())
        return group

    @classmethod
    def _preflight_command(cls) -> click.Command:
        @click.command("preflight")
        @click.option(
            "--checkout",
            type=click.Path(path_type=Path),
            default=Path("."),
            show_default=True,
            help="Current source checkout or a descendant path.",
        )
        @click.option(
            "--runtime-plan",
            type=click.Path(path_type=Path),
            default=Path("/etc/devcapsule/runtime-plan.json"),
            show_default=True,
            help="External runtime plan mounted into the current capsule.",
        )
        @click.option("--json", "as_json", is_flag=True, help="Emit stable machine-readable JSON.")
        @click.option(
            "--show-host-paths",
            is_flag=True,
            help="Include sensitive host mount sources after an explicit warning.",
        )
        def preflight(
            checkout: Path,
            runtime_plan: Path,
            as_json: bool,
            show_host_paths: bool,
        ) -> int:
            if show_host_paths:
                click.secho(
                    "WARNING: debug output includes raw host filesystem mappings; do not share it unsanitized.",
                    fg="yellow",
                    err=True,
                )
            report = run_recursive_preflight(checkout, runtime_plan_path=runtime_plan)
            if as_json:
                click.echo(preflight_json(report, show_host_paths=show_host_paths))
            else:
                click.echo(render_preflight(report, show_host_paths=show_host_paths))
            return 0 if report.ready else 1

        return preflight

    def run(self) -> Any:
        raise NotImplementedError("Recursive E2E is a Click command group.")


COMMAND = RecursiveE2ECommand
