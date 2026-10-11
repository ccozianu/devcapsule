"""Session logs: one file per component, a WARNING baseline, a lifecycle record.

Every critical component of a DevCapsule session writes its own log file,
recognizable by name, ``devcapsule-<component>.log``, in one directory per
session that the launcher creates on the host and binds into the capsule
(see ``engineering-docs/work-orders/2026-10-08-persistent-session-diagnostics.md``).
The launcher and the supervisor are Python and log through :mod:`logging`.
A child process without a severity interface of its own (a window manager, a
panel, a bridge, an IDE's standard streams) is *teed*: the supervisor copies
its output line by line into the child's file while the console keeps seeing
it unchanged.

Two levels are in play:

- The baseline is WARNING, the equivalent of slf4j's WARN. The verbosity
  override ``DEVCAPSULE_LOG_LEVEL`` lowers it for an investigation.
- Lifecycle events (a child starts, is ready, exits, is signalled; a session
  begins and ends) are recorded at INFO whatever the baseline, through
  :func:`events_logger`, because they are what reconstructs an incident.

Writing a log must never take the session down: every failure here degrades
to the console with one line saying what was lost.
"""

from __future__ import annotations

import logging
import logging.handlers
import os
from pathlib import Path
import secrets
import shutil
import sys
import threading
import time
from typing import IO, BinaryIO, Callable, Mapping

LOG_FILE_PREFIX = "devcapsule-"
LOG_FILE_SUFFIX = ".log"
LEVEL_ENV = "DEVCAPSULE_LOG_LEVEL"
"""Verbosity override: DEBUG, INFO, WARNING or ERROR; WARNING without it."""
DIRECTORY_ENV = "DEVCAPSULE_LOG_DIR"
"""Where this session's logs live, as the launcher tells the capsule."""
DEFAULT_LEVEL = logging.WARNING
LEVEL_NAMES = ("DEBUG", "INFO", "WARNING", "ERROR")

# Size bounds. A Python component rotates its own file; a teed child's file
# is cut at the budget and the console keeps the rest. The numbers are the
# work order's proposal for review, not an owner decision.
SEGMENT_BYTES = 10 * 1024 * 1024
SEGMENTS_KEPT = 5
TEE_BUDGET_BYTES = SEGMENT_BYTES * SEGMENTS_KEPT
TEE_BUDGET_NOTICE = "[devcapsule logs: size budget reached; the rest of this output went to the console only]\n"
SESSIONS_KEPT = 20
"""How many session directories a checkout keeps; older ones are removed at launch."""

SESSION_MANIFEST = "session.json"
EVENTS_SUFFIX = ".events"

_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
_LINE_FORMAT = "%(asctime)s %(levelname)s %(name)s[%(process)d]: %(message)s"
_INSTALLED_ATTRIBUTE = "_devcapsule_installed"

Owner = tuple[int, int] | None
"""``(uid, gid)`` to give a file when the writer is root, else ``None``."""


class LogLevelError(ValueError):
    """The verbosity override names no known level."""


def log_path(directory: str | Path, component: str) -> Path:
    """The file for ``component`` under ``directory``: ``devcapsule-<component>.log``."""

    if not component or "/" in component or component != component.strip():
        raise ValueError(f"log component names must be plain words, not {component!r}")
    return Path(directory) / f"{LOG_FILE_PREFIX}{component}{LOG_FILE_SUFFIX}"


def level_from_environment(environ: Mapping[str, str] | None = None) -> int:
    """The baseline level, or the override ``DEVCAPSULE_LOG_LEVEL`` names."""

    value = (os.environ if environ is None else environ).get(LEVEL_ENV, "")
    if not value:
        return DEFAULT_LEVEL
    name = value.strip().upper()
    if name not in LEVEL_NAMES:
        raise LogLevelError(f"{LEVEL_ENV} must be one of {', '.join(LEVEL_NAMES)}, not {value!r}")
    return logging.getLevelName(name)  # type: ignore[no-any-return]


def configure(
    component: str,
    directory: str | Path | None,
    *,
    environ: Mapping[str, str] | None = None,
    owner: Owner = None,
    console: Callable[[str], None] | None = None,
) -> Path | None:
    """Route this process's logging to the console and, when given, a file.

    The console handler prints WARNING and above as ``devcapsule <component>:
    message``, the form the launcher and the supervisor have always used. The
    file handler writes every record the baseline admits with a UTC
    timestamp, rotating at :data:`SEGMENT_BYTES`. Returns the file's path, or
    ``None`` when there is no directory or the file cannot be opened, which
    is reported once on the console rather than raised.
    """

    report = console or _report
    try:
        level = level_from_environment(environ)
    except LogLevelError as error:
        level = DEFAULT_LEVEL
        report(f"devcapsule {component}: {error}; logging at WARNING")
    root = logging.getLogger()
    for handler in list(root.handlers):
        if getattr(handler, _INSTALLED_ATTRIBUTE, False):
            root.removeHandler(handler)
            handler.close()
    root.setLevel(min(level, logging.INFO))  # events pass; the baseline is applied per logger
    logging.getLogger("devcapsule").setLevel(level)

    stream = logging.StreamHandler(sys.stderr)
    stream.setLevel(logging.WARNING)
    stream.setFormatter(logging.Formatter(f"devcapsule {component}: %(message)s"))
    setattr(stream, _INSTALLED_ATTRIBUTE, True)
    root.addHandler(stream)

    if directory is None:
        return None
    path = log_path(directory, component)
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
        file = logging.handlers.RotatingFileHandler(
            path, maxBytes=SEGMENT_BYTES, backupCount=SEGMENTS_KEPT, encoding="utf-8",
        )
        own(path, owner)
    except OSError as error:
        report(f"devcapsule {component}: cannot write {path} ({error}); logging to the console only")
        return None
    formatter = logging.Formatter(_LINE_FORMAT, datefmt=_TIMESTAMP_FORMAT)
    formatter.converter = time.gmtime
    file.setFormatter(formatter)
    setattr(file, _INSTALLED_ATTRIBUTE, True)
    root.addHandler(file)
    return path


def reset() -> None:
    """Remove and close the handlers :func:`configure` installed; for tests."""

    root = logging.getLogger()
    for handler in list(root.handlers):
        if getattr(handler, _INSTALLED_ATTRIBUTE, False):
            root.removeHandler(handler)
            handler.close()
    root.setLevel(logging.WARNING)
    logging.getLogger("devcapsule").setLevel(logging.NOTSET)


def events_logger(component: str) -> logging.Logger:
    """The lifecycle record of ``component``: INFO always reaches the file.

    The baseline silences INFO for ordinary loggers. Lifecycle events are the
    exception the work order asks for; this logger carries its own level so
    they are written whatever the baseline says.
    """

    logger = logging.getLogger(f"devcapsule.{component}{EVENTS_SUFFIX}")
    logger.setLevel(logging.INFO)
    return logger


def own(path: Path, owner: Owner) -> None:
    """Give ``path`` to ``owner`` when this process is root; a no-op otherwise."""

    if owner is not None and os.geteuid() == 0:
        os.chown(path, owner[0], owner[1])


def new_session_id(now: float | None = None) -> str:
    """A session identifier that sorts by start time: ``YYYYMMDD-HHMMSS-xxxx``."""

    stamp = time.strftime("%Y%m%d-%H%M%S", time.gmtime(time.time() if now is None else now))
    return f"{stamp}-{secrets.token_hex(2)}"


def prune_sessions(root: Path, *, keep: int = SESSIONS_KEPT) -> list[str]:
    """Remove the oldest session directories under ``root`` beyond ``keep``.

    Session identifiers sort by start time, so the oldest are the first by
    name. Returns the names removed. A directory that cannot be removed is
    left alone and omitted; this is housekeeping, not a guarantee.
    """

    if keep < 1:
        raise ValueError("keep must be at least one session")
    try:
        sessions = sorted(entry.name for entry in root.iterdir() if entry.is_dir())
    except OSError:
        return []
    removed: list[str] = []
    for name in sessions[: max(0, len(sessions) - keep)]:
        try:
            shutil.rmtree(root / name)
        except OSError:
            continue
        removed.append(name)
    return removed


class Tee:
    """Copy a child's output to its log file and onward to the console.

    Reads ``source`` (the child's combined stdout and stderr) line by line on
    a daemon thread. Each line goes unchanged to ``passthrough`` and, with a
    UTC timestamp in front, to the file, until :data:`TEE_BUDGET_BYTES` of
    file have been written; then one notice is written and only the console
    keeps receiving the output. A file that cannot be opened is reported
    once and the tee degrades to a plain copy.
    """

    def __init__(
        self,
        source: IO[bytes],
        path: Path,
        passthrough: IO[bytes],
        *,
        owner: Owner = None,
        budget_bytes: int = TEE_BUDGET_BYTES,
        console: Callable[[str], None] | None = None,
        clock: Callable[[], float] = time.time,
    ) -> None:
        self._source = source
        self._passthrough = passthrough
        self._budget = budget_bytes
        self._clock = clock
        self._written = 0
        self._file: BinaryIO | None
        try:
            self._file = open(path, "ab", buffering=0)
            own(path, owner)
        except OSError as error:
            (console or _report)(f"devcapsule logs: cannot write {path} ({error}); {path.name} goes to the console only")
            self._file = None
        self._thread = threading.Thread(target=self._copy, name=f"tee:{path.name}", daemon=True)

    def start(self) -> Tee:
        self._thread.start()
        return self

    def join(self, timeout: float) -> None:
        self._thread.join(timeout)

    def _copy(self) -> None:
        try:
            for line in iter(self._source.readline, b""):
                self._forward(line)
        except (OSError, ValueError):
            pass  # the child or the console went away; nothing left to copy
        finally:
            if self._file is not None:
                self._file.close()

    def _forward(self, line: bytes) -> None:
        try:
            self._passthrough.write(line)
            self._passthrough.flush()
        except (OSError, ValueError):
            pass  # the console is gone; the file is still worth keeping
        if self._file is None:
            return
        stamped = time.strftime(_TIMESTAMP_FORMAT, time.gmtime(self._clock())).encode("ascii") + b" " + line
        if self._written + len(stamped) > self._budget:
            self._write(TEE_BUDGET_NOTICE.encode("utf-8"))
            self._file.close()
            self._file = None
            return
        self._write(stamped)
        self._written += len(stamped)

    def _write(self, data: bytes) -> None:
        assert self._file is not None
        try:
            self._file.write(data)
        except OSError:
            self._file.close()
            self._file = None


def _report(message: str) -> None:
    print(message, file=sys.stderr, flush=True)
