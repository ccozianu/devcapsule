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
    (directory / "pass-2.answer.json").write_text(json.dumps({"format": 1, "id": "pass-2", "answered-at": "t", "answers": {"one": {"chosen": ["accept"]}}}), encoding="utf-8")
    assert decisions.main(["check", str(directory / "pass-2.json")]) == 0
    assert capsys.readouterr().out == "pass-2: 2 item(s); answered t\n"
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
