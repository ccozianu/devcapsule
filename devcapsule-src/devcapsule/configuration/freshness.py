"""Freshness of scoped and predecessor configuration checkpoints."""

from __future__ import annotations
from typing import Any, Mapping

from .documents import ProjectConfigurationError, canonical_digest
from .fingerprints import resolution_source_digests
from .resolution import same_effective_resolution


def stale_resolution_inputs(
    manifest: Mapping[str, Any],
    lock: Mapping[str, Any],
    checkout: Mapping[str, Any],
    resolution: Mapping[str, Any],
) -> tuple[str, ...]:
    """Name exactly which generated-resolution inputs have drifted.

    This is the single staleness policy for the resolution layer: drift is
    detected here — never by a loader refusing to read an artifact — and the
    remedy is always ``devcapsule project config resolve``.  Every consumer
    (``config list``, ``run``, ``fresh_resolved_project``) asks this one
    function so the policy cannot fork.
    """

    actual = resolution.get("sources", {})
    if not isinstance(actual, dict):
        raise ProjectConfigurationError("Generated resolution sources must be a table.")
    expected = resolution_source_digests(manifest, lock, checkout)
    # Released schema-1 resolutions used a whole-manifest digest. Accept an
    # exact legacy match without rewriting pins or asking the user to resolve.
    accepted_manifest = {expected["manifest"]}
    if actual.get("manifest-scope") is None:
        try:
            accepted_manifest.add(canonical_digest(manifest))
        except ProjectConfigurationError:
            # An unrelated TOML-native metadata value was not supported by
            # the old hash; the pure derived-meaning comparison still applies.
            pass
    if actual.get("manifest-scope") is None and actual.get("manifest") not in accepted_manifest:
        # Old checkpoints did not retain a scoped input snapshot. Their
        # complete derived meaning is the available evidence: compare it with
        # today's pure derivation while retaining the lock/checkout gates.
        legacy_digest = actual.get("manifest")
        if isinstance(legacy_digest, str) and same_effective_resolution(manifest, lock, checkout, resolution):
            accepted_manifest.add(legacy_digest)
    return tuple(
        name for name, digest in expected.items()
        if (actual.get(name) not in accepted_manifest if name == "manifest" else actual.get(name) != digest)
    )
