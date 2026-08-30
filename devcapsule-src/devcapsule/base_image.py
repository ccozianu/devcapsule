"""Redistributable DevCapsule development-base image planning."""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
import urllib.error
import urllib.request

from devcapsule.build_info import BuildInfo, BuildInfoError, read_pex_build_info
from devcapsule.compat import CliError
from devcapsule.configurations.pycharm._image_build import BASE_APT_PACKAGES
from devcapsule.image_build import (
    AptPackagesComponent,
    BaseImageComponent,
    BuildComponent,
    BuildxImageBuilder,
    CommandComponent,
    EntrypointComponent,
    EnvComponent,
    FileComponent,
    ImageBuildSpec,
    LabelComponent,
)
from devcapsule.image_tooling import (
    MAVEN_CURRENT,
    MAVEN_CURRENT_BIN,
    MAVEN_VERSION,
    NODE_CURRENT_BIN,
    TEMURIN_CURRENT,
    TEMURIN_CURRENT_BIN,
    TEMURIN_VERSION,
    maven_tooling_component,
    node_tooling_component,
    temurin_tooling_component,
)
from devcapsule.image_metadata import BASE_KIND, managed_labels


DEFAULT_ROOT_IMAGE = "ubuntu:24.04"
NVIDIA_CUDA_ROOT_IMAGE = "nvidia/cuda:12.8.1-devel-ubuntu24.04"
DEFAULT_OUTPUT_IMAGE = "devcapsule-base:latest"
PEX_DESTINATION = "/opt/devcapsule/bin/devcapsule.pex"
RUNTIME_PLAN_PATH = "/etc/devcapsule/runtime-plan.json"
BASE_RECIPE_VERSION = "5"
DEFAULT_BASE_RECIPE = "ubuntu-24.04"
NVIDIA_CUDA_BASE_RECIPE = "nvidia-cuda-devel"
BASE_RECIPE_NAMES = (DEFAULT_BASE_RECIPE, NVIDIA_CUDA_BASE_RECIPE)
PUBLIC_SOURCE_TIMEOUT_SECONDS = 10


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
    source_revision: str | None = None
    allow_local_source: bool = False
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


def pex_build_info(options: BaseImageBuildOptions) -> BuildInfo:
    try:
        info = read_pex_build_info(options.pex.expanduser().resolve())
    except BuildInfoError as exc:
        raise CliError(str(exc)) from exc
    if options.source_revision is not None and options.source_revision != info.source_revision:
        raise CliError(
            f"Expected source revision {options.source_revision}, but the selected PEX embeds "
            f"{info.source_revision}. Nox writes local-only dist/devcapsule-local.pex; rebuild the "
            "public artifact with 'scripts/build-pex.sh', verify 'dist/devcapsule.pex version --json', "
            "and retry with dist/devcapsule.pex."
        )
    if not options.allow_local_source and options.source_revision is None:
        raise CliError(
            "--source-revision is required for a base build; use --allow-local-source only for an "
            "explicit dirty or unpublished development build."
        )
    if not options.allow_local_source and not info.has_public_revision:
        raise CliError(
            "The selected PEX does not embed a full public GitHub revision. Nox writes local-only "
            "dist/devcapsule-local.pex; after pushing the commit, run 'scripts/build-pex.sh' and "
            "verify 'dist/devcapsule.pex version --json'."
        )
    return info


def verify_public_github_revision(info: BuildInfo) -> None:
    """Fail unless the PEX's exact canonical commit URL is reachable."""

    request = urllib.request.Request(
        info.source_url,
        method="HEAD",
        headers={"User-Agent": "DevCapsule source verification"},
    )
    try:
        with urllib.request.urlopen(request, timeout=PUBLIC_SOURCE_TIMEOUT_SECONDS) as response:
            status = response.status
    except urllib.error.HTTPError as exc:
        raise _public_source_error(info, f"GitHub returned HTTP {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise _public_source_error(info, f"GitHub could not be reached ({exc})") from exc
    if not 200 <= status < 300:
        raise _public_source_error(info, f"GitHub returned HTTP {status}")


def _public_source_error(info: BuildInfo, detail: str) -> CliError:
    return CliError(
        f"Source revision {info.source_revision} is not publicly reachable at "
        f"{info.source_url}: {detail}. Push the commit and retry, or use "
        "--allow-local-source only for a deliberately local image."
    )


def build_base_image_spec(options: BaseImageBuildOptions) -> ImageBuildSpec:
    pex = options.pex.expanduser().resolve()
    if not pex.is_file():
        raise CliError(f"DevCapsule PEX does not exist: {pex}")
    build_info = pex_build_info(options)
    recipe = base_image_recipe(options.recipe)
    root_image = resolved_root_image(options)
    components: list[BuildComponent] = [BaseImageComponent(root_image)]
    if options.install_baseline:
        components.extend(
            [
                AptPackagesComponent(BASE_APT_PACKAGES),
                node_tooling_component(),
                temurin_tooling_component(),
                maven_tooling_component(),
            ]
        )
        components.append(
            EnvComponent(
                (
                    ("JAVA_HOME", TEMURIN_CURRENT),
                    ("MAVEN_HOME", MAVEN_CURRENT),
                    (
                        "PATH",
                        f"{MAVEN_CURRENT_BIN}:{TEMURIN_CURRENT_BIN}:{NODE_CURRENT_BIN}:${{PATH}}",
                    ),
                )
            )
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
                    ("devcapsule.pex.build-mnemonic", build_info.build_mnemonic),
                    ("devcapsule.source.repository", build_info.source_repository),
                    ("devcapsule.source.revision", build_info.source_revision),
                    ("devcapsule.source.url", build_info.source_url),
                    ("org.opencontainers.image.source", build_info.source_repository),
                    ("org.opencontainers.image.revision", build_info.source_revision),
                    ("org.opencontainers.image.version", build_info.build_mnemonic),
                )
                + recipe.labels
                + (
                    ("devcapsule.component.temurin.version", TEMURIN_VERSION),
                    ("devcapsule.component.temurin.home", TEMURIN_CURRENT),
                    ("devcapsule.component.temurin.license", "GPL-2.0-with-classpath-exception"),
                    ("devcapsule.component.maven.version", MAVEN_VERSION),
                    ("devcapsule.component.maven.home", MAVEN_CURRENT),
                    ("devcapsule.component.maven.license", "Apache-2.0"),
                    ("devcapsule.component.postgresql-client.license", "PostgreSQL"),
                )
            ),
            # The runtime entrypoint is its own PID 1: it reaps, forwards
            # signals, and supervises the foreground child (D1: pure Python;
            # tini stays installed as the recorded fallback, not in front).
            EntrypointComponent((PEX_DESTINATION, "runtime")),
            CommandComponent((RUNTIME_PLAN_PATH,)),
        ]
    )
    return ImageBuildSpec(options.image, root_image, tuple(components))


def build_base_image(
    options: BaseImageBuildOptions,
    builder: BuildxImageBuilder | None = None,
    *,
    network: str = "default",
    source_verifier: Callable[[BuildInfo], None] = verify_public_github_revision,
) -> None:
    spec = build_base_image_spec(options)
    if not options.allow_local_source:
        source_verifier(pex_build_info(options))
    (builder or BuildxImageBuilder()).build(spec, network=network)
