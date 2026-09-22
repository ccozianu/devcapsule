# Tested patch: retire run-image and print the ordinary Docker command

From: project-management
To: maintenance
Date: 2026-09-22

Supersedes `2026-09-22-project-management-retire-run-image-print-command.md`
(sent at coordination `3231b2dcd7f5`). Preserve that message as history; this
one supplies a prepared patch rather than asking you to reimplement the design.
The owner explicitly requested a diff handoff instead of committing source on
project-management. No implementation commit exists there. After verified mail
delivery, the sender restores only these source changes to its baseline.

Maintenance owns the existing run-image network/parity defect and this bounded
replacement for 0.2.14 preparation. Accepting means reviewing and applying this
patch on your selected branch, validating that tree, and delivering through the
ordinary owner-operated GitHub PR flow. Patch delivery is not feature integration
and does not switch either checkout's workstream. The product decision remains
settled; the implementation is yours to review.

## Contract

Remove `devcapsule project run-image`. Add `project run --print-command` to prepare
the currently selected ordinary environment and print the final Docker argv,
including external-daemon path translation, as quoted shell text on stdout.
Separate `#` comment lines describe transient files, helper sockets and environment
dependencies; preparation diagnostics, including child output, use stderr.
Do not launch the project container, watch for its display, offer/select upgrades,
or record print success as successful configuration/version use. Keep normal
cleanup. Image acquisition/build and normal state preparation may still happen.
No editor integration, retained-resource bundle or standalone replay promise.
Secret bindings remain `--env NAME`; no environment dump or secret-value comments.

The actual launch builder is reused with an optional report callback at its final
invocation boundary. Normal launches retain their existing path. Help/removal,
current README/design guidance, and source/packaged smoke expectations are updated.
Tests cover both PyCharm and VSCodium, contained display and host X11, translated
bind paths, secret-name forwarding, shell metacharacters, cleanup, stderr isolation,
and absence of project launch/upgrade offers/success recording in print mode.

Do not close the entire shared host-network-default defect solely from removing
run-image: the legacy `pycharm run` caller still uses that default. This patch
intentionally does not change its network contract.

## Patch provenance and validation

Base: `44166ebf9a801db4341aea9306a6267f7bd8ec60` on
`project-management/coordination`. Its differences from main are coordination/design
records, not prerequisites for this implementation. The embedded patch also passes
`git apply --cached --check --whitespace=error` against main
`20336d80b47165dfd4a5e557b54689cd2b74804c` in a temporary index.

Patch SHA-256: `79794674807cbd3c1784599ac1ed0ae8e03995c0958917fb0e4347e60b0cbea9`.
Save exactly the contents of the final diff fence, with its final newline, as a
`.patch` file. From the repository root, review it, run `git apply --check`, then
`git apply`. It includes both new Python files; it has no status-file changes or
commits to cherry-pick. If your source has moved, reconcile against your branch
rather than assuming this historical applicability check still holds.

Validation on the uncommitted patched source:

- Focused checks: 71 passed.
- Required `nox -s build`: 1,041 passed, 18 deselected, one existing xfail;
  mypy passed for 167 files; nine packaged integration checks passed.
- Shell syntax and local PEX smoke passed. The revision-bearing public artifact
  is deliberately skipped by the existing dirty-tree policy.
- No new real Docker environment was launched for this text-generation change.

The first build exposed obsolete source/packaged smoke expectations for run-image;
they now require the removed command's rejection. The complete gate was then rerun.
The owner-requested workflow proposal is separate mail to workflow-improvements,
`2026-09-22-project-management-diff-handoff-recovery.md`; this handoff relies on
explicit owner direction, not on that proposal already being policy.

## Patch

```diff
diff --git a/devcapsule-src/README.md b/devcapsule-src/README.md
index 30d6042..26c5d48 100644
--- a/devcapsule-src/README.md
+++ b/devcapsule-src/README.md
@@ -803,7 +803,7 @@ is unchanged.
 External hyperlinks use a separate, opt-in host integration. Authorize
 `host-browser` persistently with `devcapsule project config authorize
 host-browser true`, or for one launch with `project run --authorize
-host-browser true` (`run-image` and `pycharm run` keep their dedicated
+host-browser true` (`pycharm run` keeps its dedicated
 `--host-browser` flag) to let `xdg-open` inside the capsule ask a
 launcher-owned Unix-socket broker to open an absolute HTTP(S) URL in the
 physical host's default browser. The protocol does not expose the host
@@ -1017,7 +1017,7 @@ devcapsule pycharm run --project /path/to/project
 devcapsule pycharm run
 devcapsule pycharm run --project /path/to/project --config-mode project
 devcapsule pycharm run --profile codex --project-state-root /path/to/workspace/.state
-devcapsule project --path /path/to/project run-image pycharm-isolated:latest
+devcapsule project --path /path/to/project run --print-command > launch.sh
 devcapsule pycharm build --pycharm /path/to/pycharm.tar.gz
 devcapsule pycharm check-runtime
 devcapsule bootstrap
@@ -1116,34 +1116,30 @@ tool caches use `$XDG_CACHE_HOME/devcapsule/`, while logs use
 place: their `home`, `config`, `plugins`, `system`, `log`, and `home/.cache`
 subdirectories are mounted independently at the new container destinations.
 
-`run-image IMAGE` is the expert, lock-independent PyCharm-compatible image path
-for construction and diagnosis. It passes `--pull=never` to Docker, so a
-missing local image fails instead of pulling or resolving another image. It
-defaults to no Docker-daemon access. Use
-`--docker-daemon host-socket` and `--development-sudo` only as explicit
-run-once relaxations. `--host-browser` is a separate run-once capability for
-opening HTTP(S) hyperlinks in the physical host browser; it does not imply
-Docker, network, sudo, or credential access. The broader capability-first
-state-management CLI remains under development.
-
-The first dogfood validation intentionally supplies the existing directories
-once, before the planned `state adopt` command persists those mappings:
+### Inspect the Docker launch command
 
 ```bash
-./dist/devcapsule.pex project --path "$HOST_PROJECT_ROOT" \
-  run-image mycodespace.ai/pycharm:debug-v018 \
-  --global-settings ~/.config/docker-pycharm-codex/state/ \
-  --plugins ~/.config/docker-pycharm-codex/plugins \
-  --project-mount /workspace/301e4208ef81-ChatGPT_Codex \
-  --project-state "$PROJECT_STATE" \
-  --docker-daemon host-socket \
-  --development-sudo
+devcapsule project --path /path/to/project run --print-command > launch.sh
 ```
 
-The explicit project mount preserves the absolute path already stored in the
-adopted PyCharm workspace and interpreter configuration. Omitting it during
-this migration makes saved paths such as
-`/workspace/301e4208ef81-ChatGPT_Codex/.venv/bin/python` appear missing.
+This prepares the currently selected environment through ordinary configuration
+and authorization checks, then prints the actual shell-quoted Docker command.
+It may acquire/build the image and prepare state; it does not launch the project
+container, open a desktop, check/select component updates or record successful use.
+Preparation messages go to stderr, keeping stdout suitable for a file or editor.
+Run-once configuration choices and accepted Docker passthrough options still apply.
+
+The output is for inspection and manual editing, **not a standalone replay script**.
+Comments identify temporary runtime files removed on return, helper sockets that
+require a live service, and environment dependencies. Persistent mounts still point
+at real project/IDE state. The developer must provide missing resources before
+manual execution and owns any changes to the command. Secret environment bindings
+remain variable names; their values are not copied into the output. Do not share
+output without reviewing its host paths and any raw arguments you supplied.
+
+The former `project run-image` arbitrary-image convenience command is removed.
+For an arbitrary image, use Docker directly; use the print option to inspect what
+DevCapsule would execute for a configured project.
 
 Unsupported command shapes such as top-level `devcapsule run`,
 `devcapsule run-image`, `devcapsule config`, `devcapsule state`, and
diff --git a/devcapsule-src/devcapsule/commands/project.py b/devcapsule-src/devcapsule/commands/project.py
index 57484f6..9153ccf 100644
--- a/devcapsule-src/devcapsule/commands/project.py
+++ b/devcapsule-src/devcapsule/commands/project.py
@@ -21,8 +21,9 @@ import os
 import sys
 import termios
 import tty
-from typing import Any, Mapping
+from typing import Any, Callable, Mapping
 
+from devcapsule.launch.command_output import preparation_diagnostics
 from devcapsule.commands.framework import (
     Command,
     Group,
@@ -888,10 +889,27 @@ class ProjectRunCommand(Command):
         parser.add_argument("--name", dest="container_name")
         parser.add_argument("--no-update-check", action="store_true",
                             help="Skip the daily interactive distribution refresh; cached critical notices still allow a decision.")
+        parser.add_argument("--print-command", action="store_true",
+                            help="Prepare the selected environment and print the Docker command instead of launching; comments identify transient dependencies.")
         add_carrier_options(parser, families=("set", "authorize"))
 
     @classmethod
     def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
+        if not arguments.print_command:
+            return cls._run(arguments, context)
+        commands: list[str] = []
+        # Keep both Python narration and inherited child-process output off
+        # stdout. Emit only after preparation and its cleanup have succeeded.
+        with preparation_diagnostics():
+            result = cls._run(arguments, context, command_report=commands.append)
+        if result == 0:
+            for command in commands:
+                sys.stdout.write(command)
+        return result
+
+    @classmethod
+    def _run(cls, arguments: argparse.Namespace, context: object | None,
+             command_report: Callable[[str], None] | None = None) -> int:
         admitted = ExecutionConfiguration.load(_project_context(context).start_path(), force=arguments.force)
         # Reject invalid launch overrides before an optional upgrade can change
         # selection. Reload afterward so this launch and its success record use
@@ -903,7 +921,7 @@ class ProjectRunCommand(Command):
                 reject_launcher_owned_docker_options(docker_options)
             except PycharmRunError as exc:
                 raise ProjectConfigurationError(str(exc)) from exc
-        if not offer_upgrades(admitted.project.root, refresh=not arguments.no_update_check):
+        if command_report is None and not offer_upgrades(admitted.project.root, refresh=not arguments.no_update_check):
             print("Launch cancelled; no session was started.")
             return 1
         admitted = ExecutionConfiguration.load(admitted.project.root, force=arguments.force)
@@ -1036,6 +1054,7 @@ class ProjectRunCommand(Command):
             PycharmRunOptions(
                 project=root,
                 inherit_legacy_configuration=False,
+                command_report=command_report,
                 project_mount=str(runtime["project-mount"]),
                 image=image,
                 name=arguments.container_name,
@@ -1070,6 +1089,8 @@ class ProjectRunCommand(Command):
                 display_transport=display_transport,
             )
         )
+        if command_report is not None:
+            return exit_code  # Printing is never evidence of successful use.
         if exit_code == 0:
             # D-0008: a zero exit proves this configuration; record it as a
             # known-good generation unless identical content already exists.
@@ -1149,72 +1170,6 @@ def _run_once_answers(
     return overrides, memory_override
 
 
-class ProjectRunImageCommand(Command):
-    name = "run-image"
-    help = (
-        "Run a local PyCharm-compatible image without project lock resolution. "
-        "Everything after '--' is handed verbatim to 'docker run'."
-    )
-    passthrough_dest = "docker_options"
-    passthrough_metavar = "DOCKER-RUN-OPTIONS"
-
-    @classmethod
-    def configure(cls, parser: argparse.ArgumentParser) -> None:
-        parser.add_argument("image")
-        parser.add_argument("--project-mount", help="Absolute in-container project path.")
-        parser.add_argument("--home", type=Path)
-        parser.add_argument("--global-settings", type=Path)
-        parser.add_argument("--plugins", type=Path)
-        parser.add_argument("--project-state", type=Path)
-        parser.add_argument(
-            "--docker-daemon", choices=["none", "host-socket"], default="none"
-        )
-        parser.add_argument("--development-sudo", action="store_true")
-        parser.add_argument(
-            "--host-browser",
-            action=argparse.BooleanOptionalAction,
-            default=False,
-            help="Explicitly allow HTTP(S) links to open in the physical host's default browser.",
-        )
-        parser.add_argument("--name", dest="container_name")
-
-    @classmethod
-    def run(cls, arguments: argparse.Namespace, context: object | None) -> int:
-        candidate = _project_context(context).start_path()
-        try:
-            project = discover_project(candidate)
-        except ProjectConfigurationError:
-            project = candidate.expanduser().resolve()
-        if not project.is_dir():
-            raise ProjectConfigurationError(f"Project directory does not exist: {project}")
-        docker_mode = (
-            DockerMode.host if arguments.docker_daemon == "host-socket" else DockerMode.none
-        )
-        docker_options = list(arguments.docker_options)
-        if docker_options:
-            reject_launcher_owned_docker_options(docker_options)
-            print(
-                "WARNING: passing raw docker run options: " + " ".join(docker_options),
-                file=sys.stderr,
-            )
-        return run_pycharm(
-            PycharmRunOptions(
-                project=project,
-                project_mount=arguments.project_mount,
-                image=arguments.image,
-                name=arguments.container_name,
-                persistent_home=arguments.home,
-                global_settings=arguments.global_settings,
-                project_state=arguments.project_state,
-                plugins=arguments.plugins,
-                docker_mode=docker_mode,
-                enable_sudo=arguments.development_sudo,
-                enable_host_browser=arguments.host_browser,
-                extra_docker_args=["--pull=never", *docker_options],
-            )
-        )
-
-
 class ProjectCommand(Group):
     name = "project"
     help = "Initialize, list, configure, and run DevCapsule project checkouts."
@@ -1253,7 +1208,6 @@ class ProjectCommand(Group):
             StateGroup.name: StateGroup,
             RecursiveE2EGroup.name: RecursiveE2EGroup,
             ProjectRunCommand.name: ProjectRunCommand,
-            ProjectRunImageCommand.name: ProjectRunImageCommand,
         }
 
 
diff --git a/devcapsule-src/devcapsule/launch/pycharm/_launcher.py b/devcapsule-src/devcapsule/launch/pycharm/_launcher.py
index 2c1468f..b0c3598 100644
--- a/devcapsule-src/devcapsule/launch/pycharm/_launcher.py
+++ b/devcapsule-src/devcapsule/launch/pycharm/_launcher.py
@@ -50,6 +50,7 @@ from ...host_open import (
     HostOpenError,
     host_open_bridge,
 )
+from ..command_output import render_command
 from ...materialization import RUNTIME_PLAN_PATH
 from ...runtime_configuration import CONFIGURATION_PATH, CONTEXT_PATH, LaunchConfiguration
 from ...project import ProjectMountError
@@ -114,6 +115,7 @@ class PycharmRunOptions:
     # ambient launcher options. Host observations and explicit secret sources
     # remain available in either mode.
     inherit_legacy_configuration: bool = True
+    command_report: Callable[[str], None] | None = None
     profile: str | None = None
     image: str | None = None
     name: str | None = None
@@ -249,6 +251,9 @@ def run_pycharm(options: PycharmRunOptions, env: Mapping[str, str] | None = None
                 command = ["docker", "run", *docker_args, config.image]
                 if not config.use_image_process:
                     command.extend(["/opt/pycharm/bin/pycharm.sh", config.project_mount])
+                if options.command_report is not None:
+                    options.command_report(describe_run_command(command, config, files))
+                    return 0  # Cleanup still runs; no container or display watcher.
                 stop_watching = Event()
                 if config.display_transport == CONTAINED_DISPLAY_TRANSPORT:
                     assert config.display_host_port is not None
@@ -277,6 +282,36 @@ def run_pycharm(options: PycharmRunOptions, env: Mapping[str, str] | None = None
         raise PycharmRunError(str(exc)) from exc
 
 
+def describe_run_command(command: list[str], config: PycharmRunConfig,
+                         files: TempRuntimeFiles) -> str:
+    comments = [
+        "Diagnostic Docker command; the project container has NOT been started.",
+        "Preparation may have acquired/built the selected image and prepared state directories.",
+        "This is not a standalone replay script. Review dependencies before manual execution.",
+        "Use the same host and Docker context/environment (including DOCKER_HOST if set).",
+        "Project and persistent-state mounts refer to existing host paths; edits can change host access.",
+        "The following local staging files are removed when this command returns.",
+        "Bind sources in the command may be translated to external Docker-daemon host paths.",
+    ]
+    for label, path in (
+        ("Xauthority", files.xauth_file if config.display_transport != CONTAINED_DISPLAY_TRANSPORT else None),
+        ("User identity", files.passwd_file), ("Group identity", files.group_file),
+        ("Shadow file", files.shadow_file), ("Sudo policy", files.sudoers_file),
+        ("Git token file", files.token_file), ("Runtime plan", files.runtime_plan_file),
+        ("Display token", files.display_token_file), ("Launch context", files.launch_context_file),
+    ):
+        if path is not None:
+            comments.append(f"Temporary {label}: {path}")
+    if config.host_browser_socket is not None:
+        comments.append("Host-browser socket requires a live broker; a broker owned by this invocation stops on return.")
+    if config.display_transport == CONTAINED_DISPLAY_TRANSPORT:
+        comments.append("Contained display needs its temporary token file; the chosen host port is not reserved for later use.")
+    if config.secret_environment:
+        comments.append("Required environment variables (values omitted): " + ", ".join(config.secret_environment))
+    comments.append("No successful-use history was recorded. Manual execution and any edits are your responsibility.")
+    return render_command(command, comments)
+
+
 def host_backed_runtime_environment(env: Mapping[str, str]) -> dict[str, str]:
     """Stage transient launch files where an external daemon can read them.
 
diff --git a/devcapsule-src/noxfile.py b/devcapsule-src/noxfile.py
index eff1fbd..75cb1b1 100644
--- a/devcapsule-src/noxfile.py
+++ b/devcapsule-src/noxfile.py
@@ -186,7 +186,7 @@ def run_smoke(session: nox.Session) -> None:
     session.run("python", "-m", "devcapsule", "project", "config", "bind", "--help")
     session.run("python", "-m", "devcapsule", "project", "config", "authorize", "--help")
     session.run("python", "-m", "devcapsule", "project", "run", "--help")
-    session.run("python", "-m", "devcapsule", "project", "run-image", "--help")
+    session.run("python", "-m", "devcapsule", "project", "run-image", "--help", success_codes=[2])
     session.run("python", "-m", "devcapsule", "project", "recursive-e2e", "preflight", "--help")
     session.run("python", "-m", "devcapsule", "project", "recursive-e2e", "run", "--help")
     session.run("python", "-m", "devcapsule", "project", "recursive-e2e", "launch-successor", "--help")
@@ -255,7 +255,7 @@ def smoke_pex(session: nox.Session, path: Path = TEST_PEX_PATH) -> None:
     session.run(str(path), "project", "config", "bind", "--help", external=True)
     session.run(str(path), "project", "config", "authorize", "--help", external=True)
     session.run(str(path), "project", "run", "--help", external=True)
-    session.run(str(path), "project", "run-image", "--help", external=True)
+    session.run(str(path), "project", "run-image", "--help", success_codes=[2], external=True)
     session.run(
         str(path), "project", "recursive-e2e", "preflight", "--help", external=True
     )
diff --git a/devcapsule-src/tests/test_cli.py b/devcapsule-src/tests/test_cli.py
index a33f2f8..625f30d 100644
--- a/devcapsule-src/tests/test_cli.py
+++ b/devcapsule-src/tests/test_cli.py
@@ -84,56 +84,10 @@ def test_run_pycharm_uses_translated_python_launcher(tmp_path: Path) -> None:
     assert not any(arg.endswith(",dst=/ide-global-settings/home/.gemini") for arg in command)
 
 
-def test_run_image_uses_pycharm_persistence_adapter(tmp_path: Path) -> None:
-    project = tmp_path / "example"
-    project.mkdir()
-    global_settings = tmp_path / "global-settings"
-    plugins = tmp_path / "plugins"
-    project_state = tmp_path / "project-state"
-
-    with (
-        patch("devcapsule.launch.pycharm._launcher.shutil.which", return_value=None),
-        patch("devcapsule.launch.pycharm._launcher.subprocess.run") as run,
-        patch.dict(
-            os.environ,
-            {
-                "DISPLAY": ":1",
-                "HOME": str(tmp_path / "host-home"),
-                "XDG_DATA_HOME": str(tmp_path / "data"),
-                "PYCHARM_GIT_IDENTITY_FROM_HOST": "0",
-            },
-            clear=False,
-        ),
-    ):
-        run.return_value.returncode = 0
-        result = cli.main(
-            [
-                "project",
-                "--path",
-                str(project),
-                "run-image",
-                "mycodespace.ai/pycharm:debug-v017",
-                "--project-mount",
-                "/workspace/existing-checkout",
-                "--global-settings",
-                str(global_settings),
-                "--plugins",
-                str(plugins),
-                "--project-state",
-                str(project_state),
-            ]
-        )
-
-    assert result == 0
-    command = run.call_args.args[0]
-    assert "mycodespace.ai/pycharm:debug-v017" in command
-    assert "--pull=never" in command
-    assert "--workdir" in command
-    assert command[command.index("--workdir") + 1] == "/workspace/existing-checkout"
-    assert f"type=bind,src={project.resolve()},dst=/workspace/existing-checkout" in command
-    assert f"type=bind,src={(global_settings / 'home').resolve()},dst=/home/devcapsule" in command
-    assert f"type=bind,src={(global_settings / 'config').resolve()},dst=/ide-config" in command
-    assert f"type=bind,src={plugins.resolve()},dst=/ide-plugins" in command
+def test_project_run_image_is_retired(tmp_path, capsys) -> None:
+    assert cli.main(["project", "--path", str(tmp_path), "--help"]) == 0
+    assert "run-image" not in capsys.readouterr().out
+    assert cli.main(["project", "--path", str(tmp_path), "run-image", "unused"]) != 0
 
 
 def test_run_pycharm_defaults_project_to_current_directory(tmp_path: Path, monkeypatch) -> None:
diff --git a/devcapsule-src/tests/test_project_commands.py b/devcapsule-src/tests/test_project_commands.py
index 61796f2..a101b49 100644
--- a/devcapsule-src/tests/test_project_commands.py
+++ b/devcapsule-src/tests/test_project_commands.py
@@ -2024,3 +2024,83 @@ def test_config_list_shows_the_recorded_answer_and_names_a_denial(
     assert rows["host-x11"][2:4] == ["denied", "false"]
     assert rows["host-browser"][2:4] == ["authorized", "true"]
     assert rows["development-sudo"][2:4] == ["available", "true"]
+
+
+@pytest.mark.parametrize('surface,needs', [('pycharm', ['python', 'python-ide']), ('codium', ['node', 'frontend-ide'])])
+@pytest.mark.parametrize('display', ['contained', 'host-x11'])
+def test_print_command_uses_real_launch_builder_without_launch_or_success(
+    tmp_path, monkeypatch, capfd, surface, needs, display,
+):
+    import shlex
+    import subprocess
+    from devcapsule.commands import project as command
+    from devcapsule.launch.pycharm import _launcher as launcher
+    from devcapsule.configuration.execution import ExecutionConfiguration
+
+    project = tmp_path / 'project'
+    project.mkdir()
+    monkeypatch.chdir(project)
+    for key, leaf in [('HOME', 'home'), ('XDG_CONFIG_HOME', 'config'), ('XDG_DATA_HOME', 'data'),
+                      ('XDG_STATE_HOME', 'state'), ('XDG_RUNTIME_DIR', 'runtime')]:
+        monkeypatch.setenv(key, str(tmp_path / leaf))
+    monkeypatch.setenv('DISPLAY', ':fixture')
+    monkeypatch.setenv('PRINT_TEST_SECRET', 'do-not-render-this-value')
+    need_arguments = [arg for need in needs for arg in ('--need', need)]
+    assert cli.main(['project', 'init', *need_arguments, '--creator', 'https://example.test',
+                     '--unverified', '--authorize', 'base-image', 'default']) == 0
+    assert cli.main(['project', 'config', 'authorize', 'host-x11', str(display == 'host-x11').lower()]) == 0
+    assert cli.main(['project', 'config', 'resolve']) == 0
+    selected = ExecutionConfiguration.load(project).project
+    locked = parse_locked_environment(selected.lock)
+    realized = SimpleNamespace(image=SimpleNamespace(labels={'devcapsule.base.display': 'contained'},
+                                 reference='devcapsule-local-' + surface + ':fixture'), created=False, locked=locked)
+    before = {p: p.read_bytes() for p in (selected.checkout_path, selected.resolution_path)}
+    def forbidden(*args, **kwargs):
+        pytest.fail('print mode must not launch, offer updates, watch display, or record successful use')
+    monkeypatch.setattr(command, 'offer_upgrades', forbidden)
+    monkeypatch.setattr(command, 'record_known_good_configuration', forbidden)
+    monkeypatch.setattr(command.version_sets, 'record_success', forbidden)
+    def realize(*args, **kwargs):
+        print('Python preparation progress')
+        os.write(1, b'Child-style preparation progress\n')
+        return realized
+    monkeypatch.setattr(command, 'realize_environment', realize)
+    monkeypatch.setattr(launcher, 'requires_translation', lambda env: False)
+    monkeypatch.setattr(launcher, 'write_xauthority', lambda path, env: None)
+    monkeypatch.setattr(launcher, 'apply_host_git_identity', lambda mode, name, email: (name, email))
+    monkeypatch.setattr(launcher, 'watch_display_ready', forbidden)
+    original_run = launcher.run_pycharm
+    # Supply a secret name at the actual launcher boundary, without changing
+    # selected checkout authorization or the production argument builder.
+    def run(options):
+        options.secret_environment = ('PRINT_TEST_SECRET',)
+        return original_run(options)
+    monkeypatch.setattr(command, 'run_pycharm', run)
+    captured = {}
+    original_build = launcher.build_docker_args
+    def build(config, files, env):
+        args = original_build(config, files, env)
+        captured.update(args=args, image=config.image, files=files)
+        return args
+    monkeypatch.setattr(launcher, 'build_docker_args', build)
+    # A synthetic external-daemon translation proves rendering sees the final
+    # host-side bind paths rather than an earlier intermediate plan.
+    monkeypatch.setattr(launcher, 'translate_for_external_daemon',
+                        lambda args, env: [arg.replace(str(tmp_path), '/daemon/fixture') for arg in args])
+    capfd.readouterr()
+    with patch.object(launcher.subprocess, 'run', side_effect=forbidden):
+        assert cli.main(['project', 'run', '--print-command']) == 0
+    output = capfd.readouterr()
+    assert 'Python preparation progress' in output.err
+    assert 'Child-style preparation progress' in output.err
+    assert 'preparation progress' not in output.out
+    assert 'do-not-render-this-value' not in output.out
+    assert 'Required environment variables' in output.out
+    assert 'Temporary Runtime plan:' in output.out
+    assert ('Temporary Display token:' in output.out) == (display == 'contained')
+    expected = ['docker', 'run', *[a.replace(str(tmp_path), '/daemon/fixture') for a in captured['args']], captured['image']]
+    assert shlex.split(output.out.replace('\\\n', ''), comments=True) == expected
+    subprocess.run(['sh', '-n'], input=output.out, text=True, check=True)
+    assert all(not path.exists() for path in vars(captured['files']).values() if isinstance(path, Path))
+    assert all(p.read_bytes() == content for p, content in before.items())
+    assert not (tmp_path / 'state' / 'devcapsule' / 'config-history').exists()
diff --git a/engineering-docs/design-notes/devcapsule/v1-user-experience.md b/engineering-docs/design-notes/devcapsule/v1-user-experience.md
index caa5221..e060542 100644
--- a/engineering-docs/design-notes/devcapsule/v1-user-experience.md
+++ b/engineering-docs/design-notes/devcapsule/v1-user-experience.md
@@ -42,17 +42,15 @@ devcapsule
 │   ├── config set|bind|authorize|resolve ...
 │   ├── state ...
 │   ├── lock ...
-│   ├── run ...
-│   └── run-image IMAGE ...
+│   └── run [--print-command] ...
 └── images
     ├── list
     └── build --type base|environment ...
 ```
 
 The `project` tree owns declarations, registered checkouts, developer
-configuration and state, locks, and execution. This includes the expert,
-lock-independent `run-image` path because it still operates on project source,
-state, and host choices. The `images` tree owns the workstation's managed image
+configuration and state, locks, and execution. Diagnostic `run --print-command`
+exposes the ordinary launch for inspection. The `images` tree owns the workstation's managed image
 inventory and image formation.
 
 ## Four Things With Different Owners
@@ -403,8 +401,7 @@ devcapsule project config unset      NAME
   stops modeling docker's option surface; raw options are conspicuously
   reported as a deviation from the resolved plan. The bespoke run flags
   (`--docker-daemon`, `--development-sudo`, `--host-browser`) are dropped
-  from `run`; `run-image` keeps its dedicated flags because it deliberately
-  reads no lock and therefore has no node registry.
+  from `run`. The former arbitrary-image `run-image` path is retired.
 - `host-browser`, `docker-daemon`, and `development-sudo` are proper
   authorization nodes (settled 2026-08-24) that exist on every project as
   workstation capabilities: denial stays the default, a project
@@ -1285,11 +1282,13 @@ fully pinned, materialized under a distinct identity, and shown conspicuously
 as a deviation from the committed default. The representation and support
 contract for local alternatives remain an open V1 design question.
 
-`devcapsule project [--path PATH] run-image IMAGE` remains the expert escape
-hatch for an arbitrary local image. It does not claim to reproduce the
-committed environment and does not read the project lock. When a declaration
-is discoverable, it may use declared project defaults; otherwise the selected
-path or current directory is used directly as the source directory.
+Owner refinement, 2026-09-22: retire `project run-image`. Debuggers can use
+`devcapsule project [--path PATH] run --print-command` to inspect the normal
+prepared Docker invocation, with comments identifying temporary files, live
+helpers and environment dependencies. Stdout is shell text; preparation diagnostics
+use stderr. No editor integration or replay-resource lifetime is promised. Printing
+neither launches a project session nor records successful use. Arbitrary-image
+experiments remain Docker operations.
 
 ## Human And Agent Work Resume Together
 
@@ -1312,8 +1311,8 @@ from the transitional implementation.
 Available in the current dogfood path:
 
 - the `project [--path PATH]` subtree for `list`, `init`, named checkout
-  registration, `config resolve`, `state adopt`, `lock`, `run`, and
-  `run-image`, with no top-level compatibility aliases;
+  registration, `config resolve`, `state adopt`, `lock`, and `run` (including
+  diagnostic `--print-command`), with no top-level compatibility aliases;
 - XDG registry listing with `ready`, `missing`, and `uninitialized` status;
 - clean-checkout creation of the default developer record during the first
   `project config resolve`;
diff --git a/devcapsule-src/devcapsule/launch/command_output.py b/devcapsule-src/devcapsule/launch/command_output.py
new file mode 100644
index 0000000..04f3602
--- /dev/null
+++ b/devcapsule-src/devcapsule/launch/command_output.py
@@ -0,0 +1,37 @@
+"""Diagnostic rendering at a prepared launch boundary, not subprocess interception."""
+from __future__ import annotations
+
+from contextlib import contextmanager, redirect_stdout
+import os
+import shlex
+import sys
+from typing import Iterator, Sequence
+
+
+@contextmanager
+def preparation_diagnostics() -> Iterator[None]:
+    """Reserve stdout for the result of this foreground CLI operation.
+
+    redirect_stdout covers Python writers; descriptor redirection also covers
+    inherited output from image preparation's child processes. Restore both on
+    failure. This is scoped to project-run printing, never applied to normal run.
+    """
+    sys.stdout.flush()
+    sys.stderr.flush()
+    saved = os.dup(1)
+    try:
+        os.dup2(2, 1)
+        with redirect_stdout(sys.stderr):
+            yield
+    finally:
+        try:
+            sys.stderr.flush()
+        finally:
+            os.dup2(saved, 1)
+            os.close(saved)
+
+
+def render_command(command: Sequence[str], comments: Sequence[str]) -> str:
+    """Comments are separate shell lines, never embedded in a continuation."""
+    explanation = "".join("# " + line + "\n" for comment in comments for line in comment.splitlines())
+    return explanation + " \\\n  ".join(shlex.quote(arg) for arg in command) + "\n"
diff --git a/devcapsule-src/tests/test_command_output.py b/devcapsule-src/tests/test_command_output.py
new file mode 100644
index 0000000..8cb4773
--- /dev/null
+++ b/devcapsule-src/tests/test_command_output.py
@@ -0,0 +1,35 @@
+from __future__ import annotations
+
+import json
+import os
+import subprocess
+import sys
+
+import pytest
+
+from devcapsule.launch.command_output import preparation_diagnostics, render_command
+
+
+def test_shell_rendering_preserves_arguments_without_evaluating_them(tmp_path):
+    marker = tmp_path / 'must-not-exist'
+    values = ['', 'two words', "single'quote", 'line\nbreak', '# comment',
+              f'$(touch {marker})', f'`touch {marker}`', '; exit 9', 'trailing\\']
+    command = [sys.executable, '-c', 'import json,sys; print(json.dumps(sys.argv[1:]))', *values]
+    script = render_command(command, ['ordinary note', 'path\nnot a command'])
+    subprocess.run(['sh', '-n'], input=script, text=True, check=True)
+    output = subprocess.run(['sh'], input=script, text=True, capture_output=True, check=True)
+    assert json.loads(output.stdout) == values
+    assert not marker.exists()
+
+
+def test_preparation_output_including_children_uses_stderr_and_restores_on_failure(capfd):
+    with pytest.raises(ValueError):
+        with preparation_diagnostics():
+            print('python progress')
+            subprocess.run([sys.executable, '-c', "print('child progress')"], check=True)
+            os.write(1, b'fd progress\n')
+            raise ValueError('preparation failed')
+    print('subsequent stdout')
+    captured = capfd.readouterr()
+    assert captured.out == 'subsequent stdout\n'
+    assert all(message in captured.err for message in ('python progress', 'child progress', 'fd progress'))
```
