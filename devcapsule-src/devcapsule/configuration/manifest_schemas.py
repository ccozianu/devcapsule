"""The project manifest's two schemas, each as a class, and the one migration between them.

A manifest, ``.devcapsule/devcapsule.toml``, says which schema it is written
in with ``devcapsule-schema-version``.  This module is the only place that
says what each schema may contain and how a schema-1 file becomes schema 2:

* :class:`ManifestV1` is the file as launchers before 0.3.0 rc4 wrote it.
  Its capabilities come in one of two forms, ``need`` (one list, the IDE
  among the names) or ``required``/``optional`` as rc3 wrote them, both
  beside a retired ``sdk-major`` table.  The root key ``workflow-type`` may
  stand beside ``[workflow]``.  It has no environment declarations and no
  recommendations: those are schema-2 words, and a file that uses them says 2.
* :class:`ManifestV2` is the file as the one writer, ``render_manifest``,
  writes it since rc4: ``required`` with minimums and ``optional``, the
  owner's reasons, the environment the project asks for, the ordinary
  recommendations (the IDE, memory, CPUs).  It has no ``need`` list.  A
  root ``workflow-type``, which the writers of rc4 to rc7 carried over from
  schema-1 files, is folded into ``[workflow].mode`` on reading and never
  written again.
* :func:`read_manifest` admits a decoded file as the class its version names.
* :func:`upgrade` turns a V1 into a V2 in memory, by the laws its docstring
  states.  Writing the result is the caller's act: an owner's edit or
  ``project init --regenerate``; no other command rewrites a schema-1 file
  (R-CONFIG-001, decision 19 of the CLI UX order).

Each class is strict about the other schema's words and tolerant of what
neither schema names: unknown root tables and unknown keys under
``[capabilities]`` are carried as extensions, so an edit by this launcher
never drops a newer owner's field.  The retired ``sdk-major`` table is
tolerated on both, carried in memory so ``capability_notes`` can say it is
ignored, and dropped by the writer.

The module is pure and knows no catalog.  The one catalog question the
migration asks, which names are IDE capabilities, is the ``ide`` function
the caller passes to :func:`upgrade`.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Callable, ClassVar, Mapping

from devcapsule.project import ProjectMountError, normalize_project_mount

from .capabilities import RETIRED_CAPABILITY_FIELD, CapabilityPolicy, names, requirement, resolution_recommendations
from .file_formats import ConfigurationFileKind, ProjectConfigurationError, table, validate_file_format
from .manifest_document import EnvironmentPolicy, Recommendations, capability_reasons
from .values import configuration_value_declarations

__all__ = ["ManifestV1", "ManifestV2", "NeedForm", "RequiredForm", "read_manifest", "upgrade"]

VERSION_KEY = "devcapsule-schema-version"

# The root keys each schema names; every other root key is an extension.
_V1_ROOT = frozenset({VERSION_KEY, "project", "capabilities", "host", "configuration", "workflow", "workflow-type"})
_V2_ROOT = frozenset({VERSION_KEY, "project", "capabilities", "environment", "recommendations", "host", "configuration", "workflow"})
# The keys each schema names under [capabilities]; every other key is an extension.
_V1_CAPABILITIES = frozenset({"need", "required", "optional", "resolution", RETIRED_CAPABILITY_FIELD})
_V2_CAPABILITIES = frozenset({"required", "optional", "reasons", "resolution", RETIRED_CAPABILITY_FIELD})


def _project(document: Mapping[str, Any], source: object) -> dict[str, Any]:
    """The ``[project]`` table: name, slug, creator and mount, as strings, the mount valid for the slug."""
    project = document.get("project")
    if not isinstance(project, dict) or not all(
        isinstance(project.get(key), str) and project[key] and "\x00" not in project[key]
        for key in ("name", "slug", "creator", "mount")
    ):
        raise ProjectConfigurationError(f"{source} must define project name, slug, creator, and mount.")
    try:
        normalize_project_mount(project["mount"], project["slug"])
    except ProjectMountError as exc:
        raise ProjectConfigurationError(f"{source}: {exc}") from exc
    return deepcopy(project)


def _optional_table(document: Mapping[str, Any], key: str, source: object) -> dict[str, Any] | None:
    value = document.get(key)
    if value is None:
        return None
    if not isinstance(value, dict):
        raise ProjectConfigurationError(f"{source}: {key} must be a table.")
    return deepcopy(value)


def _written_names(value: object, label: str) -> tuple[str, ...]:
    """A capability list as written: validated like ``names``, in the file's order, without duplicates."""
    names(value, label)
    assert isinstance(value, list)  # names() admitted it
    return tuple(dict.fromkeys(str(item) for item in value))


def _fold_workflow_type(workflow: dict[str, Any] | None, workflow_type: object, source: object) -> dict[str, Any] | None:
    """``workflow-type`` folded into ``[workflow].mode``: taken when ``mode`` is absent, dropped when equal, refused when they disagree."""
    if workflow_type is None:
        return workflow
    if not isinstance(workflow_type, str):
        raise ProjectConfigurationError(f"{source}: workflow-type must be a string.")
    mode = (workflow or {}).get("mode")
    if mode is None:
        return {"mode": workflow_type, **(workflow or {})}
    if mode != workflow_type:
        raise ProjectConfigurationError(
            f"{source} says workflow-type = {workflow_type!r} and [workflow].mode = {mode!r}; "
            "they must agree before the file can be written as schema 2."
        )
    return workflow


def _refuse(source: object, found: str, belongs_to: int, says: int) -> ProjectConfigurationError:
    return ProjectConfigurationError(
        f"{source} says {VERSION_KEY} = {says} but declares {found}, a schema-{belongs_to} word; "
        f"a schema-{belongs_to} manifest says {VERSION_KEY} = {belongs_to}."
    )


@dataclass(frozen=True)
class NeedForm:
    """Schema 1's ``need`` list: every name is required, the IDE capability among them."""

    need: tuple[str, ...]
    optional: tuple[str, ...] = ()


@dataclass(frozen=True)
class RequiredForm:
    """Schema 1's ``required`` and ``optional`` lists, as 0.3.0 rc3 wrote them."""

    required: tuple[str, ...]
    optional: tuple[str, ...] = ()


@dataclass(frozen=True)
class ManifestV1:
    """A manifest as launchers before 0.3.0 rc4 wrote it; read, never written.

    ``form`` is the capability declaration in the form the file used.
    ``workflow_type`` is the root key that preceded ``[workflow].mode``.
    ``retired`` holds the ``sdk-major`` table when the file still has one.
    ``capability_extensions`` and ``extensions`` are what neither schema
    names, carried untouched.
    """

    version: ClassVar[int] = 1

    project: dict[str, Any]
    form: NeedForm | RequiredForm
    resolution: dict[str, str] = field(default_factory=dict)
    host: dict[str, Any] = field(default_factory=dict)
    configuration: dict[str, Any] = field(default_factory=dict)
    workflow: dict[str, Any] | None = None
    workflow_type: str | None = None
    retired: dict[str, Any] = field(default_factory=dict)
    capability_extensions: dict[str, Any] = field(default_factory=dict)
    extensions: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def read(cls, document: Mapping[str, Any], source: object) -> ManifestV1:
        """Admit a decoded schema-1 file, refusing schema-2 words by name."""
        validate_file_format(document, ConfigurationFileKind.manifest, source)
        if document[VERSION_KEY] != cls.version:
            raise ProjectConfigurationError(f"{source} is not a schema-{cls.version} manifest; it says {document[VERSION_KEY]!r}.")
        for word in ("environment", "recommendations"):
            if word in document:
                raise _refuse(source, f"[{word}]", belongs_to=2, says=1)
        capabilities = table(document, "capabilities")
        if "reasons" in capabilities:
            raise _refuse(source, "[capabilities.reasons]", belongs_to=2, says=1)
        if "need" in capabilities and "required" in capabilities:
            raise ProjectConfigurationError(f"{source}: use capabilities.need or capabilities.required, not both.")
        optional = _written_names(capabilities.get("optional", []), "capabilities.optional")
        form: NeedForm | RequiredForm
        if "need" in capabilities:
            form = NeedForm(_written_names(capabilities["need"], "capabilities.need"), optional)
        else:
            form = RequiredForm(_written_names(capabilities.get("required", []), "capabilities.required"), optional)
        for item in (*form.optional, *(form.need if isinstance(form, NeedForm) else form.required)):
            requirement(item)
        workflow_type = document.get("workflow-type")
        if workflow_type is not None and not isinstance(workflow_type, str):
            raise ProjectConfigurationError(f"{source}: workflow-type must be a string.")
        _fold_workflow_type(_optional_table(document, "workflow", source), workflow_type, source)  # Refuse a disagreement now.
        configuration = _optional_table(document, "configuration", source) or {}
        configuration_value_declarations(document, source=str(source))
        return cls(
            project=_project(document, source),
            form=form,
            resolution=resolution_recommendations(document),
            host=_optional_table(document, "host", source) or {},
            configuration=configuration,
            workflow=_optional_table(document, "workflow", source),
            workflow_type=workflow_type,
            retired={key: deepcopy(capabilities[key]) for key in (RETIRED_CAPABILITY_FIELD,) if key in capabilities},
            capability_extensions={key: deepcopy(value) for key, value in capabilities.items() if key not in _V1_CAPABILITIES},
            extensions={key: deepcopy(value) for key, value in document.items() if key not in _V1_ROOT},
        )

    def document(self) -> dict[str, Any]:
        """The schema-1 mapping this value stands for."""
        capabilities: dict[str, Any] = (
            {"need": list(self.form.need)} if isinstance(self.form, NeedForm) else {"required": list(self.form.required)}
        )
        if self.form.optional:
            capabilities["optional"] = list(self.form.optional)
        if self.resolution:
            capabilities["resolution"] = dict(self.resolution)
        capabilities.update(deepcopy(self.capability_extensions))
        capabilities.update(deepcopy(self.retired))
        result: dict[str, Any] = {VERSION_KEY: self.version}
        if self.workflow_type is not None:
            result["workflow-type"] = self.workflow_type
        result["project"] = deepcopy(self.project)
        result["capabilities"] = capabilities
        if self.host:
            result["host"] = deepcopy(self.host)
        if self.configuration:
            result["configuration"] = deepcopy(self.configuration)
        result.update(deepcopy(self.extensions))
        if self.workflow is not None:
            result["workflow"] = deepcopy(self.workflow)
        return result


@dataclass(frozen=True)
class ManifestV2:
    """A manifest as the one writer writes it since 0.3.0 rc4.

    ``required`` and ``optional`` are the requirement strings as written
    (``NAME`` or ``NAME>=VERSION``), in the owner's order; :attr:`policy`
    is their value.  ``reasons`` is ``[capabilities.reasons]``, ``resolution``
    the owner's provider choices.  ``environment`` is the ``[environment]``
    table as written, since an entry may carry a newer owner's field beside
    its reason; :attr:`environment_policy` is its value.  ``retired``,
    ``capability_extensions`` and ``extensions`` are as on :class:`ManifestV1`.
    """

    version: ClassVar[int] = 2

    project: dict[str, Any]
    required: tuple[str, ...] = ()
    optional: tuple[str, ...] = ()
    reasons: dict[str, str] = field(default_factory=dict)
    resolution: dict[str, str] = field(default_factory=dict)
    environment: dict[str, Any] = field(default_factory=dict)
    recommendations: Recommendations = field(default_factory=Recommendations)
    host: dict[str, Any] = field(default_factory=dict)
    configuration: dict[str, Any] = field(default_factory=dict)
    workflow: dict[str, Any] | None = None
    retired: dict[str, Any] = field(default_factory=dict)
    capability_extensions: dict[str, Any] = field(default_factory=dict)
    extensions: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def read(cls, document: Mapping[str, Any], source: object) -> ManifestV2:
        """Admit a decoded schema-2 file, refusing schema-1 words by name."""
        validate_file_format(document, ConfigurationFileKind.manifest, source)
        if document[VERSION_KEY] != cls.version:
            raise ProjectConfigurationError(f"{source} is not a schema-{cls.version} manifest; it says {document[VERSION_KEY]!r}.")
        capabilities = table(document, "capabilities")
        if "need" in capabilities:
            raise _refuse(source, "capabilities.need", belongs_to=1, says=2)
        required = _written_names(capabilities.get("required", []), "capabilities.required")
        optional = _written_names(capabilities.get("optional", []), "capabilities.optional")
        CapabilityPolicy.read(document)
        try:
            reasons = capability_reasons(document)
            EnvironmentPolicy.read(document)
            recommendations = Recommendations.read(document)
        except ProjectConfigurationError as exc:
            raise ProjectConfigurationError(f"{source}: {exc}") from exc
        configuration = _optional_table(document, "configuration", source) or {}
        configuration_value_declarations(document, source=str(source))
        return cls(
            project=_project(document, source),
            required=required,
            optional=optional,
            reasons=reasons,
            resolution=resolution_recommendations(document),
            environment=_optional_table(document, "environment", source) or {},
            recommendations=recommendations,
            host=_optional_table(document, "host", source) or {},
            configuration=configuration,
            workflow=_fold_workflow_type(_optional_table(document, "workflow", source), document.get("workflow-type"), source),
            retired={key: deepcopy(capabilities[key]) for key in (RETIRED_CAPABILITY_FIELD,) if key in capabilities},
            capability_extensions={key: deepcopy(value) for key, value in capabilities.items() if key not in _V2_CAPABILITIES},
            extensions={key: deepcopy(value) for key, value in document.items() if key not in _V2_ROOT | {"workflow-type"}},
        )

    @property
    def policy(self) -> CapabilityPolicy:
        return CapabilityPolicy.read({"capabilities": {"required": list(self.required), "optional": list(self.optional)}})

    @property
    def environment_policy(self) -> EnvironmentPolicy:
        return EnvironmentPolicy.read({"environment": self.environment})

    def document(self) -> dict[str, Any]:
        """The schema-2 mapping this value stands for: the input of the one writer and of every reader."""
        capabilities: dict[str, Any] = {"required": list(self.required)}
        if self.optional:
            capabilities["optional"] = list(self.optional)
        declared = {requirement(item)[0] for item in (*self.required, *self.optional)}
        reasons = {name: reason for name, reason in self.reasons.items() if reason and name in declared}
        if reasons:
            capabilities["reasons"] = reasons
        if self.resolution:
            capabilities["resolution"] = dict(self.resolution)
        capabilities.update(deepcopy(self.capability_extensions))
        capabilities.update(deepcopy(self.retired))
        result: dict[str, Any] = {VERSION_KEY: self.version, "project": deepcopy(self.project), "capabilities": capabilities}
        if self.environment:
            result["environment"] = deepcopy(self.environment)
        recommendations = self.recommendations.document()
        if recommendations:
            result["recommendations"] = recommendations
        if self.host:
            result["host"] = deepcopy(self.host)
        if self.configuration:
            result["configuration"] = deepcopy(self.configuration)
        result.update(deepcopy(self.extensions))
        if self.workflow is not None:
            result["workflow"] = deepcopy(self.workflow)
        return result


def read_manifest(document: Mapping[str, Any], source: object) -> ManifestV1 | ManifestV2:
    """Admit a decoded manifest as the class its ``devcapsule-schema-version`` names.

    ``source`` identifies the file in messages.  Any other version is refused
    with the message ``validate_file_format`` gives, naming the versions this
    launcher reads.
    """
    validate_file_format(document, ConfigurationFileKind.manifest, source)
    if document[VERSION_KEY] == ManifestV1.version:
        return ManifestV1.read(document, source)
    return ManifestV2.read(document, source)


def upgrade(manifest: ManifestV1, *, ide: Callable[[str], str | None]) -> ManifestV2:
    """A schema-1 manifest as schema 2, in memory, by these laws.

    1. ``need`` becomes ``required``; ``required``, ``optional`` and the
       minimums are kept, in the file's order.
    2. Every IDE capability leaves the lists.  A required one becomes the IDE
       recommendation; two different required IDEs are refused, since the
       owner must choose; an optional one is dropped, since every developer
       chooses their own IDE.  ``ide`` answers which capability a name stands
       for as an IDE, or ``None``: the catalog's question, asked here alone.
    3. The retired ``sdk-major`` table is carried for the reader's note and
       dropped by the writer, never written again.
    4. ``workflow-type`` folds into ``[workflow].mode``: taken when ``mode``
       is absent, dropped when equal, refused when they disagree.
    5. The project, ``host``, ``configuration``, the provider choices,
       ``[workflow]`` and the extensions are carried verbatim.

    Nothing is written here.  Reading the rendered result gives an equal
    value, the retired table apart.
    """
    form = manifest.form
    written = form.need if isinstance(form, NeedForm) else form.required
    required_ides = {item: ide(requirement(item)[0]) for item in written}
    chosen = {capability for capability in required_ides.values() if capability is not None}
    if len(chosen) > 1:
        listed = ", ".join(item for item, capability in required_ides.items() if capability is not None)
        raise ProjectConfigurationError(
            f"The schema-1 manifest requires two IDEs, {listed}; a project recommends one IDE and each developer chooses. "
            "Keep one with 'devcapsule project config drop NAME' and regenerate again."
        )
    required = tuple(item for item, capability in required_ides.items() if capability is None)
    optional = tuple(item for item in form.optional if ide(requirement(item)[0]) is None)
    workflow = _fold_workflow_type(deepcopy(manifest.workflow), manifest.workflow_type, "the schema-1 manifest")
    return ManifestV2(
        project=deepcopy(manifest.project),
        required=required,
        optional=optional,
        resolution=dict(manifest.resolution),
        recommendations=Recommendations(ide=next(iter(chosen), None)),
        host=deepcopy(manifest.host),
        configuration=deepcopy(manifest.configuration),
        workflow=workflow,
        retired=deepcopy(manifest.retired),
        capability_extensions=deepcopy(manifest.capability_extensions),
        extensions=deepcopy(manifest.extensions),
    )
