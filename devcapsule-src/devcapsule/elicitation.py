"""The one-elicitation engine: each answer is sought once, in a fixed order.

*One Elicitation: Init Ends Resolved* (see
``engineering-docs/design-notes/devcapsule/v1-user-experience.md``): for any
node, the value is sought in one fixed order, and a prompt is only ever the
last resort:

1. the command line;
2. an answer already given earlier in the same flow;
3. an existing record — manifest, lock, or checkout configuration;
4. a derivable default;
5. otherwise, if the node is mandatory: prompt, ``ssh-keygen`` style.

Asking a question whose answer exists upstream of step 5 is a defect, and so
is silently proceeding without a mandatory answer.  In a noninteractive
context, a mandatory node that reaches step 5 is collected rather than fatal,
so :meth:`Elicitor.finish` can fail once listing **all** missing nodes with
their canonical names — batch mode, not death at the first missing answer.

The engine holds no persistent answer cache and performs no file IO: callers
pass what the existing artifacts already record, and write each returned
answer into the artifact that owns it.  A persistent cache would be a fifth
artifact with no owner in *Four Things With Different Owners*.
"""

from __future__ import annotations

from dataclasses import dataclass
import sys
from typing import Callable, Mapping, TextIO

from devcapsule.compat import CliError

__all__ = [
    "AnswerKey",
    "Elicited",
    "ElicitationIncomplete",
    "Elicitor",
    "FACET_JUSTIFICATION",
    "FACET_VALUE",
    "SOURCE_COMMAND_LINE",
    "SOURCE_DEFAULT",
    "SOURCE_EARLIER_ANSWER",
    "SOURCE_EXISTING_RECORD",
    "SOURCE_PROMPT",
]


# A node's answer and, where the schema demands one, its justification are
# distinct facets of the same node: they share the canonical name and differ
# only in this second key component.
FACET_VALUE = "value"
FACET_JUSTIFICATION = "justification"

# The five steps of the settled elicitation order, recorded as each answer's
# provenance so "derive and report" can show where a value came from.
SOURCE_COMMAND_LINE = "command-line"
SOURCE_EARLIER_ANSWER = "earlier-answer"
SOURCE_EXISTING_RECORD = "existing-record"
SOURCE_DEFAULT = "default"
SOURCE_PROMPT = "prompt"

AnswerKey = tuple[str, str]


class ElicitationIncomplete(CliError):
    """Mandatory answers are missing or supplied answers matched no node."""


@dataclass(frozen=True)
class Elicited:
    """One answered node facet with its provenance."""

    name: str
    facet: str
    value: str
    source: str


@dataclass(frozen=True)
class _Missing:
    name: str
    facet: str
    remedy: str


class Elicitor:
    """Seek answers in the fixed order for one command invocation.

    ``command_line`` maps ``(name, facet)`` to the value supplied through the
    carrier options or dedicated flags.  ``interactive`` defaults to whether
    stdin is a terminal; tests and noninteractive callers pass it explicitly.
    """

    def __init__(
        self,
        command_line: Mapping[AnswerKey, str] | None = None,
        *,
        interactive: bool | None = None,
        input_stream: TextIO | None = None,
        output_stream: TextIO | None = None,
    ) -> None:
        self._command_line = dict(command_line or {})
        self._interactive = sys.stdin.isatty() if interactive is None else interactive
        self._input = input_stream if input_stream is not None else sys.stdin
        self._output = output_stream if output_stream is not None else sys.stdout
        self._answers: dict[AnswerKey, Elicited] = {}
        self._consumed: set[AnswerKey] = set()
        self._missing: list[_Missing] = []

    def seek(
        self,
        name: str,
        *,
        facet: str = FACET_VALUE,
        description: str,
        remedy: str,
        mandatory: bool = True,
        existing: str | None = None,
        default: str | None = None,
        empty_answer: str | None = None,
        validate: Callable[[str], str] | None = None,
    ) -> Elicited | None:
        """Seek one node facet's answer; return None when it stays unanswered.

        ``existing`` is what the owning artifact already records (step 3);
        ``default`` is a derivable value that pre-empts prompting entirely
        (step 4).  ``empty_answer`` is different from ``default``: it is the
        interpretation of pressing Enter at the prompt — used for intent
        questions that must be *asked* but have a safe answer, which a
        derivable default would silently skip.  ``validate`` normalizes a
        candidate or raises :class:`CliError`; a bad command-line or recorded
        value fails immediately, while a bad prompted value re-asks.

        ``remedy`` is the exact command-line spelling that would answer this
        node, shown in the batch failure.
        """

        key = (name, facet)
        # Step 2 first in code, though it is second in the order: a repeated
        # seek returns the identical earlier answer, so the command line
        # (consumed on the first seek) can never disagree with it.
        recorded = self._answers.get(key)
        if recorded is not None:
            return recorded
        if key in self._command_line:
            self._consumed.add(key)
            value = self._command_line[key]
            return self._record(key, validate(value) if validate else value, SOURCE_COMMAND_LINE)
        if existing is not None:
            return self._record(
                key, validate(existing) if validate else existing, SOURCE_EXISTING_RECORD
            )
        if default is not None:
            return self._record(key, default, SOURCE_DEFAULT)
        if not mandatory:
            return None
        if not self._interactive:
            self._missing.append(_Missing(name, facet, remedy))
            return None
        return self._prompt(key, description, empty_answer, validate, remedy)

    def missing(self) -> tuple[str, ...]:
        """Canonical names (with facet where not the value) still unanswered."""

        return tuple(_display_name(item.name, item.facet) for item in self._missing)

    def finish(self) -> None:
        """Fail once, listing every missing node and every unmatched answer.

        Unconsumed command-line answers are failures, not surplus: a typo'd
        node name that was silently ignored would let the user believe the
        answer was recorded.
        """

        problems: list[str] = []
        if self._missing:
            problems.append("Required configuration was not provided; supply each missing answer:")
            problems.extend(
                f"  {_display_name(item.name, item.facet)}: {item.remedy}"
                for item in self._missing
            )
        unconsumed = sorted(key for key in self._command_line if key not in self._consumed)
        if unconsumed:
            problems.append("These supplied answers matched no question this command asks:")
            problems.extend(f"  {_display_name(name, facet)}" for name, facet in unconsumed)
        if problems:
            raise ElicitationIncomplete("\n".join(problems))

    def _record(self, key: AnswerKey, value: str, source: str) -> Elicited:
        answer = Elicited(name=key[0], facet=key[1], value=value, source=source)
        self._answers[key] = answer
        return answer

    def _prompt(
        self,
        key: AnswerKey,
        description: str,
        empty_answer: str | None,
        validate: Callable[[str], str] | None,
        remedy: str,
    ) -> Elicited | None:
        hint = f" [{empty_answer}]" if empty_answer is not None else ""
        while True:
            self._output.write(f"{description}{hint}: ")
            self._output.flush()
            line = self._input.readline()
            if line == "":
                # End of input mid-prompt: fall back to the noninteractive
                # contract rather than looping or dying here.
                self._missing.append(_Missing(key[0], key[1], remedy))
                return None
            answer = line.rstrip("\n").strip()
            if not answer:
                if empty_answer is None:
                    self._output.write("A value is required.\n")
                    continue
                answer = empty_answer
            if validate is not None:
                try:
                    answer = validate(answer)
                except CliError as failure:
                    self._output.write(f"{failure}\n")
                    continue
            return self._record(key, answer, SOURCE_PROMPT)


def _display_name(name: str, facet: str) -> str:
    return name if facet == FACET_VALUE else f"{name} ({facet})"
