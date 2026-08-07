from __future__ import annotations

import inspect

import pytest

from devcapsule.components import ComponentDefinition
from devcapsule.components.codex import (
    CODEX_EXECUTABLE,
    DEFINITION,
    CodexComponent,
    runtime_template,
)
from devcapsule.components.pycharm import PyCharmComponent
from devcapsule.container_runtime.contract import Identity, RuntimePlan
from devcapsule.project_configuration import (
    component_secret_inputs,
    configuration_binding_declarations,
)


def locked_components() -> dict[str, object]:
    return {
        "components": {
            "interactive-surface": "pycharm",
            "pycharm": {},
            "codex": {
                "version": "0.145.0",
                "delivery-policy": "local-materialization",
                "artifacts": {
                    "linux-amd64": {
                        "url": "https://example.test/codex.tgz",
                        "sha256": "c" * 64,
                        "archive-member": "package/vendor/x86_64-unknown-linux-musl/bin/codex",
                    }
                },
            },
        }
    }


def test_built_in_components_explicitly_implement_abstract_contract() -> None:
    assert inspect.isabstract(ComponentDefinition)
    assert issubclass(CodexComponent, ComponentDefinition)
    assert issubclass(PyCharmComponent, ComponentDefinition)
    assert isinstance(DEFINITION, ComponentDefinition)

    incomplete_component = type("IncompleteComponent", (ComponentDefinition,), {})
    assert inspect.isabstract(incomplete_component)
    with pytest.raises(TypeError, match="abstract"):
        incomplete_component()


def test_codex_implements_component_contract_and_declares_ready_made_cli() -> None:
    definition: ComponentDefinition = DEFINITION
    artifact = definition.locked_artifacts(
        locked_components()["components"]["codex"],  # type: ignore[index]
        "linux-amd64",
    )[0]

    assert definition.id == "codex"
    assert definition.capability == "codex-agent"
    assert artifact.version == "0.145.0"
    assert artifact.destination == CODEX_EXECUTABLE
    assert artifact.permissions == 0o755


def test_codex_component_derives_environment_from_credential_state() -> None:
    template = runtime_template()
    slot = template.persistence.state_slots[0]
    assert template.component.environment == {"CODEX_HOME": "/home/devcapsule/.codex"}
    assert DEFINITION.state_environment()[0].state_slot == "home"
    assert slot.name == "home"
    assert slot.sensitivity == "credentials"
    assert slot.home_overlay is True
    assert slot.permissions == "0700"


def test_runtime_plan_combines_ancillary_state_and_environment() -> None:
    from devcapsule.components.pycharm import runtime_template as pycharm_template

    plan = RuntimePlan.for_component(
        pycharm_template(),
        project_path="/workspace/project",
        home="/home/devcapsule",
        identity=Identity(1000, 1000),
        ancillary_templates=(runtime_template(),),
    )
    assert plan.slots_by_name()["codex/home"] == "/home/devcapsule/.codex"
    assert plan.component_environment() == {
        "CODEX_HOME": "/home/devcapsule/.codex",
        "JAVA_TOOL_OPTIONS": "-Dide.browser.jcef.sandbox.enable=false",
    }
    assert RuntimePlan.from_json(plan.to_json()) == plan


def test_catalog_exposes_codex_state_and_optional_secret_metadata() -> None:
    lock = locked_components()
    codex_home = configuration_binding_declarations(lock)["codex/home"]
    secret = component_secret_inputs(lock)["codex/openai-api-key"]

    assert codex_home.container_path == "/home/devcapsule/.codex"
    assert codex_home.sensitivity == "credentials"
    assert secret.environment_variable == "OPENAI_API_KEY"
    assert secret.required is False
    assert secret.exposure == "container-environment"
