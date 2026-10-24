"""The truthful listing: effective value, source and pending, computed from documents, writing nothing."""

from __future__ import annotations

from pathlib import Path
import tomllib

import pytest

from devcapsule.configuration.capability_selection import compose_lock, generate_lock
from devcapsule.configuration.capabilities import CapabilityPolicy
from devcapsule.configuration.file_formats import render_toml
from devcapsule.configuration.listing import assess_checkout
from devcapsule.configuration.launcher_values import launcher_value_sources
from devcapsule.configuration.workstation import WorkstationDefaults, render_workstation
from devcapsule.configuration.file_formats import ProjectConfigurationError
from devcapsule.platforms import Platform
from devcapsule.resolution_matrix import MATRICES

MATRIX = MATRICES[Platform.LINUX_AMD64]
SURFACES = {name: MATRIX.providers(name)[0] for name in MATRIX.local_capabilities() if not name.endswith("-agent")}
AGENTS = {name: MATRIX.providers(name)[0] for name in MATRIX.local_capabilities() if name.endswith("-agent")}


def manifest(**extra) -> dict:
    return {"devcapsule-schema-version": 2,
            "project": {"creator": "mailto:owner@example.test", "slug": "sample", "name": "Sample", "mount": "/workspace/sample"},
            "capabilities": {"required": ["node"], "optional": ["browser-automation"]}, **extra}


def listing(document: dict, checkout: dict | None = None, *, workstation: dict | None = None, saved=None):
    shared = generate_lock(CapabilityPolicy.read(document), MATRIX)
    checkout = checkout or {"devcapsule-checkout-schema-version": 1}
    composed = compose_lock(document, shared, checkout)
    return assess_checkout(document, shared, composed, checkout, workstation=workstation, saved_environment=saved,
                           surfaces=SURFACES, agents=AGENTS, project=Path("/p"))


def rows(result, kind):
    return {row.name: row for row in result.rows if row.kind == kind}


def test_an_unchosen_ide_is_a_pending_row_not_a_refusal() -> None:
    result = listing(manifest())
    ide = rows(result, "ide")["(none)"]
    assert ide.pending.startswith("choose one:") and "config ide IDE" in ide.command
    assert "ide" in [row.kind for row in result.pending]
    assert any("once an IDE is chosen" in note for note in result.notes)


def test_a_recommended_ide_is_disclosed_with_its_reason_and_not_pending() -> None:
    result = listing(manifest(recommendations={"ide": "frontend-ide", "reasons": {"ide": "TypeScript"}}))
    ide = rows(result, "ide")["frontend-ide"]
    assert ide.pending == "" and ide.source.startswith("project recommendation: TypeScript")
    assert ide.command.endswith("config ide frontend-ide")


def test_tools_show_their_scope_and_omission() -> None:
    result = listing(manifest(), {"devcapsule-checkout-schema-version": 1, "capabilities": {"without": ["browser-automation"]}})
    tools = rows(result, "tool")
    assert tools["node"].source == "project (required)" and tools["node"].effective == "supplied by the base"
    assert tools["browser-automation"].effective == "omitted" and tools["browser-automation"].source == "checkout (omitted)"


def test_launcher_values_follow_the_precedence_and_name_their_source() -> None:
    document = manifest(recommendations={"memory": "6g"})
    workstation = {"defaults": {"memory": "4GiB", "cpus": 2}}
    result = listing(document, workstation=workstation)
    assert rows(result, "memory")["memory"].effective == "6GiB" and rows(result, "memory")["memory"].source == "project recommendation"
    assert rows(result, "cpus")["cpus"].effective == "2" and rows(result, "cpus")["cpus"].source == "workstation default"
    checkout = {"devcapsule-checkout-schema-version": 1, "configuration": {"values": {"memory": "8GiB"}}}
    result = listing(document, checkout, workstation=workstation)
    assert rows(result, "memory")["memory"].source == "checkout"
    assert rows(result, "memory")["memory"].effective == "8GiB"
    none = listing(manifest())
    assert rows(none, "memory")["memory"].effective == "no limit" and rows(none, "memory")["memory"].source == "none"


def test_a_legacy_memory_declaration_is_an_alias_of_memory() -> None:
    document = manifest(configuration={"values": {"runtime.memory-limit": {
        "type": "memory-size", "runtime-effect": "docker.memory-limit", "recommended": "2GiB"}}})
    assert launcher_value_sources(document, {}) == {"memory": ("2GiB", "project recommendation"), "cpus": (None, "none")}
    recorded = {"configuration": {"values": {"runtime.memory-limit": "3GiB"}}}
    assert launcher_value_sources(document, recorded)["memory"] == ("3GiB", "checkout")
    result = listing(document, {"devcapsule-checkout-schema-version": 1, **recorded})
    assert "runtime.memory-limit" not in rows(result, "value")
    assert rows(result, "memory")["memory"].effective == "3GiB"


def test_host_access_rows_show_secure_defaults_and_ask_only_what_the_project_recommends() -> None:
    document = manifest(host={"network": {"mode": {"recommended": {"value": "host", "justification": "ports"}}}})
    result = listing(document)
    access = rows(result, "access")
    assert access["docker-daemon"].effective == "none" and access["docker-daemon"].source == "secure default" and not access["docker-daemon"].pending
    assert access["host-x11"].effective == "contained desktop"
    assert access["network"].effective == "bridge"
    assert access["network"].pending == "the project asks for network host; allow or deny"
    assert "config authorize network host" in access["network"].command and "config deny network" in access["network"].command
    denied = {"devcapsule-checkout-schema-version": 1, "authorization": {"network": {
        "value": "bridge", "recommendation-digest": "stale"}}}
    result = listing(document, denied)
    assert rows(result, "access")["network"].pending.startswith("the recommendation changed")


def test_environment_rows_cover_required_offered_and_saved() -> None:
    document = manifest(environment={"required": {"POSTGRES_HOST": {"reason": "db"}}, "optional": {"SMTP_HOST": {}}})
    result = listing(document, saved={"POSTGRES_HOST": "x", "EXTRA": None})
    env = rows(result, "env")
    assert env["POSTGRES_HOST"].effective == "set" and env["POSTGRES_HOST"].source == "checkout; project (required): db"
    assert env["SMTP_HOST"].effective == "unset" and not env["SMTP_HOST"].pending
    assert env["EXTRA"].effective == "from the host's variable" and env["EXTRA"].source == "checkout"
    result = listing(document)
    assert rows(result, "env")["POSTGRES_HOST"].pending == "the project needs a value from you"
    assert rows(result, "env")["POSTGRES_HOST"].command.endswith("config env POSTGRES_HOST")


def test_bindings_and_secrets_appear_once_an_ide_is_chosen(tmp_path: Path) -> None:
    from devcapsule.configuration.capability_commands import pin_selection
    from devcapsule.configuration.capabilities import LocalCapabilities
    document = manifest()
    shared = generate_lock(CapabilityPolicy.read(document), MATRIX)
    local = LocalCapabilities(selected=("codex-agent", "frontend-ide"))
    pins = pin_selection(MATRIX, CapabilityPolicy.read(document), local, shared, LocalCapabilities(), {}, allow_unverified=True)
    checkout = {"devcapsule-checkout-schema-version": 1,
                "capabilities": {"selected": list(local.selected), "without": [], "lock": render_toml(pins)}}
    composed = compose_lock(document, shared, checkout)
    result = assess_checkout(document, shared, composed, checkout, surfaces=SURFACES, agents=AGENTS, project=Path("/p"))
    assert rows(result, "ide")["frontend-ide"].effective.startswith("codium ")
    assert rows(result, "agent")["codex-agent"].effective.startswith("codex ")
    assert rows(result, "binding")["home"].effective == "managed directory"
    assert rows(result, "secret")["codex/openai-api-key"].source == "component (optional)"
    assert not result.notes


def test_declared_values_rows_and_undeclared_answers() -> None:
    document = manifest(configuration={"values": {"db.url": {"type": "string", "required": True},
                                                  "theme": {"type": "string", "recommended": "dark"}}})
    result = listing(document, {"devcapsule-checkout-schema-version": 1, "configuration": {"values": {"stray": 1}}})
    values = rows(result, "value")
    assert values["db.url"].pending == "the project needs a value from you" and values["db.url"].command.endswith("config set db.url VALUE")
    assert values["theme"].effective == '"dark"' and values["theme"].source == "project recommendation"
    assert values["stray"].pending == "not declared by this project"


def test_render_and_document_carry_every_column() -> None:
    result = listing(manifest())
    text = result.render()
    assert text.splitlines()[0].split() == ["KIND", "NAME", "EFFECTIVE", "SOURCE", "PENDING"]
    document = result.document()
    assert document["schema-version"] == 2 and "(none)" in document["pending"]
    assert set(document["rows"][0]) == {"kind", "name", "effective", "source", "pending", "command"}
    assert result.render_pending().startswith("Pending decisions:")


def test_workstation_defaults_validate_and_render() -> None:
    defaults = WorkstationDefaults.read({"defaults": {"memory": "4g", "cpus": 2}})
    assert defaults.values == {"memory": "4GiB", "cpus": 2}
    assert tomllib.loads(render_workstation(defaults)) == {"devcapsule-workstation-schema-version": 1,
                                                           "defaults": {"cpus": 2, "memory": "4GiB"}}
    assert defaults.with_value("cpus", None).values == {"memory": "4GiB"}
    with pytest.raises(ProjectConfigurationError, match="owns memory, cpus"):
        WorkstationDefaults.read({"defaults": {"swap": "1g"}})
    with pytest.raises(ProjectConfigurationError, match="positive integer"):
        WorkstationDefaults.read({"defaults": {"cpus": 0}})
    with pytest.raises(ProjectConfigurationError, match="schema version"):
        WorkstationDefaults.read({"devcapsule-workstation-schema-version": 2})
