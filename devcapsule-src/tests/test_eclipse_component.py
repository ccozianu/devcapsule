"""Eclipse package selection, isolated workspace and foreground runtime contract."""
import tomllib

import pytest

from devcapsule.components.eclipse import DEFINITION
from devcapsule.container_runtime.components.eclipse import plan
from devcapsule.container_runtime.contract import Identity, RuntimePlan, RuntimePlanError
from devcapsule.materialization import parse_locked_environment, surface_profile
from devcapsule.platforms import Platform
from devcapsule.resolution_matrix import MATRICES, ResolutionError


def runtime():
    return RuntimePlan.for_component(DEFINITION.runtime_template(), project_path="/workspace/project",
                                     home="/home/devcapsule", identity=Identity(1000, 1000))


def test_java_package_materializes_with_browser_and_its_own_workspace():
    matrix = MATRICES[Platform.LINUX_AMD64]
    document = tomllib.loads(matrix.resolve(["eclipse-ide", "java", "browser-automation"]).render_lock())
    environment = parse_locked_environment(document)
    assert environment.component_id == "eclipse"
    assert environment.artifact.variant == "java"
    assert "/eclipse-java-2026-09-R-linux-gtk-x86_64.tar.gz" in environment.artifact.url
    assert environment.recipe_id == "eclipse-local-materialization"
    assert surface_profile("eclipse").installation_path == "/opt/eclipse"
    assert {a.component_id for a in environment.ancillary_artifacts} == {"playwright"}
    assert runtime().slots_by_name() == {"eclipse/workspace": "/ide-workspace"}
    assert DEFINITION.runtime_template().persistence.home == "required"
    assert not DEFINITION.runtime_template().persistence.state_slots[0].concurrent
    assert plan(runtime()).command == ("/opt/eclipse/eclipse", "-data", "/ide-workspace")
    assert tomllib.loads(matrix.resolve(["java-ide"]).render_lock())["components"]["interactive-surface"] == "intellij"
    with pytest.raises(ResolutionError, match="exactly one"):
        matrix.resolve(["java-ide", "eclipse-ide"])


@pytest.mark.parametrize("field,value,message", [
    ("workspace_slot", "absent", "declared state slot"),
    ("workspace_slot", None, "one-line string"),
    ("installation_path", "relative", "must be absolute"),
    ("launcher", "/bin/other", "must be relative"),
    ("launcher", "../other", "must be relative"),
    ("launcher", "eclipse\nother", "one-line string"),
])
def test_adapter_rejects_malformed_configuration(field, value, message):
    document = runtime().to_mapping()
    document["component"]["configuration"][field] = value
    with pytest.raises(RuntimePlanError, match=message):
        plan(RuntimePlan.from_mapping(document))


def test_entrypoint_supervises_eclipse_as_the_unprivileged_foreground_child(monkeypatch):
    from devcapsule.container_runtime import entrypoint
    children = []
    monkeypatch.setattr(entrypoint, "prepare_filesystem", lambda *args: None)
    monkeypatch.setattr(entrypoint.os, "geteuid", lambda: 0)
    class Supervisor:
        def __init__(self, selected):
            children.extend(selected)
        def run(self):
            return 7
    monkeypatch.setattr(entrypoint, "Supervisor", Supervisor)
    assert entrypoint.run(runtime()) == 7
    child, = children
    assert child.name == "eclipse" and child.foreground
    assert child.command == ("gosu", "1000:1000", *plan(runtime()).command)


def test_discovery_only_considers_stable_java_packages_for_the_platform(monkeypatch):
    from devcapsule.components import discovery
    from devcapsule.compat import CliError
    monkeypatch.setattr(discovery, "read_metadata", lambda _: b'''
        eclipse-jee-2099-12-R-linux-gtk-x86_64.tar.gz
        eclipse-java-2026-12-M1-linux-gtk-x86_64.tar.gz
        eclipse-java-2026-09-R-linux-gtk-x86_64.tar.gz
        eclipse-java-2099-12-R-linux-gtk-aarch64.tar.gz
    ''')
    channel = DEFINITION.discovery_channel()
    assert channel.check("2026-06-R", "linux-amd64").candidates[0].version == "2026-09-R"
    assert channel.check("2026-09-R", "linux-amd64").candidates == ()
    monkeypatch.setattr(discovery, "read_metadata", lambda _: b"missing package")
    with pytest.raises(CliError, match="expected one stable"):
        channel.check("2026-09-R", "linux-amd64")
