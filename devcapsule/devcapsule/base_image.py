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
from devcapsule.image_metadata import BASE_KIND, managed_labels


DEFAULT_ROOT_IMAGE = "ubuntu:24.04"
NVIDIA_CUDA_ROOT_IMAGE = "nvidia/cuda:12.8.1-devel-ubuntu24.04"
DEFAULT_OUTPUT_IMAGE = "devcapsule-base:latest"
PEX_DESTINATION = "/opt/devcapsule/bin/devcapsule.pex"
RUNTIME_PLAN_PATH = "/etc/devcapsule/runtime-plan.json"
BASE_RECIPE_VERSION = "1"
DEFAULT_BASE_RECIPE = "ubuntu-24.04"
NVIDIA_CUDA_BASE_RECIPE = "nvidia-cuda-devel"
BASE_RECIPE_NAMES = (DEFAULT_BASE_RECIPE, NVIDIA_CUDA_BASE_RECIPE)


@dataclass(frozen=True)
class BaseImageRecipe:
    name: str
    default_root_image: str
    status: str
    labels: tuple[tuple[str, str], ...] = ()


BASE_IMAGE_RECIPES = {
    DEFAULT_BASE_RECIPE: BaseImageRecipe(
        name=DEFAULT_BASE_RECIPE,
        default_root_image=DEFAULT_ROOT_IMAGE,
        status="ready",
    ),
    NVIDIA_CUDA_BASE_RECIPE: BaseImageRecipe(
        name=NVIDIA_CUDA_BASE_RECIPE,
        default_root_image=NVIDIA_CUDA_ROOT_IMAGE,
        status="wip",
        labels=(
            ("devcapsule.base.gpu.vendor", "nvidia"),
            ("devcapsule.base.cuda.version", "12.8.1"),
        ),
    ),
}


@dataclass(frozen=True)
class BaseImageBuildOptions:
    pex: Path
    image: str = DEFAULT_OUTPUT_IMAGE
    root_image: str | None = None
    source_revision: str = "unknown"
    install_baseline: bool = True
    recipe: str = DEFAULT_BASE_RECIPE


def base_image_recipe(name: str) -> BaseImageRecipe:
    try:
        return BASE_IMAGE_RECIPES[name]
    except KeyError as exc:
        choices = ", ".join(BASE_RECIPE_NAMES)
        raise CliError(f"Unsupported DevCapsule base recipe {name!r}; choose one of: {choices}") from exc


def resolved_root_image(options: BaseImageBuildOptions) -> str:
    recipe = base_image_recipe(options.recipe)
    return options.root_image or recipe.default_root_image


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
    recipe = base_image_recipe(options.recipe)
    root_image = resolved_root_image(options)
    components: list[BuildComponent] = [BaseImageComponent(root_image)]
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
                managed_labels(BASE_KIND, options.image)
                + (
                    ("devcapsule.base.recipe", recipe.name),
                    ("devcapsule.base.recipe-version", BASE_RECIPE_VERSION),
                    ("devcapsule.base.recipe-status", recipe.status),
                    ("devcapsule.pex.sha256", file_sha256(pex)),
                    ("devcapsule.source.revision", options.source_revision),
                )
                + recipe.labels
            ),
            EntrypointComponent(("/usr/bin/tini", "--", PEX_DESTINATION, "runtime")),
            CommandComponent((RUNTIME_PLAN_PATH,)),
        ]
    )
    return ImageBuildSpec(options.image, root_image, tuple(components))


def build_base_image(
    options: BaseImageBuildOptions,
    builder: BuildxImageBuilder | None = None,
    *,
    network: str = "default",
) -> None:
    (builder or BuildxImageBuilder()).build(build_base_image_spec(options), network=network)
