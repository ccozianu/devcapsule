"""Create a capability-first DevCapsule project declaration."""

from __future__ import annotations

from pathlib import Path

import click

from devcapsule.commands.base import BaseCommand
from devcapsule.project import sanitize_name
from devcapsule.project_configuration import ProjectConfigurationError, quote_toml


class InitCommand(BaseCommand):
    path: Path
    need: tuple[str, ...]
    project_name: str | None
    slug: str | None
    creator: str
    project_mount: str

    name = "init"
    help = "Create a new .devcapsule project declaration without merging or overwriting."
    params = [
        click.Argument(["path"], type=click.Path(path_type=Path), default=Path(".")),
        click.Option(["--need"], multiple=True, required=True),
        click.Option(["--name", "project_name"]),
        click.Option(["--slug"]),
        click.Option(["--creator"], required=True),
        click.Option(["--project-mount"], default="/workspace/project", show_default=True),
    ]

    def run(self) -> int:
        project = self.path.expanduser().resolve()
        target = project / ".devcapsule"
        if target.exists():
            raise ProjectConfigurationError(
                f"{project} is already initialized; inspect {target / 'devcapsule.toml'} instead."
            )
        if not project.is_dir():
            raise ProjectConfigurationError(f"Project directory does not exist: {project}")
        creator = self.creator if ":" in self.creator else f"mailto:{self.creator}"
        name = self.project_name or project.name
        slug = self.slug or sanitize_name(project.name).lower()
        needs = sorted(set(self.need))
        content = (
            "devcapsule-schema-version = 1\n\n"
            "[capabilities]\n"
            f"need = [{', '.join(quote_toml(item) for item in needs)}]\n\n"
            "[project]\n"
            f"name = {quote_toml(name)}\n"
            f"slug = {quote_toml(slug)}\n"
            f"creator = {quote_toml(creator)}\n"
            f"mount = {quote_toml(self.project_mount)}\n"
        )
        target.mkdir(mode=0o755)
        (target / "devcapsule.toml").write_text(content, encoding="utf-8")
        click.echo(f"Created {target / 'devcapsule.toml'}")
        click.echo("Next: generate or add the platform lock, then run 'devcapsule config resolve'.")
        return 0


COMMAND = InitCommand
