"""Shared runtime declaration for independently scoped JetBrains IDEs."""

from devcapsule.container_runtime.contract import ComponentRuntimeTemplate


def jetbrains_template(component_id: str, launcher: str, properties_variable: str) -> ComponentRuntimeTemplate:
    return ComponentRuntimeTemplate.from_mapping(
        {
            "version": 1,
            "component": {
                "id": component_id,
                "adapter": "jetbrains",
                "environment": {
                    "JAVA_TOOL_OPTIONS": "-Dide.browser.jcef.sandbox.enable=false",
                },
                "configuration": {
                    "installation_path": f"/opt/jetbrains/{component_id}",
                    "launcher": launcher,
                    "properties_path": "/tmp/devcapsule-jetbrains.properties",
                    "properties_environment_variable": properties_variable,
                    "state_slot_mapping": {
                        "config": "config",
                        "system": "system",
                        "plugins": "plugins",
                        "log": "log",
                    },
                    "additional_properties": {
                        "ide.browser.jcef.sandbox.enable": "false",
                    },
                },
                "persistence": {
                    "home": "required",
                    "xdg": "home-relative",
                    "state_slots": [
                        _slot(
                            "config",
                            "/ide-config",
                            kind="durable",
                            sensitivity="personal",
                            reconstructable=False,
                            deletion_effect="Removes IDE settings and configuration.",
                        ),
                        _slot(
                            "plugins",
                            "/ide-plugins",
                            kind="durable",
                            sensitivity="personal",
                            reconstructable=False,
                            deletion_effect="Removes installed IDE plugins.",
                        ),
                        _slot(
                            "system",
                            "/ide-project-state/system",
                            kind="cache",
                            sensitivity="ordinary",
                            reconstructable=True,
                            deletion_effect="Removes rebuildable IDE indexes and system caches.",
                        ),
                        _slot(
                            "log",
                            "/ide-project-state/log",
                            kind="state",
                            sensitivity="personal",
                            reconstructable=False,
                            deletion_effect="Removes retained IDE diagnostic logs.",
                        ),
                        _slot(
                            "cache",
                            "/home/devcapsule/.cache",
                            kind="cache",
                            sensitivity="ordinary",
                            reconstructable=True,
                            deletion_effect="Removes rebuildable user-tool caches.",
                            home_overlay=True,
                        ),
                    ],
                },
            },
        }
    )



def _slot(
    name: str,
    container_path: str,
    *,
    kind: str,
    sensitivity: str,
    reconstructable: bool,
    deletion_effect: str,
    home_overlay: bool = False,
) -> dict[str, object]:
    value: dict[str, object] = {
        "name": name,
        "container_path": container_path,
        "kind": kind,
        "sensitivity": sensitivity,
        "default_scope": "checkout",
        "storage": "directory",
        "concurrent": False,
        "owner": "runtime-user",
        "permissions": "0700",
        "reconstructable": reconstructable,
        "deletion_effect": deletion_effect,
    }
    if home_overlay:
        value["home_overlay"] = True
    return value

