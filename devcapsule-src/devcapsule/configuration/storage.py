"""Configuration file discovery, checkout ownership and atomic persistence."""

from __future__ import annotations
import re
import tempfile
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import quote
from devcapsule.platforms import Platform, UnsupportedPlatformError, XdgHomes

from .authorization import locked_base_reference
from .documents import Artifact, ProjectConfigurationError, admit_document, table, selected_version_lock, render_document
from .manifest import validate_manifest
from .nodes import build_node_registry


CHECKOUT_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


@dataclass(frozen=True)
class RegisteredCheckout:
    project_creator: str
    project_slug: str
    checkout_name: str
    checkout_path: Path
    record_path: Path
    status: str


@dataclass(frozen=True)
class ResolvedProject:
    root: Path
    manifest: dict[str, Any]
    lock_path: Path
    lock: dict[str, Any]
    checkout_path: Path
    checkout: dict[str, Any]
    resolution_path: Path
    resolution: dict[str, Any]


def discover_project(path: Path) -> Path:
    candidate = path.expanduser().resolve()
    if candidate.is_file():
        candidate = candidate.parent
    for directory in (candidate, *candidate.parents):
        if (directory / ".devcapsule" / "devcapsule.toml").is_file():
            return directory
    raise ProjectConfigurationError(
        f"No .devcapsule/devcapsule.toml found from {candidate}; run 'devcapsule project init'."
    )


def load_toml(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as stream:
            value = tomllib.load(stream)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise ProjectConfigurationError(f"Cannot read {path}: {exc}") from exc
    return value


def load_checkout(path: Path, manifest: Mapping[str, Any], root: Path) -> dict[str, Any]:
    recover_activation(path)
    document = load_toml(path)
    admit_document(document, Artifact.checkout, path)
    recorded = table(document, "checkout").get("path")
    if not isinstance(recorded, str) or not recorded or Path(recorded).expanduser().resolve() != root:
        raise ProjectConfigurationError(f"{path} does not match observed checkout {root}.")
    identity = table(document, "project")
    if any(identity.get(key) != manifest["project"][key] for key in ("creator", "slug")):
        raise ProjectConfigurationError(f"{path} does not match the project's creator and slug.")
    return document


def load_resolution(path: Path) -> dict[str, Any]:
    document = load_toml(path)
    admit_document(document, Artifact.resolution, path)
    return document


def config_root(env: Mapping[str, str] | None = None) -> Path:
    return XdgHomes.from_environment(env).config


def checkout_directory(manifest: Mapping[str, Any], env: Mapping[str, str] | None = None) -> Path:
    project = manifest["project"]
    creator = quote(str(project["creator"]), safe="")
    slug = quote(str(project["slug"]), safe="")
    return config_root(env) / "projects" / creator / slug


def checkout_record_paths(
    manifest: Mapping[str, Any],
    project_root: Path,
    env: Mapping[str, str] | None = None,
) -> tuple[Path, Path]:
    """Select the default or named checkout record matching one canonical path."""

    directory = checkout_directory(manifest, env)
    default_input = directory / "devcapsule.checkout.toml"
    matched = find_checkout_record(manifest, project_root, env)
    if matched is not None:
        return matched, resolved_record_path(matched)
    if not default_input.exists():
        return default_input, resolved_record_path(default_input)
    raise ProjectConfigurationError(
        f"Project identity is already registered for another checkout in {directory}; "
        "run 'devcapsule project --path PATH checkout register NAME'."
    )


def find_checkout_record(
    manifest: Mapping[str, Any],
    project_root: Path,
    env: Mapping[str, str] | None = None,
) -> Path | None:
    directory = checkout_directory(manifest, env)
    default_input = directory / "devcapsule.checkout.toml"
    candidates = (default_input, *sorted((directory / "checkouts").glob("*.checkout.toml")))
    expected = project_root.expanduser().resolve()
    for candidate in candidates:
        if not candidate.is_file():
            continue
        try:
            value = load_toml(candidate)
        except ProjectConfigurationError:
            continue
        metadata = value.get("checkout", {})
        if not isinstance(metadata, dict):
            raise ProjectConfigurationError(f"{candidate}: checkout must be a table.")
        recorded = metadata.get("path")
        if recorded and Path(str(recorded)).expanduser().resolve() == expected:
            return candidate
    return None


def named_checkout_record_paths(
    manifest: Mapping[str, Any],
    name: str,
    env: Mapping[str, str] | None = None,
) -> tuple[Path, Path]:
    if not CHECKOUT_NAME_PATTERN.fullmatch(name):
        raise ProjectConfigurationError(
            "Checkout name must start with an alphanumeric character and contain only letters, digits, '.', '_', or '-'."
        )
    input_path = checkout_directory(manifest, env) / "checkouts" / f"{name}.checkout.toml"
    return input_path, resolved_record_path(input_path)


def resolved_record_path(input_path: Path) -> Path:
    if input_path.name == "devcapsule.checkout.toml":
        return input_path.with_name("devcapsule.resolved.toml")
    if input_path.name.endswith(".checkout.toml"):
        return input_path.with_name(f"{input_path.name.removesuffix('.checkout.toml')}.resolved.toml")
    raise ValueError(f"not a DevCapsule checkout record path: {input_path}")


def registered_checkouts(env: Mapping[str, str] | None = None) -> tuple[RegisteredCheckout, ...]:
    """Enumerate valid developer-owned checkout records without scanning source trees."""

    projects_root = config_root(env) / "projects"
    records: list[RegisteredCheckout] = []
    if not projects_root.is_dir():
        return ()
    candidates = sorted(projects_root.rglob("*.checkout.toml"))
    for candidate in candidates:
        try:
            value = load_toml(candidate)
        except ProjectConfigurationError:
            continue
        if value.get("devcapsule-checkout-schema-version") != 1:
            continue
        project = value.get("project")
        checkout = value.get("checkout")
        if not isinstance(project, dict) or not isinstance(checkout, dict):
            continue
        creator = project.get("creator")
        slug = project.get("slug")
        raw_path = checkout.get("path")
        if not creator or not slug or not raw_path:
            continue
        source = Path(str(raw_path)).expanduser()
        name = "default" if candidate.name == "devcapsule.checkout.toml" else candidate.name.removesuffix(
            ".checkout.toml"
        )
        if not source.exists():
            status = "missing"
        elif not (source / ".devcapsule" / "devcapsule.toml").is_file():
            status = "uninitialized"
        else:
            status = "ready"
        records.append(
            RegisteredCheckout(
                project_creator=str(creator),
                project_slug=str(slug),
                checkout_name=name,
                checkout_path=source,
                record_path=candidate,
                status=status,
            )
        )
    return tuple(
        sorted(
            records,
            key=lambda record: (
                record.project_creator,
                record.project_slug,
                record.checkout_name,
                str(record.checkout_path),
            ),
        )
    )


def atomic_write(path: Path, content: str, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # The staging file is private from creation, not merely after the bytes
    # have been written. A failed write/replace keeps the previous checkpoint.
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                     prefix=f".{path.name}.", delete=False) as stream:
        temporary = Path(stream.name)
        try:
            stream.write(content)
            stream.flush()
            temporary.chmod(mode)
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)


def manifest_for(project: Path) -> tuple[Path, dict[str, Any]]:
    root = discover_project(project)
    path = root / ".devcapsule" / "devcapsule.toml"
    value = load_toml(path)
    validate_manifest(value, path)
    return root, value


def recommendation_lock_for(root: Path, manifest: Mapping[str, Any]) -> tuple[Path, dict[str, Any]]:
    """Load the committed platform lock for this host's platform.

    The lock is the project-side record of one resolution: the version set and
    property defaults selected for one platform. It is a record, not a
    permission gate: loading it must never refuse ordinary work because some
    other project input changed. Drift between the manifest and a checkout's
    generated resolution belongs to the resolution layer
    (``fresh_resolved_project``), whose source digests name exactly what
    drifted and whose remedy — ``devcapsule project config resolve`` — actually
    reconciles it. See "The Lock Is A Record, Not A Mandate" in
    ``engineering-docs/design-notes/devcapsule/v1-user-experience.md``.

    Committed locks may carry a ``manifest-digest`` of the whole manifest.
    This function once compared it and refused every dependent command after
    any manifest edit, fatally and with a remedy that could not help. The
    field is deliberately not read: a lock derives from the capability set and
    the platform, so no other manifest field may affect its validity (the
    scoped-digest principle), and R-COMPAT-001 forbids demanding user action
    to keep existing committed locks working.
    """

    try:
        current = Platform.current()
    except UnsupportedPlatformError as exc:
        raise ProjectConfigurationError(str(exc)) from exc
    path = root / ".devcapsule" / f"devcapsule.{current}.lock"
    if not path.is_file():
        raise ProjectConfigurationError(
            f"Missing {path}: this project carries no platform lock for {current}. "
            "The platform lock is authored on the project side and committed with the project."
        )
    value = load_toml(path)
    admit_document(value, Artifact.lock, path)
    if "base" in value:
        locked_base_reference(value, source=str(path))
    # Every public consumer gets the same unambiguous vocabulary.
    build_node_registry(manifest, value)
    return path, value


def lock_for(root: Path, manifest: Mapping[str, Any]) -> tuple[Path, dict[str, Any]]:
    """Effective software selection, independently of current host decisions."""
    record = find_checkout_record(manifest, root)
    if record is not None:
        checkout = load_checkout(record, manifest, root)
        selected = selected_version_lock(checkout)
        if selected is not None:
            if selected.get("platform") != str(Platform.current()):
                raise ProjectConfigurationError("Local version set is for another platform; follow the project explicitly.")
            locked_base_reference(selected)
            build_node_registry(manifest, selected)
            return root / ".devcapsule" / f"devcapsule.{Platform.current()}.lock", selected
    return recommendation_lock_for(root, manifest)


def recover_activation(input_path: Path) -> None:
    """Finish or undo an interrupted two-file activation under serialized access.

    Checkout replacement is the commit point. No old authorization snapshot is
    used after the transaction: a later edit that differs from both endpoints
    causes refusal, never resurrection of a historical permission.
    """
    journal = input_path.with_suffix(".activation.toml")
    if not journal.exists():
        return
    transaction = load_toml(journal)
    current = input_path.read_text()
    if current == transaction["after-checkout"]:
        resolution = transaction["after-resolution"]
    elif current == transaction["before-checkout"]:
        resolution = transaction["before-resolution"]
    else:
        raise ProjectConfigurationError(f"Interrupted activation conflicts with a later edit; inspect {journal}. No choices were replaced.")
    atomic_write(resolved_record_path(input_path), resolution)
    journal.unlink()


def activate_configuration(input_path: Path, checkout: Mapping[str, Any], resolution: Mapping[str, Any]) -> None:
    """Publish a prepared choice and its derived plan recoverably."""
    recover_activation(input_path)
    output = resolved_record_path(input_path)
    journal = input_path.with_suffix(".activation.toml")
    transaction = {
        "before-checkout": input_path.read_text(),
        "before-resolution": output.read_text() if output.exists() else "",
        "after-checkout": render_document(checkout),
        "after-resolution": render_document(resolution),
    }
    atomic_write(journal, render_document(transaction))
    try:
        atomic_write(output, transaction["after-resolution"])
        atomic_write(input_path, transaction["after-checkout"])
    except OSError:
        recover_activation(input_path)
        raise
    journal.unlink()
