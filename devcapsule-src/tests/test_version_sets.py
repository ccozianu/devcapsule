"""Real CLI/configuration/acquisition/materialization paths; Docker/GUI are controlled.

The unrelated widget component exercises the same engine as the real npm
Codex adapter. Launch assertions inspect independently built formation labels.
"""
from __future__ import annotations

import base64
from copy import deepcopy
import hashlib
import io
import json
import os
import shutil
import tomllib
from pathlib import Path
import tarfile
from types import SimpleNamespace

import pytest

from devcapsule import cli, version_sets
from devcapsule.compat import CliError
from devcapsule.components.catalog import COMPONENTS
from devcapsule.components.channels import ChannelReport, ChannelSelection, ChannelVersion
from devcapsule.components.codex import CodexComponent
from devcapsule.components.interface import LockedArtifactDeclaration, AcquisitionContract
from devcapsule.components.npm_channel import NpmChannel
from devcapsule.configuration.documents import canonical_digest, render_document
from devcapsule.configuration.execution import ExecutionConfiguration
from devcapsule.configuration.storage import load_toml, lock_for, manifest_for
from devcapsule.container_runtime.contract import ComponentRuntimeTemplate
from devcapsule.materialization import ImageDetails, cache_root
from devcapsule.platforms import Platform
from devcapsule.resolution_matrix import MATRICES


def invoke(project, *args):
    return cli.main(["project", "--path", str(project), *map(str, args)])


def archive(path, members):
    with tarfile.open(path, "w:gz") as stream:
        for name, data in members.items():
            info = tarfile.TarInfo(name)
            info.size, info.mode = len(data), 0o755
            stream.addfile(info, io.BytesIO(data))
    return path


class Widget(CodexComponent):
    id = "widget"
    capability = "widget-tool"

    def runtime_template(self):
        return ComponentRuntimeTemplate.from_mapping({"version": 1, "component": {
            "id": self.id, "adapter": "ancillary", "configuration": {},
            "persistence": {"home": "required", "xdg": "home-relative", "state_slots": []}}})

    def state_environment(self):
        return ()

    def state_seeds(self):
        return ()

    def secret_inputs(self):
        return ()

    def locked_artifacts(self, metadata, platform):
        return (LockedArtifactDeclaration(self.id, metadata["version"], metadata["url"], metadata["sha256"],
                                         "/opt/widget/" + metadata["version"], artifact_format="file"),)


@pytest.fixture(params=["widget", "codex"])
def journey(tmp_path, monkeypatch, request):
    licensed = request.param == "licensed-widget"
    component = "widget" if licensed else request.param
    for key, name in (("XDG_CONFIG_HOME", "config"), ("XDG_CACHE_HOME", "cache"),
                      ("XDG_STATE_HOME", "state"), ("XDG_DATA_HOME", "data"), ("HOME", "home")):
        monkeypatch.setenv(key, str(tmp_path / name))
    root = tmp_path / "project"
    config = root / ".devcapsule"
    config.mkdir(parents=True)
    manifest = {"devcapsule-schema-version": 1, "project": {"creator": "mailto:unit@example.test", "slug": "upgrade", "name": "Upgrade fixture", "mount": "/workspace/project"},
                "capabilities": {"need": ["python", "python-ide", "codex-agent"]}}
    (config / "devcapsule.toml").write_text(render_document(manifest))
    lock = tomllib.loads(MATRICES[Platform.current()].resolve(manifest["capabilities"]["need"], allow_unverified=True).render_lock())
    ide = archive(tmp_path / "ide.tgz", {"ide/bin/pycharm.sh": b"#!/bin/sh\nexit 0\n"})
    lock["components"]["pycharm"].update(url=ide.as_uri(), sha256=hashlib.sha256(ide.read_bytes()).hexdigest())
    metadata = {}
    for version in ("1.0.0", "2.0.0", "3.0.0"):
        if component == "widget":
            payload = tmp_path / f"widget-{version}"
            payload.write_bytes(version.encode())
            metadata[version] = {"version": version, "url": payload.as_uri(), "sha256": hashlib.sha256(payload.read_bytes()).hexdigest(), "delivery-policy": "local-materialization"}
        else:
            for suffix in ("", "-linux-x64"):
                name = "@openai/codex"
                data = {"name": name, "version": version + suffix, "engines": {"node": ">=16"}}
                if suffix:
                    data.update(os=["linux"], cpu=["x64"])
                if not suffix:
                    data["optionalDependencies"] = {"@openai/codex-linux-x64": f"npm:@openai/codex@{version}-linux-x64"}
                payload = archive(tmp_path / f"codex-{version}{suffix}.tgz", {"package/package.json": json.dumps(data).encode()})
                data["dist"] = {"tarball": "https://registry.npmjs.org/@openai/codex/-/" + payload.name,
                                "integrity": "sha512-" + base64.b64encode(hashlib.sha512(payload.read_bytes()).digest()).decode()}
                metadata[version + suffix] = data
    if component == "widget":
        class Channel:
            def check(self, current, platform):
                return ChannelReport("fixture distribution", ChannelVersion(current, "available"), (ChannelVersion("2.0.0", "available"),))
            def select(self, version, platform):
                return ChannelSelection(metadata[version], (platform,))
        definition = Widget()
        if licensed:
            monkeypatch.setattr(definition, "acquisition", lambda: AcquisitionContract("widget-acquisition", "https://example.test/terms", "Widget", "Example"))
            for item in metadata.values():
                item.update({"acquisition-authorization": "widget-acquisition", "terms-url": "https://example.test/terms"})
        monkeypatch.setattr(definition, "distribution_channel", lambda: Channel())
        monkeypatch.setitem(COMPONENTS, "widget", definition)
        lock["components"].pop("codex")
        lock["components"][component] = deepcopy(metadata["1.0.0"])
    else:
        def fetch(self, version=""):
            if not version:
                return {"dist-tags": {"latest": "2.0.0"}, "versions": deepcopy(metadata)}
            return deepcopy(metadata["2.0.0" if version == "latest" else version])
        monkeypatch.setattr(NpmChannel, "_metadata", fetch)
        from urllib.request import urlopen as real_open
        def open_payload(url, **kwargs):
            return real_open((tmp_path / url.rsplit("/", 1)[1]).as_uri(), **kwargs)
        monkeypatch.setattr("devcapsule.materialization.urlopen", open_payload)
        lock["components"][component] = dict(COMPONENTS[component].distribution_channel().select("1.0.0", "linux-amd64").metadata)
        version_sets._pin_artifacts(lock["components"][component])
    path = config / "devcapsule.linux-amd64.lock"
    path.write_text(render_document(lock))
    assert invoke(root, "config", "authorize", "base-image", "default") == 0
    if licensed:
        assert invoke(root, "config", "authorize", "widget-acquisition", "true") == 0
    assert invoke(root, "config", "authorize", "host-x11", "false") == 0
    assert invoke(root, "config", "resolve") == 0
    selected = ExecutionConfiguration.load(root).project
    runtime = tmp_path / "runtime.pex"
    runtime.write_bytes(b"fixture-runtime")
    monkeypatch.setattr("devcapsule.environment_realization.runtime_artifact", lambda: runtime)
    monkeypatch.setattr("devcapsule.runtime_artifact.runtime_artifact", lambda: runtime)
    monkeypatch.setattr("devcapsule.materialization.read_pex_build_info", lambda _: SimpleNamespace(
        build_mnemonic="fixture", source_repository="fixture", source_revision="fixture", source_url="fixture"))
    base = ImageDetails(lock["base"]["reference"], "sha256:" + "a" * 64, {
        "devcapsule.image.managed": "true", "devcapsule.metadata.version": "1", "devcapsule.image.kind": "base",
        "devcapsule.base.display": "contained"}, "linux", "amd64")
    images = {base.reference: base}
    state = SimpleNamespace(fail_build=False, exit_code=0, during_run=None, launched=[], built=[], images=images,
                            root=root, record=selected.checkout_path, resolution=selected.resolution_path, component=component,
                            lock=path, original=path.read_bytes(), metadata=metadata, base=base)
    def require(reference):
        if reference not in images:
            raise CliError("local image missing")
        return images[reference]
    def build(self, spec, **kwargs):
        if state.fail_build:
            raise CliError("controlled build failure")
        plan = spec.build_plan()
        descriptor = json.loads(dict(plan.labels)["devcapsule.materialization.descriptor"])
        images[plan.image] = ImageDetails(plan.image, "sha256:" + hashlib.sha256(plan.image.encode()).hexdigest(), dict(plan.labels),
            "linux", "amd64", tuple(descriptor["runtime"]["entrypoint"]), tuple(descriptor["runtime"]["command"]))
        state.built.append(descriptor)
    monkeypatch.setattr("devcapsule.environment_realization.ensure_local_image", require)
    monkeypatch.setattr("devcapsule.environment_realization.required_local_image", require)
    monkeypatch.setattr("devcapsule.environment_realization.optional_local_image", images.get)
    monkeypatch.setattr("devcapsule.environment_realization.component_formations", lambda _: ())
    monkeypatch.setattr("devcapsule.image_build.BuildxImageBuilder.build", build)
    def launch(options):
        state.launched.append((options, json.loads(images[options.image].labels["devcapsule.materialization.descriptor"])))
        if state.during_run:
            state.during_run()
        return state.exit_code
    monkeypatch.setattr("devcapsule.commands.project.run_pycharm", launch)
    return state


def preview_select(state, capsys, version="2.0.0", *, select=True):
    capsys.readouterr()
    assert invoke(state.root, "versions", "preview", state.component, version) == 0
    identity = capsys.readouterr().out.split("Preview ", 1)[1].splitlines()[0]
    if select:
        assert invoke(state.root, "versions", "select", identity, "--unvalidated") == 0
    return identity


def launched_version(state):
    return next(c["version"] for c in state.launched[-1][1]["components"] if c["id"] == state.component)


def test_upgrade_failure_rollback_and_repeated_recovery_use_real_launch(journey, capsys):
    s = journey
    assert invoke(s.root, "config", "authorize", "docker-daemon", "host-socket") == 0
    assert invoke(s.root, "config", "resolve") == 0
    assert invoke(s.root, "run") == 0
    a = s.launched[-1][1]
    preview_select(s, capsys)
    assert s.lock.read_bytes() == s.original
    s.exit_code = 17
    assert invoke(s.root, "run") == 17
    assert launched_version(s) == "2.0.0"
    assert len(list((version_sets.state_directory(s.root) / "known-good").glob("*"))) == 1
    assert invoke(s.root, "config", "authorize", "docker-daemon", "none") == 0
    # Rollback resolves current permissions; it must not restore A's old grant.
    assert invoke(s.root, "versions", "rollback") == 0
    s.exit_code = 0
    assert invoke(s.root, "run") == 0
    assert s.launched[-1][1] == a
    assert s.launched[-1][0].docker_mode.value == "none"
    saved_a = version_sets.set_id(ExecutionConfiguration.load(s.root).project.lock)
    assert invoke(s.root, "versions", "rollback", saved_a) == 0
    assert invoke(s.root, "run") == 0
    assert s.launched[-1][1] == a
    assert s.lock.read_bytes() == s.original


def test_failed_and_interrupted_preparation_leave_old_choice(journey, capsys, monkeypatch):
    s = journey
    assert invoke(s.root, "run") == 0
    before = (s.record.read_bytes(), s.resolution.read_bytes())
    identity = preview_select(s, capsys, select=False)
    s.fail_build = True
    assert invoke(s.root, "versions", "select", identity, "--unvalidated") == 2
    assert (s.record.read_bytes(), s.resolution.read_bytes()) == before
    s.fail_build = False
    import devcapsule.configuration.storage as storage
    write = storage.atomic_write
    def interrupt(path, content, mode=0o600):
        if path == s.record:
            raise KeyboardInterrupt()
        write(path, content, mode)
    monkeypatch.setattr(storage, "atomic_write", interrupt)
    with pytest.raises(KeyboardInterrupt):
        invoke(s.root, "versions", "select", identity, "--unvalidated")
    monkeypatch.setattr(storage, "atomic_write", write)
    assert invoke(s.root, "run") == 0
    assert launched_version(s) == "1.0.0"
    assert (s.record.read_bytes(), s.resolution.read_bytes()) == before


def test_old_session_certifies_only_launched_set(journey, capsys):
    s = journey
    before = s.record.read_bytes()
    s.during_run = lambda: preview_select(s, capsys)
    assert invoke(s.root, "run") == 0
    s.during_run = None
    assert ExecutionConfiguration.load(s.root).project.lock["components"][s.component]["version"] == "2.0.0"
    entries = version_sets._known(version_sets.Workspace.load(s.root))
    assert len(entries) == 1 and entries[0][1]["components"][s.component]["version"] == "1.0.0"
    snapshots = list((Path(os.environ['XDG_STATE_HOME']) / "devcapsule/config-history").rglob("devcapsule.checkout.toml"))
    assert len(snapshots) == 1 and snapshots[0].read_bytes() == before
    assert invoke(s.root, "versions", "rollback") == 0
    assert invoke(s.root, "run") == 0
    assert launched_version(s) == "1.0.0"


def test_divergence_proposal_follow_and_offline_reminders(journey, capsys, monkeypatch, tmp_path):
    s = journey
    assert invoke(s.root, "run") == 0
    assert invoke(s.root, "versions", "check") == 0
    assert invoke(s.root, "versions", "dismiss") == 0
    assert version_sets.reminder(s.root) == ""
    preview_select(s, capsys)
    assert invoke(s.root, "versions", "propose", tmp_path / "too-early.patch") == 2
    assert invoke(s.root, "run") == 0
    upstream = load_toml(s.lock)
    upstream["components"]["pycharm"]["version"] = "upstream-new"
    s.lock.write_text(render_document(upstream))
    assert invoke(s.root, "versions", "show") == 0
    assert "changed since selection" in capsys.readouterr().out
    assert invoke(s.root, "run") == 0
    assert s.launched[-1][1]["components"][0]["version"] != "upstream-new"
    patch = tmp_path / "upstream.patch"
    assert invoke(s.root, "versions", "propose", patch) == 0
    assert "Local zero-exit" in patch.read_text() and '"version" = "2.0.0"' in patch.read_text()
    assert invoke(s.root, "versions", "follow-project") == 0
    assert "version-set" in load_toml(s.record)
    assert invoke(s.root, "versions", "follow-project", "--apply") == 0
    assert invoke(s.root, "run") == 0
    assert s.launched[-1][1]["components"][0]["version"] == "upstream-new"
    # Returning to an unchanged recommendation is fully operational.
    s.lock.write_bytes(s.original)
    assert invoke(s.root, "versions", "follow-project", "--apply") == 0
    assert "version-set" not in load_toml(s.record)
    assert invoke(s.root, "run") == 0 and launched_version(s) == "1.0.0"


def test_missing_recovery_resources_preserve_current_set(journey, capsys):
    s = journey
    assert invoke(s.root, "run") == 0
    old_image = s.launched[-1][0].image
    preview_select(s, capsys)
    before = s.record.read_bytes()
    del s.images[old_image]
    shutil.rmtree(version_sets.state_directory(s.root) / "artifacts")
    shutil.rmtree(cache_root() / "artifacts")
    assert invoke(s.root, "versions", "rollback") == 2
    assert s.record.read_bytes() == before
    assert "--reacquire" in capsys.readouterr().err
    assert invoke(s.root, "versions", "rollback", "--reacquire") == 0
    assert invoke(s.root, "run") == 0 and launched_version(s) == "1.0.0"


def test_retained_artifacts_rebuild_predecessor_without_vendor_or_cache(journey, capsys, monkeypatch):
    s = journey
    assert invoke(s.root, "run") == 0
    old_image = s.launched[-1][0].image
    before = s.launched[-1][1]
    preview_select(s, capsys)
    del s.images[old_image]
    shutil.rmtree(cache_root() / "artifacts")
    def offline(*args, **kwargs):
        raise AssertionError("Rollback contacted a distribution server")
    monkeypatch.setattr("devcapsule.materialization.urlopen", offline)
    assert invoke(s.root, "versions", "rollback") == 0
    assert invoke(s.root, "run") == 0
    assert s.launched[-1][1] == before


def test_no_predecessor_and_declining_unvalidated_selection_are_nonmutating(journey, capsys):
    s = journey
    before = s.record.read_bytes(), s.resolution.read_bytes()
    assert invoke(s.root, "versions", "rollback") == 2
    assert "No known-good predecessor" in capsys.readouterr().err
    identity = preview_select(s, capsys, select=False)
    assert invoke(s.root, "versions", "select", identity) == 2
    assert not s.built
    assert (s.record.read_bytes(), s.resolution.read_bytes()) == before


def test_reminders_defer_new_candidate_and_offline_run(journey, monkeypatch, capsys):
    s = journey
    assert invoke(s.root, "run") == 0
    assert invoke(s.root, "versions", "check") == 0
    now = 2000000000.0
    monkeypatch.setattr(version_sets.time, "time", lambda: now)
    assert s.component + "@2.0.0" in version_sets.reminder(s.root)
    assert version_sets.reminder(s.root) == ""
    now += 7 * 86400 + 1
    assert s.component + "@2.0.0" in version_sets.reminder(s.root)
    assert invoke(s.root, "versions", "dismiss") == 0
    now += 8 * 86400
    assert version_sets.reminder(s.root) == ""
    path = version_sets.state_directory(s.root) / "check.toml"
    saved = load_toml(path)
    saved["candidates"] = [s.component + "@3.0.0"]
    path.write_text(render_document(saved))
    assert s.component + "@3.0.0" in version_sets.reminder(s.root)
    def offline(*args, **kwargs):
        raise AssertionError("ordinary launch must not check a channel")
    monkeypatch.setattr(COMPONENTS[s.component], "distribution_channel", offline)
    assert invoke(s.root, "run") == 0


def test_committed_activation_recovery_and_personal_state_survive(journey, capsys, monkeypatch, tmp_path):
    s = journey
    home = tmp_path / "personal-state"
    home.mkdir()
    credential = home / "login-fixture"
    credential.write_text("test token must not be copied into selection")
    work = s.root / "work.txt"
    work.write_text("user work")
    assert invoke(s.root, "state", "adopt", "home", "--from", home) == 0
    assert invoke(s.root, "config", "resolve") == 0
    assert invoke(s.root, "run") == 0
    identity = preview_select(s, capsys, select=False)
    import devcapsule.configuration.storage as storage
    write = storage.atomic_write
    def interrupt(path, content, mode=0o600):
        write(path, content, mode)
        if path == s.record:
            raise KeyboardInterrupt()
    monkeypatch.setattr(storage, "atomic_write", interrupt)
    with pytest.raises(KeyboardInterrupt):
        invoke(s.root, "versions", "select", identity, "--unvalidated")
    monkeypatch.setattr(storage, "atomic_write", write)
    assert invoke(s.root, "run") == 0
    assert launched_version(s) == "2.0.0"
    assert invoke(s.root, "versions", "rollback") == 0
    assert invoke(s.root, "run") == 0
    assert launched_version(s) == "1.0.0"
    assert s.launched[-1][0].persistent_home == home
    assert credential.read_text() == "test token must not be copied into selection"
    assert work.read_text() == "user work"
    assert "test token" not in s.record.read_text()


def test_local_base_rollback_uses_recorded_identity_after_tag_moves(journey, capsys, monkeypatch):
    from dataclasses import replace
    s = journey
    old = replace(s.base, reference="local/base:chosen", identity="sha256:" + "b" * 64)
    s.images[old.reference] = old
    s.images[old.identity] = replace(old, reference=old.identity)
    monkeypatch.setattr("devcapsule.commands.project.required_local_image", s.images.__getitem__)
    monkeypatch.setattr("devcapsule.configuration.operations.required_local_image", s.images.__getitem__)
    assert invoke(s.root, "config", "authorize", "base-image", old.reference) == 0
    assert invoke(s.root, "config", "resolve") == 0
    assert invoke(s.root, "run") == 0
    preview_select(s, capsys)
    s.images[old.reference] = replace(old, identity="sha256:" + "c" * 64)
    assert invoke(s.root, "versions", "rollback") == 0
    assert invoke(s.root, "run") == 0
    assert s.launched[-1][1]["base"]["identity"] == old.identity
    assert load_toml(s.record)["authorization"]["base-image"]["reference"] == old.identity


def test_declared_companion_constraint_prevents_unrelated_silent_change(journey, monkeypatch, capsys):
    from dataclasses import replace
    s = journey
    channel = COMPONENTS[s.component].distribution_channel()
    original = channel.select
    monkeypatch.setattr(channel, "select", lambda v, p: replace(original(v, p), requires=(("pycharm", "requires-a-different-version"),)))
    monkeypatch.setattr(COMPONENTS[s.component], "distribution_channel", lambda: channel)
    before = s.record.read_bytes()
    assert invoke(s.root, "versions", "preview", s.component, "2.0.0") == 2
    assert "requires pycharm" in capsys.readouterr().err
    assert s.record.read_bytes() == before and not s.built


@pytest.mark.parametrize("journey", ["licensed-widget"], indirect=True)
def test_candidate_acquisition_answers_do_not_renew_host_permissions(journey, capsys):
    s = journey
    assert invoke(s.root, "run") == 0
    identity = preview_select(s, capsys, select=False)
    before = s.record.read_bytes()
    assert invoke(s.root, "versions", "select", identity, "--unvalidated") == 2
    assert s.record.read_bytes() == before
    assert invoke(s.root, "versions", "select", identity, "--unvalidated", "--authorize", "docker-daemon", "host-socket") == 2
    assert s.record.read_bytes() == before
    assert invoke(s.root, "versions", "select", identity, "--unvalidated", "--authorize", "widget-acquisition", "true") == 0
    assert invoke(s.root, "run") == 0 and launched_version(s) == "2.0.0"
    assert invoke(s.root, "config", "authorize", "widget-acquisition", "false") == 0
    assert invoke(s.root, "versions", "rollback") == 2
    assert load_toml(s.record)["authorization"]["widget-acquisition"]["value"] is False
    assert invoke(s.root, "versions", "rollback", "--authorize", "widget-acquisition", "true") == 0
    assert invoke(s.root, "run") == 0 and launched_version(s) == "1.0.0"
    upstream = load_toml(s.lock)
    upstream["components"]["widget"] = s.metadata["3.0.0"]
    s.lock.write_text(render_document(upstream))
    assert invoke(s.root, "versions", "follow-project", "--apply") == 2
    assert invoke(s.root, "versions", "follow-project", "--apply", "--authorize", "widget-acquisition", "true") == 0
    assert invoke(s.root, "run") == 0 and launched_version(s) == "3.0.0"
    assert s.launched[-1][0].docker_mode.value == "none"
