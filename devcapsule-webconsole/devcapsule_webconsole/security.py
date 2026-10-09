"""The two boundaries of the console: the run token and the project mount.

Every request carries the token or is refused; the token arrives in the URL
the launcher prints and is kept in a cookie from then on. Every file the
console reads lies inside the project mount; a path that escapes it is
refused before the filesystem is touched.
"""

from __future__ import annotations

from http.cookies import SimpleCookie
from pathlib import Path
import secrets
from typing import Awaitable, Callable, MutableMapping
from urllib.parse import parse_qs

from starlette.types import ASGIApp, Message, Receive, Scope, Send

TOKEN_QUERY_PARAMETER = "token"
TOKEN_COOKIE = "devcapsule-console-token"
TOKEN_HEADER = "x-devcapsule-token"
REFUSAL_BODY = b"devcapsule web console: missing or invalid run token\n"


class TokenGate:
    """ASGI middleware: admit a request that carries the token, refuse the rest.

    A valid token in the query string is answered with the cookie, so a page
    opened from the printed URL can follow its own links. A valid cookie or
    header is accepted as is. Comparison is constant-time.
    """

    def __init__(self, app: ASGIApp, token: str) -> None:
        self.app = app
        self.token = token

    def _matches(self, candidate: str | None) -> bool:
        return candidate is not None and secrets.compare_digest(candidate.encode(), self.token.encode())

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        headers = {name.decode("latin-1").lower(): value.decode("latin-1") for name, value in scope["headers"]}
        query = parse_qs(scope.get("query_string", b"").decode("latin-1"))
        from_query = query.get(TOKEN_QUERY_PARAMETER, [None])[0]
        if self._matches(from_query):
            await self.app(scope, receive, _setting_cookie(send, self.token))
            return
        cookies = SimpleCookie()
        cookies.load(headers.get("cookie", ""))
        from_cookie = cookies[TOKEN_COOKIE].value if TOKEN_COOKIE in cookies else None
        if self._matches(from_cookie) or self._matches(headers.get(TOKEN_HEADER)):
            await self.app(scope, receive, send)
            return
        await _refuse(send)


def _setting_cookie(send: Send, token: str) -> Send:
    cookie = f"{TOKEN_COOKIE}={token}; Path=/; HttpOnly; SameSite=Strict"

    async def send_with_cookie(message: Message) -> None:
        if message["type"] == "http.response.start":
            message = {**message, "headers": [*message.get("headers", []), (b"set-cookie", cookie.encode("latin-1"))]}
        await send(message)

    return send_with_cookie


async def _refuse(send: Send) -> None:
    await send({
        "type": "http.response.start", "status": 403,
        "headers": [(b"content-type", b"text/plain; charset=utf-8"),
                    (b"content-length", str(len(REFUSAL_BODY)).encode())],
    })
    await send({"type": "http.response.body", "body": REFUSAL_BODY})


class PathRefused(ValueError):
    """The requested path does not lie inside the project mount."""


def confine(root: Path, requested: str) -> Path:
    """The file ``requested`` names inside ``root``, or ``PathRefused``.

    ``requested`` is relative, with no ``..`` component. The result is
    resolved, so a symbolic link that leaves the mount is refused too.
    """
    candidate = Path(requested)
    if not requested or candidate.is_absolute() or ".." in candidate.parts or "\x00" in requested:
        raise PathRefused(f"path {requested!r} is not a relative path inside the project")
    base = root.resolve()
    resolved = (base / candidate).resolve()
    if not resolved.is_relative_to(base):
        raise PathRefused(f"path {requested!r} leaves the project")
    return resolved
