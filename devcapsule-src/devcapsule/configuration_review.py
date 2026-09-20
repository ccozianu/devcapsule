"""Read-only assessment of the decisions needed to resolve a checkout.

Inspection and resolution consume the same assessment. Validators own their
contracts; this module composes their results without publishing a partial
resolution or stopping at the first independent decision.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shlex
from typing import Any, Mapping

from devcapsule.project_configuration import (
    AuthorizationChoice,
    AuthorizationReview,
    AuthorizationScalar,
    ConfigurationScalar,
    ProjectConfigurationError,
    resolve_configuration_bindings,
    resolve_configuration_values,
    resolve_secret_bindings,
    review_authorizations,
)


@dataclass(frozen=True)
class ConfigurationReview:
    values: dict[str, ConfigurationScalar]
    runtime_effects: dict[str, int]
    bindings: dict[str, str]
    secret_bindings: dict[str, str]
    authorizations: tuple[AuthorizationReview, ...]
    problems: tuple[str, ...]

    @property
    def ready(self) -> bool:
        return not self.problems and all(item.problem is None for item in self.authorizations)

    def render(self, project: Path) -> str:
        lines = ["Configuration review: " + ("ready to resolve." if self.ready else "decisions required.")]
        lines.extend(self.problems)
        # Always show the base selection beside its recommendation, including
        # valid local overrides. Show pending decisions together, never serially.
        lines.extend(
            item.render(project) for item in self.authorizations
            if item.problem is not None or item.name == "base-image"
        )
        x11 = next((item for item in self.authorizations if item.name == "host-x11"), None)
        if x11 is not None and x11.value is None:
            allow = AuthorizationChoice("host-x11", "true", "").command(project)
            deny = AuthorizationChoice("host-x11", "false", "").command(project)
            lines.append(
                "Display: no host-x11 decision is recorded. A base with contained-display support "
                "uses its browser desktop by default; an older base uses host X11. "
                "An earlier implicit display default is not renewed host-access consent. "
                f"To explicitly choose host X11: {allow}\n"
                f"To require the contained desktop: {deny}\n"
                "The selected base is checked before building."
            )
        resolve = shlex.join(["devcapsule", "project", "--path", str(project), "config", "resolve"])
        lines.append(f"After settling your configuration choices, resolve explicitly: {resolve}")
        return "\n".join(lines)

    def require_ready(self, project: Path) -> None:
        if not self.ready:
            raise ProjectConfigurationError(self.render(project))

    def resolved_authorizations(self) -> dict[str, AuthorizationScalar]:
        # The caller must establish ready before consuming any partial output.
        if not self.ready:
            raise ProjectConfigurationError("Cannot consume an incomplete configuration review.")
        return {item.name: item.value for item in self.authorizations if item.value is not None}


def review_configuration(
    manifest: Mapping[str, Any], lock: Mapping[str, Any], checkout: Mapping[str, Any]
) -> ConfigurationReview:
    problems: list[str] = []
    values: dict[str, ConfigurationScalar] = {}
    effects: dict[str, int] = {}
    bindings: dict[str, str] = {}
    secrets: dict[str, str] = {}
    authorizations: tuple[AuthorizationReview, ...] = ()
    try:
        values, effects = resolve_configuration_values(manifest, checkout)
    except ProjectConfigurationError as exc:
        problems.append(str(exc))
    try:
        bindings = resolve_configuration_bindings(lock, checkout)
    except ProjectConfigurationError as exc:
        problems.append(str(exc))
    try:
        secrets = resolve_secret_bindings(lock, checkout)
    except ProjectConfigurationError as exc:
        problems.append(str(exc))
    try:
        authorizations = review_authorizations(manifest, lock, checkout)
    except ProjectConfigurationError as exc:
        problems.append(str(exc))
    state = checkout.get("state", {})
    adopted = state.get("adopted", {}) if isinstance(state, dict) else None
    if not isinstance(adopted, dict):
        problems.append("Checkout state.adopted must be a table.")
    else:
        overlap = sorted(set(adopted) & set(bindings))
        if overlap:
            problems.append("State resources cannot be both adopted and configuration-bound: " + ", ".join(overlap) + ".")
    return ConfigurationReview(values, effects, bindings, secrets, authorizations, tuple(problems))
