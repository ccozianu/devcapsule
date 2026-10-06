"""Source fingerprints for a generated configuration checkpoint."""

from __future__ import annotations
from typing import Any, Mapping

from .file_formats import canonical_digest, table, ProjectConfigurationError
from .manifest import configuration_manifest


def resolution_source_digests(
    manifest: Mapping[str, Any], lock: Mapping[str, Any], checkout: Mapping[str, Any]
) -> dict[str, str]:
    """The exact source digests a fresh generated resolution must record."""

    result = {
        "manifest": canonical_digest(configuration_manifest(manifest)),
        "platform-lock": canonical_digest(lock),
        "checkout-input": canonical_digest(checkout),
    }

    from .capabilities import CapabilityPolicy, LocalCapabilities
    policy = CapabilityPolicy.read(manifest)
    if policy.layered:
        baseline_policy = CapabilityPolicy(policy.required, (), policy.sdk_major, True)
        local = LocalCapabilities.read(checkout)
        providers = table(lock, "capability-providers")
        required = (*policy.required, *local.selected)
        if any(capability not in providers for capability in required):
            raise ProjectConfigurationError("Capability provider evidence is incomplete; resolve the selection again.")
        keep = {component for capability in required for component in providers[capability]}
        baseline = dict(lock)
        components = table(lock, "components")
        baseline["components"] = {key: value for key, value in components.items()
                                  if key in keep or key == "interactive-surface" and value in keep}
        declaration = configuration_manifest(manifest)
        declaration["capabilities"] = baseline_policy.document()
        result["capability-baseline"] = canonical_digest({
            "manifest": declaration,
            "lock": {key: baseline[key] for key in ("platform", "base", "image", "components", "materialization") if key in baseline},
        })
    return result
