"""Small environment-option helpers for Docker argument diagnostics.

Docker remains responsible for parsing and validating its options. This module
recognizes the supported spellings of its repeatable environment option only.

Without Docker's option table, a token that looks like an environment option
right after a bare option (``--label -eNAME=value``) may be that option's
value instead: Docker takes the next token as the value whatever it looks
like. Such a token is *ambiguous*. Diagnostics mask it anyway; the commands
that edit or list saved environment variables leave it alone and say so.
"""
from __future__ import annotations
from typing import Iterator, Sequence


def _bare_option(token: str) -> bool:
    return token.startswith("-") and len(token) > 1 and "=" not in token


def scan_environment_options(arguments: Sequence[str]) -> Iterator[tuple[int, int, str, bool]]:
    """Every environment-looking option: ``(start, end, value, ambiguous)``."""
    index = 0
    previous_end = 0
    while index < len(arguments):
        token = arguments[index]
        if token in ("--env", "-e") and index + 1 < len(arguments):
            end, value = index + 2, arguments[index + 1]
        elif token.startswith("--env="):
            end, value = index + 1, token[len("--env="):]
        elif token.startswith("-e") and not token.startswith("--") and len(token) > 2:
            end, value = index + 1, token[2:].removeprefix("=")
        else:
            index += 1
            continue
        # Right after another environment option, whatever its own status,
        # this token cannot be an operand; after any other bare option it may be.
        ambiguous = index > previous_end and _bare_option(arguments[index - 1])
        yield index, end, value, ambiguous
        index = previous_end = end


def environment_options(arguments: Sequence[str]) -> Iterator[tuple[int, int, str]]:
    """The unambiguous environment options only."""
    for start, end, value, ambiguous in scan_environment_options(arguments):
        if not ambiguous:
            yield start, end, value


def ambiguous_environment_options(arguments: Sequence[str]) -> list[tuple[int, int, str]]:
    return [(start, end, value) for start, end, value, ambiguous in scan_environment_options(arguments) if ambiguous]


def inline_environment_names(arguments: Sequence[str]) -> set[str]:
    return {value.partition("=")[0] for _, _, value, _ in scan_environment_options(arguments) if "=" in value}


def redact_environment(arguments: Sequence[str], names: set[str] | None = None) -> list[str]:
    """Mask inline values, ambiguous tokens included: over-masking a diagnostic is harmless."""
    result = list(arguments)
    for start, end, value, _ in scan_environment_options(arguments):
        key, equal, _ = value.partition("=")
        if equal and (names is None or key in names):
            index = end - 1
            result[index] = result[index][:len(result[index]) - len(value)] + key + "=<redacted>"
    return result
