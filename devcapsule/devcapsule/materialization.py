"""Host-side acquisition and workstation-local component materialization."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import tempfile
from typing import Callable
from urllib.request import urlopen

from devcapsule.compat import CliError
from devcapsule.image_build import (
    DirectoryComponent,
    FileComponent,
    ImageBuildSpec,
    LabelComponent,
    normalize_archive_directory,
)
from devcapsule.image_metadata import MATERIALIZED_KIND, managed_labels


@dataclass(frozen=True)
class ArtifactSpec:
    version: str
    url: str
    sha256: str


@dataclass(frozen=True)
class Acquisition:
    path: Path
    downloaded: bool


MATERIALIZATION_RECIPE_VERSION = "1"


def acquire_artifact(spec: ArtifactSpec, cache_root: Path) -> Acquisition:
    expected = spec.sha256.lower()
    if len(expected) != 64 or any(character not in "0123456789abcdef" for character in expected):
        raise CliError("Artifact SHA-256 must contain exactly 64 hexadecimal characters.")
    destination = cache_root / "artifacts" / "sha256" / expected
    if destination.is_file():
        if sha256_file(destination) == expected:
            return Acquisition(destination, False)
        destination.unlink()
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(f".{destination.name}.download")
    digest = hashlib.sha256()
    try:
        with urlopen(spec.url) as response, temporary.open("wb") as output:  # noqa: S310 - lock-pinned URL
            while chunk := response.read(1024 * 1024):
                digest.update(chunk)
                output.write(chunk)
        actual = digest.hexdigest()
        if actual != expected:
            raise CliError(f"Artifact digest mismatch: expected {expected}, received {actual}.")
        temporary.replace(destination)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    return Acquisition(destination, True)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def materialization_identity(base_identity: str, artifact: ArtifactSpec) -> str:
    identity = json.dumps(
        [base_identity, artifact.version, artifact.sha256, MATERIALIZATION_RECIPE_VERSION],
        separators=(",", ":"),
    )
    return hashlib.sha256(identity.encode()).hexdigest()


def local_image_name(base_identity: str, artifact: ArtifactSpec) -> str:
    return f"devcapsule-local-pycharm:{materialization_identity(base_identity, artifact)[:20]}"


def pycharm_materialization_spec(
    *, base_image: str, image: str, pycharm_root: Path, runtime_plan: Path, artifact: ArtifactSpec
) -> ImageBuildSpec:
    return ImageBuildSpec(
        image=image,
        base_image=base_image,
        components=(
            DirectoryComponent(pycharm_root, "/opt/jetbrains/pycharm"),
            FileComponent(runtime_plan, "/etc/devcapsule/runtime-plan.json", permissions=0o644),
            LabelComponent(
                managed_labels(MATERIALIZED_KIND, image)
                + (
                    ("devcapsule.materialization.identity", materialization_identity(base_image, artifact)),
                    ("devcapsule.materialization.recipe-version", MATERIALIZATION_RECIPE_VERSION),
                    ("devcapsule.materialization.base-identity", base_image),
                    ("devcapsule.component.id", "pycharm"),
                    ("devcapsule.component.version", artifact.version),
                    ("devcapsule.component.sha256", artifact.sha256),
                    ("devcapsule.component.jetbrains.version", artifact.version),
                    ("devcapsule.component.jetbrains.sha256", artifact.sha256),
                )
            ),
        ),
    )


def ensure_materialized_pycharm(
    *,
    base_image: str,
    artifact: ArtifactSpec,
    cache_root: Path,
    image_exists: Callable[[str], bool],
    build: Callable[[ImageBuildSpec], None],
) -> tuple[str, bool]:
    image = local_image_name(base_image, artifact)
    if image_exists(image):
        return image, False
    acquisition = acquire_artifact(artifact, cache_root)
    with tempfile.TemporaryDirectory(prefix="devcapsule-materialize-") as temporary_value:
        temporary = Path(temporary_value)
        pycharm_root = normalize_archive_directory(acquisition.path, temporary)
        launcher = pycharm_root / "bin" / "pycharm.sh"
        if not launcher.is_file():
            raise CliError("The verified JetBrains archive does not contain bin/pycharm.sh.")
        plan_path = temporary / "runtime-plan.json"
        plan_path.write_text(json.dumps(default_jetbrains_runtime_plan()) + "\n", encoding="utf-8")
        build(
            pycharm_materialization_spec(
                base_image=base_image,
                image=image,
                pycharm_root=pycharm_root,
                runtime_plan=plan_path,
                artifact=artifact,
            )
        )
    return image, True


def default_jetbrains_runtime_plan() -> dict[str, object]:
    return {
        "version": 1,
        "project_path": "/workspace/project",
        "home": "/home/devcapsule",
        "identity": {"uid": 1000, "gid": 1000, "user": "devcapsule"},
        "state_slots": [
            {"name": "pycharm/config", "path": "/ide-config"},
            {"name": "pycharm/system", "path": "/ide-project-state/system"},
            {"name": "pycharm/plugins", "path": "/ide-plugins"},
            {"name": "pycharm/log", "path": "/ide-project-state/log"},
        ],
        "component": {
            "adapter": "jetbrains",
            "configuration": {
                "installation_path": "/opt/jetbrains/pycharm",
                "launcher": "bin/pycharm.sh",
                "properties_path": "/tmp/devcapsule-jetbrains.properties",
                "properties_environment_variable": "PYCHARM_PROPERTIES",
                "state_slot_mapping": {
                    "config": "pycharm/config",
                    "system": "pycharm/system",
                    "plugins": "pycharm/plugins",
                    "log": "pycharm/log",
                },
            },
        },
    }
