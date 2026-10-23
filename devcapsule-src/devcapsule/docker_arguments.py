"""Small environment-option helpers for Docker argument diagnostics.

Docker remains responsible for parsing and validating its options. This module
recognizes the supported spellings of its repeatable environment option only.

Without Docker's option table, a token that looks like an environment option
right after a bare option (``--label -eNAME=value``) may be that option's
value instead: Docker takes the next token as the value whatever it looks
like. Such a token is *ambiguous*, and when it is a split spelling
(``--label --env --env NAME=value``) the token after it is unresolved too:
an option if the first was the operand, the operand if the first was real.
The scan therefore considers every token a candidate unless an unambiguous
option consumed it. Diagnostics mask every candidate's value; the commands
that edit or list saved environment variables refuse any ambiguity.
"""
from __future__ import annotations
from typing import Iterator, Sequence


def _bare_option(token: str) -> bool:
    return token.startswith("-") and len(token) > 1 and "=" not in token


def _attached_environment(token: str) -> bool:
    return token.startswith("-e") and not token.startswith("--") and len(token) > 2


def scan_environment_options(arguments: Sequence[str]) -> Iterator[tuple[int, int, str, bool]]:
    """Every environment-looking option: ``(start, end, value, ambiguous)``.

    Ambiguous split spellings overlap the candidate that follows them.
    """
    index = 0
    resolved_end = 0  # the end of the last unambiguous option; its value is no candidate
    while index < len(arguments):
        token = arguments[index]
        if token in ("--env", "-e") and index + 1 < len(arguments):
            end, value = index + 2, arguments[index + 1]
        elif token.startswith("--env="):
            end, value = index + 1, token[len("--env="):]
        elif _attached_environment(token):
            end, value = index + 1, token[2:].removeprefix("=")
        else:
            index += 1
            continue
        # The token before may still take this one as its operand when it is a
        # bare option that is neither self-contained (-eNAME) nor the value of
        # a resolved option. Then nothing here is settled.
        previous = arguments[index - 1] if index > resolved_end else None
        ambiguous = previous is not None and _bare_option(previous) and not _attached_environment(previous)
        yield index, end, value, ambiguous
        if ambiguous:
            index += 1  # the next token may be a real option: look at it too
        else:
            index = resolved_end = end


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
    """Mask every candidate's inline value, ambiguous and overlapping ones
    included: over-masking a diagnostic is harmless. Each token is masked
    from its original text, so overlapping views agree on the result."""
    result = list(arguments)
    for start, end, value, _ in scan_environment_options(arguments):
        key, equal, _ = value.partition("=")
        if equal and (names is None or key in names):
            index = end - 1
            original = arguments[index]
            result[index] = original[:len(original) - len(value)] + key + "=<redacted>"
    return result
