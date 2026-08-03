"""Versioned, structured contract consumed inside a capsule."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping


class RuntimePlanError(ValueError):
    """The runtime plan is malformed or unsupported."""


def _required_string(value: object, field: str) -> str:
    if not isinstance(value, str) or not value or "\x00" in value:
        raise RuntimePlanError(f"{field} must be a non-empty string")
    return value


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
    adapter: str
    configuration: Mapping[str, object]


@dataclass(frozen=True)
class RuntimePlan:
    version: int
    project_path: str
    home: str
    identity: Identity
    state_slots: tuple[StateSlot, ...]
    component: Component

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
            slots.append(StateSlot(name, _required_string(slot.get("path"), f"state_slots[{index}].path")))
        component_value = document.get("component")
        if not isinstance(component_value, dict):
            raise RuntimePlanError("component must be an object")
        configuration = component_value.get("configuration", {})
        if not isinstance(configuration, dict):
            raise RuntimePlanError("component.configuration must be an object")
        return cls(
            version=1,
            project_path=_required_string(document.get("project_path"), "project_path"),
            home=_required_string(document.get("home"), "home"),
            identity=Identity(uid, gid, _required_string(identity_value.get("user", "devcapsule"), "identity.user")),
            state_slots=tuple(slots),
            component=Component(_required_string(component_value.get("adapter"), "component.adapter"), configuration),
        )

    def slots_by_name(self) -> dict[str, str]:
        return {slot.name: slot.path for slot in self.state_slots}
