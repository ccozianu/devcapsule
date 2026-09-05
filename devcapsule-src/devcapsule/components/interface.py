"""Trusted Python interface exposed by curated DevCapsule components."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass

from devcapsule.container_runtime.contract import ComponentRuntimeTemplate


@dataclass(frozen=True)
class StateEnvironmentDeclaration:
    """Expose one component state directory through an environment variable."""

    name: str
    state_slot: str


@dataclass(frozen=True)
class SecretInputDeclaration:
    """Describe a secret a developer may explicitly deliver at runtime."""

    name: str
    environment_variable: str
    required: bool
    description: str
    exposure: str = "container-environment"


@dataclass(frozen=True)
class AcquisitionContract:
    """A vendor acquisition the developer must authorize before materialization.

    Declared by components whose artifacts are proprietary and licensed to the
    downloading user only: acceptance travels with the download, so DevCapsule
    puts this explicit authorization in front of it and never redistributes
    the result.
    """

    authorization: str
    terms_url: str
    display_name: str
    vendor: str


@dataclass(frozen=True)
class LockedArtifactDeclaration:
    """One lock-pinned artifact contribution to a local environment image.

    ``artifact_format`` says how the verified download becomes image content:

    - ``file``: the download is the executable; it is copied to ``destination``.
    - ``tar-gz-member``: exactly one regular file, ``archive_member``, is
      extracted from the tarball and copied to ``destination``.
    - ``npm-package``: the download is an npm tarball, installed with npm's
      own layout into the ``destination`` directory under the dependency
      name ``npm_package``.  Every ``npm-package`` artifact sharing a
      destination is one npm project: the vendor's tested package tree,
      launcher included, ends up under ``destination/node_modules`` and
      nothing is plucked out of it.  Components whose vendor publishes a
      meta package plus per-platform packages declare one artifact each.
    """

    component_id: str
    version: str
    url: str
    sha256: str
    destination: str
    artifact_format: str = "tar-gz-member"
    archive_member: str | None = None
    npm_package: str | None = None
    permissions: int = 0o755
    environment: tuple[tuple[str, str], ...] = ()


class ComponentDefinition(ABC):
    """Explicit contract for trusted components consumed by orchestration."""

    @property
    @abstractmethod
    def id(self) -> str:
        """Stable component identifier used by locks and runtime plans."""

    @property
    @abstractmethod
    def capability(self) -> str:
        """Project-facing capability implemented by this component."""

    def acquisition(self) -> AcquisitionContract | None:
        """The vendor acquisition this component requires, if any.

        Freely redistributable components return None (the default); a
        component whose artifact carries per-user vendor terms returns the
        contract that gates its download behind an authorization node.
        """

        return None

    @abstractmethod
    def runtime_template(self) -> ComponentRuntimeTemplate:
        """Return the component's validated, versioned runtime contract."""

    @abstractmethod
    def state_environment(self) -> tuple[StateEnvironmentDeclaration, ...]:
        """Declare environment variables derived from component state slots."""

    @abstractmethod
    def secret_inputs(self) -> tuple[SecretInputDeclaration, ...]:
        """Declare secret inputs that a developer may explicitly bind."""

    @abstractmethod
    def locked_artifacts(
        self, metadata: Mapping[str, object], platform: str
    ) -> tuple[LockedArtifactDeclaration, ...]:
        """Resolve checksum-pinned artifacts selected by component lock metadata."""


def resolved_state_environment(
    template: ComponentRuntimeTemplate,
    declarations: tuple[StateEnvironmentDeclaration, ...],
) -> dict[str, str]:
    slots = {slot.name: slot.container_path for slot in template.persistence.state_slots}
    environment: dict[str, str] = {}
    for declaration in declarations:
        try:
            environment[declaration.name] = slots[declaration.state_slot]
        except KeyError as exc:
            raise ValueError(
                f"component {template.component.id!r} environment {declaration.name!r} "
                f"names undeclared state slot {declaration.state_slot!r}"
            ) from exc
    return environment
