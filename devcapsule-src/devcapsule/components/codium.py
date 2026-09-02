"""VSCodium component interface.

This module owns VSCodium's adapter and persistence declarations, the
vscode-family analogue of the PyCharm component. Generic runtime planning
consumes the declaration without knowing what the slots mean.
"""

from __future__ import annotations

from collections.abc import Mapping

from devcapsule.container_runtime.contract import ComponentRuntimeTemplate
from devcapsule.components import (
    ComponentDefinition,
    LockedArtifactDeclaration,
    SecretInputDeclaration,
    StateEnvironmentDeclaration,
)


class CodiumComponent(ComponentDefinition):
    """Trusted VSCodium component implementation."""

    @property
    def id(self) -> str:
        return "codium"

    @property
    def capability(self) -> str:
        # Decided 2026-08-31 by the product owner: VSCodium is the surface
        # for frontend engineering (HTML/JavaScript/TypeScript); PyCharm
        # remains the python-ide surface.
        return "frontend-ide"

    def runtime_template(self) -> ComponentRuntimeTemplate:
        return _runtime_template()

    def state_environment(self) -> tuple[StateEnvironmentDeclaration, ...]:
        return ()

    def secret_inputs(self) -> tuple[SecretInputDeclaration, ...]:
        return ()

    def locked_artifacts(
        self, metadata: Mapping[str, object], platform: str
    ) -> tuple[LockedArtifactDeclaration, ...]:
        # Like PyCharm, VSCodium materializes as a whole installation
        # directory; its acquisition joins the materialization slice, not the
        # per-file artifact adapter.
        return ()


def runtime_template() -> ComponentRuntimeTemplate:
    return DEFINITION.runtime_template()


def _runtime_template() -> ComponentRuntimeTemplate:
    return ComponentRuntimeTemplate.from_mapping(
        {
            "version": 1,
            "component": {
                "id": "codium",
                "adapter": "vscode",
                "configuration": {
                    "installation_path": "/opt/codium",
                    # The Electron binary at the installation root stays in
                    # the session's foreground; the bin/codium shell wrapper
                    # daemonizes and would end the session immediately. This
                    # is the retired launcher's proven codium-foreground
                    # behavior.
                    "launcher": "codium",
                    # Ruled 2026-09-02 by the product owner, superseding the
                    # 2026-08-31 setuid ruling: renderers run unsandboxed
                    # under full container hardening; see
                    # engineering-docs/design-notes/devcapsule/renderer-sandboxing.md.
                    # The flag is template data rather than adapter logic so
                    # the frozen v0.2.8 runtime, which appends
                    # additional_arguments verbatim, launches this posture
                    # unchanged.
                    "additional_arguments": ["--no-sandbox"],
                    # Chromium renderers push frames through /dev/shm — under
                    # the launcher's forced llvmpipe software rendering the
                    # 64MB Docker default intermittently SIGTRAPs the first
                    # renderer after a relaunch. Owner-confirmed 2026-09-02:
                    # at least 512m stops the crashes; 640m adds headroom
                    # while staying friendly to small-memory adopter laptops.
                    # See the 2026-09-02 relaunch-renderer-crash bug record.
                    "shared-memory-size": "640m",
                    "state_slot_mapping": {
                        "user-data": "user-data",
                        "extensions": "extensions",
                    },
                },
                "persistence": {
                    "home": "required",
                    "xdg": "home-relative",
                    "state_slots": [
                        _slot(
                            "user-data",
                            "/ide-user-data",
                            kind="durable",
                            sensitivity="personal",
                            reconstructable=False,
                            deletion_effect=(
                                "Removes editor settings, keybindings, snippets, "
                                "and per-workspace state."
                            ),
                        ),
                        _slot(
                            "extensions",
                            "/ide-extensions",
                            kind="durable",
                            sensitivity="personal",
                            reconstructable=False,
                            deletion_effect="Removes installed editor extensions.",
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


def logical_state_slots() -> tuple[str, ...]:
    template = runtime_template()
    return tuple(template.logical_slot_name(slot.name) for slot in template.persistence.state_slots)


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


DEFINITION: ComponentDefinition = CodiumComponent()
