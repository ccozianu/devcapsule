"""Managed-image metadata and local Docker image inventory."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping

from python_on_whales import docker
from python_on_whales.exceptions import DockerException

from devcapsule.compat import CliError


MANAGED_LABEL = "devcapsule.image.managed"
METADATA_VERSION_LABEL = "devcapsule.metadata.version"
IMAGE_KIND_LABEL = "devcapsule.image.kind"
CANONICAL_NAME_LABEL = "devcapsule.image.canonical-name"
METADATA_VERSION = "1"

BASE_KIND = "base"
MATERIALIZED_KIND = "materialized"


@dataclass(frozen=True)
class LocalImageRecord:
    """One display row for a local DevCapsule-related image ID."""

    kind: str
    canonical_name: str
    aliases: tuple[str, ...]
    image_id: str
    component: str
    recipe: str
    created: str
    size: str


def managed_labels(kind: str, canonical_name: str) -> tuple[tuple[str, str], ...]:
    """Return the mandatory labels shared by every managed V1 image."""

    if kind not in {BASE_KIND, MATERIALIZED_KIND}:
        raise ValueError(f"unsupported DevCapsule image kind: {kind}")
    return (
        (MANAGED_LABEL, "true"),
        (METADATA_VERSION_LABEL, METADATA_VERSION),
        (IMAGE_KIND_LABEL, kind),
        (CANONICAL_NAME_LABEL, canonical_name),
    )


def list_local_images(*, include_legacy: bool = False) -> tuple[LocalImageRecord, ...]:
    """Read and classify DevCapsule-related images from the local Docker store."""

    try:
        images = docker.image.list(all=True)
    except DockerException as exc:
        raise CliError(f"Cannot list local Docker images: {exc}") from exc

    records: list[LocalImageRecord] = []
    for image in images:
        labels = dict(image.config.labels or {})
        managed = labels.get(MANAGED_LABEL) == "true"
        legacy = "devcapsule.configuration" in labels
        if not managed and not (include_legacy and legacy):
            continue
        records.append(
            _record(
                image_id=str(image.id),
                tags=tuple(str(tag) for tag in (image.repo_tags or ())),
                labels=labels,
                created=image.created,
                size=int(image.size),
                legacy=not managed,
            )
        )
    return tuple(sorted(records, key=lambda item: (item.kind, item.canonical_name, item.image_id)))


def inspect_local_image(reference: str) -> Any:
    """Inspect one local image and translate Docker failures consistently."""

    try:
        return docker.image.inspect(reference)
    except DockerException as exc:
        raise CliError(f"Cannot inspect local Docker image {reference!r}: {exc}") from exc


def _record(
    *,
    image_id: str,
    tags: tuple[str, ...],
    labels: Mapping[str, str],
    created: datetime | str,
    size: int,
    legacy: bool,
) -> LocalImageRecord:
    sorted_tags = tuple(sorted(tags))
    recorded_canonical = labels.get(CANONICAL_NAME_LABEL)
    canonical = recorded_canonical or (sorted_tags[0] if sorted_tags else "<untagged>")
    aliases = tuple(tag for tag in sorted_tags if tag != canonical)

    if legacy:
        kind = "legacy"
        component = labels.get("devcapsule.configuration", "-")
        recipe = "-"
    else:
        kind, component, recipe = _managed_classification(labels)

    return LocalImageRecord(
        kind=kind,
        canonical_name=canonical,
        aliases=aliases,
        image_id=_short_image_id(image_id),
        component=component,
        recipe=recipe,
        created=_created(created),
        size=_size(size),
    )


def _managed_classification(labels: Mapping[str, str]) -> tuple[str, str, str]:
    version = labels.get(METADATA_VERSION_LABEL)
    if version is not None and version != METADATA_VERSION:
        return "unsupported-metadata", labels.get("devcapsule.component.id", "-"), "-"

    kind = labels.get(IMAGE_KIND_LABEL)
    if version != METADATA_VERSION or kind not in {BASE_KIND, MATERIALIZED_KIND}:
        return "invalid-metadata", labels.get("devcapsule.component.id", "-"), "-"

    required: tuple[str, ...]
    if kind == BASE_KIND:
        required = (
            "devcapsule.base.recipe-version",
            "devcapsule.pex.sha256",
            "devcapsule.source.revision",
        )
        component = "-"
        recipe_version = labels.get("devcapsule.base.recipe-version", "-")
        recipe_name = labels.get("devcapsule.base.recipe")
        recipe = f"{recipe_name}@{recipe_version}" if recipe_name else recipe_version
        if labels.get("devcapsule.base.recipe-status") == "wip":
            recipe = f"{recipe} [WIP]"
    else:
        required = (
            "devcapsule.materialization.identity",
            "devcapsule.materialization.recipe-version",
            "devcapsule.materialization.base-identity",
            "devcapsule.component.id",
            "devcapsule.component.version",
            "devcapsule.component.sha256",
            CANONICAL_NAME_LABEL,
        )
        component = labels.get("devcapsule.component.id", "-")
        recipe = labels.get("devcapsule.materialization.recipe-version", "-")

    if any(not labels.get(name) for name in required):
        return "invalid-metadata", component, recipe
    return kind, component, recipe


def _short_image_id(value: str) -> str:
    digest = value.removeprefix("sha256:")
    return digest[:12] if digest else "-"


def _created(value: datetime | str) -> str:
    if isinstance(value, datetime):
        return value.date().isoformat()
    return str(value)[:10] if value else "-"


def _size(value: int) -> str:
    amount = float(value)
    units = ("B", "KiB", "MiB", "GiB", "TiB")
    for unit in units:
        if amount < 1024 or unit == units[-1]:
            return f"{amount:.0f} {unit}" if unit == "B" else f"{amount:.1f} {unit}"
        amount /= 1024
    raise AssertionError("unreachable")
