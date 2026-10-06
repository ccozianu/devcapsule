"""Capability command adapters: validate first, then promote owned documents.

Project replacement has one commit point (the manifest) and an undo/redo
journal. Local replacement changes one checkout file atomically. Neither path
answers host-access or acquisition questions on the developer's behalf.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Sequence

from devcapsule.platforms import Platform
from devcapsule.resolution_matrix import MATRICES
from .capabilities import CapabilityPolicy, LocalCapabilities
from .capability_selection import generate_lock, selected_lock, usable_lock
from .documents import Artifact, ProjectConfigurationError, admit_document, render_checkout, render_document, selected_version_lock
from .manifest import validate_manifest
from .nodes import build_node_registry
from .storage import atomic_write, checkout_record_paths, discover_project, load_toml, require_settled


def paths(root: Path) -> tuple[Path, Path, Path]:
    directory = root / ".devcapsule"
    return (directory / "devcapsule.toml", directory / f"devcapsule.{Platform.current()}.lock",
            directory / ".capability-transaction.toml")


def recover(root: Path) -> None:
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
    manifest_path, lock_path, journal = paths(root)
    require_settled(root)
    transaction = {"before-manifest": manifest_path.read_text() if manifest_path.exists() else "",
                   "before-lock": lock_path.read_text() if lock_path.exists() else "",
                   "after-manifest": render_document(manifest), "after-lock": render_document(lock)}
    atomic_write(journal, render_document(transaction))
    try:
        atomic_write(lock_path, transaction["after-lock"], mode=0o644)
        atomic_write(manifest_path, transaction["after-manifest"], mode=0o644)
    except OSError:
        recover(root)
        raise
    journal.unlink()


def check_documents(manifest: dict[str, Any], lock: dict[str, Any]) -> tuple[str, ...]:
    validate_manifest(manifest, Path("manifest"))
    admit_document(lock, Artifact.lock, "platform lock")
    usable, notices = usable_lock(CapabilityPolicy.read(manifest), lock)
    check_formation(manifest, usable)
    return notices


def check_formation(manifest: dict[str, Any], usable: dict[str, Any]) -> None:
    """Validate executable metadata and declarations, without acquiring anything."""
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
    """Read only: no checkout registration, resolution, recovery, Docker or network."""
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
    root = discover_project(start)
    require_settled(root)
    manifest_path, lock_path, _ = paths(root)
    manifest, lock = load_toml(manifest_path), load_toml(lock_path)
    check_documents(manifest, lock)
    policy = CapabilityPolicy.read(manifest)
    project_edit = any(value is not None for value in (required, optional, majors))
    local_edit = local is not None or without is not None
    if project_edit == local_edit:
        raise ProjectConfigurationError("Choose either project flags (--required/--optional/--sdk-major) or local flags (--local/--without).")
    matrix = MATRICES[Platform.current()]
    if project_edit:
        declarations = deepcopy(manifest["capabilities"])
        declarations.pop("need", None)
        declarations["required"] = list(policy.required if required is None else required)
        declarations["optional"] = list(policy.optional if optional is None else optional)
        if majors is not None:
            declarations["sdk-major"] = parse_majors(majors)
        manifest["capabilities"] = declarations
        candidate = CapabilityPolicy.read(manifest)
        personal = (set(candidate.required) | set(candidate.optional)) & matrix.local_capabilities()
        # Existing shared IDE/agent declarations are grandfathered on unrelated
        # edits. A project can remove them, but new choices belong to developers.
        introduced = personal - set(policy.required) - set(policy.optional)
        if introduced:
            raise ProjectConfigurationError("IDE/agent choices are local; use --local for " + ", ".join(sorted(introduced)) + ".")
        generated = generate_lock(candidate, matrix, previous=lock, allow_unverified=allow_unverified)
        check_documents(manifest, generated)
        if not preview:
            promote(root, manifest, generated)
        return ("Preview; no files changed.\n" if preview else "Updated shared capability policy and lock.\n") + render_document(manifest["capabilities"])

    input_path, _ = checkout_record_paths(manifest, root)
    if input_path.with_suffix(".activation.toml").exists():
        raise ProjectConfigurationError("A local version-set activation needs recovery; run 'project config resolve' first.")
    if input_path.exists():
        checkout = load_toml(input_path)
    else:
        import tomllib
        checkout = tomllib.loads(render_checkout(manifest, root, {}, {}))
    admit_document(checkout, Artifact.checkout, input_path)
    previous = LocalCapabilities.read(checkout)
    selection = LocalCapabilities(tuple(sorted(set(previous.selected if local is None else local))),
                                  tuple(sorted(set(previous.without if without is None else without))))
    selection.validate(policy)
    matrix.normalize(list(selection.selected))
    active = tuple(sorted(set(policy.required) | set(selection.selected)))
    # Pin local tools independently; shared optional tools continue to follow
    # the project's lock. The shared base remains authoritative.
    pins = matrix.resolve(active, project_only=True, allow_unverified=allow_unverified)
    import tomllib
    pinned = tomllib.loads(pins.render_lock())
    version_lock = selected_version_lock(checkout)
    old_pins = version_lock or tomllib.loads(checkout.get("capabilities", {}).get("lock", ""))
    retained = set(previous.selected) & set(selection.selected)
    for capability in retained:
        for component in matrix.providers(capability):
            metadata = old_pins.get("components", {}).get(component)
            if metadata is not None:
                pinned["components"][component] = deepcopy(metadata)
    checkout["capabilities"] = {"selected": list(selection.selected), "without": list(selection.without), "lock": render_document(pinned)}
    # A personal capability change preserves unrelated local version pins.
    version_record = checkout.pop("version-set", None)
    source = deepcopy(version_lock if version_lock is not None else lock)
    if version_lock is not None:
        old_surface = source["components"].get("interactive-surface")
        required_providers = {item for capability in policy.required for item in matrix.providers(capability)}
        if old_surface and old_surface not in required_providers:
            source["components"].pop("interactive-surface", None)
            source["components"].pop(old_surface, None)
    effective = selected_lock(manifest, source, checkout, warn=False)
    if version_record is not None:
        version_record["lock"] = render_document(effective)
        checkout["version-set"] = version_record
    check_formation(manifest, effective)
    if not preview:
        atomic_write(input_path, render_document(checkout))
    return ("Preview; no files changed." if preview else
            "Updated local capability selection; shared files unchanged. Run 'project config resolve' to review permissions and prepare launch.")


def initialize(root: Path, *, name: str | None, slug: str | None, creator: str | None,
               mount: str | None, required: Sequence[str], optional: Sequence[str],
               majors: Sequence[str], local: Sequence[str], allow_unverified: bool = False) -> str:
    """Create shared policy and optionally local pins; no implicit personal tools."""
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
    import tomllib
    checkout = tomllib.loads(render_checkout(manifest, root, {}, {}))
    if local:
        pins = matrix.resolve(sorted(set(required) | set(local)), allow_unverified=allow_unverified)
        checkout["capabilities"] = {"selected": sorted(set(local)), "without": [], "lock": pins.render_lock()}
        check_formation(manifest, selected_lock(manifest, lock, checkout, warn=False))
    rendered_checkout = render_document(checkout)
    promote(root, manifest, lock)
    atomic_write(input_path, rendered_checkout)
    return ("Created project capability policy, platform lock and local checkout.\n"
            "Choose an IDE with 'project config capabilities --local CAPABILITY' if needed; "
            "then run 'project config resolve' and answer the reported authorization questions.")


def parse_majors(majors: Sequence[str]) -> dict[str, int]:
    result: dict[str, int] = {}
    for item in majors:
        name, separator, value = item.partition("=")
        if not separator or not value.isdecimal() or name in result:
            raise ProjectConfigurationError("SDK majors use unique CAPABILITY=INTEGER entries, for example python=3.")
        result[name] = int(value)
    return result
