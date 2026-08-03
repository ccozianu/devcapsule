"""Shared host-side realization of one resolved project environment."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from python_on_whales import docker
from python_on_whales.exceptions import DockerException

from devcapsule.compat import CliError
from devcapsule.image_build import BuildxImageBuilder, ImageBuildSpec
from devcapsule.image_metadata import inspect_local_image
from devcapsule.materialization import (
    ImageDetails,
    LockedEnvironment,
    cache_root,
    ensure_materialized_pycharm,
    parse_locked_environment,
    validate_base_image,
)
from devcapsule.project_configuration import (
    ResolvedProject,
    authorized_base_reference,
)


@dataclass(frozen=True)
class RealizedEnvironment:
    """Verified canonical image and formation inputs selected for one run."""

    image: ImageDetails
    base: ImageDetails
    base_reference: str
    locked: LockedEnvironment
    cache: Path
    created: bool
    explicit_base_override: bool


ImageLookup = Callable[[str], ImageDetails | None]
ImageRequirement = Callable[[str], ImageDetails]
ImageBuild = Callable[[ImageBuildSpec], None]
Materialize = Callable[..., tuple[str, bool]]


def realize_environment(
    selected: ResolvedProject,
    *,
    base_override: str | None = None,
    root: Path | None = None,
    obtain_image: ImageRequirement | None = None,
    inspect_image: ImageLookup | None = None,
    require_image: ImageRequirement | None = None,
    build: ImageBuild | None = None,
    materialize: Materialize | None = None,
) -> RealizedEnvironment:
    """Strictly reuse or materialize the canonical image for one resolved project."""

    locked = parse_locked_environment(selected.lock)
    runtime = selected.resolution.get("runtime", {})
    if not isinstance(runtime, dict) or runtime.get("component") != locked.component_id:
        component = runtime.get("component") if isinstance(runtime, dict) else None
        raise CliError(
            f"Fresh resolution selects component {component!r}, "
            f"but the lock formation selects {locked.component_id!r}."
        )

    explicit_override = base_override is not None
    base_reference = base_override or locked.base_reference
    expected_base_identity = None if explicit_override else locked.base_identity
    if not explicit_override:
        authorized_base_reference(selected.lock, selected.checkout)

    obtain = obtain_image or ensure_local_image
    inspect = inspect_image or optional_local_image
    require = require_image or required_local_image
    base = obtain(base_reference)
    validate_base_image(
        base,
        platform=locked.platform,
        expected_identity=expected_base_identity,
    )

    selected_cache = (root or cache_root()).expanduser().resolve()
    if build is None:
        builder = BuildxImageBuilder(temporary_root=selected_cache / "build-contexts")
        build = lambda spec: builder.build(spec, network="none")
    materialize_environment = materialize or ensure_materialized_pycharm
    canonical, created = materialize_environment(
        base_reference=base_reference,
        base_identity=base.identity,
        platform=locked.platform,
        artifact=locked.artifact,
        cache_root=selected_cache,
        inspect_image=inspect,
        build=build,
        recipe_id=locked.recipe_id,
        recipe_version=locked.recipe_version,
    )
    image = require(canonical)
    return RealizedEnvironment(
        image=image,
        base=base,
        base_reference=base_reference,
        locked=locked,
        cache=selected_cache,
        created=created,
        explicit_base_override=explicit_override,
    )


def ensure_local_image(reference: str) -> ImageDetails:
    try:
        if not docker.image.exists(reference):
            docker.image.pull(reference)
    except DockerException as exc:
        raise CliError(f"Cannot obtain Docker image {reference!r}: {exc}") from exc
    return required_local_image(reference)


def required_local_image(reference: str) -> ImageDetails:
    image = inspect_local_image(reference)
    return image_details(reference, image)


def optional_local_image(reference: str) -> ImageDetails | None:
    try:
        if not docker.image.exists(reference):
            return None
    except DockerException as exc:
        raise CliError(f"Cannot query local Docker image {reference!r}: {exc}") from exc
    return required_local_image(reference)


def image_details(reference: str, image: Any) -> ImageDetails:
    return ImageDetails(
        reference=reference,
        identity=str(image.id),
        labels=dict(image.config.labels or {}),
        operating_system=str(image.os),
        architecture=str(image.architecture),
    )
