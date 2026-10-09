"""The FastAPI application: pages, their JSON, and the project-file reader.

Every route is ``GET``. The pages are static files that fetch their facts
from the ``/api`` routes, which run the runtime CLI. The token gate wraps the
whole application, static files included.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Query, Request
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from . import __version__
from .cli import CommandError, RuntimeCli
from .security import PathRefused, TokenGate, confine
from .settings import Settings

PAGES = {
    "/": "index.html",
    "/configuration": "configuration.html",
    "/versions": "versions.html",
    "/project": "project.html",
}


def create_app(settings: Settings) -> FastAPI:
    app = FastAPI(title="DevCapsule web console", version=__version__, docs_url=None, redoc_url=None, openapi_url=None)
    app.state.settings = settings
    cli = RuntimeCli(settings.cli, settings.project)

    def document(read: Any) -> JSONResponse:
        try:
            return JSONResponse(read())
        except CommandError as error:
            return JSONResponse(error.to_document(), status_code=502)

    for route, page in PAGES.items():
        app.add_api_route(route, _page(settings, page), methods=["GET"], include_in_schema=False)

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

    @app.get("/api/project/file")
    def project_file(path: str = Query(...)) -> PlainTextResponse:
        try:
            resolved = confine(settings.project, path)
        except PathRefused as error:
            return PlainTextResponse(str(error) + "\n", status_code=403)
        if not resolved.is_file():
            return PlainTextResponse(f"no file at {path!r} in the project\n", status_code=404)
        try:
            text = resolved.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return PlainTextResponse(f"{path!r} is not a UTF-8 text file\n", status_code=415)
        return PlainTextResponse(text)

    app.mount("/static", StaticFiles(directory=str(settings.static_root)), name="static")
    app.add_middleware(TokenGate, token=settings.token)
    return app


def _page(settings: Settings, name: str) -> Any:
    def page(request: Request) -> FileResponse:
        return FileResponse(settings.static_root / name, media_type="text/html")

    return page


def compose_identity(information: Any, versions: Any) -> dict[str, Any]:
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
