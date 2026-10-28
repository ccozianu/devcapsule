"""The workstation's own configuration: defaults that apply to every project here.

The CLI UX redesign work order of 2026-10-24, answer 6: the launcher owns
the container's memory limit and CPU count. Each has a workstation default,
set once with ``config default NAME VALUE`` and kept in
``$XDG_CONFIG_HOME/devcapsule/workstation.toml``; a project may recommend a
value, and a checkout may set its own. The precedence is the checkout's
answer, then the project's recommendation, then the workstation default,
then no limit at all.

This module is pure: it validates and renders the document. Reading and
writing the file belongs to :mod:`storage`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from .file_formats import ProjectConfigurationError, table
from .values import LAUNCHER_VALUE_NAMES, normalize_launcher_value

__all__ = ["WORKSTATION_SCHEMA_VERSION", "WorkstationDefaults", "render_workstation"]

WORKSTATION_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class WorkstationDefaults:
    """The launcher-owned values this workstation applies when neither a checkout nor a project says."""

    values: dict[str, str | int] = field(default_factory=dict)

    @classmethod
    def read(cls, document: Mapping[str, Any]) -> WorkstationDefaults:
        defaults = table(document, "defaults")
        unknown = sorted(set(defaults) - set(LAUNCHER_VALUE_NAMES))
        if unknown:
            raise ProjectConfigurationError(
                "The workstation configuration defaults " + ", ".join(unknown)
                + "; the launcher owns " + ", ".join(LAUNCHER_VALUE_NAMES) + "."
            )
        values = {name: normalize_launcher_value(name, defaults[name], field_name=f"workstation default {name}")
                  for name in LAUNCHER_VALUE_NAMES if name in defaults}
        return cls(values)

    def with_value(self, name: str, value: str | int | None) -> WorkstationDefaults:
        """A copy with ``name`` set, or removed when ``value`` is None."""
        values = dict(self.values)
        if value is None:
            values.pop(name, None)
        else:
            values[name] = normalize_launcher_value(name, value, field_name=f"workstation default {name}")
        return WorkstationDefaults(values)

    def document(self) -> dict[str, Any]:
        return {"defaults": dict(sorted(self.values.items()))}


def render_workstation(defaults: WorkstationDefaults) -> str:
    lines = ["[defaults]"]
    for name, value in sorted(defaults.values.items()):
        rendered = str(value) if isinstance(value, int) else f'"{value}"'
        lines.append(f"{name} = {rendered}")
    return "\n".join(lines) + "\n"
