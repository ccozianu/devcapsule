"""The manifest's two schemas as classes, and the one migration between them (work order of 2026-10-26)."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import tomllib

import pytest

from devcapsule.configuration.file_formats import ProjectConfigurationError, legacy_lock
from devcapsule.configuration.manifest import current_manifest, ide_capability
from devcapsule.configuration.manifest_document import Recommendations, render_manifest
from devcapsule.configuration.manifest_schemas import ManifestV1, ManifestV2, NeedForm, RequiredForm, read_manifest, upgrade
from devcapsule.configuration.storage import load_toml
from tests.test_upgrade_recovery import checkout, invoke  # noqa: F401  (the released v0.2.11 fixture)

PROJECT = {"name": "Sample", "slug": "sample", "creator": "mailto:owner@example.test", "mount": "/workspace/sample"}


def v1(**fields) -> dict:
    return {"devcapsule-schema-version": 1, "project": dict(PROJECT), **fields}


def v2(**fields) -> dict:
    return {"devcapsule-schema-version": 2, "project": dict(PROJECT), "capabilities": {"required": ["python"]}, **fields}


# The schema-1 shapes in evidence: this repository's manifest, the trading
# sample, the compat fixtures and the AI Learning bootstrap as rc3 wrote it.
SHAPES = {
    "need-with-ide-and-workflow-type": v1(**{"workflow-type": "multiple-streams"},
                                          workflow={"definition": "devcapsule", "version": "0.2.14.dev0", "mode": "multiple-streams"},
                                          capabilities={"need": ["codex-agent", "python", "python-ide"]},
                                          configuration={"values": {"runtime.memory-limit": {"type": "memory-size", "runtime-effect": "docker.memory-limit"}}},
                                          host={"network": {"mode": {"recommended": {"value": "host", "justification": "dev services"}}}}),
    "need-without-ide": v1(capabilities={"need": ["python"]}),
    "required-with-empty-sdk-major": v1(capabilities={"required": ["postgresql-client"], "optional": [], "sdk-major": {}},
                                        workflow={"definition": "devcapsule", "version": "0.3.0", "mode": "single-stream"}),
    "workflow-type-alone": v1(**{"workflow-type": "single-stream"}, capabilities={"need": ["python", "pycharm"]}),
    "extension-table": v1(capabilities={"need": ["python"], "future": {"keep": 1.5}}, extension={"ratio": 1.5}),
}


@pytest.mark.parametrize("name", sorted(SHAPES))
def test_schema_one_shapes_are_read_as_v1_and_upgraded_by_the_laws(name: str) -> None:
    document = SHAPES[name]
    read = read_manifest(document, "manifest")
    assert isinstance(read, ManifestV1)
    assert read_manifest(read.document(), "manifest") == read  # an empty optional list says nothing
    upgraded = upgrade(read, ide=ide_capability)
    result = upgraded.document()
    assert result["devcapsule-schema-version"] == 2
    assert "need" not in result["capabilities"] and "workflow-type" not in result
    assert "environment" not in result
    # Law 1: need becomes required, in the file's order, IDEs apart.
    written = document["capabilities"].get("need", document["capabilities"].get("required", []))
    assert result["capabilities"]["required"] == [item for item in written if ide_capability(item) is None]
    # Law 2: a required IDE is the recommendation.
    ides = {ide_capability(item) for item in written} - {None}
    assert result.get("recommendations", {}).get("ide") == (next(iter(ides)) if ides else None)
    # Law 3: the retired table is carried for the note and never written.
    assert ("sdk-major" in result["capabilities"]) == ("sdk-major" in document["capabilities"])
    assert "sdk-major" not in render_manifest(result)
    # Law 4: workflow-type folds into [workflow].mode.
    if "workflow-type" in document:
        assert result["workflow"]["mode"] == document["workflow-type"]
    # Law 5: everything else is carried verbatim.
    for key in ("project", "host", "configuration", "extension"):
        if key in document:
            assert result[key] == document[key]
    if "future" in document["capabilities"]:
        assert result["capabilities"]["future"] == document["capabilities"]["future"]
    # Law 6: reading the rendered result gives an equal value, the retired table apart.
    rendered = read_manifest(tomllib.loads(render_manifest(result)), "manifest")
    assert rendered == replace(upgraded, retired={})


def test_the_forms_say_which_one_the_file_used() -> None:
    assert ManifestV1.read(v1(capabilities={"need": ["python", "python"], "optional": ["codex-agent"]}), "m").form == NeedForm(("python",), ("codex-agent",))
    assert ManifestV1.read(v1(capabilities={"required": ["python>=3"]}), "m").form == RequiredForm(("python>=3",))


def test_upgrade_drops_an_optional_ide_and_refuses_two_required_ides() -> None:
    read = ManifestV1.read(v1(capabilities={"need": ["python"], "optional": ["frontend-ide", "codex-agent"]}), "m")
    assert upgrade(read, ide=ide_capability).optional == ("codex-agent",)
    read = ManifestV1.read(v1(capabilities={"need": ["python-ide", "frontend-ide"]}), "m")
    with pytest.raises(ProjectConfigurationError, match="two IDEs, python-ide, frontend-ide.*config drop NAME"):
        upgrade(read, ide=ide_capability)


def test_workflow_type_is_dropped_when_equal_and_refused_when_it_disagrees() -> None:
    equal = v1(**{"workflow-type": "single-stream"}, workflow={"mode": "single-stream"}, capabilities={"need": ["python"]})
    assert upgrade(ManifestV1.read(equal, "m"), ide=ide_capability).workflow == {"mode": "single-stream"}
    with pytest.raises(ProjectConfigurationError, match="must agree"):
        read_manifest(v1(**{"workflow-type": "single-stream"}, workflow={"mode": "multiple-streams"}, capabilities={"need": ["python"]}), "m")


@pytest.mark.parametrize("document, word", [
    (v1(capabilities={"need": ["python"]}, environment={"required": {"A": {}}}), r"\[environment\]"),
    (v1(capabilities={"need": ["python"]}, recommendations={"cpus": 2}), r"\[recommendations\]"),
    (v1(capabilities={"required": ["python"], "reasons": {"python": "why"}}), r"\[capabilities.reasons\]"),
])
def test_schema_one_refuses_schema_two_words_by_name(document: dict, word: str) -> None:
    with pytest.raises(ProjectConfigurationError, match=f"says devcapsule-schema-version = 1 but declares {word}"):
        read_manifest(document, "manifest")


def test_schema_one_refuses_both_capability_forms_at_once() -> None:
    with pytest.raises(ProjectConfigurationError, match="not both"):
        read_manifest(v1(capabilities={"need": ["python"], "required": ["python"]}), "manifest")


def test_schema_two_refuses_need_and_folds_a_carried_over_workflow_type() -> None:
    with pytest.raises(ProjectConfigurationError, match="declares capabilities.need, a schema-1 word"):
        read_manifest(v2(capabilities={"need": ["python"]}), "manifest")
    # rc4 to rc7 wrote schema-2 files that kept the root key of a schema-1 file.
    carried = read_manifest(v2(**{"workflow-type": "multiple-streams"}, workflow={"definition": "devcapsule"}), "manifest")
    assert isinstance(carried, ManifestV2)
    assert carried.workflow == {"mode": "multiple-streams", "definition": "devcapsule"}
    assert "workflow-type" not in carried.document()


@pytest.mark.parametrize("version", [3, "2", True, None])
def test_other_versions_are_refused_naming_the_ones_read(version: object) -> None:
    document = v2()
    document["devcapsule-schema-version"] = version
    with pytest.raises(ProjectConfigurationError, match="requires devcapsule-schema-version = 1 or 2"):
        read_manifest(document, "manifest")
    with pytest.raises(ProjectConfigurationError):
        ManifestV2.read(v1(capabilities={"need": ["python"]}), "manifest")
    with pytest.raises(ProjectConfigurationError):
        ManifestV1.read(v2(), "manifest")


def test_schema_two_reads_losslessly_and_exposes_its_values() -> None:
    document = v2(capabilities={"required": ["node>=22", "python"], "optional": ["codex-agent"], "reasons": {"node": "Next.js"},
                                "resolution": {"codex-agent": "codex"}, "future": 1},
                  environment={"required": {"DB": {"reason": "db", "extension": {"keep": True}}}, "optional": {"MAIL": {}}},
                  recommendations={"ide": "frontend-ide", "memory": "8GiB", "cpus": 4},
                  host={"network": {"mode": {"recommended": {"value": "host", "justification": "ports"}}}},
                  generator="newer", extension={"a": 1}, workflow={"mode": "single-stream"})
    read = read_manifest(document, "manifest")
    assert isinstance(read, ManifestV2)
    assert read.document() == document
    assert read.policy.required == ("node", "python") and read.policy.minimums == (("node", "22"),)
    assert read.environment_policy.required == {"DB": "db"} and read.environment_policy.optional == {"MAIL": ""}
    assert read.recommendations == Recommendations("frontend-ide", "8GiB", 4)
    assert current_manifest(document, "manifest") == read


def test_ide_capability_answers_from_the_component_catalog() -> None:
    assert ide_capability("python-ide") == "python-ide"
    assert ide_capability("pycharm") == "python-ide"
    assert ide_capability("python") is None
    assert ide_capability("future-tool") is None


@pytest.mark.parametrize("lock, legacy", [
    ({"resolution-matrix-version": "embedded-18"}, True),
    ({"resolution-matrix-version": "dogfood-v1"}, True),
    ({"resolution-matrix-version": "embedded-28"}, True),
    ({"capability-providers": {}}, True),
    ({"resolution-matrix-version": "embedded-26", "capability-providers": {}}, True),
    ({"resolution-matrix-version": "embedded-27", "capability-providers": {}}, False),
    ({"resolution-matrix-version": "embedded-28", "capability-providers": {"python": []}}, False),
])
def test_a_lock_is_legacy_unless_it_records_evidence_from_generation_27_on(lock: dict, legacy: bool) -> None:
    assert legacy_lock(lock) is legacy


def test_regenerate_migrates_a_schema_one_manifest_and_keeps_its_leading_comment(checkout, capsys) -> None:  # noqa: F811
    project, record, _ = checkout
    manifest_path = project / ".devcapsule/devcapsule.toml"
    lock_path = project / ".devcapsule/devcapsule.linux-amd64.lock"
    manifest_path.write_text("# The owner's note\n\n" + manifest_path.read_text().replace('slug = "project"', 'slug = "project" # inline'))
    assert load_toml(manifest_path)["devcapsule-schema-version"] == 1
    assert invoke(project, "init", "--regenerate", "--authorize", "base-image", "default") == 0
    report = capsys.readouterr().out
    assert f"Migrated {manifest_path} to schema 2; the leading comment block is kept, other comments are not." in report
    text = manifest_path.read_text()
    assert text.startswith("# The owner's note\n\ndevcapsule-schema-version = 2\n") and "# inline" not in text
    manifest = tomllib.loads(text)
    assert manifest["capabilities"] == {"required": ["python"]}
    assert manifest["recommendations"] == {"ide": "python-ide"}
    assert manifest["project"] == {"name": "project", "slug": "project", "creator": "mailto:upgrade@example.test", "mount": "/workspace/project"}
    lock = load_toml(lock_path)
    assert "interactive-surface" not in lock["components"] and "capability-providers" in lock
    # The owner's checkout keeps the IDE the schema-1 file required, so it still runs.
    assert "python-ide" in load_toml(record)["capabilities"]["selected"]
    # A second regeneration finds schema 2 and leaves the manifest's bytes alone.
    before = manifest_path.read_bytes()
    assert invoke(project, "init", "--regenerate", "--authorize", "base-image", "default") == 0
    assert manifest_path.read_bytes() == before and "Honored existing" in capsys.readouterr().out


def test_init_without_regenerate_leaves_a_schema_one_manifest_alone(checkout) -> None:  # noqa: F811
    project, _, _ = checkout
    manifest_path = project / ".devcapsule/devcapsule.toml"
    before = manifest_path.read_bytes()
    assert invoke(project, "init", "--authorize", "base-image", "default") == 0
    assert manifest_path.read_bytes() == before
    assert load_toml(manifest_path)["devcapsule-schema-version"] == 1
