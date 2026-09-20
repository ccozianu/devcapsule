"""Contract case table: unchanged / changed inputs; current / stale / invalid
base and host answers; allow / deny / unanswered; legacy / contained display;
refused / recovered / resolved / launched. Offered commands are EXECUTED through
cli.main. Historical inputs come from v0.2.11, not this implementation. Only
Docker, image building and GUI launch are substituted in the journey tests.
"""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import shlex
import shutil
import tomllib
from unittest.mock import Mock

import pytest

from devcapsule import cli
from devcapsule.compat import CliError
from devcapsule.configuration.review import (
    review_configuration,
)
from devcapsule.display_client import select_display_transport
from devcapsule.environment_realization import realize_environment
from devcapsule.materialization import ImageDetails
from devcapsule.configuration.authorization import (
    AuthorizationChoice,
    authorization_declarations,
    resolved_checkout_authorizations,
    review_authorizations,
)
from devcapsule.configuration.documents import (
    ProjectConfigurationError,
    canonical_digest,
    render_checkout,
)
from devcapsule.configuration.storage import (
    checkout_record_paths,
    load_toml,
    manifest_for,
)

FIXTURE = Path(__file__).parent / "resources/compat/v0.2.11"
OLD_LOCK = tomllib.loads((FIXTURE / "project/.devcapsule/devcapsule.linux-amd64.lock").read_text())
OLD_BASE = OLD_LOCK["base"]["reference"]
NEW_BASE = "docker.io/example/base@sha256:" + "c" * 64
LOCAL_ID = "sha256:" + "d" * 64
CONTAINED = {"devcapsule.base.display": "contained"}


@pytest.fixture
def checkout(tmp_path, monkeypatch):
    project = tmp_path / "project with spaces"
    shutil.copytree(FIXTURE / "project", project)
    for key, directory in (("HOME", "home"), ("XDG_CONFIG_HOME", "config"),
                           ("XDG_DATA_HOME", "data"), ("XDG_STATE_HOME", "state")):
        monkeypatch.setenv(key, str(tmp_path / directory))
    manifest = load_toml(project / ".devcapsule/devcapsule.toml")
    record, resolution = checkout_record_paths(manifest, project)
    record.parent.mkdir(parents=True)
    text = (FIXTURE / "checkout/devcapsule.checkout.toml").read_text().replace("@CHECKOUT_PATH@", str(project))
    record.write_text(text)
    resolution.write_text((FIXTURE / "checkout/devcapsule.resolved.toml").read_text().replace(
        "@CHECKOUT_INPUT_DIGEST@", canonical_digest(tomllib.loads(text))))
    monkeypatch.chdir(tmp_path)  # Remedies must select the checkout even from elsewhere.
    return project, record, resolution


def invoke(project, *args):
    return cli.main(["project", "--path", str(project), *args])


def review(project, record):
    _, manifest = manifest_for(project)
    lock = load_toml(project / ".devcapsule/devcapsule.linux-amd64.lock")
    return review_configuration(manifest, lock, load_toml(record))


def replace_answers(project, record, answers):
    manifest = load_toml(project / ".devcapsule/devcapsule.toml")
    record.write_text(render_checkout(manifest, project, {}, {}, answers))


def change_project(project, *, lock=True, manifest=True):
    if lock:
        path = project / ".devcapsule/devcapsule.linux-amd64.lock"
        path.write_text(path.read_text().replace(OLD_BASE, NEW_BASE))
    if manifest:
        path = project / ".devcapsule/devcapsule.toml"
        path.write_text(path.read_text() + '\n[host.browser.host-open.recommended]\nvalue = true\njustification = "Open project links in the host browser."\n')


def install_external_fakes(monkeypatch, events, *, contained=True):
    """Keep real realization; substitute its external effects."""
    def realize(selected, *, report, prepare_base):
        def obtain(reference):
            events.append("obtain-base")
            return ImageDetails(reference, LOCAL_ID, {
                "devcapsule.image.managed": "true", "devcapsule.metadata.version": "1",
                "devcapsule.image.kind": "base", **(CONTAINED if contained else {}),
            }, "linux", "amd64")
        def prepare(base):
            prepare_base(base)
            events.append("display-reviewed")
        def materialize(**kwargs):
            events.append("materialize")
            return "local/environment:test", False
        return realize_environment(selected, obtain_image=obtain, inspect_image=Mock(), build=Mock(),
            require_image=lambda ref: ImageDetails(ref, "sha256:environment", CONTAINED if contained else {}, "linux", "amd64"),
            materialize=materialize, report=report, prepare_base=prepare)
    launch = Mock(side_effect=lambda options: events.append(options) or 0)
    monkeypatch.setattr("devcapsule.commands.project.realize_environment", realize)
    monkeypatch.setattr("devcapsule.commands.project.run_pycharm", launch)
    return launch


# Persistence adapter law: inspection and execution preserve their input files.
@pytest.mark.parametrize("operation", [("config", "list"), ("run",)])
def test_read_only_operations_preserve_configuration_files(checkout, monkeypatch, operation):
    """Persistence adapter contract; semantic upgrade laws live in tests.configuration.test_adt."""
    project, record, resolution = checkout
    paths = [record, resolution, *sorted((project / ".devcapsule").iterdir())]
    before = {p: p.read_bytes() for p in paths}
    if operation == ("run",):
        install_external_fakes(monkeypatch, [], contained=False)
    assert invoke(project, *operation) == 0
    assert {p: p.read_bytes() for p in paths} == before


# Show all changed questions; each selected answer makes progress. Unrelated
# decisions survive. Absence never turns into host-session consent.
@pytest.mark.parametrize("lock_changed,manifest_changed", [(True, False), (False, True), (True, True)])
@pytest.mark.parametrize("display_answer", [None, True, False])
def test_upgrade_recovery_commands_converge_to_the_intended_launch(
    checkout, monkeypatch, capsys, lock_changed, manifest_changed, display_answer,
):
    project, record, resolution = checkout
    if display_answer is not None:
        assert invoke(project, "config", "authorize", "host-x11", str(display_answer).lower()) == 0
    assert invoke(project, "config", "authorize", "development-sudo", "false") == 0
    assert invoke(project, "config", "resolve") == 0
    original_answers = load_toml(record)["authorization"]
    before_record, before_resolution = record.read_bytes(), resolution.read_bytes()
    change_project(project, lock=lock_changed, manifest=manifest_changed)
    capsys.readouterr()
    events = []
    launch = install_external_fakes(monkeypatch, events)
    assert invoke(project, "run") == 2
    assert events == []
    assert invoke(project, "config", "resolve") == 2
    refusal = capsys.readouterr().err
    expected = ({"base-image"} if lock_changed else set()) | ({"host-browser"} if manifest_changed else set())
    pending = {r.name: r for r in review(project, record).authorizations if r.problem}
    assert set(pending) == expected
    for name in expected:
        assert f"{name}: stale" in refusal
    assert record.read_bytes() == before_record
    assert resolution.read_bytes() == before_resolution
    assert invoke(project, "config", "list") == 0
    listing = capsys.readouterr().out
    for item in pending.values():
        command = item.choices[0].command(project)
        assert command in listing
        assert cli.main(shlex.split(command)[1:]) == 0
        expected.remove(item.name)
        assert {r.name for r in review(project, record).authorizations if r.problem} == expected
    assert invoke(project, "config", "resolve") == 0
    assert review(project, record).ready
    answers = load_toml(record)["authorization"]
    assert answers["development-sudo"] == original_answers["development-sudo"]
    if display_answer is not None:
        assert answers["host-x11"] == original_answers["host-x11"]
    else:
        assert "host-x11" not in answers
    assert answers["base-image"]["reference"] == (NEW_BASE if lock_changed else OLD_BASE)
    assert invoke(project, "run") == 0
    options = launch.call_args.args[0]
    assert options.display_transport == ("host-x11" if display_answer else "contained")
    assert options.enable_sudo is False
    assert events[:3] == ["obtain-base", "display-reviewed", "materialize"]


# Every host node crosses allow/deny with current/stale. Execute every offered
# alternative through the real CLI and require that it settles that node.
@pytest.mark.parametrize("name,allow,deny", [
    ("host-browser", True, False), ("host-x11", True, False),
    ("development-sudo", True, False), ("docker-daemon", "host-socket", "none"),
    ("network", "host", "bridge"),
])
@pytest.mark.parametrize("allowed", [True, False])
@pytest.mark.parametrize("stale", [True, False])
def test_host_answer_state_table_and_executable_choices(checkout, name, allow, deny, allowed, stale):
    project, record, _ = checkout
    if name == "network":
        path = project / ".devcapsule/devcapsule.toml"
        path.write_text(path.read_text() + '\n[host.network.mode.recommended]\nvalue = "host"\njustification = "Test service access."\n')
    manifest = load_toml(project / ".devcapsule/devcapsule.toml")
    declarations = authorization_declarations(manifest, OLD_LOCK)
    answer = allow if allowed else deny
    answers = {name: {"value": answer, "recommendation-digest": "old" if stale else declarations[name].recommendation_digest}}
    replace_answers(project, record, answers)
    result = next(item for item in review(project, record).authorizations if item.name == name)
    assert result.status == ("stale" if stale else "authorized" if allowed else "denied")
    assert result.value == answer
    if stale:
        assert result.choices[0].value == str(answer).lower()
        for choice in result.choices:
            replace_answers(project, record, answers)
            assert cli.main(shlex.split(choice.command(project))[1:]) == 0
            updated = next(item for item in review(project, record).authorizations if item.name == name)
            assert updated.problem is None
            assert updated.value == (allow if choice.value == str(allow).lower() else deny)
    else:
        assert result.choices == ()


@pytest.mark.parametrize("record,status,choice_values", [
    (None, "missing-required", ("default",)),
    ("broken", "invalid", ("default",)),
    ({}, "invalid", ("default",)),
    ({"reference": OLD_BASE, "lock-digest": canonical_digest(OLD_LOCK)}, "authorized", ()),
    ({"reference": OLD_BASE, "lock-digest": "old"}, "stale", ("default",)),
    ({"reference": NEW_BASE, "lock-digest": canonical_digest(OLD_LOCK)}, "invalid", ("default",)),
    ({"reference": "local/base:tag", "image-id": LOCAL_ID, "lock-digest": canonical_digest(OLD_LOCK)}, "authorized-local", ()),
    ({"reference": "local/base:tag", "image-id": LOCAL_ID, "lock-digest": "old"}, "stale", ("default", LOCAL_ID)),
    ({"reference": "local/base:tag", "image-id": "malformed", "lock-digest": canonical_digest(OLD_LOCK)}, "invalid", ("default",)),
    ({"reference": OLD_BASE, "image-id": LOCAL_ID, "lock-digest": canonical_digest(OLD_LOCK)}, "invalid", ("default", LOCAL_ID)),
])
def test_base_state_table(checkout, record, status, choice_values):
    project, _, _ = checkout
    manifest = load_toml(project / ".devcapsule/devcapsule.toml")
    records = {} if record is None else {"base-image": record}
    item = review_authorizations(manifest, OLD_LOCK, {"authorization": records})[0]
    assert item.name == "base-image"
    assert item.status == status
    assert tuple(choice.value for choice in item.choices) == choice_values
    assert not any(choice.value == "local/base:tag" for choice in item.choices)


def test_local_base_recovery_keeps_immutable_identity_not_mutable_tag(checkout, monkeypatch):
    project, record, _ = checkout
    replace_answers(project, record, {"base-image": {"reference": "local/base:moved", "image-id": LOCAL_ID, "lock-digest": "old"}})
    item = next(r for r in review(project, record).authorizations if r.name == "base-image")
    obtain = Mock(return_value=ImageDetails(LOCAL_ID, LOCAL_ID, {
        "devcapsule.image.managed": "true", "devcapsule.metadata.version": "1", "devcapsule.image.kind": "base",
    }, "linux", "amd64"))
    monkeypatch.setattr("devcapsule.commands.project.required_local_image", obtain)
    assert cli.main(shlex.split(item.choices[1].command(project))[1:]) == 0
    obtain.assert_called_once_with(LOCAL_ID)
    saved = load_toml(record)["authorization"]["base-image"]
    assert saved["reference"] == saved["image-id"] == LOCAL_ID
    assert review(project, record).ready


# Collect independent failures and reject partial output.
def test_independent_value_binding_secret_and_authorization_errors_are_collected(checkout):
    project, record, _ = checkout
    manifest = load_toml(project / ".devcapsule/devcapsule.toml")
    manifest["configuration"] = {"values": {"database.port": {"type": "integer", "required": True}}}
    broken = {"authorization": "broken", "configuration": {"bindings": {"host-directory": [], "host-environment": []}}, "state": []}
    result = review_configuration(manifest, OLD_LOCK, broken)
    assert not result.ready
    assert len(result.problems) == 5
    with pytest.raises(ProjectConfigurationError, match="Cannot consume an incomplete"):
        result.resolved_authorizations()
    with pytest.raises(ProjectConfigurationError, match="database.port"):
        result.require_ready(project)
    for term in ("database.port", "host-directory", "host-environment", "authorization", "state.adopted"):
        assert term in result.render(project)


def test_conflicting_state_bindings_do_not_publish_partial_resolution(checkout):
    project, record, resolution = checkout
    manifest = load_toml(project / ".devcapsule/devcapsule.toml")
    answers = load_toml(record)["authorization"]
    record.write_text(render_checkout(manifest, project, {"home": str(project)}, {}, answers,
        host_directory_bindings={"home": str(project)}))
    before = resolution.read_bytes()
    assert invoke(project, "config", "resolve") == 2
    assert resolution.read_bytes() == before
    assert "cannot be both adopted" in review(project, record).render(project)


@pytest.mark.parametrize("labels,answer,expected", [
    ({}, None, "host-x11"), ({}, True, "host-x11"), ({}, False, None),
    (CONTAINED, None, "contained"), (CONTAINED, True, "host-x11"), (CONTAINED, False, "contained"),
])
def test_display_decision_table(labels, answer, expected):
    if expected is None:
        with pytest.raises(CliError, match="explicitly denied"):
            select_display_transport(labels, host_x11_answer=answer)
    else:
        assert select_display_transport(labels, host_x11_answer=answer)[0] == expected


def test_display_denial_stops_before_materialization(checkout, monkeypatch):
    project, _, _ = checkout
    assert invoke(project, "config", "authorize", "host-x11", "false") == 0
    assert invoke(project, "config", "resolve") == 0
    events = []
    launch = install_external_fakes(monkeypatch, events, contained=False)
    assert invoke(project, "run") == 2
    assert events == ["obtain-base"]
    launch.assert_not_called()


@pytest.mark.parametrize("args", [
    ("--authorize", "host-x11", "typo"), ("--authorize", "base-image", "default"),
    ("--", "--network", "host"),
])
def test_invalid_run_once_choices_cannot_trigger_a_build(checkout, monkeypatch, args):
    project, _, _ = checkout
    events = []
    launch = install_external_fakes(monkeypatch, events)
    assert invoke(project, "run", *args) == 2
    assert events == []
    launch.assert_not_called()


def test_force_cannot_resurrect_a_revoked_host_permission(checkout, monkeypatch):
    project, record, _ = checkout
    assert invoke(project, "config", "unset", "host-browser") == 0
    before = record.read_bytes()
    events = []
    launch = install_external_fakes(monkeypatch, events)
    assert invoke(project, "run", "--force") == 0
    assert launch.call_args.args[0].enable_host_browser is False
    assert record.read_bytes() == before


def test_review_handles_invalid_and_removed_host_nodes(checkout):
    project, _, _ = checkout
    manifest = load_toml(project / ".devcapsule/devcapsule.toml")
    result = review_authorizations(manifest, OLD_LOCK, {"authorization": {
        "host-browser": "not a table", "host-x11": {"value": "bad"}, "removed": {},
    }})
    rows = {item.name: item for item in result}
    assert rows["host-browser"].status == rows["host-x11"].status == "invalid"
    assert rows["removed"].status == "unsupported"
    assert rows["removed"].choices == ()
    with pytest.raises(ProjectConfigurationError, match="removed"):
        resolved_checkout_authorizations(manifest, OLD_LOCK, {"authorization": {"removed": {}}})
    with pytest.raises(ProjectConfigurationError, match="must be a table"):
        review_authorizations(manifest, OLD_LOCK, {"authorization": []})


def test_review_has_no_display_advice_without_a_display_node(checkout):
    project, record, _ = checkout
    result = replace(review(project, record), authorizations=())
    assert "Display:" not in result.render(project)
    assert result.resolved_authorizations() == {}


def test_commands_quote_context_and_accept_no_context():
    choice = AuthorizationChoice("base-image", "default", "Accept recommendation")
    assert shlex.split(choice.command(Path("/tmp/a 'quoted' checkout")))[2:4] == ["--path", "/tmp/a 'quoted' checkout"]
    assert choice.command() == "devcapsule project config authorize base-image default"


@pytest.mark.parametrize("component,node,terms", [
    ("claude-code", "claude-code-download", "https://www.anthropic.com/legal/commercial-terms"),
    ("antigravity-cli", "antigravity-download", "https://antigravity.google/terms/"),
])
@pytest.mark.parametrize("answer,state", [
    (None, "missing-required"), (True, "authorized"), (False, "denied"), ("stale", "stale"),
])
def test_acquisition_decisions_use_the_same_review_contract(checkout, component, node, terms, answer, state):
    from copy import deepcopy
    project, record, _ = checkout
    manifest = load_toml(project / ".devcapsule/devcapsule.toml")
    lock = deepcopy(OLD_LOCK)
    lock["components"][component] = {
        "version": "1.0.0", "acquisition-authorization": node, "terms-url": terms,
    }
    declaration = authorization_declarations(manifest, lock)[node]
    answers = {} if answer is None else {
        node: {"value": False if answer is False else True,
               "recommendation-digest": "old" if answer == "stale" else declaration.recommendation_digest},
    }
    result = next(r for r in review_authorizations(manifest, lock, {"authorization": answers}) if r.name == node)
    assert result.status == state
    assert (result.problem is None) == (state == "authorized")
    if result.problem is not None:
        assert [choice.value for choice in result.choices] == ["true"]
    else:
        assert result.value is True


def test_regeneration_preserves_an_existing_denial(checkout):
    project, record, _ = checkout
    change_project(project, lock=False)
    assert invoke(project, "config", "authorize", "host-browser", "false") == 0
    assert invoke(project, "config", "resolve") == 0
    previous = load_toml(record)["authorization"]["host-browser"]
    assert invoke(project, "init", "--regenerate", "--authorize", "base-image", "default") == 0
    assert load_toml(record)["authorization"]["host-browser"] == previous
    assert review(project, record).resolved_authorizations()["host-browser"] is False


def test_repeated_init_does_not_turn_acquisition_denial_into_consent(checkout):
    project, record, _ = checkout
    assert invoke(project, "config", "need", "claude-code-agent",
                  "--authorize", "base-image", "default",
                  "--authorize", "claude-code-download", "true") == 0
    assert invoke(project, "config", "authorize", "claude-code-download", "false") == 0
    before = record.read_bytes()
    assert invoke(project, "init", "--regenerate", "--authorize", "base-image", "default") == 2
    assert record.read_bytes() == before


def test_local_recovery_refusal_preserves_the_record(checkout, monkeypatch):
    project, record, resolution = checkout
    replace_answers(project, record, {"base-image": {
        "reference": "local/base:old", "image-id": LOCAL_ID, "lock-digest": "old",
    }})
    before = record.read_bytes(), resolution.read_bytes()
    monkeypatch.setattr("devcapsule.commands.project.required_local_image", Mock(side_effect=CliError("image is absent")))
    choice = next(r for r in review(project, record).authorizations if r.name == "base-image").choices[1]
    assert cli.main(shlex.split(choice.command(project))[1:]) == 2
    assert (record.read_bytes(), resolution.read_bytes()) == before


def test_current_answers_have_one_resolved_interpretation(checkout):
    project, record, _ = checkout
    _, manifest = manifest_for(project)
    assert resolved_checkout_authorizations(manifest, OLD_LOCK, load_toml(record)) == {
        "base-image": OLD_BASE, "host-browser": True,
    }


def test_recovery_preserves_values_bindings_secrets_and_adopted_state(checkout, monkeypatch, capsys):
    project, record, resolution = checkout
    assert invoke(project, "config", "need", "codex-agent", "--authorize", "base-image", "default") == 0
    manifest_path = project / ".devcapsule/devcapsule.toml"
    manifest_path.write_text(manifest_path.read_text() + '''
[configuration.values."editor.theme"]
type = "string"
[configuration.values."runtime.memory-limit"]
type = "memory-size"
runtime-effect = "docker.memory-limit"
''')
    assert invoke(project, "config", "set", "editor.theme", "dark") == 0
    assert invoke(project, "config", "set", "runtime.memory-limit", "8GiB") == 0
    assert invoke(project, "config", "bind", "home", f"host-directory:{project}") == 0
    assert invoke(project, "config", "bind", "codex/openai-api-key", "host-environment:OPENAI_API_KEY") == 0
    record.write_text(record.read_text() + f'\n[state.adopted]\n"pycharm/config" = "{project.as_posix()}"\n')
    assert invoke(project, "config", "resolve") == 0
    before_record = load_toml(record)
    before_resolution = load_toml(resolution)
    monkeypatch.setenv("OPENAI_API_KEY", "test-secret-must-never-be-persisted")
    manifest_path.write_text(manifest_path.read_text() + '''
[host.browser.host-open.recommended]
value = true
justification = "Changed browser recommendation."
''')
    assert invoke(project, "config", "resolve") == 2
    for item in review(project, record).authorizations:
        if item.problem:
            assert cli.main(shlex.split(item.choices[0].command(project))[1:]) == 0
    assert invoke(project, "config", "resolve") == 0
    after_record = load_toml(record)
    after_resolution = load_toml(resolution)
    for key in ("configuration", "state"):
        assert after_record[key] == before_record[key]
        assert after_resolution[key] == before_resolution[key]
    assert after_resolution["runtime"]["memory-limit-bytes"] == 8 * 1024**3
    assert after_resolution["secret"] == before_resolution["secret"]
    out = capsys.readouterr()
    assert "test-secret-must-never-be-persisted" not in record.read_text() + resolution.read_text() + out.out + out.err


def test_force_uses_current_legacy_host_decisions(checkout, monkeypatch):
    project, record, _ = checkout
    manifest = load_toml(project / ".devcapsule/devcapsule.toml")
    answers = load_toml(record)["authorization"]
    record.write_text(render_checkout(manifest, project, {}, {"development-sudo": True}, answers))
    assert invoke(project, "config", "resolve") == 0
    replace_answers(project, record, answers)
    launch = install_external_fakes(monkeypatch, [])
    assert invoke(project, "run", "--force") == 0
    assert launch.call_args.args[0].enable_sudo is False
