"""Project declaration admission at the file boundary, and its configuration-relevant projection.

The schemas themselves, and the migration between them, are
:mod:`manifest_schemas`.  This module adds the one thing that module cannot
know, the component catalog's answer to which names are IDE capabilities,
and gives every consumer the manifest in schema 2.
"""

from __future__ import annotations
from typing import Any, Mapping

from .file_formats import ProjectConfigurationError
from .manifest_schemas import ManifestV1, ManifestV2, read_manifest, upgrade


def ide_capability(name: str) -> str | None:
    """The IDE capability ``name`` stands for, by the component catalog, or None.

    A name is an IDE capability when an interactive surface provides it
    (``python-ide``, provided by PyCharm) or when it is such a surface's own
    id, the alias a schema-1 ``need`` list may have used (``pycharm``).
    """
    from devcapsule.components.catalog import INTERACTIVE_SURFACES
    for component_id, definition in INTERACTIVE_SURFACES.items():
        if name in (component_id, definition.capability):
            return definition.capability
    return None


def current(manifest: ManifestV1 | ManifestV2, source: object) -> ManifestV2:
    """``manifest`` as schema 2: itself, or a schema-1 value upgraded in memory.

    Nothing is written here.  An owner's edit or ``project init --regenerate``
    writes the upgraded form; no other command rewrites a schema-1 file.
    """
    if isinstance(manifest, ManifestV2):
        return manifest
    try:
        return upgrade(manifest, ide=ide_capability)
    except ProjectConfigurationError as exc:
        raise ProjectConfigurationError(f"{source}: {exc}") from exc


def current_manifest(document: Mapping[str, Any], source: object) -> ManifestV2:
    """A decoded manifest file as this launcher reads it: admitted by its schema, then schema 2."""
    return current(read_manifest(document, source), source)


def configuration_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """The manifest projection consumed by environment resolution.

    Workflow and descriptive project metadata cannot change a derived runtime.
    Authorization fingerprints are independently scoped to their questions.
    The environment the project asks for and its ordinary recommendations are
    inputs of the derived plan, so they are part of the projection.
    """
    return {
        "devcapsule-schema-version": manifest.get("devcapsule-schema-version"),
        "project": {key: manifest.get("project", {}).get(key) for key in ("creator", "slug", "mount")},
        **{key: manifest.get(key, {}) for key in ("capabilities", "configuration", "host", "environment", "recommendations")},
    }
