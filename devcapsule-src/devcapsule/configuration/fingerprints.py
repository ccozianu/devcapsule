"""Source fingerprints for a generated configuration checkpoint."""

from __future__ import annotations
from typing import Any, Mapping

from .documents import canonical_digest
from .manifest import configuration_manifest


def resolution_source_digests(
    manifest: Mapping[str, Any], lock: Mapping[str, Any], checkout: Mapping[str, Any]
) -> dict[str, str]:
    """The exact source digests a fresh generated resolution must record."""

    return {
        "manifest": canonical_digest(configuration_manifest(manifest)),
        "platform-lock": canonical_digest(lock),
        "checkout-input": canonical_digest(checkout),
    }
