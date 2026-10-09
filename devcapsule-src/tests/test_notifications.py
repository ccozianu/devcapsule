"""The notifications store: the contract's validation, the merged listing, and where the store lives."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import stat

import pytest

from devcapsule import notifications
from devcapsule.notifications import (
    ListingError,
    Notification,
    NotificationError,
    NotificationStore,
    listing_document,
    notification_from_mapping,
    store_for,
    store_in_environment,
)

DOCUMENT = {
    "format": 1, "id": "20261009t120000-abc123", "kind": "gate", "title": "Gate failed on main",
    "summary": "Two unit cases; see the **log**.", "link": "/records/engineering-docs/README.md",
    "posted-by": "ci", "posted-at": "2026-10-09T12:00:00+00:00", "read-at": None,
}


def write(directory: Path, name: str, document: object) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


@pytest.fixture
def store(tmp_path: Path) -> NotificationStore:
    return NotificationStore(tmp_path / "state" / "notifications", tmp_path / "state" / "decisions")


def test_a_valid_document_round_trips() -> None:
    notification = notification_from_mapping(DOCUMENT)
    assert notification == Notification("20261009t120000-abc123", "gate", "Gate failed on main", "ci",
                                        "2026-10-09T12:00:00+00:00", "Two unit cases; see the **log**.",
                                        "/records/engineering-docs/README.md")
    assert notification.unread
    assert notification.to_mapping() == DOCUMENT


@pytest.mark.parametrize("change, message", [
    ({"format": "1"}, "format must be 1"),
    ({"format": True}, "format must be 1"),
    ({"id": "Bad Id"}, "id must be lowercase"),
    ({"id": "-leading"}, "id must be lowercase"),
    ({"kind": "decision"}, "kind 'decision' is reserved"),
    ({"kind": "x" * 33}, "kind must be lowercase"),
    ({"title": " "}, "title must be a non-empty string"),
    ({"posted-by": None}, "posted-by must be a non-empty string"),
    ({"posted-at": "2026-10-09"}, "posted-at must be an ISO 8601 timestamp"),
    ({"posted-at": "noon"}, "posted-at must be an ISO 8601 timestamp"),
    ({"read-at": 5}, "read-at must be a string"),
    ({"link": "records/x.md"}, "link must be a console path"),
    ({"link": "/records/a b.md"}, "link must be a console path"),
    ({"link": "/" + "x" * 1000}, "link must be a console path"),
    ({"summary": "\udc80"}, "summary must contain valid Unicode text"),
])
def test_malformed_documents_are_refused_with_the_field_named(change: dict[str, object], message: str) -> None:
    with pytest.raises(NotificationError, match=re.escape(message)):
        notification_from_mapping({**DOCUMENT, **change})


def test_not_an_object_is_refused() -> None:
    with pytest.raises(NotificationError, match="must be a JSON object"):
        notification_from_mapping(["not", "an", "object"])


def test_post_writes_a_validated_document_with_a_fresh_sortable_id(store: NotificationStore) -> None:
    first = store.post(kind="gate", title="First", posted_by="ci", now="2026-10-09T12:00:00+00:00")
    second = store.post(kind="gate", title="Second", posted_by="ci", summary="s", link="/records/x.md",
                        now="2026-10-09T12:00:01+02:00")
    assert first.id.startswith("20261009t120000-") and second.id.startswith("20261009t100001-")
    assert first.id != second.id and notifications.ID_PATTERN.fullmatch(second.id)
    written = json.loads(store.path(second.id).read_text(encoding="utf-8"))
    assert written == second.to_mapping() and written["read-at"] is None
    assert stat.S_IMODE(store.path(second.id).stat().st_mode) == 0o600
    with pytest.raises(NotificationError, match="kind 'decision' is reserved"):
        store.post(kind="decision", title="No", posted_by="ci")
    assert sorted(p.name for p in store.directory.iterdir()) == sorted([f"{first.id}.json", f"{second.id}.json"])


def test_listing_is_newest_first_and_merges_unanswered_decisions(store: NotificationStore) -> None:
    old = store.post(kind="gate", title="Old", posted_by="ci", now="2026-10-08T12:00:00+00:00")
    new = store.post(kind="note", title="New", posted_by="me", now="2026-10-10T12:00:00+00:00")
    write(store.decisions, "intake-pass.json", {"format": 1, "id": "intake-pass", "title": "Intake pass",
                                                "asked-by": "project-management", "asked-at": "2026-10-09T12:00:00+00:00",
                                                "items": []})
    write(store.decisions, "answered.json", {"format": 1, "id": "answered", "title": "Answered", "items": []})
    write(store.decisions, "answered.answer.json", {"format": 1, "id": "answered", "answers": {}})
    entries = store.list()
    assert [entry.id for entry in entries] == [new.id, "intake-pass", old.id]
    decision = entries[1]
    assert isinstance(decision, Notification)
    assert decision == Notification("intake-pass", "decision", "Intake pass", "project-management",
                                    "2026-10-09T12:00:00+00:00", link="/decisions/intake-pass")
    assert decision.unread
    document = listing_document(store)
    assert document["unread"] == 3 and [entry["id"] for entry in document["notifications"]] == [new.id, "intake-pass", old.id]
    store.mark_read(old.id, now="2026-10-10T13:00:00+00:00")
    unread = listing_document(store, unread_only=True)
    assert unread["unread"] == 2 and [entry["id"] for entry in unread["notifications"]] == [new.id, "intake-pass"]


def test_a_decision_without_a_title_or_timestamp_is_listed_from_its_file(store: NotificationStore) -> None:
    path = write(store.decisions, "bare.json", {"format": 1, "id": "bare", "items": []})
    os.utime(path, (1_760_000_000, 1_760_000_000))
    (entry,) = store.list()
    assert isinstance(entry, Notification)
    assert entry.title == "bare" and entry.posted_by == "an agent" and entry.posted_at == "2025-10-09T08:53:20+00:00"
    assert entry.link == "/decisions/bare"


def test_malformed_files_are_listed_as_errors_not_hidden(store: NotificationStore) -> None:
    good = store.post(kind="gate", title="Good", posted_by="ci", now="2026-10-09T12:00:00+00:00")
    write(store.directory, "broken.json", {"format": 1, "id": "other", "kind": "gate", "title": "x",
                                           "posted-by": "ci", "posted-at": "2026-10-09T12:00:00+00:00"})
    (store.directory / "garbage.json").write_text("{", encoding="utf-8")
    (store.directory / "Ignored.json").write_text("{}", encoding="utf-8")  # not an id: never listed
    (store.directory / "huge.json").write_bytes(b"[" + b" " * notifications.MAXIMUM_DOCUMENT_BYTES + b"]")
    (store.decisions.mkdir(parents=True, exist_ok=True))
    (store.decisions / "bad-decision.json").write_text("[]", encoding="utf-8")
    entries = store.list()
    errors = {entry.id: entry for entry in entries if isinstance(entry, ListingError)}
    assert [entry.id for entry in entries if isinstance(entry, Notification)] == [good.id]
    assert set(errors) == {"broken", "garbage", "huge", "bad-decision"}
    assert "carries id 'other'" in errors["broken"].error
    assert "not a JSON document" in errors["garbage"].error
    assert "larger than" in errors["huge"].error
    assert errors["bad-decision"].kind == "decision" and "must be a JSON object" in errors["bad-decision"].error
    assert json.loads(json.dumps(listing_document(store)))["notifications"][1]["error"]


def test_symbolic_links_and_special_files_are_refused(store: NotificationStore, tmp_path: Path) -> None:
    target = tmp_path / "elsewhere.json"
    target.write_text(json.dumps(DOCUMENT), encoding="utf-8")
    store.directory.mkdir(parents=True)
    (store.directory / "linked.json").symlink_to(target)
    os.mkfifo(store.directory / "pipe.json")
    errors = {entry.id: entry.error for entry in store.list() if isinstance(entry, ListingError)}
    assert set(errors) == {"linked", "pipe"}
    assert "cannot read linked.json" in errors["linked"]
    assert "must be a regular file" in errors["pipe"]


def test_read_marks_once_and_dismiss_removes(store: NotificationStore) -> None:
    posted = store.post(kind="gate", title="Gate", posted_by="ci", now="2026-10-09T12:00:00+00:00")
    read = store.mark_read(posted.id, now="2026-10-09T12:30:00+00:00")
    assert read.read_at == "2026-10-09T12:30:00+00:00" and not read.unread
    again = store.mark_read(posted.id, now="2026-10-09T13:00:00+00:00")
    assert again.read_at == "2026-10-09T12:30:00+00:00"
    assert json.loads(store.path(posted.id).read_text(encoding="utf-8"))["read-at"] == "2026-10-09T12:30:00+00:00"
    store.dismiss(posted.id)
    assert not store.path(posted.id).exists()
    with pytest.raises(NotificationError, match=f"no notification '{posted.id}'"):
        store.read(posted.id)


def test_decisions_are_neither_read_nor_dismissed_here(store: NotificationStore) -> None:
    write(store.decisions, "intake-pass.json", {"format": 1, "id": "intake-pass", "title": "Intake pass", "items": []})
    with pytest.raises(NotificationError, match="'intake-pass' is a decision: answer it in the web console"):
        store.mark_read("intake-pass")
    with pytest.raises(NotificationError, match="is a decision"):
        store.dismiss("intake-pass")
    assert (store.decisions / "intake-pass.json").exists()
    with pytest.raises(NotificationError, match="the id must be lowercase"):
        store.dismiss("../escape")


def test_store_in_environment_follows_xdg_state_and_the_overrides(tmp_path: Path) -> None:
    home = tmp_path / "home"
    by_home = store_in_environment({"HOME": str(home)})
    assert by_home.directory == home / ".local" / "state" / "devcapsule" / "notifications"
    assert by_home.decisions == home / ".local" / "state" / "devcapsule" / "decisions"
    by_state = store_in_environment({"HOME": str(home), "XDG_STATE_HOME": str(tmp_path / "xdg")})
    assert by_state.directory == tmp_path / "xdg" / "devcapsule" / "notifications"
    named = store_in_environment({"HOME": str(home), "DEVCAPSULE_NOTIFICATIONS": str(tmp_path / "n"),
                                  "DEVCAPSULE_CONSOLE_DECISIONS": str(tmp_path / "d")})
    assert named == NotificationStore(tmp_path / "n", tmp_path / "d")
    assert store_in_environment({"HOME": str(home), "DEVCAPSULE_NOTIFICATIONS": str(tmp_path / "s" / "n")}).decisions \
        == tmp_path / "s" / "decisions"


def test_inside_a_capsule_the_environment_wins_over_the_selected_path(tmp_path: Path) -> None:
    env = {"HOME": str(tmp_path / "home"), "DEVCAPSULE_CONTAINER_NAME": "capsule-1"}
    inside = store_for(tmp_path / "some" / "project", env)
    assert inside.directory == tmp_path / "home" / ".local" / "state" / "devcapsule" / "notifications"
