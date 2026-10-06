"""Offline generation and tolerant consumption of capability locks.

Shared bytes are never changed by consumption. Mandatory providers are checked
first; optional provider closures are admitted only as whole units. Local
component pins are overlaid on the shared base, then the same policy is checked.
"""
from __future__ import annotations

from copy import deepcopy
import sys
import tomllib
from typing import Any, Mapping

from devcapsule.components.catalog import COMPONENTS
from devcapsule.platforms import Platform
from devcapsule.resolution_matrix import MATRICES, ResolutionMatrix
from .capabilities import CapabilityPolicy, LocalCapabilities, names
from .file_formats import ProjectConfigurationError, table


def matrix_for(lock: Mapping[str, Any]) -> ResolutionMatrix:
    """Return this launcher's catalog for the lock's declared platform.

    Raise ProjectConfigurationError if that platform is absent or unsupported.
    """
    try:
        return MATRICES[Platform(str(lock.get("platform")))]
    except (ValueError, KeyError):
        raise ProjectConfigurationError(f"Unsupported lock platform {lock.get('platform')!r}.") from None


def generate_lock(policy: CapabilityPolicy, matrix: ResolutionMatrix, *,
                  previous: Mapping[str, Any] | None = None,
                  allow_unverified: bool = False) -> dict[str, Any]:
    """Build a shared lock for a validated policy, without writing files.

    Resolve known capabilities using ``matrix``; a project need not choose an
    IDE. Unknown optional names can survive only when ``previous`` supplies
    their provider lists and nonconflicting metadata. Otherwise raise
    ProjectConfigurationError, as for unsupported requirements or SDK majors.
    ``allow_unverified`` permits catalog combinations without recorded
    compatibility evidence. Inputs are unchanged; the returned lock is new.
    """
    matrix.normalize(list(policy.required))
    accepted = list(policy.required)
    for capability in policy.optional:
        if capability in matrix.capabilities():
            # Authored known optional capabilities must be resolvable. A writer
            # does not commit a typo or silently write a reduced recommendation.
            accepted.append(capability)
    lock = tomllib.loads(matrix.resolve(accepted, project_only=True,
                                      allow_unverified=allow_unverified).render_lock())
    providers = {name: list(matrix.providers(name)) for name in accepted}
    for capability in set(policy.optional) - set(accepted):
        old_providers = table(previous or {}, "capability-providers")
        if capability not in old_providers:
            raise ProjectConfigurationError(f"Cannot author unknown capability {capability!r}; use a launcher that supports it.")
        opaque = names(old_providers[capability], f"providers for {capability}")
        for component in opaque:
            metadata = table(previous or {}, "components").get(component)
            if metadata is None or component in lock["components"] and lock["components"][component] != metadata:
                raise ProjectConfigurationError(f"Cannot preserve optional {capability!r} safely; its provider {component!r} conflicts or is missing.")
            lock["components"][component] = deepcopy(metadata)
        providers[capability] = list(opaque)
    lock["capability-providers"] = providers
    check_majors(policy, lock, matrix)
    return lock


def check_majors(policy: CapabilityPolicy, lock: Mapping[str, Any], matrix: ResolutionMatrix) -> None:
    """Require the lock to establish every SDK major requested by the policy.

    Raise ProjectConfigurationError for a mismatch or unknown major. Evidence
    comes from ``matrix.sdk_major``; this does not execute an installed SDK.
    """
    for capability, expected in policy.sdk_major:
        actual = matrix.sdk_major(capability, lock)
        if actual != expected:
            raise ProjectConfigurationError(
                f"Required {capability} SDK major {expected}; selected lock provides {actual if actual is not None else 'an unknown major'}. "
                "Choose a compatible base/SDK with 'project config capabilities'; the project constraint cannot be overridden locally."
            )


def selected_lock(manifest: Mapping[str, Any], shared: Mapping[str, Any],
                  checkout: Mapping[str, Any], *, warn: bool = True) -> dict[str, Any]:
    """Return the checkout's effective lock without changing input documents.

    Use its explicit version set when present; otherwise overlay its personal
    component pins on ``shared``. Apply ``usable_lock`` to enforce required
    capabilities and local choices. Missing local pins or a conflicting shared
    IDE raise ProjectConfigurationError. ``warn`` prints optional omissions
    to stderr; False suppresses that output, not validation.
    """
    from .file_formats import selected_version_lock
    local = LocalCapabilities.read(checkout)
    policy = CapabilityPolicy.read(manifest)
    local.validate(policy)
    selected = selected_version_lock(checkout)
    lock = deepcopy(dict(selected if selected is not None else shared))
    if selected is None and local.selected:
        encoded = table(checkout, "capabilities").get("lock")
        if not isinstance(encoded, str):
            raise ProjectConfigurationError("Local capability pins are missing; run 'project config capabilities --local CAPABILITY ...'.")
        try:
            pins = tomllib.loads(encoded)
        except tomllib.TOMLDecodeError as exc:
            raise ProjectConfigurationError(f"Invalid local capability pins: {exc}") from exc
        matrix = matrix_for(lock)
        for capability in local.selected:
            for component in matrix.providers(capability):
                metadata = table(pins, "components").get(component)
                if metadata is None:
                    raise ProjectConfigurationError(f"Local selection is missing provider {component!r}; select local capabilities again.")
                lock.setdefault("components", {})[component] = deepcopy(metadata)
        surface = table(pins, "components").get("interactive-surface")
        if surface:
            previous_surface = lock["components"].get("interactive-surface")
            if previous_surface and previous_surface != surface:
                # A legacy required surface is still mandatory until explicitly
                # migrated by its project owner.
                raise ProjectConfigurationError("Local IDE conflicts with the project's required IDE; migrate the project declaration first.")
            lock["components"]["interactive-surface"] = surface
            lock["materialization"] = deepcopy(pins["materialization"])
    usable, notices = usable_lock(policy, lock, local)
    if warn:
        for notice in notices:
            print(f"Warning: {notice}", file=sys.stderr)
    return usable


def usable_lock(policy: CapabilityPolicy, source: Mapping[str, Any],
                local: LocalCapabilities = LocalCapabilities()) -> tuple[dict[str, Any], tuple[str, ...]]:
    """Return an effective lock and warning strings for omitted enhancements.

    ``policy`` and ``local`` must be validated values; ``source`` supplies
    pinned component metadata. Required and locally selected capabilities,
    including their dependencies, must be available or this raises
    ProjectConfigurationError. Optional omissions never remove those providers.
    Unsupported or missing optional providers are skipped with a warning.

    The returned lock is a filtered copy for execution, not a replacement for
    persisted version pins. Inputs remain unchanged. A legacy policy without
    optional, SDK or local choices returns an unfiltered copy for compatibility.
    This checks provider availability; artifact integrity and host permissions
    are checked by later admission stages.
    """
    lock = deepcopy(dict(source))
    if not policy.layered and not policy.optional and not policy.sdk_major and not local.selected and not local.without:
        return lock, ()  # Old locks remain records, not requests to re-resolve.
    local.validate(policy)
    matrix = matrix_for(lock)
    components = table(lock, "components")
    base = matrix.base_image(str(table(lock, "base").get("reference")))
    keep: set[str] = set()
    notices: list[str] = []

    def supply(capability: str) -> tuple[str, ...]:
        if capability not in matrix.capabilities():
            raise ProjectConfigurationError("this launcher does not support it")
        providers = matrix.providers(capability)
        if not providers and (base is None or capability not in base.contract.services):
            raise ProjectConfigurationError("the selected base cannot establish that it supplies this capability")
        missing = [name for name in providers if name not in COMPONENTS or not isinstance(components.get(name), dict)]
        if missing:
            raise ProjectConfigurationError("missing supported providers: " + ", ".join(missing))
        return providers

    for capability in (*policy.required, *local.selected):
        try:
            keep.update(supply(capability))
        except ProjectConfigurationError as exc:
            raise ProjectConfigurationError(f"Required capability {capability!r} is unavailable: {exc}. Upgrade the launcher or select compatible components.") from exc
    check_majors(policy, lock, matrix)
    for capability in policy.optional:
        if capability in local.without:
            notices.append(f"Optional {capability!r} omitted by local choice; that enhancement is unavailable.")
            continue
        try:
            keep.update(supply(capability))
        except ProjectConfigurationError as exc:
            notices.append(f"Optional {capability!r} omitted: {exc}; that enhancement is unavailable.")
    surface = components.get("interactive-surface")
    lock["components"] = {name: deepcopy(value) for name, value in components.items() if name in keep}
    if surface in keep:
        lock["components"]["interactive-surface"] = surface
    else:
        lock["materialization"] = {}
    # Evidence is reconstructed by this reader, never trusted from a newer
    # writer. The pure configuration core uses it for optional-only freshness.
    lock["capability-providers"] = {capability: list(matrix.providers(capability))
                                    for capability in (*policy.required, *local.selected)}
    return lock, tuple(notices)
