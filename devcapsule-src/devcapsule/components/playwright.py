"""Python browser automation and its pinned Chromium runtime, installed offline."""

from collections.abc import Mapping

from devcapsule.compat import CliError
from devcapsule.components import ComponentDefinition, LockedArtifactDeclaration, SecretInputDeclaration, StateEnvironmentDeclaration
from devcapsule.components.discovery import PlaywrightDiscovery
from devcapsule.container_runtime.contract import ComponentRuntimeTemplate

ENVIRONMENT = (
    ("PLAYWRIGHT_BROWSERS_PATH", "/opt/playwright/browsers"),
    ("DEVCAPSULE_PLAYWRIGHT_PYTHON", "/opt/playwright/venv/bin/python"),
    ("DEVCAPSULE_PLAYWRIGHT_WHEELS", "/opt/playwright/wheels"),
)


class PlaywrightComponent(ComponentDefinition):
    @property
    def id(self) -> str:
        return "playwright"

    @property
    def capability(self) -> str:
        return "browser-automation"

    def channel_omission_reason(self) -> str:
        return "Python wheels and browser revisions are updated together through a reviewed catalog pin."

    def discovery_channel(self) -> PlaywrightDiscovery:
        return PlaywrightDiscovery()

    def runtime_template(self) -> ComponentRuntimeTemplate:
        return ComponentRuntimeTemplate.from_mapping({
            "version": 1,
            "component": {
                "id": self.id, "adapter": "ancillary", "configuration": {},
                "environment": dict(ENVIRONMENT),
                "persistence": {"home": "required", "xdg": "home-relative", "state_slots": []},
            },
        })

    def state_environment(self) -> tuple[StateEnvironmentDeclaration, ...]:
        return ()

    def secret_inputs(self) -> tuple[SecretInputDeclaration, ...]:
        return ()

    def locked_artifacts(self, metadata: Mapping[str, object], platform: str) -> tuple[LockedArtifactDeclaration, ...]:
        if metadata.get("delivery-policy") != "local-materialization" or metadata.get("platform") != platform:
            raise CliError("Playwright requires a local-materialization pin for the selected platform.")
        version = metadata.get("version")
        artifacts = metadata.get("artifacts")
        if not isinstance(version, str) or not isinstance(artifacts, dict) or not artifacts:
            raise CliError("Playwright pin must include its version, wheels and browser artifacts.")
        result = []
        for item in artifacts.values():
            if not isinstance(item, dict) or any(not isinstance(item.get(k), str) or not item[k]
                                                 for k in ("format", "url", "sha256", "destination")):
                raise CliError("Malformed Playwright artifact declaration.")
            if item["format"] not in {"python-wheel", "zip-directory"}:
                raise CliError("Playwright artifacts must be wheels or browser ZIP directories.")
            result.append(LockedArtifactDeclaration(
                self.id, version, item["url"], item["sha256"], item["destination"],
                artifact_format=item["format"], permissions=0o644, environment=ENVIRONMENT,
            ))
        return tuple(result)


DEFINITION: ComponentDefinition = PlaywrightComponent()
