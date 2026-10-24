"""Derive one checkout's launch plan from its documents: the resolve step, done by ``run``.

Answer 1 of the CLI UX redesign work order of 2026-10-24 and its principle
3: ``project run`` is the first-contact command and the return-to-work
command. It reads the project's manifest and lock, the workstation's
defaults and the checkout's record, derives the plan, asks only what it
cannot derive, and launches. Nothing derived is the user's to refresh:
the generated resolution is written here, every time, as the launch's own
artifact, and ``config resolve`` is gone.

This module is the adapter between the documents on disk and the
in-memory :class:`Configuration`: it registers a checkout that has no record
yet, composes the checkout's selection (with a run-once IDE or agent laid
over it when asked), derives and writes the resolution, and hands the
launch a :class:`ResolvedProject`. Asking the developer is the command's
job; the structured decisions come from the listing.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import tomllib
import shlex
from typing import Any, Mapping

from devcapsule.compat import DecisionPending
from devcapsule.materialization import validate_base_image
from devcapsule.platforms import Platform
from devcapsule.project import sanitize_name
from devcapsule.resolution_matrix import MATRICES, ResolutionMatrix, known_base_image

from .authorization import authorized_base_selection
from .capabilities import CapabilityPolicy, LocalCapabilities
from .capability_commands import pin_selection, release_deselected
from .capability_selection import compose_lock, effective_lock, local_pins
from .file_formats import ProjectConfigurationError, canonical_digest, render_checkout, render_toml
from .listing import Listing, assess_checkout
from .model import Configuration
from .storage import (
    ResolvedProject,
    atomic_write,
    checkout_record_paths,
    find_checkout_record,
    load_checkout,
    load_toml,
    load_workstation,
    named_checkout_record_paths,
    recommendation_lock_for,
    resolved_record_path,
)
from .file_formats import selected_version_lock
from .docker_arguments import arguments_path, read_arguments, read_environment

__all__ = ["CheckoutState", "Selection", "derive_plan", "load_state", "register_checkout", "selection_catalog"]


def selection_catalog(matrix: ResolutionMatrix | None = None) -> tuple[dict[str, str], dict[str, str]]:
    """The IDE and agent capabilities this launcher knows, each with the component it selects."""
    matrix = matrix or MATRICES[Platform.current()]
    personal = matrix.local_capabilities()
    surfaces = {name: matrix.providers(name)[0] for name in personal if not name.endswith("-agent")}
    agents = {name: matrix.providers(name)[0] for name in personal if name.endswith("-agent")}
    return surfaces, agents


class Selection:
    """A checkout's IDE, agents and omissions, as capability names, editable in memory."""

    def __init__(self, local: LocalCapabilities, surfaces: Mapping[str, str], agents: Mapping[str, str]) -> None:
        self.ide = next((name for name in local.selected if name in surfaces), None)
        self.agents = {name for name in local.selected if name in agents}
        self.extra = {name for name in local.selected if name not in surfaces and name not in agents}
        self.without = set(local.without)

    def local(self) -> LocalCapabilities:
        selected = {*self.agents, *self.extra} | ({self.ide} if self.ide else set())
        return LocalCapabilities(tuple(sorted(selected)), tuple(sorted(self.without)))


class CheckoutState:
    """One checkout's documents as loaded for a launch, registered or not, writing nothing on load."""

    def __init__(self, root: Path, manifest: dict[str, Any]) -> None:
        self.root = root
        self.manifest = manifest
        self.matrix = MATRICES[Platform.current()]
        self.surfaces, self.agents = selection_catalog(self.matrix)
        self.lock_path, self.shared_lock = recommendation_lock_for(root, manifest)
        self.workstation = load_workstation()
        record = find_checkout_record(manifest, root)
        self.input_path: Path | None = record
        self.checkout: dict[str, Any] = load_checkout(record, manifest, root) if record is not None else tomllib.loads(
            render_checkout(manifest, root, {}, {})
        )
        if record is None:
            try:
                self.input_path, _ = checkout_record_paths(manifest, root)
            except ProjectConfigurationError:
                self.input_path = None  # the default record belongs to another checkout of this project
        self.saved_environment: dict[str, str | None] = {}
        if record is not None:
            read_arguments(arguments_path(record))  # Malformed storage is a refusal.
            try:
                self.saved_environment = read_environment(arguments_path(record))
            except ProjectConfigurationError:
                # Ambiguous Docker tokens remain literal passthrough. They
                # cannot establish answers to declared environment inputs.
                self.saved_environment = {}

    @property
    def registered(self) -> bool:
        return self.input_path is not None and self.input_path.is_file()

    def composed_lock(self, checkout: Mapping[str, Any] | None = None) -> dict[str, Any]:
        """The shared lock, or the checkout's version set, with the checkout's pins laid over it."""
        document = self.checkout if checkout is None else checkout
        selected = selected_version_lock(document)
        if selected is not None and selected.get("platform") != str(Platform.current()):
            raise ProjectConfigurationError("Local version set is for another platform; follow the project explicitly.")
        return compose_lock(self.manifest, selected if selected is not None else self.shared_lock, document)

    def listing(self, checkout: Mapping[str, Any] | None = None, *, check_display: bool = True) -> Listing:
        document = self.checkout if checkout is None else checkout
        lock = self.composed_lock(document)
        reference = document.get("authorization", {}).get("base-image", {}).get("reference") or lock.get("base", {}).get("reference")
        base = known_base_image(str(reference))
        return assess_checkout(
            self.manifest, self.shared_lock, lock, document,
            workstation=self.workstation, saved_environment=self.saved_environment,
            surfaces=self.surfaces, agents=self.agents, project=self.root, registered=self.registered,
            base_display=base.contract.display if check_display and base is not None else None,
        )

    def with_selection(self, selection: Selection, *, allow_unverified: bool = False,
                       checkout: Mapping[str, Any] | None = None) -> dict[str, Any]:
        """A copy of the checkout document with ``selection`` pinned, for a run-once IDE or agent."""
        document = deepcopy(dict(self.checkout if checkout is None else checkout))
        local = selection.local()
        local.validate(CapabilityPolicy.read(self.manifest))
        previous = LocalCapabilities.read(document)
        selected = selected_version_lock(document)
        version_record = document.pop("version-set", None)
        source = deepcopy(selected if selected is not None else self.shared_lock)
        if selected is not None:
            release_deselected(source, self.matrix, CapabilityPolicy.read(self.manifest), previous, local)
        pins = pin_selection(self.matrix, CapabilityPolicy.read(self.manifest), local, source, previous,
                             local_pins(document), allow_unverified=allow_unverified)
        document["capabilities"] = {"selected": list(local.selected), "without": list(local.without),
                                    "lock": render_toml(pins)}
        if version_record is not None:
            version_record["lock"] = render_toml(compose_lock(self.manifest, source, document))
            document["version-set"] = version_record
        return document


def load_state(root: Path, manifest: dict[str, Any]) -> CheckoutState:
    return CheckoutState(root, manifest)


def register_checkout(state: CheckoutState, *, write: bool = True) -> Path:
    """Give an unregistered checkout its record: the project's default one, or one named after its directory.

    Answer 14 of the work order: ``run`` registers a second checkout of the
    same project by itself, with a name derived from its path; each checkout
    keeps its own record and inherits nothing.
    """
    if state.registered:
        assert state.input_path is not None
        return state.input_path
    if state.input_path is None:
        base = sanitize_name(state.root.name).lower().lstrip("._-") or "checkout"
        for suffix in ("", *(f"-{index}" for index in range(2, 100))):
            candidate, _ = named_checkout_record_paths(state.manifest, f"{base}{suffix}")
            if f"{base}{suffix}" != "default" and not candidate.exists():
                state.input_path = candidate
                break
        else:
            raise ProjectConfigurationError(f"No free checkout name derived from {state.root.name!r}; register one with 'checkout register NAME'.")
    assert state.input_path is not None
    if write:
        atomic_write(state.input_path, render_toml(state.checkout))
    return state.input_path


def derive_plan(state: CheckoutState, checkout: Mapping[str, Any] | None = None, *, write: bool = True) -> ResolvedProject:
    """Derive the launch plan from the state's documents and write it as the checkout's resolution.

    ``checkout`` is the record to derive from when it differs from the one
    on disk, for a run-once IDE or agent. The review must be ready: every
    decision answered; the caller asks or exits 3 before coming here. A
    local base override is validated against the daemon, as the resolve
    step did.
    """
    document = dict(state.checkout if checkout is None else checkout)
    composed = state.composed_lock(document)
    try:
        lock = effective_lock(state.manifest, composed, document, warn=False)
    except ProjectConfigurationError as exc:
        if selected_version_lock(document) is None:
            raise
        command = shlex.join(["devcapsule", "project", "--path", str(state.root), "versions"])
        raise DecisionPending(
            f"Saved version set {canonical_digest(composed)[:12]} cannot run this project: {exc}\n"
            f"Follow the project with {command} follow-project --apply, or select a compatible set with "
            f"{command} select SET. Nothing was written."
        ) from exc
    if not lock.get("components", {}).get("interactive-surface"):
        raise ProjectConfigurationError("Choose your IDE for this checkout: devcapsule project config ide IDE.")
    configuration = Configuration(state.manifest, lock, document, state.workstation)
    configuration.review().require_ready(state.root)
    resolution = configuration.resolve()
    base_selection = authorized_base_selection(lock, document) if "base" in lock else None
    if base_selection is not None and base_selection.local_image_identity is not None:
        # Looked up through the operations adapter, the one seam the launch
        # and its tests patch for the local daemon.
        from . import operations
        local_base = operations.required_local_image(base_selection.reference)
        validate_base_image(local_base, platform=str(lock["platform"]), expected_identity=base_selection.local_image_identity)
    assert state.input_path is not None
    resolution_path = resolved_record_path(state.input_path)
    if write:
        atomic_write(resolution_path, render_toml(resolution.document()))
    return ResolvedProject(state.root, state.manifest, state.lock_path, lock, state.input_path, document,
                           resolution_path, resolution.document())
