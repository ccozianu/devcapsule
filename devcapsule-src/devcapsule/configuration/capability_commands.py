"""Capability command adapters: validate first, then promote owned documents.

Project replacement has one commit point (the manifest) and an undo/redo
journal. Local replacement changes one checkout file atomically. Neither path
answers host-access or acquisition questions on the developer's behalf.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import tomllib
from typing import Any, Mapping, Sequence

from devcapsule.platforms import Platform
from devcapsule.resolution_matrix import MATRICES, ResolutionMatrix
from .capabilities import CapabilityPolicy, LocalCapabilities
from .capability_selection import compose_lock, effective_lock, generate_lock, local_pins, usable_lock
from .file_formats import ConfigurationFileKind, ProjectConfigurationError, table, validate_file_format, render_checkout, render_toml, selected_version_lock
from .manifest import validate_manifest
from .nodes import build_node_registry
from .storage import atomic_write, checkout_record_paths, discover_project, load_toml, require_settled


def paths(root: Path) -> tuple[Path, Path, Path]:
    """Return manifest, current-platform lock and recovery-journal paths.

    ``root`` is the project directory. This only constructs paths.
    """
    directory = root / ".devcapsule"
    return (directory / "devcapsule.toml", directory / f"devcapsule.{Platform.current()}.lock",
            directory / ".capability-transaction.toml")


def recover(root: Path) -> None:
    """Finish an interrupted shared edit, or do nothing if no journal exists.

    The manifest chooses the before/after lock to restore. Refuse malformed
    journals or independent edits with ProjectConfigurationError. Successful
    recovery removes the journal. Use the same platform that began the edit;
    callers must exclude concurrent writers. Filesystem errors propagate.
    """
    manifest_path, lock_path, journal = paths(root)
    if not journal.exists():
        return
    transaction = load_toml(journal)
    if set(transaction) != {"before-manifest", "after-manifest", "before-lock", "after-lock"} or any(
        not isinstance(value, str) for value in transaction.values()
    ):
        raise ProjectConfigurationError("Malformed capability transaction; preserve it for recovery.")
    current = manifest_path.read_text() if manifest_path.exists() else ""
    current_lock = lock_path.read_text() if lock_path.exists() else ""
    if current_lock not in {transaction["before-lock"], transaction["after-lock"]}:
        raise ProjectConfigurationError("Lock changed outside the pending transaction; refusing to overwrite it.")
    if current == transaction["after-manifest"]:
        chosen = "after-lock"
    elif current == transaction["before-manifest"]:
        chosen = "before-lock"
    else:
        raise ProjectConfigurationError("Configuration changed outside the pending transaction; refusing to overwrite it.")
    if transaction[chosen]:
        atomic_write(lock_path, transaction[chosen], mode=0o644)
    else:
        lock_path.unlink(missing_ok=True)
    journal.unlink()


def promote(root: Path, manifest: dict[str, Any], lock: dict[str, Any]) -> None:
    """Persist an already-validated manifest/lock pair with a recovery journal.

    Call ``check_documents`` first and exclude concurrent writers. Write the
    lock before the manifest; attempt recovery on OSError. Failures propagate.
    A pending journal raises ProjectConfigurationError. This updates shared
    files only; it neither writes nor resolves a developer's checkout.
    """
    manifest_path, lock_path, journal = paths(root)
    require_settled(root)
    transaction = {"before-manifest": manifest_path.read_text() if manifest_path.exists() else "",
                   "before-lock": lock_path.read_text() if lock_path.exists() else "",
                   "after-manifest": render_toml(manifest), "after-lock": render_toml(lock)}
    atomic_write(journal, render_toml(transaction))
    try:
        atomic_write(lock_path, transaction["after-lock"], mode=0o644)
        atomic_write(manifest_path, transaction["after-manifest"], mode=0o644)
    except OSError:
        recover(root)
        raise
    journal.unlink()


def check_documents(manifest: dict[str, Any], lock: dict[str, Any]) -> tuple[str, ...]:
    """Validate shared documents offline and return optional-omission warnings.

    Check schemas, required capabilities, SDK majors and usable artifact
    metadata. Invalid configuration raises CliError or its configuration
    subclass. This does not change inputs or files, download artifacts, or
    grant host access.
    """
    validate_manifest(manifest, Path("manifest"))
    validate_file_format(lock, ConfigurationFileKind.lock, "platform lock")
    usable, notices = usable_lock(CapabilityPolicy.read(manifest), lock)
    check_formation(manifest, usable)
    return notices


def check_formation(manifest: dict[str, Any], usable: dict[str, Any]) -> None:
    """Check artifact metadata and declarations in an already-selected lock.

    ``usable`` must contain only supported components, as returned by
    ``usable_lock``. Raise CliError for invalid metadata or declarations.
    No artifacts are downloaded and no launch permissions are granted.
    """
    from devcapsule.components.catalog import COMPONENTS
    from devcapsule.materialization import parse_locked_environment, validate_locked_artifact
    from .authorization import locked_base_reference, authorization_declarations
    if "base" in usable:
        locked_base_reference(usable)
        if usable.get("components", {}).get("interactive-surface"):
            parse_locked_environment(usable)
        else:
            for name, metadata in usable.get("components", {}).items():
                for artifact in COMPONENTS[name].locked_artifacts(metadata, str(usable["platform"])):
                    validate_locked_artifact(artifact)
    authorization_declarations(manifest, usable)
    if usable.get("components", {}).get("interactive-surface"):
        build_node_registry(manifest, usable)


def check(start: Path, *, manifest_path: Path | None = None, lock_path: Path | None = None) -> str:
    """Return an offline validation report for the project containing ``start``.

    Candidate paths override the shared manifest/current-platform lock paths.
    A pending edit must be recovered first. Invalid documents raise CliError;
    filesystem errors propagate. This reads only: it does not register a
    checkout, recover an edit, download artifacts or test launch permissions.
    """
    root = discover_project(start)
    default_manifest, default_lock, _ = paths(root)
    require_settled(root)
    manifest = load_toml(manifest_path or default_manifest)
    lock = load_toml(lock_path or default_lock)
    notices = check_documents(manifest, lock)
    return "\n".join(("Configuration contract valid (offline; launch permissions and downloads are not tested).",
                      *(f"Warning: {notice}" for notice in notices)))


def configure(start: Path, *, required: Sequence[str] | None = None,
              optional: Sequence[str] | None = None, majors: Sequence[str] | None = None,
              local: Sequence[str] | None = None, without: Sequence[str] | None = None,
              preview: bool = False, allow_unverified: bool = False) -> str:
    """Replace project capability declarations or this checkout's local choices.

    ``start`` locates the project. Supply one group: shared ``required``,
    ``optional``, ``majors``; or local ``local``, ``without``. Name sequences
    replace the corresponding lists; ``majors`` uses entries like ``python=3``.
    None retains a field; an empty sequence clears it. IDE/agent additions
    belong in ``local``. Host decisions are retained and never answered here.

    Validate before writing and return a human-readable result. ``preview``
    performs the same validation without writes. ``allow_unverified`` permits
    catalog combinations lacking compatibility evidence. Invalid edits raise
    CliError; I/O errors propagate. A successful edit still needs an explicit
    configuration resolution before launch when local inputs have changed.
    """
    root = discover_project(start)
    require_settled(root)
    manifest_path, lock_path, _ = paths(root)
    manifest, lock = load_toml(manifest_path), load_toml(lock_path)
    check_documents(manifest, lock)
    project_edit = any(value is not None for value in (required, optional, majors))
    local_edit = local is not None or without is not None
    if project_edit == local_edit:
        raise ProjectConfigurationError("Choose either project flags (--required/--optional/--sdk-major) or local flags (--local/--without).")
    matrix = MATRICES[Platform.current()]
    if project_edit:
        return configure_project(root, manifest, lock, matrix, required=required, optional=optional, majors=majors,
                                 preview=preview, allow_unverified=allow_unverified)
    return configure_local(root, manifest, lock, matrix, local=local, without=without,
                           preview=preview, allow_unverified=allow_unverified)


def configure_project(root: Path, manifest: dict[str, Any], lock: dict[str, Any], matrix: ResolutionMatrix, *,
                      required: Sequence[str] | None, optional: Sequence[str] | None, majors: Sequence[str] | None,
                      preview: bool, allow_unverified: bool) -> str:
    """Replace the shared policy and regenerate the platform lock; see ``configure``.

    ``manifest`` and ``lock`` are the validated current shared documents and
    are not changed; ``manifest`` is used as the candidate's template.
    """
    policy = CapabilityPolicy.read(manifest)
    candidate_manifest = deepcopy(manifest)
    declarations = candidate_manifest["capabilities"]
    declarations.pop("need", None)
    declarations["required"] = list(policy.required if required is None else required)
    declarations["optional"] = list(policy.optional if optional is None else optional)
    if majors is not None:
        declarations["sdk-major"] = parse_majors(majors)
    candidate = CapabilityPolicy.read(candidate_manifest)
    personal = (set(candidate.required) | set(candidate.optional)) & matrix.local_capabilities()
    # Existing shared IDE/agent declarations are grandfathered on unrelated
    # edits. A project can remove them, but new choices belong to developers.
    introduced = personal - set(policy.required) - set(policy.optional)
    if introduced:
        raise ProjectConfigurationError("IDE/agent choices are local; use --local for " + ", ".join(sorted(introduced)) + ".")
    generated = generate_lock(candidate, matrix, previous=lock, allow_unverified=allow_unverified)
    check_documents(candidate_manifest, generated)
    if not preview:
        promote(root, candidate_manifest, generated)
    return ("Preview; no files changed.\n" if preview else "Updated shared capability policy and lock.\n") + render_toml(declarations)


def configure_local(root: Path, manifest: dict[str, Any], shared: dict[str, Any], matrix: ResolutionMatrix, *,
                    local: Sequence[str] | None, without: Sequence[str] | None,
                    preview: bool, allow_unverified: bool) -> str:
    """Replace this checkout's selections and omissions; see ``configure``.

    Only the checkout record changes. Its persistent selection (an explicit
    version set when present) keeps every pin that an omission merely hides;
    omissions take effect when the selection is projected for execution.
    Provider pins for the new selection come from ``pin_selection``, and an
    explicit version set drops only providers that no capability needs anymore.
    """
    policy = CapabilityPolicy.read(manifest)
    input_path, _ = checkout_record_paths(manifest, root)
    if input_path.with_suffix(".activation.toml").exists():
        raise ProjectConfigurationError("A local version-set activation needs recovery; run 'project config resolve' first.")
    if input_path.exists():
        checkout = load_toml(input_path)
    else:
        checkout = tomllib.loads(render_checkout(manifest, root, {}, {}))
    validate_file_format(checkout, ConfigurationFileKind.checkout, input_path)
    previous = LocalCapabilities.read(checkout)
    selection = LocalCapabilities.read({"capabilities": {
        "selected": list(previous.selected if local is None else local),
        "without": list(previous.without if without is None else without)}})
    selection.validate(policy)
    matrix.normalize(list(selection.selected))
    previous_pins = local_pins(checkout)
    version_lock = selected_version_lock(checkout)
    version_record = checkout.pop("version-set", None)
    source = deepcopy(version_lock if version_lock is not None else shared)
    if version_lock is not None:
        release_deselected(source, matrix, policy, previous, selection)
    pins = pin_selection(matrix, policy, selection, source, previous, previous_pins, allow_unverified=allow_unverified)
    checkout["capabilities"] = {"selected": list(selection.selected), "without": list(selection.without), "lock": render_toml(pins)}
    composed = compose_lock(manifest, source, checkout)
    if version_record is not None:
        version_record["lock"] = render_toml(composed)
        checkout["version-set"] = version_record
    check_formation(manifest, effective_lock(manifest, composed, checkout, warn=False))
    if not preview:
        atomic_write(input_path, render_toml(checkout))
    return ("Preview; no files changed." if preview else
            "Updated local capability selection; shared files unchanged. Run 'project config resolve' to review permissions and prepare launch.")


def pin_selection(matrix: ResolutionMatrix, policy: CapabilityPolicy, selection: LocalCapabilities,
                  source: Mapping[str, Any], previous: LocalCapabilities, previous_pins: Mapping[str, Any], *,
                  allow_unverified: bool) -> dict[str, Any]:
    """Return the pins document for ``selection``: a lock holding exactly its providers.

    Each provider's metadata comes from the first document that has it: the
    ``source`` selection the pins will be laid over, then ``previous_pins``
    for a capability that ``previous`` already selected, then a fresh catalog
    resolution of the project's required and the selected capabilities. The IDE
    selector and materialization follow the IDE component's document. Catalog
    resolution failures raise ProjectConfigurationError. Inputs are unchanged.
    """
    active = sorted(set(policy.required) | set(selection.selected))
    fresh = tomllib.loads(matrix.resolve(active, project_only=True, allow_unverified=allow_unverified).render_lock())
    pins = {key: deepcopy(value) for key, value in fresh.items() if key != "components"}
    pins["components"] = {}
    pins["materialization"] = {}
    surface = fresh["components"].get("interactive-surface")
    retained = set(previous.selected) & set(selection.selected)
    for capability in selection.selected:
        for component in matrix.providers(capability):
            documents = (source, *((previous_pins,) if capability in retained else ()), fresh)
            document = next((item for item in documents if table(item, "components").get(component) is not None), None)
            if document is None:
                raise ProjectConfigurationError(f"The catalog resolved {capability!r} without pinning its provider {component!r}.")
            pins["components"][component] = deepcopy(table(document, "components")[component])
            if component == surface:
                pins["components"]["interactive-surface"] = surface
                pins["materialization"] = deepcopy(table(document, "materialization"))
    return pins


def release_deselected(source: dict[str, Any], matrix: ResolutionMatrix, policy: CapabilityPolicy,
                       previous: LocalCapabilities, selection: LocalCapabilities) -> None:
    """Remove providers of deselected capabilities from ``source`` in place.

    A provider stays when a required, known optional or still-selected
    capability needs it. Removing the IDE also clears the IDE selector and
    materialization. Capabilities this launcher does not know are left alone.
    """
    known = set(matrix.capabilities())
    needed = {component for capability in (*policy.required, *policy.optional, *selection.selected)
              if capability in known for component in matrix.providers(capability)}
    table(source, "components")
    components: dict[str, Any] = source.setdefault("components", {})
    for capability in set(previous.selected) - set(selection.selected):
        if capability not in known:
            continue
        for component in matrix.providers(capability):
            if component in needed:
                continue
            components.pop(component, None)
            if components.get("interactive-surface") == component:
                del components["interactive-surface"]
                source["materialization"] = {}


def initialize(root: Path, *, name: str | None, slug: str | None, creator: str | None,
               mount: str | None, required: Sequence[str], optional: Sequence[str],
               majors: Sequence[str], local: Sequence[str], allow_unverified: bool = False) -> str:
    """Create project policy, a platform lock and a local checkout record.

    ``root`` must exist without shared config; ``creator`` is required.
    Name/slug default from the directory, and mount to ``/workspace/<slug>``.
    Capability arguments have the meanings in ``configure``; an empty ``local``
    selects no IDE or agent. Validate all candidates before writing; invalid
    input raises CliError. Shared promotion and the later local write are
    separate operations, so an I/O failure can leave local setup incomplete.
    Return setup instructions; permissions and launch resolution remain undone.
    """
    from devcapsule.project import sanitize_name
    root = root.expanduser().resolve()
    if not root.is_dir():
        raise ProjectConfigurationError(f"Project directory does not exist: {root}")
    manifest_path, lock_path, _ = paths(root)
    require_settled(root)
    if manifest_path.exists() or lock_path.exists():
        raise ProjectConfigurationError("Project configuration already exists; use 'project config capabilities'.")
    if not creator:
        raise ProjectConfigurationError("Supply --creator URL_OR_EMAIL for the shared project identity.")
    identity_slug = slug or sanitize_name(root.name).lower()
    parsed = parse_majors(majors)
    manifest = {"devcapsule-schema-version": 1,
                "project": {"name": name or root.name, "slug": identity_slug, "creator": creator,
                            "mount": mount or f"/workspace/{identity_slug}"},
                "capabilities": {"required": list(required), "optional": list(optional), "sdk-major": parsed}}
    validate_manifest(manifest, manifest_path)
    policy = CapabilityPolicy.read(manifest)
    matrix = MATRICES[Platform.current()]
    personal = (set(required) | set(optional)) & matrix.local_capabilities()
    if personal:
        raise ProjectConfigurationError("IDE/agent choices belong in --local: " + ", ".join(sorted(personal)) + ".")
    lock = generate_lock(policy, matrix, allow_unverified=allow_unverified)
    check_documents(manifest, lock)
    input_path, _ = checkout_record_paths(manifest, root)
    checkout = tomllib.loads(render_checkout(manifest, root, {}, {}))
    if local:
        selection = LocalCapabilities.read({"capabilities": {"selected": list(local)}})
        matrix.normalize(list(selection.selected))
        pins = pin_selection(matrix, policy, selection, lock, LocalCapabilities(), {}, allow_unverified=allow_unverified)
        checkout["capabilities"] = {"selected": list(selection.selected), "without": [], "lock": render_toml(pins)}
        check_formation(manifest, effective_lock(manifest, compose_lock(manifest, lock, checkout), checkout, warn=False))
    rendered_checkout = render_toml(checkout)
    promote(root, manifest, lock)
    atomic_write(input_path, rendered_checkout)
    return ("Created project capability policy, platform lock and local checkout.\n"
            "Choose an IDE with 'project config capabilities --local CAPABILITY' if needed; "
            "then run 'project config resolve' and answer the reported authorization questions.")


def parse_majors(majors: Sequence[str]) -> dict[str, int]:
    """Parse CLI entries such as ``python=3`` into capability-to-major pairs.

    Raise ProjectConfigurationError for duplicate names or invalid syntax.
    CapabilityPolicy.read subsequently checks positivity and required membership.
    """
    result: dict[str, int] = {}
    for item in majors:
        name, separator, value = item.partition("=")
        if not separator or not value.isdecimal() or name in result:
            raise ProjectConfigurationError("SDK majors use unique CAPABILITY=INTEGER entries, for example python=3.")
        result[name] = int(value)
    return result
