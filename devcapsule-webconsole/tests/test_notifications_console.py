"""The notifications page and routes: the runtime CLI's listing shown, read and dismiss sent back through it."""
from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from fastapi.testclient import TestClient

from conftest import TOKEN, invocations, with_token
from devcapsule_webconsole.app import create_app
from devcapsule_webconsole.cli import CommandError, RuntimeCli

LISTING = {
    "format": 1, "directory": "/home/devcapsule/.local/state/devcapsule/notifications",
    "decisions": "/home/devcapsule/.local/state/devcapsule/decisions", "unread": 2,
    "notifications": [
        {"format": 1, "id": "intake-pass", "kind": "decision", "title": "Intake pass", "summary": "",
         "link": "/decisions/intake-pass", "posted-by": "project-management", "posted-at": "2026-10-09T12:00:00+00:00",
         "read-at": None},
        {"format": 1, "id": "20261009t110000-abc123", "kind": "gate", "title": "Gate failed on main",
         "summary": "Two cases; see the **log**.", "link": "/records/README.md", "posted-by": "ci",
         "posted-at": "2026-10-09T11:00:00+00:00", "read-at": None},
        {"id": "broken", "kind": "", "error": "broken.json is not a JSON document"},
    ],
}
UNREAD = {**LISTING, "notifications": LISTING["notifications"][:2]}


@pytest.fixture
def listing(monkeypatch: pytest.MonkeyPatch, fake_cli) -> Path:
    _, log = fake_cli
    monkeypatch.setenv("FAKE_CLI_DOCUMENTS", json.dumps({
        "checkout notifications list": LISTING,
        "checkout notifications list --unread": UNREAD,
        "checkout notifications read 20261009t110000-abc123": {"done": True},
        "checkout notifications dismiss 20261009t110000-abc123": {"done": True},
    }))
    return log


def test_the_page_and_the_bell_are_served(client):
    page = with_token(client).get("/notifications")
    assert page.status_code == 200 and 'data-page="notifications"' in page.text and "<h1>Notifications</h1>" in page.text
    for route in ("/", "/configuration", "/versions", "/project", "/processes", "/records", "/decisions", "/notifications"):
        text = with_token(client).get(route).text
        assert '<a class="bell" href="/notifications"' in text, route
        assert '<div class="bell-menu" hidden></div>' in text, route


def test_the_listing_is_the_cli_output_for_the_checkout(client, listing, project: Path):
    client = with_token(client)
    assert client.get("/api/notifications").json() == LISTING
    assert client.get("/api/notifications?unread=1").json() == UNREAD
    assert invocations(listing) == [
        ["project", "--path", str(project), "checkout", "notifications", "list", "--json"],
        ["project", "--path", str(project), "checkout", "notifications", "list", "--unread", "--json"],
    ]


def test_listing_uses_the_same_decisions_directory_as_the_console(settings, tmp_path, monkeypatch):
    import os
    script = tmp_path / "show-environment.py"
    script.write_text('import json, os; print(json.dumps({"decisions": os.environ.get("DEVCAPSULE_CONSOLE_DECISIONS"), '
                      '"notifications": os.environ.get("DEVCAPSULE_NOTIFICATIONS")}))', encoding="utf-8")
    monkeypatch.setenv("DEVCAPSULE_CONSOLE_DECISIONS", str(tmp_path / "ambient-decisions"))
    monkeypatch.setenv("DEVCAPSULE_NOTIFICATIONS", str(tmp_path / "notifications"))
    with TestClient(create_app(replace(settings, cli=(sys.executable, str(script))))) as client:
        response = with_token(client).get("/api/notifications")
    assert response.status_code == 200
    assert response.json() == {"decisions": str(settings.decisions), "notifications": str(tmp_path / "notifications")}
    assert os.environ["DEVCAPSULE_CONSOLE_DECISIONS"] == str(tmp_path / "ambient-decisions")


def test_a_failing_cli_is_a_502_with_its_reason(client, listing, monkeypatch):
    monkeypatch.setenv("FAKE_CLI_EXIT", "1")
    response = with_token(client).get("/api/notifications")
    assert response.status_code == 502
    assert response.json()["error"] == "the runtime CLI exited with status 1"
    assert "the fixture refused" in response.json()["stderr"]


@pytest.mark.parametrize("action", ["read", "dismiss"])
def test_read_and_dismiss_go_through_the_cli_from_the_console_origin_only(client, listing, project: Path, action):
    client = with_token(client)
    origin = "http://testserver"
    done = client.post(f"/api/notifications/20261009t110000-abc123/{action}", headers={"Origin": origin})
    assert done.status_code == 200, done.text
    assert done.json() == {"id": "20261009t110000-abc123", "action": action, "output": '{"done": true}'}
    assert invocations(listing) == [["project", "--path", str(project), "checkout", "notifications", action,
                                     "20261009t110000-abc123"]]
    for headers in ({}, {"Origin": "null"}, {"Origin": "http://evil.test"}, {"Origin": origin + "/"}):
        refused = client.post(f"/api/notifications/20261009t110000-abc123/{action}", headers=headers)
        assert refused.status_code == 403, headers
    assert len(invocations(listing)) == 1  # nothing ran for the refusals
    assert client.post(f"/api/notifications/../escape/{action}", headers={"Origin": origin}).status_code in (404, 422)
    assert client.post(f"/api/notifications/Bad%20Id/{action}", headers={"Origin": origin}).status_code == 404
    assert len(invocations(listing)) == 1


def test_the_cli_refusal_is_a_422_with_its_message(client, listing, monkeypatch):
    monkeypatch.setenv("FAKE_CLI_EXIT", "2")
    response = with_token(client).post("/api/notifications/intake-pass/dismiss", headers={"Origin": "http://testserver"})
    assert response.status_code == 422
    assert response.text == "devcapsule: the fixture refused\n"


def test_tokenless_requests_are_refused(client):
    assert client.get("/api/notifications").status_code == 403
    assert client.post("/api/notifications/x/read", headers={"Origin": "http://testserver"}).status_code == 403


@pytest.mark.parametrize("action", ["read", "dismiss"])
@pytest.mark.parametrize("origins", [[], ["null"], ["http://evil.test"], ["http://testserver/"],
                                    ["http://testserver:81"], ["https://testserver"],
                                    ["http://testserver", "http://testserver"],
                                    ["http://evil.test", "http://testserver"]])
def test_cross_origin_posts_never_invoke_the_cli(client, listing, action, origins):
    # Even a known token in a form action must not bypass Origin validation.
    response = client.post(f"/api/notifications/x/{action}?token={TOKEN}",
                           headers=[("Origin", origin) for origin in origins], data={"ignored": "form"})
    assert response.status_code == 403
    assert invocations(listing) == []


@pytest.mark.parametrize("action", ["read", "dismiss"])
def test_notification_writes_require_a_token_and_post(client, listing, action):
    url = f"/api/notifications/x/{action}"
    assert client.post(url, headers={"Origin": "http://testserver"}).status_code == 403
    assert with_token(client).get(url).status_code == 405
    assert invocations(listing) == []


@pytest.mark.parametrize("notification_id", ["-option", "A", "a_b", "a%00", "a%0A", "a" * 101])
def test_notification_id_refusals_never_invoke_the_cli(client, listing, notification_id):
    response = with_token(client).post(f"/api/notifications/{notification_id}/read", headers={"Origin": "http://testserver"})
    assert response.status_code == 404
    assert invocations(listing) == []


def test_maximum_id_and_request_body_cannot_add_cli_arguments(client, listing, monkeypatch, project):
    notification_id = "9" + "a" * 98 + "-"
    monkeypatch.setenv("FAKE_CLI_DOCUMENTS", json.dumps({f"checkout notifications read {notification_id}": "done"}))
    response = with_token(client).post(f"/api/notifications/{notification_id}/read?unread=true&action=dismiss",
                                       headers={"Origin": "http://testserver"},
                                       json={"id": "other", "action": "dismiss", "arguments": ["--help"]})
    assert response.status_code == 200
    assert response.json()["id"] == notification_id and response.json()["action"] == "read"
    assert invocations(listing) == [["project", "--path", str(project), "checkout", "notifications", "read", notification_id]]


@pytest.mark.parametrize("status, stderr, expected_status, message", [
    (2, b"  denied \xff\n", 422, "denied \ufffd\n"),
    (2, b" \n", 422, "the runtime CLI refused the request\n"),
    (7, b"failed \xff", 502, "the runtime CLI exited with status 7"),
])
@pytest.mark.parametrize("action", ["read", "dismiss"])
def test_action_failures_keep_the_cli_reason(settings, tmp_path, status, stderr, expected_status, message, action):
    script = tmp_path / "refuse.py"
    script.write_text(f"import sys; sys.stderr.buffer.write({stderr!r}); sys.exit({status})", encoding="utf-8")
    with TestClient(create_app(replace(settings, cli=(sys.executable, str(script))))) as client:
        response = with_token(client).post(f"/api/notifications/x/{action}", headers={"Origin": "http://testserver"})
    assert response.status_code == expected_status
    if expected_status == 422:
        assert response.text == message
    else:
        assert response.json() == {"error": message,
                                   "command": [sys.executable, str(script), "project", "--path", str(settings.project),
                                               "checkout", "notifications", action, "x"],
                                   "stderr": "failed \ufffd"}


def test_actions_decode_plain_output_without_requiring_json(project, tmp_path):
    script = tmp_path / "done.py"
    script.write_text("import sys; sys.stdout.buffer.write(b'  read \\xff\\n')", encoding="utf-8")
    assert RuntimeCli((sys.executable, str(script)), project).act("checkout", "notifications", "read", "x") == "read \ufffd"


def test_action_start_failure_is_a_502(settings, tmp_path):
    executable = str(tmp_path / "absent")
    with TestClient(create_app(replace(settings, cli=(executable,)))) as client:
        response = with_token(client).post("/api/notifications/x/read", headers={"Origin": "http://testserver"})
    assert response.status_code == 502
    assert response.json()["error"].startswith("cannot run the runtime CLI:")
    assert response.json()["command"] == [executable, "project", "--path", str(settings.project),
                                           "checkout", "notifications", "read", "x"]


def test_action_timeout_is_a_command_error(project, tmp_path):
    script = tmp_path / "slow.py"
    script.write_text("import time; time.sleep(5)", encoding="utf-8")
    cli = RuntimeCli((sys.executable, str(script)), project, timeout=0.2)
    with pytest.raises(CommandError) as raised:
        cli.act("checkout", "notifications", "dismiss", "x")
    assert type(raised.value) is CommandError
    assert raised.value.reason == "the runtime CLI did not answer within 0.2s"
    assert raised.value.command[-4:] == ("checkout", "notifications", "dismiss", "x")


def test_notifications_script_behaviour():
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node is a development-only script test dependency")
    subprocess.run([node, str(Path(__file__).with_name("notifications-script.cjs"))], check=True)
