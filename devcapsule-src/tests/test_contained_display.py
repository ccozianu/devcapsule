"""The contained display: plan contract, per-run files, and declared children."""

from __future__ import annotations

import json
from pathlib import Path
import struct

import pytest

from devcapsule.container_runtime.contract import DisplayPlan, RuntimePlan, RuntimePlanError
from devcapsule.container_runtime.display import (
    DISPLAY_NAME,
    NOVNC_CHILD,
    WINDOW_MANAGER_CHILD,
    X_SOCKET_PATH,
    XVNC_CHILD,
    prepare_contained_display,
    read_token,
    write_xauthority,
)
from devcapsule.container_runtime.entrypoint import run

from tests.test_runtime_entrypoint import SupervisorCapture, captured_supervisor, runtime_document

_ = captured_supervisor  # re-exported fixture


def contained_document(tmp_path: Path, token: str = "a1b2c3") -> dict[str, object]:
    token_path = tmp_path / "display-token"
    token_path.write_text(token + "\n", encoding="utf-8")
    document = runtime_document(tmp_path)
    document["display"] = {
        "transport": "contained",
        "listen_address": "0.0.0.0",
        "port": 6080,
        "token_path": str(token_path),
    }
    return document


def test_contract_round_trips_both_transports(tmp_path: Path) -> None:
    contained = RuntimePlan.from_mapping(contained_document(tmp_path))
    assert contained.display is not None and contained.display.is_contained
    assert contained.display_transport() == "contained"
    assert RuntimePlan.from_json(contained.to_json()) == contained
    assert json.loads(contained.to_json())["display"]["port"] == 6080

    passthrough = RuntimePlan.from_mapping(runtime_document(tmp_path)).with_display(DisplayPlan.host_x11())
    assert passthrough.display_transport() == "host-x11"
    assert json.loads(passthrough.to_json())["display"] == {"transport": "host-x11"}
    assert RuntimePlan.from_json(passthrough.to_json()) == passthrough

    # Plans from before the section existed keep meaning passthrough.
    assert RuntimePlan.from_mapping(runtime_document(tmp_path)).display_transport() == "host-x11"


@pytest.mark.parametrize(
    ("display", "message"),
    [
        ({"transport": "xephyr"}, "display.transport must be one of"),
        ({"transport": "host-x11", "port": 1}, "must not carry port"),
        ({"transport": "contained", "listen_address": "0.0.0.0", "port": 0, "token_path": "/t"}, "display.port"),
        ({"transport": "contained", "listen_address": "0.0.0.0", "port": 6080, "token_path": "t"}, "token_path"),
        ({"transport": "contained", "listen_address": "", "port": 6080, "token_path": "/t"}, "listen_address"),
        ("contained", "display must be an object"),
    ],
)
def test_contract_rejects_malformed_display(tmp_path: Path, display: object, message: str) -> None:
    document = runtime_document(tmp_path)
    document["display"] = display
    with pytest.raises(RuntimePlanError, match=message):
        RuntimePlan.from_mapping(document)


def test_xauthority_entry_is_a_wildcard_cookie_for_the_display(tmp_path: Path) -> None:
    path = tmp_path / "Xauthority"
    write_xauthority(path, 1, b"\x01" * 16)
    body = path.read_bytes()
    assert path.stat().st_mode & 0o777 == 0o600
    family, = struct.unpack(">H", body[:2])
    assert family == 0xFFFF
    # address (empty), number "1", protocol name, 16-byte cookie
    assert body[2:] == b"\x00\x00" + b"\x00\x011" + b"\x00\x12MIT-MAGIC-COOKIE-1" + b"\x00\x10" + b"\x01" * 16


def test_token_must_be_one_clean_line(tmp_path: Path) -> None:
    good = tmp_path / "good"
    good.write_text("  f00d\n", encoding="utf-8")
    assert read_token(str(good)) == "f00d"
    for content in ("", "two words", "colon:here"):
        bad = tmp_path / "bad"
        bad.write_text(content, encoding="utf-8")
        with pytest.raises(RuntimePlanError, match="empty or malformed"):
            read_token(str(bad))
    with pytest.raises(RuntimePlanError, match="cannot read the display token"):
        read_token(str(tmp_path / "missing"))


def test_prepared_display_declares_children_and_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("devcapsule.container_runtime.display.os.geteuid", lambda: 1000)
    plan = RuntimePlan.from_mapping(contained_document(tmp_path, token="deadbeef"))
    runtime_dir = tmp_path / "runtime"
    runtime_dir.mkdir(mode=0o700)

    display = prepare_contained_display(plan, str(runtime_dir), lambda command: ("as-user", *command))

    assert [child.name for child in display.children] == [XVNC_CHILD, WINDOW_MANAGER_CHILD, NOVNC_CHILD]
    assert not any(child.foreground for child in display.children)
    xvnc, window_manager, novnc = display.children
    assert xvnc.command[:3] == ("as-user", "Xvnc", DISPLAY_NAME)
    assert ("-rfbport", "-1") == xvnc.command[xvnc.command.index("-rfbport"):][:2]
    assert ("-rfbunixpath", display.rfb_socket_path) == xvnc.command[xvnc.command.index("-rfbunixpath"):][:2]
    assert ("-auth", display.xauthority_path) == xvnc.command[xvnc.command.index("-auth"):][:2]
    assert xvnc.ready is not None and xvnc.ready() is False  # no X server in the test process
    assert window_manager.command == ("as-user", "openbox")
    assert novnc.command[-1] == "0.0.0.0:6080"
    assert "TokenFile" in novnc.command
    assert novnc.ready is not None and novnc.ready() is False  # nothing listens on 6080 here

    directory = runtime_dir / "display"
    assert directory.stat().st_mode & 0o777 == 0o700
    tokens = directory / "tokens"
    assert tokens.read_text(encoding="utf-8") == f"deadbeef: unix_socket:{display.rfb_socket_path}\n"
    assert tokens.stat().st_mode & 0o777 == 0o600
    assert Path(display.xauthority_path).stat().st_size == 2 + 2 + 3 + 20 + 18
    assert display.environment == {"DISPLAY": DISPLAY_NAME, "XAUTHORITY": display.xauthority_path}
    assert X_SOCKET_PATH == "/tmp/.X11-unix/X1"


def test_prepare_refuses_a_plan_without_the_contained_display(tmp_path: Path) -> None:
    plan = RuntimePlan.from_mapping(runtime_document(tmp_path)).with_display(DisplayPlan.host_x11())
    with pytest.raises(RuntimePlanError, match="does not select the contained display"):
        prepare_contained_display(plan, str(tmp_path), lambda command: command)


def test_entrypoint_starts_display_infrastructure_before_the_surface(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, captured_supervisor: type[SupervisorCapture]
) -> None:
    monkeypatch.setattr("devcapsule.container_runtime.display.os.geteuid", lambda: 1000)
    monkeypatch.delenv("DISPLAY", raising=False)
    plan = RuntimePlan.from_mapping(contained_document(tmp_path))

    assert run(plan) == 42

    (supervisor,) = captured_supervisor.instances
    names = [child.name for child in supervisor.children]
    assert names == [XVNC_CHILD, WINDOW_MANAGER_CHILD, NOVNC_CHILD, "jetbrains"]
    assert [child.foreground for child in supervisor.children] == [False, False, False, True]
    import os

    assert os.environ["DISPLAY"] == DISPLAY_NAME
    assert os.environ["XAUTHORITY"].startswith("/tmp/devcapsule-runtime-1000/display/")


def test_entrypoint_declares_no_display_for_passthrough_or_headless(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, captured_supervisor: type[SupervisorCapture]
) -> None:
    passthrough = RuntimePlan.from_mapping(runtime_document(tmp_path)).with_display(DisplayPlan.host_x11())
    assert run(passthrough) == 42
    contained = RuntimePlan.from_mapping(contained_document(tmp_path))
    assert run(contained, job=("pytest",)) == 42

    first, second = captured_supervisor.instances
    assert [child.name for child in first.children] == ["jetbrains"]
    assert [child.name for child in second.children] == ["job"]
