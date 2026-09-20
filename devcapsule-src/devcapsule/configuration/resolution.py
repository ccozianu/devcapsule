"""Pure serialization of a complete, assessed configuration checkpoint.

Resolution, execution verification and predecessor compatibility use this same
projection. No Docker, secret reads, or file writes occur here.
"""
from __future__ import annotations

from copy import deepcopy
import tomllib
from typing import Any, Mapping
from devcapsule.components.catalog import INTERACTIVE_SURFACES
from devcapsule.project import ProjectMountError, normalize_project_mount

from .authorization import authorized_base_selection
from .documents import (
    Artifact,
    ProjectConfigurationError,
    admit_document,
    canonical_digest,
    quote_toml,
    render_toml_scalar,
    table,
)
from .fingerprints import resolution_source_digests
from .review import ConfigurationReview, HostAccess, review_configuration
from .values import checkout_omitted_values


def render_resolution(manifest: Mapping[str, Any], lock: Mapping[str, Any],
                      checkout: Mapping[str, Any], review: ConfigurationReview) -> str:
    if not review.ready:
        raise ProjectConfigurationError("Cannot publish an incomplete configuration.")
    image = lock.get("image", {}).get("reference")
    component = lock.get("components", {}).get("interactive-surface")
    state = checkout.get("state", {}).get("adopted", {})
    host = checkout.get("host", {})
    values, runtime_effects = review.values, review.runtime_effects
    bindings, secret_bindings = review.bindings, review.secret_bindings
    authorizations = review.resolved_authorizations()
    sources = resolution_source_digests(manifest, lock, checkout)
    lines = [
        "devcapsule-resolved-schema-version = 1",
        "",
        "[sources]",
        f"manifest = {quote_toml(sources['manifest'])}",
        f"platform-lock = {quote_toml(sources['platform-lock'])}",
        f"checkout-input = {quote_toml(sources['checkout-input'])}",
        'workstation-config = "absent"',
        'manifest-scope = "configuration-v1"',
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
    omitted = checkout_omitted_values(checkout)
    if omitted:
        # Explicit omissions are inspectable decisions, not silent gaps.
        rendered_names = ", ".join(quote_toml(name) for name in omitted)
        lines.extend(["", "[configuration]", f"omitted-values = [{rendered_names}]"])
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
    if "base-image" in authorizations:
        base_selection = authorized_base_selection(lock, checkout)
        if base_selection is None:  # pragma: no cover - authorized_base establishes it.
            raise ProjectConfigurationError("Resolved base-image authorization is missing.")
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
    return "\n".join(lines) + "\n"


def same_effective_resolution(manifest: Mapping[str, Any], lock: Mapping[str, Any],
                              checkout: Mapping[str, Any], resolution: Mapping[str, Any]) -> bool:
    """Compare a predecessor's derived meaning, not its retired digest algorithm."""
    review = review_configuration(manifest, lock, checkout)
    if not review.ready:
        return False
    expected = tomllib.loads(render_resolution(manifest, lock, checkout, review))
    return Resolution(expected).same_meaning_as(Resolution(resolution))


class Resolution:
    """A well-formed runtime plan with separate meaning and freshness.

    Decoding establishes a supported plan shape, not execution permission.
    Only Configuration.accept establishes that this plan belongs to its inputs.
    """

    def __init__(self, document: Mapping[str, Any]) -> None:
        admit_document(document, Artifact.resolution, "resolution")
        self._document = deepcopy(dict(document))
        runtime = table(self._document, "runtime")
        component = runtime.get("component")
        mount = runtime.get("project-mount")
        memory = runtime.get("memory-limit-bytes")
        image = runtime.get("image")
        if (not isinstance(component, str) or component not in INTERACTIVE_SURFACES
                or not isinstance(mount, str) or not mount.startswith("/") or "\x00" in mount):
            raise ProjectConfigurationError("Run requires a valid resolved runtime; run 'devcapsule project config resolve'.")
        try:
            normalize_project_mount(mount, "resolved-project")
        except ProjectMountError as exc:
            raise ProjectConfigurationError(str(exc)) from exc
        if memory is not None and (type(memory) is not int or memory <= 0):
            raise ProjectConfigurationError("Resolved runtime.memory-limit-bytes must be a positive integer.")
        if image is not None and (not isinstance(image, str) or not image):
            raise ProjectConfigurationError("Resolved runtime.image must be a non-empty string.")

    def document(self) -> dict[str, Any]:
        """Export an owned document for the persistence/launch adapter."""
        return deepcopy(self._document)

    def same_meaning_as(self, other: Resolution) -> bool:
        """Compare derived plans, deliberately excluding source fingerprints.

        This is not equality of resolutions: equivalent plans may differ in
        freshness, which is a separate observation made by Configuration.
        """
        return self._meaning() == other._meaning()

    def _meaning(self) -> str:
        return canonical_digest({k: v for k, v in self._document.items() if k != "sources"})

    @property
    def component(self) -> str:
        return self._document["runtime"]["component"]

    @property
    def project_mount(self) -> str:
        return self._document["runtime"]["project-mount"]

    @property
    def base_reference(self) -> str | None:
        base = table(self._document, "authorization", "base-image")
        reference = base.get("reference")
        if reference is not None and (not isinstance(reference, str) or not reference):
            raise ProjectConfigurationError("Resolved base reference must be a non-empty string.")
        return reference

    @property
    def host_access(self) -> HostAccess:
        authorizations = self._document.get("authorization", {})
        host_names = {"docker-daemon", "network", "development-sudo", "host-browser", "host-x11"}
        return HostAccess().overlay(self._document.get("host", {})).overlay({
            name: value for name, value in authorizations.items() if name in host_names
        })
