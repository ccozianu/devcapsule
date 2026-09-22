"""Diagnostic rendering at a prepared launch boundary, not subprocess interception."""
from __future__ import annotations

from contextlib import contextmanager, redirect_stdout
import os
import shlex
import sys
from typing import Iterator, Sequence


@contextmanager
def preparation_diagnostics() -> Iterator[None]:
    """Reserve stdout for the result of this foreground CLI operation.

    redirect_stdout covers Python writers; descriptor redirection also covers
    inherited output from image preparation's child processes. Restore both on
    failure. This is scoped to project-run printing, never applied to normal run.
    """
    sys.stdout.flush()
    sys.stderr.flush()
    saved = os.dup(1)
    try:
        os.dup2(2, 1)
        with redirect_stdout(sys.stderr):
            yield
    finally:
        try:
            sys.stderr.flush()
        finally:
            os.dup2(saved, 1)
            os.close(saved)


def render_command(command: Sequence[str], comments: Sequence[str]) -> str:
    """Comments are separate shell lines, never embedded in a continuation."""
    explanation = "".join("# " + line + "\n" for comment in comments for line in comment.splitlines())
    return explanation + " \\\n  ".join(shlex.quote(arg) for arg in command) + "\n"
