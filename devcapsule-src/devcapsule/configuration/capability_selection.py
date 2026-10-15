"""Offline generation and tolerant consumption of capability locks.

Shared bytes are never changed by consumption. Two steps are kept apart:
``compose_lock`` builds the persistent selection (shared lock plus personal
pins, or an explicit version set) and ``usable_lock`` projects it for one
execution, checking mandatory providers first and admitting optional provider
closures only as whole units. Only the projection applies omissions, so a
persisted selection never loses what an omission merely hides.
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


def local_pins(checkout: Mapping[str, Any]) -> dict[str, Any]:
    """Return the checkout's personal provider pins as a parsed lock document.

    The pins are the TOML text in ``capabilities.lock``, written by the local
    capability command. A missing field means no pins: an empty dict. Raise
    ProjectConfigurationError for a field that is not a string or not TOML.
    The checkout is unchanged; the result is new.
    """
    encoded = table(checkout, "capabilities").get("lock")
    if encoded is None:
        return {}
    if not isinstance(encoded, str):
        raise ProjectConfigurationError("Local capabilities.lock must contain a TOML lock.")
    try:
        return tomllib.loads(encoded)
    except tomllib.TOMLDecodeError as exc:
        raise ProjectConfigurationError(f"Invalid local capability pins: {exc}") from exc


def compose_lock(manifest: Mapping[str, Any], shared: Mapping[str, Any],
                 checkout: Mapping[str, Any]) -> dict[str, Any]:
    """Return the checkout's persistent software selection, before any filtering.

    An explicit version set is that selection and is returned as a copy.
    Otherwise the result is ``shared`` with the checkout's personal pins laid
    over it: exactly the providers of each locally selected capability, and
    the IDE selector with its materialization when a selected capability
    supplies the IDE. A selected IDE that differs from the shared lock's
    IDE raises ProjectConfigurationError, as do missing or malformed pins and
    an omission of something the project does not list as optional.
    Omissions are not applied here; ``usable_lock`` filters for execution.
    Input documents are unchanged.
    """
    from .file_formats import selected_version_lock
    local = LocalCapabilities.read(checkout)
    local.validate(CapabilityPolicy.read(manifest))
    selected = selected_version_lock(checkout)
    if selected is not None:
        return selected
    lock = deepcopy(dict(shared))
    if not local.selected:
        return lock
    pins = local_pins(checkout)
    if not pins:
        raise ProjectConfigurationError("Local capability pins are missing; run 'project config capabilities --local CAPABILITY ...'.")
    matrix = matrix_for(lock)
    pinned = table(pins, "components")
    overlaid: set[str] = set()
    for capability in local.selected:
        for component in matrix.providers(capability):
            metadata = pinned.get(component)
            if metadata is None:
                raise ProjectConfigurationError(f"Local selection is missing provider {component!r}; select local capabilities again.")
            lock.setdefault("components", {})[component] = deepcopy(metadata)
            overlaid.add(component)
    surface = pinned.get("interactive-surface")
    if surface in overlaid:
        shared_surface = lock["components"].get("interactive-surface")
        if shared_surface and shared_surface != surface:
            # A legacy required surface is still mandatory until explicitly
            # migrated by its project owner.
            raise ProjectConfigurationError("Local IDE conflicts with the project's required IDE; migrate the project declaration first.")
        lock["components"]["interactive-surface"] = surface
        lock["materialization"] = deepcopy(table(pins, "materialization"))
    return lock


def effective_lock(manifest: Mapping[str, Any], composed: Mapping[str, Any],
                   checkout: Mapping[str, Any], *, warn: bool = True) -> dict[str, Any]:
    """Return the execution projection of a composed selection.

    Apply ``usable_lock`` with the manifest's policy and the checkout's local
    choices. ``warn`` prints optional omissions to stderr; False suppresses
    that output, not validation. Inputs are unchanged.
    """
    usable, notices = usable_lock(CapabilityPolicy.read(manifest), composed, LocalCapabilities.read(checkout))
    if warn:
        for notice in notices:
            print(f"Warning: {notice}", file=sys.stderr)
    return usable


def selected_lock(manifest: Mapping[str, Any], shared: Mapping[str, Any],
                  checkout: Mapping[str, Any], *, warn: bool = True) -> dict[str, Any]:
    """Return the checkout's effective lock without changing input documents.

    This is ``effective_lock`` of ``compose_lock``: the persistent selection
    (explicit version set, or ``shared`` plus personal pins) filtered by the
    policy and local omissions. Errors and ``warn`` behave as in those two.
    """
    return effective_lock(manifest, compose_lock(manifest, shared, checkout), checkout, warn=warn)


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

    for role, capabilities in (("Required", policy.required), ("Selected", local.selected)):
        for capability in capabilities:
            try:
                keep.update(supply(capability))
            except ProjectConfigurationError as exc:
                raise ProjectConfigurationError(f"{role} capability {capability!r} is unavailable: {exc}. Upgrade the launcher or select compatible components.") from exc
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
