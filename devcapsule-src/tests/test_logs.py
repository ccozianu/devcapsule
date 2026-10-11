"""The session log framework: names, levels, the lifecycle record, the tee."""

from __future__ import annotations

import io
import logging
import os
from pathlib import Path
import subprocess
import sys
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


def test_prune_keeps_the_newest_sessions(tmp_path: Path) -> None:
    for name in ("20260101-000000-aaaa", "20260102-000000-bbbb", "20260103-000000-cccc", "not-a-dir"):
        (tmp_path / name).mkdir() if name != "not-a-dir" else (tmp_path / name).write_text("", encoding="utf-8")
    assert logs.prune_sessions(tmp_path, keep=2) == ["20260101-000000-aaaa"]
    assert sorted(p.name for p in tmp_path.iterdir()) == ["20260102-000000-bbbb", "20260103-000000-cccc", "not-a-dir"]
    assert logs.prune_sessions(tmp_path / "absent") == []
    with pytest.raises(ValueError):
        logs.prune_sessions(tmp_path, keep=0)


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
        old = next(h for h in root.handlers if isinstance(h, logging.handlers.RotatingFileHandler))
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


def test_rotation_owns_every_new_segment(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(logs, "SEGMENT_BYTES", 140)
    monkeypatch.setattr(logs.os, "geteuid", lambda: 0)
    owned: list[tuple[Path, int, int]] = []
    monkeypatch.setattr(logs.os, "chown", lambda path, uid, gid: owned.append((path, uid, gid)))
    path = logs.configure("supervisor", tmp_path, environ={}, owner=(1234, 5678))
    logs.events_logger("supervisor").info("first segment")
    logs.events_logger("supervisor").info("second segment")
    assert path is not None
    assert "first segment" in path.with_suffix(".log.1").read_text()
    assert "second segment" in path.read_text()
    assert owned == [(path, 1234, 5678), (path, 1234, 5678)]


def test_rollover_failure_reports_once_and_keeps_console(tmp_path: Path, monkeypatch, capsys) -> None:
    reports: list[str] = []
    logs.configure("supervisor", tmp_path, environ={}, console=reports.append)
    handler = next(h for h in logging.getLogger().handlers if isinstance(h, logging.handlers.RotatingFileHandler))

    def fail(record):
        raise OSError("bind mount unavailable")

    monkeypatch.setattr(handler, "shouldRollover", fail)
    logger = logging.getLogger("devcapsule.supervisor")
    logger.warning("first warning")
    logger.warning("second warning")
    assert handler.stream is None
    assert len(reports) == 1 and "bind mount unavailable" in reports[0]
    assert capsys.readouterr().err == "devcapsule supervisor: first warning\ndevcapsule supervisor: second warning\n"
