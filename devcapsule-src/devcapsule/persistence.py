"""Generic host-side planning for component-declared persistent state."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
from typing import Mapping

from devcapsule.container_runtime.contract import (
    ComponentRuntimeTemplate,
    Identity,
    RuntimePlan,
    RuntimePlanError,
    StateSlotDeclaration,
)


@dataclass(frozen=True)
class StateRoots:
    data: Path
    state: Path
    cache: Path

    @classmethod
    def from_environment(cls, env: Mapping[str, str] | None = None) -> StateRoots:
        values = os.environ if env is None else env
        home = Path(values.get("HOME", "~")).expanduser()
        return cls(
            data=Path(values.get("XDG_DATA_HOME") or home / ".local" / "share") / "devcapsule",
            state=Path(values.get("XDG_STATE_HOME") or home / ".local" / "state") / "devcapsule",
            cache=Path(values.get("XDG_CACHE_HOME") or home / ".cache") / "devcapsule",
        )

    def for_kind(self, kind: str) -> Path:
        if kind == "durable":
            return self.data
        if kind == "state":
            return self.state
        if kind == "cache":
            return self.cache
        raise RuntimePlanError(f"unsupported component state kind: {kind!r}")


@dataclass(frozen=True)
class PersistentMount:
    logical_name: str
    source: str
    destination: str
    storage: str
    declaration: StateSlotDeclaration | None = None


@dataclass(frozen=True)
class ComponentPersistencePlan:
    template: ComponentRuntimeTemplate
    mounts: tuple[PersistentMount, ...]

    @property
    def home(self) -> PersistentMount:
        return self.mounts[0]

    def runtime_plan(self, *, project_path: str, identity: Identity) -> RuntimePlan:
        return RuntimePlan.for_component(
            self.template,
            project_path=project_path,
            home=self.home.destination,
            identity=identity,
        )


def plan_component_persistence(
    template: ComponentRuntimeTemplate,
    *,
    roots: StateRoots,
    checkout_namespace: Path,
    project_namespace: Path | None = None,
    adopted: Mapping[str, str | Path] | None = None,
    container_home: str = "/home/devcapsule",
) -> ComponentPersistencePlan:
    """Resolve generic host storage without interpreting component or slot names."""

    checkout = _relative_namespace(checkout_namespace, "checkout_namespace")
    project = _relative_namespace(project_namespace or checkout, "project_namespace")
    overrides = {} if adopted is None else adopted
    home_source = _directory_source(overrides.get("home", roots.data / checkout / "home"), "home")
    mounts = [PersistentMount("home", home_source, container_home, "directory")]
    for declaration in template.persistence.state_slots:
        logical_name = template.logical_slot_name(declaration.name)
        namespace = checkout if declaration.default_scope == "checkout" else project
        if declaration.storage == "directory":
            default_source = (
                roots.for_kind(declaration.kind)
                / namespace
                / "components"
                / template.component.id
                / declaration.name
            )
            source = _directory_source(overrides.get(logical_name, default_source), logical_name)
        else:
            if logical_name in overrides:
                raise RuntimePlanError(
                    f"{logical_name} uses Docker-volume storage and cannot be adopted from a host directory"
                )
            source = _volume_name(namespace, template.component.id, declaration.name)
        mounts.append(
            PersistentMount(
                logical_name,
                source,
                declaration.container_path,
                declaration.storage,
                declaration,
            )
        )
    # Parent mounts must be passed to Docker before their declared overlays.
    ordered = (mounts[0], *sorted(mounts[1:], key=lambda mount: len(Path(mount.destination).parts)))
    return ComponentPersistencePlan(template, ordered)


def prepare_persistence_directories(plan: ComponentPersistencePlan) -> None:
    """Create only directory-backed storage selected by an already-reviewed plan."""

    for mount in plan.mounts:
        if mount.storage == "directory":
            Path(mount.source).mkdir(parents=True, exist_ok=True)


def _relative_namespace(value: Path, field: str) -> Path:
    if value.is_absolute() or value in {Path(""), Path(".")} or ".." in value.parts:
        raise RuntimePlanError(f"{field} must be a non-empty relative namespace")
    return value


def _directory_source(value: str | Path, logical_name: str) -> str:
    path = Path(value).expanduser()
    if not path.is_absolute():
        raise RuntimePlanError(f"state binding {logical_name!r} must use an absolute host directory")
    return str(path)


def _volume_name(namespace: Path, component_id: str, slot_name: str) -> str:
    identity = hashlib.sha256(f"{namespace}/{component_id}/{slot_name}".encode()).hexdigest()[:24]
    return f"devcapsule-{identity}"
