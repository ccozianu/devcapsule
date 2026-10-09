"""Read-only project information, with launch evidence distinct from selection."""
from __future__ import annotations

from copy import deepcopy
import os
from pathlib import Path
from typing import Any

from devcapsule.components.catalog import selected_component_definitions
from devcapsule.configuration.bindings import configuration_binding_declarations, managed_binding_path
from devcapsule.configuration.storage import checkout_name_for, find_checkout_record, load_checkout, lock_for, manifest_for
from devcapsule.configuration.file_formats import ProjectConfigurationError


ENVIRONMENT_PURPOSES = {
    "HOME": "Persistent user home",
    "PROJECT_PATH": "Project source inside the capsule",
    "PATH": "Executable search path; xtras/bin is available to tools and terminals",
    "XDG_CONFIG_HOME": "User configuration",
    "XDG_DATA_HOME": "User data",
    "XDG_STATE_HOME": "User state",
    "XDG_CACHE_HOME": "Reconstructable caches",
    "XDG_RUNTIME_DIR": "Temporary per-session runtime files",
    "CODEX_HOME": "Persistent Codex configuration and authentication",
    "CLAUDE_CONFIG_DIR": "Persistent Claude configuration and authentication",
    "DISABLE_UPDATES": "Use the lock-selected Claude installation",
    "DEVCAPSULE_CONTAINER_NAME": "Running container name",
    "DISPLAY": "Selected display server",
    "XAUTHORITY": "Display credential file path (contents omitted)",
    "BROWSER": "Host browser dispatch command, when authorized",
    "DOCKER_HOST": "Docker endpoint, when authorized",
    "IDE_UID": "Capsule user's UID",
    "IDE_GID": "Capsule user's GID",
    "IDE_USER": "Capsule user's name",
    "IDE_CONFIG_PATH": "IDE configuration mount",
    "IDE_PROJECT_STATE_PATH": "IDE project-state mount",
    "IDE_GLOBAL_SETTINGS_PATH": "IDE persistent home",
    "LIBGL_ALWAYS_SOFTWARE": "Software graphics rendering",
    "MESA_LOADER_DRIVER_OVERRIDE": "Graphics driver selection",
    "LIBGL_DRI3_DISABLE": "Graphics transport compatibility",
    "NO_AT_BRIDGE": "Accessibility bus selection",
    "PYCHARM_PROPERTIES": "Generated IDE properties file",
    "JAVA_TOOL_OPTIONS": "Managed JVM options for the IDE",
}
TEMPORARY_PATHS = [
    {"path": path, "lifecycle": "Lost when this container is removed"}
    for path in ("/tmp", "/run", "/var/tmp", "/dev/shm")
]
NOTES = [
    "Managed storage may live outside the Git checkout. It survives container replacement, not deletion of that storage.",
    "Extra tools are developer-managed files, not catalog components or a reproducible package set.",
    "Changes outside the listed persistent mounts are lost when the container is removed; the root filesystem is normally read-only.",
    "Secret values are omitted; this report never enumerates the full process environment.",
]


def component_versions(lock: dict[str, Any]) -> dict[str, str]:
    return {name: str(value.get("version", "unknown"))
            for name, value in lock.get("components", {}).items() if isinstance(value, dict)}


def configured_environment(lock: dict[str, Any], mount: str) -> list[dict[str, str]]:
    home = "/home/devcapsule"
    values = {"HOME": home, "PROJECT_PATH": mount,
              "XDG_CONFIG_HOME": home + "/.config", "XDG_DATA_HOME": home + "/.local/share",
              "XDG_STATE_HOME": home + "/.local/state", "XDG_CACHE_HOME": home + "/.cache"}
    interactive, ancillary = selected_component_definitions(lock)
    prefixes = ["/opt/xtras/bin"]
    for definition in (interactive, *ancillary):
        values.update({key: value for key, value in definition.runtime_template().component.environment.items()
                       if key in ENVIRONMENT_PURPOSES})
        metadata = lock["components"].get(definition.id)
        if not isinstance(metadata, dict):
            continue  # Legacy image-reference locks do not describe artifacts.
        for artifact in definition.locked_artifacts(metadata, lock["platform"]):
            for name, value in artifact.environment:
                if name == "PATH" and value.endswith(":${PATH}"):
                    prefix = value.removesuffix(":${PATH}")
                    if prefix not in prefixes:
                        prefixes.append(prefix)
                elif name in ENVIRONMENT_PURPOSES:
                    values[name] = value
    values["PATH"] = ":".join([*prefixes, "<base-image PATH>"])
    return [{"name": name, "value": value, "purpose": ENVIRONMENT_PURPOSES[name],
             "source": "configured; base PATH suffix is not inspected" if name == "PATH" else "configured"}
            for name, value in sorted(values.items())]


def configured_information(root: Path, manifest: dict[str, Any], lock: dict[str, Any],
                           checkout: dict[str, Any], *, checkout_name: str) -> dict[str, Any]:
    """Project the launcher's selected inputs without resolving or writing them.

    ``checkout_name`` comes from where the checkout's record lives
    (``checkout_name_for``); no record carries a name key.
    """
    mount = manifest["project"]["mount"]
    configured = dict(checkout.get("state", {}).get("adopted", {}))
    configured.update(checkout.get("configuration", {}).get("bindings", {}).get("host-directory", {}))
    persistence = [{"name": "project", "path": mount, "backing": str(root),
                    "scope": "this checkout", "kind": "source",
                    "lifecycle": "Source files survive container removal"}]
    for name, declaration in configuration_binding_declarations(lock).items():
        explicit = configured.get(name)
        backing = (Path(str(explicit)).expanduser().resolve() if explicit is not None
                   else managed_binding_path(root, declaration).resolve())
        persistence.append({"name": name, "path": declaration.container_path, "backing": str(backing),
                            "scope": "explicit storage; may be shared" if explicit is not None else "this checkout",
                            "kind": declaration.kind,
                            "lifecycle": "Survives container replacement; caches may be cleared" if declaration.kind == "cache"
                            else "Survives container replacement"})
    home = next(row for row in persistence if row["name"] == "home")
    persistence.append({"name": "xtras", "path": "/opt/xtras", "backing": str(Path(home["backing"]) / "xtras"),
                        "scope": home["scope"], "kind": "durable",
                        "lifecycle": "Alias of /home/devcapsule/xtras; follows home storage"})
    return {
        "schema-version": 1, "context": "host selection (next launch)",
        "project": {key: manifest["project"].get(key) for key in ("name", "creator", "slug")},
        "checkout": {"launcher-path": str(root), "runtime-path": mount,
                     "name": checkout_name, "registered": bool(checkout)},
        "components": component_versions(lock),
        "base": {key: lock.get("base", {}).get(key) for key in ("reference", "build-mnemonic")},
        "environment": configured_environment(lock, mount), "persistence": persistence,
        "temporary": deepcopy(TEMPORARY_PATHS), "notes": list(NOTES),
    }


def project_information(start: Path, *, runtime_fallback: bool) -> dict[str, Any]:
    from devcapsule import runtime_configuration

    context = runtime_configuration.for_project(start, fallback=runtime_fallback)
    if context is not None:
        captured = context.document.get("info")
        if isinstance(captured, dict):
            report = deepcopy(captured)
        else:
            report = {"schema-version": 1, "project": context.document["project"],
                      "checkout": {"launcher-path": context.document["launcher-root"],
                                   "runtime-path": str(context.root)},
                      "environment": [], "persistence": [], "temporary": deepcopy(TEMPORARY_PATHS),
                      "notes": [*NOTES, "This older launch did not capture storage backing; relaunch with the updated launcher."]}
        running = context.document["running"]
        report["context"] = "running capsule (captured at launch)"
        # Prefer the launch context's checkout-name, with a filename fallback
        # for older contexts. Their captured info named every checkout "default".
        report["checkout"]["name"] = context.checkout_name
        report["components"] = component_versions(running["lock"])
        report["base"] = {key: running["lock"].get("base", {}).get(key) for key in ("reference", "build-mnemonic")}
        report["running-selection"] = running["identity"]
        # An allowlist excludes credential variables, including unrelated or
        # undeclared secrets. Runtime-only fields come from this process.
        report["environment"] = [{"name": name, "value": os.environ[name], "purpose": purpose,
                                  "source": "observed in this process"}
                                 for name, purpose in ENVIRONMENT_PURPOSES.items() if name in os.environ]
        try:
            _, next_lock, _ = context.current()
            report["next-launch-components"] = component_versions(next_lock)
            report["selection-changed"] = next_lock != running["lock"]
        except ProjectConfigurationError as exc:
            report["next-launch-unavailable"] = str(exc)
        return report
    root, manifest = manifest_for(start)
    _, lock = lock_for(root, manifest)
    record = find_checkout_record(manifest, root)
    checkout = load_checkout(record, manifest, root) if record is not None else {}
    report = configured_information(
        root, manifest, lock, checkout,
        checkout_name=checkout_name_for(manifest, record) if record is not None else "default")
    report["notes"].append("Runtime-only display, container name and actual base PATH are unavailable before launch.")
    return report


def render_information(report: dict[str, Any]) -> str:
    project = report["project"]
    lines = [f"Project: {project.get('name') or project['slug']} ({project['creator']}/{project['slug']})",
             f"Context: {report['context']}",
             f"Checkout: {report['checkout']['launcher-path']}",
             f"Checkout name: {report['checkout']['name']}",
             f"Source in capsule: {report['checkout']['runtime-path']}", "", "Components:"]
    lines.extend(f"  {name}: {version}" for name, version in report["components"].items())
    lines.append(f"Base: {report['base'].get('reference', 'unavailable')}")
    if "next-launch-components" in report:
        lines.append("Next launch components" + (" (changed):" if report["selection-changed"] else " (same selection):"))
        lines.extend(f"  {name}: {version}" for name, version in report["next-launch-components"].items())
    if "next-launch-unavailable" in report:
        lines.append("Next launch unavailable: " + report["next-launch-unavailable"])
    lines.extend(["", "Environment:"])
    lines.extend(f"  {row['name']}={row['value']} — {row['purpose']} ({row['source']})" for row in report["environment"])
    lines.extend(["", "Persistence (backing paths as seen by the launcher):"])
    lines.extend(f"  {row['path']} -> {row['backing']} [{row['scope']}; {row['kind']}] — {row['lifecycle']}"
                 for row in report["persistence"])
    lines.extend(["", "Temporary:"])
    lines.extend(f"  {row['path']}: {row['lifecycle']}" for row in report["temporary"])
    lines.extend(["", *report["notes"]])
    return "\n".join(lines)
