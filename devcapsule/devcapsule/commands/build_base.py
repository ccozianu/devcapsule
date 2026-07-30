"""Build the redistributable DevCapsule development base."""

from __future__ import annotations

from pathlib import Path

import click

from devcapsule.base_image import BaseImageBuildOptions, build_base_image
from devcapsule.commands.base import BaseCommand


class BuildBaseCommand(BaseCommand):
    pex: Path
    image: str
    root_image: str
    source_revision: str

    name = "build-base"
    help = "Build the JetBrains-free DevCapsule development base image."
    params = [
        click.Option(["--pex"], type=click.Path(path_type=Path, exists=True, dir_okay=False), required=True),
        click.Option(["--image"], default="devcapsule-base:latest", show_default=True),
        click.Option(["--root-image"], default="ubuntu:24.04", show_default=True),
        click.Option(["--source-revision"], default="unknown", show_default=True),
    ]

    def run(self) -> int:
        build_base_image(BaseImageBuildOptions(self.pex, self.image, self.root_image, self.source_revision))
        return 0


COMMAND = BuildBaseCommand
