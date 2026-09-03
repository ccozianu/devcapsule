"""Checkout-facing operations: one function per user-visible operation.

Command modules translate parsed arguments into exactly one call here and
print the returned report; policy, validation, and artifact writes live on
this side of the boundary.  This is the operation layer the first-run design
requires: the write half and the read half of each artifact contract sit in
the same module instead of being split between a command callback and a
library loader.

Reports render themselves (`render()`), so the exact user-facing wording of
an operation's outcome is owned here alongside the operation, not composed
ad hoc at each call site.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any, Mapping, Sequence, TextIO

from devcapsule.configuration_nodes import (
    CARRIER_FAMILY_BIND,
    CARRIER_FAMILY_SET,
    PROVIDER_HOST_DIRECTORY,
    build_node_registry,
)
from devcapsule.components.antigravity_cli import DEFINITION as ANTIGRAVITY_CLI
from devcapsule.components.catalog import INTERACTIVE_SURFACES
from devcapsule.elicitation import AnswerKey, Elicitor
from devcapsule.environment_realization import required_local_image
from devcapsule.materialization import validate_base_image
from devcapsule.project import sanitize_name
from devcapsule.project_configuration import (
    CURATED_HOST_RECOMMENDATIONS,
    AuthorizationScalar,
    ProjectConfigurationError,
    atomic_write,
    authorization_declarations,
    authorized_base_selection,
    canonical_digest,
    checkout_record_paths,
    immutable_registry_reference,
    load_toml,
    lock_for,
    manifest_for,
    normalize_configuration_value,
    quote_toml,
    render_authorization_value,
    render_checkout,
    render_toml_scalar,
    resolve_configuration_bindings,
    resolve_configuration_values,
    resolve_secret_bindings,
    resolution_source_digests,
    resolved_checkout_authorizations,
    stale_resolution_inputs,
    validate_manifest,
)
from devcapsule.platforms import Platform, UnsupportedPlatformError
from devcapsule.resolution_matrix import MATRICES, ResolutionMatrix


def _current_matrix() -> ResolutionMatrix:
    """This host's resolution matrix, with platform failures as user errors."""

    try:
        return MATRICES[Platform.current()]
    except UnsupportedPlatformError as exc:
        raise ProjectConfigurationError(str(exc)) from exc

__all__ = [
    "CheckoutRecord",
    "InitializeReport",
    "InitializeRequest",
    "ProvidedAnswer",
    "ResolveReport",
    "add_capability_need",
    "initialize_project",
    "resolve_checkout",
]


@dataclass(frozen=True)
class ResolveReport:
    """Outcome of one successful resolution."""

    resolution_path: Path
    lock_name: str
    registered_checkout: Path | None

    def render(self) -> str:
        lines = []
        if self.registered_checkout is not None:
            lines.append(f"Registered checkout: {self.registered_checkout}")
        lines.append(f"Resolved {self.resolution_path} from {self.lock_name}")
        return "\n".join(lines)


class CheckoutRecord:
    """One checkout record loaded for mutation and written back atomically.

    Every mutating operation (set, bind, authorize, adopt) edits the same
    developer-owned record through this class, so the ownership check and the
    table validation exist exactly once.
    """

    def __init__(self, manifest: Mapping[str, Any], root: Path) -> None:
        self._manifest = manifest
        self._root = root
        input_path, _resolution_path = checkout_record_paths(manifest, root)
        self.input_path = input_path
        checkout: dict[str, Any] = load_toml(input_path) if input_path.is_file() else {}
        recorded_path = checkout.get("checkout", {}).get("path")
        # A record reached through this project identity must describe this
        # exact checkout; editing another checkout's record would let one
        # checkout inherit another's permissions.
        if recorded_path and Path(str(recorded_path)).expanduser().resolve() != root:
            raise ProjectConfigurationError(
                f"{input_path} belongs to another checkout: {recorded_path}"
            )
        self.document = checkout
        self.state = dict(checkout.get("state", {}).get("adopted", {}))
        self.host = dict(checkout.get("host", {}))
        self.authorization = dict(checkout.get("authorization", {}))
        self.values = _checkout_values(checkout)
        self.directory_bindings = _checkout_host_directory_bindings(checkout)
        self.environment_bindings = _checkout_host_environment_bindings(checkout)

    def write(self) -> None:
        atomic_write(
            self.input_path,
            render_checkout(
                self._manifest,
                self._root,
                self.state,
                self.host,
                self.authorization,
                self.values,
                self.directory_bindings,
                self.environment_bindings,
            ),
        )


def resolve_checkout(start_path: Path) -> ResolveReport:
    """Validate one checkout's combined inputs and write its fresh resolution.

    This is the explicit "my configuration choices are complete" step: it
    validates completeness and consistency across manifest, lock, and the
    developer-owned record, then writes the inspectable generated resolution
    whose source digests reveal later drift.  It creates the checkout record
    on a first resolution — record creation belongs to this path, which is
    the first persistent developer-owned act.
    """

    root, manifest = manifest_for(start_path)
    lock_path, lock = lock_for(root, manifest)
    input_path, output = checkout_record_paths(manifest, root)
    registered: Path | None = None
    if not input_path.is_file():
        atomic_write(input_path, render_checkout(manifest, root, {}, {}))
        registered = input_path
    checkout = load_toml(input_path)
    if checkout.get("devcapsule-checkout-schema-version") != 1:
        raise ProjectConfigurationError(
            f"{input_path} has an unsupported checkout schema version."
        )
    if Path(str(checkout.get("checkout", {}).get("path", ""))).resolve() != root:
        raise ProjectConfigurationError(
            f"{input_path} does not match observed checkout {root}."
        )
    image = lock.get("image", {}).get("reference")
    component = lock.get("components", {}).get("interactive-surface")
    has_formation = isinstance(lock.get("base"), dict) and isinstance(
        lock.get("materialization"), dict
    )
    if component not in INTERACTIVE_SURFACES or (not image and not has_formation):
        raise ProjectConfigurationError(
            "The V1 slice requires a lock selecting a known interactive surface "
            "with either a completed image or formation inputs."
        )
    state = checkout.get("state", {}).get("adopted", {})
    host = checkout.get("host", {})
    values, runtime_effects = resolve_configuration_values(manifest, checkout)
    bindings = resolve_configuration_bindings(lock, checkout)
    secret_bindings = resolve_secret_bindings(lock, checkout)
    overlap = sorted(set(state) & set(bindings))
    if overlap:
        raise ProjectConfigurationError(
            "State resources cannot be both adopted and configuration-bound: "
            + ", ".join(overlap)
            + "."
        )
    authorizations = resolved_checkout_authorizations(manifest, lock, checkout)
    sources = resolution_source_digests(manifest, lock, checkout)
    lines = [
        "devcapsule-resolved-schema-version = 1",
        "",
        "[sources]",
        f"manifest = {quote_toml(sources['manifest'])}",
        f"platform-lock = {quote_toml(sources['platform-lock'])}",
        f"checkout-input = {quote_toml(sources['checkout-input'])}",
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
            f"{quote_toml(str(key))} = {quote_toml(str(value))}"
            for key, value in sorted(state.items())
        )
    if bindings:
        lines.extend(["", "[state.bindings]"])
        lines.extend(
            f"{quote_toml(key)} = {quote_toml(value)}" for key, value in sorted(bindings.items())
        )
    if secret_bindings:
        lines.extend(["", "[secret.bindings.host-environment]"])
        lines.extend(
            f"{quote_toml(key)} = {quote_toml(value)}"
            for key, value in sorted(secret_bindings.items())
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
        base_selection = authorized_base_selection(lock, checkout)
        if base_selection is None:  # pragma: no cover - authorized_base establishes it.
            raise ProjectConfigurationError("Resolved base-image authorization is missing.")
        if base_selection.local_image_identity is not None:
            # A developer-selected local base must still exist and match the
            # exact inspected identity the authorization recorded.
            local_base = required_local_image(base_selection.reference)
            validate_base_image(
                local_base,
                platform=str(lock["platform"]),
                expected_identity=base_selection.local_image_identity,
            )
        lines.extend(
            [
                "",
                "[authorization.base-image]",
                f"reference = {quote_toml(base_selection.reference)}",
                f"lock-digest = {quote_toml(canonical_digest(lock))}",
            ]
        )
        if base_selection.local_image_identity is not None:
            lines.append(f"image-id = {quote_toml(base_selection.local_image_identity)}")
    atomic_write(output, "\n".join(lines) + "\n")
    return ResolveReport(
        resolution_path=output,
        lock_name=lock_path.name,
        registered_checkout=registered,
    )


@dataclass(frozen=True)
class ProvidedAnswer:
    """One configuration answer supplied on the command line."""

    family: str
    name: str
    value: str
    justification: str | None = None


@dataclass(frozen=True)
class InitializeRequest:
    """Everything ``devcapsule project init`` collected from its command line."""

    directory: Path
    need: tuple[str, ...] = ()
    project_name: str | None = None
    slug: str | None = None
    creator: str | None = None
    project_mount: str | None = None
    answers: tuple[ProvidedAnswer, ...] = ()
    regenerate: bool = False
    # Skip consent solicitations for explicitly supplied values (today: a
    # base-image selection); validation and recording are unchanged.
    less_pedantic: bool = False
    # None: decide from whether stdin is a terminal.
    interactive: bool | None = None


@dataclass(frozen=True)
class InitializeReport:
    """Outcome of one successful initialization, in owner order."""

    manifest_path: Path
    manifest_action: str
    project_name: str
    creator: str
    slug: str
    project_mount: str
    capabilities: tuple[str, ...]
    lock_path: Path
    lock_action: str
    base_display: str
    recommendations: tuple[tuple[str, str], ...]
    authorized: tuple[str, ...]
    checkout_record: Path
    resolve: ResolveReport

    def render(self) -> str:
        lines = [
            f"{self.manifest_action} {self.manifest_path}",
            f"Project: {self.project_name} — {self.creator}/{self.slug}",
            f"Project mount: {self.project_mount}",
            f"Capabilities: {' '.join(self.capabilities)}",
            f"{self.lock_action} {self.lock_path} (base {self.base_display})",
        ]
        lines.extend(
            f"Recommended {name} = {value} for every checkout."
            for name, value in self.recommendations
        )
        if self.authorized:
            lines.append(
                "Authorized for this checkout: " + ", ".join(self.authorized) + "."
            )
        lines.append(f"Checkout record: {self.checkout_record}")
        lines.append(self.resolve.render())
        lines.append("Project initialized; 'devcapsule project run' starts it.")
        return "\n".join(lines)


def initialize_project(
    request: InitializeRequest,
    *,
    input_stream: TextIO | None = None,
    output_stream: TextIO | None = None,
) -> InitializeReport:
    """Bring the four owned artifacts into existence, in owner order.

    The settled postcondition (*Initializing A New Project* in the
    v1-user-experience design note): a valid manifest and a platform lock for
    this platform exist, the owner's checkout record is registered, and a
    fresh resolution stands — achieved by invoking the same resolution the
    standalone command runs.  The three entry states are handled in order:
    nothing initialized (author everything), partially initialized (honor
    what exists, complete what is missing — repair is init's own job), and
    fully initialized (fail loudly naming ``--regenerate``).
    """

    root = request.directory.expanduser().resolve()
    if not root.is_dir():
        raise ProjectConfigurationError(f"Project directory does not exist: {root}")
    manifest_path = root / ".devcapsule" / "devcapsule.toml"
    try:
        platform = Platform.current()
    except UnsupportedPlatformError as exc:
        raise ProjectConfigurationError(str(exc)) from exc
    lock_path = root / ".devcapsule" / f"devcapsule.{platform}.lock"

    existing_manifest: dict[str, Any] | None = None
    if manifest_path.is_file():
        # A hand-authored or carried-over manifest is the ordinary form of
        # partial initialization, not an error: honor it and generate what
        # follows from it.
        existing_manifest = load_toml(manifest_path)
        validate_manifest(existing_manifest, manifest_path)

    if existing_manifest is not None and lock_path.is_file() and not request.regenerate:
        if _fully_initialized(root, existing_manifest):
            if request.answers:
                # A repeated init carrying --authorize/--set/--bind must not
                # silently drop the developer's expressed answers (bug of
                # 2026-09-01): they are "individual answers" in the design's
                # own vocabulary, applied here through the same primitives
                # the config family uses, then resolved afresh so the init
                # postcondition — 'project run' starts it — holds.
                return _apply_answers_to_standing_checkout(
                    root, manifest_path, lock_path, platform, request
                )
            raise ProjectConfigurationError(
                f"{root} is already fully initialized: manifest, platform lock, "
                "checkout record, and a fresh resolution all stand. 'devcapsule "
                "project init --regenerate' rewrites the derived platform lock; "
                "the 'config' family changes individual answers."
            )

    elicitor = Elicitor(
        _init_command_line(request),
        interactive=request.interactive,
        input_stream=input_stream,
        output_stream=output_stream,
    )
    identity = _elicit_identity(elicitor, root, existing_manifest)
    recommendations = _elicit_recommendations(elicitor, existing_manifest)
    # Fail now if identity or capabilities are unanswered: the lock cannot be
    # generated without them, so later questions are unreachable and their
    # supplied answers must not be misreported as unknown.
    if elicitor.missing():
        elicitor.finish(require_all_consumed=False)

    manifest_action = _write_manifest(
        manifest_path, existing_manifest, identity, recommendations
    )
    manifest = load_toml(manifest_path)
    validate_manifest(manifest, manifest_path)

    if lock_path.is_file() and not request.regenerate:
        lock_action = "Kept"
    else:
        lock_action = "Regenerated" if lock_path.is_file() else "Created"
        generated = MATRICES[platform].resolve(list(identity.capabilities))
        # World-readable like any committed project file; the 0600 default is
        # for developer-owned records.
        atomic_write(lock_path, generated.render_lock(), mode=0o644)
    _, lock = lock_for(root, manifest)

    declarations = authorization_declarations(manifest, lock)
    record = CheckoutRecord(manifest, root)
    authorized = _elicit_acquisitions(
        elicitor,
        declarations,
        record,
        platform=str(platform),
        less_pedantic=request.less_pedantic,
    )
    elicitor.finish()

    for name, _value in recommendations:
        declaration = declarations[name]
        record.authorization[name] = {
            "value": declaration.recommended_value,
            "recommendation-digest": declaration.recommendation_digest,
        }
        authorized.append(name)
    _apply_extra_answers(request.answers, manifest, lock, record)
    record.write()

    resolve_report = resolve_checkout(root)
    base_declaration = declarations.get("base-image")
    if base_declaration is not None:
        base_display = base_declaration.display_value or str(base_declaration.recommended_value)
    else:
        base_display = str(lock.get("image", {}).get("reference", "image lock"))
    return InitializeReport(
        manifest_path=manifest_path,
        manifest_action=manifest_action,
        project_name=identity.name,
        creator=identity.creator,
        slug=identity.slug,
        project_mount=identity.mount,
        capabilities=identity.capabilities,
        lock_path=lock_path,
        lock_action=lock_action,
        base_display=base_display,
        recommendations=tuple(recommendations),
        authorized=tuple(authorized),
        checkout_record=record.input_path,
        resolve=resolve_report,
    )


@dataclass(frozen=True)
class _ProjectIdentity:
    name: str
    slug: str
    creator: str
    mount: str
    capabilities: tuple[str, ...]


def _init_command_line(request: InitializeRequest) -> dict[AnswerKey, str]:
    """Map init's dedicated flags and --authorize carriers to elicitation keys.

    ``--set`` and ``--bind`` answers stay out of the elicitor: they are
    optional extras applied after the lock exists, validated by the node
    registry, and never prompted for.  Only authorization nodes share the
    elicitor with the identity flags, and their names cannot collide with the
    identity keys because the authorization vocabulary is curated.
    """

    command_line: dict[AnswerKey, str] = {}
    if request.need:
        command_line[("need", "value")] = " ".join(request.need)
    for key, value in (
        ("name", request.project_name),
        ("slug", request.slug),
        ("creator", request.creator),
        ("project-mount", request.project_mount),
    ):
        if value is not None:
            command_line[(key, "value")] = value
    for answer in request.answers:
        if answer.family != "authorize":
            continue
        command_line[(answer.name, "value")] = answer.value
        if answer.justification is not None:
            command_line[(answer.name, "justification")] = answer.justification
    return command_line


def _elicit_identity(
    elicitor: Elicitor, root: Path, existing_manifest: Mapping[str, Any] | None
) -> _ProjectIdentity:
    project = (existing_manifest or {}).get("project", {})
    existing_need = (existing_manifest or {}).get("capabilities", {}).get("need")

    def existing_field(key: str) -> str | None:
        value = project.get(key)
        return str(value) if value else None

    name = elicitor.seek(
        "name",
        description="Project name",
        remedy="--name NAME",
        existing=existing_field("name"),
        default=root.name,
    )
    slug = elicitor.seek(
        "slug",
        description="Project slug",
        remedy="--slug SLUG",
        existing=existing_field("slug"),
        default=sanitize_name(root.name).lower(),
    )
    creator = elicitor.seek(
        "creator",
        description="Project creator (URL or email address)",
        remedy="--creator CREATOR",
        existing=existing_field("creator"),
        validate=_normalize_creator,
    )
    assert slug is not None  # a default always answers it
    mount = elicitor.seek(
        "project-mount",
        description="In-container project mount path",
        remedy="--project-mount PATH",
        existing=existing_field("mount"),
        default=f"/workspace/{slug.value}",
    )
    need = elicitor.seek(
        "need",
        description=(
            "Capabilities the project needs, space-separated "
            f"({', '.join(_current_matrix().capabilities())})"
        ),
        remedy="--need CAPABILITY [--need CAPABILITY ...]",
        existing=" ".join(str(item) for item in existing_need) if existing_need else None,
        validate=_normalize_need_string,
    )
    capabilities = tuple(need.value.split()) if need else ()
    capabilities = _with_default_agent(elicitor, capabilities, existing_need)
    return _ProjectIdentity(
        name=name.value if name else "",
        slug=slug.value,
        creator=creator.value if creator else "",
        mount=mount.value if mount else "",
        capabilities=capabilities,
    )


def _with_default_agent(
    elicitor: Elicitor,
    capabilities: tuple[str, ...],
    existing_need: object,
) -> tuple[str, ...]:
    """Offer the default-selected agent when a fresh need does not name one.

    Per the component-catalog delivery contract (2026-08-30), the Antigravity
    CLI is default-selected: "available by default" without living in any
    base. Concretely: an interactive init whose freshly authored need omits
    ``antigravity-agent`` asks once, with Enter meaning yes; a noninteractive
    init keeps its explicit ``--need`` list unchanged (the remedy *is* the
    need flag), and a re-init of an existing manifest never grows an authored
    need behind the owner's back.
    """

    default_capability = ANTIGRAVITY_CLI.capability
    if not capabilities or existing_need or default_capability in capabilities:
        return capabilities
    grown = tuple(sorted((*capabilities, default_capability)))
    try:
        # Only offer a default that resolves: while the matrix lacks verified
        # edges combining the agent with this need's surface or siblings, the
        # default silently does not apply rather than failing the init.
        _current_matrix().resolve(grown)
    except ProjectConfigurationError:
        return capabilities
    answer = elicitor.seek(
        "default-agent",
        description=(
            f"Select the default agent component ({default_capability})? (yes/no)"
        ),
        remedy=f"--need {default_capability}",
        empty_answer="yes",
        omitted_answer="no",
        validate=_yes_no_validator("default-agent"),
    )
    if answer is not None and answer.value == "yes":
        return grown
    return capabilities


def _yes_no_validator(name: str) -> Any:
    def validate(value: str) -> str:
        candidate = value.strip().lower()
        if candidate in {"yes", "y"}:
            return "yes"
        if candidate in {"no", "n"}:
            return "no"
        raise ProjectConfigurationError(f"Question {name!r} accepts yes or no.")

    return validate


def _elicit_recommendations(
    elicitor: Elicitor, existing_manifest: Mapping[str, Any] | None
) -> list[tuple[str, str]]:
    """Ask the three curated host-recommendation intent questions.

    Interactively each is asked with Enter meaning "none"; noninteractively
    an unflagged question records no recommendation — settled by the product
    owner on 2026-08-24.  A command-line answer that contradicts what the
    manifest already declares is a conflict, not an override: the manifest is
    authored content, so changing it is a manifest edit, never a silent init
    side effect.
    """

    recommendations: list[tuple[str, str]] = []
    host = (existing_manifest or {}).get("host", {})
    for name, (path, supported) in CURATED_HOST_RECOMMENDATIONS.items():
        rendered = render_authorization_value(supported)
        declared = _declared_recommendation(host, path)
        existing_value = (
            render_authorization_value(declared["value"])
            if declared is not None and isinstance(declared.get("value"), (str, bool))
            else None
        )
        answer = elicitor.seek(
            name,
            description=f"Recommend {name} = {rendered} for every checkout? ({rendered}/none)",
            remedy=f"--authorize {name} {rendered}",
            existing=existing_value,
            empty_answer="none",
            omitted_answer="none",
            validate=_recommendation_validator(name, rendered),
        )
        if answer is None:
            continue
        if existing_value is not None and answer.value != existing_value:
            raise ProjectConfigurationError(
                f"The manifest already recommends {name} = {existing_value}; init never "
                "rewrites an authored recommendation. Edit the manifest to change it."
            )
        if answer.value == "none":
            continue
        justification = elicitor.seek(
            name,
            facet="justification",
            description=f"Justification recorded beside the {name} recommendation",
            remedy=f'--authorize {name} {rendered} "JUSTIFICATION"',
            existing=(
                str(declared.get("justification"))
                if declared is not None and declared.get("justification")
                else None
            ),
        )
        recommendations.append((name, justification.value if justification else ""))
    return recommendations


def _declared_recommendation(
    host: Mapping[str, Any], path: tuple[str, ...]
) -> Mapping[str, Any] | None:
    node: object = host
    for key in path:
        if not isinstance(node, Mapping) or key not in node:
            return None
        node = node[key]
    return node if isinstance(node, Mapping) else None


def _recommendation_validator(name: str, rendered: str) -> Any:
    def validate(value: str) -> str:
        candidate = value.strip().lower()
        if candidate not in {"none", rendered}:
            raise ProjectConfigurationError(
                f"Recommendation {name!r} accepts exactly {rendered!r} or 'none'."
            )
        return candidate

    return validate


def _elicit_acquisitions(
    elicitor: Elicitor,
    declarations: Mapping[str, Any],
    record: CheckoutRecord,
    *,
    platform: str,
    less_pedantic: bool = False,
) -> list[str]:
    """Elicit the owner's own executable and vendor-terms authorizations.

    These have no safe omission — executing an artifact and accepting vendor
    acquisition terms must be answered — so a noninteractive run without their
    flags batch-fails rather than inferring authorization.  Interactively
    each is asked with Enter meaning yes, because the owner just chose the
    inputs that derived them.

    The base-image answer additionally accepts an image reference — a
    developer-owned base selection for this checkout (product-owner ruling
    2026-09-03): the image is read from the local daemon, its identity and
    metadata are presented, and consent is solicited; ``less_pedantic``
    records the selection without the solicitation.
    """

    authorized: list[str] = []
    base = declarations.get("base-image")
    if base is None:
        # A legacy image-reference lock has no formation base to authorize.
        return _elicit_component_acquisitions(elicitor, declarations, record, authorized)
    reference = str(base.recommended_value)
    existing_base = record.authorization.get("base-image")
    fresh = (
        isinstance(existing_base, dict)
        and existing_base.get("reference") == reference
        and existing_base.get("lock-digest") == base.recommendation_digest
    )
    answer = elicitor.seek(
        "base-image",
        description=f"Authorize this checkout to execute {base.display_value or reference}? (yes/no)",
        remedy=f"--authorize base-image {reference}",
        existing="yes" if fresh else None,
        empty_answer="yes",
        validate=_base_answer_validator("base-image", reference),
    )
    if answer is not None:
        if answer.value == "no":
            raise ProjectConfigurationError(
                "Initialization needs the base authorization to reach a fresh resolution; "
                "declined. Authorize later with 'devcapsule project config authorize "
                f"base-image {reference}' and run 'devcapsule project config resolve'."
            )
        if answer.value != "yes":
            _record_base_selection(
                elicitor,
                record,
                base,
                selection=answer.value,
                recommended=reference,
                platform=platform,
                less_pedantic=less_pedantic,
            )
            authorized.append("base-image")
            return _elicit_component_acquisitions(elicitor, declarations, record, authorized)
        record.authorization["base-image"] = {
            "reference": reference,
            "lock-digest": base.recommendation_digest,
        }
        authorized.append("base-image")
    return _elicit_component_acquisitions(elicitor, declarations, record, authorized)


def _elicit_component_acquisitions(
    elicitor: Elicitor,
    declarations: Mapping[str, Any],
    record: CheckoutRecord,
    authorized: list[str],
) -> list[str]:
    """Ask every component acquisition the lock's formation requires.

    The declarations derive from the locked components' vendor contracts
    (Claude Code, Antigravity CLI, …), one authorization node each; the
    question wording and the persistence shape are uniform so a new curated
    component never needs its own elicitation code.
    """

    for declaration in declarations.values():
        if declaration.kind != "acquisition":
            continue
        existing = record.authorization.get(declaration.name)
        fresh = (
            isinstance(existing, dict)
            and existing.get("recommendation-digest") == declaration.recommendation_digest
        )
        answer = elicitor.seek(
            declaration.name,
            description=f"{declaration.description} Authorize? (yes/no)",
            remedy=f"--authorize {declaration.name} true",
            existing="yes" if fresh else None,
            empty_answer="yes",
            validate=_acquisition_validator(declaration.name, "true"),
        )
        if answer is None:
            continue
        if answer.value == "no":
            raise ProjectConfigurationError(
                f"Initialization needs the {declaration.subject} acquisition answered; "
                f"declined. Remove {declaration.capability!r} from capabilities.need or "
                f"authorize with 'devcapsule project config authorize "
                f"{declaration.name} true'."
            )
        record.authorization[declaration.name] = {
            "value": True,
            "recommendation-digest": declaration.recommendation_digest,
        }
        authorized.append(declaration.name)
    return authorized


def _acquisition_validator(name: str, accepted_value: str) -> Any:
    def validate(value: str) -> str:
        candidate = value.strip().lower()
        if candidate in {"yes", "y", accepted_value.lower()}:
            return "yes"
        if candidate in {"no", "n"}:
            return "no"
        raise ProjectConfigurationError(
            f"Authorization {name!r} accepts yes, no, or the exact value {accepted_value!r}."
        )

    return validate


def _looks_like_image_reference(value: str) -> bool:
    """A candidate the daemon could plausibly resolve: a tag/digest reference
    or a bare image ID — anything the developer might name a base by."""

    if not value or any(character.isspace() for character in value):
        return False
    if re.fullmatch(r"(sha256:)?[0-9a-f]{12,64}", value):
        return True
    return "/" in value or ":" in value or "@" in value


def _base_answer_validator(name: str, recommended: str) -> Any:
    """Like ``_acquisition_validator``, but a reference-shaped answer is a
    developer base selection rather than garbage (owner ruling 2026-09-03)."""

    def validate(value: str) -> str:
        candidate = value.strip()
        if candidate.lower() in {"yes", "y"} or candidate == recommended:
            return "yes"
        if candidate.lower() in {"no", "n"}:
            return "no"
        if _looks_like_image_reference(candidate):
            return candidate
        raise ProjectConfigurationError(
            f"Authorization {name!r} answers one question: execute the base the "
            f"resolution matrix selected from capabilities.need ({recommended})? "
            "Answer yes or no. To run a different base on this checkout, name a "
            "locally built or pulled image instead (tag or image ID) — DevCapsule "
            "reads its digest and metadata and asks you to confirm the selection "
            f"('--less-pedantic' skips the confirmation). {value!r} is neither an "
            "answer nor an image reference."
        )

    return validate


def _record_base_selection(
    elicitor: Elicitor,
    record: CheckoutRecord,
    declaration: Any,
    *,
    selection: str,
    recommended: str,
    platform: str,
    less_pedantic: bool,
) -> None:
    """Record a developer-owned base selection with informed consent.

    The selection must be daemon-local: trust binds to the inspected image
    ID (D-0004 — never to a mutable tag), and init resolves offline, so a
    reference the daemon cannot produce is refused with the pull remedy.
    """

    try:
        immutable_registry_reference(selection)
    except ProjectConfigurationError:
        pass
    else:
        # D-0004: a different *published* digest needs its own
        # project-reviewed metadata; only a daemon-local selection is exempt.
        raise ProjectConfigurationError(
            f"Published base {selection!r} is not the lock-recommended digest; "
            "a different published artifact requires distinct project-reviewed "
            "metadata. A locally built or pulled image (named by tag or image "
            "ID) can be selected for this checkout instead."
        )
    local_base = required_local_image(selection)
    validate_base_image(local_base, platform=platform, expected_identity=None)
    if not less_pedantic:
        base_labels = "\n".join(
            f"  {key} = {value}"
            for key, value in sorted(local_base.labels.items())
            if key.startswith("devcapsule.")
        )
        presentation = (
            f"The lock recommends base {recommended}.\n"
            f"You selected local base {selection}:\n"
            f"  Image ID: {local_base.identity}\n"
            f"  Platform: {local_base.operating_system}/{local_base.architecture}\n"
            + (f"{base_labels}\n" if base_labels else "")
            + "This developer-owned selection overrides the recommendation for "
            "this checkout only; trust binds to the image ID above.\n"
            f"Authorize {selection}? (yes/no)"
        )
        consent = elicitor.seek(
            "base-image",
            facet="confirmation",
            description=presentation,
            remedy="--less-pedantic (records the reviewed selection without this confirmation)",
            empty_answer="yes",
            validate=_acquisition_validator("base-image (confirmation)", "yes"),
        )
        if consent is None:
            return
        if consent.value == "no":
            raise ProjectConfigurationError(
                f"Base selection {selection!r} declined; re-run with the "
                "recommended base or a different selection."
            )
    record.authorization["base-image"] = {
        "reference": selection,
        "lock-digest": declaration.recommendation_digest,
        "image-id": local_base.identity,
    }


def _apply_extra_answers(
    answers: tuple[ProvidedAnswer, ...],
    manifest: Mapping[str, Any],
    lock: Mapping[str, Any],
    record: CheckoutRecord,
) -> None:
    """Apply optional --set/--bind answers through the node registry."""

    if not any(answer.family in (CARRIER_FAMILY_SET, CARRIER_FAMILY_BIND) for answer in answers):
        return
    registry = build_node_registry(manifest, lock)
    for answer in answers:
        if answer.family == CARRIER_FAMILY_SET:
            registry.answerable(answer.name, CARRIER_FAMILY_SET)
            record.values[answer.name] = normalize_configuration_value(
                manifest, answer.name, answer.value
            )
        elif answer.family == CARRIER_FAMILY_BIND:
            provider, value = registry.split_bind_value(answer.name, answer.value)
            if provider == PROVIDER_HOST_DIRECTORY:
                source = Path(value).expanduser().resolve()
                if not source.is_dir():
                    raise ProjectConfigurationError(
                        f"Binding source is not an existing directory: {source}"
                    )
                record.directory_bindings[answer.name] = str(source)
            else:
                declaration = registry.node(answer.name).declaration
                if value != declaration.environment_variable:
                    raise ProjectConfigurationError(
                        f"Secret input {answer.name!r} must use host environment variable "
                        f"{declaration.environment_variable!r}."
                    )
                record.environment_bindings[answer.name] = value


def add_capability_need(
    root: Path,
    names: Sequence[str],
    answers: tuple[ProvidedAnswer, ...] = (),
) -> InitializeReport:
    """Grow the project's capability need; everything downstream re-derives.

    The manifest gains the new names in its authored ``need`` line (a
    surgical textual edit — authored content is never rewritten from its
    parsed form), then the regenerate path rebuilds the lock from the
    current matrix, elicits any acquisition gates the new components bring
    (``--authorize`` carriers answer them noninteractively), and refreshes
    the resolution — so ``project run`` works immediately afterward.
    Adding an already-needed capability converges to the same state.
    """

    resolved_root = root.expanduser().resolve()
    manifest_path = resolved_root / ".devcapsule" / "devcapsule.toml"
    if not manifest_path.is_file():
        raise ProjectConfigurationError(
            f"{resolved_root} carries no project manifest; run 'devcapsule project init' first."
        )
    manifest = load_toml(manifest_path)
    validate_manifest(manifest, manifest_path)
    matrix = _current_matrix()
    current = matrix.normalize(manifest.get("capabilities", {}).get("need", []))
    requested = matrix.normalize([*current, *names])
    if requested != current:
        # Pre-flight the grown need before touching authored content: an
        # unresolvable set (a second surface, no verified combination) must
        # leave the manifest exactly as it was.
        matrix.resolve(requested)
        _rewrite_manifest_need(manifest_path, requested)
    return initialize_project(
        InitializeRequest(directory=resolved_root, answers=answers, regenerate=True)
    )


def _rewrite_manifest_need(manifest_path: Path, need: tuple[str, ...]) -> None:
    """Replace the single authored ``need = […]`` line under ``[capabilities]``."""

    text = manifest_path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    in_capabilities = False
    replaced = False
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            in_capabilities = stripped == "[capabilities]"
            continue
        if in_capabilities and re.match(r"need\s*=\s*\[.*\]\s*$", stripped):
            newline = "\n" if line.endswith("\n") else ""
            lines[index] = (
                "need = [" + ", ".join(quote_toml(name) for name in need) + "]" + newline
            )
            replaced = True
            break
    if not replaced:
        raise ProjectConfigurationError(
            f"{manifest_path} has no single-line 'need = [...]' under [capabilities]; "
            "edit the manifest by hand and run 'devcapsule project init --regenerate'."
        )
    atomic_write(manifest_path, "".join(lines), mode=0o644)


def _fully_initialized(root: Path, manifest: Mapping[str, Any]) -> bool:
    """Whether all four owned artifacts stand with a fresh resolution.

    Partial and stale states stay init's own repair job; only this state
    makes a plain re-init meaningless.
    """

    _path, lock = lock_for(root, manifest)
    input_path, output_path = checkout_record_paths(manifest, root)
    if not input_path.is_file() or not output_path.is_file():
        return False
    checkout = load_toml(input_path)
    resolution = load_toml(output_path)
    if resolution.get("devcapsule-resolved-schema-version") != 1:
        return False
    if resolution.get("status") == "unresolved":
        return False
    if stale_resolution_inputs(manifest, lock, checkout, resolution):
        return False
    return True


def _apply_answers_to_standing_checkout(
    root: Path,
    manifest_path: Path,
    lock_path: Path,
    platform: Platform,
    request: InitializeRequest,
) -> InitializeReport:
    """Apply a repeated init's carried answers to the standing checkout.

    Init stays non-idempotent over authored artifacts — identity flags on a
    standing manifest are not re-authored here — but the invocation's
    authorization, set, and bind answers are applied exactly as the config
    family would apply them, and the resolution is refreshed so 'project
    run' works immediately afterward.
    """

    manifest = load_toml(manifest_path)
    validate_manifest(manifest, manifest_path)
    _, lock = lock_for(root, manifest)
    declarations = authorization_declarations(manifest, lock)
    record = CheckoutRecord(manifest, root)
    authorize_answers = {
        (answer.name, "value"): answer.value
        for answer in request.answers
        if answer.family == "authorize"
    }
    elicitor = Elicitor(authorize_answers, interactive=False)
    authorized = _elicit_acquisitions(
        elicitor,
        declarations,
        record,
        platform=str(platform),
        less_pedantic=request.less_pedantic,
    )
    elicitor.finish()
    _apply_extra_answers(request.answers, manifest, lock, record)
    record.write()
    resolve_report = resolve_checkout(root)

    project = manifest["project"]
    base_declaration = declarations.get("base-image")
    if base_declaration is not None:
        base_display = base_declaration.display_value or str(
            base_declaration.recommended_value
        )
    else:
        base_display = str(lock.get("image", {}).get("reference", "image lock"))
    return InitializeReport(
        manifest_path=manifest_path,
        manifest_action="Kept",
        project_name=str(project["name"]),
        creator=str(project["creator"]),
        slug=str(project["slug"]),
        project_mount=str(project["mount"]),
        capabilities=MATRICES[platform].normalize(
            manifest.get("capabilities", {}).get("need", [])
        ),
        lock_path=lock_path,
        lock_action="Kept",
        base_display=base_display,
        recommendations=(),
        authorized=tuple(authorized),
        checkout_record=record.input_path,
        resolve=resolve_report,
    )


def _normalize_creator(value: str) -> str:
    candidate = value.strip()
    if not candidate:
        raise ProjectConfigurationError("The project creator must not be empty.")
    return candidate if ":" in candidate else f"mailto:{candidate}"


def _normalize_need_string(value: str) -> str:
    names = [item for item in value.replace(",", " ").split() if item]
    return " ".join(_current_matrix().normalize(names))


def _write_manifest(
    manifest_path: Path,
    existing_manifest: Mapping[str, Any] | None,
    identity: _ProjectIdentity,
    recommendations: list[tuple[str, str]],
) -> str:
    """Author a fresh manifest, or append only what an existing one lacks.

    An existing manifest is authored content: it is never rewritten from its
    parsed form, which would destroy comments and fields init does not model.
    """

    if existing_manifest is None:
        lines = [
            "devcapsule-schema-version = 1",
            "",
            "[capabilities]",
            "need = [" + ", ".join(quote_toml(name) for name in identity.capabilities) + "]",
            "",
            "[project]",
            f"name = {quote_toml(identity.name)}",
            f"slug = {quote_toml(identity.slug)}",
            f"creator = {quote_toml(identity.creator)}",
            f"mount = {quote_toml(identity.mount)}",
        ]
        for name, justification in recommendations:
            lines.extend(_recommendation_block(name, justification))
        manifest_path.parent.mkdir(mode=0o755, exist_ok=True)
        atomic_write(manifest_path, "\n".join(lines) + "\n", mode=0o644)
        return "Created"

    host = existing_manifest.get("host", {})
    appended = False
    content = manifest_path.read_text(encoding="utf-8")
    for name, justification in recommendations:
        path = CURATED_HOST_RECOMMENDATIONS[name][0]
        if _declared_recommendation(host if isinstance(host, Mapping) else {}, path) is not None:
            continue
        content = content.rstrip("\n") + "\n" + "\n".join(
            _recommendation_block(name, justification)
        ) + "\n"
        appended = True
    if appended:
        atomic_write(manifest_path, content, mode=0o644)
        return "Updated"
    return "Honored existing"


def _recommendation_block(name: str, justification: str) -> list[str]:
    path, supported = CURATED_HOST_RECOMMENDATIONS[name]
    value: AuthorizationScalar = supported
    return [
        "",
        f"[host.{'.'.join(path)}]",
        f"value = {render_toml_scalar(value)}",
        f"justification = {quote_toml(justification)}",
    ]


def _checkout_values(checkout: Mapping[str, Any]) -> dict[str, Any]:
    configuration = checkout.get("configuration", {})
    if not isinstance(configuration, dict):
        raise ProjectConfigurationError("Checkout configuration must be a table.")
    values = configuration.get("values", {})
    if not isinstance(values, dict):
        raise ProjectConfigurationError("Checkout configuration.values must be a table.")
    return dict(values)


def _checkout_host_directory_bindings(checkout: Mapping[str, Any]) -> dict[str, str]:
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


def _checkout_host_environment_bindings(checkout: Mapping[str, Any]) -> dict[str, str]:
    configuration = checkout.get("configuration", {})
    if not isinstance(configuration, dict):
        raise ProjectConfigurationError("Checkout configuration must be a table.")
    bindings = configuration.get("bindings", {})
    if not isinstance(bindings, dict):
        raise ProjectConfigurationError("Checkout configuration.bindings must be a table.")
    host_environment = bindings.get("host-environment", {})
    if not isinstance(host_environment, dict) or not all(
        isinstance(name, str) and isinstance(source, str)
        for name, source in host_environment.items()
    ):
        raise ProjectConfigurationError(
            "Checkout configuration.bindings.host-environment must contain environment names."
        )
    return dict(host_environment)
