"""Generate the initial platform lock for the PyCharm dogfood base."""

from __future__ import annotations

from pathlib import Path

import click

from devcapsule.commands.base import BaseCommand
from devcapsule.project_configuration import (
    atomic_write,
    canonical_digest,
    manifest_for,
    platform_alias,
    quote_toml,
)


class LockCommand(BaseCommand):
    project: Path
    image: str

    name = "lock"
    help = "Generate the current-platform lock for the initial curated PyCharm slice."
    params = [
        click.Option(["--project"], type=click.Path(path_type=Path), default=Path(".")),
        click.Option(
            ["--image"], required=True,
            help="Existing local PyCharm image reference to pin for this dogfood slice.",
        ),
    ]

    def run(self) -> int:
        root, manifest = manifest_for(self.project)
        alias = platform_alias()
        output = root / ".devcapsule" / f"devcapsule.{alias}.lock"
        content = (
            "devcapsule-lock-format-version = 1\n"
            'resolution-matrix-version = "dogfood-v1"\n'
            f"manifest-digest = {quote_toml(canonical_digest(manifest))}\n"
            f"platform = {quote_toml(alias)}\n\n"
            "[image]\n"
            f"reference = {quote_toml(self.image)}\n\n"
            "[components]\n"
            'interactive-surface = "pycharm"\n'
        )
        atomic_write(output, content, mode=0o644)
        click.echo(f"Generated {output}")
        click.echo("This first dogfood lock pins a local image tag; immutable image digests remain follow-up work.")
        return 0


COMMAND = LockCommand
