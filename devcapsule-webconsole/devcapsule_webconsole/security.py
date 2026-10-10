"""The two boundaries of the console: the run token and the project mount.

Every request carries the token or is refused; the token arrives in the URL
the launcher prints and is kept in a cookie from then on. Every file the
console reads lies inside the project mount; a path that escapes it is
refused before its contents are read.
"""

from __future__ import annotations

from contextlib import ExitStack
import errno
from http.cookies import CookieError, SimpleCookie
import os
from pathlib import Path
import secrets
import stat
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
        try:
            cookies.load(headers.get("cookie", ""))
        except CookieError:
            # A malformed cookie supplies no credential; a valid header still can.
            cookies.clear()
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
    try:
        resolved = (base / candidate).resolve()
    except (OSError, RuntimeError) as error:
        raise PathRefused(f"cannot resolve path {requested!r} inside the project") from error
    if not resolved.is_relative_to(base):
        raise PathRefused(f"path {requested!r} leaves the project")
    return resolved


def read_project_text(root: Path, requested: str) -> str:
    """``read_project_bytes`` decoded as UTF-8; a ``UnicodeDecodeError`` says it is not text."""
    return read_project_bytes(root, requested).decode("utf-8")


def read_project_bytes(root: Path, requested: str) -> bytes:
    """Resolve inside the mount, then open without following replacement links.

    A pathname check alone is insufficient: an editor or agent can replace
    the file or a parent directory between resolution and open. Directory
    descriptors anchor each lookup; O_NOFOLLOW refuses a substituted symlink.
    Internal symlinks still work because confine resolves them first.
    """
    base = root.resolve()
    resolved = confine(base, requested)
    parts = resolved.relative_to(base).parts
    if not parts:
        raise FileNotFoundError(requested)
    with ExitStack() as opened:
        directory = os.open(base, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        opened.callback(os.close, directory)
        try:
            for part in parts[:-1]:
                directory = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
                opened.callback(os.close, directory)
            # Do not block if a regular file was replaced by a FIFO.
            descriptor = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
        except OSError as error:
            if error.errno in (errno.ELOOP, errno.ENOTDIR):
                raise PathRefused(f"path {requested!r} changed during the read") from error
            raise
        opened.callback(os.close, descriptor)
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise FileNotFoundError(requested)
        with os.fdopen(descriptor, "rb", closefd=False) as stream:
            return stream.read()
