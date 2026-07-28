"""Launch the first capability-first resolved project."""

from __future__ import annotations

from pathlib import Path

import click

from devcapsule.commands.base import BaseCommand
from devcapsule.configurations.pycharm import DockerMode, PycharmRunOptions, run_pycharm
from devcapsule.project_configuration import (
    ProjectConfigurationError,
    canonical_digest,
    checkout_path,
    load_toml,
    lock_for,
    manifest_for,
    resolved_path,
)


class RunCommand(BaseCommand):
    project: Path
    force: bool
    docker_daemon: str | None
    development_sudo: bool | None
    container_name: str | None

    name = "run"
    help = "Run the current project from its platform lock and developer-owned resolution."
    params = [
        click.Option(["--project"], type=click.Path(path_type=Path), default=Path(".")),
        click.Option(["--force"], is_flag=True, help="Use stale generated resolution once, with a warning."),
        click.Option(["--docker-daemon"], type=click.Choice(["none", "host-socket"])),
        click.Option(["--development-sudo"], is_flag=True, default=None),
        click.Option(["--name", "container_name"]),
    ]

    def run(self) -> int:
        root, manifest = manifest_for(self.project)
        _lock_path, lock = lock_for(root, manifest)
        input_path = checkout_path(manifest)
        output_path = resolved_path(manifest)
        if not input_path.is_file() or not output_path.is_file():
            raise ProjectConfigurationError("Local resolution is missing; run 'devcapsule config resolve'.")
        checkout = load_toml(input_path)
        resolved = load_toml(output_path)
        expected = {
            "manifest": canonical_digest(manifest),
            "platform-lock": canonical_digest(lock),
            "checkout-input": canonical_digest(checkout),
        }
        actual = resolved.get("sources", {})
        stale = [name for name, digest in expected.items() if actual.get(name) != digest]
        if stale and not self.force:
            raise ProjectConfigurationError(
                f"Local resolution is stale ({', '.join(stale)}); run 'devcapsule config resolve'."
            )
        if stale:
            click.echo(f"WARNING: using stale generated resolution once ({', '.join(stale)}).", err=True)
        runtime = resolved.get("runtime", {})
        if runtime.get("component") != "pycharm" or not runtime.get("image"):
            raise ProjectConfigurationError("The first run slice supports only resolved PyCharm images.")
        state = resolved.get("state", {}).get("adopted", {})
        host = resolved.get("host", {})
        docker_daemon = self.docker_daemon or host.get("docker-daemon", "none")
        development_sudo = self.development_sudo
        if development_sudo is None:
            development_sudo = bool(host.get("development-sudo", False))
        if host.get("network", "bridge") != "bridge":
            raise ProjectConfigurationError(
                "The first normal-run slice supports only bridge networking; use run-image for an explicit exception."
            )
        return run_pycharm(
            PycharmRunOptions(
                project=root,
                project_mount=str(runtime["project-mount"]),
                image=str(runtime["image"]),
                name=self.container_name,
                persistent_home=Path(state["home"]) if "home" in state else None,
                ide_config=Path(state["pycharm/config"]) if "pycharm/config" in state else None,
                plugins=Path(state["pycharm/plugins"]) if "pycharm/plugins" in state else None,
                ide_system=Path(state["pycharm/system"]) if "pycharm/system" in state else None,
                ide_log=Path(state["pycharm/log"]) if "pycharm/log" in state else None,
                tool_cache=Path(state["pycharm/cache"]) if "pycharm/cache" in state else None,
                docker_mode=DockerMode.host if docker_daemon == "host-socket" else DockerMode.none,
                enable_sudo=bool(development_sudo),
                extra_docker_args=["--pull=never"],
                project_state=None,
            )
        )


COMMAND = RunCommand
