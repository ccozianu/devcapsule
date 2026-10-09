"""The pages and their documents, read from the runtime CLI."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from conftest import CONFIGURATION, INFORMATION, VERSIONS, invocations, with_token
from devcapsule_webconsole import __version__
from devcapsule_webconsole.app import compose_identity
from devcapsule_webconsole.cli import CommandError, RuntimeCli


@pytest.mark.parametrize("route, title", [("/", "This capsule"), ("/configuration", "Configuration"),
                                          ("/versions", "Versions"), ("/project", "Project")])
def test_each_page_is_html_that_loads_the_console_script(client, route, title):
    response = with_token(client).get(route)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert f"<h1>{title}</h1>" in response.text
    assert '<script src="/static/console.js" defer></script>' in response.text
    assert f'data-page="{route.strip("/") or "home"}"' in response.text


@pytest.mark.parametrize("route, expected, command", [
    ("/api/configuration", CONFIGURATION, ["config", "list"]),
    ("/api/versions", VERSIONS, ["versions", "show"]),
    ("/api/project", INFORMATION, ["info"]),
])
def test_each_document_is_the_cli_output_for_the_project(client, fake_cli, project: Path, route, expected, command):
    _, log = fake_cli
    response = with_token(client).get(route)
    assert response.status_code == 200
    assert response.json() == expected
    assert invocations(log) == [["project", "--path", str(project), *command, "--json"]]


def test_the_identity_composes_information_and_versions(client, fake_cli):
    _, log = fake_cli
    response = with_token(client).get("/api/identity")
    assert response.status_code == 200
    assert response.json() == {
        "context": "host selection (next launch)",
        "project": INFORMATION["project"], "checkout": INFORMATION["checkout"], "base": INFORMATION["base"],
        "version-set": {"identity": "set-aaaa", "origin": "project recommendation"},
        "console-version": __version__,
    }
    assert [call[3:] for call in invocations(log)] == [["info", "--json"], ["versions", "show", "--json"]]


def test_the_identity_prefers_the_running_set_inside_a_capsule():
    versions = {"context": "running capsule", "running": {"identity": "run-1", "origin": "local selection", "x": 1},
                "next-launch": {"identity": "next-2", "origin": "project recommendation"}}
    identity = compose_identity({"context": "running capsule (captured at launch)"}, versions)
    assert identity["version-set"] == {"identity": "run-1", "origin": "local selection"}
    assert identity["project"] == {} and identity["checkout"] == {} and identity["base"] == {}
    assert compose_identity({}, {"context": "host selection (next launch)"})["version-set"] is None


def test_a_change_made_with_a_command_shows_after_reload(client, monkeypatch):
    client = with_token(client)
    assert client.get("/api/configuration").json()["rows"][0]["status"] == "unset-optional"
    changed = json.loads(json.dumps(CONFIGURATION))
    changed["rows"][0]["status"] = "configured"
    monkeypatch.setenv("FAKE_CLI_DOCUMENTS", json.dumps({"config list": changed}))
    assert client.get("/api/configuration").json()["rows"][0]["status"] == "configured"


def test_a_failing_cli_is_reported_as_a_bad_gateway(client, monkeypatch, project: Path):
    monkeypatch.setenv("FAKE_CLI_EXIT", "2")
    response = with_token(client).get("/api/configuration")
    assert response.status_code == 502
    body = response.json()
    assert body["error"] == "the runtime CLI exited with status 2"
    assert body["stderr"] == "devcapsule: the fixture refused\n"
    assert body["command"][-3:] == ["config", "list", "--json"]
    monkeypatch.delenv("FAKE_CLI_EXIT")
    monkeypatch.setenv("FAKE_CLI_GARBAGE", "1")
    response = with_token(client).get("/api/identity")
    assert response.status_code == 502
    assert response.json()["error"].startswith("the runtime CLI printed no JSON document")


def test_the_reader_names_an_absent_executable_and_a_timeout(project: Path, tmp_path: Path):
    absent = RuntimeCli((str(tmp_path / "no-such-devcapsule"),), project)
    with pytest.raises(CommandError) as refused:
        absent.configuration()
    assert refused.value.reason.startswith("cannot run the runtime CLI")
    assert refused.value.command == (str(tmp_path / "no-such-devcapsule"), "project", "--path", str(project),
                                     "config", "list", "--json")
    sleeper = tmp_path / "sleep.py"
    sleeper.write_text("import time; time.sleep(5)\n", encoding="utf-8")
    import sys
    slow = RuntimeCli((sys.executable, str(sleeper)), project, timeout=0.2)
    with pytest.raises(CommandError) as timed_out:
        slow.versions()
    assert timed_out.value.reason == "the runtime CLI did not answer within 0.2s"


@pytest.mark.parametrize("output", [b"\xff", b"[]", b"null", b'"text"', b'{"value": NaN}',
                                  b'{"value": Infinity}', b'{"value": 1e999}'])
def test_invalid_cli_documents_are_bad_gateways(settings, tmp_path, output):
    import sys
    from dataclasses import replace
    from fastapi.testclient import TestClient
    from devcapsule_webconsole.app import create_app

    script = tmp_path / "bad-output.py"
    script.write_text(f"import sys; sys.stdout.buffer.write({output!r})", encoding="utf-8")
    with TestClient(create_app(replace(settings, cli=(sys.executable, str(script))))) as client:
        response = with_token(client).get("/api/project")
    assert response.status_code == 502
    assert response.json()["error"].startswith("the runtime CLI printed no JSON document")


def test_invalid_stderr_does_not_hide_cli_exit_status(settings, tmp_path):
    import sys
    from dataclasses import replace
    from fastapi.testclient import TestClient
    from devcapsule_webconsole.app import create_app

    script = tmp_path / "bad-stderr.py"
    script.write_text("import sys; sys.stderr.buffer.write(b'bad \\xff'); sys.exit(7)", encoding="utf-8")
    with TestClient(create_app(replace(settings, cli=(sys.executable, str(script))))) as client:
        response = with_token(client).get("/api/project")
    assert response.status_code == 502
    assert response.json()["error"] == "the runtime CLI exited with status 7"
    assert response.json()["stderr"] == "bad \ufffd"


def test_an_unavailable_running_set_never_uses_the_next_launch():
    identity = compose_identity({}, {"context": "running capsule", "running": None,
                                     "next-launch": VERSIONS["selected"], "selected": VERSIONS["selected"]})
    assert identity["version-set"] is None


def test_the_reader_preserves_unicode_and_finite_numbers(client, monkeypatch):
    document = {"text": "caf\u00e9", "numbers": [1.25, -2.5e10, 0]}
    monkeypatch.setenv("FAKE_CLI_DOCUMENTS", json.dumps({"config list": document}, ensure_ascii=False))
    assert with_token(client).get("/api/configuration").json() == document
