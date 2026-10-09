"""Decision pages: the contract, the store, the table builder, and the one write route."""

from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import re

import pytest
from fastapi.testclient import TestClient

from conftest import TOKEN, with_token
from devcapsule_webconsole import decisions
from devcapsule_webconsole.app import create_app
from devcapsule_webconsole.decisions import (
    Answer, DecisionError, DecisionStore, answer_from_mapping, decision_from_mapping, default_directory,
    from_markdown_table,
)

DECISION = {
    "format": 1, "id": "2026-10-09-intake-pass", "title": "Intake disposition pass",
    "asked-by": "project-management", "asked-at": "2026-10-09T18:00:00+00:00",
    "context": "Two items wait. **Decide** each.",
    "items": [
        {"key": "blog", "title": "A development blog", "summary": "Worth it?",
         "records": ["docs/guide.md"],
         "options": [{"key": "accept", "label": "Accept"}, {"key": "decline", "label": "Decline", "summary": "Close it."}],
         "multiple": False},
        {"key": "naming", "title": "Naming", "options": [{"key": "a", "label": "A"}, {"key": "b", "label": "B"}, {"key": "c", "label": "C"}],
         "multiple": True},
    ],
}


@pytest.fixture
def store(tmp_path: Path) -> DecisionStore:
    directory = tmp_path / "decisions"
    directory.mkdir()
    (directory / "2026-10-09-intake-pass.json").write_text(json.dumps(DECISION), encoding="utf-8")
    return DecisionStore(directory)


@pytest.fixture
def deciding_client(settings, store: DecisionStore):
    with TestClient(create_app(replace(settings, decisions=store.directory))) as client:
        client.headers["Origin"] = "http://testserver"
        yield with_token(client)


def test_a_decision_document_round_trips(store: DecisionStore):
    decision = store.read_decision("2026-10-09-intake-pass")
    assert decision.title == "Intake disposition pass" and decision.asked_by == "project-management"
    assert [item.key for item in decision.items] == ["blog", "naming"]
    assert decision.items[0].records == ("docs/guide.md",) and decision.items[1].multiple is True
    assert decision.items[0].options[1].summary == "Close it."
    assert decision_from_mapping(decision.to_mapping()) == decision
    assert store.list_ids() == ["2026-10-09-intake-pass"]
    assert store.read_answer(decision) is None


@pytest.mark.parametrize("change, message", [
    ({"format": 2}, "format must be 1"),
    ({"id": "Bad Id"}, "id must be lowercase"),
    ({"title": " "}, "title must be a non-empty string"),
    ({"items": []}, "items must be a non-empty array"),
    ({"items": [{"key": "x", "title": "X", "options": [{"key": "a", "label": "A"}]}]}, "items[0].options must hold at least two"),
    ({"items": [{"key": "x", "title": "X", "options": [{"key": "a", "label": "A"}, {"key": "a", "label": "B"}]}]}, "items[0].options must have unique keys"),
    ({"items": [{"key": "x", "title": "X", "options": [{"key": "a", "label": ""}, {"key": "b", "label": "B"}]}]}, "items[0].options[0].label must be a non-empty string"),
    ({"items": [{"key": "x", "title": "X", "records": "docs", "options": [{"key": "a", "label": "A"}, {"key": "b", "label": "B"}]}]}, "items[0].records must be an array"),
    ({"items": [{"key": "x", "title": "X", "multiple": "yes", "options": [{"key": "a", "label": "A"}, {"key": "b", "label": "B"}]}]}, "items[0].multiple must be true or false"),
    ({"items": [DECISION["items"][0], DECISION["items"][0]]}, "items must have unique keys"),
])
def test_malformed_decisions_are_refused_with_the_field_named(change, message):
    with pytest.raises(DecisionError, match=re.escape(message)):
        decision_from_mapping({**DECISION, **change})


def test_the_file_name_is_the_id(store: DecisionStore):
    (store.directory / "other-name.json").write_text(json.dumps(DECISION), encoding="utf-8")
    with pytest.raises(DecisionError, match="the file name is the id"):
        store.read_decision("other-name")
    (store.directory / "2026-10-09-intake-pass.answer.json").write_text("{}", encoding="utf-8")
    (store.directory / "Not A Decision.json").write_text("{}", encoding="utf-8")
    assert store.list_ids() == ["2026-10-09-intake-pass", "other-name"]
    with pytest.raises(FileNotFoundError):
        store.read_decision("absent")
    with pytest.raises(DecisionError, match="id must be lowercase"):
        store.read_decision("../escape")


def test_answers_are_validated_against_the_decision(store: DecisionStore):
    decision = store.read_decision("2026-10-09-intake-pass")
    answer = answer_from_mapping(decision, {"answers": {"blog": {"chosen": ["accept"], "note": "yes"}, "naming": {"chosen": ["a", "c"]}}, "note": "all"},
                                 answered_at="2026-10-09T18:12:40+00:00")
    assert answer == Answer("2026-10-09-intake-pass", "2026-10-09T18:12:40+00:00",
                            {"blog": {"chosen": ["accept"], "note": "yes"}, "naming": {"chosen": ["a", "c"], "note": ""}}, "all")
    for body, message in [
        ({"answers": {"other": {"chosen": ["accept"]}}}, "unknown item"),
        ({"answers": {"blog": {"chosen": ["maybe"]}}}, "unknown options"),
        ({"answers": {"blog": {"chosen": ["accept", "decline"]}}}, "several options for a single-choice item"),
        ({"answers": {"naming": {"chosen": ["a", "a"]}}}, "repeats an option"),
        ({"answers": {"blog": {"chosen": "accept"}}}, "must be an array of option keys"),
        ({"answers": []}, "answers must be an object"),
        ({"id": "other"}, "id must be"),
        ({"format": 0}, "format must be 1"),
        ([], "must be a JSON object"),
    ]:
        with pytest.raises(DecisionError, match=message):
            answer_from_mapping(decision, body)


def test_the_store_writes_answers_atomically_and_reads_them_back(store: DecisionStore):
    decision = store.read_decision("2026-10-09-intake-pass")
    answer = answer_from_mapping(decision, {"answers": {"blog": {"chosen": ["decline"]}}}, answered_at="2026-10-09T18:12:40+00:00")
    path = store.write_answer(answer)
    assert path == store.directory / "2026-10-09-intake-pass.answer.json"
    assert json.loads(path.read_text(encoding="utf-8")) == answer.to_mapping()
    assert [name for name in (p.name for p in store.directory.iterdir()) if name.startswith(".")] == []
    assert store.read_answer(decision) == answer
    later = answer_from_mapping(decision, {"answers": {"blog": {"chosen": ["accept"]}}}, answered_at="2026-10-09T18:20:00+00:00")
    store.write_answer(later)
    assert store.read_answer(decision) == later
    path.write_text("not json", encoding="utf-8")
    with pytest.raises(DecisionError, match="not a JSON document"):
        store.read_answer(decision)


def test_a_decision_is_built_from_a_markdown_table():
    table = """
| key | title | summary | records | options | multiple |
|---|---|---|---|---|---|
| blog | A development blog | Worth it? | docs/guide.md docs/other.md | | |
| naming | Naming | | | a:A, b:B, c | yes |
"""
    decision = from_markdown_table(table, decision_id="pass-1", title="Pass", asked_by="pm", context="ctx")
    assert decision.id == "pass-1" and decision.asked_by == "pm" and decision.context == "ctx"
    assert decision.asked_at.endswith("+00:00")
    blog, naming = decision.items
    assert blog.records == ("docs/guide.md", "docs/other.md")
    assert [option.key for option in blog.options] == ["accept", "decline", "defer"]
    assert [(option.key, option.label) for option in naming.options] == [("a", "A"), ("b", "B"), ("c", "c")]
    assert naming.multiple is True and blog.multiple is False
    with pytest.raises(DecisionError, match="needs a 'title' column"):
        from_markdown_table("| key |\n|---|\n| x |\n", decision_id="p", title="T")
    with pytest.raises(DecisionError, match="has 1 cells; the header has 2"):
        from_markdown_table("| key | title |\n|---|---|\n| x |\n", decision_id="p", title="T")
    with pytest.raises(DecisionError, match="at least one item row"):
        from_markdown_table("| key | title |\n|---|---|\n", decision_id="p", title="T")


def test_the_command_line_builds_and_checks_documents(tmp_path: Path, capsys, monkeypatch):
    table = tmp_path / "table.md"
    table.write_text("| key | title |\n|---|---|\n| one | One |\n| two | Two |\n", encoding="utf-8")
    assert decisions.main(["from-table", str(table), "--id", "pass-2", "--title", "Pass two", "--asked-by", "pm"]) == 0
    document = json.loads(capsys.readouterr().out)
    assert document["id"] == "pass-2" and [item["key"] for item in document["items"]] == ["one", "two"]
    directory = tmp_path / "decisions"
    directory.mkdir()
    (directory / "pass-2.json").write_text(json.dumps(document), encoding="utf-8")
    assert decisions.main(["check", str(directory / "pass-2.json")]) == 0
    assert capsys.readouterr().out == "pass-2: 2 item(s); unanswered\n"
    (directory / "pass-2.answer.json").write_text(json.dumps({"format": 1, "id": "pass-2", "answered-at": "2026-10-09T18:12:40+00:00", "answers": {"one": {"chosen": ["accept"]}}}), encoding="utf-8")
    assert decisions.main(["check", str(directory / "pass-2.json")]) == 0
    assert capsys.readouterr().out == "pass-2: 2 item(s); answered 2026-10-09T18:12:40+00:00\n"
    (directory / "pass-2.json").write_text("{}", encoding="utf-8")
    assert decisions.main(["check", str(directory / "pass-2.json")]) == 2
    assert "format must be 1" in capsys.readouterr().err
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    monkeypatch.delenv(decisions.DECISIONS_ENV, raising=False)
    assert default_directory() == tmp_path / "state" / "devcapsule" / "decisions"
    monkeypatch.setenv(decisions.DECISIONS_ENV, str(tmp_path / "named"))
    assert default_directory() == tmp_path / "named"


def test_the_pages_list_and_show_decisions(deciding_client):
    listing = deciding_client.get("/api/decisions")
    assert listing.status_code == 200
    assert listing.json() == {"decisions": [{"id": "2026-10-09-intake-pass", "title": "Intake disposition pass",
                                             "asked-by": "project-management", "asked-at": "2026-10-09T18:00:00+00:00",
                                             "items": 2, "answered-at": None}]}
    one = deciding_client.get("/api/decisions/2026-10-09-intake-pass")
    assert one.status_code == 200
    assert one.json() == {"decision": decision_from_mapping(DECISION).to_mapping(), "answer": None}
    assert deciding_client.get("/api/decisions/absent").status_code == 404
    assert deciding_client.get("/api/decisions/Bad%20Id").status_code == 404
    for route in ("/decisions", "/decisions/2026-10-09-intake-pass"):
        page = deciding_client.get(route)
        assert page.status_code == 200 and 'data-page="decisions"' in page.text


def test_answering_writes_the_answer_and_only_the_answer(deciding_client, store: DecisionStore, project: Path):
    before = sorted(p.name for p in store.directory.iterdir())
    body = {"answers": {"blog": {"chosen": ["accept"], "note": "yes"}}, "note": "done"}
    response = deciding_client.post("/api/decisions/2026-10-09-intake-pass/answer", json=body)
    assert response.status_code == 200
    written = json.loads((store.directory / "2026-10-09-intake-pass.answer.json").read_text(encoding="utf-8"))
    assert written["answers"] == {"blog": {"chosen": ["accept"], "note": "yes"}} and written["note"] == "done"
    assert response.json() == {"answer": written}
    assert sorted(p.name for p in store.directory.iterdir()) == sorted(before + ["2026-10-09-intake-pass.answer.json"])
    assert deciding_client.get("/api/decisions/2026-10-09-intake-pass").json()["answer"] == written
    assert deciding_client.get("/api/decisions").json()["decisions"][0]["answered-at"] == written["answered-at"]
    # The project itself is untouched: the answer is capsule state, not a record.
    assert not any(p.name.endswith(".answer.json") for p in project.rglob("*"))


@pytest.mark.parametrize("body, status, message", [
    ({"answers": {"blog": {"chosen": ["maybe"]}}}, 422, "unknown options"),
    ({"answers": {"other": {"chosen": ["accept"]}}}, 422, "unknown item"),
    ("not json", 422, "JSON"),
])
def test_a_bad_answer_is_refused_and_nothing_is_written(deciding_client, store: DecisionStore, body, status, message):
    kwargs = {"json": body} if not isinstance(body, str) else {"content": body, "headers": {"content-type": "application/json"}}
    response = deciding_client.post("/api/decisions/2026-10-09-intake-pass/answer", **kwargs)
    assert response.status_code == status and message in response.text
    assert not (store.directory / "2026-10-09-intake-pass.answer.json").exists()
    assert deciding_client.post("/api/decisions/absent/answer", json={"answers": {}}).status_code == 404


def test_the_answer_route_accepts_same_origin_requests_only(deciding_client, store: DecisionStore):
    refused = deciding_client.post("/api/decisions/2026-10-09-intake-pass/answer", json={"answers": {}},
                                   headers={"Origin": "http://evil.example"})
    assert refused.status_code == 403 and "origin" in refused.text.lower()
    assert not (store.directory / "2026-10-09-intake-pass.answer.json").exists()
    accepted = deciding_client.post("/api/decisions/2026-10-09-intake-pass/answer", json={"answers": {}},
                                    headers={"Origin": "http://testserver"})
    assert accepted.status_code == 200


def test_the_answer_route_needs_the_token(client, store: DecisionStore, settings):
    with TestClient(create_app(replace(settings, decisions=store.directory))) as anonymous:
        assert anonymous.post("/api/decisions/2026-10-09-intake-pass/answer", json={"answers": {}}).status_code == 403
        assert anonymous.get("/decisions").status_code == 403
    assert not (store.directory / "2026-10-09-intake-pass.answer.json").exists()


def test_a_malformed_decision_file_is_reported_not_served(deciding_client, store: DecisionStore):
    (store.directory / "broken.json").write_text("{\"format\": 1}", encoding="utf-8")
    listing = deciding_client.get("/api/decisions").json()
    assert [entry["id"] for entry in listing["decisions"]] == ["2026-10-09-intake-pass", "broken"]
    broken = next(entry for entry in listing["decisions"] if entry["id"] == "broken")
    assert broken["title"] is None and "items must be a non-empty array" in broken["error"]
    one = deciding_client.get("/api/decisions/broken")
    assert one.status_code == 422 and "items must be a non-empty array" in one.text


def test_an_absent_decisions_directory_lists_nothing(settings, tmp_path: Path):
    with TestClient(create_app(replace(settings, decisions=tmp_path / "none"))) as client:
        assert with_token(client).get("/api/decisions").json() == {"decisions": []}
        assert with_token(client).get("/decisions").status_code == 200


def test_settings_name_the_decisions_directory(project: Path, tmp_path: Path, monkeypatch):
    from devcapsule_webconsole.settings import settings_from_arguments
    token = tmp_path / "token"
    token.write_text("abc123\n", encoding="utf-8")
    monkeypatch.delenv(decisions.DECISIONS_ENV, raising=False)
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    assert settings_from_arguments(["--project", str(project), "--token-file", str(token)], dict(os_environ_for(tmp_path))).decisions == tmp_path / "state" / "devcapsule" / "decisions"
    explicit = settings_from_arguments(["--project", str(project), "--token-file", str(token), "--decisions", str(tmp_path / "d")], {})
    assert explicit.decisions == tmp_path / "d"


def os_environ_for(tmp_path: Path) -> dict[str, str]:
    return {"XDG_STATE_HOME": str(tmp_path / "state")}


@pytest.mark.parametrize("origin", [None, "null", "https://testserver", "http://testserver:81", "http://testserver/", "http://testserver.evil"])
def test_answer_requires_an_exact_origin(deciding_client, store, origin):
    deciding_client.headers.pop("origin", None)
    headers = {} if origin is None else {"Origin": origin}
    response = deciding_client.post("/api/decisions/2026-10-09-intake-pass/answer", json={}, headers=headers)
    assert response.status_code == 403
    assert not store.answer_path(DECISION["id"]).exists()


def test_invalid_choices_are_not_reported_as_invalid_json(deciding_client):
    response = deciding_client.post("/api/decisions/2026-10-09-intake-pass/answer",
                                   json={"answers": {"blog": {"chosen": ["unknown"]}}})
    assert response.status_code == 422
    assert response.text.startswith("the answer does not fit the decision:")


def test_answer_body_limit_stops_reading_before_the_next_chunk(deciding_client, store, monkeypatch):
    from starlette.requests import Request

    async def chunks(self):
        yield b" " * (decisions.MAXIMUM_ANSWER_BYTES + 1)
        pytest.fail("read beyond the answer limit")

    monkeypatch.setattr(Request, "stream", chunks)
    response = deciding_client.post("/api/decisions/2026-10-09-intake-pass/answer", content=b"ignored")
    assert response.status_code == 413
    assert not store.answer_path(DECISION["id"]).exists()


def test_predictable_temporary_symlink_cannot_overwrite_a_record(store, tmp_path):
    import os
    record = tmp_path / "record.md"
    record.write_text("Keep this record.\n")
    trap = store.directory / f".{DECISION['id']}.answer.json.{os.getpid()}.tmp"
    trap.symlink_to(record)
    answer = answer_from_mapping(decision_from_mapping(DECISION), {"note": "human"})
    store.write_answer(answer)
    assert record.read_text() == "Keep this record.\n"
    assert store.read_answer(decision_from_mapping(DECISION)) == answer


def test_overlapping_answer_writes_publish_complete_documents(store, monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    rendezvous = Barrier(2)
    original = Path.replace

    def together(source, target):
        rendezvous.wait(timeout=5)
        return original(source, target)

    monkeypatch.setattr(Path, "replace", together)
    decision = decision_from_mapping(DECISION)
    answers = [answer_from_mapping(decision, {"note": note}) for note in ("first", "second")]
    with ThreadPoolExecutor(2) as pool:
        assert list(pool.map(store.write_answer, answers)) == [store.answer_path(decision.id)] * 2
    assert store.read_answer(decision) in answers
    assert not list(store.directory.glob(".*.tmp"))


def test_failed_answer_replace_preserves_previous_answer_and_removes_temporary(store, monkeypatch):
    decision = decision_from_mapping(DECISION)
    old = answer_from_mapping(decision, {"note": "old"})
    store.write_answer(old)

    def denied(source, target):
        raise PermissionError("replace denied")

    monkeypatch.setattr(Path, "replace", denied)
    with pytest.raises(PermissionError, match="replace denied"):
        store.write_answer(answer_from_mapping(decision, {"note": "new"}))
    assert store.read_answer(decision) == old
    assert not list(store.directory.glob(".*.tmp"))


@pytest.mark.parametrize("answer_file", [False, True])
def test_store_refuses_symlink_documents(store, tmp_path, answer_file):
    decision = decision_from_mapping(DECISION)
    path = store.answer_path(decision.id) if answer_file else store.decision_path(decision.id)
    external = tmp_path / "external.json"
    external.write_text(json.dumps({"note": "private", "answered-at": "2026-10-09T18:12:40+00:00"} if answer_file else DECISION))
    path.unlink(missing_ok=True)
    path.symlink_to(external)
    with pytest.raises(DecisionError, match="cannot read"):
        store.read_answer(decision) if answer_file else store.read_decision(decision.id)


@pytest.mark.parametrize("answer_file", [False, True])
def test_disk_document_reads_are_bounded(store, monkeypatch, answer_file):
    decision = decision_from_mapping(DECISION)
    path = store.answer_path(decision.id) if answer_file else store.decision_path(decision.id)
    path.write_bytes(b" " * (decisions.MAXIMUM_DOCUMENT_BYTES + 1))
    sizes = []

    # Observe the underlying descriptor read without allocating a huge fixture.
    original_fdopen = decisions.os.fdopen
    class CheckedReader:
        def __init__(self, stream):
            self.stream = stream
        def __enter__(self):
            return self
        def __exit__(self, *args):
            self.stream.close()
        def read(self, size=-1):
            sizes.append(size)
            assert 0 < size <= decisions.MAXIMUM_DOCUMENT_BYTES + 1
            return self.stream.read(size)
    monkeypatch.setattr(decisions.os, "fdopen", lambda *args, **kwargs: CheckedReader(original_fdopen(*args, **kwargs)))
    with pytest.raises(DecisionError, match="larger than"):
        store.read_answer(decision) if answer_file else store.read_decision(decision.id)
    assert sizes == [decisions.MAXIMUM_DOCUMENT_BYTES + 1]


def test_list_survives_agent_removing_a_decision(deciding_client, store, monkeypatch):
    original = DecisionStore.read_decision
    def removed(self, decision_id):
        if decision_id == DECISION["id"]:
            self.decision_path(decision_id).unlink()
        return original(self, decision_id)
    monkeypatch.setattr(DecisionStore, "read_decision", removed)
    assert deciding_client.get("/api/decisions").json() == {"decisions": []}


@pytest.mark.parametrize("raw", [b"[" * 10000 + b"]" * 10000, b'"\\ud800"', b"\xff"])
def test_bad_json_values_do_not_crash_routes(deciding_client, store, raw):
    response = deciding_client.post("/api/decisions/2026-10-09-intake-pass/answer", content=raw)
    assert response.status_code == 422
    assert not store.answer_path(DECISION["id"]).exists()
    store.decision_path(DECISION["id"]).write_bytes(raw)
    assert deciding_client.get("/api/decisions/" + DECISION["id"]).status_code == 422
    assert "error" in deciding_client.get("/api/decisions").json()["decisions"][0]


def test_surrogate_text_is_refused_before_writing(deciding_client, store):
    response = deciding_client.post("/api/decisions/2026-10-09-intake-pass/answer", content=b'{"note":"\\ud800"}')
    assert response.status_code == 422
    assert not store.answer_path(DECISION["id"]).exists()
    store.decision_path(DECISION["id"]).write_text(json.dumps({**DECISION, "title": "\ud800"}))
    assert deciding_client.get("/api/decisions/" + DECISION["id"]).status_code == 422


def test_table_keeps_empty_edge_cells():
    decision = from_markdown_table("|key|title|summary|\n|---|---|---|\n|one|One||", decision_id="p", title="Pass")
    assert decision.items[0].summary == ""


@pytest.mark.parametrize("table, message", [
    ("|key|title|\n|one|One|\n|two|Two|", "separator"),
    ("|key|title|title|\n|---|---|---|\n|one|One|Other|", "unique"),
])
def test_ambiguous_tables_are_refused(table, message):
    with pytest.raises(DecisionError, match=message):
        from_markdown_table(table, decision_id="p", title="Pass")


def test_decision_script_behaviour():
    import shutil
    import subprocess
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node is a development-only script test dependency")
    subprocess.run([node, str(Path(__file__).with_name("decisions-script.cjs"))], check=True)


@pytest.mark.parametrize("value", [True, 1.0, "1"])
def test_format_is_an_integer_not_a_boolean_or_float(value):
    with pytest.raises(DecisionError, match="format must be 1"):
        decision_from_mapping({**DECISION, "format": value})
    with pytest.raises(DecisionError, match="format must be 1"):
        answer_from_mapping(decision_from_mapping(DECISION), {"format": value})


@pytest.mark.parametrize("value, message", [
    (None, "JSON object"), ({**DECISION, "items": [None]}, "must be an object"),
    ({**DECISION, "items": [{**DECISION["items"][0], "options": [None, None]}]}, "options[0] must be an object"),
    ({**DECISION, "context": 3}, "context must be a string"),
])
def test_decision_object_and_text_refusals(value, message):
    with pytest.raises(DecisionError, match=re.escape(message)):
        decision_from_mapping(value)


@pytest.mark.parametrize("document, message", [
    ({"answers": {"blog": None}}, "must be an object"),
    ({"answers": {"blog": {"chosen": [1]}}}, "array of option keys"),
    ({"answers": {"blog": {"note": 1}}}, "must be a string"),
])
def test_answer_object_and_text_refusals(document, message):
    with pytest.raises(DecisionError, match=message):
        answer_from_mapping(decision_from_mapping(DECISION), document)


@pytest.mark.parametrize("answer_file", [False, True])
def test_special_files_are_refused_without_blocking(store, answer_file):
    import os
    decision = decision_from_mapping(DECISION)
    path = store.answer_path(decision.id) if answer_file else store.decision_path(decision.id)
    path.unlink(missing_ok=True)
    os.mkfifo(path)
    with pytest.raises(DecisionError, match="regular file"):
        store.read_answer(decision) if answer_file else store.read_decision(decision.id)


def test_scan_survives_disappearing_files_and_sorts_by_age(store, monkeypatch):
    import os
    old = store.directory / "old.json"
    old.write_text("{}")
    os.utime(old, (1, 1))
    gone = store.directory / "gone.json"
    gone.write_text("{}")
    (store.directory / "directory.json").mkdir()
    original = Path.lstat
    def vanished(path, *args, **kwargs):
        if path == gone:
            path.unlink()
        return original(path, *args, **kwargs)
    monkeypatch.setattr(Path, "lstat", vanished)
    assert store.list_ids() == ["old", DECISION["id"]]


@pytest.mark.parametrize("raw", [b"[]", b"\xff", b"[" * 10000 + b"]" * 10000])
def test_malformed_answers_are_reported_by_both_read_routes(deciding_client, store, raw):
    store.answer_path(DECISION["id"]).write_bytes(raw)
    response = deciding_client.get("/api/decisions/" + DECISION["id"])
    assert response.status_code == 422
    assert response.text.startswith("answer for")
    assert "error" in deciding_client.get("/api/decisions").json()["decisions"][0]


def test_write_failure_is_reported_without_losing_the_old_answer(deciding_client, store, monkeypatch):
    decision = decision_from_mapping(DECISION)
    old = answer_from_mapping(decision, {"note": "old"})
    store.write_answer(old)
    def denied(source, target):
        raise PermissionError("replace denied")
    monkeypatch.setattr(Path, "replace", denied)
    response = deciding_client.post("/api/decisions/2026-10-09-intake-pass/answer", json={"note": "new"})
    assert response.status_code == 500 and "cannot write the answer" in response.text
    assert store.read_answer(decision) == old
    assert not list(store.directory.glob(".*.tmp"))


def test_full_size_answer_is_accepted_but_one_more_byte_is_refused(deciding_client, store):
    body = b'{"note":"' + b"x" * (decisions.MAXIMUM_ANSWER_BYTES - 11) + b'"}'
    assert len(body) == decisions.MAXIMUM_ANSWER_BYTES
    assert deciding_client.post("/api/decisions/2026-10-09-intake-pass/answer", content=body).status_code == 200
    old = store.answer_path(DECISION["id"]).read_bytes()
    assert deciding_client.post("/api/decisions/2026-10-09-intake-pass/answer", content=body + b" ").status_code == 413
    assert store.answer_path(DECISION["id"]).read_bytes() == old


def test_repeated_origin_headers_are_refused(deciding_client, store):
    response = deciding_client.post("/api/decisions/2026-10-09-intake-pass/answer", json={},
                                   headers=[("Origin", "http://testserver"), ("Origin", "http://evil.example")])
    assert response.status_code == 403
    assert not store.answer_path(DECISION["id"]).exists()


def test_cli_reads_stdin_and_reports_bad_encoding(tmp_path, monkeypatch, capsys):
    import io
    monkeypatch.setattr("sys.stdin", io.StringIO("|key|title|\n|---|---|\n|one|One|"))
    assert decisions.main(["from-table", "-", "--id", "p", "--title", "Pass"]) == 0
    assert json.loads(capsys.readouterr().out)["items"][0]["key"] == "one"
    table = tmp_path / "bad.md"
    table.write_bytes(b"\xff")
    assert decisions.main(["from-table", str(table), "--id", "p", "--title", "Pass"]) == 2
    assert "codec" in capsys.readouterr().err
    assert decisions.main(["check", str(tmp_path / "missing.json")]) == 2
    assert "No such file" in capsys.readouterr().err


@pytest.mark.parametrize("timestamp", ["yesterday", "2026-10-09", "2026-99-09T12:00:00"])
def test_supplied_decision_timestamps_follow_the_contract(timestamp):
    with pytest.raises(DecisionError, match="asked-at must be an ISO 8601 timestamp"):
        decision_from_mapping({**DECISION, "asked-at": timestamp})


@pytest.mark.parametrize("timestamp", [None, "", 7, "yesterday", "2026-10-09", "\ud800"])
def test_read_answer_never_invents_a_timestamp(store, timestamp):
    store.answer_path(DECISION["id"]).write_text(json.dumps({"answered-at": timestamp}))
    with pytest.raises(DecisionError, match="answered-at"):
        store.read_answer(decision_from_mapping(DECISION))


def test_answer_write_replaces_the_link_without_touching_its_target(store, tmp_path):
    target = tmp_path / "record"
    target.write_text("record")
    path = store.answer_path(DECISION["id"])
    path.symlink_to(target)
    answer = answer_from_mapping(decision_from_mapping(DECISION), {})
    store.write_answer(answer)
    assert target.read_text() == "record" and not path.is_symlink()
    assert json.loads(path.read_text()) == answer.to_mapping()


def test_new_directory_and_state_environment_defaults(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    assert default_directory({}) == tmp_path / ".local/state/devcapsule/decisions"
    assert default_directory({"XDG_STATE_HOME": ""}) == default_directory({})
    store = DecisionStore(tmp_path / "new" / "decisions")
    answer = answer_from_mapping(decision_from_mapping(DECISION), {})
    assert store.write_answer(answer).is_file()


def test_decisions_setting_uses_the_supplied_environment_and_cli_precedence(project, tmp_path, monkeypatch):
    from devcapsule_webconsole.settings import settings_from_arguments
    token = tmp_path / "token"
    token.write_text("abc123")
    monkeypatch.setenv("DEVCAPSULE_CONSOLE_DECISIONS", "ambient-must-not-win")
    args = ["--project", str(project), "--token-file", str(token)]
    env = {"DEVCAPSULE_CONSOLE_DECISIONS": str(tmp_path / "env")}
    assert settings_from_arguments(args, env).decisions == tmp_path / "env"
    assert settings_from_arguments(args + ["--decisions", str(tmp_path / "cli")], env).decisions == tmp_path / "cli"


# The hand-off: the decision as chat text, ending with the link to act in the browser.

def test_hand_off_text_stands_alone_and_ends_with_the_tokened_link(tmp_path: Path, monkeypatch):
    token_file = tmp_path / "token"
    token_file.write_text("abc/def 123\n", encoding="utf-8")
    decision = decision_from_mapping({**DECISION, "context": "Two items from the **intake** queue.",
                                      "asked-by": "project-management", "asked-at": "2026-10-09T12:00:00+00:00"})
    link = decisions.hand_off_link(decision.id, {"DEVCAPSULE_CONSOLE_URL": "http://127.0.0.1:43123/"}, token_file)
    assert link == ("http://127.0.0.1:43123/decisions/2026-10-09-intake-pass?token=abc%2Fdef%20123", "")
    text = decisions.hand_off_text(decision, link)
    lines = text.splitlines()
    assert lines[0] == "Intake disposition pass"
    assert lines[1] == "Asked by project-management at 2026-10-09T12:00:00+00:00"
    assert "Two items from the **intake** queue." in lines
    assert "1. " + decision.items[0].title in lines
    assert any(line.startswith("   - ") and ": " in line for line in lines), "options are listed with their keys"
    assert lines[-2].startswith("Answer here with each item's number and option key, or follow this link")
    assert lines[-1] == "http://127.0.0.1:43123/decisions/2026-10-09-intake-pass?token=abc%2Fdef%20123"
    assert text.endswith("\n") and "\n\n\n" not in text


def test_hand_off_without_a_console_or_without_a_readable_token_says_so(tmp_path: Path):
    decision = decision_from_mapping(DECISION)
    assert decisions.hand_off_link(decision.id, {}, tmp_path / "token") is None
    no_console = decisions.hand_off_text(decision, None).splitlines()[-1]
    assert "not reachable" in no_console and "/decisions/2026-10-09-intake-pass" in no_console
    missing = decisions.hand_off_link(decision.id, {"DEVCAPSULE_CONSOLE_URL": "http://127.0.0.1:1"}, tmp_path / "absent")
    assert missing is not None and missing[0] == "http://127.0.0.1:1/decisions/2026-10-09-intake-pass"
    assert "was not readable" in missing[1]
    (tmp_path / "empty").write_text("\n", encoding="utf-8")
    empty = decisions.hand_off_link(decision.id, {"DEVCAPSULE_CONSOLE_URL": "http://127.0.0.1:1"}, tmp_path / "empty")
    assert empty is not None and "is empty" in empty[1]
    assert decisions.hand_off_text(decision, missing).splitlines()[-1].startswith(
        "http://127.0.0.1:1/decisions/2026-10-09-intake-pass (the console's token file")


def test_hand_off_command_reads_the_environment_the_launcher_sets(tmp_path: Path, capsys, monkeypatch):
    directory = tmp_path / "decisions"
    directory.mkdir()
    (directory / "2026-10-09-intake-pass.json").write_text(json.dumps(DECISION), encoding="utf-8")
    token_file = tmp_path / "token"
    token_file.write_text("tok\n", encoding="utf-8")
    monkeypatch.setenv("DEVCAPSULE_CONSOLE_URL", "http://127.0.0.1:5")
    monkeypatch.setenv("DEVCAPSULE_CONSOLE_TOKEN_FILE", str(token_file))
    assert decisions.main(["hand-off", str(directory / "2026-10-09-intake-pass.json")]) == 0
    out = capsys.readouterr().out
    assert out.startswith("Intake disposition pass\n")
    assert out.rstrip("\n").endswith("http://127.0.0.1:5/decisions/2026-10-09-intake-pass?token=tok")
    other = tmp_path / "other"
    other.write_text("second\n", encoding="utf-8")
    assert decisions.main(["hand-off", str(directory / "2026-10-09-intake-pass.json"), "--token-file", str(other)]) == 0
    assert capsys.readouterr().out.rstrip("\n").endswith("?token=second")
    (directory / "bad.json").write_text("{", encoding="utf-8")
    assert decisions.main(["hand-off", str(directory / "bad.json")]) == 2
    assert "not a JSON document" in capsys.readouterr().err
