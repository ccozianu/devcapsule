"""The project owner's commands: what the project requires, offers and recommends.

Each operation edits the shared manifest through one writer
(:func:`manifest_document.render_manifest`) and, when the tools change,
regenerates the platform lock, validating the candidate pair before anything
is written and promoting both files under the capability transaction journal
of :mod:`capability_commands`. The rc4 IDE recommendation command stays; agents are ordinary shared
capabilities. Component acquisition still requires the developer's consent.

The verbs are the ones the CLI UX redesign work order of 2026-10-24 settled:
``require``, ``offer`` and ``drop`` for tools and environment variables,
``recommend`` for the IDE, the memory limit, the CPU count and the curated host
accesses, each with the owner's reason (``--because``).
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping, Sequence

from devcapsule.platforms import Platform
from devcapsule.resolution_matrix import MATRICES, ResolutionMatrix

from .authorization import CURATED_HOST_RECOMMENDATIONS, render_authorization_value
from .capabilities import CapabilityPolicy
from .capability_commands import canonical_tool_name, check_documents, parse_tool_names, paths, promote
from .capability_selection import generate_lock
from .file_formats import ProjectConfigurationError
from .manifest_document import (
    CURRENT_MANIFEST_SCHEMA_VERSION,
    RECOMMENDATION_NAMES,
    EnvironmentPolicy,
    Recommendations,
    capability_reasons,
    capability_table,
    environment_name,
)
from .storage import discover_project, load_toml, require_settled
from .values import normalize_memory_size

__all__ = [
    "drop_environment",
    "drop_tools",
    "offer_environment",
    "offer_tools",
    "recommend",
    "require_environment",
    "require_tools",
]


def _project(start: Path) -> tuple[Path, dict[str, Any], dict[str, Any], ResolutionMatrix]:
    root = discover_project(start)
    require_settled(root)
    manifest_path, lock_path, _ = paths(root)
    manifest, lock = load_toml(manifest_path), load_toml(lock_path)
    check_documents(manifest, lock)
    return root, manifest, lock, MATRICES[Platform.current()]


def _policy_edit(
    start: Path, *, change: str, names: Sequence[str], because: str | None,
    preview: bool, allow_unverified: bool,
) -> str:
    root, manifest, lock, matrix = _project(start)
    policy = CapabilityPolicy.read(manifest)
    reasons = capability_reasons(manifest)
    required, optional = set(policy.required), set(policy.optional)
    minimums = dict(policy.minimums)
    # Preserve a hand-written component alias while editing its declaration.
    declared: dict[str, str] = {}
    for name in (*policy.required, *policy.optional):
        try:
            declared[matrix.canonical_name(name)] = name
        except ProjectConfigurationError:
            continue  # Unknown optional declarations remain opaque.
    def declared_name(name: str) -> str:
        canonical = canonical_tool_name(matrix, name)
        return declared.get(canonical, canonical)
    if change == "drop":
        canonical = tuple(declared_name(name) for name in names)
        unknown = sorted(set(canonical) - required - optional)
        if unknown:
            raise ProjectConfigurationError(
                "Not declared by this project: " + ", ".join(unknown) + "; nothing changed."
            )
        for name in canonical:
            required.discard(name)
            optional.discard(name)
            minimums.pop(name, None)
            reasons.pop(name, None)
    else:
        canonical = tuple(declared_name(name) for name in parse_tool_names(matrix, names))
        if any(matrix.is_ide(name) for name in canonical):
            raise ProjectConfigurationError(
                "IDE choices are each developer's; recommend one with 'config recommend ide NAME'."
            )
        target, other = (required, optional) if change == "require" else (optional, required)
        for name in canonical:
            target.add(name)
            other.discard(name)
            if because is not None:
                reasons[name] = because
        if change == "offer":
            for name in canonical:
                minimums.pop(name, None)
    candidate = CapabilityPolicy(tuple(sorted(required)), tuple(sorted(optional)), tuple(sorted(minimums.items())), layered=True)
    candidate_manifest = deepcopy(manifest)
    candidate_manifest["devcapsule-schema-version"] = CURRENT_MANIFEST_SCHEMA_VERSION
    candidate_manifest["capabilities"] = capability_table(candidate, reasons, previous=manifest["capabilities"])
    generated = generate_lock(candidate, matrix, previous=lock, allow_unverified=allow_unverified)
    check_documents(candidate_manifest, generated)
    if not preview:
        promote(root, candidate_manifest, generated)
    verb = {"require": "Required", "offer": "Offered", "drop": "Dropped"}[change]
    lines = [
        ("Preview; nothing written." if preview else f"{verb} {', '.join(canonical)}; the manifest and the lock are updated."),
        f"Required: {' '.join(candidate.requirements()) or 'none'}",
        f"Offered: {' '.join(candidate.optional) or 'none'}",
    ]
    if not preview:
        lines.extend(_refresh_own_checkout(root, candidate_manifest))
    return "\n".join(lines)


def _refresh_own_checkout(root: Path, manifest: Mapping[str, Any]) -> list[str]:
    """Re-derive the owner's own resolution after a lock change, so ``run`` works at once.

    Only a registered checkout is touched, and only when nothing is pending;
    otherwise the pending decisions are named, as ``config show`` names them.
    """
    from .storage import find_checkout_record
    from .operations import resolve_checkout
    if find_checkout_record(manifest, root) is None:
        return []
    try:
        report = resolve_checkout(root)
    except ProjectConfigurationError as exc:
        first = str(exc).splitlines()[0]
        return [f"Your checkout is not ready to run yet: {first}", "Review with 'devcapsule project config show'."]
    return [report.render()]


def require_tools(start: Path, names: Sequence[str], *, because: str | None = None,
                  preview: bool = False, allow_unverified: bool = False) -> str:
    """Make ``names`` required tools of the project, with an optional reason; regenerate the lock."""
    return _policy_edit(start, change="require", names=names, because=because, preview=preview, allow_unverified=allow_unverified)


def offer_tools(start: Path, names: Sequence[str], *, because: str | None = None,
                preview: bool = False, allow_unverified: bool = False) -> str:
    """Make ``names`` offered (optional) tools of the project; a developer may omit them."""
    return _policy_edit(start, change="offer", names=names, because=because, preview=preview, allow_unverified=allow_unverified)


def drop_tools(start: Path, names: Sequence[str], *, preview: bool = False, allow_unverified: bool = False) -> str:
    """Remove ``names`` from the project's required and offered tools, with their minimum versions."""
    return _policy_edit(start, change="drop", names=names, because=None, preview=preview, allow_unverified=allow_unverified)


def _environment_edit(start: Path, *, change: str, names: Sequence[str], because: str | None, preview: bool) -> str:
    root, manifest, _lock, _matrix = _project(start)
    environment = deepcopy(manifest.get("environment", {}))
    required, optional = environment.get("required", {}), environment.get("optional", {})
    canonical = tuple(environment_name(name, field_name="environment variable") for name in names)
    if change == "drop":
        unknown = sorted(set(canonical) - set(required) - set(optional))
        if unknown:
            raise ProjectConfigurationError("Not declared by this project: " + ", ".join(unknown) + "; nothing changed.")
        for name in canonical:
            required.pop(name, None)
            optional.pop(name, None)
    else:
        target, other = (required, optional) if change == "require" else (optional, required)
        for name in canonical:
            entry = other.pop(name, target.get(name, {}))
            if because is not None:
                entry["reason"] = because
            target[name] = entry
    candidate_manifest = deepcopy(manifest)
    candidate_manifest["devcapsule-schema-version"] = CURRENT_MANIFEST_SCHEMA_VERSION
    candidate_manifest.pop("environment", None)
    document = {scope: dict(sorted(entries.items())) for scope, entries in
                (("required", required), ("optional", optional)) if entries}
    if document:
        candidate_manifest["environment"] = document
    candidate = EnvironmentPolicy.read(candidate_manifest)
    if not preview:
        promote(root, candidate_manifest)
    verb = {"require": "Required", "offer": "Offered", "drop": "Dropped"}[change]
    lines = [("Preview; nothing written." if preview else f"{verb} environment {', '.join(canonical)}; the manifest is updated.")]
    for scope, entries in (("Required environment", candidate.required), ("Offered environment", candidate.optional)):
        rendered = ", ".join(f"{name} ({reason})" if reason else name for name, reason in entries.items()) or "none"
        lines.append(f"{scope}: {rendered}")
    lines.append("Values belong to each developer; this command stores declarations only.")
    return "\n".join(lines)


def require_environment(start: Path, names: Sequence[str], *, because: str | None = None, preview: bool = False) -> str:
    """Declare environment variables every developer must supply, with the owner's reason."""
    return _environment_edit(start, change="require", names=names, because=because, preview=preview)


def offer_environment(start: Path, names: Sequence[str], *, because: str | None = None, preview: bool = False) -> str:
    """Declare environment variables a developer may supply, with the owner's reason."""
    return _environment_edit(start, change="offer", names=names, because=because, preview=preview)


def drop_environment(start: Path, names: Sequence[str], *, preview: bool = False) -> str:
    """Remove environment declarations from the project."""
    return _environment_edit(start, change="drop", names=names, because=None, preview=preview)


HOST_RECOMMENDATION_NODES = tuple(CURATED_HOST_RECOMMENDATIONS)


def recommend(start: Path, name: str, value: str, *, because: str | None = None, preview: bool = False) -> str:
    """Record, change or remove one project recommendation.

    ``name`` is ``ide``, ``memory`` or ``cpus`` (an ordinary recommendation,
    applied by the launcher as the default and disclosed) or a curated host
    access (``network``, ``docker-daemon``, ``development-sudo``,
    ``host-browser``), which the developer is asked about with the reason.
    ``value`` is the recommended value, or ``none`` to remove the
    recommendation. A host recommendation requires ``because``: the reason is
    what the developer reads when asked.
    """
    root, manifest, _lock, matrix = _project(start)
    candidate_manifest = deepcopy(manifest)
    candidate_manifest["devcapsule-schema-version"] = CURRENT_MANIFEST_SCHEMA_VERSION
    removing = value.strip().lower() == "none"
    if name in RECOMMENDATION_NAMES:
        current = Recommendations.read(manifest)
        reasons = dict(current.reasons)
        fields: dict[str, Any] = {"ide": current.ide, "memory": current.memory, "cpus": current.cpus}
        if removing:
            if fields[name] is None:
                raise ProjectConfigurationError(f"The project recommends no {name}; nothing changed.")
            fields[name] = None
            reasons.pop(name, None)
            rendered = "none"
        else:
            fields[name] = _ordinary_recommendation_value(matrix, name, value)
            if because is not None:
                reasons[name] = because
            rendered = str(fields[name])
        candidate = Recommendations(fields["ide"], fields["memory"], fields["cpus"], reasons)
        candidate_manifest.pop("recommendations", None)
        document = candidate.document()
        if document:
            candidate_manifest["recommendations"] = document
        effect = {
            "ide": "a developer who has not chosen an IDE gets this one, and may choose another",
            "memory": "the capsule's memory limit unless the developer sets another",
            "cpus": "the capsule's CPU count unless the developer sets another",
        }[name]
    elif name in HOST_RECOMMENDATION_NODES:
        path, supported = CURATED_HOST_RECOMMENDATIONS[name]
        host = candidate_manifest.setdefault("host", {})
        if removing:
            if _host_recommendation(host, path) is None:
                raise ProjectConfigurationError(f"The project recommends no {name}; nothing changed.")
            _remove_host_recommendation(host, path)
            rendered = "none"
        else:
            accepted = render_authorization_value(supported)
            if value.strip().lower() not in {accepted, "default"}:
                raise ProjectConfigurationError(
                    f"Recommendation {name!r} accepts exactly {accepted!r} (or 'none' to remove it); got {value!r}."
                )
            if not because:
                raise ProjectConfigurationError(
                    f"A host access recommendation needs the reason the developer will read: "
                    f"--because \"...\" with 'recommend {name} {accepted}'."
                )
            node = host
            for key in path:
                node = node.setdefault(key, {})
            node["value"] = supported
            node["justification"] = because
            rendered = accepted
        if not candidate_manifest["host"]:
            del candidate_manifest["host"]
        effect = "every developer is asked, with your reason; a recommendation grants nothing"
    else:
        raise ProjectConfigurationError(
            f"Unknown recommendation {name!r}; the project may recommend "
            + ", ".join((*RECOMMENDATION_NAMES, *HOST_RECOMMENDATION_NODES)) + "."
        )
    _validate(candidate_manifest)
    if not preview:
        promote(root, candidate_manifest)
    head = "Preview; nothing written." if preview else (
        f"Recommendation removed: {name}." if removing else f"Recommended {name} = {rendered}: {effect}."
    )
    return head


def _ordinary_recommendation_value(matrix: ResolutionMatrix, name: str, value: str) -> str | int:
    if name == "ide":
        candidate = value.strip()
        surfaces = list(matrix.ide_capabilities())
        by_component = {matrix.resolve_provider(capability): capability for capability in surfaces}
        if candidate in by_component:
            candidate = by_component[candidate]
        if candidate not in surfaces:
            raise ProjectConfigurationError(
                f"Unknown IDE {value!r}; this launcher knows: " + ", ".join(surfaces) + "."
            )
        return candidate
    if name == "memory":
        return normalize_memory_size(value, field_name="recommendation memory")
    if not value.strip().isdecimal() or int(value) < 1:
        raise ProjectConfigurationError(f"Recommendation cpus takes a positive integer; got {value!r}.")
    return int(value)


def _host_recommendation(host: Mapping[str, Any], path: tuple[str, ...]) -> Mapping[str, Any] | None:
    node: Any = host
    for key in path:
        if not isinstance(node, Mapping) or key not in node:
            return None
        node = node[key]
    return node if isinstance(node, Mapping) else None


def _remove_host_recommendation(host: dict[str, Any], path: tuple[str, ...]) -> None:
    parents: list[dict[str, Any]] = [host]
    node: dict[str, Any] = host
    for key in path:
        node = node[key]
        parents.append(node)
    for index in range(len(path) - 1, -1, -1):
        parent = parents[index]
        child = parent[path[index]]
        if index == len(path) - 1 or not child:
            del parent[path[index]]
        else:
            break


def _validate(manifest: dict[str, Any]) -> None:
    from .manifest import validate_manifest
    validate_manifest(manifest, Path("manifest"))
    from .authorization import authorization_declarations
    authorization_declarations(manifest, {})
