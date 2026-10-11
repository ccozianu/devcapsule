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

Every writer rotates its own file, in process, the moment a write would
carry it past its segment (:class:`SegmentedFile`): the live file is
renamed, compressed to ``.1.gz``, the older segments shift up and the one
beyond the count is removed. No external rotator, no polling, no window in
which output lands in a rotated segment, and no base image requirement.
``DEVCAPSULE_LOG_BUDGET`` sets a retention target for the checkout, not a
hard disk quota: the launcher derives each file's segment size from it and
removes the oldest ended sessions beyond it at the next launch.

Writing a log must never take the session down: every failure here degrades
to the console with one line saying what was lost.
"""

from __future__ import annotations

import calendar
import gzip
import json
import logging
import logging.handlers
import os
from pathlib import Path
import re
import secrets
import shutil
import sys
import threading
import time
from typing import IO, Callable, Mapping

LOG_FILE_PREFIX = "devcapsule-"
LOG_FILE_SUFFIX = ".log"
LEVEL_ENV = "DEVCAPSULE_LOG_LEVEL"
"""Verbosity override: DEBUG, INFO, WARNING or ERROR; WARNING without it."""
DIRECTORY_ENV = "DEVCAPSULE_LOG_DIR"
"""Where this session's logs live, as the launcher tells the capsule."""
DEFAULT_LEVEL = logging.WARNING
LEVEL_NAMES = ("DEBUG", "INFO", "WARNING", "ERROR")

BUDGET_ENV = "DEVCAPSULE_LOG_BUDGET"
"""The checkout's retention target: a size such as ``256M`` or ``1G``."""
DEFAULT_BUDGET_BYTES = 256 * 1024 * 1024
MINIMUM_BUDGET_BYTES = 16 * 1024 * 1024
# Each component's file rotates at a segment derived from the budget: one
# thirty-second of it, within these bounds, so a small budget still rotates
# often enough and a large one does not make single files unwieldy.
MAXIMUM_SEGMENT_BYTES = 10 * 1024 * 1024
MINIMUM_SEGMENT_BYTES = 1024 * 1024
SEGMENT_SHARE = 32
ROTATIONS = 4
"""Older segments kept per file, all gzipped: ``.1.gz`` the newest to ``.4.gz``."""

SESSION_MANIFEST = "session.json"
ABANDONED_SESSION_SECONDS = 7 * 24 * 3600
"""A session with no end recorded counts as abandoned, and prunable, after this long."""
EVENTS_SUFFIX = ".events"

_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
_LINE_FORMAT = "%(asctime)s %(levelname)s %(name)s[%(process)d]: %(message)s"
_INSTALLED_ATTRIBUTE = "_devcapsule_installed"
# Bound both memory use and the wait for output without a trailing newline.
_TEE_READ_BYTES = 64 * 1024

Owner = tuple[int, int] | None
"""``(uid, gid)`` to give a file when the writer is root, else ``None``."""


class LogLevelError(ValueError):
    """The verbosity override names no known level."""


class LogBudgetError(ValueError):
    """The budget override is not a size, or is too small to rotate anything."""


_SIZE_UNITS = {"": 1, "K": 1024, "M": 1024 ** 2, "G": 1024 ** 3}


def parse_size(text: str) -> int:
    """Bytes from ``256M``, ``1G``, ``512K`` or a plain number; binary units."""

    match = re.fullmatch(r"\s*(\d+)\s*(?:([KMGkmg])(?:i?[Bb])?|[Bb]?)\s*", text)
    if match is None:
        raise LogBudgetError(f"{text!r} is not a size; use a number with K, M or G, such as 256M")
    try:
        return int(match.group(1)) * _SIZE_UNITS[(match.group(2) or "").upper()]
    except ValueError as error:
        # Python bounds decimal conversion; keep oversized input on the same
        # recoverable path as other invalid budget values.
        raise LogBudgetError("size contains too many digits") from error


def format_size(size: int) -> str:
    """``256 MiB``, ``1 GiB``, ``512 KiB``: the unit that divides it, else bytes."""

    for unit, factor in (("GiB", 1024 ** 3), ("MiB", 1024 ** 2), ("KiB", 1024)):
        if size >= factor and size % factor == 0:
            return f"{size // factor} {unit}"
    return f"{size} bytes"


def budget_from_environment(environ: Mapping[str, str] | None = None) -> int:
    """The checkout's log budget: :data:`DEFAULT_BUDGET_BYTES` unless the override names one."""

    value = (os.environ if environ is None else environ).get(BUDGET_ENV, "")
    if not value:
        return DEFAULT_BUDGET_BYTES
    try:
        budget = parse_size(value)
    except LogBudgetError as error:
        raise LogBudgetError(f"{BUDGET_ENV}: {error}") from error
    if budget < MINIMUM_BUDGET_BYTES:
        raise LogBudgetError(f"{BUDGET_ENV} must be at least {format_size(MINIMUM_BUDGET_BYTES)}, not {value!r}")
    return budget


def segment_bytes_for(budget: int) -> int:
    """The size at which each file rotates under ``budget``; see :data:`SEGMENT_SHARE`."""

    return max(MINIMUM_SEGMENT_BYTES, min(MAXIMUM_SEGMENT_BYTES, budget // SEGMENT_SHARE))


class _SessionFileHandler(logging.Handler):
    """The component's file for :mod:`logging`: a :class:`SegmentedFile`, owned by the capsule user.

    A write that fails, on a full or disconnected bind mount, is reported
    once and the handler goes quiet, so the console is not flooded with a
    traceback per record. The console handler remains.
    """

    def __init__(
        self, path: Path, *, segment_bytes: int, rotations: int, owner: Owner, report: Callable[[str], None]
    ) -> None:
        super().__init__()
        self._path = path
        self._report = report
        self._file: SegmentedFile | None = SegmentedFile(path, segment_bytes=segment_bytes, rotations=rotations, owner=owner)

    def emit(self, record: logging.LogRecord) -> None:
        if self._file is None:
            return
        try:
            self._file.write((self.format(record) + "\n").encode("utf-8", "replace"))
        except OSError as error:
            self._quiet()
            self._report(f"devcapsule logs: cannot write {self._path} ({error}); logging to the console only")

    def close(self) -> None:
        self._quiet()
        super().close()

    def _quiet(self) -> None:
        if self._file is not None:
            try:
                self._file.close()
            except OSError:
                pass  # closing the same unavailable mount can fail too
            self._file = None


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
    segment_bytes: int = MAXIMUM_SEGMENT_BYTES,
    rotations: int = ROTATIONS,
) -> Path | None:
    """Route this process's logging to the console and, when given, a file.

    The console handler prints WARNING and above as ``devcapsule <component>:
    message``, the form the launcher and the supervisor have always used. The
    file handler writes every record the baseline admits with a UTC
    timestamp into a :class:`SegmentedFile` rotated at ``segment_bytes``.
    Returns the file's path, or ``None`` when there is no directory or the
    file cannot be opened, which is reported once on the console rather
    than raised.
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
        file = _SessionFileHandler(path, segment_bytes=segment_bytes, rotations=rotations, owner=owner, report=report)
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


def directory_size(path: Path) -> int:
    """Bytes of the regular files under ``path``; what cannot be read counts as nothing."""

    total = 0
    for directory, _subdirectories, files in os.walk(path):
        for name in files:
            try:
                total += os.lstat(os.path.join(directory, name)).st_size
            except OSError:
                continue
    return total


def session_ended(directory: Path, *, now: float | None = None) -> bool:
    """Whether the session that owns ``directory`` is over.

    The launcher records ``ended-at`` in the manifest when its ``docker run``
    returns. A session without that record is still running, or its launcher
    died before writing it; after :data:`ABANDONED_SESSION_SECONDS` from the
    start time in the directory's name it counts as abandoned. A directory
    whose name is not a session id is not ours to judge and counts as ended.
    """

    try:
        manifest = json.loads((directory / SESSION_MANIFEST).read_text(encoding="utf-8"))
        if isinstance(manifest, dict) and manifest.get("ended-at"):
            return True
    except (OSError, ValueError):
        pass
    try:
        # Session ids are UTC, independent of the launcher's timezone or DST.
        started = calendar.timegm(time.strptime(directory.name[:15], "%Y%m%d-%H%M%S"))
    except ValueError:
        return True
    return (time.time() if now is None else now) - started > ABANDONED_SESSION_SECONDS


def prune_sessions(root: Path, *, budget_bytes: int, current: str, now: float | None = None) -> list[str]:
    """Remove the oldest ended session directories under ``root`` until it fits the budget.

    Session identifiers sort by start time, so the oldest are the first by
    name. The ``current`` session and every session not yet ended (see
    :func:`session_ended`) are never removed, so the directory may exceed
    the budget by those sessions. Returns the names removed. A directory
    that cannot be removed is left alone and omitted; this is housekeeping,
    not a guarantee.
    """

    if budget_bytes < 0:
        raise ValueError("the budget cannot be negative")
    try:
        sessions = sorted(entry.name for entry in root.iterdir() if entry.is_dir())
    except OSError:
        return []
    sizes = {name: directory_size(root / name) for name in sessions}
    total = sum(sizes.values())
    removed: list[str] = []
    for name in sessions:
        if total <= budget_bytes:
            break
        if name == current or not session_ended(root / name, now=now):
            continue
        try:
            shutil.rmtree(root / name)
        except OSError:
            continue
        total -= sizes[name]
        removed.append(name)
    return removed


class SegmentedFile:
    """An append-only log file that its writer rotates at an exact size.

    A write that would carry the live file past ``segment_bytes`` rotates
    first: the live file becomes ``<name>.1.gz``, the older segments shift
    to ``.2.gz`` and on, the one beyond ``rotations`` is removed, and a new
    live file starts with that write. The live file therefore never exceeds
    the segment, with one exception: a single write larger than the segment
    goes into a fresh file on its own. Every file created here is given to
    ``owner`` when the writer is root. Failures raise ``OSError`` to the
    caller, which decides how to degrade.
    """

    def __init__(self, path: Path, *, segment_bytes: int, rotations: int, owner: Owner = None) -> None:
        if segment_bytes < 1 or rotations < 1:
            raise ValueError("rotation needs a positive segment size and at least one rotation")
        self._path = path
        self._segment = segment_bytes
        self._rotations = rotations
        self._owner = owner
        self._file: IO[bytes] | None = None
        self._size = 0
        self._open()

    @property
    def path(self) -> Path:
        return self._path

    @property
    def size(self) -> int:
        """Bytes in the live file."""
        return self._size

    def segment_path(self, index: int) -> Path:
        """``<name>.<index>.gz``; 1 is the newest rotated segment."""
        return self._path.with_name(f"{self._path.name}.{index}.gz")

    def write(self, data: bytes) -> None:
        if self._file is None:
            raise ValueError("the segmented file is closed")
        if self._size and self._size + len(data) > self._segment:
            self.rotate()
        assert self._file is not None
        self._file.write(data)
        self._size += len(data)

    def rotate(self) -> None:
        """Compress the live file into ``.1.gz``, shift the older segments, start a new live file."""

        if self._file is not None:
            self._file.close()
            self._file = None
        for index in range(self._rotations - 1, 0, -1):
            older = self.segment_path(index)
            if older.exists():
                os.replace(older, self.segment_path(index + 1))
        staging = self.segment_path(1).with_name(self.segment_path(1).name + ".tmp")
        with open(self._path, "rb") as source, gzip.open(staging, "wb", compresslevel=6) as target:
            shutil.copyfileobj(source, target)
        own(staging, self._owner)
        os.replace(staging, self.segment_path(1))
        os.unlink(self._path)
        self._open()

    def close(self) -> None:
        if self._file is not None:
            self._file.close()
            self._file = None

    def _open(self) -> None:
        file = open(self._path, "ab", buffering=0)
        try:
            own(self._path, self._owner)
            self._size = os.fstat(file.fileno()).st_size
        except OSError:
            file.close()
            raise
        self._file = file


class Tee:
    """Copy a child's output to its log file and onward to the console.

    Reads ``source`` (the child's combined stdout and stderr) in bounded chunks
    on a daemon thread, so partial lines reach the console promptly. Output
    goes unchanged to ``passthrough`` and, with a UTC timestamp in front of
    each line, into a :class:`SegmentedFile` rotated at ``segment_bytes``. A
    file that cannot be opened or written is reported once and the tee
    degrades to a plain copy to the console.
    """

    def __init__(
        self,
        source: IO[bytes],
        path: Path,
        passthrough: IO[bytes],
        *,
        owner: Owner = None,
        segment_bytes: int = MAXIMUM_SEGMENT_BYTES,
        rotations: int = ROTATIONS,
        console: Callable[[str], None] | None = None,
        clock: Callable[[], float] = time.time,
    ) -> None:
        self._source = source
        self._path = path
        self._passthrough = passthrough
        self._clock = clock
        self._line_start = True
        self._report = console or _report
        self._file: SegmentedFile | None = None
        try:
            self._file = SegmentedFile(path, segment_bytes=segment_bytes, rotations=rotations, owner=owner)
        except OSError as error:
            self._report(f"devcapsule logs: cannot write {path} ({error}); {path.name} goes to the console only")
        self._thread = threading.Thread(target=self._copy, name=f"tee:{path.name}", daemon=True)

    def start(self) -> Tee:
        self._thread.start()
        return self

    def join(self, timeout: float) -> None:
        self._thread.join(timeout)

    def _copy(self) -> None:
        try:
            # BufferedReader.read() may wait for a full chunk; read1() returns
            # the bytes available from one pipe read, including prompts.
            read = getattr(self._source, "read1", self._source.read)
            while chunk := read(_TEE_READ_BYTES):
                self._forward(chunk)
        except (OSError, ValueError):
            pass  # the child or the console went away; nothing left to copy
        finally:
            if self._file is not None:
                self._file.close()

    def _forward(self, chunk: bytes) -> None:
        try:
            self._passthrough.write(chunk)
            self._passthrough.flush()
        except (OSError, ValueError):
            pass  # the console is gone; the file is still worth keeping
        if self._file is None:
            return
        # Split only on LF: binary output may contain other control bytes.
        pieces = chunk.split(b"\n")
        for index, piece in enumerate(pieces):
            if index < len(pieces) - 1:
                piece += b"\n"
            if not piece:
                continue
            prefix = (
                time.strftime(_TIMESTAMP_FORMAT, time.gmtime(self._clock())).encode("ascii") + b" "
                if self._line_start else b""
            )
            self._write(prefix + piece)
            if self._file is None:
                return
            self._line_start = piece.endswith(b"\n")

    def _write(self, data: bytes) -> None:
        assert self._file is not None
        try:
            self._file.write(data)
        except OSError as error:
            self._file.close()
            self._file = None
            self._report(f"devcapsule logs: cannot write {self._path} ({error}); the rest goes to the console only")


def _report(message: str) -> None:
    print(message, file=sys.stderr, flush=True)
