"""Read-only configuration access for the project hosted by this runtime.

The launcher owns checkout records and recovery. A capsule receives their
containing directory read-only plus an immutable description of this launch.
Host paths are identities here, not paths to resolve in the container.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import json
import os
from pathlib import Path
import shlex
from typing import Any, Mapping, Sequence

from devcapsule.configuration.documents import Artifact, ProjectConfigurationError, admit_document, render_document, selected_version_lock
from devcapsule.configuration.storage import ResolvedProject, discover_project, load_toml, manifest_for, recommendation_lock_for


CONTEXT_PATH = Path("/etc/devcapsule/launch-context.json")
CONFIGURATION_PATH = Path("/etc/devcapsule/checkout")


@dataclass(frozen=True)
class LaunchConfiguration:
    directory: Path
    document: dict[str, Any]

    @classmethod
    def capture(cls, selected: ResolvedProject, identity: str) -> LaunchConfiguration:
        return cls(selected.checkout_path.parent, {
            "format": 1, "project": deepcopy(selected.manifest["project"]),
            "launcher-root": str(selected.root),
            "runtime-root": selected.resolution["runtime"]["project-mount"],
            "checkout-file": selected.checkout_path.name,
            "running": {"identity": identity, "lock": deepcopy(selected.lock),
                        "origin": "local selection" if selected_version_lock(selected.checkout) else "project recommendation",
                        "base": deepcopy(selected.checkout.get("authorization", {}).get("base-image", {}))},
        })


@dataclass(frozen=True)
class RuntimeConfiguration:
    document: dict[str, Any]

    @property
    def root(self) -> Path:
        return Path(self.document["runtime-root"])

    @property
    def checkout_path(self) -> Path:
        return CONFIGURATION_PATH / self.document["checkout-file"]

    def launcher_command(self, arguments: Sequence[str]) -> str:
        return shlex.join(["devcapsule", "project", "--path", self.document["launcher-root"], *arguments])

    def current(self) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
        """Read the next-launch selection without repair or host path validation."""
        root, manifest = manifest_for(self.root)
        identity = self.document["project"]
        if any(manifest["project"][key] != identity[key] for key in ("creator", "slug")):
            raise ProjectConfigurationError("Project identity changed since launch; inspect it with the launcher.")
        if self.checkout_path.with_suffix(".activation.toml").exists():
            raise ProjectConfigurationError("A launcher activation is in progress or needs recovery; retry after the launcher finishes. Runtime inspection never repairs host records.")
        checkout = load_toml(self.checkout_path)
        admit_document(checkout, Artifact.checkout, self.checkout_path)
        if checkout.get("checkout", {}).get("path") != self.document["launcher-root"]:
            raise ProjectConfigurationError("Mounted checkout record does not match this launch's checkout identity.")
        if any(checkout.get("project", {}).get(key) != identity[key] for key in ("creator", "slug")):
            raise ProjectConfigurationError("Mounted checkout record does not match this launch's project identity.")
        lock = selected_version_lock(checkout)
        if lock is None:
            _, lock = recommendation_lock_for(root, manifest)
        return manifest, lock, checkout

    def configuration_report(self) -> str:
        _, _, checkout = self.current()
        shown = {key: value for key, value in checkout.items() if key != "version-set"}
        return ("Runtime context: read-only launcher configuration for the next launch.\n"
                "Host paths and permissions below are recorded choices, not observations of this running session.\n"
                "Use 'devcapsule project versions show' for running and next-launch software.\n\n"
                + render_document(shown)
                + "\nTo change configuration, use the launcher outside this capsule: "
                + self.launcher_command(["config", "list"]))


def for_project(start: Path) -> RuntimeConfiguration | None:
    """Runtime for its own project; still a launcher for separate nested projects."""
    try:
        root = discover_project(start)
    except ProjectConfigurationError:
        root = start.expanduser().resolve()
    # Older capsules have the project/name environment but no mounted context.
    # Do not pretend their project recommendation describes the running image.
    declared = os.environ.get("PROJECT_PATH") if os.environ.get("DEVCAPSULE_CONTAINER_NAME") else None
    if not CONTEXT_PATH.is_file():
        if declared and root == Path(declared).resolve():
            raise ProjectConfigurationError(
                "This capsule has no launcher configuration mount. Relaunch this project from outside "
                "the capsule with the updated DevCapsule launcher, then retry. Its running versions "
                "cannot be inferred from the project recommendation."
            )
        return None
    try:
        document = json.loads(CONTEXT_PATH.read_text())
        if not isinstance(document, dict) or document.get("format") != 1:
            raise ValueError("unsupported launch context format")
        for key in ("launcher-root", "runtime-root"):
            if not isinstance(document.get(key), str) or not Path(document[key]).is_absolute():
                raise ValueError(f"{key} must be an absolute path")
        if root != Path(document["runtime-root"]).resolve():
            return None
        name = document.get("checkout-file")
        if not isinstance(name, str) or Path(name).name != name or not name.endswith(".checkout.toml"):
            raise ValueError("invalid checkout record name")
        project, running = document["project"], document["running"]
        if not isinstance(project, dict) or not all(isinstance(project.get(key), str) for key in ("creator", "slug")):
            raise ValueError("missing project identity")
        if not isinstance(running, dict) or not isinstance(running.get("base"), dict):
            raise ValueError("missing running version set")
        if not isinstance(running.get("identity"), str) or running.get("origin") not in {"local selection", "project recommendation"}:
            raise ValueError("invalid running version-set identity/origin")
        admit_document(running["lock"], Artifact.lock, CONTEXT_PATH)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise ProjectConfigurationError(f"Cannot read runtime launch context: {exc}. Relaunch with the updated launcher.") from exc
    return RuntimeConfiguration(document)


def require_launcher(start: Path, arguments: Sequence[str]) -> None:
    context = for_project(start)
    if context is not None:
        raise ProjectConfigurationError(
            "This command needs launcher-owned configuration or state. Inside this capsule that "
            "configuration is read-only. Run outside the capsule: " + context.launcher_command(arguments)
        )
