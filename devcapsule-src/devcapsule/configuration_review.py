"""Read-only assessment of the decisions needed to resolve a checkout.

Inspection and resolution consume the same assessment. Validators own their
contracts; this module composes their results without publishing a partial
resolution or stopping at the first independent decision.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path
import shlex
from typing import Any, Mapping

from devcapsule.configuration_nodes import build_node_registry
from devcapsule.configuration_documents import table

from devcapsule.project_configuration import (
    AuthorizationChoice,
    AuthorizationReview,
    AuthorizationScalar,
    ConfigurationScalar,
    ProjectConfigurationError,
    ResolvedProject,
    manifest_for,
    lock_for,
    checkout_record_paths,
    load_checkout,
    load_resolution,
    resolve_configuration_bindings,
    resolve_configuration_values,
    resolve_secret_bindings,
    review_authorizations,
)


@dataclass(frozen=True)
class HostAccess:
    """Effective host decisions; absence has a safe, explicit interpretation."""
    docker_daemon: str = "none"
    network: str = "bridge"
    development_sudo: bool = False
    host_browser: bool = False
    host_x11: bool | None = None

    def overlay(self, answers: Mapping[str, Any]) -> HostAccess:
        fields = {
            "docker-daemon": ("docker_daemon", ("none", "host-socket")),
            "network": ("network", ("bridge", "host")),
            "development-sudo": ("development_sudo", (False, True)),
            "host-browser": ("host_browser", (False, True)),
            "host-x11": ("host_x11", (False, True)),
        }
        changes: dict[str, Any] = {}
        problems: list[str] = []
        for name, value in answers.items():
            if name not in fields:
                problems.append(f"Unknown legacy host decision {name!r}.")
                continue
            attribute, domain = fields[name]
            if not any(type(value) is type(item) and value == item for item in domain):
                problems.append(f"Host decision {name!r} must be one of {domain!r}; found {value!r}.")
            else:
                changes[attribute] = value
        if problems:
            raise ProjectConfigurationError("\n".join(problems))
        return replace(self, **changes)


@dataclass(frozen=True)
class ConfigurationReview:
    values: dict[str, ConfigurationScalar]
    runtime_effects: dict[str, int]
    bindings: dict[str, str]
    secret_bindings: dict[str, str]
    authorizations: tuple[AuthorizationReview, ...]
    problems: tuple[str, ...]
    legacy_host: HostAccess = field(default_factory=HostAccess)

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

    def effective_host(self, overrides: Mapping[str, Any] | None = None) -> HostAccess:
        answers = {
            name: value for name, value in self.resolved_authorizations().items()
            if name in {"docker-daemon", "network", "development-sudo", "host-browser", "host-x11"}
        }
        return self.legacy_host.overlay(answers).overlay(overrides or {})


def review_configuration(
    manifest: Mapping[str, Any], lock: Mapping[str, Any], checkout: Mapping[str, Any]
) -> ConfigurationReview:
    # No consumer can assess a tree with ambiguous names or runtime effects.
    build_node_registry(manifest, lock)
    problems: list[str] = []
    values: dict[str, ConfigurationScalar] = {}
    effects: dict[str, int] = {}
    bindings: dict[str, str] = {}
    secrets: dict[str, str] = {}
    authorizations: tuple[AuthorizationReview, ...] = ()
    host = HostAccess()
    try:
        host = host.overlay(table(checkout, "host"))
    except ProjectConfigurationError as exc:
        problems.append(str(exc))
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
        try:
            resolve_configuration_bindings(lock, {"configuration": {"bindings": {"host-directory": adopted}}})
        except ProjectConfigurationError as exc:
            problems.append("Adopted state: " + str(exc))
        overlap = sorted(set(adopted) & set(bindings))
        if overlap:
            problems.append("State resources cannot be both adopted and configuration-bound: " + ", ".join(overlap) + ".")
    return ConfigurationReview(values, effects, bindings, secrets, authorizations, tuple(problems), host)


@dataclass(frozen=True)
class ExecutionConfiguration:
    """The single admission boundary before any project execution effects."""
    project: ResolvedProject
    review: ConfigurationReview
    stale_inputs: tuple[str, ...]

    @classmethod
    def load(cls, start: Path, *, force: bool = False) -> ExecutionConfiguration:
        root, manifest = manifest_for(start)
        lock_path, lock = lock_for(root, manifest)
        input_path, output_path = checkout_record_paths(manifest, root)
        if not input_path.is_file() or not output_path.is_file():
            raise ProjectConfigurationError("Local resolution is missing; run 'devcapsule project config resolve'.")
        checkout = load_checkout(input_path, manifest, root)
        resolution = load_resolution(output_path)
        from devcapsule.configuration import Configuration, Resolution
        configuration = Configuration(manifest, lock, checkout)
        plan = Resolution(resolution)
        review = configuration.review()
        # Keep the complete, path-qualified recovery advice at the CLI boundary.
        if force or not configuration.stale_inputs(plan):
            review.require_ready(root)
        stale = configuration.accept(plan, force=force)
        selected = ResolvedProject(root, manifest, lock_path, lock, input_path, checkout, output_path, resolution)
        return cls(selected, review, stale)
