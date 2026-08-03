"""Project and checkout command subtree."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any

import click
import readchar

from devcapsule.commands.base import BaseCommand
from devcapsule.components.pycharm import logical_state_slots as pycharm_state_slots
from devcapsule.configurations.pycharm import DockerMode, PycharmRunOptions, run_pycharm
from devcapsule.project import sanitize_name
from devcapsule.project_configuration import (
    AuthorizationDeclaration,
    ProjectConfigurationError,
    authorization_declarations,
    atomic_write,
    canonical_digest,
    checkout_record_paths,
    configuration_binding_declarations,
    configuration_value_declarations,
    config_root,
    discover_project,
    find_checkout_record,
    load_toml,
    lock_for,
    manifest_for,
    named_checkout_record_paths,
    normalize_configuration_value,
    normalize_authorization_value,
    platform_alias,
    quote_toml,
    registered_checkouts,
    render_checkout,
    render_authorization_value,
    render_toml_scalar,
    resolve_configuration_bindings,
    resolve_configuration_values,
    resolved_checkout_authorizations,
)


KNOWN_SLOTS = {"home", *pycharm_state_slots()}


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
        has_formation = isinstance(lock.get("base"), dict) and isinstance(lock.get("materialization"), dict)
        if component != "pycharm" or (not image and not has_formation):
            raise ProjectConfigurationError(
                "The V1 slice requires a lock selecting either a completed PyCharm image or PyCharm formation inputs."
            )
        state = checkout.get("state", {}).get("adopted", {})
        host = checkout.get("host", {})
        values, runtime_effects = resolve_configuration_values(manifest, checkout)
        bindings = resolve_configuration_bindings(lock, checkout)
        overlap = sorted(set(state) & set(bindings))
        if overlap:
            raise ProjectConfigurationError(
                "State resources cannot be both adopted and configuration-bound: "
                + ", ".join(overlap)
                + "."
            )
        authorizations = resolved_checkout_authorizations(manifest, lock, checkout)
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
            f"component = {quote_toml(str(component))}",
            f"project-mount = {quote_toml(str(manifest['project']['mount']))}",
        ]
        lines.extend(
            f"{key} = {render_toml_scalar(value)}" for key, value in sorted(runtime_effects.items())
        )
        if image:
            lines.append(f"image = {quote_toml(str(image))}")
        if values:
            lines.extend(["", "[configuration.values]"])
            lines.extend(
                f"{quote_toml(key)} = {render_toml_scalar(value)}"
                for key, value in sorted(values.items())
            )
        if state:
            lines.extend(["", "[state.adopted]"])
            lines.extend(
                f"{quote_toml(str(key))} = {quote_toml(str(value))}" for key, value in sorted(state.items())
            )
        if bindings:
            lines.extend(["", "[state.bindings]"])
            lines.extend(
                f"{quote_toml(key)} = {quote_toml(value)}"
                for key, value in sorted(bindings.items())
            )
        if host:
            lines.extend(["", "[host]"])
            for key, value in sorted(host.items()):
                rendered = str(value).lower() if isinstance(value, bool) else quote_toml(str(value))
                lines.append(f"{key} = {rendered}")
        runtime_authorizations = {
            key: value for key, value in authorizations.items() if key != "base-image"
        }
        if runtime_authorizations:
            lines.extend(["", "[authorization]"])
            lines.extend(
                f"{key} = {render_toml_scalar(value)}"
                for key, value in sorted(runtime_authorizations.items())
            )
        authorized_base = authorizations.get("base-image")
        if authorized_base is not None:
            if not isinstance(authorized_base, str):
                raise ProjectConfigurationError("Resolved base-image authorization must be a string.")
            lines.extend(
                [
                    "",
                    "[authorization.base-image]",
                    f"reference = {quote_toml(authorized_base)}",
                    f"lock-digest = {quote_toml(canonical_digest(lock))}",
                ]
            )
        atomic_write(output, "\n".join(lines) + "\n")
        click.echo(f"Resolved {output} from {lock_path.name}")
        return 0

    group.add_command(_config_list_command())
    group.add_command(resolve)
    group.add_command(_config_set_command())
    group.add_command(_config_bind_command())
    group.add_command(_config_authorize_command())
    return group


@dataclass(frozen=True)
class ConfigurationListRow:
    kind: str
    name: str
    status: str
    value: str


def _config_list_command() -> click.Command:
    @click.command("list", help="Show configured values, bindings, authorizations, and resolution readiness.")
    @click.pass_obj
    def list_configuration(context: ProjectCommandContext) -> int:
        root, manifest = manifest_for(context.start_path())
        _lock_path, lock = lock_for(root, manifest)
        input_path, resolution_path = checkout_record_paths(manifest, root)
        if not input_path.is_file():
            atomic_write(input_path, render_checkout(manifest, root, {}, {}))
            click.echo(f"Initialized checkout input: {input_path}")
        if not resolution_path.is_file():
            atomic_write(
                resolution_path,
                'devcapsule-resolved-schema-version = 1\nstatus = "unresolved"\n',
            )
            click.echo(f"Initialized resolution placeholder: {resolution_path}")
        checkout = load_toml(input_path)

        identity = manifest["project"]
        click.echo(f"Project: {identity['creator']}/{identity['slug']}")
        click.echo(f"Checkout: {root}")
        checkout_name = (
            "default"
            if input_path.name == "devcapsule.checkout.toml"
            else input_path.name.removesuffix(".checkout.toml")
        )
        click.echo(f"Checkout name: {checkout_name}")
        click.echo(f"Checkout input: {input_path}")
        click.echo(f"Generated plan: {resolution_path}")

        rows = [
            *_configuration_value_rows(manifest, checkout),
            *_configuration_binding_rows(lock, checkout),
            *_configuration_authorization_rows(manifest, lock, checkout),
            _configuration_resolution_row(
                manifest,
                lock,
                checkout,
                resolution_path,
            ),
        ]
        _print_configuration_rows(rows)
        return 0

    return list_configuration


def _configuration_value_rows(
    manifest: dict[str, Any], checkout: dict[str, Any]
) -> list[ConfigurationListRow]:
    declarations = configuration_value_declarations(manifest)
    configuration = checkout.get("configuration", {})
    if not isinstance(configuration, dict):
        return [ConfigurationListRow("value", "*", "invalid", "configuration is not a table")]
    raw_values = configuration.get("values", {})
    if not isinstance(raw_values, dict):
        return [ConfigurationListRow("value", "*", "invalid", "values is not a table")]

    rows: list[ConfigurationListRow] = []
    for name, declaration in sorted(declarations.items()):
        if name not in raw_values:
            status = "missing-required" if declaration.get("required", False) else "unset-optional"
            rows.append(ConfigurationListRow("value", name, status, "-"))
            continue
        try:
            normalized = normalize_configuration_value(manifest, name, raw_values[name])
        except ProjectConfigurationError as exc:
            rows.append(ConfigurationListRow("value", name, "invalid", str(exc)))
        else:
            rows.append(
                ConfigurationListRow("value", name, "configured", render_toml_scalar(normalized))
            )
    for name, value in sorted(raw_values.items(), key=lambda item: str(item[0])):
        if name not in declarations:
            rows.append(ConfigurationListRow("value", str(name), "undeclared", repr(value)))
    return rows


def _configuration_binding_rows(
    lock: dict[str, Any], checkout: dict[str, Any]
) -> list[ConfigurationListRow]:
    declarations = configuration_binding_declarations(lock)
    configuration = checkout.get("configuration", {})
    if not isinstance(configuration, dict):
        raw_bindings: object = {}
    else:
        bindings = configuration.get("bindings", {})
        raw_bindings = bindings.get("host-directory", {}) if isinstance(bindings, dict) else bindings
    if not isinstance(raw_bindings, dict):
        return [ConfigurationListRow("binding", "*", "invalid", "host-directory is not a table")]
    state = checkout.get("state", {})
    adopted = state.get("adopted", {}) if isinstance(state, dict) else {}
    if not isinstance(adopted, dict):
        adopted = {}

    rows: list[ConfigurationListRow] = []
    for name in sorted(declarations):
        bound = raw_bindings.get(name)
        legacy = adopted.get(name)
        if bound is not None and legacy is not None:
            rows.append(ConfigurationListRow("binding", name, "conflict", "bound and adopted"))
        elif bound is not None:
            path = Path(str(bound)).expanduser().resolve()
            status = "bound" if isinstance(bound, str) and path.is_dir() else "invalid"
            rows.append(ConfigurationListRow("binding", name, status, f"host-directory: {path}"))
        elif legacy is not None:
            path = Path(str(legacy)).expanduser().resolve()
            status = "adopted-legacy" if isinstance(legacy, str) and path.is_dir() else "invalid"
            rows.append(ConfigurationListRow("binding", name, status, str(path)))
        else:
            rows.append(ConfigurationListRow("binding", name, "managed-default", "managed directory"))
    for name, value in sorted(raw_bindings.items(), key=lambda item: str(item[0])):
        if name not in declarations:
            rows.append(ConfigurationListRow("binding", str(name), "undeclared", str(value)))
    return rows


def _configuration_authorization_rows(
    manifest: dict[str, Any], lock: dict[str, Any], checkout: dict[str, Any]
) -> list[ConfigurationListRow]:
    declarations = authorization_declarations(manifest, lock)
    authorization = checkout.get("authorization", {})
    if not isinstance(authorization, dict):
        return [ConfigurationListRow("authorization", "*", "invalid", "authorization is not a table")]

    rows: list[ConfigurationListRow] = []
    for name, declaration in sorted(declarations.items()):
        recommended = render_authorization_value(declaration.recommended_value)
        record = authorization.get(name)
        if record is None:
            status = "missing-required" if name == "base-image" else "missing-recommended"
            rows.append(ConfigurationListRow("authorization", name, status, recommended))
            continue
        if not isinstance(record, dict):
            rows.append(ConfigurationListRow("authorization", name, "invalid", recommended))
            continue
        if name == "base-image":
            raw_value = record.get("reference")
            digest = record.get("lock-digest")
        else:
            raw_value = record.get("value")
            digest = record.get("recommendation-digest")
        try:
            normalize_authorization_value(declaration, raw_value)
        except ProjectConfigurationError:
            status = "invalid"
        else:
            status = "authorized" if digest == declaration.recommendation_digest else "stale"
        rows.append(ConfigurationListRow("authorization", name, status, recommended))
    for name, value in sorted(authorization.items(), key=lambda item: str(item[0])):
        if name not in declarations:
            rows.append(ConfigurationListRow("authorization", str(name), "unsupported", repr(value)))
    return rows


def _configuration_resolution_row(
    manifest: dict[str, Any],
    lock: dict[str, Any],
    checkout: dict[str, Any],
    resolution_path: Path,
) -> ConfigurationListRow:
    if not resolution_path.is_file():
        return ConfigurationListRow("resolution", "generated", "missing", str(resolution_path))
    resolved = load_toml(resolution_path)
    if resolved.get("devcapsule-resolved-schema-version") != 1:
        return ConfigurationListRow(
            "resolution", "generated", "invalid", "unsupported schema version"
        )
    if resolved.get("status") == "unresolved":
        return ConfigurationListRow("resolution", "generated", "unresolved", str(resolution_path))
    expected = {
        "manifest": canonical_digest(manifest),
        "platform-lock": canonical_digest(lock),
        "checkout-input": canonical_digest(checkout),
    }
    actual = resolved.get("sources", {})
    if not isinstance(actual, dict):
        return ConfigurationListRow("resolution", "generated", "invalid", "sources is not a table")
    stale = [name for name, digest in expected.items() if actual.get(name) != digest]
    if stale:
        return ConfigurationListRow("resolution", "generated", "stale", ", ".join(stale))
    return ConfigurationListRow("resolution", "generated", "fresh", str(resolution_path))


def _print_configuration_rows(rows: list[ConfigurationListRow]) -> None:
    headers = ("KIND", "NAME", "STATUS", "VALUE / RECOMMENDATION")
    values = [(row.kind, row.name, row.status, row.value) for row in rows]
    widths = [max(len(headers[index]), *(len(row[index]) for row in values)) for index in range(4)]
    click.echo("")
    click.echo("  ".join(header.ljust(widths[index]) for index, header in enumerate(headers)))
    for row in values:
        click.echo("  ".join(value.ljust(widths[index]) for index, value in enumerate(row)))


def _config_set_command() -> click.Command:
    @click.command("set", help="Set one ordinary value declared by the project configuration metadata.")
    @click.argument("name")
    @click.argument("value")
    @click.pass_obj
    def set_value(context: ProjectCommandContext, name: str, value: str) -> int:
        root, manifest = manifest_for(context.start_path())
        normalized = normalize_configuration_value(manifest, name, value)
        input_path, _output_path = checkout_record_paths(manifest, root)
        checkout: dict[str, Any] = load_toml(input_path) if input_path.is_file() else {}
        recorded_path = checkout.get("checkout", {}).get("path")
        if recorded_path and Path(str(recorded_path)).expanduser().resolve() != root:
            raise ProjectConfigurationError(f"{input_path} belongs to another checkout: {recorded_path}")
        state = dict(checkout.get("state", {}).get("adopted", {}))
        host = dict(checkout.get("host", {}))
        authorization = dict(checkout.get("authorization", {}))
        configuration = checkout.get("configuration", {})
        if not isinstance(configuration, dict):
            raise ProjectConfigurationError("Checkout configuration must be a table.")
        existing_values = configuration.get("values", {})
        if not isinstance(existing_values, dict):
            raise ProjectConfigurationError("Checkout configuration.values must be a table.")
        values = dict(existing_values)
        values[name] = normalized
        bindings = _checkout_host_directory_bindings(checkout)
        atomic_write(
            input_path,
            render_checkout(manifest, root, state, host, authorization, values, bindings),
        )
        click.echo(f"Set {name} = {render_toml_scalar(normalized)}")
        click.echo(f"Checkout input: {input_path}")
        click.echo("Run 'devcapsule project config resolve' before launch.")
        return 0

    return set_value


def _config_bind_command() -> click.Command:
    @click.command("bind", help="Bind a declared logical resource to a developer-owned provider.")
    @click.argument("name")
    @click.option(
        "--host-directory",
        "source",
        type=click.Path(path_type=Path),
        required=True,
        help="Existing host directory to expose read-write at the declared container path.",
    )
    @click.pass_obj
    def bind(context: ProjectCommandContext, name: str, source: Path) -> int:
        root, manifest = manifest_for(context.start_path())
        lock_path, lock = lock_for(root, manifest)
        declarations = configuration_binding_declarations(lock, source=str(lock_path))
        declaration = declarations.get(name)
        if declaration is None:
            available = ", ".join(sorted(declarations))
            raise ProjectConfigurationError(
                f"Configuration binding {name!r} is not declared by the selected component; "
                f"declared bindings: {available}."
            )
        source = source.expanduser().resolve()
        if not source.is_dir():
            raise ProjectConfigurationError(f"Binding source is not an existing directory: {source}")

        input_path, _output_path = checkout_record_paths(manifest, root)
        checkout: dict[str, Any] = load_toml(input_path) if input_path.is_file() else {}
        recorded_path = checkout.get("checkout", {}).get("path")
        if recorded_path and Path(str(recorded_path)).expanduser().resolve() != root:
            raise ProjectConfigurationError(f"{input_path} belongs to another checkout: {recorded_path}")
        state = dict(checkout.get("state", {}).get("adopted", {}))
        if name in state:
            raise ProjectConfigurationError(
                f"State resource {name!r} was already adopted; remove that transitional entry before binding it."
            )
        host = dict(checkout.get("host", {}))
        authorization = dict(checkout.get("authorization", {}))
        values = _checkout_values(checkout)
        bindings = _checkout_host_directory_bindings(checkout)
        bindings[name] = str(source)
        atomic_write(
            input_path,
            render_checkout(manifest, root, state, host, authorization, values, bindings),
        )
        click.echo(
            f"WARNING: exposing host directory read-write for {name}: {source} -> "
            f"{declaration.container_path}",
            err=True,
        )
        click.echo(f"Sensitivity: {declaration.sensitivity}", err=True)
        if not declaration.concurrent:
            click.echo("Concurrency: exclusive; do not share this binding with a concurrent capsule.", err=True)
        click.echo(f"Bound {name} to host directory: {source}")
        click.echo(f"Checkout input: {input_path}")
        click.echo("Run 'devcapsule project config resolve' before launch.")
        return 0

    return bind


def _checkout_values(checkout: dict[str, Any]) -> dict[str, Any]:
    configuration = checkout.get("configuration", {})
    if not isinstance(configuration, dict):
        raise ProjectConfigurationError("Checkout configuration must be a table.")
    values = configuration.get("values", {})
    if not isinstance(values, dict):
        raise ProjectConfigurationError("Checkout configuration.values must be a table.")
    return dict(values)


def _checkout_host_directory_bindings(checkout: dict[str, Any]) -> dict[str, str]:
    configuration = checkout.get("configuration", {})
    if not isinstance(configuration, dict):
        raise ProjectConfigurationError("Checkout configuration must be a table.")
    bindings = configuration.get("bindings", {})
    if not isinstance(bindings, dict):
        raise ProjectConfigurationError("Checkout configuration.bindings must be a table.")
    host_directories = bindings.get("host-directory", {})
    if not isinstance(host_directories, dict) or not all(
        isinstance(name, str) and isinstance(source, str)
        for name, source in host_directories.items()
    ):
        raise ProjectConfigurationError(
            "Checkout configuration.bindings.host-directory must contain path strings."
        )
    return dict(host_directories)


def _config_authorize_command() -> click.Command:
    @click.command(
        "authorize",
        help="Authorize exact security-sensitive values recommended by the project.",
    )
    @click.argument("name", required=False)
    @click.argument("value", required=False)
    @click.option(
        "--all-recommended",
        is_flag=True,
        help="Preview every recommendation and authorize all only after the y key is pressed.",
    )
    @click.pass_obj
    def authorize(
        context: ProjectCommandContext,
        name: str | None,
        value: str | None,
        all_recommended: bool,
    ) -> int:
        root, manifest = manifest_for(context.start_path())
        _lock_path, lock = lock_for(root, manifest)
        declarations = authorization_declarations(manifest, lock)
        if all_recommended:
            if name is not None or value is not None:
                raise click.UsageError(
                    "--all-recommended cannot be combined with an authorization NAME or VALUE."
                )
            return _authorize_all_recommended(root, manifest, declarations)
        if name is None or value is None:
            raise click.UsageError(
                "Provide NAME VALUE, or use --all-recommended for interactive bulk authorization."
            )
        declaration = declarations.get(name)
        if declaration is None:
            available = ", ".join(sorted(declarations)) or "none"
            raise ProjectConfigurationError(
                f"Authorization {name!r} is not declared by this project and lock; "
                f"declared authorizations: {available}."
            )
        normalized = normalize_authorization_value(declaration, value)

        input_path, _output_path = checkout_record_paths(manifest, root)
        checkout: dict[str, Any] = load_toml(input_path) if input_path.is_file() else {}
        recorded_path = checkout.get("checkout", {}).get("path")
        if recorded_path and Path(str(recorded_path)).expanduser().resolve() != root:
            raise ProjectConfigurationError(f"{input_path} belongs to another checkout: {recorded_path}")
        state = dict(checkout.get("state", {}).get("adopted", {}))
        host = dict(checkout.get("host", {}))
        authorization = dict(checkout.get("authorization", {}))
        values = _checkout_values(checkout)
        bindings = _checkout_host_directory_bindings(checkout)
        if name == "base-image":
            authorization[name] = {
                "reference": normalized,
                "lock-digest": declaration.recommendation_digest,
            }
        else:
            authorization[name] = {
                "value": normalized,
                "recommendation-digest": declaration.recommendation_digest,
            }
        atomic_write(
            input_path,
            render_checkout(manifest, root, state, host, authorization, values, bindings),
        )
        click.echo(f"Authorized {name} for this checkout: {render_authorization_value(normalized)}")
        click.echo(f"Recommendation: {declaration.description}")
        click.echo(f"Recommendation digest: {declaration.recommendation_digest}")
        click.echo(f"Checkout input: {input_path}")
        click.echo("This authorization applies only to the exact recorded value and recommendation.")
        click.echo("Run 'devcapsule project config resolve' before materialization or launch.")
        return 0

    return authorize


def _authorize_all_recommended(
    root: Path,
    manifest: dict[str, Any],
    declarations: dict[str, AuthorizationDeclaration],
) -> int:
    if not declarations:
        raise ProjectConfigurationError("This project and lock declare no authorization recommendations.")

    input_path, _output_path = checkout_record_paths(manifest, root)
    checkout: dict[str, Any] = load_toml(input_path) if input_path.is_file() else {}
    recorded_path = checkout.get("checkout", {}).get("path")
    if recorded_path and Path(str(recorded_path)).expanduser().resolve() != root:
        raise ProjectConfigurationError(f"{input_path} belongs to another checkout: {recorded_path}")
    state = dict(checkout.get("state", {}).get("adopted", {}))
    host = dict(checkout.get("host", {}))
    authorization = dict(checkout.get("authorization", {}))
    values = _checkout_values(checkout)
    bindings = _checkout_host_directory_bindings(checkout)

    click.echo(f"The following authorizations will be granted for checkout {root}:")
    for name, declaration in sorted(declarations.items()):
        rendered = render_authorization_value(declaration.recommended_value)
        click.echo(f"- {name}: {rendered}")
        click.echo(f"  Justification: {declaration.description}")
        click.echo(f"  Recommendation digest: {declaration.recommendation_digest}")
    if not sys.stdin.isatty():
        raise ProjectConfigurationError(
            "--all-recommended requires an interactive terminal; authorize each exact value "
            "individually in non-interactive workflows."
        )
    click.echo("Press y to authorize every recommendation; any other key cancels: ", nl=False)
    try:
        accepted = readchar.readkey() == "y"
    except (EOFError, OSError) as exc:
        click.echo("")
        raise ProjectConfigurationError(f"Cannot read authorization confirmation key: {exc}") from exc
    click.echo("")
    if not accepted:
        click.echo("Authorization cancelled; no changes written.")
        return 1

    for name, declaration in declarations.items():
        if name == "base-image":
            authorization[name] = {
                "reference": declaration.recommended_value,
                "lock-digest": declaration.recommendation_digest,
            }
        else:
            authorization[name] = {
                "value": declaration.recommended_value,
                "recommendation-digest": declaration.recommendation_digest,
            }
    atomic_write(
        input_path,
        render_checkout(manifest, root, state, host, authorization, values, bindings),
    )
    click.echo(f"Authorized {len(declarations)} recommendations for this checkout.")
    click.echo(f"Checkout input: {input_path}")
    click.echo("Run 'devcapsule project config resolve' before materialization or launch.")
    return 0


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
        authorization = dict(checkout.get("authorization", {}))
        values = _checkout_values(checkout)
        bindings = _checkout_host_directory_bindings(checkout)
        if slot in bindings:
            raise ProjectConfigurationError(
                f"State resource {slot!r} is already configuration-bound; it cannot also be adopted."
            )
        state[slot] = str(source)
        atomic_write(
            path,
            render_checkout(manifest, root, state, host, authorization, values, bindings),
        )
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
        memory_limit = runtime.get("memory-limit-bytes")
        if memory_limit is not None and (
            not isinstance(memory_limit, int) or isinstance(memory_limit, bool) or memory_limit <= 0
        ):
            raise ProjectConfigurationError("Resolved runtime.memory-limit-bytes must be a positive integer.")
        state_root = resolved.get("state", {})
        state = dict(state_root.get("adopted", {}))
        state.update(state_root.get("bindings", {}))
        host = resolved.get("host", {})
        authorization = resolved.get("authorization", {})
        selected_docker_daemon = (
            docker_daemon
            or authorization.get("docker-daemon")
            or host.get("docker-daemon", "none")
        )
        selected_sudo = development_sudo
        if selected_sudo is None:
            selected_sudo = bool(
                authorization.get("development-sudo", host.get("development-sudo", False))
            )
        selected_network = str(authorization.get("network", host.get("network", "bridge")))
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
                network_mode=selected_network,
                memory_limit_bytes=memory_limit,
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
