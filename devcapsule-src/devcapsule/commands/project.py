"""Project and checkout command subtree.

Command classes here declare parameters and print operation reports; policy
and artifact writes live in :mod:`devcapsule.configuration.operations` and the
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
import getpass
import warnings
from dataclasses import dataclass, replace
import json
from pathlib import Path
import os
import subprocess
import sys
import termios
import shlex
from typing import Any, Callable, ClassVar, Mapping

from devcapsule.launch.command_output import preparation_diagnostics
from devcapsule.commands.framework import (
    STABLE_JSON_HELP,
    Command,
    Group,
    add_carrier_options,
    carrier_answers,
)
from devcapsule.components.catalog import COMPONENTS, INTERACTIVE_SURFACES
from devcapsule.commands._versions import VersionsGroup
from devcapsule.commands._upgrade_prompt import offer_upgrades
from devcapsule.commands._software_approvals import (
    SOFTWARE_APPROVALS_GUIDE_URL,
    approve as approve_software,
    approve_command as software_approve_command,
    confirmation_key as _confirmation_key,
    offer_software_approvals,
    pending_for as pending_software_approvals_for,
)
from devcapsule.configuration.approvals import render_software_approvals, select_software_approvals
from devcapsule import notifications
from devcapsule import version_sets
from devcapsule import runtime_configuration
from devcapsule.runtime_configuration import CapsuleAccess
from devcapsule.compat import CliError
from devcapsule.configuration.docker_arguments import (
    arguments_path, read_arguments, replace_arguments, read_environment, update_environment, validate_name,
)
from devcapsule.docker_arguments import redact_environment
from devcapsule.configuration.history import (
    record_known_good_configuration,
)
from devcapsule.launch.pycharm import (
    DockerMode,
    PycharmRunOptions,
    PycharmRunError,
    reject_launcher_owned_docker_options,
    run_pycharm,
)
from devcapsule.configuration.execution import (
    ExecutionConfiguration,
)
from devcapsule.configuration.review import (
    review_configuration,
)
from devcapsule.configuration.nodes import (
    CARRIER_FAMILY_BIND,
    CARRIER_FAMILY_SET,
    PROVIDER_HOST_DIRECTORY,
    build_node_registry,
)
from devcapsule.environment_realization import realize_environment, required_local_image, omit_unavailable_optional
from devcapsule.materialization import ArtifactUnavailable
from devcapsule.display_client import select_display_transport
from devcapsule.images.contract import WebConsoleAvailability, web_console_availability
from devcapsule.materialization import ImageDetails, validate_base_image
from devcapsule.project import project_namespace
from devcapsule.configuration.operations import (
    CheckoutRecord,
    InitializeRequest,
    ProvidedAnswer,
    apply_configuration_answers,
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
    SuccessorResult,
    launch_successor,
)
from devcapsule.resolution_matrix import compatibility_report, known_base_image
from devcapsule.configuration.authorization import (
    AuthorizationChoice,
    AuthorizationDeclaration,
    authorization_declarations,
    immutable_registry_reference,
    normalize_authorization_value,
    render_authorization_value,
    review_authorizations,
)
from devcapsule.configuration.file_formats import (
    ProjectConfigurationError,
    render_checkout,
    render_toml_scalar,
)
from devcapsule.configuration.storage import (
    atomic_write,
    checkout_name_for,
    checkout_record_paths,
    config_root,
    discover_project,
    find_checkout_record,
    load_checkout,
    load_resolution,
    lock_for,
    manifest_for,
    named_checkout_record_paths,
    registered_checkouts,
)
from devcapsule.configuration.bindings import (
    configuration_binding_declarations,
    managed_binding_path as _managed_binding_path,
    component_secret_inputs,
    resolve_secret_bindings,
)
from devcapsule.configuration.values import (
    configuration_value_declarations,
    memory_size_bytes,
    normalize_configuration_value,
)
from devcapsule.configuration.freshness import (
    stale_resolution_inputs,
)


@dataclass(frozen=True)
class ProjectCommandContext:
    """What the ``project`` group selected for its subcommand.

    ``selected_path`` is the user's ``--path``; it always wins.
    ``capsule_root`` is the capsule's own project, set by the group when no
    ``--path`` was given, no project encloses the working directory, and the
    subcommand's :class:`CapsuleAccess` selects it; otherwise ``None``.
    """

    selected_path: Path | None
    capsule_root: Path | None = None

    def start_path(self) -> Path:
        return self.selected_path or self.capsule_root or Path(".")

    def target_path(self) -> Path:
        return self.start_path().expanduser().resolve()


def _project_context(context: object | None) -> ProjectCommandContext:
    assert isinstance(context, ProjectCommandContext)
    return context


class ProjectInfoCommand(Command):
    name = "info"
    capsule_access: ClassVar[CapsuleAccess] = CapsuleAccess.INSPECTS
    help = "Show project software, environment and persistent storage without changing state."

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--json", action="store_true", help="Print the information as JSON.")

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        from devcapsule.project_information import project_information, render_information

        selected = _project_context(context)
        report = project_information(selected.start_path(), runtime_fallback=selected.selected_path is None)
        print(json.dumps(report, indent=2) if arguments.json else render_information(report))
        return 0


class ProjectListCommand(Command):
    name = "list"
    capsule_access: ClassVar[CapsuleAccess] = CapsuleAccess.INDEPENDENT
    help = "List developer-owned checkout records from the XDG registry."

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        # Without a supplied runtime context this is still the workstation's
        # registry enumeration, including in older/nested launcher capsules.
        runtime_context = (runtime_configuration.for_project(_project_context(context).start_path())
                           if runtime_configuration.CONTEXT_PATH.is_file() else None)
        if runtime_context is not None:
            identity = runtime_context.document["project"]
            print(f"Runtime project: {identity['creator']}/{identity['slug']}")
            print(f"Runtime checkout: {runtime_context.root}")
            print(f"Launcher checkout: {runtime_context.document['launcher-root']}")
            print("Only this capsule's checkout is selected here; list other checkouts through the launcher.")
            return 0
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
    capsule_access: ClassVar[CapsuleAccess] = CapsuleAccess.CREATES_HERE
    help = (
        "Initialize the project: the manifest with what it requires and offers, the platform "
        "lock, your own checkout record with your IDE and agents, and, once an IDE is chosen, "
        "a fresh resolution."
    )

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--require", action="append", default=[], metavar="TOOL[=MAJOR]",
            help="A tool every checkout must have, such as python or node; python=3 pins the SDK major. Repeatable.",
        )
        parser.add_argument(
            "--offer", action="append", default=[], metavar="TOOL",
            help="A tool the project offers and a developer may leave out, such as browser-automation. Repeatable.",
        )
        parser.add_argument("--ide", metavar="IDE", help="Your IDE for this checkout: python-ide, frontend-ide, java-ide, eclipse-ide or dotnet-ide.")
        parser.add_argument(
            "--agent", action="append", default=[], metavar="AGENT",
            help="A coding agent for this checkout: codex-agent, claude-code-agent or antigravity-agent. Repeatable.",
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
            help=argparse.SUPPRESS,
        )
        parser.add_argument(
            "--unverified",
            action="store_true",
            dest="allow_unverified",
            help=(
                "If no fully verified combination satisfies the requirements, resolve past "
                "the matrix with a gentle warning; the generated lock names every "
                "unverified combination."
            ),
        )
        # The spellings of 0.3.0 rc3 and earlier, accepted for one release and
        # mapped onto the ones above: --need and --local mixed the project's
        # tools with the developer's IDE and agents (deficiency 9 of the CLI UX
        # work order); --required, --optional and --sdk-major are --require and --offer.
        for legacy in ("--need", "--required", "--optional", "--local", "--sdk-major"):
            parser.add_argument(legacy, nargs="*", action="append", default=[], help=argparse.SUPPRESS)
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
        require, offer, ide, agents = _init_selection(arguments)
        report = initialize_project(
            InitializeRequest(
                directory=_project_context(context).target_path(),
                require=require,
                offer=offer,
                ide=ide,
                agents=agents,
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


def _init_selection(arguments: argparse.Namespace) -> tuple[tuple[str, ...], tuple[str, ...], str | None, tuple[str, ...]]:
    """The project's requirements and offers, and the owner's IDE and agents, legacy spellings mapped.

    ``--need`` and ``--local`` named IDEs and agents beside tools; here each
    name goes where it belongs, and the mapping is announced once on stderr.
    """
    from devcapsule.platforms import Platform
    from devcapsule.resolution_matrix import MATRICES
    matrix = MATRICES[Platform.current()]
    surfaces = {name for name in matrix.local_capabilities() if not name.endswith("-agent")}
    agent_names = matrix.local_capabilities() - surfaces
    require = list(arguments.require)
    offer = list(arguments.offer)
    ide = arguments.ide
    agents = list(arguments.agent)
    legacy_used: list[str] = []

    def flatten(flag: str) -> list[str]:
        values = [item for group in getattr(arguments, flag.lstrip("-").replace("-", "_")) for item in group]
        if getattr(arguments, flag.lstrip("-").replace("-", "_")):
            legacy_used.append(flag)
        return values

    for name in (*flatten("--need"), *flatten("--local")):
        if name in surfaces:
            if ide is not None and ide != name:
                raise ProjectConfigurationError(f"Two IDEs named, {ide} and {name}; a checkout has one IDE.")
            ide = name
        elif name in agent_names:
            agents.append(name)
        else:
            require.append(name)
    require.extend(flatten("--required"))
    offer.extend(flatten("--optional"))
    require.extend(flatten("--sdk-major"))
    if legacy_used:
        print(
            "Note: " + ", ".join(legacy_used) + " are the spellings of 0.3.0 rc3; use --require, --offer, "
            "--ide and --agent. The IDE and the agents are your checkout's, the tools are the project's.",
            file=sys.stderr,
        )
    return tuple(require), tuple(offer), ide, tuple(dict.fromkeys(agents))


class CheckoutRegisterCommand(Command):
    name = "register"
    capsule_access: ClassVar[CapsuleAccess] = CapsuleAccess.MUTATES
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


def _notification_store(context: object | None) -> "notifications.NotificationStore":
    """The checkout's store: its own state inside a capsule, its persistent home from the host."""
    selected = _project_context(context)
    try:
        return notifications.store_for(selected.selected_path)
    except (ProjectConfigurationError, OSError) as error:
        raise ProjectConfigurationError(f"Cannot locate this checkout's notifications: {error}") from error


def _render_notification_listing(document: dict[str, Any]) -> str:
    """The human form of the listing: one line per entry, a star marking unread."""
    entries = document["notifications"]
    if not entries:
        return f"No notifications under {document['directory']}.\n"
    lines = []
    for entry in entries:
        if "error" in entry:
            lines.append(f"  ! {entry['id']}: {entry['error']}")
            continue
        mark = "*" if entry["read-at"] is None else " "
        link = f"  {entry['link']}" if entry["link"] else ""
        lines.append(f"{mark} {entry['posted-at']}  {entry['kind']:<10}  {entry['id']}  {entry['title']}{link}")
    return f"{document['unread']} unread of {len(entries)}; * marks unread.\n" + "\n".join(lines) + "\n"


class NotificationsListCommand(Command):
    name = "list"
    capsule_access: ClassVar[CapsuleAccess] = CapsuleAccess.INDEPENDENT
    help = "List this checkout's notifications and its unanswered decisions, newest first."

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--unread", action="store_true", help="Only the entries not yet read.")
        parser.add_argument("--json", dest="as_json", action="store_true", help=STABLE_JSON_HELP)

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        try:
            document = notifications.listing_document(_notification_store(context), unread_only=arguments.unread)
        except notifications.NotificationError as error:
            raise ProjectConfigurationError(str(error)) from error
        print(json.dumps(document, indent=2, sort_keys=True) if arguments.as_json
              else _render_notification_listing(document), end="")
        return 0


class NotificationsPostCommand(Command):
    name = "post"
    capsule_access: ClassVar[CapsuleAccess] = CapsuleAccess.INDEPENDENT
    help = "Post a notification to this checkout's human; capsule state only, never a record."

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--kind", required=True, help="Lowercase letters, digits and hyphens; 'decision' is reserved.")
        parser.add_argument("--title", required=True)
        parser.add_argument("--summary", default="", help="Markdown shown under the title.")
        parser.add_argument("--link", default="", help="A web console path to open, such as /records/README.md.")
        parser.add_argument("--posted-by", dest="posted_by", default="", help="Who posts; default $USER or 'unknown'.")
        parser.add_argument("--json", dest="as_json", action="store_true", help=STABLE_JSON_HELP)

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        store = _notification_store(context)
        try:
            posted = store.post(kind=arguments.kind, title=arguments.title, summary=arguments.summary,
                                link=arguments.link, posted_by=arguments.posted_by or os.environ.get("USER") or "unknown")
        except notifications.NotificationError as error:
            raise ProjectConfigurationError(f"Cannot post the notification: {error}") from error
        print(json.dumps(posted.to_mapping(), indent=2, sort_keys=True) if arguments.as_json
              else f"Posted {posted.id}: {store.path(posted.id)}")
        return 0


class NotificationsReadCommand(Command):
    name = "read"
    capsule_access: ClassVar[CapsuleAccess] = CapsuleAccess.INDEPENDENT
    help = "Mark a notification read; a decision is read by answering it."

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("notification_id", metavar="ID")

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        try:
            read = _notification_store(context).mark_read(arguments.notification_id)
        except notifications.NotificationError as error:
            raise ProjectConfigurationError(str(error)) from error
        print(f"Read {read.id} at {read.read_at}")
        return 0


class NotificationsDismissCommand(Command):
    name = "dismiss"
    capsule_access: ClassVar[CapsuleAccess] = CapsuleAccess.INDEPENDENT
    help = "Remove a notification; a decision is removed by the agent that asked it."

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("notification_id", metavar="ID")

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        try:
            _notification_store(context).dismiss(arguments.notification_id)
        except notifications.NotificationError as error:
            raise ProjectConfigurationError(str(error)) from error
        print(f"Dismissed {arguments.notification_id}")
        return 0


class NotificationsGroup(Group):
    name = "notifications"
    help = "What this checkout's environment tells its human: list, post, read, dismiss."

    @classmethod
    def subcommands(cls) -> Mapping[str, type[Command] | type[Group]]:
        return {
            NotificationsListCommand.name: NotificationsListCommand,
            NotificationsPostCommand.name: NotificationsPostCommand,
            NotificationsReadCommand.name: NotificationsReadCommand,
            NotificationsDismissCommand.name: NotificationsDismissCommand,
        }


class CheckoutDecisionsCommand(Command):
    """``project checkout decisions ...``: the web console's decision tools, from one CLI.

    The decision document is the console's contract (``DECISIONS.md`` in
    its source), and the tools that build, check and hand off one live in
    the console's package, which is not in the runtime PEX by the work
    order's binding decision. Inside a capsule the console is installed in
    the base, or mounted from the checkout under the self-hosting
    exception; this command runs that module, so an agent sees one CLI.
    Outside a capsule it says where the module is.
    """

    name = "decisions"
    capsule_access: ClassVar[CapsuleAccess] = CapsuleAccess.INDEPENDENT
    help = "Build, check or hand off a decision document with the capsule's web console tools."

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("arguments", nargs=argparse.REMAINDER, metavar="SUBCOMMAND ...",
                            help="from-table, check or hand-off with their arguments, as "
                                 "`python -m devcapsule_webconsole.decisions` takes them.")

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        from devcapsule.console_tools import console_decisions_command

        command = console_decisions_command(arguments.arguments)
        try:
            return subprocess.run(command, check=False).returncode
        except OSError as error:
            raise CliError(f"cannot run the console's decision tools: {error}") from error


class CheckoutGroup(Group):
    name = "checkout"
    help = "This local checkout: register its name, its notifications, its decisions."

    @classmethod
    def subcommands(cls) -> Mapping[str, type[Command] | type[Group]]:
        return {
            CheckoutRegisterCommand.name: CheckoutRegisterCommand,
            NotificationsGroup.name: NotificationsGroup,
            CheckoutDecisionsCommand.name: CheckoutDecisionsCommand,
        }


class ConfigResolveCommand(Command):
    name = "resolve"
    capsule_access: ClassVar[CapsuleAccess] = CapsuleAccess.MUTATES
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
    # Which document the row's status and value come from, named by the
    # tokens the Sources block of `config show` expands to paths: checkout,
    # manifest, lock, resolution, managed, environment.
    source: str


CONFIGURATION_LISTING_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class ConfigurationListing:
    """What `config list` printed, for `config show` to explain further."""

    root: Path
    manifest: dict[str, Any]
    manifest_path: Path
    lock: dict[str, Any]
    lock_path: Path
    checkout: dict[str, Any]
    input_path: Path
    resolution_path: Path
    resolution_row: ConfigurationListRow
    rows: list[ConfigurationListRow]
    """Every row of the table, the resolution row last."""

    @property
    def checkout_name(self) -> str:
        return checkout_name_for(self.manifest, self.input_path)

    def render_identity(self) -> str:
        identity = self.manifest["project"]
        return "\n".join([
            f"Project: {identity['creator']}/{identity['slug']}",
            f"Checkout: {self.root}",
            f"Checkout name: {self.checkout_name}",
            f"Checkout input: {self.input_path}",
            f"Generated plan: {self.resolution_path}",
        ])

    def to_document(self) -> dict[str, Any]:
        """The listing as the stable ``config list --json`` document.

        Schema version 1: ``context`` names the host selection; ``rows`` are
        the table's rows with the table's columns as keys. Adding a key keeps
        the version; renaming, removing or retyping one bumps it.
        """
        identity = self.manifest["project"]
        return {
            "schema-version": CONFIGURATION_LISTING_SCHEMA_VERSION,
            "context": "host selection (next launch)",
            "project": {"creator": identity["creator"], "slug": identity["slug"]},
            "checkout": {"name": self.checkout_name, "launcher-path": str(self.root),
                         "input": str(self.input_path), "resolution": str(self.resolution_path)},
            "rows": [{"kind": row.kind, "name": row.name, "status": row.status,
                      "source": row.source, "value": row.value} for row in self.rows],
        }

    def render_base(self) -> str:
        """Name the base by its contract, say who built it and where the recipe
        is, and say which locked components are validated for it and why."""
        reference = self.lock.get("base", {}).get("reference")
        image = known_base_image(str(reference)) if reference else None
        lines = ["Base:"]
        if image is None:
            lines.append(f"  {reference}: not pinned by this DevCapsule's matrix.")
        else:
            lines.append(f"  {image.contract.describe()}")
            lines.append(f"  at {image.reference}")
            lines.append(f"  {image.built.describe()}")
        lines.extend(f"  {line}" for line in compatibility_report(self.lock))
        return "\n".join(lines)

    def render_sources(self) -> str:
        """Name every document behind the listing and whether the generated
        resolution still reflects it. The tokens match the SOURCE column."""
        resolved = load_resolution(self.resolution_path) if self.resolution_path.is_file() else {}
        drifted = (
            set(stale_resolution_inputs(self.manifest, self.lock, self.checkout, resolved))
            if resolved.get("status") != "unresolved" and resolved else set()
        )
        def note(key: str) -> str:
            if not resolved or resolved.get("status") == "unresolved":
                return "not yet resolved"
            return "changed since the resolution" if key in drifted else "as resolved"
        lines = [
            "Sources:",
            f"  manifest     {self.manifest_path}  ({note('manifest')})",
            f"  lock         {self.lock_path}  ({note('platform-lock')})",
            f"  checkout     {self.input_path}  ({note('checkout-input')})",
            "  workstation  absent (no workstation-level configuration exists yet)",
            f"  resolution   {self.resolution_path}  (generated: {self.resolution_row.status})",
            "  managed      DevCapsule-owned state directories under the XDG data home",
            "  environment  the launching shell's environment variables",
        ]
        return "\n".join(lines)


def _load_configuration_listing(
    context: object | None, *, notice: Callable[[str], None] = print
) -> ConfigurationListing | runtime_configuration.RuntimeConfiguration:
    """Load the documents behind ``config list`` and build its table.

    Inside a capsule the mounted runtime configuration is the whole listing
    and is returned as such. Outside, a missing checkout input or resolution
    placeholder is materialized first and reported through ``notice``, so a
    JSON caller can keep its standard output to the document alone.
    """
    runtime_context = runtime_configuration.for_project(_project_context(context).start_path())
    if runtime_context is not None:
        return runtime_context
    root, manifest = manifest_for(_project_context(context).start_path())
    lock_path, lock = lock_for(root, manifest)
    input_path, resolution_path = checkout_record_paths(manifest, root)
    if not input_path.is_file():
        atomic_write(input_path, render_checkout(manifest, root, {}, {}))
        notice(f"Initialized checkout input: {input_path}")
    if not resolution_path.is_file():
        atomic_write(
            resolution_path,
            'devcapsule-resolved-schema-version = 1\nstatus = "unresolved"\n',
        )
        notice(f"Initialized resolution placeholder: {resolution_path}")
    checkout = load_checkout(input_path, manifest, root)
    resolution_row = _configuration_resolution_row(manifest, lock, checkout, resolution_path)
    rows = [
        *_configuration_value_rows(manifest, checkout),
        *_configuration_binding_rows(lock, checkout),
        *_component_secret_rows(lock, checkout),
        *_configuration_authorization_rows(manifest, lock, checkout),
        resolution_row,
    ]
    return ConfigurationListing(
        root, manifest, root / ".devcapsule" / "devcapsule.toml", lock, lock_path,
        checkout, input_path, resolution_path, resolution_row, rows,
    )


def _print_configuration_listing(context: object | None) -> ConfigurationListing | None:
    """Print the checkout identity and the configuration table.

    Returns the loaded documents and the rows for a caller that adds the
    review, or ``None`` inside a capsule, where the runtime report is the
    whole listing. The table is data: every declared value, binding, secret
    input and authorization with its recorded status, and the generated
    resolution's state. Advice belongs to ``config show``.
    """
    loaded = _load_configuration_listing(context)
    if isinstance(loaded, runtime_configuration.RuntimeConfiguration):
        print(loaded.configuration_report())
        return None
    print(loaded.render_identity())
    _print_configuration_rows(loaded.rows)
    return loaded


class ConfigListCommand(Command):
    name = "list"
    capsule_access: ClassVar[CapsuleAccess] = CapsuleAccess.INSPECTS
    help = "List configured values, bindings, authorizations, and the resolution state; data only."

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--json", dest="as_json", action="store_true", help=STABLE_JSON_HELP)

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        if not arguments.as_json:
            _print_configuration_listing(context)
            return 0
        loaded = _load_configuration_listing(context, notice=lambda line: print(line, file=sys.stderr))
        document = (loaded.configuration_document() if isinstance(loaded, runtime_configuration.RuntimeConfiguration)
                    else loaded.to_document())
        print(json.dumps(document, indent=2, sort_keys=True))
        return 0


class ConfigShowCommand(Command):
    name = "show"
    capsule_access: ClassVar[CapsuleAccess] = CapsuleAccess.INSPECTS
    help = "Show the listing, the documents every row comes from, and the review: decisions, remedies, and whether to resolve."

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        listing = _print_configuration_listing(context)
        if listing is None:
            return 0
        row = listing.resolution_row
        resolution = f"stale: {row.value}" if row.status == "stale" else row.status
        print("")
        print(listing.render_sources())
        print("")
        print(listing.render_base())
        print("")
        print(review_configuration(listing.manifest, listing.lock, listing.checkout).render(
            listing.root, resolution=resolution))
        return 0


class ConfigSetCommand(Command):
    name = "set"
    capsule_access: ClassVar[CapsuleAccess] = CapsuleAccess.MUTATES
    help = "Set one ordinary value declared by the project configuration metadata."

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("node_name", metavar="NAME")
        parser.add_argument("value", metavar="VALUE")

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        name = arguments.node_name
        root, manifest = manifest_for(_project_context(context).start_path())
        _lock_path, lock = lock_for(root, manifest)
        build_node_registry(manifest, lock).answerable(name, CARRIER_FAMILY_SET)
        record = CheckoutRecord(manifest, root)
        apply_configuration_answers((ProvidedAnswer("set", name, arguments.value),), manifest, lock, record)
        record.write()
        if name in record.omitted_values:
            print(f"Set {name} = none (explicitly absent from the runtime configuration)")
        else:
            print(f"Set {name} = {render_toml_scalar(record.values[name])}")
        print(f"Checkout input: {record.input_path}")
        print("Run 'devcapsule project config resolve' before launch.")
        return 0


def _managed_arguments_path(context: object | None) -> Path:
    """The saved arguments of the registered checkout record for this project.

    The record is located, never loaded: the saved-argument commands edit no
    checkout record, so they must not recover an interrupted activation either.
    """
    root, manifest = manifest_for(_project_context(context).start_path())
    input_path, _resolution_path = checkout_record_paths(manifest, root)
    if not input_path.is_file():
        raise ProjectConfigurationError("Initialize or register this checkout before setting its environment.")
    return arguments_path(input_path)


class ConfigSetEnvCommand(Command):
    name = "set-env"
    capsule_access: ClassVar[CapsuleAccess] = CapsuleAccess.MUTATES
    help = "Save a checkout environment variable; omit VALUE for a hidden terminal prompt."

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("key", metavar="KEY")
        parser.add_argument("value", metavar="VALUE", nargs="?")

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        path = _managed_arguments_path(context)
        validate_name(arguments.key)
        value = arguments.value
        if value is None:
            if not sys.stdin.isatty():
                raise ProjectConfigurationError("A terminal is required for the hidden value prompt.")
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("error", getpass.GetPassWarning)
                    value = getpass.getpass("Value: ")
            except (getpass.GetPassWarning, EOFError):
                raise ProjectConfigurationError("Cannot read a hidden value from this terminal.") from None
        update_environment(path, arguments.key, value)
        print(f"Saved {arguments.key}. Run 'devcapsule project run' to use it in a new container.")
        return 0


class ConfigUnsetEnvCommand(Command):
    name = "unset-env"
    capsule_access: ClassVar[CapsuleAccess] = CapsuleAccess.MUTATES
    help = "Remove a saved checkout environment variable."

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("key", metavar="KEY")

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        update_environment(_managed_arguments_path(context), arguments.key, None)
        print(f"Removed {arguments.key} from the saved environment. Existing containers are unchanged.")
        return 0


class ConfigListEnvCommand(Command):
    name = "list-env"
    # Host-owned file is deliberately not mounted into the running capsule.
    capsule_access: ClassVar[CapsuleAccess] = CapsuleAccess.MUTATES
    help = "List saved environment names on the launcher host, never their values."

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--json", dest="as_json", action="store_true", help=STABLE_JSON_HELP)

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        path = _managed_arguments_path(context)
        names = sorted(read_environment(path))
        if arguments.as_json:
            print(json.dumps({"path": str(path), "names": names}, sort_keys=True))
        else:
            print(f"Docker arguments file: {path}")
            print("\n".join(names) if names else "No saved environment variables.")
        return 0


class ConfigSetExtraDockerArgsCommand(Command):
    name = "set-extra-docker-args"
    capsule_access: ClassVar[CapsuleAccess] = CapsuleAccess.MUTATES
    help = "Replace the saved Docker argument list with the tokens after '--'."
    passthrough_dest = "docker_options"
    passthrough_metavar = "DOCKER-RUN-OPTIONS"

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        options = list(arguments.docker_options)
        if not options:
            raise ProjectConfigurationError("Supply Docker arguments after '--', or use remove-extra-docker-args.")
        _validate_extra_docker_args(options)
        replace_arguments(_managed_arguments_path(context), options)
        print("Saved extra Docker arguments. They apply to new containers started by 'project run'.")
        return 0


class ConfigListExtraDockerArgsCommand(Command):
    name = "list-extra-docker-args"
    capsule_access: ClassVar[CapsuleAccess] = CapsuleAccess.MUTATES
    help = "List saved Docker arguments with inline environment values masked."

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--json", dest="as_json", action="store_true", help=STABLE_JSON_HELP)

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        path = _managed_arguments_path(context)
        options = redact_environment(read_arguments(path))
        if arguments.as_json:
            print(json.dumps({"path": str(path), "arguments": options}, sort_keys=True))
        else:
            print(f"Docker arguments file: {path}")
            print(shlex.join(options) if options else "No saved extra Docker arguments.")
        return 0


class ConfigRemoveExtraDockerArgsCommand(Command):
    name = "remove-extra-docker-args"
    capsule_access: ClassVar[CapsuleAccess] = CapsuleAccess.MUTATES
    help = "Clear the complete saved Docker argument list, including saved environment options."

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        replace_arguments(_managed_arguments_path(context), [])
        print("Removed saved extra Docker arguments. Existing containers are unchanged.")
        return 0


def _validate_extra_docker_args(options: list[str]) -> None:
    try:
        reject_launcher_owned_docker_options(options)
    except PycharmRunError as exc:
        raise ProjectConfigurationError(str(exc)) from exc


class ConfigBindCommand(Command):
    name = "bind"
    capsule_access: ClassVar[CapsuleAccess] = CapsuleAccess.MUTATES
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
        apply_configuration_answers((ProvidedAnswer("bind", name, arguments.value),), manifest, lock, record)
        record.write()
        if provider == PROVIDER_HOST_DIRECTORY:
            source = Path(record.directory_bindings[name])
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
            print(
                f"WARNING: {raw_value} will be visible to every process in the capsule "
                "and through Docker container inspection while it runs.",
                file=sys.stderr,
            )
            print(f"Bound {name} to host environment variable: {raw_value}")
        print(f"Checkout input: {record.input_path}")
        print("Run 'devcapsule project config resolve' before launch.")
        return 0


class ConfigApproveCommand(Command):
    name = "approve"
    capsule_access: ClassVar[CapsuleAccess] = CapsuleAccess.MUTATES
    help = (
        "Approve new versions of vendor software you approved before, after the project's "
        "lock changed; the vendors and their terms are unchanged. Lists what is pending; "
        "NAME... or --all records the approvals. The resolution is regenerated "
        "when no software approvals remain."
    )

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("names", metavar="NAME", nargs="*", help="an authorization name from the list")
        parser.add_argument("--all", action="store_true", help="approve every pending software update")

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        root, manifest = manifest_for(_project_context(context).start_path())
        if arguments.all and arguments.names:
            raise ProjectConfigurationError("--all cannot be combined with NAME.")
        approvals = pending_software_approvals_for(root, manifest)
        if approvals is None:
            raise ProjectConfigurationError(
                "The pending decisions are not all software approvals; review them one by one: "
                + shlex.join(["devcapsule", "project", "--path", str(root), "config", "resolve"])
            )
        if not approvals:
            print("No software approvals are pending for this checkout.")
            return 0
        for line in render_software_approvals(approvals):
            print(line)
        if not arguments.all and not arguments.names:
            print(f"Approve with: {software_approve_command(root)}, or name the ones to approve.")
            print(f"Software approvals: {SOFTWARE_APPROVALS_GUIDE_URL}")
            return 1
        selected = approvals if arguments.all else select_software_approvals(approvals, tuple(arguments.names))
        approve_software(root, manifest, selected)
        return 0


class ConfigUnsetCommand(Command):
    name = "unset"
    capsule_access: ClassVar[CapsuleAccess] = CapsuleAccess.MUTATES
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
            legacy = record.host.pop(name, None)
            removed = record.authorization.pop(name, legacy)
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
    capsule_access: ClassVar[CapsuleAccess] = CapsuleAccess.MUTATES
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
        record.authorize(declaration, normalized, local_base_identity)
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
            "This authorization applies to the exact recorded image, by digest or by local image "
            "identity, and stays valid while the lock recommends that image."
        )
        print("Run 'devcapsule project config resolve' before materialization or launch.")
        return 0


class _OwnerToolCommand(Command):
    """One owner verb over the project's tools: ``require``, ``offer`` or ``drop``."""

    name = "tool"
    capsule_access: ClassVar[CapsuleAccess] = CapsuleAccess.MUTATES
    verb: ClassVar[str] = ""
    help = ""

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("names", nargs="+", metavar="TOOL" if cls.verb == "drop" else "TOOL[=MAJOR]",
                            help="A tool capability such as python, node or browser-automation; python=3 pins an SDK major.")
        if cls.verb != "drop":
            parser.add_argument("--because", metavar="REASON", help="The reason a developer reads beside this tool.")
        parser.add_argument("--preview", action="store_true", help="Validate and show the result; write nothing.")
        parser.add_argument("--unverified", action="store_true", dest="allow_unverified",
                            help="Accept a combination the matrix has not validated; the lock records it.")

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        from devcapsule.configuration import owner_commands
        start = _project_context(context).start_path()
        if cls.verb == "drop":
            print(owner_commands.drop_tools(start, arguments.names, preview=arguments.preview,
                                            allow_unverified=arguments.allow_unverified))
        elif cls.verb == "require":
            print(owner_commands.require_tools(start, arguments.names, because=arguments.because,
                                               preview=arguments.preview, allow_unverified=arguments.allow_unverified))
        else:
            print(owner_commands.offer_tools(start, arguments.names, because=arguments.because,
                                             preview=arguments.preview, allow_unverified=arguments.allow_unverified))
        return 0


class _OwnerEnvironmentCommand(Command):
    """One owner verb over the environment the project asks of each developer."""

    name = "env"
    capsule_access: ClassVar[CapsuleAccess] = CapsuleAccess.MUTATES
    verb: ClassVar[str] = ""
    help = ""

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("names", nargs="+", metavar="NAME", help="An environment variable name such as POSTGRES_HOST.")
        if cls.verb != "drop":
            parser.add_argument("--because", metavar="REASON", help="The reason a developer reads when asked for the value.")
        parser.add_argument("--preview", action="store_true", help="Validate and show the result; write nothing.")

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        from devcapsule.configuration import owner_commands
        start = _project_context(context).start_path()
        if cls.verb == "drop":
            print(owner_commands.drop_environment(start, arguments.names, preview=arguments.preview))
        elif cls.verb == "require":
            print(owner_commands.require_environment(start, arguments.names, because=arguments.because, preview=arguments.preview))
        else:
            print(owner_commands.offer_environment(start, arguments.names, because=arguments.because, preview=arguments.preview))
        return 0


def _owner_group(verb: str, help_text: str, tool_help: str, env_help: str) -> type[Group]:
    tool = type(f"Config{verb.title()}ToolCommand", (_OwnerToolCommand,),
                {"verb": verb, "help": tool_help, "capsule_access": CapsuleAccess.MUTATES})
    env = type(f"Config{verb.title()}EnvCommand", (_OwnerEnvironmentCommand,),
               {"verb": verb, "help": env_help, "capsule_access": CapsuleAccess.MUTATES})

    class OwnerGroup(Group):
        name = verb
        help = help_text

        @classmethod
        def subcommands(cls) -> Mapping[str, type[Command] | type[Group]]:
            return {"tool": tool, "env": env}

    OwnerGroup.__name__ = f"Config{verb.title()}Group"
    return OwnerGroup


ConfigRequireGroup = _owner_group(
    "require", "Project owners: what every checkout must have.",
    "Require tools, regenerating the lock; TOOL=MAJOR pins an SDK major. IDE and agent choices stay each developer's.",
    "Require environment variables every developer supplies, privately, before the first launch.",
)
ConfigOfferGroup = _owner_group(
    "offer", "Project owners: what a developer may take or leave.",
    "Offer tools a developer may omit; the lock pins them.",
    "Offer environment variables a developer may supply.",
)
ConfigDropGroup = _owner_group(
    "drop", "Project owners: remove a requirement or an offer.",
    "Drop tools from the project's requirements and offers, with their SDK majors.",
    "Drop environment declarations from the project.",
)


class ConfigRecommendCommand(Command):
    name = "recommend"
    capsule_access: ClassVar[CapsuleAccess] = CapsuleAccess.MUTATES
    help = (
        "Project owners: recommend an IDE, a memory limit, a CPU count, or a host access "
        "(network host, docker-daemon host-socket, development-sudo true, host-browser true) with the reason; "
        "'none' removes the recommendation."
    )

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("recommendation", metavar="NAME", help="ide, memory, cpus, network, docker-daemon, development-sudo or host-browser.")
        parser.add_argument("value", metavar="VALUE", help="The recommended value, or none.")
        parser.add_argument("--because", metavar="REASON", help="The reason a developer reads; required for a host access.")
        parser.add_argument("--preview", action="store_true", help="Validate and show the result; write nothing.")

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        from devcapsule.configuration import owner_commands
        print(owner_commands.recommend(_project_context(context).start_path(), arguments.recommendation,
                                       arguments.value, because=arguments.because, preview=arguments.preview))
        return 0


class ConfigNeedCommand(Command):
    """The 0.3.0 rc3 spelling, kept for one release to name its replacement."""

    name = "need"
    hidden = True
    capsule_access: ClassVar[CapsuleAccess] = CapsuleAccess.MUTATES
    help = "Replaced by 'config require tool'; kept for one release to say so."

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("capabilities", nargs="*", metavar="CAPABILITY")
        parser.add_argument("--unverified", action="store_true", dest="allow_unverified")
        add_carrier_options(parser, families=("authorize",))

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        names = " ".join(arguments.capabilities) or "TOOL"
        raise ProjectConfigurationError(
            "'config need' is replaced: a project requires tools with "
            f"'devcapsule project config require tool {names}'; a developer chooses an IDE or an agent "
            "for their checkout with 'devcapsule project config capabilities --local NAME'."
        )


class ConfigCheckCommand(Command):
    name = "check"
    capsule_access: ClassVar[CapsuleAccess] = CapsuleAccess.INSPECTS
    help = "Validate the project capability contract, or candidate files, without writing or launching."

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--manifest", type=Path, help="Candidate manifest; defaults to the project's manifest.")
        parser.add_argument("--lock", type=Path, help="Candidate platform lock; defaults to this platform's lock.")

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        from devcapsule.configuration.capability_commands import check
        print(check(_project_context(context).start_path(), manifest_path=arguments.manifest, lock_path=arguments.lock))
        return 0


class ConfigCapabilitiesCommand(Command):
    name = "capabilities"
    capsule_access: ClassVar[CapsuleAccess] = CapsuleAccess.MUTATES
    help = "Replace this checkout's IDE, agent and extra-tool selection (--local) or its omissions (--without); validate before writing."

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        for legacy in ("--required", "--optional", "--sdk-major"):
            parser.add_argument(legacy, nargs="*", help=argparse.SUPPRESS)
        parser.add_argument("--local", nargs="*", metavar="CAPABILITY", help="Replace personal IDE/agent/extra-tool choices.")
        parser.add_argument("--without", nargs="*", metavar="CAPABILITY", help="Replace local omissions of project optional tools.")
        parser.add_argument("--preview", action="store_true", help="Validate and display the candidate; write nothing.")
        parser.add_argument("--unverified", action="store_true", help="Explicitly select an unverified combination.")
        parser.add_argument("--recover", action="store_true", help="Finish or undo an interrupted shared configuration edit.")

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        from devcapsule.configuration.capability_commands import configure, recover
        from devcapsule.configuration.storage import discover_project
        start = _project_context(context).start_path()
        if any(getattr(arguments, key) is not None for key in ("required", "optional", "sdk_major")):
            raise ProjectConfigurationError(
                "The project's tools are edited with 'devcapsule project config require tool TOOL[=MAJOR]', "
                "'config offer tool TOOL' and 'config drop tool TOOL'; 'capabilities' keeps the checkout's "
                "--local and --without choices."
            )
        if arguments.recover:
            if any(getattr(arguments, key) is not None for key in ("required", "optional", "sdk_major", "local", "without")) or arguments.preview or arguments.unverified:
                raise ProjectConfigurationError("--recover is a standalone operation.")
            root = start.expanduser().resolve()
            recover(root if (root / ".devcapsule/.capability-transaction.toml").exists() else discover_project(root))
            print("Configuration transaction recovered (or none pending).")
        else:
            print(configure(start, required=arguments.required, optional=arguments.optional,
                            majors=arguments.sdk_major, local=arguments.local, without=arguments.without,
                            preview=arguments.preview, allow_unverified=arguments.unverified))
        return 0


class ConfigGroup(Group):
    name = "config"
    help = "Inspect and resolve layered project configuration."

    @classmethod
    def subcommands(cls) -> Mapping[str, type[Command] | type[Group]]:
        return {
            ConfigListCommand.name: ConfigListCommand,
            ConfigCheckCommand.name: ConfigCheckCommand,
            ConfigCapabilitiesCommand.name: ConfigCapabilitiesCommand,
            ConfigShowCommand.name: ConfigShowCommand,
            ConfigResolveCommand.name: ConfigResolveCommand,
            ConfigRequireGroup.name: ConfigRequireGroup,
            ConfigOfferGroup.name: ConfigOfferGroup,
            ConfigDropGroup.name: ConfigDropGroup,
            ConfigRecommendCommand.name: ConfigRecommendCommand,
            ConfigNeedCommand.name: ConfigNeedCommand,
            ConfigSetCommand.name: ConfigSetCommand,
            ConfigSetExtraDockerArgsCommand.name: ConfigSetExtraDockerArgsCommand,
            ConfigListExtraDockerArgsCommand.name: ConfigListExtraDockerArgsCommand,
            ConfigRemoveExtraDockerArgsCommand.name: ConfigRemoveExtraDockerArgsCommand,
            ConfigSetEnvCommand.name: ConfigSetEnvCommand,
            ConfigUnsetEnvCommand.name: ConfigUnsetEnvCommand,
            ConfigListEnvCommand.name: ConfigListEnvCommand,
            ConfigBindCommand.name: ConfigBindCommand,
            ConfigAuthorizeCommand.name: ConfigAuthorizeCommand,
            ConfigApproveCommand.name: ConfigApproveCommand,
            ConfigUnsetCommand.name: ConfigUnsetCommand,
        }


class StateAdoptCommand(Command):
    name = "adopt"
    capsule_access: ClassVar[CapsuleAccess] = CapsuleAccess.MUTATES
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
    capsule_access: ClassVar[CapsuleAccess] = CapsuleAccess.INDEPENDENT
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
    capsule_access: ClassVar[CapsuleAccess] = CapsuleAccess.INDEPENDENT
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
    capsule_access: ClassVar[CapsuleAccess] = CapsuleAccess.INDEPENDENT
    help = "Launch a successor capsule from a retained materialization run."

    @classmethod
    def configure(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--run-id", required=True, help="Existing retained materialization run ID.")
        _add_runtime_plan_options(parser, host_paths=False)

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        root = _recursive_project_root(_project_context(context))

        def report(result: SuccessorResult) -> None:
            # Printed once the successor runs and its inspection passed; the
            # command then stays attached until the container exits, like
            # `project run`. The successor's own output is in the run's log.
            print(result.to_json() if arguments.as_json else json.dumps(result.to_mapping(), indent=2, sort_keys=True), flush=True)

        try:
            result = launch_successor(
                root, arguments.run_id, runtime_plan_path=arguments.runtime_plan, on_running=report
            )
        except RecursiveSuccessorError as exc:
            raise ProjectConfigurationError(str(exc)) from exc
        report(result)
        return 0 if result.exit_code == 0 else (result.exit_code or 1)


class RecursiveInspectSuccessorCommand(Command):
    name = "inspect-successor"
    capsule_access: ClassVar[CapsuleAccess] = CapsuleAccess.INDEPENDENT
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
_RUN_ONCE_AUTHORIZATIONS = ("docker-daemon", "network", "development-sudo", "host-browser", "host-x11")


class ProjectRunCommand(Command):
    name = "run"
    capsule_access: ClassVar[CapsuleAccess] = CapsuleAccess.MUTATES
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
        parser.add_argument("--no-update-check", action="store_true",
                            help="Skip the daily interactive distribution refresh; cached critical notices still allow a decision.")
        parser.add_argument("--print-command", action="store_true",
                            help="Prepare and print the Docker command without launching; inline extra environment values are redacted and comments identify transient dependencies.")
        add_carrier_options(parser, families=("set", "authorize"))

    @classmethod
    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
        if not arguments.print_command:
            return cls._run(arguments, context)
        commands: list[str] = []
        # Keep both Python narration and inherited child-process output off
        # stdout. Emit only after preparation and its cleanup have succeeded.
        with preparation_diagnostics():
            result = cls._run(arguments, context, command_report=commands.append)
        if result == 0:
            for command in commands:
                sys.stdout.write(command)
        return result

    @classmethod
    def _run(cls, arguments: argparse.Namespace, context: object | None,
             command_report: Callable[[str], None] | None = None) -> int:
        start = _project_context(context).start_path()
        # Software approvals first: new versions of vendor software approved
        # before are one question at launch, by the owner's direction of
        # 2026-10-22. Any other pending decision is reported by the loading
        # below, as before. Printing the command never asks or writes.
        if command_report is None and not offer_software_approvals(start):
            print("Launch cancelled; no session was started.")
            return 1
        admitted = ExecutionConfiguration.load(start, force=arguments.force)
        # Reject invalid launch overrides before an optional upgrade can change
        # selection. Reload afterward so this launch and its success record use
        # exactly the version set the developer has just chosen.
        overrides, memory_override = _run_once_answers(arguments, admitted.project.manifest, admitted.project.lock)
        # The saved Docker arguments are validated here too: a bad file refuses the
        # launch before the upgrade offer asks anything or changes the selection.
        saved_docker_args = read_arguments(arguments_path(admitted.project.checkout_path))
        _validate_extra_docker_args(saved_docker_args)
        docker_options = list(arguments.docker_options)
        if docker_options:
            try:
                reject_launcher_owned_docker_options(docker_options)
            except PycharmRunError as exc:
                raise ProjectConfigurationError(str(exc)) from exc
        if command_report is None and not offer_upgrades(admitted.project.root, refresh=not arguments.no_update_check):
            print("Launch cancelled; no session was started.")
            return 1
        admitted = ExecutionConfiguration.load(admitted.project.root, force=arguments.force)
        selected, review = admitted.project, admitted.review
        root, manifest, lock = selected.root, selected.manifest, selected.lock
        input_path, output_path = selected.checkout_path, selected.resolution_path
        checkout, resolved = selected.checkout, selected.resolution
        # Capture before launching: a later session completion cannot certify
        # edits or a successor selection made while this session was running.
        captured_files = {input_path.name: input_path.read_bytes(), output_path.name: output_path.read_bytes()}
        try:
            notice = version_sets.reminder(root)
            if notice:
                print(notice)
        except (OSError, CliError):
            pass  # Optional cached reminders never gate an offline launch.
        if admitted.stale_inputs:
            print(f"WARNING: using stale generated resolution once ({', '.join(admitted.stale_inputs)}).", file=sys.stderr)
        authorizations = review.resolved_authorizations()
        host_access = review.effective_host(overrides)
        host_x11_answer = host_access.host_x11
        display_transport: str | None = None
        web_console: WebConsoleAvailability | None = None

        def prepare_display(base: ImageDetails) -> None:
            nonlocal display_transport, web_console
            display_transport = _select_display_transport(
                base.labels, host_x11_answer=host_x11_answer
            )
            web_console = web_console_availability(base.labels)
            if host_x11_answer is None:
                allow = AuthorizationChoice("host-x11", "true", "").command(root)
                deny = AuthorizationChoice("host-x11", "false", "").command(root)
                print(
                    "No explicit host-x11 choice is recorded.\n"
                    f"To select host X11: {allow}\n"
                    f"To require the contained desktop: {deny}\n"
                    "Resolve after changing the choice."
                )

        runtime = resolved["runtime"]
        component = runtime["component"]
        image = runtime.get("image")
        checkout_runtime_plan = None
        use_image_process = False
        image_labels: Mapping[str, str] = {}
        realized = None
        degraded_download = False
        if isinstance(lock.get("base"), dict) and isinstance(lock.get("materialization"), dict):
            while True:
                try:
                    realized = realize_environment(selected, report=print, prepare_base=prepare_display)
                    break
                except ArtifactUnavailable as exc:
                    smaller = omit_unavailable_optional(selected, exc.url)
                    if smaller is None:
                        raise
                    omitted = set(selected.lock["components"]) - set(smaller.lock["components"])
                    print(f"Warning: optional tools {', '.join(sorted(omitted))} unavailable: {exc}; continuing without those enhancements.", file=sys.stderr)
                    selected = smaller
                    lock, checkout, resolved = selected.lock, selected.checkout, selected.resolution
                    review = review_configuration(manifest, lock, checkout)
                    authorizations = review.resolved_authorizations()
                    degraded_download = True
            image = realized.image.reference
            image_labels = realized.image.labels
            checkout_runtime_plan = project_runtime_plan(selected, realized.locked)
            use_image_process = True
            action = "Materialized" if realized.created else "Reused"
            print(f"{action} canonical environment: {image}")
        if not isinstance(image, str) or not image:
            raise ProjectConfigurationError(
                f"The resolved {component} environment has no runnable image."
            )
        memory_limit = runtime.get("memory-limit-bytes")
        # Bindings convey host access too. --force may retain stale ordinary
        # runtime choices, but never resurrect a removed mapping or secret.
        state = dict(checkout.get("state", {}).get("adopted", {}))
        state.update(review.bindings)
        secret_environment = review.secret_bindings
        if memory_override is not None:
            memory_limit = memory_override
        selected_docker_daemon = host_access.docker_daemon
        selected_sudo = host_access.development_sudo
        selected_network = host_access.network
        selected_host_browser = host_access.host_browser
        if arguments.no_recursive_e2e:
            selected_docker_daemon = "none"
            selected_sudo = False
            selected_network = "bridge"
        if display_transport is None:
            display_transport = _select_display_transport(
                image_labels, host_x11_answer=host_x11_answer
            )
        if web_console is None:
            web_console = web_console_availability(image_labels)
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
        if saved_docker_args or docker_options:
            # Single-instance options the launcher composes are refused —
            # docker would keep the passthrough occurrence and silently
            # override the resolved plan. Everything else is deliberate
            # stepping outside the plan; show what is being handed to Docker,
            # masking inline environment values.
            print(
                "WARNING: passing raw docker run options outside the resolved plan: "
                + " ".join(redact_environment([*saved_docker_args, *docker_options])),
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
                inherit_legacy_configuration=False,
                command_report=command_report,
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
                enable_sudo=selected_sudo,
                network_mode=selected_network,
                memory_limit_bytes=memory_limit,
                runtime_plan=checkout_runtime_plan,
                launch_configuration=runtime_configuration.LaunchConfiguration.capture(selected, version_sets.effective_set_id(lock, checkout)),
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
                extra_docker_args=["--pull=never", *saved_docker_args, *docker_options],
                project_state=None,
                enable_host_browser=selected_host_browser,
                display_transport=display_transport,
                web_console=web_console,
            )
        )
        if command_report is not None:
            return exit_code  # Printing is never evidence of successful use.
        if exit_code == 0 and not degraded_download:
            # D-0008: a zero exit proves this configuration; record it as a
            # known-good generation unless identical content already exists.
            # Recording failure must never fail the successful run.
            try:
                recorded = record_known_good_configuration(
                    manifest, input_path, output_path, captured_files=captured_files
                )
                version_sets.record_success(selected, realized)
                if "version-set" in checkout:
                    print("Local use succeeded. Optionally prepare an upstream proposal with 'project versions propose PATH'.")
            except (OSError, CliError) as exc:
                print(
                    f"Warning: could not record the known-good configuration: {exc}",
                    file=sys.stderr,
                )
            else:
                if recorded is not None:
                    print(f"Recorded known-good configuration: {recorded}")
        return exit_code


def _select_display_transport(image_labels: Mapping[str, str], *, host_x11_answer: object) -> str:
    """Choose the display transport for this run and say why, once."""

    transport, reason = select_display_transport(image_labels, host_x11_answer=host_x11_answer)
    print(reason)
    return transport


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
        """Select the project and apply the subcommand's capsule access.

        The subcommand is resolved first, without side effects: an unknown
        name, help, or a bare nested group gets a plain context and the
        dispatch reports it as it would outside a capsule. For a known leaf,
        its declared :class:`CapsuleAccess` decides whether the capsule's own
        project is selected when none encloses the working directory, and
        whether the command is refused inside the capsule in favour of the
        launcher.
        """
        context = ProjectCommandContext(arguments.selected_path)
        tokens: list[str] = list(arguments.rest)
        parsed_tokens = tokens[:tokens.index("--")] if "--" in tokens else tokens
        if any(token in {"-h", "--help"} for token in parsed_tokens):
            return context
        leaf = cls.resolve(tokens)
        if leaf is None or issubclass(leaf, Group):
            return context
        access = _capsule_access(leaf)
        if access.selects_capsule_project and context.selected_path is None:
            context = replace(context, capsule_root=runtime_configuration.capsule_project_root(Path(".")))
        if access.needs_launcher:
            runtime_configuration.require_launcher(context.start_path(), tokens)
        return context

    @classmethod
    def subcommands(cls) -> Mapping[str, type[Command] | type[Group]]:
        return {
            ProjectInfoCommand.name: ProjectInfoCommand,
            ProjectListCommand.name: ProjectListCommand,
            ProjectInitCommand.name: ProjectInitCommand,
            CheckoutGroup.name: CheckoutGroup,
            ConfigGroup.name: ConfigGroup,
            VersionsGroup.name: VersionsGroup,
            StateGroup.name: StateGroup,
            RecursiveE2EGroup.name: RecursiveE2EGroup,
            ProjectRunCommand.name: ProjectRunCommand,
        }


def _capsule_access(leaf: type[Command]) -> CapsuleAccess:
    """The access a ``project`` leaf declares for itself.

    Every leaf of the tree declares one explicitly, which
    ``test_project_commands`` checks by walking the tree; an inherited or
    missing declaration is a programming error, never a default.
    """
    access = leaf.__dict__.get("capsule_access")
    if not isinstance(access, CapsuleAccess):
        raise AssertionError(f"{leaf.__name__} declares no capsule access.")
    return access


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
        return [ConfigurationListRow("value", "*", "invalid", "configuration is not a table", "checkout")]
    raw_values = configuration.get("values", {})
    if not isinstance(raw_values, dict):
        return [ConfigurationListRow("value", "*", "invalid", "values is not a table", "checkout")]

    rows: list[ConfigurationListRow] = []
    for name, declaration in sorted(declarations.items()):
        if name not in raw_values:
            if name in configuration.get("omitted-values", []):
                rows.append(ConfigurationListRow("value", name, "omitted", "-", "checkout"))
            elif "recommended" in declaration:
                value = normalize_configuration_value(manifest, name, "default")
                rows.append(ConfigurationListRow("value", name, "project-recommended", render_toml_scalar(value), "manifest"))
            else:
                status = "missing-required" if declaration.get("required", False) else "unset-optional"
                rows.append(ConfigurationListRow("value", name, status, "-", "manifest (declared, no value)"))
            continue
        try:
            normalized = normalize_configuration_value(manifest, name, raw_values[name])
        except ProjectConfigurationError as exc:
            rows.append(ConfigurationListRow("value", name, "invalid", str(exc), "checkout"))
        else:
            rows.append(
                ConfigurationListRow("value", name, "configured", render_toml_scalar(normalized), "checkout")
            )
    for name, value in sorted(raw_values.items(), key=lambda item: str(item[0])):
        if name not in declarations:
            rows.append(ConfigurationListRow("value", str(name), "undeclared", repr(value), "checkout"))
    return rows


def _component_secret_rows(
    lock: dict[str, Any], checkout: dict[str, Any]
) -> list[ConfigurationListRow]:
    declarations = component_secret_inputs(lock)
    try:
        bindings = resolve_secret_bindings(lock, checkout)
    except ProjectConfigurationError as exc:
        return [ConfigurationListRow("secret", "*", "invalid", str(exc), "checkout")]
    rows: list[ConfigurationListRow] = []
    for name, declaration in sorted(declarations.items()):
        source = bindings.get(name)
        if source is None:
            status = "missing-required" if declaration.required else "optional-unbound"
            origin = "lock (declared, unbound)"
        else:
            status = "bound" if source in os.environ else "bound-unavailable"
            origin = "checkout, environment" if status == "bound" else "checkout (variable unset in environment)"
        rows.append(
            ConfigurationListRow(
                "secret",
                name,
                status,
                f"{declaration.environment_variable} ({declaration.exposure})",
                origin,
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
        return [ConfigurationListRow("binding", "*", "invalid", "host-directory is not a table", "checkout")]
    state = checkout.get("state", {})
    adopted = state.get("adopted", {}) if isinstance(state, dict) else {}
    if not isinstance(adopted, dict):
        adopted = {}

    rows: list[ConfigurationListRow] = []
    for name in sorted(declarations):
        bound = raw_bindings.get(name)
        legacy = adopted.get(name)
        if bound is not None and legacy is not None:
            rows.append(ConfigurationListRow("binding", name, "conflict", "bound and adopted", "checkout"))
        elif bound is not None:
            path = Path(str(bound)).expanduser().resolve()
            status = "bound" if isinstance(bound, str) and path.is_dir() else "invalid"
            rows.append(ConfigurationListRow("binding", name, status, f"host-directory: {path}", "checkout"))
        elif legacy is not None:
            path = Path(str(legacy)).expanduser().resolve()
            status = "adopted-legacy" if isinstance(legacy, str) and path.is_dir() else "invalid"
            rows.append(ConfigurationListRow("binding", name, status, str(path), "checkout (state.adopted)"))
        else:
            rows.append(ConfigurationListRow("binding", name, "managed-default", "managed directory", "managed (lock declares the slot)"))
    for name, value in sorted(raw_bindings.items(), key=lambda item: str(item[0])):
        if name not in declarations:
            rows.append(ConfigurationListRow("binding", str(name), "undeclared", str(value), "checkout"))
    return rows


def _configuration_authorization_rows(
    manifest: dict[str, Any], lock: dict[str, Any], checkout: dict[str, Any]
) -> list[ConfigurationListRow]:
    try:
        reviews = review_authorizations(manifest, lock, checkout)
        declarations = authorization_declarations(manifest, lock)
    except ProjectConfigurationError as exc:
        return [ConfigurationListRow("authorization", "*", "invalid", str(exc), "checkout")]
    rows = []
    for item in reviews:
        declaration = declarations.get(item.name)
        # The base selection and vendor acquisitions are recommended by the
        # lock; host access is recommended by the manifest's host tables.
        recommender = "lock" if declaration is None or declaration.required else "manifest"
        if declaration is not None and not declaration.project_recommended:
            # Workstation defaults are available without project advice. Do not
            # attribute those defaults, or a return to them, to the manifest.
            if item.recorded == "unanswered":
                origin = "workstation default (unanswered)"
            elif item.status == "stale":
                origin = "checkout (answer predates the workstation default)"
            else:
                origin = "checkout"
        elif item.recorded == "unanswered":
            origin = f"{recommender} (recommendation, unanswered)"
        else:
            origin = "checkout" if item.status != "stale" else f"checkout (answer predates the {recommender} recommendation)"
        rows.append(
            ConfigurationListRow(
                "authorization", item.name, item.status,
                item.recommended if item.recorded == "unanswered" else item.recorded,
                origin,
            )
        )
    return rows


def _configuration_resolution_row(
    manifest: dict[str, Any],
    lock: dict[str, Any],
    checkout: dict[str, Any],
    resolution_path: Path,
) -> ConfigurationListRow:
    if not resolution_path.is_file():
        return ConfigurationListRow("resolution", "generated", "missing", str(resolution_path), "resolution")
    resolved = load_resolution(resolution_path)
    if resolved.get("status") == "unresolved":
        return ConfigurationListRow("resolution", "generated", "unresolved", str(resolution_path), "resolution")
    stale = stale_resolution_inputs(manifest, lock, checkout, resolved)
    if stale:
        return ConfigurationListRow("resolution", "generated", "stale", ", ".join(stale), "resolution (inputs changed: " + ", ".join(stale) + ")")
    return ConfigurationListRow("resolution", "generated", "fresh", str(resolution_path), "resolution")


def _print_configuration_rows(rows: list[ConfigurationListRow]) -> None:
    # SOURCE precedes the value: values carry digests and paths that push a
    # trailing column past most terminal widths.
    headers = ("KIND", "NAME", "STATUS", "SOURCE", "VALUE / RECOMMENDATION")
    values = [(row.kind, row.name, row.status, row.source, row.value) for row in rows]
    widths = [max(len(headers[index]), *(len(row[index]) for row in values)) for index in range(5)]
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

    for declaration in declarations.values():
        record.authorize(declaration, declaration.recommended_value)
    record.write()
    print(f"Authorized {len(declarations)} recommendations for this checkout.")
    print(f"Checkout input: {input_path}")
    print("Run 'devcapsule project config resolve' before materialization or launch.")
    return 0


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
            _seed_component_state(source, declaration)
        mounts[name] = (source, declaration.container_path)
    return mounts


def _seed_component_state(source: Path, declaration: Any) -> None:
    """Place a component's declared default files into its managed slot.

    Written as the invoking user before the daemon mounts the slot. JSON
    seeds may fill missing keys; explicit values always survive. Adopted
    directories never reach here (see the caller).
    """

    definition = COMPONENTS.get(str(declaration.component_id))
    if definition is None:
        return
    for seed in definition.state_seeds():
        if seed.slot != declaration.slot_name:
            continue
        target = source / seed.relative_path
        # A developer may link settings elsewhere. Do not follow or replace
        # those links, including dangling links and linked parent directories.
        relative_parts = Path(seed.relative_path).parts
        if any(source.joinpath(*relative_parts[:i]).is_symlink()
               for i in range(1, len(relative_parts) + 1)):
            print(f"Warning: leaving linked component settings unchanged: {target}", file=sys.stderr)
            continue
        if target.exists():
            if not seed.merge_missing_json:
                continue
            try:
                settings = json.loads(target.read_text(encoding="utf-8"))
                defaults = json.loads(seed.content)
                if not isinstance(settings, dict):
                    raise ValueError("expected a JSON object")
                if _fill_missing_settings(settings, defaults):
                    atomic_write(target, json.dumps(settings, indent=2) + "\n")
            except (ValueError, OSError) as exc:
                # Do not echo file contents: settings may include credentials.
                print(
                    f"Warning: leaving component settings unchanged: {target} "
                    f"({type(exc).__name__}); repair the JSON object to apply defaults.",
                    file=sys.stderr,
                )
            continue
        target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        atomic_write(target, seed.content)


def _fill_missing_settings(settings: dict[str, Any], defaults: dict[str, Any]) -> bool:
    """Add missing JSON keys in memory; reject incompatible object structure."""
    changed = False
    for key, value in defaults.items():
        if key not in settings:
            settings[key] = value
            changed = True
        elif isinstance(value, dict):
            if not isinstance(settings[key], dict):
                raise ValueError(f"expected an object for {key}")
            changed = _fill_missing_settings(settings[key], value) or changed
    return changed



COMMAND = ProjectCommand
