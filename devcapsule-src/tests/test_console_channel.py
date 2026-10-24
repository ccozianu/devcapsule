"""The console's configuration channel on the launcher's side: results, deferral, the in-capsule listing, the commands."""

from __future__ import annotations

import io
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from devcapsule import cli
from devcapsule.commands._console_channel import ChannelWatcher, handle_request, read_channel, sweep
from devcapsule.commands._run_flow import RunFlags, launch_listing_document, prepare_launch
from devcapsule.configuration.capability_commands import paths
from devcapsule.configuration.console_channel import (
    Disposition, classify, listing_document, parse_request, read_document, request_id, write_complete,
)
from devcapsule.configuration.console_requests import console_requests_path, deferred_requests
from devcapsule.configuration.file_formats import ProjectConfigurationError
from devcapsule.configuration.storage import checkout_record_paths, load_toml
from devcapsule import runtime_configuration


@pytest.fixture
def project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    for key in ("HOME", "XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_STATE_HOME"):
        monkeypatch.setenv(key, str(tmp_path / key.lower()))
    root = tmp_path / "project"
    root.mkdir()
    assert cli.main(["project", "--path", str(root), "init", "--require", "node", "--creator", "mailto:owner@example.test"]) == 0
    return root


def config(root: Path, *arguments: str) -> int:
    return cli.main(["project", "--path", str(root), "config", *arguments])


def record_path(root: Path) -> Path:
    return checkout_record_paths(load_toml(paths(root)[0]), root)[0]


def request(directory: Path, identifier: str, *arguments: str) -> Path:
    path = directory / f"{identifier}.request.json"
    write_complete(path, {"format": 1, "requested": "2026-10-24T10:00:00+00:00", "arguments": list(arguments)})
    return path


def result(directory: Path, identifier: str) -> dict:
    return read_document(directory / f"{identifier}.result.json")


@pytest.mark.parametrize("arguments, expected", [
    (["ide", "python-ide"], Disposition.APPLY), (["env", "set", "X", "1"], Disposition.APPLY),
    (["deny", "network"], Disposition.APPLY), (["trust", "withdraw", "x"], Disposition.APPLY),
    (["docker-args", "clear"], Disposition.APPLY),
    (["authorize", "network", "host"], Disposition.DEFER), (["trust", "accept", "x"], Disposition.DEFER),
    (["bind", "x", "y"], Disposition.DEFER), (["docker-args", "set", "--privileged"], Disposition.DEFER),
    (["show"], Disposition.REFUSE), (["env", "list"], Disposition.REFUSE), (["default", "memory", "8G"], Disposition.REFUSE),
    (["require", "tool", "x"], Disposition.REFUSE), (["run"], Disposition.REFUSE), ([], Disposition.REFUSE),
])
def test_classification(arguments: list[str], expected: Disposition) -> None:
    disposition, reason = classify(arguments)
    assert disposition is expected and bool(reason) == (expected is Disposition.REFUSE)


def test_request_documents_are_validated(tmp_path: Path) -> None:
    assert request_id(Path("000001-ide.request.json")) == "000001-ide"
    for name in ("x.json", "1-ide.request.json", "000001-Ide.request.json"):
        with pytest.raises(ProjectConfigurationError):
            request_id(Path(name))
    assert parse_request({"format": 1, "arguments": ["ide", "x"]}) == ["ide", "x"]
    documents: list[object] = [{"format": 2, "arguments": ["ide"]}, {"format": 1, "arguments": []}, {"format": 1, "arguments": ["a\nb"]},
                               {"format": 1, "arguments": ["ide", "--path", "/x"]}, {"format": 1, "arguments": ["x" * 5000]}, []]
    for document in documents:
        with pytest.raises(ProjectConfigurationError):
            parse_request(document)
    (tmp_path / "link.json").symlink_to(tmp_path / "missing")
    with pytest.raises(ProjectConfigurationError, match="cannot open"):
        read_document(tmp_path / "link.json")
    big = tmp_path / "big.json"
    big.write_text("[" + "1," * 200000 + "1]")
    with pytest.raises(ProjectConfigurationError, match="larger than"):
        read_document(big)
    path = write_complete(tmp_path / "doc.json", {"a": 1})
    assert read_document(path) == {"a": 1} and not list(tmp_path.glob(".doc.json.*"))


def test_an_applied_request_runs_the_config_command_and_reports_its_output(project: Path, tmp_path: Path) -> None:
    channel = tmp_path / "channel"
    channel.mkdir()
    request(channel, "000001-ide", "ide", "python-ide")
    request(channel, "000002-ide", "ide", "no-such-ide")
    assert sweep(channel, project, record_path(project)) == 2
    recorded = result(channel, "000001-ide")
    assert recorded["status"] == "recorded" and "python-ide" in recorded["text"]
    assert load_toml(record_path(project))["capabilities"]["selected"] == ["python-ide"]
    refused = result(channel, "000002-ide")
    assert refused["status"] == "refused" and "no-such-ide" in refused["text"]
    assert sweep(channel, project, record_path(project)) == 0  # answered requests are never run twice


def test_a_widening_is_deferred_until_confirmed_on_the_host(project: Path, tmp_path: Path, capsys) -> None:
    assert config(project, "ide", "python-ide") == 0
    assert config(project, "trust", "accept", "devcapsule-base") == 0
    channel = tmp_path / "channel"
    channel.mkdir()
    request(channel, "000001-authorize", "authorize", "network", "host")
    request(channel, "000002-ide", "ide")  # malformed: refused by the command, not by the launcher
    request(channel, "000003-show", "show")
    assert sweep(channel, project, record_path(project)) == 3
    deferred = result(channel, "000001-authorize")
    assert deferred["status"] == "deferred" and "console apply 000001-authorize" in deferred["text"]
    assert result(channel, "000003-show")["status"] == "refused"
    assert "network" not in load_toml(record_path(project)).get("authorization", {})
    kept = deferred_requests(record_path(project))
    assert [item.id for item in kept] == ["000001-authorize"] and kept[0].statement == "config authorize network host"
    assert not str(console_requests_path(record_path(project))).startswith(str(record_path(project).parent))
    capsys.readouterr()
    # The host's listing shows it, pending and soft; check does not block on it, run asks.
    assert config(project, "show") == 0
    shown = capsys.readouterr().out
    assert "000001-authorize" in shown and "confirm or discard: config authorize network host" in shown
    assert config(project, "check") == 3
    assert config(project, "console", "list") == 0
    assert "000001-authorize  asked 2026-10-24T10:00:00+00:00: config authorize network host" in capsys.readouterr().out
    prompts = io.StringIO()
    prepared = prepare_launch(project, RunFlags(), interactive=True, input_stream=io.StringIO("\n"), output_stream=prompts)
    assert "The console asked at 2026-10-24T10:00:00+00:00: config authorize network host" in prompts.getvalue()
    assert deferred_requests(record_path(project))  # kept
    prepared = prepare_launch(project, RunFlags(), interactive=False)
    assert any("000001-authorize" in note and "console apply" in note for note in prepared.notes)
    prompts = io.StringIO()
    prepare_launch(project, RunFlags(), interactive=True, input_stream=io.StringIO("a\n"), output_stream=prompts)
    assert load_toml(record_path(project))["authorization"]["network"]["value"] == "host"
    assert deferred_requests(record_path(project)) == []
    request(channel, "000004-bind", "bind", "x", "y")
    sweep(channel, project, record_path(project))
    assert config(project, "console", "discard", "000004-bind") == 0
    assert deferred_requests(record_path(project)) == []
    assert config(project, "console", "discard", "000004-bind") == 2
    assert config(project, "console", "apply", "000009-x") == 2


def test_console_apply_runs_the_command_and_forgets_the_request(project: Path, tmp_path: Path, capsys) -> None:
    channel = tmp_path / "channel"
    channel.mkdir()
    request(channel, "000001-authorize", "authorize", "network", "host")
    sweep(channel, project, record_path(project))
    assert config(project, "console", "apply", "000001-authorize") == 0
    out = capsys.readouterr().out
    assert "Authorized network for this checkout: host" in out and "Applied and forgot" in out
    assert deferred_requests(record_path(project)) == []
    request(channel, "000002-authorize", "authorize", "quantum", "x")
    sweep(channel, project, record_path(project))
    assert config(project, "console", "apply", "000002-authorize") == 2
    assert [item.id for item in deferred_requests(record_path(project))] == ["000002-authorize"]  # kept after a refusal


def test_the_watcher_answers_while_running_and_once_more_on_stop(project: Path, tmp_path: Path) -> None:
    channel = tmp_path / "channel"
    channel.mkdir()
    watcher = ChannelWatcher(channel, project, record_path(project), interval=0.05)
    watcher.start()
    request(channel, "000001-deny", "deny", "network")
    for _ in range(200):
        if (channel / "000001-deny.result.json").exists():
            break
        import time
        time.sleep(0.05)
    assert result(channel, "000001-deny")["status"] == "recorded"
    watcher.stop()
    request(channel, "000002-forget", "forget", "network")
    assert sweep(channel, project, record_path(project)) == 1


def test_inside_a_capsule_show_prints_the_launch_listing_and_the_requests(project: Path, tmp_path: Path, monkeypatch, capsys) -> None:
    assert config(project, "ide", "python-ide") == 0
    assert config(project, "trust", "accept", "devcapsule-base") == 0
    prepared = prepare_launch(project, RunFlags(), interactive=False)
    listing = launch_listing_document(prepared.selected)
    assert listing["context"] == "at launch" and listing["checkout"]["name"] == "default"
    assert any(row["kind"] == "ide" and row["name"] == "python-ide" for row in listing["rows"])
    channel = tmp_path / "channel"
    channel.mkdir()
    write_complete(channel / "listing.json", listing_document(listing, "2026-10-24T12:00:00+00:00"))
    request(channel, "000001-ide", "ide", "frontend-ide")
    write_complete(channel / "000001-ide.result.json", {"format": 1, "status": "recorded", "text": "done", "at": "t"})
    request(channel, "000002-authorize", "authorize", "network", "host")
    view = read_channel(channel)
    assert view is not None and view.at == "2026-10-24T12:00:00+00:00" and len(view.requests) == 2
    assert view.requests[1]["result"] is None
    # The in-capsule command reads the channel through the runtime context.
    monkeypatch.setattr(runtime_configuration, "CHANNEL_PATH", channel)
    context = runtime_configuration.RuntimeConfiguration({"format": 1, "project": listing["project"], "launcher-root": str(project),
                                                          "runtime-root": "/workspace/project", "checkout-file": "devcapsule.checkout.toml",
                                                          "checkout-name": "default"})
    from devcapsule.commands.project import _show_inside_capsule
    assert _show_inside_capsule(context, False) == 0
    out = capsys.readouterr().out
    assert "At launch, 2026-10-24T12:00:00+00:00:" in out and "python-ide" in out
    assert "000001-ide: config ide frontend-ide" in out and "recorded: done" in out
    assert "000002-authorize: config authorize network host" in out and "waiting for the launcher" in out
    assert "config show" in out
    assert _show_inside_capsule(context, True) == 0
    document = json.loads(capsys.readouterr().out)
    assert document["at"] == "2026-10-24T12:00:00+00:00" and len(document["console-requests"]) == 2
    assert document["rows"] == listing["rows"]
    # Without the launcher's listing, the older read-only report stays.
    monkeypatch.setattr(runtime_configuration, "CHANNEL_PATH", tmp_path / "absent")
    with patch.object(runtime_configuration.RuntimeConfiguration, "configuration_report", return_value="legacy report"):
        assert _show_inside_capsule(context, False) == 0
    assert "legacy report" in capsys.readouterr().out
