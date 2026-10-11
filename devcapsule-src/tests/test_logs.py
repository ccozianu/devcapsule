"""The session log framework: names, levels, the lifecycle record, the tee."""

from __future__ import annotations

from collections.abc import Buffer
import io
import logging
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Iterator

import pytest

from devcapsule import logs


@pytest.fixture(autouse=True)
def clean_logging() -> Iterator[None]:
    """Each test configures from a bare root logger and leaves none of its handlers behind."""
    yield
    logs.reset()


def test_log_files_follow_one_recognizable_pattern(tmp_path: Path) -> None:
    assert logs.log_path(tmp_path, "launcher") == tmp_path / "devcapsule-launcher.log"
    assert logs.log_path(tmp_path, "window-manager").name == "devcapsule-window-manager.log"
    for bad in ("", "a/b", " spaced"):
        with pytest.raises(ValueError, match="plain words"):
            logs.log_path(tmp_path, bad)


def test_the_baseline_is_warning_and_the_override_names_a_level() -> None:
    assert logs.level_from_environment({}) == logging.WARNING
    assert logs.level_from_environment({logs.LEVEL_ENV: "debug"}) == logging.DEBUG
    assert logs.level_from_environment({logs.LEVEL_ENV: " Info "}) == logging.INFO
    with pytest.raises(logs.LogLevelError, match="DEBUG, INFO, WARNING, ERROR, not 'loud'"):
        logs.level_from_environment({logs.LEVEL_ENV: "loud"})


def test_configure_writes_warnings_to_the_file_with_utc_timestamps_and_drops_info(tmp_path: Path) -> None:
    path = logs.configure("launcher", tmp_path, environ={})
    assert path == tmp_path / "devcapsule-launcher.log"
    logger = logging.getLogger("devcapsule.launcher")
    logger.info("not kept")
    logger.warning("kept: %s", "detail")
    logging.getLogger("devcapsule").warning("root of the package")
    text = path.read_text(encoding="utf-8")
    assert "not kept" not in text
    lines = text.splitlines()
    assert len(lines) == 2
    assert lines[0].endswith(f"WARNING devcapsule.launcher[{os.getpid()}]: kept: detail")
    assert lines[0][:21].endswith("Z ") and lines[0][4] == "-" and lines[0][10] == "T"


def test_lifecycle_events_are_recorded_at_info_whatever_the_baseline(tmp_path: Path) -> None:
    path = logs.configure("supervisor", tmp_path, environ={})
    events = logs.events_logger("supervisor")
    events.info("child %r started", "xvnc")
    logging.getLogger("devcapsule.supervisor").info("ordinary info stays out")
    assert path is not None
    text = path.read_text(encoding="utf-8")
    assert "INFO devcapsule.supervisor.events" in text and "child 'xvnc' started" in text
    assert "ordinary info" not in text


def test_the_override_lowers_the_baseline_for_ordinary_loggers(tmp_path: Path) -> None:
    path = logs.configure("launcher", tmp_path, environ={logs.LEVEL_ENV: "DEBUG"})
    logging.getLogger("devcapsule.launcher").debug("now kept")
    assert path is not None and "DEBUG devcapsule.launcher" in path.read_text(encoding="utf-8")


def test_configure_prints_warnings_to_the_console_in_the_component_form(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    logs.configure("supervisor", None, environ={})
    logging.getLogger("devcapsule.supervisor").warning("session end requested")
    logs.events_logger("supervisor").info("child started")
    err = capsys.readouterr().err
    assert err == "devcapsule supervisor: session end requested\n"


def test_configure_is_repeatable_and_reports_a_bad_override_and_an_unwritable_directory(tmp_path: Path) -> None:
    reports: list[str] = []
    first = logs.configure("launcher", tmp_path, environ={}, console=reports.append)
    second = logs.configure("launcher", tmp_path, environ={logs.LEVEL_ENV: "loud"}, console=reports.append)
    assert first == second
    installed = [h for h in logging.getLogger().handlers if getattr(h, "_devcapsule_installed", False)]
    assert len(installed) == 2  # one console, one file; never accumulated
    assert reports == ["devcapsule launcher: DEVCAPSULE_LOG_LEVEL must be one of DEBUG, INFO, WARNING, ERROR, not 'loud'; logging at WARNING"]
    blocked = tmp_path / "file-not-directory"
    blocked.write_text("", encoding="utf-8")
    assert logs.configure("launcher", blocked / "logs", environ={}, console=reports.append) is None
    assert reports[-1].startswith("devcapsule launcher: cannot write") and reports[-1].endswith("logging to the console only")


def test_session_ids_sort_by_start_time() -> None:
    earlier = logs.new_session_id(1_700_000_000)
    later = logs.new_session_id(1_700_000_001)
    assert earlier.startswith("20231114-221320-") and len(earlier) == len("20231114-221320-abcd")
    assert earlier < later


def test_prune_removes_the_oldest_sessions_until_the_budget_fits_and_spares_the_current(tmp_path: Path) -> None:
    for name, size in (("20260101-000000-aaaa", 30), ("20260102-000000-bbbb", 30), ("20260103-000000-cccc", 30), ("20260104-000000-dddd", 5)):
        (tmp_path / name).mkdir()
        (tmp_path / name / "devcapsule-x.log").write_bytes(b"x" * size)
    (tmp_path / "not-a-dir").write_text("", encoding="utf-8")
    assert logs.directory_size(tmp_path / "20260101-000000-aaaa") == 30
    assert logs.prune_sessions(tmp_path, budget_bytes=70, current="20260104-000000-dddd") == ["20260101-000000-aaaa"]
    assert logs.prune_sessions(tmp_path, budget_bytes=0, current="20260101-000000-aaaa") == ["20260102-000000-bbbb", "20260103-000000-cccc", "20260104-000000-dddd"]
    assert sorted(entry.name for entry in tmp_path.iterdir()) == ["not-a-dir"]
    assert logs.prune_sessions(tmp_path / "absent", budget_bytes=1, current="x") == []
    with pytest.raises(ValueError):
        logs.prune_sessions(tmp_path, budget_bytes=-1, current="x")


def test_the_budget_knob_parses_sizes_and_has_a_floor() -> None:
    assert logs.parse_size("256M") == 256 * 1024 ** 2
    assert logs.parse_size(" 1g ") == 1024 ** 3
    assert logs.parse_size("512KiB") == 512 * 1024
    assert logs.parse_size("4096") == 4096
    assert logs.format_size(256 * 1024 ** 2) == "256 MiB" and logs.format_size(1024 ** 3) == "1 GiB" and logs.format_size(1500) == "1500 bytes"
    assert logs.budget_from_environment({}) == 256 * 1024 ** 2
    assert logs.budget_from_environment({logs.BUDGET_ENV: "64M"}) == 64 * 1024 ** 2
    with pytest.raises(logs.LogBudgetError, match="DEVCAPSULE_LOG_BUDGET: 'much' is not a size; use a number with K, M or G"):
        logs.budget_from_environment({logs.BUDGET_ENV: "much"})
    with pytest.raises(logs.LogBudgetError, match="at least 16 MiB"):
        logs.budget_from_environment({logs.BUDGET_ENV: "8M"})
    # One thirty-second of the budget per segment, between 1 and 10 MiB.
    assert logs.segment_bytes_for(256 * 1024 ** 2) == 8 * 1024 ** 2
    assert logs.segment_bytes_for(16 * 1024 ** 2) == 1024 ** 2
    assert logs.segment_bytes_for(10 * 1024 ** 3) == 10 * 1024 ** 2


def test_logrotate_configuration_bounds_every_component_file_and_delays_compression(tmp_path: Path) -> None:
    path = logs.write_logrotate_configuration(tmp_path, segment_bytes=1024 ** 2, rotations=4)
    assert path == tmp_path / "logrotate.conf" and path.stat().st_mode & 0o777 == 0o644
    text = path.read_text(encoding="utf-8")
    assert text.startswith(f"{tmp_path}/devcapsule-*.log {{\n")
    for directive in ("size 1048576", "rotate 4", "compress", "delaycompress", "missingok", "notifempty", "create"):
        assert f"    {directive}\n" in text
    assert logs.logrotate_command(tmp_path) == ("logrotate", "-s", str(tmp_path / ".logrotate.state"), str(tmp_path / "logrotate.conf"))
    with pytest.raises(ValueError):
        logs.logrotate_configuration(tmp_path, segment_bytes=0, rotations=4)


def test_rotation_runs_logrotate_every_interval_and_once_more_at_the_end(tmp_path: Path) -> None:
    marks = tmp_path / "runs"
    command = ("sh", "-c", f"echo run >> {marks}")
    with logs.Rotation(command, interval_seconds=0.05) as rotation:
        deadline = time.monotonic() + 5.0
        while rotation.runs < 2 and time.monotonic() < deadline:
            time.sleep(0.01)
    assert rotation.runs >= 3  # two timed runs and the final one
    assert marks.read_text(encoding="utf-8").count("run") == rotation.runs


def test_rotation_reports_a_failing_logrotate_once_and_keeps_trying(tmp_path: Path) -> None:
    path = logs.configure("supervisor", tmp_path, environ={})
    rotation = logs.Rotation(("sh", "-c", "echo bad config >&2; exit 1"), interval_seconds=1.0)
    assert rotation.run_once() is False and rotation.run_once() is False
    assert path is not None
    text = path.read_text(encoding="utf-8")
    assert text.count("logrotate exited 1: bad config; rotation keeps retrying every 1s") == 1
    absent = logs.Rotation(("/nonexistent/logrotate",), interval_seconds=1.0)
    assert absent.run_once() is False
    with pytest.raises(ValueError):
        logs.Rotation((), interval_seconds=1.0)


def test_tee_follows_the_file_logrotate_moves_away(tmp_path: Path) -> None:
    path = tmp_path / "devcapsule-child.log"
    source_read, source_write = os.pipe()
    writer = os.fdopen(source_write, "wb", buffering=0)
    passthrough = io.BytesIO()
    tee = logs.Tee(os.fdopen(source_read, "rb", buffering=0), path, passthrough, budget_bytes=None, clock=lambda: 0.0).start()
    writer.write(b"before\n")
    deadline = time.monotonic() + 5.0
    while b"before" not in passthrough.getvalue() and time.monotonic() < deadline:
        time.sleep(0.01)
    path.rename(tmp_path / "devcapsule-child.log.1")  # what logrotate does, then `create`
    writer.write(b"after\n")
    writer.close()
    tee.join(5.0)
    assert (tmp_path / "devcapsule-child.log.1").read_bytes() == b"1970-01-01T00:00:00Z before\n"
    assert path.read_bytes() == b"1970-01-01T00:00:00Z after\n"


def run_tee(tmp_path: Path, payload: bytes, **options: object) -> tuple[bytes, Path]:
    passthrough = io.BytesIO()
    path = tmp_path / "devcapsule-child.log"
    tee = logs.Tee(io.BytesIO(payload), path, passthrough, clock=lambda: 0.0, **options)  # type: ignore[arg-type]
    tee.start()
    tee.join(5.0)
    return passthrough.getvalue(), path


def test_tee_copies_every_line_to_the_console_unchanged_and_stamps_the_file(tmp_path: Path) -> None:
    passthrough, path = run_tee(tmp_path, b"first line\nsecond\nno newline at the end")
    assert passthrough == b"first line\nsecond\nno newline at the end"
    assert path.read_bytes() == (
        b"1970-01-01T00:00:00Z first line\n1970-01-01T00:00:00Z second\n1970-01-01T00:00:00Z no newline at the end"
    )


def test_tee_stops_writing_the_file_at_its_budget_and_says_so(tmp_path: Path) -> None:
    line = b"x" * 50 + b"\n"
    passthrough, path = run_tee(tmp_path, line * 10, budget_bytes=3 * (21 + len(line)))
    assert passthrough == line * 10
    text = path.read_text(encoding="utf-8")
    assert text.count("Z xxxxx") == 3
    assert text.endswith(logs.TEE_BUDGET_NOTICE)


def test_tee_degrades_to_a_plain_copy_when_the_file_cannot_be_opened(tmp_path: Path) -> None:
    reports: list[str] = []
    passthrough = io.BytesIO()
    tee = logs.Tee(io.BytesIO(b"still seen\n"), tmp_path / "missing" / "devcapsule-x.log", passthrough, console=reports.append)
    tee.start()
    tee.join(5.0)
    assert passthrough.getvalue() == b"still seen\n"
    assert len(reports) == 1 and "devcapsule-x.log goes to the console only" in reports[0]


def test_tee_follows_a_real_child_process(tmp_path: Path) -> None:
    process = subprocess.Popen(
        [sys.executable, "-c", "import sys; print('out'); print('err', file=sys.stderr)"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    assert process.stdout is not None
    passthrough = io.BytesIO()
    path = tmp_path / "devcapsule-job.log"
    tee = logs.Tee(process.stdout, path, passthrough).start()
    assert process.wait(timeout=10) == 0
    tee.join(5.0)
    assert sorted(passthrough.getvalue().split()) == [b"err", b"out"]
    assert path.read_text(encoding="utf-8").count("Z ") == 2


def test_reconfigure_closes_old_file_and_keeps_unrelated_handlers(tmp_path: Path) -> None:
    unrelated = logging.NullHandler()
    root = logging.getLogger()
    root.addHandler(unrelated)
    try:
        first = logs.configure("launcher", tmp_path / "first", environ={logs.LEVEL_ENV: "DEBUG"})
        old = next(h for h in root.handlers if isinstance(h, logging.handlers.WatchedFileHandler))
        logging.getLogger("devcapsule.launcher").debug("first session")
        second = logs.configure("launcher", tmp_path / "second", environ={logs.LEVEL_ENV: "ERROR"})
        assert old.stream is None and unrelated in root.handlers
        logger = logging.getLogger("devcapsule.launcher")
        logger.debug("discarded debug")
        logger.warning("discarded warning")
        logs.events_logger("launcher").info("second session")
        assert first is not None and second is not None
        assert "second session" not in first.read_text()
        assert "first session" not in second.read_text()
        assert "discarded" not in second.read_text()
        assert second.read_text().count("second session") == 1
        logs.configure("launcher", None, environ={})
        logs.events_logger("launcher").info("console only")
        assert "console only" not in second.read_text()
    finally:
        root.removeHandler(unrelated)


def test_the_handler_follows_logrotate_and_owns_the_reopened_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(logs.os, "geteuid", lambda: 0)
    owned: list[tuple[Path, int, int]] = []
    monkeypatch.setattr(logs.os, "chown", lambda path, uid, gid: owned.append((path, uid, gid)))
    path = logs.configure("supervisor", tmp_path, environ={}, owner=(1234, 5678))
    assert path is not None
    logs.events_logger("supervisor").info("first segment")
    path.rename(path.with_suffix(".log.1"))  # what logrotate does before `create`
    logs.events_logger("supervisor").info("second segment")
    assert "first segment" in path.with_suffix(".log.1").read_text()
    assert path.read_text().count("second segment") == 1 and "first segment" not in path.read_text()
    assert owned == [(path, 1234, 5678), (path, 1234, 5678)]


def test_a_failed_reopen_reports_once_and_keeps_the_console(tmp_path: Path, monkeypatch, capsys) -> None:
    reports: list[str] = []
    logs.configure("supervisor", tmp_path, environ={}, console=reports.append)
    handler = next(h for h in logging.getLogger().handlers if isinstance(h, logging.handlers.WatchedFileHandler))

    def fail():
        raise OSError("bind mount unavailable")

    monkeypatch.setattr(handler, "reopenIfNeeded", fail)
    logger = logging.getLogger("devcapsule.supervisor")
    logger.warning("first warning")
    logger.warning("second warning")
    assert handler.stream is None
    assert len(reports) == 1 and "bind mount unavailable" in reports[0]
    assert capsys.readouterr().err == "devcapsule supervisor: first warning\ndevcapsule supervisor: second warning\n"


def test_tee_write_failure_at_budget_cut_keeps_forwarding(tmp_path: Path, monkeypatch) -> None:
    class FullDisk(io.BytesIO):
        def write(self, data: Buffer, /) -> int:
            raise OSError("disk full")

    real = open(tmp_path / "log", "ab")  # the tee stats the path and its descriptor to follow logrotate
    file = FullDisk()
    file.fileno = real.fileno  # type: ignore[method-assign]
    monkeypatch.setattr("builtins.open", lambda *args, **kwargs: file)
    passthrough = io.BytesIO()
    reports: list[str] = []
    tee = logs.Tee(io.BytesIO(), tmp_path / "log", passthrough, budget_bytes=0, console=reports.append)
    # Run synchronously so a broken budget path fails this test directly.
    tee._forward(b"first\n")
    tee._forward(b"second\n")
    assert passthrough.getvalue() == b"first\nsecond\n"
    assert file.closed and len(reports) == 1 and "disk full" in reports[0]


def test_tee_ownership_failure_closes_file_and_keeps_console(tmp_path: Path, monkeypatch) -> None:
    file = io.BytesIO()
    monkeypatch.setattr("builtins.open", lambda *args, **kwargs: file)

    def fail(path, owner):
        raise PermissionError("chown denied")

    monkeypatch.setattr(logs, "own", fail)
    reports: list[str] = []
    passthrough, _ = run_tee(tmp_path, b"still seen\n", owner=(1234, 5678), console=reports.append)
    assert file.closed and passthrough == b"still seen\n"
    assert len(reports) == 1 and "chown denied" in reports[0]


def test_tee_bounds_reads_without_repeating_timestamps_within_a_line(tmp_path: Path) -> None:
    payload = b"x" * (2 * logs._TEE_READ_BYTES) + b"\nlast\rbyte\n"

    class BoundedSource(io.BytesIO):
        def read1(self, size: int | None = -1) -> bytes:
            assert size is not None and 0 < size <= logs._TEE_READ_BYTES
            return super().read1(size)

    path = tmp_path / "log"
    passthrough = io.BytesIO()
    tee = logs.Tee(BoundedSource(payload), path, passthrough, clock=lambda: 0.0).start()
    tee.join(5)
    assert passthrough.getvalue() == payload
    assert path.read_bytes() == b"1970-01-01T00:00:00Z " + payload.replace(b"\nlast", b"\n1970-01-01T00:00:00Z last")
