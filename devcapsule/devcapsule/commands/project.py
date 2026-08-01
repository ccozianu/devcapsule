"""Project and checkout command subtree."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import click

from devcapsule.commands.base import BaseCommand
from devcapsule.configurations.pycharm import DockerMode, PycharmRunOptions, run_pycharm
from devcapsule.project import sanitize_name
from devcapsule.project_configuration import (
    ProjectConfigurationError,
    atomic_write,
    canonical_digest,
    checkout_record_paths,
    config_root,
    discover_project,
    find_checkout_record,
    load_toml,
    lock_for,
    manifest_for,
    named_checkout_record_paths,
    platform_alias,
    quote_toml,
    registered_checkouts,
    render_checkout,
)


KNOWN_SLOTS = {"home", "pycharm/config", "pycharm/plugins", "pycharm/system", "pycharm/log", "pycharm/cache"}


@dataclass(frozen=True)
class ProjectCommandContext:
    selected_path: Path | None

    def start_path(self) -> Path:
        return self.selected_path or Path(".")

    def target_path(self) -> Path:
        return self.start_path().expanduser().resolve()


class ProjectCommand(BaseCommand):
    name = "project"
    help = "Initialize, list, configure, and run DevCapsule project checkouts."

    @classmethod
    def to_click_command(cls) -> click.Command:
        @click.group(name=cls.name, help=cls.help, no_args_is_help=True)
        @click.option(
            "--path",
            "selected_path",
            type=click.Path(path_type=Path),
            help="Project root or descendant; defaults to discovery from the current directory.",
        )
        @click.pass_context
        def group(ctx: click.Context, selected_path: Path | None) -> None:
            ctx.obj = ProjectCommandContext(selected_path)

        group.add_command(_list_command())
        group.add_command(_init_command())
        group.add_command(_checkout_command())
        group.add_command(_lock_command())
        group.add_command(_config_command())
        group.add_command(_state_command())
        group.add_command(_run_command())
        group.add_command(_run_image_command())
        return group

    def run(self) -> Any:
        raise NotImplementedError("Project is a Click command group.")


def _list_command() -> click.Command:
    @click.command("list", help="List developer-owned checkout records from the XDG registry.")
    @click.pass_obj
    def list_projects(_context: ProjectCommandContext) -> int:
        records = registered_checkouts()
        if not records:
            click.echo(f"No registered DevCapsule project checkouts found in {config_root() / 'projects'}.")
            return 0
        headers = ("PROJECT", "CHECKOUT", "PATH", "STATUS")
        rows = [
            (
                f"{record.project_creator}/{record.project_slug}",
                record.checkout_name,
                str(record.checkout_path),
                record.status,
            )
            for record in records
        ]
        widths = [max(len(header), *(len(row[index]) for row in rows)) for index, header in enumerate(headers)]
        click.echo("  ".join(header.ljust(widths[index]) for index, header in enumerate(headers)))
        for row in rows:
            click.echo("  ".join(value.ljust(widths[index]) for index, value in enumerate(row)))
        return 0

    return list_projects


def _init_command() -> click.Command:
    @click.command("init", help="Create a new .devcapsule project declaration without overwriting.")
    @click.option("--need", multiple=True, required=True)
    @click.option("--name", "project_name")
    @click.option("--slug")
    @click.option("--creator", required=True)
    @click.option("--project-mount", default="/workspace/project", show_default=True)
    @click.pass_obj
    def init_project(
        context: ProjectCommandContext,
        need: tuple[str, ...],
        project_name: str | None,
        slug: str | None,
        creator: str,
        project_mount: str,
    ) -> int:
        project = context.target_path()
        target = project / ".devcapsule"
        if target.exists():
            raise ProjectConfigurationError(
                f"{project} is already initialized; inspect {target / 'devcapsule.toml'} instead."
            )
        if not project.is_dir():
            raise ProjectConfigurationError(f"Project directory does not exist: {project}")
        normalized_creator = creator if ":" in creator else f"mailto:{creator}"
        name = project_name or project.name
        project_slug = slug or sanitize_name(project.name).lower()
        needs = sorted(set(need))
        content = (
            "devcapsule-schema-version = 1\n\n"
            "[capabilities]\n"
            f"need = [{', '.join(quote_toml(item) for item in needs)}]\n\n"
            "[project]\n"
            f"name = {quote_toml(name)}\n"
            f"slug = {quote_toml(project_slug)}\n"
            f"creator = {quote_toml(normalized_creator)}\n"
            f"mount = {quote_toml(project_mount)}\n"
        )
        target.mkdir(mode=0o755)
        (target / "devcapsule.toml").write_text(content, encoding="utf-8")
        click.echo(f"Created {target / 'devcapsule.toml'}")
        click.echo("Next: generate or add the platform lock, then run 'devcapsule project config resolve'.")
        return 0

    return init_project


def _checkout_command() -> click.Command:
    group = click.Group(name="checkout", help="Register additional local checkouts.", no_args_is_help=True)

    @click.command("register")
    @click.argument("name")
    @click.pass_obj
    def register(context: ProjectCommandContext, name: str) -> int:
        root, manifest = manifest_for(context.start_path())
        selected_input = find_checkout_record(manifest, root)
        if selected_input is not None:
            raise ProjectConfigurationError(f"Checkout is already registered in {selected_input}.")
        input_path, output_path = named_checkout_record_paths(manifest, name)
        if input_path.exists() or output_path.exists():
            raise ProjectConfigurationError(f"Checkout name {name!r} is already in use under {input_path.parent}.")
        atomic_write(input_path, render_checkout(manifest, root, {}, {}))
        click.echo(f"Registered checkout {name!r}: {input_path}")
        return 0

    group.add_command(register)
    return group


def _lock_command() -> click.Command:
    @click.command("lock", help="Generate the current-platform lock for the initial curated PyCharm slice.")
    @click.option(
        "--image",
        required=True,
        help="Existing local PyCharm image reference to pin for this dogfood slice.",
    )
    @click.pass_obj
    def lock_project(context: ProjectCommandContext, image: str) -> int:
        root, manifest = manifest_for(context.start_path())
        alias = platform_alias()
        output = root / ".devcapsule" / f"devcapsule.{alias}.lock"
        content = (
            "devcapsule-lock-format-version = 1\n"
            'resolution-matrix-version = "dogfood-v1"\n'
            f"manifest-digest = {quote_toml(canonical_digest(manifest))}\n"
            f"platform = {quote_toml(alias)}\n\n"
            "[image]\n"
            f"reference = {quote_toml(image)}\n\n"
            "[components]\n"
            'interactive-surface = "pycharm"\n'
        )
        atomic_write(output, content, mode=0o644)
        click.echo(f"Generated {output}")
        click.echo("This dogfood lock pins a local image tag; immutable formation locks remain follow-up work.")
        return 0

    return lock_project


def _config_command() -> click.Command:
    group = click.Group(name="config", help="Inspect and resolve layered project configuration.", no_args_is_help=True)

    @click.command("resolve")
    @click.pass_obj
    def resolve(context: ProjectCommandContext) -> int:
        root, manifest = manifest_for(context.start_path())
        lock_path, lock = lock_for(root, manifest)
        input_path, output = checkout_record_paths(manifest, root)
        if not input_path.is_file():
            atomic_write(input_path, render_checkout(manifest, root, {}, {}))
            click.echo(f"Registered checkout: {input_path}")
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
            "devcapsule-resolved-schema-version = 1",
            "",
            "[sources]",
            f"manifest = {quote_toml(canonical_digest(manifest))}",
            f"platform-lock = {quote_toml(canonical_digest(lock))}",
            f"checkout-input = {quote_toml(canonical_digest(checkout))}",
            'workstation-config = "absent"',
            "",
            "[runtime]",
            f"image = {quote_toml(str(image))}",
            f"component = {quote_toml(str(component))}",
            f"project-mount = {quote_toml(str(manifest['project']['mount']))}",
        ]
        if state:
            lines.extend(["", "[state.adopted]"])
            lines.extend(
                f"{quote_toml(str(key))} = {quote_toml(str(value))}" for key, value in sorted(state.items())
            )
        if host:
            lines.extend(["", "[host]"])
            for key, value in sorted(host.items()):
                rendered = str(value).lower() if isinstance(value, bool) else quote_toml(str(value))
                lines.append(f"{key} = {rendered}")
        atomic_write(output, "\n".join(lines) + "\n")
        click.echo(f"Resolved {output} from {lock_path.name}")
        return 0

    group.add_command(resolve)
    return group


def _state_command() -> click.Command:
    group = click.Group(name="state", help="Inspect and adopt checkout-scoped persistent state.", no_args_is_help=True)

    @click.command("adopt")
    @click.argument("slot", type=click.Choice(sorted(KNOWN_SLOTS)))
    @click.option("--from", "source", type=click.Path(path_type=Path), required=True)
    @click.pass_obj
    def adopt(context: ProjectCommandContext, slot: str, source: Path) -> int:
        root, manifest = manifest_for(context.start_path())
        source = source.expanduser().resolve()
        if not source.is_dir():
            raise ProjectConfigurationError(f"State source is not a directory: {source}")
        path, _resolved = checkout_record_paths(manifest, root)
        checkout: dict[str, Any] = load_toml(path) if path.is_file() else {}
        recorded_path = checkout.get("checkout", {}).get("path")
        if recorded_path and Path(recorded_path).resolve() != root:
            raise ProjectConfigurationError(f"{path} belongs to another checkout: {recorded_path}")
        state = dict(checkout.get("state", {}).get("adopted", {}))
        host = dict(checkout.get("host", {}))
        state[slot] = str(source)
        atomic_write(path, render_checkout(manifest, root, state, host))
        click.echo(f"Adopted {slot}: {source}")
        click.echo("Run 'devcapsule project config resolve' before launch.")
        return 0

    group.add_command(adopt)
    return group


def _run_command() -> click.Command:
    @click.command("run", help="Run the project from its platform lock and developer-owned resolution.")
    @click.option("--force", is_flag=True, help="Use stale generated resolution once, with a warning.")
    @click.option("--docker-daemon", type=click.Choice(["none", "host-socket"]))
    @click.option("--development-sudo", is_flag=True, default=None)
    @click.option("--name", "container_name")
    @click.pass_obj
    def run_project(
        context: ProjectCommandContext,
        force: bool,
        docker_daemon: str | None,
        development_sudo: bool | None,
        container_name: str | None,
    ) -> int:
        root, manifest = manifest_for(context.start_path())
        _lock_path, lock = lock_for(root, manifest)
        input_path, output_path = checkout_record_paths(manifest, root)
        if not input_path.is_file() or not output_path.is_file():
            raise ProjectConfigurationError(
                "Local resolution is missing; run 'devcapsule project config resolve'."
            )
        checkout = load_toml(input_path)
        resolved = load_toml(output_path)
        expected = {
            "manifest": canonical_digest(manifest),
            "platform-lock": canonical_digest(lock),
            "checkout-input": canonical_digest(checkout),
        }
        actual = resolved.get("sources", {})
        stale = [name for name, digest in expected.items() if actual.get(name) != digest]
        if stale and not force:
            raise ProjectConfigurationError(
                f"Local resolution is stale ({', '.join(stale)}); run 'devcapsule project config resolve'."
            )
        if stale:
            click.echo(f"WARNING: using stale generated resolution once ({', '.join(stale)}).", err=True)
        runtime = resolved.get("runtime", {})
        if runtime.get("component") != "pycharm" or not runtime.get("image"):
            raise ProjectConfigurationError("The first run slice supports only resolved PyCharm images.")
        state = resolved.get("state", {}).get("adopted", {})
        host = resolved.get("host", {})
        selected_docker_daemon = docker_daemon or host.get("docker-daemon", "none")
        selected_sudo = development_sudo
        if selected_sudo is None:
            selected_sudo = bool(host.get("development-sudo", False))
        if host.get("network", "bridge") != "bridge":
            raise ProjectConfigurationError(
                "The normal run path supports only bridge networking; use 'devcapsule project run-image' "
                "for an explicit exception."
            )
        return run_pycharm(
            PycharmRunOptions(
                project=root,
                project_mount=str(runtime["project-mount"]),
                image=str(runtime["image"]),
                name=container_name,
                persistent_home=Path(state["home"]) if "home" in state else None,
                ide_config=Path(state["pycharm/config"]) if "pycharm/config" in state else None,
                plugins=Path(state["pycharm/plugins"]) if "pycharm/plugins" in state else None,
                ide_system=Path(state["pycharm/system"]) if "pycharm/system" in state else None,
                ide_log=Path(state["pycharm/log"]) if "pycharm/log" in state else None,
                tool_cache=Path(state["pycharm/cache"]) if "pycharm/cache" in state else None,
                docker_mode=DockerMode.host if selected_docker_daemon == "host-socket" else DockerMode.none,
                enable_sudo=bool(selected_sudo),
                extra_docker_args=["--pull=never"],
                project_state=None,
            )
        )

    return run_project


def _run_image_command() -> click.Command:
    @click.command(
        "run-image",
        help="Run a local PyCharm-compatible image without project lock resolution.",
    )
    @click.argument("image")
    @click.option("--project-mount", help="Absolute in-container project path.")
    @click.option("--home", type=click.Path(path_type=Path))
    @click.option("--global-settings", type=click.Path(path_type=Path))
    @click.option("--plugins", type=click.Path(path_type=Path))
    @click.option("--project-state", type=click.Path(path_type=Path))
    @click.option("--docker-daemon", type=click.Choice(["none", "host-socket"]), default="none", show_default=True)
    @click.option("--development-sudo", is_flag=True)
    @click.option("--name", "container_name")
    @click.pass_obj
    def run_image(
        context: ProjectCommandContext,
        image: str,
        project_mount: str | None,
        home: Path | None,
        global_settings: Path | None,
        plugins: Path | None,
        project_state: Path | None,
        docker_daemon: str,
        development_sudo: bool,
        container_name: str | None,
    ) -> int:
        candidate = context.start_path()
        try:
            project = discover_project(candidate)
        except ProjectConfigurationError:
            project = candidate.expanduser().resolve()
        if not project.is_dir():
            raise ProjectConfigurationError(f"Project directory does not exist: {project}")
        docker_mode = DockerMode.host if docker_daemon == "host-socket" else DockerMode.none
        return run_pycharm(
            PycharmRunOptions(
                project=project,
                project_mount=project_mount,
                image=image,
                name=container_name,
                persistent_home=home,
                global_settings=global_settings,
                project_state=project_state,
                plugins=plugins,
                docker_mode=docker_mode,
                enable_sudo=development_sudo,
                extra_docker_args=["--pull=never"],
            )
        )

    return run_image


COMMAND = ProjectCommand
