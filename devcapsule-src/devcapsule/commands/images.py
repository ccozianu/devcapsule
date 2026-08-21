"""Build and inspect DevCapsule-managed local images."""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any
import zipfile

import click
from python_on_whales import docker
from python_on_whales.exceptions import DockerException

from devcapsule.base_image import (
    BASE_RECIPE_NAMES,
    BASE_RECIPE_VERSION,
    DEFAULT_BASE_RECIPE,
    BaseImageBuildOptions,
    base_image_recipe,
    build_base_image,
    resolved_root_image,
)
from devcapsule.commands.base import BaseCommand
from devcapsule.compat import CliError
from devcapsule.environment_realization import optional_local_image, realize_environment
from devcapsule.image_metadata import LocalImageRecord, inspect_local_image, list_local_images
from devcapsule.materialization import ImageDetails
from devcapsule.project_configuration import (
    fresh_resolved_project,
)


class ImagesCommand(BaseCommand):
    name = "images"
    help = "List and build DevCapsule-managed images."

    @classmethod
    def to_click_command(cls) -> click.Command:
        group = click.Group(name=cls.name, help=cls.help, no_args_is_help=True)
        group.add_command(cls._list_command())
        group.add_command(cls._build_command())
        return group

    @classmethod
    def _list_command(cls) -> click.Command:
        @click.command("list")
        @click.option(
            "--include-legacy",
            is_flag=True,
            help="Include transitional images carrying only legacy DevCapsule labels.",
        )
        def list_images(include_legacy: bool) -> int:
            records = list_local_images(include_legacy=include_legacy)
            if not records:
                click.echo("No DevCapsule images found in the local Docker image store.")
                return 0
            _print_table(records)
            return 0

        return list_images

    @classmethod
    def _build_command(cls) -> click.Command:
        @click.command("build")
        @click.option("--type", "image_type", type=click.Choice(["base", "environment"]), required=True)
        @click.option("--tag", help="Local output name for a base image.")
        @click.option(
            "--recipe",
            type=click.Choice(BASE_RECIPE_NAMES),
            default=DEFAULT_BASE_RECIPE,
            show_default=True,
            help="Curated base-image recipe to build.",
        )
        @click.option("--from", "root_image", help="Override the recipe's default root image.")
        @click.option("--pex", type=click.Path(path_type=Path, exists=True, dir_okay=False))
        @click.option(
            "--source-revision",
            help="Assert the source revision already embedded in the selected PEX.",
        )
        @click.option(
            "--allow-local-source",
            is_flag=True,
            help="Allow a PEX built from dirty or unpublished local source.",
        )
        @click.option(
            "--project",
            type=click.Path(path_type=Path),
            help="Project root or descendant for an environment build; defaults to current-directory discovery.",
        )
        @click.option(
            "--base",
            "base_override",
            help="Explicit local or registry DevCapsule base override for an environment build.",
        )
        @click.option("--alias", help="Optional additional local tag for the canonical environment image.")
        @click.option(
            "--network",
            type=click.Choice(["default", "host", "none"]),
            default="default",
            show_default=True,
            help="Build network mode forwarded to Docker buildx.",
        )
        def build_image(
            image_type: str,
            tag: str,
            recipe: str,
            root_image: str | None,
            pex: Path | None,
            source_revision: str | None,
            allow_local_source: bool,
            project: Path | None,
            base_override: str | None,
            alias: str | None,
            network: str,
        ) -> int:
            if image_type == "environment":
                return _build_environment(
                    project=project,
                    base_override=base_override,
                    alias=alias,
                )
            if tag is None:
                raise CliError("--tag is required for 'images build --type base'.")
            if source_revision is None and not allow_local_source:
                raise CliError(
                    "--source-revision is required for a base build; use --allow-local-source "
                    "only for an explicit dirty or unpublished development build."
                )
            if project is not None or base_override is not None or alias is not None:
                raise CliError("--project, --base, and --alias apply only to environment builds.")
            selected_pex = pex.expanduser().resolve() if pex is not None else _running_pex()
            selected_recipe = base_image_recipe(recipe)
            options = BaseImageBuildOptions(
                pex=selected_pex,
                image=tag,
                root_image=root_image,
                source_revision=source_revision,
                allow_local_source=allow_local_source,
                recipe=recipe,
            )
            if selected_recipe.status == "wip":
                click.secho(
                    f"WARNING: base recipe {recipe!r} is WIP and still requires specialized "
                    "NVIDIA GPU E2E validation before V1 release.",
                    fg="yellow",
                    err=True,
                )
            build_base_image(
                options,
                network=network,
            )
            image = inspect_local_image(tag)
            labels = dict(image.config.labels or {})
            click.echo(f"Built DevCapsule base image: {tag}")
            click.echo(f"Image ID: {image.id}")
            click.echo(f"Root image: {resolved_root_image(options)}")
            recipe_name = labels.get("devcapsule.base.recipe", recipe)
            recipe_version = labels.get("devcapsule.base.recipe-version", BASE_RECIPE_VERSION)
            recipe_status = labels.get("devcapsule.base.recipe-status", selected_recipe.status)
            click.echo(f"Base recipe: {recipe_name}@{recipe_version} ({recipe_status.upper()})")
            click.echo(
                f"DevCapsule build: {labels.get('devcapsule.pex.build-mnemonic', 'unknown')}"
            )
            click.echo(f"PEX SHA-256: {labels.get('devcapsule.pex.sha256', 'unknown')}")
            click.echo(f"Source revision: {labels.get('devcapsule.source.revision', 'unknown')}")
            click.echo(f"Source URL: {labels.get('devcapsule.source.url', 'unknown')}")
            verification = (
                "bypassed for explicit local source" if allow_local_source else "public GitHub commit reachable"
            )
            click.echo(f"Source verification: {verification}")
            click.echo(f"Build network: {network}")
            return 0

        return build_image

    def run(self) -> Any:
        raise NotImplementedError("Images is a Click command group.")


def _running_pex() -> Path:
    candidate = Path(sys.argv[0]).expanduser().resolve()
    if candidate.is_file() and zipfile.is_zipfile(candidate):
        return candidate
    raise CliError("--pex is required when DevCapsule is not running from a PEX artifact.")


def _print_table(records: tuple[LocalImageRecord, ...]) -> None:
    headers = ("KIND", "CANONICAL", "ALIASES", "IMAGE-ID", "COMPONENT", "RECIPE", "CREATED", "SIZE")
    rows = [
        (
            record.kind,
            record.canonical_name,
            ",".join(record.aliases) or "-",
            record.image_id,
            record.component,
            record.recipe,
            record.created,
            record.size,
        )
        for record in records
    ]
    widths = [max(len(header), *(len(row[index]) for row in rows)) for index, header in enumerate(headers)]
    click.echo("  ".join(header.ljust(widths[index]) for index, header in enumerate(headers)))
    for row in rows:
        click.echo("  ".join(value.ljust(widths[index]) for index, value in enumerate(row)))


COMMAND = ImagesCommand


def _build_environment(*, project: Path | None, base_override: str | None, alias: str | None) -> int:
    selected = fresh_resolved_project(project or Path("."))
    realized = realize_environment(selected, base_override=base_override)
    locked = realized.locked
    canonical_details = realized.image
    if alias is not None:
        _add_alias(canonical_details, alias)

    labels = canonical_details.labels
    action = "Built" if realized.created else "Reused"
    click.echo(f"{action} DevCapsule environment image: {canonical_details.reference}")
    click.echo(f"Image ID: {canonical_details.identity}")
    click.echo(f"Base reference: {realized.base_reference}")
    click.echo(f"Base identity: {realized.base.identity}")
    click.echo(f"Component: {locked.component_id}@{locked.artifact.version} ({locked.artifact.variant})")
    click.echo(f"Component SHA-256: {locked.artifact.sha256.lower()}")
    click.echo(f"Formation identity: {labels['devcapsule.materialization.identity']}")
    click.echo(
        f"Artifact cache: {realized.cache / 'artifacts' / 'sha256' / locked.artifact.sha256.lower()}"
    )
    if realized.explicit_base_override:
        click.echo("Base selection: explicit developer override", err=True)
    if alias is not None:
        click.echo(f"Alias: {alias}")
    click.echo("No container was launched.")
    return 0


def _add_alias(canonical: ImageDetails, alias: str) -> None:
    existing = optional_local_image(alias)
    if existing is not None:
        if existing.identity != canonical.identity:
            raise CliError(
                f"Alias {alias!r} already identifies {existing.identity}; remove or retag it before retrying."
            )
        return
    try:
        docker.image.tag(canonical.reference, alias)
    except DockerException as exc:
        raise CliError(f"Cannot add image alias {alias!r}: {exc}") from exc
