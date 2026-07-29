from __future__ import annotations

import json
from pathlib import Path

import pytest

from devcapsule.container_runtime.components.jetbrains import plan as plan_jetbrains
from devcapsule.container_runtime.contract import RuntimePlan, RuntimePlanError
from devcapsule.container_runtime.entrypoint import run
from devcapsule.container_runtime.filesystem import FilesystemPlan, plan_filesystem, prepare_filesystem
from devcapsule.container_runtime.graphics import environment as graphics_environment
from devcapsule.container_runtime.identity import foreground_command


def runtime_document(tmp_path: Path) -> dict[str, object]:
    return {
        "version": 1,
        "project_path": "/workspace/project",
        "home": str(tmp_path / "home"),
        "identity": {"uid": 1000, "gid": 1001, "user": "developer"},
        "state_slots": [
            {"name": "jetbrains/config", "path": str(tmp_path / "config")},
            {"name": "jetbrains/system", "path": str(tmp_path / "system")},
            {"name": "jetbrains/plugins", "path": str(tmp_path / "plugins")},
            {"name": "jetbrains/log", "path": str(tmp_path / "log")},
        ],
        "component": {
            "adapter": "jetbrains",
            "configuration": {
                "installation_path": "/opt/jetbrains/pycharm",
                "launcher": "bin/pycharm.sh",
                "properties_path": str(tmp_path / "idea.properties"),
                "properties_environment_variable": "PYCHARM_PROPERTIES",
                "state_slot_mapping": {
                    "config": "jetbrains/config",
                    "system": "jetbrains/system",
                    "plugins": "jetbrains/plugins",
                    "log": "jetbrains/log",
                },
            },
        },
    }


def test_contract_parses_versioned_runtime_plan(tmp_path: Path) -> None:
    plan = RuntimePlan.from_json(json.dumps(runtime_document(tmp_path)))
    assert plan.identity.uid == 1000
    assert plan.component.adapter == "jetbrains"
    assert plan.slots_by_name()["jetbrains/config"] == str(tmp_path / "config")


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda doc: doc.update(version=2), "unsupported runtime plan version"),
        (lambda doc: doc.update(identity={"uid": True, "gid": 1}), "identity.uid"),
        (lambda doc: doc.update(state_slots=[{"name": "same", "path": "/a"}, {"name": "same", "path": "/b"}]), "duplicate state slot"),
    ],
)
def test_contract_rejects_invalid_input(tmp_path: Path, change: object, message: str) -> None:
    document = runtime_document(tmp_path)
    change(document)  # type: ignore[operator]
    with pytest.raises(RuntimePlanError, match=message):
        RuntimePlan.from_mapping(document)


def test_generic_filesystem_plan_uses_persistent_home_and_declared_slots(tmp_path: Path) -> None:
    plan = plan_filesystem(RuntimePlan.from_mapping(runtime_document(tmp_path)))
    assert plan.environment["XDG_CONFIG_HOME"] == str(tmp_path / "home" / ".config")
    assert str(tmp_path / "plugins") in plan.directories
    assert plan.environment["XDG_RUNTIME_DIR"] == "/tmp/devcapsule-runtime-1000"


def test_filesystem_assigns_only_new_directories_when_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    existing = tmp_path / "existing"
    existing.mkdir()
    new = existing / "new"
    changed: list[tuple[Path, int, int]] = []
    monkeypatch.setattr("devcapsule.container_runtime.filesystem.os.geteuid", lambda: 0)
    monkeypatch.setattr(
        "devcapsule.container_runtime.filesystem.os.chown",
        lambda path, uid, gid: changed.append((Path(path), uid, gid)),
    )
    prepare_filesystem(
        FilesystemPlan(
            (str(existing), str(existing / ".ssh"), str(new)),
            {"HOME": str(existing), "XDG_RUNTIME_DIR": str(new)},
        ),
        RuntimePlan.from_mapping(runtime_document(tmp_path)).identity,
    )
    assert changed == [(existing / ".ssh", 1000, 1001), (new, 1000, 1001)]


def test_jetbrains_adapter_generates_properties_and_foreground_command(tmp_path: Path) -> None:
    launch = plan_jetbrains(RuntimePlan.from_mapping(runtime_document(tmp_path)))
    assert launch.command == ("/opt/jetbrains/pycharm/bin/pycharm.sh", "/workspace/project")
    assert launch.properties_environment_variable == "PYCHARM_PROPERTIES"
    assert f"idea.plugins.path={tmp_path / 'plugins'}\n" in launch.properties


def test_jetbrains_adapter_requires_declared_slot(tmp_path: Path) -> None:
    document = runtime_document(tmp_path)
    configuration = document["component"]["configuration"]  # type: ignore[index]
    configuration["state_slot_mapping"]["log"] = "missing"  # type: ignore[index]
    with pytest.raises(RuntimePlanError, match="log mapping"):
        plan_jetbrains(RuntimePlan.from_mapping(document))


def test_graphics_preserves_explicit_environment() -> None:
    assert graphics_environment({"LIBGL_ALWAYS_SOFTWARE": "0"})["LIBGL_ALWAYS_SOFTWARE"] == "0"


def test_identity_adds_gosu_only_when_root(monkeypatch: pytest.MonkeyPatch) -> None:
    plan = RuntimePlan.from_mapping(runtime_document(Path("/tmp/test")))
    monkeypatch.setattr("devcapsule.container_runtime.identity.os.geteuid", lambda: 0)
    assert foreground_command(("ide",), plan.identity) == ("gosu", "1000:1001", "ide")
    monkeypatch.setattr("devcapsule.container_runtime.identity.os.geteuid", lambda: 1000)
    assert foreground_command(("ide",), plan.identity) == ("ide",)


def test_entrypoint_prepares_properties_and_execs_foreground(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runtime = RuntimePlan.from_mapping(runtime_document(tmp_path))
    executed: list[object] = []

    def capture_exec(executable: str, command: tuple[str, ...], environment: dict[str, str]) -> None:
        executed.extend((executable, command, environment.copy()))
        raise RuntimeError("exec captured")

    monkeypatch.setattr("devcapsule.container_runtime.identity.os.geteuid", lambda: 1000)
    monkeypatch.setattr("devcapsule.container_runtime.entrypoint.os.execvpe", capture_exec)
    with pytest.raises(RuntimeError, match="exec captured"):
        run(runtime)

    properties_path = tmp_path / "idea.properties"
    assert properties_path.read_text(encoding="utf-8").startswith(
        f"idea.config.path={tmp_path / 'config'}\n"
    )
    assert executed[0] == "/opt/jetbrains/pycharm/bin/pycharm.sh"
    assert executed[1] == ("/opt/jetbrains/pycharm/bin/pycharm.sh", "/workspace/project")
    assert executed[2]["PYCHARM_PROPERTIES"] == str(properties_path)  # type: ignore[index]
