"""Resolve developer-owned project configuration."""

from __future__ import annotations

from pathlib import Path

import click

from devcapsule.commands.base import BaseCommand
from devcapsule.project_configuration import (
    ProjectConfigurationError,
    atomic_write,
    canonical_digest,
    checkout_path,
    load_toml,
    lock_for,
    manifest_for,
    quote_toml,
    resolved_path,
)


class ConfigCommand(BaseCommand):
    name = "config"
    help = "Inspect and resolve layered DevCapsule configuration."

    @classmethod
    def to_click_command(cls) -> click.Command:
        group = click.Group(name=cls.name, help=cls.help, no_args_is_help=True)

        @click.command("resolve")
        @click.option("--project", type=click.Path(path_type=Path), default=Path("."))
        def resolve(project: Path) -> int:
            root, manifest = manifest_for(project)
            lock_path, lock = lock_for(root, manifest)
            input_path = checkout_path(manifest)
            if not input_path.is_file():
                raise ProjectConfigurationError(
                    f"Missing developer-owned {input_path}; adopt state or create checkout authorization first."
                )
            checkout = load_toml(input_path)
            if checkout.get("devcapsule-checkout-schema-version") != 1:
                raise ProjectConfigurationError(f"{input_path} has an unsupported checkout schema version.")
            if Path(str(checkout.get("checkout", {}).get("path", ""))).resolve() != root:
                raise ProjectConfigurationError(f"{input_path} does not match observed checkout {root}.")
            image = lock.get("image", {}).get("reference")
            component = lock.get("components", {}).get("interactive-surface")
            if not image or component != "pycharm":
                raise ProjectConfigurationError("The first run slice requires a lock selecting a PyCharm image.")
            state = checkout.get("state", {}).get("adopted", {})
            host = checkout.get("host", {})
            lines = [
                "devcapsule-resolved-schema-version = 1", "", "[sources]",
                f"manifest = {quote_toml(canonical_digest(manifest))}",
                f"platform-lock = {quote_toml(canonical_digest(lock))}",
                f"checkout-input = {quote_toml(canonical_digest(checkout))}",
                'workstation-config = "absent"', "", "[runtime]",
                f"image = {quote_toml(str(image))}",
                f"component = {quote_toml(str(component))}",
                f"project-mount = {quote_toml(str(manifest['project']['mount']))}",
            ]
            if state:
                lines.extend(["", "[state.adopted]"])
                lines.extend(f"{quote_toml(str(key))} = {quote_toml(str(value))}" for key, value in sorted(state.items()))
            if host:
                lines.extend(["", "[host]"])
                for key, value in sorted(host.items()):
                    rendered = str(value).lower() if isinstance(value, bool) else quote_toml(str(value))
                    lines.append(f"{key} = {rendered}")
            output = resolved_path(manifest)
            atomic_write(output, "\n".join(lines) + "\n")
            click.echo(f"Resolved {output} from {lock_path.name}")
            return 0

        group.add_command(resolve)
        return group


COMMAND = ConfigCommand
