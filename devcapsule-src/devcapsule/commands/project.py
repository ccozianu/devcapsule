"""Project and checkout command subtree.

Command classes here declare parameters and print operation reports; policy
and artifact writes live in :mod:`devcapsule.project_operations` and the
modules it composes.  The configuration grammar is the settled v027 shape:
every mutation is ``VERB NAME VALUE`` with the node's one canonical name —
``set NAME VALUE``, ``bind NAME PROVIDER:VALUE``,
``authorize NAME VALUE [JUSTIFICATION]``, ``unset NAME`` — and ``init``
accepts the same spellings through its carrier options.  The standalone
``lock`` stub is retired: the platform lock is authored by ``init`` from the
embedded resolution matrix.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import os
import sys
import termios
import tty
from typing import Any, Mapping

from devcapsule.commands.framework import (
    Command,
    Group,
    add_carrier_options,
    carrier_answers,
)
from devcapsule.components.catalog import INTERACTIVE_SURFACES
from devcapsule.config_history import record_known_good_configuration
from devcapsule.configurations.pycharm import (
    DockerMode,
    PycharmRunOptions,
    reject_launcher_owned_docker_options,
    run_pycharm,
)
from devcapsule.configuration_nodes import (
    CARRIER_FAMILY_BIND,
    CARRIER_FAMILY_SET,
    PROVIDER_HOST_DIRECTORY,
    build_node_registry,
)
from devcapsule.environment_realization import realize_environment, required_local_image
from devcapsule.materialization import validate_base_image
from devcapsule.project import project_namespace
from devcapsule.project_operations import (
    CheckoutRecord,
    InitializeRequest,
    ProvidedAnswer,
    add_capability_need,
    initialize_project,
    resolve_checkout,
)
from devcapsule.project_runtime_plan import project_runtime_plan
from devcapsule.recursive_dogfood import (
    RECURSIVE_E2E_ENABLED_ENV,
    PreflightError,
    preflight_json,
    recursive_e2e_launch_environment,
    render_preflight,
    require_recursive_e2e_project,
    run_recursive_preflight,
)
from devcapsule.recursive_orchestrator import (
    RecursiveE2EError,
    RecursivePreflightFailed,
    run_recursive_e2e_dry_run,
)
from devcapsule.recursive_successor import (
    RecursiveSuccessorError,
    inspect_successor,
    launch_successor,
)
from devcapsule.project_configuration import (
    AuthorizationDeclaration,
    ProjectConfigurationError,
    ResolvedProject,
    authorized_base_selection,
    authorization_declarations,
    atomic_write,
    checkout_record_paths,
    configuration_binding_declarations,
    component_secret_inputs,
    configuration_value_declarations,
    config_root,
    discover_project,
    find_checkout_record,
    immutable_registry_reference,
    load_toml,
    lock_for,
    manifest_for,
    named_checkout_record_paths,
    memory_size_bytes,
    normalize_configuration_value,
    normalize_authorization_value,
    registered_checkouts,
    render_checkout,
    render_authorization_value,
    render_toml_scalar,
    resolve_secret_bindings,
    stale_resolution_inputs,
)


@dataclass(frozen=True)
class ProjectCommandContext:
    selected_path: Path | None

    def start_path(self) -> Path:
        return self.selected_path or Path(".")

    def target_path(self) -> Path:
        return self.start_path().expanduser().resolve()


def _project_context(context: object | None) -> ProjectCommandContext:
    assert isinstance(context, ProjectCommandContext)
    return context


class ProjectListCommand(Command):
    name = "list"
    help = "List developer-owned checkout records from the XDG registry."

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        records = registered_checkouts()
        if not records:
            print(f"No registered DevCapsule project checkouts found in {config_root() / 'projects'}.")
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
        print("  ".join(header.ljust(widths[index]) for index, header in enumerate(headers)))
        for row in rows:
            print("  ".join(value.ljust(widths[index]) for index, value in enumerate(row)))
        return 0


class ProjectInitCommand(Command):
    name = "init"
    help = (
        "Initialize the project: manifest, platform lock, owner checkout record, "
        "and a fresh resolution."
    )

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--need",
            action="append",
            default=[],
            metavar="CAPABILITY",
            help="A capability the project needs; repeatable.",
        )
        parser.add_argument("--name", dest="project_name", help="Project display name.")
        parser.add_argument("--slug", help="Project identity slug.")
        parser.add_argument("--creator", help="Project creator URL or email address.")
        parser.add_argument("--project-mount", help="In-container project mount path.")
        parser.add_argument(
            "--regenerate",
            action="store_true",
            help="Rewrite the derived platform lock from the current embedded matrix; keep the authored manifest.",
        )
        parser.add_argument(
            "--less-pedantic",
            action="store_true",
            help=(
                "Skip confirmation prompts for values supplied explicitly — e.g. a "
                "base-image selection is validated and recorded without soliciting "
                "consent."
            ),
        )
        parser.add_argument(
            "--unverified",
            action="store_true",
            dest="allow_unverified",
            help=(
                "If no fully verified combination satisfies the need, resolve past "
                "the matrix with a gentle warning; the generated lock names every "
                "unverified combination."
            ),
        )
        add_carrier_options(parser)

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        answers = tuple(
            ProvidedAnswer(
                family=answer.family,
                name=answer.name,
                value=answer.value,
                justification=answer.justification,
            )
            for answer in carrier_answers(arguments)
        )
        report = initialize_project(
            InitializeRequest(
                directory=_project_context(context).target_path(),
                need=tuple(arguments.need),
                project_name=arguments.project_name,
                slug=arguments.slug,
                creator=arguments.creator,
                project_mount=arguments.project_mount,
                answers=answers,
                regenerate=arguments.regenerate,
                less_pedantic=arguments.less_pedantic,
                allow_unverified=arguments.allow_unverified,
            )
        )
        print(report.render())
        return 0


class CheckoutRegisterCommand(Command):
    name = "register"
    help = "Register this checkout under a distinct workstation-owned name."

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("checkout_name", metavar="NAME")

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        root, manifest = manifest_for(_project_context(context).start_path())
        selected_input = find_checkout_record(manifest, root)
        if selected_input is not None:
            raise ProjectConfigurationError(f"Checkout is already registered in {selected_input}.")
        input_path, output_path = named_checkout_record_paths(manifest, arguments.checkout_name)
        if input_path.exists() or output_path.exists():
            raise ProjectConfigurationError(
                f"Checkout name {arguments.checkout_name!r} is already in use under {input_path.parent}."
            )
        atomic_write(input_path, render_checkout(manifest, root, {}, {}))
        print(f"Registered checkout {arguments.checkout_name!r}: {input_path}")
        return 0


class CheckoutGroup(Group):
    name = "checkout"
    help = "Register additional local checkouts."

    @classmethod
    def subcommands(cls) -> Mapping[str, type[Command] | type[Group]]:
        return {CheckoutRegisterCommand.name: CheckoutRegisterCommand}


class ConfigResolveCommand(Command):
    name = "resolve"
    help = "Validate the combined configuration and write the generated resolution."

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        report = resolve_checkout(_project_context(context).start_path())
        print(report.render())
        return 0


@dataclass(frozen=True)
class ConfigurationListRow:
    kind: str
    name: str
    status: str
    value: str


class ConfigListCommand(Command):
    name = "list"
    help = "Show configured values, bindings, authorizations, and resolution readiness."

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        root, manifest = manifest_for(_project_context(context).start_path())
        _lock_path, lock = lock_for(root, manifest)
        input_path, resolution_path = checkout_record_paths(manifest, root)
        if not input_path.is_file():
            atomic_write(input_path, render_checkout(manifest, root, {}, {}))
            print(f"Initialized checkout input: {input_path}")
        if not resolution_path.is_file():
            atomic_write(
                resolution_path,
                'devcapsule-resolved-schema-version = 1\nstatus = "unresolved"\n',
            )
            print(f"Initialized resolution placeholder: {resolution_path}")
        checkout = load_toml(input_path)

        identity = manifest["project"]
        print(f"Project: {identity['creator']}/{identity['slug']}")
        print(f"Checkout: {root}")
        checkout_name = (
            "default"
            if input_path.name == "devcapsule.checkout.toml"
            else input_path.name.removesuffix(".checkout.toml")
        )
        print(f"Checkout name: {checkout_name}")
        print(f"Checkout input: {input_path}")
        print(f"Generated plan: {resolution_path}")

        rows = [
            *_configuration_value_rows(manifest, checkout),
            *_configuration_binding_rows(lock, checkout),
            *_component_secret_rows(lock, checkout),
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


class ConfigSetCommand(Command):
    name = "set"
    help = "Set one ordinary value declared by the project configuration metadata."

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("node_name", metavar="NAME")
        parser.add_argument("value", metavar="VALUE")

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        name = arguments.node_name
        root, manifest = manifest_for(_project_context(context).start_path())
        record = CheckoutRecord(manifest, root)
        if arguments.value.strip().lower() == "none":
            # The explicit-absence answer (owner ruling 2026-09-03): recorded
            # as a decision, the node stays absent from the runtime config
            # unless overridden on the 'project run' command line.
            _lock_path, lock = lock_for(root, manifest)
            node = build_node_registry(manifest, lock).node(name)
            if node.family != CARRIER_FAMILY_SET:
                raise ProjectConfigurationError(
                    f"Configuration node {name!r} is a {node.family} node; "
                    f"answer it through 'config {node.family}'."
                )
            if node.required:
                raise ProjectConfigurationError(
                    f"Configuration value {name!r} is mandatory and cannot be "
                    "'none'; record a value instead."
                )
            record.omit_value(name)
            record.write()
            print(f"Set {name} = none (explicitly absent from the runtime configuration)")
        else:
            normalized = normalize_configuration_value(manifest, name, arguments.value)
            record.set_value(name, normalized)
            record.write()
            print(f"Set {name} = {render_toml_scalar(normalized)}")
        print(f"Checkout input: {record.input_path}")
        print("Run 'devcapsule project config resolve' before launch.")
        return 0


class ConfigBindCommand(Command):
    name = "bind"
    help = "Bind a declared logical resource to a developer-owned provider (PROVIDER:VALUE)."

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("node_name", metavar="NAME")
        parser.add_argument(
            "value",
            metavar="PROVIDER:VALUE",
            help="host-directory:PATH for state, host-environment:VARIABLE for a declared secret.",
        )

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        name = arguments.node_name
        root, manifest = manifest_for(_project_context(context).start_path())
        _lock_path, lock = lock_for(root, manifest)
        registry = build_node_registry(manifest, lock)
        provider, raw_value = registry.split_bind_value(name, arguments.value)
        node = registry.node(name)

        record = CheckoutRecord(manifest, root)
        if name in record.state:
            raise ProjectConfigurationError(
                f"State resource {name!r} was already adopted; remove that transitional entry before binding it."
            )
        if provider == PROVIDER_HOST_DIRECTORY:
            source = Path(raw_value).expanduser().resolve()
            if not source.is_dir():
                raise ProjectConfigurationError(
                    f"Binding source is not an existing directory: {source}"
                )
            record.directory_bindings[name] = str(source)
            record.write()
            declaration = node.declaration
            print(
                f"WARNING: exposing host directory read-write for {name}: {source} -> "
                f"{declaration.container_path}",
                file=sys.stderr,
            )
            print(f"Sensitivity: {declaration.sensitivity}", file=sys.stderr)
            if not declaration.concurrent:
                print(
                    "Concurrency: exclusive; do not share this binding with a concurrent capsule.",
                    file=sys.stderr,
                )
            print(f"Bound {name} to host directory: {source}")
        else:
            secret = node.declaration
            if raw_value != secret.environment_variable:
                raise ProjectConfigurationError(
                    f"Secret input {name!r} must use host environment variable "
                    f"{secret.environment_variable!r}."
                )
            record.environment_bindings[name] = raw_value
            record.write()
            print(
                f"WARNING: {raw_value} will be visible to every process in the capsule "
                "and through Docker container inspection while it runs.",
                file=sys.stderr,
            )
            print(f"Bound {name} to host environment variable: {raw_value}")
        print(f"Checkout input: {record.input_path}")
        print("Run 'devcapsule project config resolve' before launch.")
        return 0


class ConfigUnsetCommand(Command):
    name = "unset"
    help = "Remove one recorded answer from this checkout."

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("node_name", metavar="NAME")

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        name = arguments.node_name
        root, manifest = manifest_for(_project_context(context).start_path())
        _lock_path, lock = lock_for(root, manifest)
        registry = build_node_registry(manifest, lock)
        node = registry.node(name)
        if node.required:
            # Owner ruling 2026-09-03: unset removes the name from the tree,
            # and a mandatory node without an answer only defers the failure
            # to resolve time — refuse it here, naming the replacement verb.
            replacement = {
                CARRIER_FAMILY_SET: f"'devcapsule project config set {name} VALUE'",
                CARRIER_FAMILY_BIND: f"'devcapsule project config bind {name} PROVIDER:VALUE'",
            }.get(
                node.family,
                f"'devcapsule project config authorize {name} VALUE'",
            )
            raise ProjectConfigurationError(
                f"Configuration node {name!r} is mandatory: resolution fails while "
                f"it is unanswered, so 'unset' would only trade the recorded answer "
                f"for a failure at resolve time. Record a different answer with "
                f"{replacement} instead."
            )
        record = CheckoutRecord(manifest, root)
        if node.family == CARRIER_FAMILY_SET:
            removed = record.values.pop(name, None)
            if removed is None and name in record.omitted_values:
                # Unsetting an explicit omission returns the node to silence.
                record.omitted_values.discard(name)
                removed = "none"
        elif node.family == CARRIER_FAMILY_BIND:
            removed = (
                record.directory_bindings.pop(name, None)
                or record.environment_bindings.pop(name, None)
                # A transitional 'state adopt' entry answers the same node.
                or record.state.pop(name, None)
            )
        else:
            removed = record.authorization.pop(name, None)
        if removed is None:
            raise ProjectConfigurationError(
                f"Configuration node {name!r} has no recorded answer for this checkout."
            )
        record.write()
        print(f"Unset {name} for this checkout.")
        print(f"Checkout input: {record.input_path}")
        print("Run 'devcapsule project config resolve' before launch.")
        return 0


class ConfigAuthorizeCommand(Command):
    name = "authorize"
    help = (
        "Authorize project-recommended host access or select an exact inspected "
        "local DevCapsule base."
    )

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("node_name", metavar="NAME", nargs="?")
        parser.add_argument("value", metavar="VALUE", nargs="?")
        parser.add_argument("justification", metavar="JUSTIFICATION", nargs="?")
        parser.add_argument(
            "--all-recommended",
            action="store_true",
            help="Preview every recommendation and authorize all only after the y key is pressed.",
        )

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        name = arguments.node_name
        value = arguments.value
        root, manifest = manifest_for(_project_context(context).start_path())
        _lock_path, lock = lock_for(root, manifest)
        declarations = authorization_declarations(manifest, lock)
        if arguments.all_recommended:
            if name is not None or value is not None:
                raise ProjectConfigurationError(
                    "--all-recommended cannot be combined with an authorization NAME or VALUE."
                )
            return _authorize_all_recommended(root, manifest, declarations)
        if name is None or value is None:
            raise ProjectConfigurationError(
                "Provide NAME VALUE, or use --all-recommended for interactive bulk authorization."
            )
        if arguments.justification is not None:
            # The justification facet belongs to recommendation authoring at
            # init; an already-declared recommendation carries its own.
            raise ProjectConfigurationError(
                "A justification is recorded when the project owner authors the recommendation "
                "at 'devcapsule project init'; it does not apply to authorizing this checkout."
            )
        declaration = declarations.get(name)
        if declaration is None:
            available = ", ".join(sorted(declarations)) or "none"
            raise ProjectConfigurationError(
                f"Authorization {name!r} is not declared by this project and lock; "
                f"declared authorizations: {available}."
            )
        local_base_identity: str | None = None
        local_base_value = (
            name == "base-image"
            and value.strip().lower() not in {"default", "none"}
            and value != declaration.recommended_value
        )
        if local_base_value:
            try:
                immutable_registry_reference(value)
            except ProjectConfigurationError:
                pass
            else:
                # A different published digest needs its own project-reviewed
                # recommendation. Only a daemon-local selection is exempt.
                normalize_authorization_value(declaration, value)
            platform_name = lock.get("platform")
            if not isinstance(platform_name, str) or not platform_name:
                raise ProjectConfigurationError("Platform lock must name its target platform.")
            local_base = required_local_image(value)
            validate_base_image(
                local_base,
                platform=platform_name,
                expected_identity=None,
            )
            normalized: str | bool = value
            local_base_identity = local_base.identity
        else:
            normalized = normalize_authorization_value(declaration, value)

        record = CheckoutRecord(manifest, root)
        input_path = record.input_path
        if name == "base-image":
            record.authorization[name] = {
                "reference": normalized,
                "lock-digest": declaration.recommendation_digest,
            }
            if local_base_identity is not None:
                record.authorization[name]["image-id"] = local_base_identity
        else:
            record.authorization[name] = {
                "value": normalized,
                "recommendation-digest": declaration.recommendation_digest,
            }
        record.write()
        authorized_value = render_authorization_value(normalized)
        if local_base_identity is None and declaration.display_value is not None:
            authorized_value = declaration.display_value
        print(f"Authorized {name} for this checkout: {authorized_value}")
        if local_base_identity is not None:
            print(f"Local image ID: {local_base_identity}")
            print(
                "This developer-owned selection overrides the published base recommendation "
                "for this checkout."
            )
        else:
            print(f"Recommendation: {declaration.description}")
        print(f"Recommendation digest: {declaration.recommendation_digest}")
        print(f"Checkout input: {input_path}")
        print(
            "This authorization applies only to the exact recorded value, image identity when "
            "local, and current lock."
        )
        print("Run 'devcapsule project config resolve' before materialization or launch.")
        return 0


class ConfigNeedCommand(Command):
    name = "need"
    help = (
        "Add capabilities to the project's need; the lock regenerates, new "
        "acquisition gates elicit (--authorize NAME VALUE answers them), and "
        "the resolution refreshes so 'project run' works immediately."
    )

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "capabilities",
            nargs="+",
            metavar="CAPABILITY",
            help="Capability to add to capabilities.need; repeatable.",
        )
        add_carrier_options(parser, families=("authorize",))

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        answers = tuple(
            ProvidedAnswer(
                family=answer.family,
                name=answer.name,
                value=answer.value,
                justification=answer.justification,
            )
            for answer in carrier_answers(arguments)
        )
        report = add_capability_need(
            _project_context(context).target_path(),
            arguments.capabilities,
            answers,
        )
        print(report.render())
        return 0


class ConfigGroup(Group):
    name = "config"
    help = "Inspect and resolve layered project configuration."

    @classmethod
    def subcommands(cls) -> Mapping[str, type[Command] | type[Group]]:
        return {
            ConfigListCommand.name: ConfigListCommand,
            ConfigResolveCommand.name: ConfigResolveCommand,
            ConfigNeedCommand.name: ConfigNeedCommand,
            ConfigSetCommand.name: ConfigSetCommand,
            ConfigBindCommand.name: ConfigBindCommand,
            ConfigAuthorizeCommand.name: ConfigAuthorizeCommand,
            ConfigUnsetCommand.name: ConfigUnsetCommand,
        }


class StateAdoptCommand(Command):
    name = "adopt"
    help = "Adopt an existing host directory for a declared state slot."

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("slot")
        parser.add_argument("--from", dest="source", type=Path, required=True)

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        slot = arguments.slot
        root, manifest = manifest_for(_project_context(context).start_path())
        lock_path, lock = lock_for(root, manifest)
        declarations = configuration_binding_declarations(lock, source=str(lock_path))
        if slot not in declarations:
            available = ", ".join(sorted(declarations))
            raise ProjectConfigurationError(
                f"State resource {slot!r} is not declared by the selected components; "
                f"declared resources: {available}."
            )
        source = arguments.source.expanduser().resolve()
        if not source.is_dir():
            raise ProjectConfigurationError(f"State source is not a directory: {source}")
        record = CheckoutRecord(manifest, root)
        if slot in record.directory_bindings:
            raise ProjectConfigurationError(
                f"State resource {slot!r} is already configuration-bound; it cannot also be adopted."
            )
        record.state[slot] = str(source)
        record.write()
        print(f"Adopted {slot}: {source}")
        print("Run 'devcapsule project config resolve' before launch.")
        return 0


class StateGroup(Group):
    name = "state"
    help = "Inspect and adopt checkout-scoped persistent state."

    @classmethod
    def subcommands(cls) -> Mapping[str, type[Command] | type[Group]]:
        return {StateAdoptCommand.name: StateAdoptCommand}


def _add_runtime_plan_options(parser: argparse.ArgumentParser, *, host_paths: bool = True) -> None:
    parser.add_argument(
        "--runtime-plan",
        type=Path,
        default=Path("/etc/devcapsule/runtime-plan.json"),
        help="External runtime plan mounted into the current capsule.",
    )
    parser.add_argument(
        "--json", dest="as_json", action="store_true", help="Emit stable machine-readable JSON."
    )
    if host_paths:
        parser.add_argument(
            "--show-host-paths",
            action="store_true",
            help="Include sensitive host mount sources after an explicit warning.",
        )


class RecursivePreflightCommand(Command):
    name = "preflight"
    help = "Check recursive dogfood readiness for this capsule."

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        _add_runtime_plan_options(parser)

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        root = _recursive_project_root(_project_context(context))
        _warn_for_host_path_disclosure(arguments.show_host_paths)
        report = run_recursive_preflight(root, runtime_plan_path=arguments.runtime_plan)
        print(
            preflight_json(report, show_host_paths=arguments.show_host_paths)
            if arguments.as_json
            else render_preflight(report, show_host_paths=arguments.show_host_paths)
        )
        return 0 if report.ready else 1


class RecursiveRunCommand(Command):
    name = "run"
    help = "Run the recursive dogfood E2E dry run."

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        _add_runtime_plan_options(parser)
        parser.add_argument(
            "--keep-on-failure",
            action="store_true",
            help="Preserve only this run's ownership-marked workspace after failure.",
        )

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        root = _recursive_project_root(_project_context(context))
        _warn_for_host_path_disclosure(arguments.show_host_paths)
        try:
            result = run_recursive_e2e_dry_run(
                root,
                runtime_plan_path=arguments.runtime_plan,
                keep_on_failure=arguments.keep_on_failure,
            )
        except RecursivePreflightFailed as exc:
            print(
                preflight_json(exc.report, show_host_paths=arguments.show_host_paths)
                if arguments.as_json
                else render_preflight(exc.report, show_host_paths=arguments.show_host_paths)
            )
            return 1
        except RecursiveE2EError as exc:
            raise ProjectConfigurationError(str(exc)) from exc
        mapping = result.to_mapping(show_host_paths=arguments.show_host_paths)
        print(
            result.to_json(show_host_paths=arguments.show_host_paths)
            if arguments.as_json
            else json.dumps(mapping, ensure_ascii=False, indent=2, sort_keys=True)
        )
        return 0


class RecursiveLaunchSuccessorCommand(Command):
    name = "launch-successor"
    help = "Launch a successor capsule from a retained materialization run."

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--run-id", required=True, help="Existing retained materialization run ID.")
        _add_runtime_plan_options(parser, host_paths=False)

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        root = _recursive_project_root(_project_context(context))
        try:
            result = launch_successor(
                root, arguments.run_id, runtime_plan_path=arguments.runtime_plan
            )
        except RecursiveSuccessorError as exc:
            raise ProjectConfigurationError(str(exc)) from exc
        print(result.to_json() if arguments.as_json else json.dumps(result.to_mapping(), indent=2, sort_keys=True))
        return 0


class RecursiveInspectSuccessorCommand(Command):
    name = "inspect-successor"
    help = "Independently inspect a retained successor against its expected plan."

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--run-id", required=True, help="Existing retained successor run ID.")
        parser.add_argument(
            "--json", dest="as_json", action="store_true", help="Emit stable machine-readable JSON."
        )

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        try:
            result = inspect_successor(arguments.run_id)
        except RecursiveSuccessorError as exc:
            raise ProjectConfigurationError(str(exc)) from exc
        print(result.to_json() if arguments.as_json else json.dumps(result.to_mapping(), indent=2, sort_keys=True))
        return 0


class RecursiveE2EGroup(Group):
    name = "recursive-e2e"
    help = "Run DevCapsule's project-specific recursive dogfood validation."

    @classmethod
    def subcommands(cls) -> Mapping[str, type[Command] | type[Group]]:
        return {
            RecursivePreflightCommand.name: RecursivePreflightCommand,
            RecursiveRunCommand.name: RecursiveRunCommand,
            RecursiveLaunchSuccessorCommand.name: RecursiveLaunchSuccessorCommand,
            RecursiveInspectSuccessorCommand.name: RecursiveInspectSuccessorCommand,
        }


# The authorization nodes whose run-once answers feed the launch plan; every
# other authorization (base-image, acquisitions) is inherently persistent.
_RUN_ONCE_AUTHORIZATIONS = ("docker-daemon", "network", "development-sudo", "host-browser")


class ProjectRunCommand(Command):
    name = "run"
    help = (
        "Run the project from its platform lock and developer-owned resolution. "
        "Run-once answers use the config grammar (--authorize NAME VALUE, "
        "--set NAME VALUE) and are never persisted; everything after '--' is "
        "handed verbatim to 'docker run', except single-instance options the "
        "launcher composes (--network, --memory, --shm-size, ...), which are "
        "refused with the sanctioned alternative named."
    )
    passthrough_dest = "docker_options"
    passthrough_metavar = "DOCKER-RUN-OPTIONS"

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--force", action="store_true", help="Use stale generated resolution once, with a warning."
        )
        parser.add_argument(
            "--no-recursive-e2e",
            action="store_true",
            help="Disable DevCapsule recursive-E2E readiness for this launch.",
        )
        parser.add_argument("--name", dest="container_name")
        add_carrier_options(parser, families=("set", "authorize"))

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        root, manifest = manifest_for(_project_context(context).start_path())
        _lock_path, lock = lock_for(root, manifest)
        input_path, output_path = checkout_record_paths(manifest, root)
        if not input_path.is_file() or not output_path.is_file():
            raise ProjectConfigurationError(
                "Local resolution is missing; run 'devcapsule project config resolve'."
            )
        checkout = load_toml(input_path)
        resolved = load_toml(output_path)
        stale = stale_resolution_inputs(manifest, lock, checkout, resolved)
        if stale and not arguments.force:
            raise ProjectConfigurationError(
                f"Local resolution is stale ({', '.join(stale)}); run 'devcapsule project config resolve'."
            )
        if stale:
            print(f"WARNING: using stale generated resolution once ({', '.join(stale)}).", file=sys.stderr)
        runtime = resolved.get("runtime", {})
        component = runtime.get("component") if isinstance(runtime, dict) else None
        if not isinstance(runtime, dict) or component not in INTERACTIVE_SURFACES:
            raise ProjectConfigurationError(
                "Run requires a resolution selecting a known interactive surface; "
                "run 'devcapsule project config resolve'."
            )
        image = runtime.get("image")
        checkout_runtime_plan = None
        use_image_process = False
        if isinstance(lock.get("base"), dict) and isinstance(lock.get("materialization"), dict):
            selected = ResolvedProject(
                root=root,
                manifest=manifest,
                lock_path=_lock_path,
                lock=lock,
                checkout_path=input_path,
                checkout=checkout,
                resolution_path=output_path,
                resolution=resolved,
            )
            realized = realize_environment(selected)
            image = realized.image.reference
            checkout_runtime_plan = project_runtime_plan(selected, realized.locked)
            use_image_process = True
            action = "Materialized" if realized.created else "Reused"
            print(f"{action} canonical environment: {image}")
        if not isinstance(image, str) or not image:
            raise ProjectConfigurationError(
                f"The resolved {component} environment has no runnable image."
            )
        memory_limit = runtime.get("memory-limit-bytes")
        if memory_limit is not None and (
            not isinstance(memory_limit, int) or isinstance(memory_limit, bool) or memory_limit <= 0
        ):
            raise ProjectConfigurationError("Resolved runtime.memory-limit-bytes must be a positive integer.")
        state_root = resolved.get("state", {})
        state = dict(state_root.get("adopted", {}))
        state.update(state_root.get("bindings", {}))
        secret_root = resolved.get("secret", {})
        secret_bindings_root = (
            secret_root.get("bindings", {}) if isinstance(secret_root, dict) else {}
        )
        secret_environment = (
            secret_bindings_root.get("host-environment", {})
            if isinstance(secret_bindings_root, dict)
            else {}
        )
        if not isinstance(secret_environment, dict) or not all(
            isinstance(name, str) and isinstance(source, str)
            for name, source in secret_environment.items()
        ):
            raise ProjectConfigurationError(
                "Resolved secret.bindings.host-environment must contain environment names."
            )
        host = resolved.get("host", {})
        authorization = resolved.get("authorization", {})
        overrides, memory_override = _run_once_answers(arguments, manifest, lock)
        if memory_override is not None:
            memory_limit = memory_override
        selected_docker_daemon = (
            overrides.get("docker-daemon")
            or authorization.get("docker-daemon")
            or host.get("docker-daemon", "none")
        )
        selected_sudo = bool(
            overrides.get(
                "development-sudo",
                authorization.get("development-sudo", host.get("development-sudo", False)),
            )
        )
        selected_network = str(
            overrides.get("network", authorization.get("network", host.get("network", "bridge")))
        )
        selected_host_browser = bool(
            overrides.get(
                "host-browser",
                authorization.get("host-browser", host.get("host-browser", False)),
            )
        )
        if arguments.no_recursive_e2e:
            selected_docker_daemon = "none"
            selected_sudo = False
            selected_network = "bridge"
        recursive_environment = recursive_e2e_launch_environment(
            root,
            docker_daemon=str(selected_docker_daemon),
            disabled=arguments.no_recursive_e2e,
        )
        readiness = recursive_environment.get(RECURSIVE_E2E_ENABLED_ENV)
        if readiness is not None:
            if readiness == "1":
                print("Recursive E2E readiness: enabled for this DevCapsule launch.")
            elif arguments.no_recursive_e2e:
                print(
                    "Recursive E2E readiness: disabled for this launch; host Docker, "
                    "host networking, and development sudo were downgraded."
                )
            else:
                print(
                    "Recursive E2E readiness: unavailable because host Docker access is not authorized."
                )
        docker_options = list(arguments.docker_options)
        if docker_options:
            # Single-instance options the launcher composes are refused —
            # docker would keep the passthrough occurrence and silently
            # override the resolved plan. Everything else is deliberate
            # stepping outside the plan; show exactly what is being handed
            # to docker, once, conspicuously.
            reject_launcher_owned_docker_options(docker_options)
            print(
                "WARNING: passing raw docker run options outside the resolved plan: "
                + " ".join(docker_options),
                file=sys.stderr,
            )
        # PyCharm still travels through the launcher's named state fields;
        # every other surface's state comes from its runtime-plan slots.
        # Migrating PyCharm onto the generic slot path is a recorded follow-up.
        interactive_state_mounts: dict[str, tuple[Path, str]] = {}
        pycharm_state = {
            name: Path(state[f"pycharm/{name}"]) if f"pycharm/{name}" in state else None
            for name in ("config", "plugins", "system", "log", "cache")
        }
        if component != "pycharm":
            if checkout_runtime_plan is None:
                raise ProjectConfigurationError(
                    f"The {component} surface requires lock formation inputs; "
                    "regenerate the lock with 'devcapsule project init'."
                )
            pycharm_state = dict.fromkeys(pycharm_state)
            interactive_state_mounts = _component_state_mounts(
                root,
                lock,
                state,
                checkout_runtime_plan,
                {checkout_runtime_plan.component.id},
            )
        exit_code = run_pycharm(
            PycharmRunOptions(
                project=root,
                project_mount=str(runtime["project-mount"]),
                image=image,
                name=arguments.container_name,
                persistent_home=Path(state["home"]) if "home" in state else None,
                ide_config=pycharm_state["config"],
                plugins=pycharm_state["plugins"],
                ide_system=pycharm_state["system"],
                ide_log=pycharm_state["log"],
                tool_cache=pycharm_state["cache"],
                interactive_state_mounts=interactive_state_mounts,
                docker_mode=DockerMode.host if selected_docker_daemon == "host-socket" else DockerMode.none,
                enable_sudo=bool(selected_sudo),
                network_mode=selected_network,
                memory_limit_bytes=memory_limit,
                runtime_plan=checkout_runtime_plan,
                use_image_process=use_image_process,
                additional_state_mounts=_component_state_mounts(
                    root,
                    lock,
                    state,
                    checkout_runtime_plan,
                    set()
                    if checkout_runtime_plan is None
                    else {item.id for item in checkout_runtime_plan.ancillary_components},
                ),
                additional_environment=recursive_environment,
                secret_environment=tuple(sorted(secret_environment.values())),
                extra_docker_args=["--pull=never", *docker_options],
                project_state=None,
                enable_host_browser=selected_host_browser,
            )
        )
        if exit_code == 0:
            # D-0008: a zero exit proves this configuration; record it as a
            # known-good generation unless identical content already exists.
            # Recording failure must never fail the successful run.
            try:
                recorded = record_known_good_configuration(
                    manifest, input_path, output_path
                )
            except OSError as exc:
                print(
                    f"Warning: could not record the known-good configuration: {exc}",
                    file=sys.stderr,
                )
            else:
                if recorded is not None:
                    print(f"Recorded known-good configuration: {recorded}")
        return exit_code


def _run_once_answers(
    arguments: argparse.Namespace,
    manifest: dict[str, Any],
    lock: dict[str, Any],
) -> tuple[dict[str, Any], int | None]:
    """Validate run-once --authorize/--set answers and derive their launch effects.

    Run-once answers use the same node names and value spellings as the
    persistent config family, are applied to this launch only, and are never
    written anywhere.  Each accepted answer is echoed conspicuously, because a
    run-once choice is a deliberate deviation from the recorded resolution.
    """

    overrides: dict[str, Any] = {}
    memory_override: int | None = None
    for answer in carrier_answers(arguments, families=("set", "authorize")):
        if answer.justification is not None:
            raise ProjectConfigurationError(
                "A justification is recorded when the project owner authors the recommendation "
                "at 'devcapsule project init'; it does not apply to a run-once answer."
            )
        if answer.family == "authorize":
            declarations = authorization_declarations(manifest, lock)
            declaration = declarations.get(answer.name)
            if declaration is None or answer.name not in _RUN_ONCE_AUTHORIZATIONS:
                available = ", ".join(
                    name for name in _RUN_ONCE_AUTHORIZATIONS if name in declarations
                )
                raise ProjectConfigurationError(
                    f"Authorization {answer.name!r} cannot be answered run-once; "
                    f"run-once authorizations: {available}."
                )
            overrides[answer.name] = normalize_authorization_value(declaration, answer.value)
            print(
                f"Run-once authorization: {answer.name} = {answer.value}", file=sys.stderr
            )
        else:
            normalized = normalize_configuration_value(manifest, answer.name, answer.value)
            declaration_metadata = configuration_value_declarations(manifest)[answer.name]
            if declaration_metadata.get("runtime-effect") != "docker.memory-limit":
                raise ProjectConfigurationError(
                    f"Configuration value {answer.name!r} has no run-once launch effect; "
                    "record it persistently with 'devcapsule project config set'."
                )
            memory_override = memory_size_bytes(str(normalized))
            print(f"Run-once value: {answer.name} = {normalized}", file=sys.stderr)
    return overrides, memory_override


class ProjectRunImageCommand(Command):
    name = "run-image"
    help = (
        "Run a local PyCharm-compatible image without project lock resolution. "
        "Everything after '--' is handed verbatim to 'docker run'."
    )
    passthrough_dest = "docker_options"
    passthrough_metavar = "DOCKER-RUN-OPTIONS"

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("image")
        parser.add_argument("--project-mount", help="Absolute in-container project path.")
        parser.add_argument("--home", type=Path)
        parser.add_argument("--global-settings", type=Path)
        parser.add_argument("--plugins", type=Path)
        parser.add_argument("--project-state", type=Path)
        parser.add_argument(
            "--docker-daemon", choices=["none", "host-socket"], default="none"
        )
        parser.add_argument("--development-sudo", action="store_true")
        parser.add_argument(
            "--host-browser",
            action=argparse.BooleanOptionalAction,
            default=False,
            help="Explicitly allow HTTP(S) links to open in the physical host's default browser.",
        )
        parser.add_argument("--name", dest="container_name")

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        candidate = _project_context(context).start_path()
        try:
            project = discover_project(candidate)
        except ProjectConfigurationError:
            project = candidate.expanduser().resolve()
        if not project.is_dir():
            raise ProjectConfigurationError(f"Project directory does not exist: {project}")
        docker_mode = (
            DockerMode.host if arguments.docker_daemon == "host-socket" else DockerMode.none
        )
        docker_options = list(arguments.docker_options)
        if docker_options:
            reject_launcher_owned_docker_options(docker_options)
            print(
                "WARNING: passing raw docker run options: " + " ".join(docker_options),
                file=sys.stderr,
            )
        return run_pycharm(
            PycharmRunOptions(
                project=project,
                project_mount=arguments.project_mount,
                image=arguments.image,
                name=arguments.container_name,
                persistent_home=arguments.home,
                global_settings=arguments.global_settings,
                project_state=arguments.project_state,
                plugins=arguments.plugins,
                docker_mode=docker_mode,
                enable_sudo=arguments.development_sudo,
                enable_host_browser=arguments.host_browser,
                extra_docker_args=["--pull=never", *docker_options],
            )
        )


class ProjectCommand(Group):
    name = "project"
    help = "Initialize, list, configure, and run DevCapsule project checkouts."

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--path",
            dest="selected_path",
            type=Path,
            help="Project root or descendant; defaults to discovery from the current directory.",
        )

    @classmethod
    def make_context(cls, arguments: argparse.Namespace, parent: object | None) -> object | None:
        return ProjectCommandContext(arguments.selected_path)

    @classmethod
    def subcommands(cls) -> Mapping[str, type[Command] | type[Group]]:
        return {
            ProjectListCommand.name: ProjectListCommand,
            ProjectInitCommand.name: ProjectInitCommand,
            CheckoutGroup.name: CheckoutGroup,
            ConfigGroup.name: ConfigGroup,
            StateGroup.name: StateGroup,
            RecursiveE2EGroup.name: RecursiveE2EGroup,
            ProjectRunCommand.name: ProjectRunCommand,
            ProjectRunImageCommand.name: ProjectRunImageCommand,
        }


def _recursive_project_root(context: ProjectCommandContext) -> Path:
    root = discover_project(context.start_path())
    try:
        return require_recursive_e2e_project(root)
    except PreflightError as exc:
        raise ProjectConfigurationError(str(exc)) from exc


def _warn_for_host_path_disclosure(show_host_paths: bool) -> None:
    if show_host_paths:
        print(
            "WARNING: debug output includes raw host filesystem mappings; "
            "do not share it unsanitized.",
            file=sys.stderr,
        )


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


def _component_secret_rows(
    lock: dict[str, Any], checkout: dict[str, Any]
) -> list[ConfigurationListRow]:
    declarations = component_secret_inputs(lock)
    try:
        bindings = resolve_secret_bindings(lock, checkout)
    except ProjectConfigurationError as exc:
        return [ConfigurationListRow("secret", "*", "invalid", str(exc))]
    rows: list[ConfigurationListRow] = []
    for name, declaration in sorted(declarations.items()):
        source = bindings.get(name)
        if source is None:
            status = "missing-required" if declaration.required else "optional-unbound"
        else:
            status = "bound" if source in os.environ else "bound-unavailable"
        rows.append(
            ConfigurationListRow(
                "secret",
                name,
                status,
                f"{declaration.environment_variable} ({declaration.exposure})",
            )
        )
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
        recommended = _authorization_display_value(declaration)
        record = authorization.get(name)
        if record is None:
            if name == "base-image":
                status = "missing-required"
            elif declaration.project_recommended:
                status = "missing-recommended"
            else:
                # A workstation capability nobody asked for yet: available to
                # authorize, not a gap the project expects filled.
                status = "available"
            rows.append(ConfigurationListRow("authorization", name, status, recommended))
            continue
        if not isinstance(record, dict):
            rows.append(ConfigurationListRow("authorization", name, "invalid", recommended))
            continue
        if name == "base-image":
            try:
                selection = authorized_base_selection(
                    lock,
                    {"authorization": {"base-image": record}},
                )
            except ProjectConfigurationError:
                digest = record.get("lock-digest")
                status = "stale" if digest != declaration.recommendation_digest else "invalid"
                value = str(record.get("reference", recommended))
            else:
                if selection is None:  # pragma: no cover - record establishes it.
                    status = "invalid"
                    value = recommended
                else:
                    status = "authorized-local" if selection.is_local else "authorized"
                    value = selection.reference
                    if selection.local_image_identity is not None:
                        value += f" ({selection.local_image_identity[:19]}...)"
            rows.append(ConfigurationListRow("authorization", name, status, value))
            continue
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
    if not isinstance(resolved.get("sources", {}), dict):
        return ConfigurationListRow("resolution", "generated", "invalid", "sources is not a table")
    stale = stale_resolution_inputs(manifest, lock, checkout, resolved)
    if stale:
        return ConfigurationListRow("resolution", "generated", "stale", ", ".join(stale))
    return ConfigurationListRow("resolution", "generated", "fresh", str(resolution_path))


def _print_configuration_rows(rows: list[ConfigurationListRow]) -> None:
    headers = ("KIND", "NAME", "STATUS", "VALUE / RECOMMENDATION")
    values = [(row.kind, row.name, row.status, row.value) for row in rows]
    widths = [max(len(headers[index]), *(len(row[index]) for row in values)) for index in range(4)]
    print("")
    print("  ".join(header.ljust(widths[index]) for index, header in enumerate(headers)))
    for row in values:
        print("  ".join(value.ljust(widths[index]) for index, value in enumerate(row)))


def _authorize_all_recommended(
    root: Path,
    manifest: dict[str, Any],
    declarations: dict[str, AuthorizationDeclaration],
) -> int:
    # Bulk authorization covers what the project and lock actually recommend;
    # workstation-capability defaults are individual decisions and must never
    # ride along in an "authorize everything recommended" stroke.
    declarations = {
        name: declaration
        for name, declaration in declarations.items()
        if declaration.project_recommended
    }
    if not declarations:
        raise ProjectConfigurationError("This project and lock declare no authorization recommendations.")

    record = CheckoutRecord(manifest, root)
    input_path = record.input_path

    print(f"The following authorizations will be granted for checkout {root}:")
    for name, declaration in sorted(declarations.items()):
        rendered = _authorization_display_value(declaration)
        print(f"- {name}: {rendered}")
        print(f"  Justification: {declaration.description}")
        print(f"  Recommendation digest: {declaration.recommendation_digest}")
    if not sys.stdin.isatty():
        raise ProjectConfigurationError(
            "--all-recommended requires an interactive terminal; authorize each exact value "
            "individually in non-interactive workflows."
        )
    print("Press y to authorize every recommendation; any other key cancels: ", end="", flush=True)
    try:
        accepted = _confirmation_key() == "y"
    except (EOFError, OSError, termios.error) as exc:
        print("")
        raise ProjectConfigurationError(f"Cannot read authorization confirmation key: {exc}") from exc
    print("")
    if not accepted:
        print("Authorization cancelled; no changes written.")
        return 1

    for name, declaration in declarations.items():
        if name == "base-image":
            record.authorization[name] = {
                "reference": declaration.recommended_value,
                "lock-digest": declaration.recommendation_digest,
            }
        else:
            record.authorization[name] = {
                "value": declaration.recommended_value,
                "recommendation-digest": declaration.recommendation_digest,
            }
    record.write()
    print(f"Authorized {len(declarations)} recommendations for this checkout.")
    print(f"Checkout input: {input_path}")
    print("Run 'devcapsule project config resolve' before materialization or launch.")
    return 0


def _confirmation_key() -> str:
    """Read one raw keypress without echo or a newline.

    The bulk-authorization confirmation is deliberately a single keypress so
    a stray Enter in a paste cannot accept it; the interactive-terminal guard
    above runs first, so stdin is a tty here.
    """

    descriptor = sys.stdin.fileno()
    saved = termios.tcgetattr(descriptor)
    try:
        tty.setraw(descriptor)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(descriptor, termios.TCSADRAIN, saved)


def _authorization_display_value(declaration: AuthorizationDeclaration) -> str:
    return declaration.display_value or render_authorization_value(declaration.recommended_value)


def _component_state_mounts(
    root: Path,
    lock: dict[str, Any],
    configured_state: dict[str, Any],
    runtime_plan: Any,
    component_ids: set[str],
) -> dict[str, tuple[Path, str]]:
    if runtime_plan is None:
        return {}
    declarations = configuration_binding_declarations(lock)
    mounts: dict[str, tuple[Path, str]] = {}
    for name, declaration in declarations.items():
        if declaration.component_id not in component_ids:
            continue
        configured = configured_state.get(name)
        source = (
            Path(str(configured)).expanduser().resolve()
            if configured is not None
            else _managed_binding_path(root, declaration)
        )
        source.mkdir(parents=True, exist_ok=True, mode=0o700)
        if configured is None:
            source.chmod(0o700)
        mounts[name] = (source, declaration.container_path)
    return mounts


def _managed_binding_path(root: Path, declaration: Any) -> Path:
    home = Path(os.environ.get("HOME", "~")).expanduser()
    roots = {
        "durable": Path(os.environ.get("XDG_DATA_HOME") or home / ".local" / "share"),
        "state": Path(os.environ.get("XDG_STATE_HOME") or home / ".local" / "state"),
        "cache": Path(os.environ.get("XDG_CACHE_HOME") or home / ".cache"),
    }
    namespace = roots[declaration.kind] / "devcapsule" / "projects" / "by-path" / project_namespace(root)
    if declaration.name == "home":
        return namespace / "home"
    return namespace / "components" / str(declaration.component_id) / str(declaration.slot_name)


COMMAND = ProjectCommand
