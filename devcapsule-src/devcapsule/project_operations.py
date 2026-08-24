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
from typing import Any, Mapping

from devcapsule.environment_realization import required_local_image
from devcapsule.materialization import validate_base_image
from devcapsule.project_configuration import (
    ProjectConfigurationError,
    atomic_write,
    authorized_base_selection,
    canonical_digest,
    checkout_record_paths,
    load_toml,
    lock_for,
    manifest_for,
    quote_toml,
    render_checkout,
    render_toml_scalar,
    resolve_configuration_bindings,
    resolve_configuration_values,
    resolve_secret_bindings,
    resolution_source_digests,
    resolved_checkout_authorizations,
)

__all__ = [
    "CheckoutRecord",
    "ResolveReport",
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
    if component != "pycharm" or (not image and not has_formation):
        raise ProjectConfigurationError(
            "The V1 slice requires a lock selecting either a completed PyCharm image "
            "or PyCharm formation inputs."
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
