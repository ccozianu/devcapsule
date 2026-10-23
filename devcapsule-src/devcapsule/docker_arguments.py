"""Small environment-option helpers for Docker argument diagnostics.

Docker remains responsible for parsing and validating its options. This module
recognizes the supported spellings of its repeatable environment option only.
"""
from __future__ import annotations
from typing import Iterator, Sequence


def environment_options(arguments: Sequence[str]) -> Iterator[tuple[int, int, str]]:
    index = 0
    while index < len(arguments):
        token = arguments[index]
        if token in ("--env", "-e") and index + 1 < len(arguments):
            yield index, index + 2, arguments[index + 1]
            index += 2
            continue
        if token.startswith("--env="):
            yield index, index + 1, token[len("--env="):]
        elif token.startswith("-e") and not token.startswith("--") and len(token) > 2:
            yield index, index + 1, token[2:].removeprefix("=")
        index += 1


def inline_environment_names(arguments: Sequence[str]) -> set[str]:
    return {value.partition("=")[0] for _, _, value in environment_options(arguments) if "=" in value}


def redact_environment(arguments: Sequence[str], names: set[str] | None = None) -> list[str]:
    result = list(arguments)
    for start, end, value in environment_options(arguments):
        key, equal, _ = value.partition("=")
        if equal and (names is None or key in names):
            index = end - 1
            result[index] = result[index][:len(result[index]) - len(value)] + key + "=<redacted>"
    return result
