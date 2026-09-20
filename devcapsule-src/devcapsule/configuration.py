"""Configuration admission and resolution as values, independent of CLI effects.

The representation boundary accepts decoded documents and exports a resolution
for persistence. Between those boundaries, callers inspect, resolve and admit
configuration values. Inputs and exported documents are owned copies: observing
or resolving a configuration cannot edit its inputs or another configuration.

Host-directory existence checks remain part of assessment. Docker/image identity
verification, persistence and launch belong to the operation adapters.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import tomllib
from typing import Any, Mapping

from devcapsule.components.catalog import INTERACTIVE_SURFACES
from devcapsule.configuration_documents import Artifact, admit_document, table
from devcapsule.configuration_resolution import render_resolution
from devcapsule.configuration_review import ConfigurationReview, HostAccess, review_configuration
from devcapsule.project import ProjectMountError, normalize_project_mount
from devcapsule.project_configuration import (
    ProjectConfigurationError, canonical_digest, locked_base_reference,
    stale_resolution_inputs, validate_manifest,
)


class Resolution:
    """A well-formed runtime plan with separate meaning and freshness.

    Decoding establishes a supported plan shape, not execution permission.
    Only Configuration.accept establishes that this plan belongs to its inputs.
    """

    def __init__(self, document: Mapping[str, Any]) -> None:
        admit_document(document, Artifact.resolution, "resolution")
        self._document = deepcopy(dict(document))
        runtime = table(self._document, "runtime")
        component = runtime.get("component")
        mount = runtime.get("project-mount")
        memory = runtime.get("memory-limit-bytes")
        image = runtime.get("image")
        if (not isinstance(component, str) or component not in INTERACTIVE_SURFACES
                or not isinstance(mount, str) or not mount.startswith("/") or "\x00" in mount):
            raise ProjectConfigurationError("Run requires a valid resolved runtime; run 'devcapsule project config resolve'.")
        try:
            normalize_project_mount(mount, "resolved-project")
        except ProjectMountError as exc:
            raise ProjectConfigurationError(str(exc)) from exc
        if memory is not None and (type(memory) is not int or memory <= 0):
            raise ProjectConfigurationError("Resolved runtime.memory-limit-bytes must be a positive integer.")
        if image is not None and (not isinstance(image, str) or not image):
            raise ProjectConfigurationError("Resolved runtime.image must be a non-empty string.")

    def document(self) -> dict[str, Any]:
        """Export an owned document for the persistence/launch adapter."""
        return deepcopy(self._document)

    def same_meaning_as(self, other: Resolution) -> bool:
        """Compare derived plans, deliberately excluding source fingerprints.

        This is not equality of resolutions: equivalent plans may differ in
        freshness, which is a separate observation made by Configuration.
        """
        return self._meaning() == other._meaning()

    def _meaning(self) -> str:
        return canonical_digest({k: v for k, v in self._document.items() if k != "sources"})

    @property
    def component(self) -> str:
        return self._document["runtime"]["component"]

    @property
    def project_mount(self) -> str:
        return self._document["runtime"]["project-mount"]

    @property
    def base_reference(self) -> str | None:
        base = table(self._document, "authorization", "base-image")
        reference = base.get("reference")
        if reference is not None and (not isinstance(reference, str) or not reference):
            raise ProjectConfigurationError("Resolved base reference must be a non-empty string.")
        return reference

    @property
    def host_access(self) -> HostAccess:
        authorizations = self._document.get("authorization", {})
        host_names = {"docker-daemon", "network", "development-sudo", "host-browser", "host-x11"}
        return HostAccess().overlay(self._document.get("host", {})).overlay({
            name: value for name, value in authorizations.items() if name in host_names
        })


class Configuration:
    """An owned snapshot of project policy, platform selection and local decisions.

    Operations are observers: resolve returns a new plan, accept returns its
    stale-input set or refuses, and review returns an independently owned view.
    Editing and file identity/path selection remain separate adapter contracts.
    """

    def __init__(self, manifest: Mapping[str, Any], lock: Mapping[str, Any],
                 checkout: Mapping[str, Any]) -> None:
        self._manifest = deepcopy(dict(manifest))
        self._lock = deepcopy(dict(lock))
        self._checkout = deepcopy(dict(checkout))
        validate_manifest(self._manifest, Path("manifest"))
        admit_document(self._lock, Artifact.lock, "platform lock")
        admit_document(self._checkout, Artifact.checkout, "checkout")
        if "base" in self._lock:
            locked_base_reference(self._lock)
        identity = table(self._checkout, "project")
        if any(identity.get(key) != self._manifest["project"][key] for key in ("creator", "slug")):
            raise ProjectConfigurationError("Checkout does not match the project's creator and slug.")
        self._review = review_configuration(self._manifest, self._lock, self._checkout)

    def review(self) -> ConfigurationReview:
        return deepcopy(self._review)

    def resolve(self) -> Resolution:
        """Derive one complete plan, or refuse without changing the snapshot."""
        component = self._lock.get("components", {}).get("interactive-surface")
        image = self._lock.get("image", {}).get("reference")
        has_formation = "base" in self._lock and "materialization" in self._lock
        if component not in INTERACTIVE_SURFACES or (not image and not has_formation):
            raise ProjectConfigurationError(
                "The V1 slice requires a lock selecting a known interactive surface "
                "with either a completed image or formation inputs."
            )
        # require_ready is rendered by the file/CLI adapter with its actual path.
        return Resolution(tomllib.loads(render_resolution(
            self._manifest, self._lock, self._checkout, self._review,
        )))

    def stale_inputs(self, resolution: Resolution) -> tuple[str, ...]:
        return stale_resolution_inputs(self._manifest, self._lock, self._checkout, resolution.document())

    def accept(self, resolution: Resolution, *, force: bool = False) -> tuple[str, ...]:
        """Admit a saved plan. Force waives freshness only, never validity.

        The result names waived inputs; an empty tuple means ordinary admission.
        A caller must use review().effective_host() for current permissions even
        when explicitly admitting an old plan with force.
        """
        stale = self.stale_inputs(resolution)
        if stale and not force:
            raise ProjectConfigurationError(
                f"Local resolution is stale ({', '.join(stale)}); run 'devcapsule project config resolve'."
            )
        if not self._review.ready:
            raise ProjectConfigurationError("Cannot consume an incomplete configuration review.")
        if resolution.component != self._lock["components"]["interactive-surface"]:
            raise ProjectConfigurationError("Resolved surface differs from the lock; run 'devcapsule project config resolve'.")
        if not stale and not resolution.same_meaning_as(self.resolve()):
            raise ProjectConfigurationError(
                "Generated resolution does not match its inputs; run 'devcapsule project config resolve'."
            )
        return stale
