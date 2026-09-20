"""Host and acquisition decisions, base trust and explicit recovery choices."""

from __future__ import annotations
import re
import shlex
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping
from devcapsule.components.catalog import COMPONENTS

from .documents import AuthorizationScalar, ProjectConfigurationError, canonical_digest


OCI_REPOSITORY_COMPONENT_PATTERN = re.compile(r"^[a-z0-9]+(?:[._-][a-z0-9]+)*$")


OCI_REGISTRY_HOST_PATTERN = re.compile(r"^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$")


SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


RELEASE_BUILD_MNEMONIC_PATTERN = re.compile(r"^v[0-9][0-9A-Za-z._-]*$")


# The curated V1 host-access recommendation vocabulary.  Each entry maps a
# node's canonical name to the manifest subtree that declares its
# recommendation and to the single supported V1 value.  ``init`` asks exactly
# these questions when it authors a manifest, and ``authorization_declarations``
# turns present declarations into authorization nodes; they share this one
# table so the asked question and the honored declaration cannot drift.
CURATED_HOST_RECOMMENDATIONS: dict[str, tuple[tuple[str, ...], AuthorizationScalar]] = {
    "docker-daemon": (("docker", "mode", "recommended"), "host-socket"),
    "network": (("network", "mode", "recommended"), "host"),
    "development-sudo": (("privilege", "development-sudo", "recommended"), True),
    "host-browser": (("browser", "host-open", "recommended"), True),
}


# Host capabilities that exist as authorization nodes on every project,
# whether or not the project recommends them. Settled by the product owner on
# 2026-08-24: host-browser, docker-daemon, and development-sudo are proper
# configuration nodes under authorize. These are developer-owned choices —
# "Denial is the default. The developer may deny it, allow it once, allow it
# for this checkout" — so their availability cannot depend on the project's
# advice; a recommendation merely attaches the project's justification and
# rebinds the answer to it. Host networking is deliberately absent: its
# run-once form is the raw docker passthrough, and its persistent relaxation
# remains a project-recommended decision.
WORKSTATION_CAPABILITY_DEFAULTS: dict[str, tuple[AuthorizationScalar, str]] = {
    "docker-daemon": (
        "host-socket",
        "Expose the host Docker daemon socket to the capsule; this permits broad "
        "control of the host.",
    ),
    "development-sudo": (
        True,
        "Enable the declared development-sudo behavior inside the capsule.",
    ),
    "host-browser": (
        True,
        "Open HTTP(S) links from the capsule in the physical host's default browser "
        "through the URL-only broker.",
    ),
    # Host X11 passthrough survives only as this node (contained-display
    # design note, T7): never a default, never a project recommendation,
    # and the trade-off is stated where the answer is given.
    "host-x11": (
        True,
        "Run the IDE on the host's X session instead of the capsule's contained "
        "display, handing the capsule your full X session credential: keystroke "
        "capture across the session, window capture, input injection, and "
        "clipboard access. The session-credential boundary test is waived for such runs.",
    ),
}


# Each string-valued authorization node's deny spelling — the value the run
# path falls back to when nothing grants the capability. Recording it is the
# developer's reduce-privilege decision (owner rulings 2026-09-03: denial is a
# *value*, so a checkout's recorded denial outranks a workstation-level
# allow); bool nodes deny with plain ``false`` and need no entry here.
AUTHORIZATION_DENY_VALUES: dict[str, str] = {
    "docker-daemon": "none",
    "network": "bridge",
}


def authorization_deny_value(declaration: "AuthorizationDeclaration") -> AuthorizationScalar | None:
    """The node's deny value, or None for nodes with no deny state (base-image)."""

    if isinstance(declaration.recommended_value, bool):
        return False
    return AUTHORIZATION_DENY_VALUES.get(declaration.name)


@dataclass(frozen=True)
class AuthorizationDeclaration:
    name: str
    recommended_value: AuthorizationScalar
    recommendation_digest: str
    description: str
    display_value: str | None = None
    # False for workstation-capability defaults the project did not recommend;
    # bulk authorization of "everything recommended" must not include them.
    project_recommended: bool = True
    # "acquisition" nodes gate a vendor download with per-user terms; init has
    # no safe omission for them and asks each one. Everything else is "host".
    kind: str = "host"
    # For acquisition nodes: the capability whose removal from the need is the
    # alternative to authorizing, and the vendor product name for messages.
    capability: str | None = None
    subject: str | None = None

    @property
    def required(self) -> bool:
        """Selected executables/acquisitions require consent; host access does not."""
        return self.name == "base-image" or self.kind == "acquisition"


@dataclass(frozen=True)
class AuthorizedBaseSelection:
    """Developer-approved base bound to the current lock and optional local image ID."""

    reference: str
    lock_digest: str
    local_image_identity: str | None = None

    @property
    def is_local(self) -> bool:
        return self.local_image_identity is not None


@dataclass(frozen=True)
class AuthorizationChoice:
    """An explicit decision, never an instruction to grant permission implicitly."""

    name: str
    value: str
    meaning: str

    def command(self, project: Path | None = None) -> str:
        context = ["--path", str(project)] if project is not None else []
        return shlex.join(["devcapsule", "project", *context, "config", "authorize", self.name, self.value])


@dataclass(frozen=True)
class AuthorizationReview:
    """One interpretation of a recorded answer for inspection and resolution.

    A problem prevents resolution. Choices are alternatives, not a script to
    execute in sequence. A valid denial remains a denial even when the project
    recommends granting the capability.
    """

    name: str
    status: str
    recorded: str
    recommended: str
    description: str
    value: AuthorizationScalar | None = None
    problem: str | None = None
    choices: tuple[AuthorizationChoice, ...] = ()

    def render(self, project: Path | None = None) -> str:
        lines = [
            f"{self.name}: {self.status}; recorded: {self.recorded}; recommended: {self.recommended}",
            f"  {self.description}",
        ]
        if self.problem is not None:
            lines.append(f"  {self.problem}")
        for choice in self.choices:
            lines.append(f"  {choice.meaning}: {choice.command(project)}")
        return "\n".join(lines)


def authorization_declarations(
    manifest: Mapping[str, Any], lock: Mapping[str, Any]
) -> dict[str, AuthorizationDeclaration]:
    """Build the curated V1 authorization catalog from project recommendations."""

    declarations: dict[str, AuthorizationDeclaration] = {}
    if "base" in lock:
        reference = locked_base_reference(lock)
        build_mnemonic = locked_base_build_mnemonic(lock)
        display_value = (
            f"{build_mnemonic} — {reference}" if build_mnemonic is not None else None
        )
        declarations["base-image"] = AuthorizationDeclaration(
            name="base-image",
            recommended_value=reference,
            recommendation_digest=canonical_digest(lock),
            description=(
                f"Execute DevCapsule {build_mnemonic} at the exact registry digest selected "
                "by the platform lock."
                if build_mnemonic is not None
                else "Execute the exact registry digest selected by the platform lock."
            ),
            display_value=display_value,
        )

    components = lock.get("components", {})
    if not isinstance(components, dict):
        raise ProjectConfigurationError("Platform lock components must be a table.")
    for component_id, metadata in components.items():
        if component_id == "interactive-surface":
            continue
        definition = COMPONENTS.get(component_id) if isinstance(component_id, str) else None
        if definition is None:
            # Unknown ids fail later at catalog selection.
            continue
        contract = definition.acquisition()
        if contract is None:
            # Components without vendor terms need no acquisition authorization.
            continue
        if not isinstance(metadata, dict):
            raise ProjectConfigurationError(f"components.{component_id} must be a table.")
        if metadata.get("acquisition-authorization") != contract.authorization:
            raise ProjectConfigurationError(
                f"components.{component_id} must declare acquisition-authorization = "
                f"{contract.authorization!r}."
            )
        if metadata.get("terms-url") != contract.terms_url:
            raise ProjectConfigurationError(
                f"components.{component_id} terms-url must be {contract.terms_url!r}."
            )
        version = metadata.get("version")
        if not isinstance(version, str) or not version:
            raise ProjectConfigurationError(
                f"components.{component_id}.version must be a non-empty string."
            )
        declarations[contract.authorization] = AuthorizationDeclaration(
            name=contract.authorization,
            recommended_value=True,
            recommendation_digest=canonical_digest(
                {"name": contract.authorization, "component": metadata}
            ),
            description=(
                f"Download checksum-pinned {contract.display_name} {version} directly "
                f"from {contract.vendor} during local materialization, subject to "
                f"{contract.terms_url}."
            ),
            kind="acquisition",
            capability=definition.capability,
            subject=contract.display_name,
        )

    host = manifest.get("host", {})
    if not isinstance(host, dict):
        raise ProjectConfigurationError("Project declaration host metadata must be a table.")
    for name, (path, supported_value) in CURATED_HOST_RECOMMENDATIONS.items():
        recommendation: object = host
        for key in path:
            if not isinstance(recommendation, dict) or key not in recommendation:
                recommendation = None
                break
            recommendation = recommendation[key]
        if recommendation is None:
            continue
        if not isinstance(recommendation, dict):
            raise ProjectConfigurationError(
                f"Project authorization recommendation for {name!r} must be a table."
            )
        value = recommendation.get("value")
        justification = recommendation.get("justification")
        if type(value) is not type(supported_value) or value != supported_value:
            raise ProjectConfigurationError(
                f"Project recommendation {name!r} must use the supported V1 value "
                f"{supported_value!r}; found {value!r}."
            )
        if not isinstance(justification, str) or not justification:
            raise ProjectConfigurationError(
                f"Project recommendation {name!r} must include a non-empty justification."
            )
        declarations[name] = AuthorizationDeclaration(
            name=name,
            recommended_value=supported_value,
            recommendation_digest=canonical_digest({"name": name, "recommendation": recommendation}),
            description=justification,
        )
    for name, (supported_value, description) in WORKSTATION_CAPABILITY_DEFAULTS.items():
        if name in declarations:
            continue
        # The digest is a stable constant distinct from every recommendation
        # digest, so a later project recommendation correctly stales the
        # workstation-default answer: the question changed, so it is re-asked.
        declarations[name] = AuthorizationDeclaration(
            name=name,
            recommended_value=supported_value,
            recommendation_digest=canonical_digest(
                {"name": name, "recommendation": "workstation-default"}
            ),
            description=description,
            project_recommended=False,
        )
    return declarations


def normalize_authorization_value(
    declaration: AuthorizationDeclaration, value: object
) -> AuthorizationScalar:
    expected = declaration.recommended_value
    deny = authorization_deny_value(declaration)
    if isinstance(value, str):
        keyword = value.strip().lower()
        if keyword == "default":
            # The reserved keyword accepting the recommendation for one key
            # (owner ruling 2026-09-03); the bulk counterpart is
            # --all-recommended. Input artifact only: the resolved value is
            # what gets stored.
            return expected
        if keyword == "none":
            # The reserved denial keyword (owner ruling 2026-09-03): resolves
            # to the node's deny value at decision time and stores it, so a
            # checkout's recorded denial outranks a workstation-level allow.
            if deny is None:
                raise ProjectConfigurationError(
                    f"Authorization {declaration.name!r} is mandatory and has no deny "
                    "state; 'none' cannot apply. Accept the recommendation with "
                    "'default' or record a different selection."
                )
            return deny
    if isinstance(expected, bool):
        if isinstance(value, str) and value.lower() in {"true", "false"}:
            normalized: AuthorizationScalar = value.lower() == "true"
        elif isinstance(value, bool):
            normalized = value
        else:
            raise ProjectConfigurationError(
                f"Authorization {declaration.name!r} requires true or false."
            )
    elif isinstance(value, str):
        normalized = value
    else:  # pragma: no cover - AuthorizationScalar makes this defensive only.
        raise ProjectConfigurationError(f"Unsupported authorization metadata for {declaration.name!r}.")
    if normalized != expected and (deny is None or normalized != deny):
        # Deliberately source-neutral: the recommendation may be a project's
        # or a workstation default, and denial is always the developer's to
        # record — only values *beyond* recommendation-or-deny need reviewed
        # metadata (2026-09-02 denial-grammar bug, aggravations 1 and 2).
        accepted = f"its recommended value {render_authorization_value(expected)!r}"
        if deny is not None:
            accepted += f", its deny value {render_authorization_value(deny)!r}"
        raise ProjectConfigurationError(
            f"Authorization {declaration.name!r} accepts {accepted}, or the keywords "
            f"'default'/'none'; got {normalized!r}. Any other value requires distinct "
            "reviewed metadata."
        )
    return normalized


def base_recovery_choices(record: Mapping[str, Any]) -> tuple[AuthorizationChoice, ...]:
    """Always offer the reviewed pin; renew a local override only by exact ID.

    The old published digest is not an accepted value under the new lock.
    Replaying a local tag is also wrong: it may now point at different bytes.
    """

    choices = [AuthorizationChoice("base-image", "default", "Accept the current project recommendation")]
    identity = record.get("image-id")
    if (
        isinstance(identity, str)
        and identity.startswith("sha256:")
        and SHA256_PATTERN.fullmatch(identity.removeprefix("sha256:")) is not None
    ):
        choices.append(AuthorizationChoice(
            "base-image", identity, "Keep the exact local image, if still available and valid"
        ))
    return tuple(choices)


def _authorization_choices(
    declaration: AuthorizationDeclaration, recorded_value: AuthorizationScalar | None
) -> tuple[AuthorizationChoice, ...]:
    """Construct only values accepted by this declaration's own validator."""

    if declaration.kind == "acquisition":
        # Keeping a declined mandatory acquisition is legitimate, but is not
        # a recovery action: the selected environment then cannot be built.
        return (AuthorizationChoice(declaration.name, "true", "Authorize the selected acquisition after review"),)
    values: list[tuple[AuthorizationScalar, str]] = []
    if recorded_value is not None:
        values.append((recorded_value, "Keep the recorded decision after review"))
    values.append((declaration.recommended_value, "Accept the current recommendation"))
    deny = authorization_deny_value(declaration)
    # Base selection has its own choices; all remaining host nodes have a
    # denial state by the curated authorization contract.
    assert deny is not None
    values.append((deny, "Deny this capability"))
    choices: list[AuthorizationChoice] = []
    for value, meaning in values:
        normalized = normalize_authorization_value(declaration, value)
        rendered = render_authorization_value(normalized)
        if all(choice.value != rendered for choice in choices):
            choices.append(AuthorizationChoice(declaration.name, rendered, meaning))
    return tuple(choices)


def review_authorizations(
    manifest: Mapping[str, Any], lock: Mapping[str, Any], checkout: Mapping[str, Any]
) -> tuple[AuthorizationReview, ...]:
    """Assess every authorization without writes, Docker calls or early refusal.

    The same result drives inspection and resolution. Missing optional host
    access is safe; missing base consent or selected vendor acquisition is not
    run-ready. Stale answers must be renewed, never silently reinterpreted.
    """

    declarations = authorization_declarations(manifest, lock)
    records = checkout.get("authorization", {})
    if not isinstance(records, dict):
        raise ProjectConfigurationError("Checkout authorization must be a table.")
    reviews: list[AuthorizationReview] = []
    for name, declaration in sorted(declarations.items()):
        record = records.get(name)
        required = declaration.required
        recommended = declaration.display_value or render_authorization_value(declaration.recommended_value)
        recorded = "unanswered"
        value: AuthorizationScalar | None = None
        problem: str | None = None
        choices: tuple[AuthorizationChoice, ...] = ()
        if name not in records:
            status = "missing-required" if required else (
                "missing-recommended" if declaration.project_recommended else "available"
            )
            if required:
                problem = "An explicit decision is required before this environment can run."
        elif not isinstance(record, dict):
            status = "invalid"
            problem = f"Checkout authorization {name!r} must be a table."
        elif name == "base-image":
            recorded = str(record.get("reference", "missing reference"))
            if record.get("image-id") is not None:
                recorded += f" (local image {record['image-id']})"
            try:
                selection = authorized_base_selection(lock, checkout)
            except ProjectConfigurationError as exc:
                status = "stale" if (
                    isinstance(record.get("reference"), str) and record["reference"]
                    and record.get("lock-digest") != declaration.recommendation_digest
                ) else "invalid"
                problem = (
                    "The recorded base selection was authorized against a different lock. "
                    "Review the previous selection and current recommendation before choosing."
                    if status == "stale" else str(exc)
                )
            else:
                assert selection is not None  # required=True either returns a selection or raises
                status = "authorized-local" if selection.is_local else "authorized"
                value = selection.reference
        else:
            recorded = str(record.get("value", "missing value")).lower() if isinstance(
                record.get("value"), bool
            ) else str(record.get("value", "missing value"))
            try:
                value = normalize_authorization_value(declaration, record.get("value"))
            except ProjectConfigurationError as exc:
                status = "invalid"
                problem = str(exc)
            else:
                if record.get("recommendation-digest") != declaration.recommendation_digest:
                    status = "stale"
                    problem = "The recommendation changed; review it and explicitly renew or change your answer."
                elif value == authorization_deny_value(declaration):
                    status = "denied"
                    if required:
                        problem = (
                            f"The selected {declaration.subject} acquisition is denied. "
                            f"Remove {declaration.capability!r} from the project need, or explicitly authorize it."
                        )
                else:
                    status = "authorized"
        if problem is not None:
            choices = (
                base_recovery_choices(record if isinstance(record, dict) else {})
                if name == "base-image"
                else _authorization_choices(declaration, value)
            )
        reviews.append(AuthorizationReview(
            name, status, recorded, recommended, declaration.description, value, problem, choices
        ))
    for name in sorted(set(records) - set(declarations)):
        reviews.append(AuthorizationReview(
            name, "unsupported", "recorded", "not declared", "This node no longer belongs to the project configuration.",
            problem="Remove the obsolete entry from the checkout authorization table after review.",
        ))
    return tuple(reviews)


def resolved_checkout_authorizations(
    manifest: Mapping[str, Any], lock: Mapping[str, Any], checkout: Mapping[str, Any]
) -> dict[str, AuthorizationScalar]:
    reviews = review_authorizations(manifest, lock, checkout)
    problems = [review for review in reviews if review.problem is not None]
    if problems:
        raise ProjectConfigurationError(
            "Configuration needs authorization decisions:\n"
            + "\n".join(review.render() for review in problems)
        )
    return {review.name: review.value for review in reviews if review.value is not None}


def render_authorization_value(value: AuthorizationScalar) -> str:
    return str(value).lower() if isinstance(value, bool) else value


def immutable_registry_reference(reference: str) -> str:
    """Require a globally named OCI repository pinned by one SHA-256 digest."""

    name, separator, digest = reference.rpartition("@sha256:")
    if not separator or not SHA256_PATTERN.fullmatch(digest):
        raise ProjectConfigurationError(
            "Base references in committed locks must end with one immutable @sha256:<64-hex-digest>."
        )
    registry, slash, repository = name.partition("/")
    if not slash or not repository:
        raise ProjectConfigurationError(
            "Base references in committed locks must include an explicit global registry such as docker.io."
        )
    registry_host, colon, port = registry.rpartition(":")
    if not colon:
        registry_host = registry
    elif not port.isdigit():
        raise ProjectConfigurationError("The registry port in a committed base reference must be numeric.")
    normalized_host = registry_host.lower()
    if (
        not OCI_REGISTRY_HOST_PATTERN.fullmatch(normalized_host)
        or ".." in normalized_host
        or "." not in normalized_host
        or normalized_host == "localhost"
        or normalized_host.startswith("127.")
        or normalized_host == "0.0.0.0"
    ):
        raise ProjectConfigurationError(
            "Base references in committed locks must use a globally resolvable registry, not a local daemon name."
        )
    if registry != registry.lower() or repository != repository.lower():
        raise ProjectConfigurationError("Committed base registry and repository names must be lowercase.")
    if ":" in repository or any(
        not OCI_REPOSITORY_COMPONENT_PATTERN.fullmatch(component)
        for component in repository.split("/")
    ):
        raise ProjectConfigurationError(
            "Committed base references must name an OCI repository without a mutable tag."
        )
    return reference


def locked_base_reference(lock: Mapping[str, Any], *, source: str = "platform lock") -> str:
    base = lock.get("base")
    if not isinstance(base, dict):
        raise ProjectConfigurationError(f"{source} does not define formation base inputs.")
    reference = base.get("reference")
    if not isinstance(reference, str) or not reference:
        raise ProjectConfigurationError(f"{source} base.reference must be a non-empty string.")
    try:
        return immutable_registry_reference(reference)
    except ProjectConfigurationError as exc:
        raise ProjectConfigurationError(f"Invalid {source} base.reference {reference!r}: {exc}") from exc


def locked_base_build_mnemonic(lock: Mapping[str, Any]) -> str | None:
    base = lock.get("base")
    if not isinstance(base, dict):
        raise ProjectConfigurationError("Platform lock does not define formation base inputs.")
    value = base.get("build-mnemonic")
    if value is None:
        return None
    if not isinstance(value, str) or RELEASE_BUILD_MNEMONIC_PATTERN.fullmatch(value) is None:
        raise ProjectConfigurationError(
            "Platform lock base.build-mnemonic must be a release mnemonic such as 'v026'."
        )
    return value


def authorized_base_selection(
    lock: Mapping[str, Any],
    checkout: Mapping[str, Any],
    *,
    required: bool = True,
) -> AuthorizedBaseSelection | None:
    locked_reference = locked_base_reference(lock)
    build_mnemonic = locked_base_build_mnemonic(lock)
    authorization_root = checkout.get("authorization")
    authorization = (
        authorization_root.get("base-image") if isinstance(authorization_root, dict) else None
    )
    command = f"devcapsule project config authorize base-image {locked_reference}"
    if not isinstance(authorization, dict):
        if required:
            recognizable_base = (
                f"DevCapsule {build_mnemonic} base {locked_reference}"
                if build_mnemonic is not None
                else f"base {locked_reference}"
            )
            raise ProjectConfigurationError(
                f"The lock recommends {recognizable_base}, but this checkout has not authorized it; "
                f"run '{command}', or explicitly authorize an inspected local DevCapsule base."
            )
        return None
    authorized_reference = authorization.get("reference")
    if not isinstance(authorized_reference, str) or not authorized_reference:
        raise ProjectConfigurationError(
            "The checkout's base-image authorization must contain a non-empty reference."
        )
    authorized_lock = authorization.get("lock-digest")
    expected_lock = canonical_digest(lock)
    if authorized_lock != expected_lock:
        choices = base_recovery_choices(authorization)
        raise ProjectConfigurationError(
            "The checkout's base-image authorization is stale for the current lock; "
            f"previous selection: {authorized_reference}; current recommendation: {locked_reference}. "
            + " ".join(f"{choice.meaning}: {choice.command()}." for choice in choices)
        )
    local_identity = authorization.get("image-id")
    if authorized_reference == locked_reference:
        if local_identity is not None:
            raise ProjectConfigurationError(
                "The lock-recommended base-image authorization must not contain a local image ID."
            )
        return AuthorizedBaseSelection(
            reference=authorized_reference,
            lock_digest=expected_lock,
        )
    try:
        immutable_registry_reference(authorized_reference)
    except ProjectConfigurationError:
        pass
    else:
        raise ProjectConfigurationError(
            f"Published base {authorized_reference!r} is not the lock-recommended digest; "
            "a different published artifact requires distinct project-reviewed metadata."
        )
    if (
        not isinstance(local_identity, str)
        or not local_identity.startswith("sha256:")
        or not SHA256_PATTERN.fullmatch(local_identity.removeprefix("sha256:"))
    ):
        raise ProjectConfigurationError(
            "A non-recommended base-image authorization must be bound to an exact local "
            "Docker image ID; rerun "
            f"'devcapsule project config authorize base-image {authorized_reference}'."
        )
    return AuthorizedBaseSelection(
        reference=authorized_reference,
        lock_digest=expected_lock,
        local_image_identity=local_identity,
    )


def authorized_base_reference(
    lock: Mapping[str, Any],
    checkout: Mapping[str, Any],
    *,
    required: bool = True,
) -> str | None:
    """Compatibility accessor for consumers needing only the selected reference."""

    selection = authorized_base_selection(lock, checkout, required=required)
    return selection.reference if selection is not None else None
