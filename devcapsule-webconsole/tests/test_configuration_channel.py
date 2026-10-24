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
    assert (first.id, second.id) == ("000001-ide", "000002-authorize")
    assert not [p for p in channel.iterdir() if p.name.endswith(".tmp")]
    written = json.loads((channel / "000001-ide.request.json").read_text())
    assert written == {"format": 1, "requested": first.requested, "arguments": ["ide", "python-ide"]}
    (channel / "000001-ide.result.json").write_text(json.dumps(
        {"format": 1, "status": "recorded", "text": "Your IDE for this checkout: python-ide", "at": "t"}))
    listed = store.requests()
    assert [item.id for item in listed] == ["000001-ide", "000002-authorize"]
    assert listed[0].result == {"format": 1, "status": "recorded", "text": "Your IDE for this checkout: python-ide", "at": "t"}
    assert listed[1].result is None and listed[1].to_mapping()["widening"] is True
    assert listed[0].to_mapping()["command"] == "config ide python-ide"
    # A planted symbolic link is never followed; a name outside the contract is ignored.
    (channel / "000003-x.request.json").symlink_to(channel / "listing.json")
    (channel / "notes.txt").write_text("x")
    assert [item.id for item in store.requests()] == ["000001-ide", "000002-authorize", "000003-x"]
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
    assert created.status_code == 201 and created.json()["request"]["id"] == "000001-ide"
    assert (channel / "000001-ide.request.json").is_file()
    (channel / "000001-ide.result.json").write_text(json.dumps({"format": 1, "status": "recorded", "text": "ok", "at": "t"}))
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
