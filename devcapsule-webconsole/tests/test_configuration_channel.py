"""The configuration channel: the launcher's listing at launch, the console's requests, the launcher's results."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from conftest import CONFIGURATION, TOKEN, with_token
from devcapsule_webconsole.configuration import (
    ChannelError, ConfigurationChannel, is_widening, parse_command, suggested_arguments,
)
from fastapi.testclient import TestClient

from devcapsule_webconsole.app import create_app
from devcapsule_webconsole.settings import Settings, settings_from_arguments

LISTING = {"format": 1, "at": "2026-10-24T10:00:00+00:00", "listing": {
    **CONFIGURATION, "schema-version": 2,
    "rows": [{"kind": "ide", "name": "ide", "effective": "-", "source": "lock (recommended)",
              "pending": "choose your IDE", "command": "devcapsule project --path '/home/dev/sample' config ide IDE"},
             {"kind": "access", "name": "network", "effective": "bridge", "source": "default", "pending": "",
              "command": ""}],
    "pending": ["ide"], "notes": []}}


@pytest.fixture
def channel(tmp_path: Path) -> Path:
    directory = tmp_path / "channel"
    directory.mkdir()
    (directory / "listing.json").write_text(json.dumps(LISTING), encoding="utf-8")
    return directory


@pytest.fixture
def channel_client(project: Path, fake_cli, channel: Path):
    settings = Settings(project=project, cli=fake_cli[0], token=TOKEN, decisions=project.parent / "decisions",
                        configuration=channel)
    with TestClient(create_app(settings)) as client:
        yield with_token(client)


def test_commands_are_parsed_and_checked_against_the_launchers_vocabulary() -> None:
    assert parse_command("ide python-ide") == ["ide", "python-ide"]
    assert parse_command("config env set POSTGRES_HOST 'db one'") == ["env", "set", "POSTGRES_HOST", "db one"]
    for text, reason in (("", "names no command"), ("show", "not a request the launcher takes"),
                         ("ide --path /x", "--path"), ("ide 'unterminated", "does not parse"),
                         ("ide a\x01b", "control characters"), ("x" * 20000, "too long")):
        with pytest.raises(ChannelError, match=reason):
            parse_command(text)
    assert is_widening(["authorize", "network", "host"]) and is_widening(["trust", "accept", "claude-code"])
    assert not is_widening(["deny", "network"]) and not is_widening(["trust", "withdraw", "x"])
    assert suggested_arguments("devcapsule project --path '/home/dev/my project' config authorize base-image default") == "authorize base-image default"
    assert suggested_arguments("not a request") == ""


def test_requests_are_complete_when_visible_and_numbered(channel: Path) -> None:
    store = ConfigurationChannel(channel)
    assert store.available and store.listing() == {"at": LISTING["at"], "listing": LISTING["listing"]}
    first = store.write_request(["ide", "python-ide"])
    second = store.write_request(["authorize", "network", "host"])
    assert first.id.startswith("000001-ide-") and second.id.startswith("000002-authorize-")
    assert not [p for p in channel.iterdir() if p.name.endswith(".tmp")]
    written = json.loads((channel / f"{first.id}.request.json").read_text())
    assert written == {"format": 1, "requested": first.requested, "arguments": ["ide", "python-ide"]}
    (channel / f"{first.id}.result.json").write_text(json.dumps(
        {"format": 1, "status": "recorded", "text": "Your IDE for this checkout: python-ide", "at": "t"}))
    listed = store.requests()
    assert [item.id for item in listed] == [first.id, second.id]
    assert listed[0].result == {"format": 1, "status": "recorded", "text": "Your IDE for this checkout: python-ide", "at": "t"}
    assert listed[1].result is None and listed[1].to_mapping()["widening"] is True
    assert listed[0].to_mapping()["command"] == "config ide python-ide"
    # A planted symbolic link is never followed; a name outside the contract is ignored.
    (channel / "000003-x.request.json").symlink_to(channel / "listing.json")
    (channel / "notes.txt").write_text("x")
    assert [item.id for item in store.requests()] == [first.id, second.id, "000003-x"]
    assert store.requests()[2].arguments == ()


def test_write_refuses_without_the_mounted_channel(tmp_path: Path) -> None:
    with pytest.raises(ChannelError, match="did not mount"):
        ConfigurationChannel(tmp_path / "absent").write_request(["ide", "python-ide"])
    assert not ConfigurationChannel(tmp_path / "absent").available
    assert ConfigurationChannel(tmp_path / "absent").requests() == []


def test_the_configuration_route_marks_pending_rows_with_their_request(channel_client: TestClient) -> None:
    document = channel_client.get("/api/configuration").json()
    assert document["channel"] is True
    assert document["rows"][0].get("request") is None  # the fixture's rows pend nothing


def test_request_routes_write_and_list(channel_client: TestClient, channel: Path) -> None:
    assert channel_client.get("/api/configuration/requests").json() == {"channel": True, "requests": []}
    refused = channel_client.post("/api/configuration/requests", json={"command": "ide python-ide"},
                                  headers={"Origin": "http://evil.example"})
    assert refused.status_code == 403 and not list(channel.glob("*.request.json"))
    bad = channel_client.post("/api/configuration/requests", json={"command": "show"}, headers={"Origin": "http://testserver"})
    assert bad.status_code == 422 and "read-only" not in bad.text and "not a request" in bad.text
    shape = channel_client.post("/api/configuration/requests", json={"cmd": 1}, headers={"Origin": "http://testserver"})
    assert shape.status_code == 422
    created = channel_client.post("/api/configuration/requests", json={"command": "config ide python-ide"},
                                  headers={"Origin": "http://testserver"})
    assert created.status_code == 201
    identifier = created.json()["request"]["id"]
    assert identifier.startswith("000001-ide-")
    assert (channel / f"{identifier}.request.json").is_file()
    (channel / f"{identifier}.result.json").write_text(json.dumps({"format": 1, "status": "recorded", "text": "ok", "at": "t"}))
    listed = channel_client.get("/api/configuration/requests").json()["requests"]
    assert listed[0]["result"]["status"] == "recorded" and listed[0]["command"] == "config ide python-ide"


def test_settings_name_the_channel(project: Path, tmp_path: Path) -> None:
    token = tmp_path / "token"
    token.write_text(TOKEN)
    settings = settings_from_arguments(["--project", str(project), "--token-file", str(token)], {})
    assert settings.configuration == Path("/run/devcapsule-configuration")
    settings = settings_from_arguments(["--project", str(project), "--token-file", str(token)],
                                       {"DEVCAPSULE_CONSOLE_CONFIGURATION": str(tmp_path / "c")})
    assert settings.configuration == tmp_path / "c"
    settings = settings_from_arguments(["--project", str(project), "--token-file", str(token), "--configuration", str(tmp_path / "d")], {})
    assert settings.configuration == tmp_path / "d"


@pytest.mark.parametrize("kind", ["link", "fifo", "huge", "partial", "wrong-shape"])
def test_unreadable_requests_and_results_do_not_break_listing(channel_client, channel, kind):
    import os
    request = ConfigurationChannel(channel).write_request(["ide", "python-ide"])
    answer = channel / (request.id + ".result.json")
    bad = channel / "000002-ide.request.json"
    for path in (answer, bad):
        if kind == "link":
            path.symlink_to(channel / "listing.json")
        elif kind == "fifo":
            os.mkfifo(path)
        elif kind == "huge":
            path.write_bytes(b" " * (256 * 1024 + 1))
        elif kind == "partial":
            path.write_text('{"format":')
        else:
            path.write_text('{"format":1,"arguments":{},"status":[]}')
    response = channel_client.get("/api/configuration/requests")
    assert response.status_code == 200
    rows = response.json()["requests"]
    assert rows[0]["result"]["status"] == "unknown" and rows[0]["result"]["text"]
    assert rows[1]["arguments"] == [] and rows[1]["widening"] is False


def test_restart_and_concurrent_writers_never_replace_requests(channel, monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    import threading
    store = ConfigurationChannel(channel)
    first = store.write_request(["ide", "python-ide"])
    second = ConfigurationChannel(channel).write_request(["ide", "frontend-ide"])
    assert first.id != second.id and second.id.startswith("000002-")
    # Both processes observe the same directory before publishing.
    barrier = threading.Barrier(2)
    def stale_listing(self):
        barrier.wait(timeout=5)
        return []
    with monkeypatch.context() as patcher:
        patcher.setattr(ConfigurationChannel, "requests", stale_listing)
        with ThreadPoolExecutor(2) as pool:
            written = list(pool.map(lambda _: store.write_request(["deny", "network"]), range(2)))
    assert written[0].id != written[1].id
    assert len(store.requests()) == 4
    assert json.loads((channel / (first.id + ".request.json")).read_text())["arguments"] == ["ide", "python-ide"]


def test_request_is_complete_before_publication(channel, monkeypatch):
    import os
    original = os.link
    observed = []
    def publish(source, destination):
        assert not destination.exists()
        observed.append(json.loads(source.read_text())["arguments"])
        original(source, destination)
    monkeypatch.setattr(os, "link", publish)
    ConfigurationChannel(channel).write_request(["env", "set", "X", "one two"])
    assert observed == [["env", "set", "X", "one two"]]
    assert not list(channel.glob("*.tmp"))


def test_existing_directory_without_listing_cannot_accept_requests(channel_client, channel):
    (channel / "listing.json").unlink()
    response = channel_client.post("/api/configuration/requests", json={"command": "ide python-ide"},
                                   headers={"Origin": "http://testserver"})
    assert response.status_code == 422 and "did not mount" in response.text
    assert not list(channel.glob("*.request.json"))


@pytest.mark.parametrize("body", [[], None, 1, "ide python-ide", {"command": []}, {"command": "env set X ''"}, {"command": "ide \ud800"}])
def test_json_that_is_not_a_request_is_refused(channel_client, channel, body):
    response = channel_client.post("/api/configuration/requests", content=json.dumps(body),
                                   headers={"Origin": "http://testserver"})
    assert response.status_code == 422 and not list(channel.glob("*.request.json"))


def test_route_requires_token_and_origin_and_bounds_body(channel_client, channel):
    channel_client.cookies.clear()
    channel_client.headers.pop("x-devcapsule-token", None)
    response = channel_client.post("/api/configuration/requests", json={"command": "deny network"},
                                   headers={"Origin": "http://testserver"})
    assert response.status_code == 403 and "token" in response.text
    with_token(channel_client)
    response = channel_client.post("/api/configuration/requests", json={"command": "deny network"})
    assert response.status_code == 403
    response = channel_client.post("/api/configuration/requests", content=b"x" * (16 * 1024 + 1),
                                   headers={"Origin": "http://testserver"})
    assert response.status_code == 413 and not list(channel.glob("*.request.json"))


@pytest.mark.parametrize("tokens", [["forget", "network"], ["env", "set", "SECRET", "--from-h"]])
def test_console_explains_indirect_widening(tokens):
    assert is_widening(tokens)


def test_configuration_script_behaviour():
    import shutil
    import subprocess
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node is a development-only script test dependency")
    subprocess.run([node, str(Path(__file__).with_name("configuration-script.cjs"))], check=True)


def test_explicit_secure_authorization_is_not_labelled_as_widening():
    assert not is_widening(["authorize", "network", "bridge"])
    assert is_widening(["authorize", "network", "host"])
    assert is_widening(["authorize", "base-image", "default"])


def test_sequence_exhaustion_is_an_explained_refusal(channel_client, channel):
    (channel / "999999-ide.request.json").write_text(json.dumps({"format": 1, "arguments": ["ide", "python-ide"]}))
    response = channel_client.post("/api/configuration/requests", json={"command": "deny network"},
                                   headers={"Origin": "http://testserver"})
    assert response.status_code == 422 and "exhausted" in response.text
    assert len(list(channel.glob("*.request.json"))) == 1
