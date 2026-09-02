"""Host-side acquisition and workstation-local component materialization."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import fcntl
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import tarfile
from typing import Any, Callable, Iterator, Mapping
from urllib.error import URLError
from urllib.request import urlopen

from devcapsule.compat import CliError
from devcapsule.platforms import XdgHomes
from devcapsule.components.catalog import (
    ComponentCatalogError,
    selected_component_definitions,
)
from devcapsule.components import LockedArtifactDeclaration
from devcapsule.components.catalog import INTERACTIVE_SURFACES
from devcapsule.image_build import (
    DirectoryComponent,
    EnvComponent,
    ExecComponent,
    FileComponent,
    ImageBuildSpec,
    LabelComponent,
    normalize_archive_directory,
)
from devcapsule.image_metadata import (
    BASE_KIND,
    CANONICAL_NAME_LABEL,
    IMAGE_KIND_LABEL,
    MANAGED_LABEL,
    MATERIALIZED_KIND,
    METADATA_VERSION,
    METADATA_VERSION_LABEL,
    managed_labels,
)


@dataclass(frozen=True)
class ArtifactSpec:
    version: str
    url: str
    sha256: str
    # Surfaces without a lock-recorded variant (VSCodium) carry None; the
    # ancillary-acquisition path reuses this field as a cache discriminator.
    variant: str | None = "professional"


@dataclass(frozen=True)
class Acquisition:
    path: Path
    downloaded: bool


@dataclass(frozen=True)
class ImageDetails:
    reference: str
    identity: str
    labels: Mapping[str, str]
    operating_system: str
    architecture: str


@dataclass(frozen=True)
class LockedEnvironment:
    platform: str
    base_reference: str
    base_identity: str | None
    component_id: str
    artifact: ArtifactSpec
    ancillary_artifacts: tuple[LockedArtifactDeclaration, ...]
    recipe_id: str
    recipe_version: str


FORMATION_SCHEMA_NAME = "devcapsule-formation"
FORMATION_SCHEMA_VERSION = 1
MATERIALIZATION_RECIPE_ID = "jetbrains-local-materialization"
MATERIALIZATION_RECIPE_VERSION = "1"


@dataclass(frozen=True)
class SurfaceMaterialization:
    """One interactive surface's archive-to-image materialization contract."""

    component_id: str
    family: str
    recipe_id: str
    installation_path: str
    # Relative paths that must exist in the unpacked archive before it is
    # trusted as this surface's installation.
    archive_probes: tuple[str, ...]
    # PyCharm locks record an edition variant; other surfaces do not.
    requires_variant: bool
    # Root-run build steps after the installation directory is copied in.
    post_install: tuple[ExecComponent, ...]


SURFACE_MATERIALIZATIONS: dict[str, SurfaceMaterialization] = {
    "pycharm": SurfaceMaterialization(
        component_id="pycharm",
        family="jetbrains",
        recipe_id=MATERIALIZATION_RECIPE_ID,
        installation_path="/opt/jetbrains/pycharm",
        archive_probes=("bin/pycharm.sh",),
        requires_variant=True,
        post_install=(),
    ),
    "codium": SurfaceMaterialization(
        component_id="codium",
        family="vscode",
        recipe_id="vscode-local-materialization",
        installation_path="/opt/codium",
        archive_probes=("codium", "bin/codium", "chrome-sandbox"),
        requires_variant=False,
        # Electron's setuid sandbox helper must be root-owned mode 4755 to
        # sandbox renderers without --no-sandbox; the trade-off is analyzed in
        # engineering-docs/design-notes/devcapsule/vscode-sandbox-setuid.md.
        post_install=(
            ExecComponent(
                (
                    "bash",
                    "-euo",
                    "pipefail",
                    "-c",
                    "chown root:root /opt/codium/chrome-sandbox"
                    " && chmod 4755 /opt/codium/chrome-sandbox",
                )
            ),
        ),
    ),
}
COMPONENT_TEMPLATE_PATH = "/etc/devcapsule/component-runtime-template.json"
RUNTIME_PLAN_PATH = "/etc/devcapsule/runtime-plan.json"
ENTRYPOINT_CONTRACT = (
    "/opt/devcapsule/bin/devcapsule.pex",
    "runtime",
)


def cache_root(env: Mapping[str, str] | None = None) -> Path:
    return XdgHomes.from_environment(env).cache


def acquire_artifact(spec: ArtifactSpec, root: Path) -> Acquisition:
    expected = _validated_sha256(spec.sha256, "Artifact SHA-256")
    destination = root / "artifacts" / "sha256" / expected
    lock = root / "locks" / "artifacts" / f"{expected}.lock"
    with _exclusive_lock(lock):
        if destination.is_file():
            if sha256_file(destination) == expected:
                return Acquisition(destination, False)
            destination.unlink()

        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary_path: Path | None = None
        digest = hashlib.sha256()
        try:
            with tempfile.NamedTemporaryFile(
                prefix=f".{destination.name}.", suffix=".download", dir=destination.parent, delete=False
            ) as output:
                temporary_path = Path(output.name)
                with urlopen(spec.url) as response:  # noqa: S310 - project-lock-pinned URL
                    while chunk := response.read(1024 * 1024):
                        digest.update(chunk)
                        output.write(chunk)
            actual = digest.hexdigest()
            if actual != expected:
                raise CliError(f"Artifact digest mismatch: expected {expected}, received {actual}.")
            temporary_path.replace(destination)
        except URLError as exc:
            raise CliError(f"Cannot download locked artifact {spec.url!r}: {exc}") from exc
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
        return Acquisition(destination, True)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(value: Mapping[str, Any]) -> str:
    """Serialize the JSON-native formation schema canonically for V1."""

    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def surface_profile(component_id: str) -> SurfaceMaterialization:
    profile = SURFACE_MATERIALIZATIONS.get(component_id)
    if profile is None:
        supported = ", ".join(sorted(SURFACE_MATERIALIZATIONS))
        raise CliError(
            f"V1 environment materialization supports no interactive surface "
            f"{component_id!r}; supported surfaces: {supported}."
        )
    return profile


def component_runtime_template(component_id: str = "pycharm") -> dict[str, Any]:
    """Return formation-owned component data without checkout/runtime choices."""

    definition = INTERACTIVE_SURFACES.get(component_id)
    if definition is None:
        raise CliError(f"No interactive surface component {component_id!r} is in the catalog.")
    return definition.runtime_template().to_mapping()


def formation_descriptor(
    *,
    platform: str,
    base_identity: str,
    artifact: ArtifactSpec,
    ancillary_artifacts: tuple[LockedArtifactDeclaration, ...] = (),
    recipe_id: str = MATERIALIZATION_RECIPE_ID,
    recipe_version: str = MATERIALIZATION_RECIPE_VERSION,
    component_id: str = "pycharm",
) -> dict[str, Any]:
    operating_system, architecture = _split_platform(platform)
    profile = surface_profile(component_id)
    template_digest = hashlib.sha256(
        canonical_json(component_runtime_template(component_id)).encode()
    ).hexdigest()
    return {
        "schema": {"name": FORMATION_SCHEMA_NAME, "version": FORMATION_SCHEMA_VERSION},
        "platform": {"os": operating_system, "architecture": architecture},
        "base": {"identity": base_identity},
        "components": [
            {
                "id": component_id,
                "version": artifact.version,
                "artifact": {"sha256": _validated_sha256(artifact.sha256, "Artifact SHA-256")},
                # Only variant-carrying surfaces record one, keeping earlier
                # PyCharm formation identities byte-stable.
                **({"variant": artifact.variant} if artifact.variant is not None else {}),
            },
            *[
                {
                    "id": item.component_id,
                    "version": item.version,
                    "artifact": {
                        "sha256": _validated_sha256(
                            item.sha256, f"{item.component_id} artifact SHA-256"
                        )
                    },
                    "installation": {
                        "format": item.artifact_format,
                        "destination": item.destination,
                        **(
                            {"archive-member": item.archive_member}
                            if item.archive_member is not None
                            else {}
                        ),
                    },
                }
                for item in ancillary_artifacts
            ],
        ],
        "recipe": {
            "id": recipe_id,
            "version": recipe_version,
            "parameters": {"installation-path": profile.installation_path},
        },
        "runtime": {
            "component-template-sha256": template_digest,
            "entrypoint": list(ENTRYPOINT_CONTRACT),
            "command": [RUNTIME_PLAN_PATH],
        },
    }


def formation_identity(descriptor: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json(descriptor).encode()).hexdigest()


def canonical_image_name(descriptor: Mapping[str, Any], component_id: str = "pycharm") -> str:
    return f"devcapsule-local-{component_id}:{formation_identity(descriptor)[:20]}"


def parse_locked_environment(lock: Mapping[str, Any]) -> LockedEnvironment:
    platform = _required_string(lock, "platform", "platform lock")
    base = _required_mapping(lock, "base", "platform lock")
    components = _required_mapping(lock, "components", "platform lock")
    component_id = _required_string(components, "interactive-surface", "components")
    profile = surface_profile(component_id)
    component = _required_mapping(components, component_id, "components")
    try:
        _interactive, ancillary_definitions = selected_component_definitions(lock)
    except ComponentCatalogError as exc:
        raise CliError(str(exc)) from exc
    materialization = _required_mapping(lock, "materialization", "platform lock")
    policy = _required_string(component, "delivery-policy", f"components.{component_id}")
    if policy != "local-materialization":
        raise CliError(
            f"Locked {component_id} delivery-policy must be 'local-materialization'."
        )
    artifact = ArtifactSpec(
        version=_required_string(component, "version", f"components.{component_id}"),
        url=_required_string(component, "url", f"components.{component_id}"),
        sha256=_required_string(component, "sha256", f"components.{component_id}"),
        variant=(
            _required_string(component, "variant", f"components.{component_id}")
            if profile.requires_variant
            else None
        ),
    )
    _validated_sha256(artifact.sha256, "Locked component SHA-256")
    ancillary_artifacts: list[LockedArtifactDeclaration] = []
    for definition in ancillary_definitions:
        metadata = _required_mapping(components, definition.id, "components")
        for locked_artifact in definition.locked_artifacts(metadata, platform):
            _validated_sha256(
                locked_artifact.sha256,
                f"Locked {locked_artifact.component_id} artifact SHA-256",
            )
            if locked_artifact.artifact_format not in {"file", "tar-gz-member"}:
                raise CliError(
                    f"Locked {locked_artifact.component_id} artifact format must be "
                    "'file' or 'tar-gz-member'."
                )
            if (
                locked_artifact.artifact_format == "tar-gz-member"
                and not locked_artifact.archive_member
            ):
                raise CliError(
                    f"Locked {locked_artifact.component_id} tar-gz-member artifact must name "
                    "an archive member."
                )
            if not Path(locked_artifact.destination).is_absolute():
                raise CliError(
                    f"Locked {locked_artifact.component_id} destination must be absolute."
                )
            ancillary_artifacts.append(locked_artifact)
    recipe_id = _required_string(materialization, "recipe", "materialization")
    recipe_version = _required_string(materialization, "recipe-version", "materialization")
    if recipe_id != profile.recipe_id or recipe_version != MATERIALIZATION_RECIPE_VERSION:
        raise CliError(
            f"Unsupported materialization recipe {recipe_id!r}@{recipe_version}; "
            f"the {component_id} surface expects "
            f"{profile.recipe_id!r}@{MATERIALIZATION_RECIPE_VERSION}."
        )
    identity_value = base.get("identity")
    if identity_value is not None and not isinstance(identity_value, str):
        raise CliError("platform lock base.identity must be a string when present.")
    return LockedEnvironment(
        platform=platform,
        base_reference=_required_string(base, "reference", "base"),
        base_identity=identity_value,
        component_id=component_id,
        artifact=artifact,
        ancillary_artifacts=tuple(ancillary_artifacts),
        recipe_id=recipe_id,
        recipe_version=recipe_version,
    )


def validate_base_image(
    details: ImageDetails,
    *,
    platform: str,
    expected_identity: str | None,
) -> None:
    operating_system, architecture = _split_platform(platform)
    if (details.operating_system, details.architecture) != (operating_system, architecture):
        raise CliError(
            f"Selected base {details.reference!r} is {details.operating_system}-{details.architecture}, "
            f"but the lock targets {platform}."
        )
    labels = details.labels
    if (
        labels.get(MANAGED_LABEL) != "true"
        or labels.get(METADATA_VERSION_LABEL) != METADATA_VERSION
        or labels.get(IMAGE_KIND_LABEL) != BASE_KIND
    ):
        raise CliError(
            f"Selected base {details.reference!r} is not a DevCapsule metadata-v1 base image."
        )
    if expected_identity is not None and details.identity != expected_identity:
        raise CliError(
            f"Selected base identity mismatch: expected {expected_identity}, received {details.identity}."
        )


def surface_materialization_spec(
    *,
    base_reference: str,
    base_identity: str,
    image: str,
    surface_root: Path,
    component_template: Path,
    artifact: ArtifactSpec,
    ancillary_files: tuple[tuple[Path, LockedArtifactDeclaration], ...] = (),
    platform: str,
    recipe_id: str = MATERIALIZATION_RECIPE_ID,
    recipe_version: str = MATERIALIZATION_RECIPE_VERSION,
    component_id: str = "pycharm",
) -> ImageBuildSpec:
    profile = surface_profile(component_id)
    descriptor = formation_descriptor(
        platform=platform,
        base_identity=base_identity,
        artifact=artifact,
        ancillary_artifacts=tuple(declaration for _path, declaration in ancillary_files),
        recipe_id=recipe_id,
        recipe_version=recipe_version,
        component_id=component_id,
    )
    identity = formation_identity(descriptor)
    environment = _ancillary_environment(
        tuple(declaration for _path, declaration in ancillary_files)
    )
    return ImageBuildSpec(
        image=image,
        base_image=base_reference,
        components=(
            DirectoryComponent(surface_root, profile.installation_path),
            *profile.post_install,
            FileComponent(component_template, COMPONENT_TEMPLATE_PATH, permissions=0o644),
            *(
                FileComponent(path, declaration.destination, permissions=declaration.permissions)
                for path, declaration in ancillary_files
            ),
            *( (EnvComponent(environment),) if environment else () ),
            LabelComponent(
                managed_labels(MATERIALIZED_KIND, image)
                + (
                    ("devcapsule.materialization.descriptor", canonical_json(descriptor)),
                    ("devcapsule.materialization.identity", identity),
                    ("devcapsule.materialization.recipe-version", recipe_version),
                    ("devcapsule.materialization.base-identity", base_identity),
                    ("devcapsule.component.id", component_id),
                    ("devcapsule.component.version", artifact.version),
                    *(
                        (("devcapsule.component.variant", artifact.variant),)
                        if artifact.variant is not None
                        else ()
                    ),
                    ("devcapsule.component.sha256", artifact.sha256.lower()),
                    (f"devcapsule.component.{profile.family}.version", artifact.version),
                    (f"devcapsule.component.{profile.family}.sha256", artifact.sha256.lower()),
                )
            ),
        ),
    )


def ensure_materialized_surface(
    *,
    base_reference: str,
    base_identity: str,
    platform: str,
    artifact: ArtifactSpec,
    ancillary_artifacts: tuple[LockedArtifactDeclaration, ...] = (),
    cache_root: Path,
    inspect_image: Callable[[str], ImageDetails | None],
    build: Callable[[ImageBuildSpec], None],
    recipe_id: str = MATERIALIZATION_RECIPE_ID,
    recipe_version: str = MATERIALIZATION_RECIPE_VERSION,
    component_id: str = "pycharm",
) -> tuple[str, bool]:
    profile = surface_profile(component_id)
    descriptor = formation_descriptor(
        platform=platform,
        base_identity=base_identity,
        artifact=artifact,
        ancillary_artifacts=ancillary_artifacts,
        recipe_id=recipe_id,
        recipe_version=recipe_version,
        component_id=component_id,
    )
    image = canonical_image_name(descriptor, component_id)
    identity = formation_identity(descriptor)
    with _exclusive_lock(cache_root / "locks" / "materializations" / f"{identity}.lock"):
        existing = inspect_image(image)
        if existing is not None:
            verify_materialized_image(existing, descriptor=descriptor, canonical_name=image)
            return image, False

        acquisition = acquire_artifact(artifact, cache_root)
        ancillary_acquisitions = tuple(
            (
                acquire_artifact(
                    ArtifactSpec(item.version, item.url, item.sha256, item.component_id),
                    cache_root,
                ),
                item,
            )
            for item in ancillary_artifacts
        )
        work_root = cache_root / "work"
        work_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="devcapsule-materialize-", dir=work_root) as temporary_value:
            temporary = Path(temporary_value)
            try:
                surface_root = normalize_archive_directory(acquisition.path, temporary)
            except OSError as exc:
                raise CliError(
                    f"Cannot unpack the verified {component_id} archive beneath {work_root}: {exc}"
                ) from exc
            for probe in profile.archive_probes:
                if not (surface_root / probe).is_file():
                    raise CliError(
                        f"The verified {component_id} archive does not contain {probe}."
                    )
            template_path = temporary / "component-runtime-template.json"
            template_path.write_text(
                canonical_json(component_runtime_template(component_id)) + "\n", encoding="utf-8"
            )
            ancillary_files = tuple(
                (
                    _prepare_locked_artifact(
                        acquired.path,
                        declaration,
                        temporary / f"{declaration.component_id}-{index}",
                    ),
                    declaration,
                )
                for index, (acquired, declaration) in enumerate(ancillary_acquisitions)
            )
            build(
                surface_materialization_spec(
                    base_reference=base_reference,
                    base_identity=base_identity,
                    image=image,
                    surface_root=surface_root,
                    component_template=template_path,
                    artifact=artifact,
                    ancillary_files=ancillary_files,
                    platform=platform,
                    recipe_id=recipe_id,
                    recipe_version=recipe_version,
                    component_id=component_id,
                )
            )
        completed = inspect_image(image)
        if completed is None:
            raise CliError(f"Docker build completed without creating canonical image {image!r}.")
        verify_materialized_image(completed, descriptor=descriptor, canonical_name=image)
        return image, True


def _extract_archive_member(archive: Path, member_name: str, destination: Path) -> Path:
    """Extract exactly one regular file from a verified tar archive."""

    try:
        with tarfile.open(archive, mode="r:gz") as package:
            try:
                member = package.getmember(member_name)
            except KeyError as exc:
                raise CliError(
                    f"Verified component artifact does not contain {member_name!r}."
                ) from exc
            if not member.isfile() or member.size <= 0 or member.size > 1024**3:
                raise CliError(f"Locked archive member {member_name!r} is not a regular executable file.")
            source = package.extractfile(member)
            if source is None:
                raise CliError(f"Cannot read locked archive member {member_name!r}.")
            with source, destination.open("wb") as output:
                while chunk := source.read(1024 * 1024):
                    output.write(chunk)
    except tarfile.TarError as exc:
        raise CliError(f"Cannot read verified component archive {archive}: {exc}") from exc
    destination.chmod(0o700)
    return destination


def _prepare_locked_artifact(
    acquired: Path,
    declaration: LockedArtifactDeclaration,
    destination: Path,
) -> Path:
    if declaration.artifact_format == "file":
        shutil.copyfile(acquired, destination)
        destination.chmod(0o700)
        return destination
    if declaration.artifact_format == "tar-gz-member" and declaration.archive_member is not None:
        return _extract_archive_member(acquired, declaration.archive_member, destination)
    raise CliError(
        f"Unsupported locked artifact format {declaration.artifact_format!r} for "
        f"{declaration.component_id}."
    )


def _ancillary_environment(
    declarations: tuple[LockedArtifactDeclaration, ...],
) -> tuple[tuple[str, str], ...]:
    environment: dict[str, str] = {}
    for declaration in declarations:
        for name, value in declaration.environment:
            previous = environment.get(name)
            if previous is not None and previous != value:
                raise CliError(
                    f"Materialized components declare conflicting values for environment {name}."
                )
            environment[name] = value
    return tuple(sorted(environment.items()))


def verify_materialized_image(
    details: ImageDetails,
    *,
    descriptor: Mapping[str, Any],
    canonical_name: str,
) -> None:
    labels = details.labels
    expected_json = canonical_json(descriptor)
    expected_identity = formation_identity(descriptor)
    problem = (
        labels.get(MANAGED_LABEL) != "true"
        or labels.get(METADATA_VERSION_LABEL) != METADATA_VERSION
        or labels.get(IMAGE_KIND_LABEL) != MATERIALIZED_KIND
        or labels.get(CANONICAL_NAME_LABEL) != canonical_name
        or labels.get("devcapsule.materialization.identity") != expected_identity
        or labels.get("devcapsule.materialization.base-identity") != descriptor["base"]["identity"]
        or labels.get("devcapsule.materialization.recipe-version") != descriptor["recipe"]["version"]
        or labels.get("devcapsule.component.id") != descriptor["components"][0]["id"]
        or labels.get("devcapsule.component.version") != descriptor["components"][0]["version"]
        or labels.get("devcapsule.component.sha256") != descriptor["components"][0]["artifact"]["sha256"]
    )
    stored_descriptor = labels.get("devcapsule.materialization.descriptor")
    try:
        parsed_descriptor = json.loads(stored_descriptor or "")
    except json.JSONDecodeError:
        parsed_descriptor = None
    if (
        problem
        or not isinstance(parsed_descriptor, dict)
        or canonical_json(parsed_descriptor) != expected_json
        or formation_identity(parsed_descriptor) != expected_identity
    ):
        raise CliError(
            f"Canonical image tag {canonical_name!r} exists with conflicting or malformed metadata; "
            "inspect and remove or retag it before retrying."
        )


@contextmanager
def _exclusive_lock(path: Path) -> Iterator[None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as stream:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def _validated_sha256(value: str, label: str) -> str:
    normalized = value.lower()
    if len(normalized) != 64 or any(character not in "0123456789abcdef" for character in normalized):
        raise CliError(f"{label} must contain exactly 64 hexadecimal characters.")
    return normalized


def _split_platform(value: str) -> tuple[str, str]:
    try:
        operating_system, architecture = value.split("-", 1)
    except ValueError as exc:
        raise CliError(f"Unsupported platform alias {value!r}; expected OS-ARCHITECTURE.") from exc
    if not operating_system or not architecture:
        raise CliError(f"Unsupported platform alias {value!r}; expected OS-ARCHITECTURE.")
    return operating_system, architecture


def _required_mapping(value: Mapping[str, Any], key: str, context: str) -> Mapping[str, Any]:
    selected = value.get(key)
    if not isinstance(selected, dict):
        raise CliError(f"{context} must define [{key}] formation data.")
    return selected


def _required_string(value: Mapping[str, Any], key: str, context: str) -> str:
    selected = value.get(key)
    if not isinstance(selected, str) or not selected:
        raise CliError(f"{context} must define non-empty {key!r} formation data.")
    return selected
