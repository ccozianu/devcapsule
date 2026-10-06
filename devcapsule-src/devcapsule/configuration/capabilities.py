"""Capability policy values. Parsing does not depend on the installed catalog.

The project owns required/optional intent and SDK majors. The developer owns
extra selections and omissions. Unknown optional names remain ordinary data;
only a consumer decides which of them it can supply.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .documents import ProjectConfigurationError, table


def names(value: object, label: str) -> tuple[str, ...]:
    """Return sorted, unique names from a decoded TOML array.

    Raise ProjectConfigurationError, using ``label`` to identify the field,
    unless every item is a nonempty, trimmed string without NUL characters.
    Names need not be known to this launcher's component catalog.
    """
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item or item.strip() != item or "\x00" in item
        for item in value
    ):
        raise ProjectConfigurationError(f"{label} must be an array of non-empty capability names.")
    return tuple(sorted(set(value)))


@dataclass(frozen=True)
class CapabilityPolicy:
    """The development capabilities a project asks every checkout to provide.

    These are shared requirements from the manifest's ``[capabilities]``
    table. Personal IDE/agent choices belong to LocalCapabilities.

    Attributes:
        required: Capability names that must be supplied before launch, such
            as ``("python",)``. Names identify functionality, not component
            packages: ``"python-ide"``, for example, is supplied by PyCharm.
        optional: Desired enhancements, such as ``("browser-automation",)``.
            A reader may omit unavailable enhancements with a warning.
            No name may also appear in ``required``.
        sdk_major: Exact SDK major-version constraints, stored as sorted
            ``(capability_name, major_version)`` pairs. ``(("python", 3),)``
            requires Python 3; minor/patch versions come from the lock.
            Each name must be required and each major a positive integer.
            An empty tuple imposes no major-version constraints.
        layered: True when read from ``capabilities.required``; False when
            read from legacy ``capabilities.need``. This selects compatibility
            behavior when consuming old locks; it is not a TOML field.

    Use ``read(manifest)`` for external data. Direct construction assumes
    valid, normalized fields: names and SDK pairs are sorted and unique.
    This value describes intent; lock selection checks whether it can be met.
    """
    required: tuple[str, ...]
    optional: tuple[str, ...] = ()
    sdk_major: tuple[tuple[str, int], ...] = ()
    layered: bool = False

    @classmethod
    def read(cls, manifest: Mapping[str, Any]) -> CapabilityPolicy:
        """Read the capabilities table from a full decoded manifest.

        Normalize name lists and validate the field rules above, raising
        ProjectConfigurationError for malformed or conflicting declarations.
        Leave the input unchanged and accept unknown capability names;
        catalog support is checked later.
        """
        value = table(manifest, "capabilities")
        layered = "required" in value
        if layered and "need" in value:
            raise ProjectConfigurationError("Use capabilities.required or legacy capabilities.need, not both.")
        key = "required" if layered else "need"
        required = names(value.get(key), f"capabilities.{key}")
        optional = names(value.get("optional", []), "capabilities.optional")
        overlap = set(required) & set(optional)
        if overlap:
            raise ProjectConfigurationError(f"Capabilities cannot be both required and optional: {', '.join(sorted(overlap))}.")
        majors = table(value, "sdk-major")
        for capability, major in majors.items():
            if capability not in required or type(major) is not int or major < 1:
                raise ProjectConfigurationError("Each capabilities.sdk-major entry must name a required capability and a positive integer major.")
        return cls(required, optional, tuple(sorted(majors.items())), layered)

    def document(self) -> dict[str, Any]:
        """Return a fresh ``[capabilities]`` table using the ``required`` form.

        The result contains only this policy's fields, not the whole manifest
        or unrecognized fields from the input. Legacy ``need`` is not emitted.
        """
        return {"required": list(self.required), "optional": list(self.optional),
                "sdk-major": dict(self.sdk_major)}


@dataclass(frozen=True)
class LocalCapabilities:
    """One developer's additions and omissions for a project checkout.

    ``selected`` contains capability names chosen locally, such as
    ``("codex-agent", "python-ide")``. Once selected, these must be supplied
    for this checkout to launch. ``without`` contains project optional names
    to skip, such as ``("browser-automation",)``; it cannot waive a required
    capability or a dependency needed by another selected capability.

    Both tuples are sorted and unique, with no name in both. Use
    ``read(checkout)`` then ``validate(policy)`` for external data; direct
    construction assumes these invariants. Version pins remain in the
    checkout document's embedded lock, outside this value.
    """
    selected: tuple[str, ...] = ()
    without: tuple[str, ...] = ()

    @classmethod
    def read(cls, checkout: Mapping[str, Any]) -> LocalCapabilities:
        """Read selections from a full decoded checkout without changing it.

        A missing capabilities table means no additions or omissions.
        Raise ProjectConfigurationError for invalid fields or overlapping
        choices. An embedded lock must be a string; parsing its contents and
        checking catalog support belong to lock selection, not this method.
        """
        value = table(checkout, "capabilities")
        if set(value) - {"selected", "without", "lock"}:
            raise ProjectConfigurationError("Unsupported local capability fields; left intact.")
        selected = names(value.get("selected", []), "local capabilities.selected")
        without = names(value.get("without", []), "local capabilities.without")
        if set(selected) & set(without):
            raise ProjectConfigurationError("A local capability cannot be both selected and omitted.")
        if "lock" in value and not isinstance(value["lock"], str):
            raise ProjectConfigurationError("Local capabilities.lock must contain a TOML lock.")
        return cls(selected, without)

    def validate(self, policy: CapabilityPolicy) -> None:
        """Raise ProjectConfigurationError if an omission is not project-optional.

        Call after ``read`` to check choices against a particular project.
        This does not check provider availability or change either value.
        """
        invalid = set(self.without) - set(policy.optional)
        if invalid:
            raise ProjectConfigurationError("Only project optional capabilities may be omitted locally: " + ", ".join(sorted(invalid)) + ".")
