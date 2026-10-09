"""Records: the raw file route, the records pages, and the vendored renderers."""

from __future__ import annotations

import hashlib
from pathlib import Path
import re

import pytest

from conftest import with_token
from devcapsule_webconsole.app import raw_content_type
from devcapsule_webconsole.settings import Settings

STATIC = Path(Settings.__module__ and __import__("devcapsule_webconsole").__file__).parent / "static"


@pytest.mark.parametrize("path, expected", [
    ("docs/guide.md", "text/markdown; charset=utf-8"),
    ("README", "application/octet-stream"),
    ("notes.txt", "text/plain; charset=utf-8"),
    ("config.toml", "text/plain; charset=utf-8"),
    ("data.json", "application/json"),
    ("diagram.svg", "image/svg+xml"),
    ("shot.PNG", "image/png"),
    ("clip.webm", "video/webm"),
    ("page.html", "text/plain; charset=utf-8"),
    ("script.js", "text/plain; charset=utf-8"),
    ("archive.tar.gz", "application/octet-stream"),
    ("dir.v2/file", "application/octet-stream"),
])
def test_raw_content_types_never_let_a_project_file_run_as_a_page(path, expected):
    assert raw_content_type(path) == expected


def test_the_raw_route_serves_bytes_inside_the_project_and_refuses_outside(client, project: Path):
    assert client.get("/api/project/raw", params={"path": "image.bin"}).status_code == 403  # no token yet
    client = with_token(client)
    image = client.get("/api/project/raw", params={"path": "image.bin"})
    assert image.status_code == 200
    assert image.content == b"\xff\xfe\x00binary"
    assert image.headers["content-type"] == "application/octet-stream"
    (project / "docs" / "shot.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 8)
    shot = client.get("/api/project/raw", params={"path": "docs/shot.png"})
    assert shot.status_code == 200 and shot.headers["content-type"] == "image/png"
    (project / "docs" / "page.html").write_text("<script>alert(1)</script>", encoding="utf-8")
    page = client.get("/api/project/raw", params={"path": "docs/page.html"})
    assert page.status_code == 200 and page.headers["content-type"] == "text/plain; charset=utf-8"
    guide = client.get("/api/project/raw", params={"path": "docs/guide.md"})
    assert guide.status_code == 200 and guide.headers["content-type"] == "text/markdown; charset=utf-8"
    assert client.get("/api/project/raw", params={"path": "../outside.txt"}).status_code == 403
    assert client.get("/api/project/raw", params={"path": "escape.md"}).status_code == 403
    assert client.get("/api/project/raw", params={"path": "/etc/hostname"}).status_code == 403
    assert client.get("/api/project/raw", params={"path": "docs/missing.png"}).status_code == 404
    assert client.get("/api/project/raw", params={"path": "docs"}).status_code == 404
    assert client.get("/api/project/raw").status_code == 422


@pytest.mark.parametrize("route", ["/records", "/records/", "/records/index.md", "/records/engineering-docs/wip/x/CURRENT-STATUS.md",
                                   "/records/docs/guide.md#section"])
def test_every_records_path_serves_the_records_page(client, route):
    assert client.get(route).status_code == 403
    response = with_token(client).get(route)
    assert response.status_code == 200
    assert 'data-page="records"' in response.text
    assert '<script src="/static/vendor/markdown-it-15.0.2.umd.min.js" defer></script>' in response.text
    assert '<script src="/static/vendor/viz-3.31.0.global.js" defer></script>' in response.text


def test_the_navigation_and_the_home_page_name_records(client):
    home = with_token(client).get("/").text
    assert home.count('href="/records"') == 2  # navigation and card
    for route in ("/configuration", "/versions", "/project", "/processes", "/records"):
        assert 'href="/records"' in with_token(client).get(route).text


def test_vendored_renderers_match_their_recorded_digests():
    """VENDORED.md is the provenance record; the files must be the ones it names."""
    table = (STATIC / "vendor" / "VENDORED.md").read_text(encoding="utf-8")
    rows = [line for line in table.splitlines() if line.startswith("| `")]
    assert len(rows) == 2
    for row in rows:
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        name = cells[0].strip("`")
        digest = cells[-1].strip("`")
        assert re.fullmatch(r"[0-9a-f]{64}", digest), row
        assert hashlib.sha256((STATIC / "vendor" / name).read_bytes()).hexdigest() == digest, name
    served = with_token_free_listing()
    assert {"markdown-it-15.0.2.umd.min.js", "viz-3.31.0.global.js", "VENDORED.md", "markdown-it-LICENSE"} <= served


def with_token_free_listing() -> set[str]:
    return {path.name for path in (STATIC / "vendor").iterdir()}


def test_vendored_files_are_served_behind_the_token(client):
    assert client.get("/static/vendor/viz-3.31.0.global.js").status_code == 403
    response = with_token(client).get("/static/vendor/markdown-it-15.0.2.umd.min.js")
    assert response.status_code == 200
    assert response.text.startswith("/*! markdown-it") or "markdownit" in response.text[:4000]
