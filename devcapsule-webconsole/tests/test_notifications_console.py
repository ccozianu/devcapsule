"""The notifications page and routes: the runtime CLI's listing shown, read and dismiss sent back through it."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from conftest import invocations, with_token

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
