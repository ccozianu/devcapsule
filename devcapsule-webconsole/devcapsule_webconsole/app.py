"""The FastAPI application: pages, their JSON, the project-file readers, the monitor.

Every route is ``GET``. The pages are static files that fetch their facts
from the ``/api`` routes, which run the runtime CLI, read the capsule's
processes and cgroup, or read a file inside the project mount. The records
page renders any markdown file of the project in the browser. The token
gate wraps the whole application, static files included.
"""

from __future__ import annotations

import mimetypes
from typing import Any, Callable

from fastapi import FastAPI, Query, Response
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from . import __version__
from . import monitor
from .cli import CommandError, RuntimeCli
from .security import PathRefused, TokenGate, read_project_bytes, read_project_text
from .settings import Settings

PAGES = {
    "/": "index.html",
    "/configuration": "configuration.html",
    "/versions": "versions.html",
    "/project": "project.html",
    "/processes": "processes.html",
    "/records": "records.html",
}
# What a raw project file is served as, by extension. Markdown is text so a
# browser shows it; anything unknown is bytes a browser offers to save.
# SVG can contain active content. The raw route isolates every response below.
RAW_CONTENT_TYPES = {
    ".md": "text/markdown; charset=utf-8",
    ".txt": "text/plain; charset=utf-8",
    ".toml": "text/plain; charset=utf-8",
    ".json": "application/json",
    ".svg": "image/svg+xml",
}


def create_app(settings: Settings) -> FastAPI:
    app = FastAPI(title="DevCapsule web console", version=__version__, docs_url=None, redoc_url=None, openapi_url=None)
    app.state.settings = settings
    cli = RuntimeCli(settings.cli, settings.project)

    def document(read: Callable[[], dict[str, Any]]) -> JSONResponse:
        try:
            return JSONResponse(read())
        except CommandError as error:
            return JSONResponse(error.to_document(), status_code=502)

    for route, page in PAGES.items():
        app.add_api_route(route, _page(settings, page), methods=["GET"], include_in_schema=False)
    # One page for every record: the script reads the path from the URL.
    app.add_api_route("/records/{record:path}", _page(settings, "records.html"), methods=["GET"], include_in_schema=False)

    @app.get("/api/identity")
    def identity() -> JSONResponse:
        return document(lambda: compose_identity(cli.information(), cli.versions()))

    @app.get("/api/configuration")
    def configuration() -> JSONResponse:
        return document(cli.configuration)

    @app.get("/api/versions")
    def versions() -> JSONResponse:
        return document(cli.versions)

    @app.get("/api/project")
    def project() -> JSONResponse:
        return document(cli.information)

    @app.get("/api/processes")
    def processes() -> JSONResponse:
        return JSONResponse(monitor.processes())

    @app.get("/api/resources")
    def resources() -> JSONResponse:
        return JSONResponse(monitor.resources())

    @app.get("/api/project/file")
    def project_file(path: str = Query(...)) -> PlainTextResponse:
        try:
            text = read_project_text(settings.project, path)
        except PathRefused as error:
            return PlainTextResponse(str(error) + "\n", status_code=403)
        except FileNotFoundError:
            return PlainTextResponse(f"no file at {path!r} in the project\n", status_code=404)
        except UnicodeDecodeError:
            return PlainTextResponse(f"{path!r} is not a UTF-8 text file\n", status_code=415)
        except OSError:
            return PlainTextResponse(f"cannot read {path!r} in the project\n", status_code=403)
        return PlainTextResponse(text)

    @app.get("/api/project/raw")
    def project_raw(path: str = Query(...)) -> Response:
        """A project file as bytes, for images and non-markdown links in records."""
        try:
            content = read_project_bytes(settings.project, path)
        except PathRefused as error:
            return PlainTextResponse(str(error) + "\n", status_code=403)
        except FileNotFoundError:
            return PlainTextResponse(f"no file at {path!r} in the project\n", status_code=404)
        except OSError:
            return PlainTextResponse(f"cannot read {path!r} in the project\n", status_code=403)
        # An SVG is an image when embedded, but an active document when opened.
        # Isolate raw documents from the console origin and forbid their code,
        # subresources and forms. nosniff also prevents use as a script or style.
        return Response(content, media_type=raw_content_type(path), headers={
            "Content-Security-Policy": "sandbox; default-src 'none'; style-src 'unsafe-inline'",
            "X-Content-Type-Options": "nosniff",
        })

    app.mount("/static", StaticFiles(directory=str(settings.static_root)), name="static")
    app.add_middleware(TokenGate, token=settings.token)
    return app


def _page(settings: Settings, name: str) -> Callable[[], FileResponse]:
    def page() -> FileResponse:
        return FileResponse(settings.static_root / name, media_type="text/html")

    return page


def compose_identity(information: dict[str, Any], versions: dict[str, Any]) -> dict[str, Any]:
    """The home page's identity block from ``project info`` and ``versions show``.

    The version set is the running one inside a capsule and the selected one
    on a host; ``versions show`` names which through its ``context``.
    """
    version_set = versions.get("running") if versions.get("context") == "running capsule" else versions.get("selected")
    return {
        "context": information.get("context"),
        "project": information.get("project", {}),
        "checkout": information.get("checkout", {}),
        "base": information.get("base", {}),
        "version-set": {key: version_set.get(key) for key in ("identity", "origin")} if version_set else None,
        "console-version": __version__,
    }


def raw_content_type(path: str) -> str:
    """The media type for a raw project file, isolated by the raw route's CSP.

    HTML is served as plain text. SVG keeps its image type for illustrations;
    the response sandbox prevents an opened SVG from using the console origin.
    """
    suffix = "." + path.rsplit(".", 1)[-1].lower() if "." in path.rsplit("/", 1)[-1] else ""
    if suffix in RAW_CONTENT_TYPES:
        return RAW_CONTENT_TYPES[suffix]
    guessed, _ = mimetypes.guess_type(path)
    if guessed and (guessed.startswith("image/") or guessed.startswith("video/") or guessed.startswith("audio/")):
        return guessed
    if guessed and guessed.startswith("text/"):
        return "text/plain; charset=utf-8"
    return "application/octet-stream"
