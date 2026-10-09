"""Decision pages: an agent's question as a document, the human's answer as another.

Deliverable 5 of the capsule web console work order; the contract is in
``DECISIONS.md`` beside the package. An agent writes ``<id>.json`` into the
decisions directory, the console renders it, the human answers, the console
writes ``<id>.answer.json``, and the agent reads it back. Nothing here is a
record; the agent records the outcome in the normal files and deletes both.

The answer write is the console's one write operation, which the work order
allows for this deliverable and nothing else.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence

FORMAT = 1
DECISIONS_ENV = "DEVCAPSULE_CONSOLE_DECISIONS"
DEFAULT_SUBDIRECTORY = Path("devcapsule") / "decisions"
KEY_PATTERN = re.compile(r"[a-z0-9][a-z0-9-]{0,99}")
DEFAULT_OPTIONS = (
    {"key": "accept", "label": "Accept", "summary": "Take it as a task."},
    {"key": "decline", "label": "Decline", "summary": "Close it with a reason."},
    {"key": "defer", "label": "Defer", "summary": "Leave it in intake."},
)
MAXIMUM_DOCUMENT_BYTES = 1024 * 1024
MAXIMUM_ANSWER_BYTES = 64 * 1024


class DecisionError(ValueError):
    """A decision or answer document does not follow the contract; the message says where."""


def default_directory(environ: Mapping[str, str] = os.environ) -> Path:
    """``$DEVCAPSULE_CONSOLE_DECISIONS``, else ``$XDG_STATE_HOME/devcapsule/decisions``."""
    named = environ.get(DECISIONS_ENV)
    if named:
        return Path(named)
    state = environ.get("XDG_STATE_HOME") or str(Path.home() / ".local" / "state")
    return Path(state) / DEFAULT_SUBDIRECTORY


@dataclass(frozen=True)
class Option:
    key: str
    label: str
    summary: str = ""


@dataclass(frozen=True)
class Item:
    key: str
    title: str
    options: tuple[Option, ...]
    summary: str = ""
    records: tuple[str, ...] = ()
    multiple: bool = False


@dataclass(frozen=True)
class Decision:
    id: str
    title: str
    items: tuple[Item, ...]
    asked_by: str = ""
    asked_at: str = ""
    context: str = ""

    def to_mapping(self) -> dict[str, Any]:
        return {
            "format": FORMAT, "id": self.id, "title": self.title, "asked-by": self.asked_by,
            "asked-at": self.asked_at, "context": self.context,
            "items": [{
                "key": item.key, "title": item.title, "summary": item.summary, "records": list(item.records),
                "options": [{"key": option.key, "label": option.label, "summary": option.summary} for option in item.options],
                "multiple": item.multiple,
            } for item in self.items],
        }

    def item(self, key: str) -> Item | None:
        return next((item for item in self.items if item.key == key), None)


@dataclass(frozen=True)
class Answer:
    id: str
    answered_at: str
    answers: dict[str, dict[str, Any]] = field(default_factory=dict)
    note: str = ""

    def to_mapping(self) -> dict[str, Any]:
        return {"format": FORMAT, "id": self.id, "answered-at": self.answered_at, "answers": self.answers, "note": self.note}


def _key(value: object, where: str) -> str:
    if not isinstance(value, str) or KEY_PATTERN.fullmatch(value) is None:
        raise DecisionError(f"{where} must be lowercase letters, digits and hyphens, at most 100 characters")
    return value


def _text(value: object, where: str, *, required: bool = False) -> str:
    if value is None and not required:
        return ""
    if not isinstance(value, str) or (required and not value.strip()):
        raise DecisionError(f"{where} must be a {'non-empty ' if required else ''}string")
    return value


def decision_from_mapping(document: object) -> Decision:
    """Validate a decision document; every refusal names the field."""
    if not isinstance(document, dict):
        raise DecisionError("a decision must be a JSON object")
    if document.get("format") != FORMAT:
        raise DecisionError(f"format must be {FORMAT}")
    items_value = document.get("items")
    if not isinstance(items_value, list) or not items_value:
        raise DecisionError("items must be a non-empty array")
    items: list[Item] = []
    for index, item_value in enumerate(items_value):
        where = f"items[{index}]"
        if not isinstance(item_value, dict):
            raise DecisionError(f"{where} must be an object")
        options_value = item_value.get("options")
        if not isinstance(options_value, list) or len(options_value) < 2:
            raise DecisionError(f"{where}.options must hold at least two options")
        options: list[Option] = []
        for option_index, option_value in enumerate(options_value):
            option_where = f"{where}.options[{option_index}]"
            if not isinstance(option_value, dict):
                raise DecisionError(f"{option_where} must be an object")
            options.append(Option(
                _key(option_value.get("key"), f"{option_where}.key"),
                _text(option_value.get("label"), f"{option_where}.label", required=True),
                _text(option_value.get("summary"), f"{option_where}.summary"),
            ))
        if len({option.key for option in options}) != len(options):
            raise DecisionError(f"{where}.options must have unique keys")
        records_value = item_value.get("records", [])
        if not isinstance(records_value, list) or not all(isinstance(record, str) and record for record in records_value):
            raise DecisionError(f"{where}.records must be an array of paths")
        multiple = item_value.get("multiple", False)
        if not isinstance(multiple, bool):
            raise DecisionError(f"{where}.multiple must be true or false")
        items.append(Item(
            _key(item_value.get("key"), f"{where}.key"),
            _text(item_value.get("title"), f"{where}.title", required=True),
            tuple(options),
            _text(item_value.get("summary"), f"{where}.summary"),
            tuple(records_value),
            multiple,
        ))
    if len({item.key for item in items}) != len(items):
        raise DecisionError("items must have unique keys")
    return Decision(
        _key(document.get("id"), "id"),
        _text(document.get("title"), "title", required=True),
        tuple(items),
        _text(document.get("asked-by"), "asked-by"),
        _text(document.get("asked-at"), "asked-at"),
        _text(document.get("context"), "context"),
    )


def answer_from_mapping(decision: Decision, document: object, *, answered_at: str | None = None) -> Answer:
    """Validate an answer against its decision: known items, known options, one choice unless multiple."""
    if not isinstance(document, dict):
        raise DecisionError("an answer must be a JSON object")
    if document.get("format", FORMAT) != FORMAT:
        raise DecisionError(f"format must be {FORMAT}")
    if document.get("id", decision.id) != decision.id:
        raise DecisionError(f"id must be {decision.id!r}")
    answers_value = document.get("answers", {})
    if not isinstance(answers_value, dict):
        raise DecisionError("answers must be an object keyed by item")
    answers: dict[str, dict[str, Any]] = {}
    for item_key, answer_value in answers_value.items():
        item = decision.item(str(item_key))
        if item is None:
            raise DecisionError(f"answers names an unknown item {item_key!r}")
        if not isinstance(answer_value, dict):
            raise DecisionError(f"answers[{item_key!r}] must be an object")
        chosen = answer_value.get("chosen", [])
        if not isinstance(chosen, list) or not all(isinstance(choice, str) for choice in chosen):
            raise DecisionError(f"answers[{item_key!r}].chosen must be an array of option keys")
        known = {option.key for option in item.options}
        unknown = [choice for choice in chosen if choice not in known]
        if unknown:
            raise DecisionError(f"answers[{item_key!r}] names unknown options {unknown!r}")
        if len(set(chosen)) != len(chosen):
            raise DecisionError(f"answers[{item_key!r}] repeats an option")
        if not item.multiple and len(chosen) > 1:
            raise DecisionError(f"answers[{item_key!r}] chooses several options for a single-choice item")
        answers[item.key] = {"chosen": list(chosen), "note": _text(answer_value.get("note"), f"answers[{item_key!r}].note")}
    return Answer(decision.id, answered_at or _now(), answers, _text(document.get("note"), "note"))


@dataclass(frozen=True)
class DecisionStore:
    """The decisions directory: read decisions and answers, write answers atomically."""

    directory: Path

    def decision_path(self, decision_id: str) -> Path:
        return self.directory / f"{_key(decision_id, 'id')}.json"

    def answer_path(self, decision_id: str) -> Path:
        return self.directory / f"{_key(decision_id, 'id')}.answer.json"

    def list_ids(self) -> list[str]:
        """Every decision in the directory, by id, oldest file first."""
        if not self.directory.is_dir():
            return []
        found = []
        for path in self.directory.glob("*.json"):
            if path.name.endswith(".answer.json") or KEY_PATTERN.fullmatch(path.stem) is None or not path.is_file():
                continue
            found.append((path.stat().st_mtime, path.stem))
        return [decision_id for _, decision_id in sorted(found)]

    def read_decision(self, decision_id: str) -> Decision:
        path = self.decision_path(decision_id)
        try:
            raw = path.read_bytes()
        except FileNotFoundError:
            raise
        except OSError as error:
            raise DecisionError(f"cannot read {path.name}: {error}") from error
        if len(raw) > MAXIMUM_DOCUMENT_BYTES:
            raise DecisionError(f"{path.name} is larger than {MAXIMUM_DOCUMENT_BYTES} bytes")
        try:
            document = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, ValueError) as error:
            raise DecisionError(f"{path.name} is not a JSON document: {error}") from error
        decision = decision_from_mapping(document)
        if decision.id != decision_id:
            raise DecisionError(f"{path.name} carries id {decision.id!r}; the file name is the id")
        return decision

    def read_answer(self, decision: Decision) -> Answer | None:
        path = self.answer_path(decision.id)
        try:
            raw = path.read_bytes()
        except FileNotFoundError:
            return None
        except OSError as error:
            raise DecisionError(f"cannot read {path.name}: {error}") from error
        try:
            document = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, ValueError) as error:
            raise DecisionError(f"{path.name} is not a JSON document: {error}") from error
        if not isinstance(document, dict):
            raise DecisionError(f"{path.name} must be a JSON object")
        answered_at = document.get("answered-at")
        return answer_from_mapping(decision, document, answered_at=answered_at if isinstance(answered_at, str) else _now())

    def write_answer(self, answer: Answer) -> Path:
        """Write the answer beside its decision: a temporary file, then one rename."""
        path = self.answer_path(answer.id)
        self.directory.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
        temporary.write_text(json.dumps(answer.to_mapping(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temporary.replace(path)
        return path


def from_markdown_table(text: str, *, decision_id: str, title: str, asked_by: str = "", context: str = "") -> Decision:
    """A decision from a markdown table: ``key`` and ``title`` columns required.

    Optional columns: ``summary``; ``records``, paths separated by spaces;
    ``options``, ``key:Label`` pairs separated by commas, else accept,
    decline and defer; ``multiple``, ``yes`` for several choices.
    """
    rows = [line.strip() for line in text.splitlines() if line.strip().startswith("|")]
    if len(rows) < 3:
        raise DecisionError("the table needs a header row, a separator row and at least one item row")
    header = [cell.strip().lower() for cell in rows[0].strip("|").split("|")]
    for required in ("key", "title"):
        if required not in header:
            raise DecisionError(f"the table needs a {required!r} column")
    items = []
    for row in rows[2:]:
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        if len(cells) != len(header):
            raise DecisionError(f"row {row!r} has {len(cells)} cells; the header has {len(header)}")
        values = dict(zip(header, cells))
        options_text = values.get("options", "")
        if options_text:
            options = []
            for pair in options_text.split(","):
                key, _, label = pair.strip().partition(":")
                options.append({"key": key.strip(), "label": label.strip() or key.strip()})
        else:
            options = [dict(option) for option in DEFAULT_OPTIONS]
        items.append({
            "key": values["key"], "title": values["title"], "summary": values.get("summary", ""),
            "records": [record for record in values.get("records", "").split() if record],
            "options": options, "multiple": values.get("multiple", "").strip().lower() in {"yes", "true"},
        })
    return decision_from_mapping({
        "format": FORMAT, "id": decision_id, "title": title, "asked-by": asked_by,
        "asked-at": _now(), "context": context, "items": items,
    })


def main(argv: Sequence[str] | None = None) -> int:
    """``python -m devcapsule_webconsole.decisions``: build or check decision documents."""
    parser = argparse.ArgumentParser(prog="devcapsule-webconsole decisions", description=main.__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    table = commands.add_parser("from-table", help="Print a decision document built from a markdown table.")
    table.add_argument("table", type=Path, help="A markdown file holding the table; '-' for standard input.")
    table.add_argument("--id", required=True, help="The decision id and file stem.")
    table.add_argument("--title", required=True)
    table.add_argument("--asked-by", default="")
    table.add_argument("--context", default="", help="Markdown shown above the items.")
    check = commands.add_parser("check", help="Validate a decision document, and its answer when present.")
    check.add_argument("decision", type=Path)
    arguments = parser.parse_args(list(sys.argv[1:] if argv is None else argv))
    try:
        if arguments.command == "from-table":
            text = sys.stdin.read() if str(arguments.table) == "-" else arguments.table.read_text(encoding="utf-8")
            decision = from_markdown_table(text, decision_id=arguments.id, title=arguments.title,
                                           asked_by=arguments.asked_by, context=arguments.context)
            print(json.dumps(decision.to_mapping(), indent=2))
            return 0
        store = DecisionStore(arguments.decision.parent)
        decision = store.read_decision(arguments.decision.stem)
        answer = store.read_answer(decision)
        print(f"{decision.id}: {len(decision.items)} item(s); " + (f"answered {answer.answered_at}" if answer else "unanswered"))
        return 0
    except (DecisionError, OSError) as error:
        print(f"devcapsule-webconsole decisions: {error}", file=sys.stderr)
        return 2


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


if __name__ == "__main__":
    raise SystemExit(main())
