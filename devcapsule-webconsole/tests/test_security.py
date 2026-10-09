"""The token gate and the path confinement, through the application."""

from __future__ import annotations

from pathlib import Path

import pytest

from conftest import TOKEN, invocations, with_token
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


@pytest.mark.parametrize("authenticated", [False, True])
def test_a_malformed_cookie_does_not_crash_or_hide_a_valid_header(client, authenticated):
    headers = {"Cookie": "other=value; $invalid=attribute"}
    if authenticated:
        headers["X-DevCapsule-Token"] = TOKEN
    assert client.get("/", headers=headers).status_code == (200 if authenticated else 403)


@pytest.mark.parametrize("path", ["/static/console.js", "/missing", "/openapi.json"])
def test_unlisted_paths_also_require_the_token(client, path):
    assert client.get(path).status_code == 403


def test_refusal_never_runs_the_cli(client, fake_cli):
    assert client.get("/api/identity").status_code == 403
    assert invocations(fake_cli[1]) == []


@pytest.mark.parametrize("carrier", ["query", "cookie", "header"])
def test_comparisons_use_compare_digest(client, monkeypatch, carrier):
    from devcapsule_webconsole import security
    compare = security.secrets.compare_digest
    compared = []

    def record(candidate, expected):
        compared.append((candidate, expected))
        return compare(candidate, expected)

    monkeypatch.setattr(security.secrets, "compare_digest", record)
    if carrier == "query":
        response = client.get("/", params={"token": TOKEN})
    elif carrier == "cookie":
        response = with_token(client).get("/")
    else:
        response = client.get("/", headers={"X-DevCapsule-Token": TOKEN})
    assert response.status_code == 200
    assert (TOKEN.encode(), TOKEN.encode()) in compared


def test_an_invalid_query_does_not_replace_a_valid_cookie(client):
    response = with_token(client).get("/", params={"token": "wrong"})
    assert response.status_code == 200
    assert "set-cookie" not in response.headers


def test_internal_symlinks_are_readable_but_loops_are_refused(client, project):
    (project / "inside.md").symlink_to("docs/guide.md")
    (project / "loop.md").symlink_to("loop.md")
    client = with_token(client)
    assert client.get("/api/project/file", params={"path": "inside.md"}).text == "# Guide\n\nText.\n"
    assert client.get("/api/project/file", params={"path": "loop.md"}).status_code == 403


@pytest.mark.parametrize("replace_directory", [False, True])
def test_a_symlink_swap_after_resolution_cannot_read_outside(client, project, monkeypatch, replace_directory):
    outside = project.parent / "outside"
    outside.mkdir()
    (outside / "guide.md").write_text("outside secret", encoding="utf-8")
    target = project / "docs" / "guide.md"
    resolve = Path.resolve
    swapped = False

    def resolve_then_swap(path, *args, **kwargs):
        nonlocal swapped
        resolved = resolve(path, *args, **kwargs)
        if path == target and not swapped:
            swapped = True
            if replace_directory:
                target.parent.rename(project / "old-docs")
                target.parent.symlink_to(outside, target_is_directory=True)
            else:
                target.unlink()
                target.symlink_to(outside / "guide.md")
        return resolved

    monkeypatch.setattr(Path, "resolve", resolve_then_swap)
    response = with_token(client).get("/api/project/file", params={"path": "docs/guide.md"})
    assert swapped
    assert response.status_code == 403
    assert "outside secret" not in response.text


@pytest.mark.parametrize("failure", [PermissionError("denied"), FileNotFoundError("removed")])
def test_file_read_errors_have_http_responses(client, project, monkeypatch, failure):
    import os
    original_os_open = os.open

    def fail_descriptor(path, *args, **kwargs):
        if path == "guide.md":
            raise failure
        return original_os_open(path, *args, **kwargs)

    monkeypatch.setattr(os, "open", fail_descriptor)
    response = with_token(client).get("/api/project/file", params={"path": "docs/guide.md"})
    assert response.status_code == (404 if isinstance(failure, FileNotFoundError) else 403)


def test_the_mount_itself_is_not_a_file(client):
    assert with_token(client).get("/api/project/file", params={"path": "."}).status_code == 404


def test_a_fifo_is_refused_without_waiting_for_a_writer(project):
    import os
    import subprocess
    import sys

    os.mkfifo(project / "pipe")
    # A subprocess timeout makes removal of O_NONBLOCK fail instead of hanging pytest.
    script = """
import sys
from pathlib import Path
from devcapsule_webconsole.security import read_project_text
try:
    read_project_text(Path(sys.argv[1]), "pipe")
except FileNotFoundError:
    sys.exit(0)
sys.exit(1)
"""
    result = subprocess.run([sys.executable, "-c", script, str(project)], timeout=5, capture_output=True)
    assert result.returncode == 0, result.stderr
