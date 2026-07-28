"""Persistent-state commands for the first capability-first slice."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import click

from devcapsule.commands.base import BaseCommand
from devcapsule.project_configuration import (
    ProjectConfigurationError,
    atomic_write,
    checkout_path,
    load_toml,
    manifest_for,
    render_checkout,
)


KNOWN_SLOTS = {"home", "pycharm/config", "pycharm/plugins", "pycharm/system", "pycharm/log", "pycharm/cache"}


class StateCommand(BaseCommand):
    name = "state"
    help = "Inspect and adopt checkout-scoped persistent state."

    @classmethod
    def to_click_command(cls) -> click.Command:
        group = click.Group(name=cls.name, help=cls.help, no_args_is_help=True)

        @click.command("adopt")
        @click.argument("slot", type=click.Choice(sorted(KNOWN_SLOTS)))
        @click.option("--from", "source", type=click.Path(path_type=Path), required=True)
        @click.option("--project", type=click.Path(path_type=Path), default=Path("."))
        def adopt(slot: str, source: Path, project: Path) -> int:
            root, manifest = manifest_for(project)
            source = source.expanduser().resolve()
            if not source.is_dir():
                raise ProjectConfigurationError(f"State source is not a directory: {source}")
            path = checkout_path(manifest)
            checkout: dict[str, Any] = load_toml(path) if path.is_file() else {}
            recorded_path = checkout.get("checkout", {}).get("path")
            if recorded_path and Path(recorded_path).resolve() != root:
                raise ProjectConfigurationError(f"{path} belongs to another checkout: {recorded_path}")
            state = dict(checkout.get("state", {}).get("adopted", {}))
            host = dict(checkout.get("host", {}))
            state[slot] = str(source)
            atomic_write(path, render_checkout(manifest, root, state, host))
            click.echo(f"Adopted {slot}: {source}")
            click.echo("Run 'devcapsule config resolve' before launch.")
            return 0

        group.add_command(adopt)
        return group


COMMAND = StateCommand
