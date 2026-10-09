"""The token gate and the path confinement, through the application."""

from __future__ import annotations

from pathlib import Path

import pytest

from conftest import TOKEN, with_token
from devcapsule_webconsole.security import PathRefused, confine


@pytest.mark.parametrize("path", ["/", "/configuration", "/versions", "/project", "/static/console.css",
                                  "/api/identity", "/api/configuration", "/api/versions", "/api/project",
                                  "/api/project/file?path=docs/guide.md"])
def test_every_route_refuses_a_request_without_the_token(client, path):
    response = client.get(path)
    assert response.status_code == 403
    assert response.text == "devcapsule web console: missing or invalid run token\n"
    assert "set-cookie" not in response.headers


@pytest.mark.parametrize("wrong", ["", "x", TOKEN[:-1], TOKEN + "0", TOKEN.upper()])
def test_a_wrong_token_is_refused_in_every_carrier(client, wrong):
    assert client.get("/", params={"token": wrong}).status_code == 403
    assert client.get("/", headers={"X-DevCapsule-Token": wrong}).status_code == 403
    client.cookies.set("devcapsule-console-token", wrong)
    assert client.get("/").status_code == 403


def test_the_query_token_admits_and_sets_the_cookie(client):
    response = client.get("/", params={"token": TOKEN})
    assert response.status_code == 200
    cookie = response.headers["set-cookie"]
    assert cookie.startswith(f"devcapsule-console-token={TOKEN}; Path=/; HttpOnly; SameSite=Strict")
    # The client keeps the cookie; the next request carries no query token.
    assert client.get("/configuration").status_code == 200
    assert client.get("/static/console.css").status_code == 200


def test_the_header_token_admits_without_a_cookie(client):
    response = client.get("/api/configuration", headers={"X-DevCapsule-Token": TOKEN})
    assert response.status_code == 200
    assert "set-cookie" not in response.headers


def test_the_cookie_token_admits_without_a_new_cookie(client):
    response = with_token(client).get("/api/versions")
    assert response.status_code == 200
    assert "set-cookie" not in response.headers


def test_only_get_is_served(client):
    for method in ("post", "put", "delete", "patch"):
        assert getattr(with_token(client), method)("/api/configuration").status_code == 405


def test_confine_accepts_files_inside_the_project(project: Path):
    assert confine(project, "docs/guide.md") == (project / "docs" / "guide.md").resolve()
    assert confine(project, "./docs/guide.md") == (project / "docs" / "guide.md").resolve()


@pytest.mark.parametrize("requested", ["", "/etc/passwd", "../outside.txt", "docs/../../outside.txt",
                                       "docs/../docs/guide.md", "escape.md", "docs/\x00guide.md"])
def test_confine_refuses_paths_that_leave_the_project(project: Path, requested: str):
    with pytest.raises(PathRefused):
        confine(project, requested)


def test_the_file_route_serves_inside_and_refuses_outside(client, project: Path):
    client = with_token(client)
    inside = client.get("/api/project/file", params={"path": "docs/guide.md"})
    assert inside.status_code == 200
    assert inside.text == "# Guide\n\nText.\n"
    assert client.get("/api/project/file", params={"path": "../outside.txt"}).status_code == 403
    assert client.get("/api/project/file", params={"path": "escape.md"}).status_code == 403
    assert client.get("/api/project/file", params={"path": "/etc/hostname"}).status_code == 403
    assert client.get("/api/project/file", params={"path": "docs/missing.md"}).status_code == 404
    assert client.get("/api/project/file", params={"path": "docs"}).status_code == 404
    assert client.get("/api/project/file", params={"path": "image.bin"}).status_code == 415
    assert client.get("/api/project/file").status_code == 422
