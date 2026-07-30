"""Redistributable DevCapsule development-base image planning."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from devcapsule.compat import CliError
from devcapsule.configurations.pycharm._image_build import BASE_APT_PACKAGES
from devcapsule.image_build import (
    AptPackagesComponent,
    BaseImageComponent,
    BuildComponent,
    BuildxImageBuilder,
    CommandComponent,
    EntrypointComponent,
    FileComponent,
    ImageBuildSpec,
    LabelComponent,
)
from devcapsule.image_tooling import public_default_cli_tooling_component


DEFAULT_ROOT_IMAGE = "ubuntu:24.04"
DEFAULT_OUTPUT_IMAGE = "devcapsule-base:latest"
PEX_DESTINATION = "/opt/devcapsule/bin/devcapsule.pex"
RUNTIME_PLAN_PATH = "/etc/devcapsule/runtime-plan.json"
BASE_RECIPE_VERSION = "1"


@dataclass(frozen=True)
class BaseImageBuildOptions:
    pex: Path
    image: str = DEFAULT_OUTPUT_IMAGE
    root_image: str = DEFAULT_ROOT_IMAGE
    source_revision: str = "unknown"
    install_baseline: bool = True


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_base_image_spec(options: BaseImageBuildOptions) -> ImageBuildSpec:
    pex = options.pex.expanduser().resolve()
    if not pex.is_file():
        raise CliError(f"DevCapsule PEX does not exist: {pex}")
    components: list[BuildComponent] = [BaseImageComponent(options.root_image)]
    if options.install_baseline:
        components.extend(
            [
                AptPackagesComponent(BASE_APT_PACKAGES),
                public_default_cli_tooling_component(),
            ]
        )
    components.extend(
        [
            FileComponent(pex, PEX_DESTINATION, permissions=0o755),
            LabelComponent(
                (
                    ("devcapsule.image.kind", "base"),
                    ("devcapsule.base.recipe-version", BASE_RECIPE_VERSION),
                    ("devcapsule.pex.sha256", file_sha256(pex)),
                    ("devcapsule.source.revision", options.source_revision),
                )
            ),
            EntrypointComponent(("/usr/bin/tini", "--", PEX_DESTINATION, "runtime")),
            CommandComponent((RUNTIME_PLAN_PATH,)),
        ]
    )
    return ImageBuildSpec(options.image, options.root_image, tuple(components))


def build_base_image(options: BaseImageBuildOptions, builder: BuildxImageBuilder | None = None) -> None:
    (builder or BuildxImageBuilder()).build(build_base_image_spec(options))
