"""Pure-Python PID 1 supervision: reap, forward, graceful end, honest exit."""

from __future__ import annotations

from dataclasses import dataclass
import os
import signal
import subprocess
import sys
import time
from typing import Iterable


class SupervisorError(ValueError):
    """The supervised child set is malformed."""


# Session exit code when a non-foreground child dies. The foreground child's
# own codes travel through unchanged, so the supervisor's one verdict of its
# own uses a value ordinary tools rarely produce (BSD sysexits EX_SOFTWARE).
INFRASTRUCTURE_FAILURE_EXIT_CODE = 70

# How long children get between SIGTERM and SIGKILL. Kept below Docker's
# default ten-second `docker stop` timeout so the supervisor finishes its own
# orderly end and exits honestly before the engine kills the whole container.
DEFAULT_GRACE_SECONDS = 5.0

_HANDLED_SIGNALS = frozenset({signal.SIGCHLD, signal.SIGTERM, signal.SIGINT})


@dataclass(frozen=True)
class SupervisedChild:
    """One process the supervisor starts and owns until the session ends."""

    name: str
    command: tuple[str, ...]
    foreground: bool = False
    working_directory: str | None = None


@dataclass
class _RunningChild:
    child: SupervisedChild
    process: subprocess.Popen[bytes]


class Supervisor:
    """Runs an ordered set of children of which exactly one is foreground.

    The foreground child is the session: when it exits, the session ends and
    its exit status becomes the supervisor's, with death-by-signal reported
    as the shell convention 128 plus the signal number. Any other child dying
    first is a session failure: everything is shut down and the supervisor
    exits with ``INFRASTRUCTURE_FAILURE_EXIT_CODE`` naming the dead child.
    ``SIGTERM`` (what ``docker stop`` sends) and ``SIGINT`` are the explicit
    session end. Every ending runs the same sequence: SIGTERM to the live
    children in reverse start order, a grace period, SIGKILL to stragglers.

    ``run`` must be called on the process's main thread while no other thread
    leaves the handled signals unblocked; the intended caller is the
    single-threaded container entrypoint at PID 1, where the supervisor also
    reaps orphans re-parented to it.
    """

    def __init__(
        self,
        children: tuple[SupervisedChild, ...],
        *,
        grace_seconds: float = DEFAULT_GRACE_SECONDS,
    ) -> None:
        if not children:
            raise SupervisorError("supervisor requires at least one child")
        names = [child.name for child in children]
        if len(set(names)) != len(names) or not all(names):
            raise SupervisorError("supervised children must carry unique non-empty names")
        if any(not child.command for child in children):
            raise SupervisorError("supervised children must carry non-empty commands")
        if sum(1 for child in children if child.foreground) != 1:
            raise SupervisorError("exactly one supervised child must be foreground")
        if grace_seconds <= 0:
            raise SupervisorError("grace period must be positive")
        self._children = children
        self._grace_seconds = grace_seconds

    def run(self) -> int:
        previous_mask = signal.pthread_sigmask(signal.SIG_BLOCK, _HANDLED_SIGNALS)
        try:
            return self._supervise()
        finally:
            signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)

    def _supervise(self) -> int:
        # Insertion order is start order; iterating live reversed is shutdown
        # order. The Popen objects must stay referenced for the session: a
        # collected Popen reaps its own zombie behind the supervisor's back,
        # and the exit would never be attributed to its child.
        live: dict[int, _RunningChild] = {}
        for child in self._children:
            try:
                process = subprocess.Popen(
                    child.command,
                    cwd=child.working_directory,
                    preexec_fn=_unblock_all_signals,
                )
            except OSError as error:
                for pid in reversed(live):
                    _signal_child(pid, signal.SIGKILL)
                _reap()
                raise SupervisorError(f"cannot start child {child.name!r}: {error}") from error
            live[process.pid] = _RunningChild(child, process)

        foreground_status: int | None = None
        failed_child: SupervisedChild | None = None
        ending = False
        killed = False
        deadline = 0.0

        while live:
            if not ending or killed:
                # Nothing is timed: children either run (until a signal or an
                # exit wakes us) or are already SIGKILLed and cannot linger.
                received = signal.sigwaitinfo(_HANDLED_SIGNALS).si_signo
            else:
                remaining = deadline - time.monotonic()
                info = signal.sigtimedwait(_HANDLED_SIGNALS, max(remaining, 0.0))
                if info is None:
                    _announce(
                        "grace period over; killing "
                        + _names(running.child for running in live.values())
                    )
                    for pid in live:
                        _signal_child(pid, signal.SIGKILL)
                    killed = True
                    continue
                received = info.si_signo

            if received in (signal.SIGTERM, signal.SIGINT):
                if not ending:
                    _announce(f"session end requested ({signal.Signals(received).name}); stopping children")
                    ending = True
                    deadline = time.monotonic() + self._grace_seconds
                for pid in reversed(live):
                    _signal_child(pid, signal.SIGTERM)

            for pid, status in _reap():
                running = live.pop(pid, None)
                if running is None:
                    continue  # an orphan adopted by PID 1; reaping it is the whole duty
                # Tell the Popen its child is gone so it never polls the pid again.
                running.process.returncode = os.waitstatus_to_exitcode(status)
                exited = running.child
                if exited.foreground:
                    foreground_status = status
                elif not ending:
                    failed_child = exited
                    _announce(
                        f"child {exited.name!r} died unexpectedly"
                        f" ({_describe_status(status)}); the session has failed"
                    )
                if not ending and live:
                    ending = True
                    deadline = time.monotonic() + self._grace_seconds
                    for other_pid in reversed(live):
                        _signal_child(other_pid, signal.SIGTERM)

        if failed_child is not None:
            return INFRASTRUCTURE_FAILURE_EXIT_CODE
        assert foreground_status is not None  # the loop cannot end without it
        return _honest_exit_code(foreground_status)


def _reap() -> list[tuple[int, int]]:
    reaped: list[tuple[int, int]] = []
    while True:
        try:
            pid, status = os.waitpid(-1, os.WNOHANG)
        except ChildProcessError:
            break
        if pid == 0:
            break
        reaped.append((pid, status))
    return reaped


def _honest_exit_code(status: int) -> int:
    if os.WIFEXITED(status):
        return os.WEXITSTATUS(status)
    if os.WIFSIGNALED(status):
        return 128 + os.WTERMSIG(status)
    return 1


def _describe_status(status: int) -> str:
    if os.WIFEXITED(status):
        return f"exit code {os.WEXITSTATUS(status)}"
    if os.WIFSIGNALED(status):
        return f"killed by {signal.Signals(os.WTERMSIG(status)).name}"
    return "unknown status"


def _signal_child(pid: int, signum: signal.Signals) -> None:
    try:
        os.kill(pid, signum)
    except ProcessLookupError:
        pass  # exited between bookkeeping and delivery; the reap loop settles it


def _unblock_all_signals() -> None:
    # Children must not inherit the supervisor's blocked mask, or they would
    # never see the SIGTERM it forwards.
    signal.pthread_sigmask(signal.SIG_SETMASK, set())


def _names(children: Iterable[SupervisedChild]) -> str:
    return ", ".join(child.name for child in children)


def _announce(message: str) -> None:
    print(f"devcapsule supervisor: {message}", file=sys.stderr, flush=True)
