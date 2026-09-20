"""Pure serialization of a complete, assessed configuration checkpoint.

Resolution, execution verification and predecessor compatibility use this same
projection. No Docker, secret reads, or file writes occur here.
"""
from __future__ import annotations

import tomllib
from typing import Any, Mapping

from devcapsule.configuration_review import ConfigurationReview, review_configuration
from devcapsule.project_configuration import (
    ProjectConfigurationError, authorized_base_selection, canonical_digest,
    checkout_omitted_values, quote_toml, render_toml_scalar, resolution_source_digests,
)


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
    # Python equality equates True with 1; configuration meaning does not.
    return canonical_digest({k: v for k, v in expected.items() if k != "sources"}) == canonical_digest({
        k: v for k, v in resolution.items() if k != "sources"
    })
