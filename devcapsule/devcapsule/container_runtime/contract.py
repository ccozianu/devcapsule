"""Versioned, structured contract consumed inside a capsule."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any, Mapping


class RuntimePlanError(ValueError):
    """The runtime plan is malformed or unsupported."""


def _required_string(value: object, field: str) -> str:
    if not isinstance(value, str) or not value or "\x00" in value:
        raise RuntimePlanError(f"{field} must be a non-empty string")
    return value


def _required_choice(value: object, field: str, choices: set[str]) -> str:
    selected = _required_string(value, field)
    if selected not in choices:
        expected = ", ".join(sorted(choices))
        raise RuntimePlanError(f"{field} must be one of: {expected}")
    return selected


def _absolute_path(value: object, field: str) -> str:
    selected = _required_string(value, field)
    path = Path(selected)
    if not path.is_absolute() or ".." in path.parts:
        raise RuntimePlanError(f"{field} must be an absolute normalized container path")
    return selected


def _identifier(value: object, field: str) -> str:
    selected = _required_string(value, field)
    if re.fullmatch(r"[a-z0-9][a-z0-9._-]*", selected) is None:
        raise RuntimePlanError(f"{field} must be a lowercase stable identifier")
    return selected


@dataclass(frozen=True)
class Identity:
    uid: int
    gid: int
    user: str = "devcapsule"


@dataclass(frozen=True)
class StateSlot:
    name: str
    path: str


@dataclass(frozen=True)
class Component:
    id: str
    adapter: str
    configuration: Mapping[str, object]
    environment: Mapping[str, str]

    def slot_name(self, local_name: str) -> str:
        return f"{self.id}/{local_name}"


@dataclass(frozen=True)
class StateSlotDeclaration:
    name: str
    container_path: str
    kind: str
    sensitivity: str
    default_scope: str
    storage: str
    concurrent: bool
    owner: str
    permissions: str
    reconstructable: bool
    deletion_effect: str
    home_overlay: bool = False

    @classmethod
    def from_mapping(cls, value: object, field: str) -> StateSlotDeclaration:
        if not isinstance(value, dict):
            raise RuntimePlanError(f"{field} must be an object")
        name = _identifier(value.get("name"), f"{field}.name")
        concurrent = value.get("concurrent")
        if not isinstance(concurrent, bool):
            raise RuntimePlanError(f"{field}.concurrent must be a boolean")
        reconstructable = value.get("reconstructable")
        if not isinstance(reconstructable, bool):
            raise RuntimePlanError(f"{field}.reconstructable must be a boolean")
        home_overlay = value.get("home_overlay", False)
        if not isinstance(home_overlay, bool):
            raise RuntimePlanError(f"{field}.home_overlay must be a boolean")
        permissions = _required_string(value.get("permissions"), f"{field}.permissions")
        if len(permissions) != 4 or permissions[0] != "0" or any(character not in "01234567" for character in permissions):
            raise RuntimePlanError(f"{field}.permissions must be a four-digit octal string")
        return cls(
            name=name,
            container_path=_absolute_path(value.get("container_path"), f"{field}.container_path"),
            kind=_required_choice(value.get("kind"), f"{field}.kind", {"durable", "state", "cache"}),
            sensitivity=_required_choice(
                value.get("sensitivity"),
                f"{field}.sensitivity",
                {"ordinary", "personal", "credentials"},
            ),
            default_scope=_required_choice(
                value.get("default_scope"), f"{field}.default_scope", {"checkout", "project"}
            ),
            storage=_required_choice(
                value.get("storage"), f"{field}.storage", {"directory", "docker-volume"}
            ),
            concurrent=concurrent,
            owner=_required_choice(value.get("owner"), f"{field}.owner", {"runtime-user"}),
            permissions=permissions,
            reconstructable=reconstructable,
            deletion_effect=_required_string(value.get("deletion_effect"), f"{field}.deletion_effect"),
            home_overlay=home_overlay,
        )

    def to_mapping(self) -> dict[str, object]:
        value: dict[str, object] = {
            "name": self.name,
            "container_path": self.container_path,
            "kind": self.kind,
            "sensitivity": self.sensitivity,
            "default_scope": self.default_scope,
            "storage": self.storage,
            "concurrent": self.concurrent,
            "owner": self.owner,
            "permissions": self.permissions,
            "reconstructable": self.reconstructable,
            "deletion_effect": self.deletion_effect,
        }
        if self.home_overlay:
            value["home_overlay"] = True
        return value


@dataclass(frozen=True)
class PersistenceContract:
    home: str
    xdg: str
    state_slots: tuple[StateSlotDeclaration, ...]


@dataclass(frozen=True)
class ComponentRuntimeTemplate:
    version: int
    component: Component
    persistence: PersistenceContract

    @classmethod
    def from_mapping(cls, document: object) -> ComponentRuntimeTemplate:
        if not isinstance(document, dict):
            raise RuntimePlanError("component runtime template must be a JSON object")
        version = document.get("version")
        if version != 1:
            raise RuntimePlanError(f"unsupported component runtime template version: {version!r}")
        component_value = document.get("component")
        if not isinstance(component_value, dict):
            raise RuntimePlanError("component must be an object")
        component_id = _identifier(component_value.get("id"), "component.id")
        configuration = component_value.get("configuration", {})
        if not isinstance(configuration, dict):
            raise RuntimePlanError("component.configuration must be an object")
        environment = _environment_mapping(
            component_value.get("environment", {}), "component.environment"
        )
        persistence_value = component_value.get("persistence")
        if not isinstance(persistence_value, dict):
            raise RuntimePlanError("component.persistence must be an object")
        slots_value = persistence_value.get("state_slots", [])
        if not isinstance(slots_value, list):
            raise RuntimePlanError("component.persistence.state_slots must be an array")
        slots = tuple(
            StateSlotDeclaration.from_mapping(slot, f"component.persistence.state_slots[{index}]")
            for index, slot in enumerate(slots_value)
        )
        cls._validate_slots(slots)
        return cls(
            version=1,
            component=Component(
                component_id,
                _required_string(component_value.get("adapter"), "component.adapter"),
                configuration,
                environment,
            ),
            persistence=PersistenceContract(
                home=_required_choice(
                    persistence_value.get("home"),
                    "component.persistence.home",
                    {"available", "required"},
                ),
                xdg=_required_choice(
                    persistence_value.get("xdg"),
                    "component.persistence.xdg",
                    {"home-relative", "unused"},
                ),
                state_slots=slots,
            ),
        )

    @classmethod
    def from_json(cls, value: str) -> ComponentRuntimeTemplate:
        try:
            document = json.loads(value)
        except json.JSONDecodeError as error:
            raise RuntimePlanError(f"component runtime template is not valid JSON: {error.msg}") from error
        return cls.from_mapping(document)

    @staticmethod
    def _validate_slots(slots: tuple[StateSlotDeclaration, ...]) -> None:
        names: set[str] = set()
        for slot in slots:
            if slot.name in names:
                raise RuntimePlanError(f"duplicate component state slot: {slot.name}")
            names.add(slot.name)
        for index, slot in enumerate(slots):
            path = Path(slot.container_path)
            home = Path("/home/devcapsule")
            if path != home and home in path.parents and not slot.home_overlay:
                raise RuntimePlanError(
                    f"component state slot {slot.name!r} is beneath persistent home and must declare home_overlay"
                )
            for other in slots[index + 1 :]:
                other_path = Path(other.container_path)
                if path == other_path or path in other_path.parents or other_path in path.parents:
                    raise RuntimePlanError(
                        f"component state slots {slot.name!r} and {other.name!r} have conflicting container paths"
                    )

    def logical_slot_name(self, local_name: str) -> str:
        return self.component.slot_name(local_name)

    def to_mapping(self) -> dict[str, object]:
        component: dict[str, object] = {
            "id": self.component.id,
            "adapter": self.component.adapter,
            "configuration": dict(self.component.configuration),
            "persistence": {
                "home": self.persistence.home,
                "xdg": self.persistence.xdg,
                "state_slots": [slot.to_mapping() for slot in self.persistence.state_slots],
            },
        }
        if self.component.environment:
            component["environment"] = dict(self.component.environment)
        return {
            "version": self.version,
            "component": component,
        }


@dataclass(frozen=True)
class RuntimePlan:
    version: int
    project_path: str
    home: str
    identity: Identity
    state_slots: tuple[StateSlot, ...]
    component: Component
    ancillary_components: tuple[Component, ...] = ()

    @classmethod
    def for_component(
        cls,
        template: ComponentRuntimeTemplate,
        *,
        project_path: str,
        home: str,
        identity: Identity,
        ancillary_templates: tuple[ComponentRuntimeTemplate, ...] = (),
        include_ancillary_state: bool = True,
    ) -> RuntimePlan:
        templates = (template, *ancillary_templates)
        cls._validate_components(tuple(item.component for item in templates))
        return cls(
            version=1,
            project_path=_absolute_path(project_path, "project_path"),
            home=_absolute_path(home, "home"),
            identity=identity,
            state_slots=tuple(
                StateSlot(item.logical_slot_name(slot.name), slot.container_path)
                for item in (templates if include_ancillary_state else (template,))
                for slot in item.persistence.state_slots
            ),
            component=template.component,
            ancillary_components=tuple(item.component for item in ancillary_templates),
        )

    @classmethod
    def from_json(cls, value: str) -> RuntimePlan:
        try:
            document = json.loads(value)
        except json.JSONDecodeError as error:
            raise RuntimePlanError(f"runtime plan is not valid JSON: {error.msg}") from error
        return cls.from_mapping(document)

    @classmethod
    def from_file(cls, path: str | Path) -> RuntimePlan:
        try:
            return cls.from_json(Path(path).read_text(encoding="utf-8"))
        except OSError as error:
            raise RuntimePlanError(f"cannot read runtime plan {path}: {error}") from error

    @classmethod
    def from_mapping(cls, document: object) -> RuntimePlan:
        if not isinstance(document, dict):
            raise RuntimePlanError("runtime plan must be a JSON object")
        version = document.get("version")
        if version != 1:
            raise RuntimePlanError(f"unsupported runtime plan version: {version!r}")
        identity_value = document.get("identity")
        if not isinstance(identity_value, dict):
            raise RuntimePlanError("identity must be an object")
        uid, gid = identity_value.get("uid"), identity_value.get("gid")
        if not isinstance(uid, int) or isinstance(uid, bool) or uid < 0:
            raise RuntimePlanError("identity.uid must be a non-negative integer")
        if not isinstance(gid, int) or isinstance(gid, bool) or gid < 0:
            raise RuntimePlanError("identity.gid must be a non-negative integer")
        slots_value = document.get("state_slots", [])
        if not isinstance(slots_value, list):
            raise RuntimePlanError("state_slots must be an array")
        slots: list[StateSlot] = []
        names: set[str] = set()
        for index, slot in enumerate(slots_value):
            if not isinstance(slot, dict):
                raise RuntimePlanError(f"state_slots[{index}] must be an object")
            name = _required_string(slot.get("name"), f"state_slots[{index}].name")
            if name in names:
                raise RuntimePlanError(f"duplicate state slot: {name}")
            names.add(name)
            slots.append(StateSlot(name, _absolute_path(slot.get("path"), f"state_slots[{index}].path")))
        component = cls._component_from_mapping(document.get("component"), "component")
        ancillary_value = document.get("ancillary_components", [])
        if not isinstance(ancillary_value, list):
            raise RuntimePlanError("ancillary_components must be an array")
        ancillary = tuple(
            cls._component_from_mapping(value, f"ancillary_components[{index}]")
            for index, value in enumerate(ancillary_value)
        )
        cls._validate_components((component, *ancillary))
        prefixes = {item.id for item in (component, *ancillary)}
        for slot in slots:
            namespace, separator, local_name = slot.name.partition("/")
            if not separator or namespace not in prefixes:
                raise RuntimePlanError(
                    f"runtime state slot {slot.name!r} must be namespaced by a declared component"
                )
            _identifier(local_name, f"runtime state slot {slot.name!r}")
        return cls(
            version=1,
            project_path=_absolute_path(document.get("project_path"), "project_path"),
            home=_absolute_path(document.get("home"), "home"),
            identity=Identity(uid, gid, _required_string(identity_value.get("user", "devcapsule"), "identity.user")),
            state_slots=tuple(slots),
            component=component,
            ancillary_components=ancillary,
        )

    @staticmethod
    def _component_from_mapping(value: object, field: str) -> Component:
        if not isinstance(value, dict):
            raise RuntimePlanError(f"{field} must be an object")
        configuration = value.get("configuration", {})
        if not isinstance(configuration, dict):
            raise RuntimePlanError(f"{field}.configuration must be an object")
        return Component(
            _identifier(value.get("id"), f"{field}.id"),
            _required_string(value.get("adapter"), f"{field}.adapter"),
            configuration,
            _environment_mapping(value.get("environment", {}), f"{field}.environment"),
        )

    @staticmethod
    def _validate_components(components: tuple[Component, ...]) -> None:
        identifiers: set[str] = set()
        environment: dict[str, str] = {}
        for component in components:
            if component.id in identifiers:
                raise RuntimePlanError(f"duplicate runtime component: {component.id}")
            identifiers.add(component.id)
            for name, value in component.environment.items():
                previous = environment.get(name)
                if previous is not None and previous != value:
                    raise RuntimePlanError(
                        f"runtime components declare conflicting values for environment variable {name}"
                    )
                environment[name] = value

    def component_environment(self) -> dict[str, str]:
        result: dict[str, str] = {}
        for component in (self.component, *self.ancillary_components):
            result.update(component.environment)
        return result

    def slots_by_name(self) -> dict[str, str]:
        return {slot.name: slot.path for slot in self.state_slots}

    def to_mapping(self) -> dict[str, object]:
        component: dict[str, object] = {
            "id": self.component.id,
            "adapter": self.component.adapter,
            "configuration": dict(self.component.configuration),
        }
        if self.component.environment:
            component["environment"] = dict(self.component.environment)
        result: dict[str, object] = {
            "version": self.version,
            "project_path": self.project_path,
            "home": self.home,
            "identity": {
                "uid": self.identity.uid,
                "gid": self.identity.gid,
                "user": self.identity.user,
            },
            "state_slots": [
                {"name": slot.name, "path": slot.path} for slot in self.state_slots
            ],
            "component": component,
        }
        if self.ancillary_components:
            result["ancillary_components"] = [
                _runtime_component_mapping(item) for item in self.ancillary_components
            ]
        return result

    def to_json(self) -> str:
        return json.dumps(
            self.to_mapping(),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )


def _environment_mapping(value: object, field: str) -> dict[str, str]:
    if not isinstance(value, dict):
        raise RuntimePlanError(f"{field} must be an object")
    environment: dict[str, str] = {}
    for name, raw_value in value.items():
        if not isinstance(name, str) or re.fullmatch(r"[A-Z_][A-Z0-9_]*", name) is None:
            raise RuntimePlanError(f"{field} names must be uppercase environment identifiers")
        environment[name] = _required_string(raw_value, f"{field}.{name}")
    return environment


def _runtime_component_mapping(component: Component) -> dict[str, object]:
    value: dict[str, object] = {
        "id": component.id,
        "adapter": component.adapter,
        "configuration": dict(component.configuration),
    }
    if component.environment:
        value["environment"] = dict(component.environment)
    return value
