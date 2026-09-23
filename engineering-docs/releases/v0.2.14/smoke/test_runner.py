"""Runner failure/recording checks. These do not claim real IDE acceptance."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

SPEC = importlib.util.spec_from_file_location("rc0_runner", Path(__file__).with_name("runner.py"))
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


class ImmediateObserver:
    """Deterministic scheduling for recording tests; no clock-speed assumptions."""
    def __init__(self, *, target, daemon):
        self.target = target

    def start(self):
        self.target()

    def join(self, timeout):
        pass

    def is_alive(self):
        return False


class RunnerTests(unittest.TestCase):
    def exercise_session(self, directory, *, code=0, final_error=False):
        record = {"schema": 1, "candidate_sha256": runner.RC0_SHA, "pex": "/test/rc0.pex",
                  "project": "/test/project", "host_home": str(Path.home()), "environment": {},
                  "container_name": "test-owned", "sessions": [], "observations": []}
        process = Mock()
        process.wait.return_value = code
        ids = ["", "container-id", RuntimeError("daemon unavailable") if final_error else ""]
        with patch.object(runner, "verify_pex"), patch.object(runner, "capture", return_value="daemon-id"), \
             patch.object(runner, "project_facts", return_value={"revision": "source-id"}), \
             patch.object(runner, "container_id", side_effect=ids), \
             patch.object(runner, "inspect_container", return_value={"running": True, "id": "container-id"}), \
             patch.object(runner.threading, "Thread", ImmediateObserver), \
             patch.object(runner.subprocess, "Popen", return_value=process):
            result = runner.session(directory, record)
        saved = json.loads((directory / "run.json").read_text())
        return result, saved

    def test_successful_process_does_not_invent_a_visual_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, record = self.exercise_session(Path(tmp))
        self.assertEqual(code, 0)
        self.assertEqual(record["sessions"][0]["status"], "PROCESS_CHECKS_PASSED")
        self.assertEqual(record["observations"], [])

    def test_daemon_failure_is_not_container_absence(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, record = self.exercise_session(Path(tmp), final_error=True)
        self.assertEqual(code, 1)
        self.assertIsNone(record["sessions"][0]["container_absent_after_exit"])
        self.assertEqual(record["sessions"][0]["status"], "NEEDS_REVIEW")

    def test_launcher_failure_is_persisted(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, record = self.exercise_session(Path(tmp), code=17)
        self.assertEqual(code, 1)
        self.assertEqual(record["sessions"][0]["launcher_exit"], 17)
        self.assertNotEqual(record["sessions"][0]["status"], "RUNNING")

    def test_concurrent_writer_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            with runner.locked(Path(tmp)):
                with self.assertRaisesRegex(ValueError, "active runner"):
                    with runner.locked(Path(tmp)):
                        self.fail("Acquired an already held lock")

    def test_resume_keeps_selected_configuration_and_removes_runtime_override(self):
        with patch.dict(runner.os.environ, {"XDG_CONFIG_HOME": "/wrong", "DEVCAPSULE_RUNTIME_PEX": "/wrong"}):
            env = runner.environment({"environment": {"XDG_CONFIG_HOME": "/original"}})
        self.assertEqual(env["XDG_CONFIG_HOME"], "/original")
        self.assertNotIn("DEVCAPSULE_RUNTIME_PEX", env)

    def test_wrong_executable_is_not_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            pex = Path(tmp) / "fake.pex"
            pex.write_bytes(b"not RC0")
            with self.assertRaisesRegex(ValueError, "not the published RC0"):
                runner.verify_pex(pex)

    def test_resume_refuses_changed_docker_daemon_before_launch(self):
        record = {"pex": "/test/rc0", "project": "/test/project", "host_home": str(Path.home()),
                  "environment": {}, "docker_daemon": "old"}
        with tempfile.TemporaryDirectory() as tmp, patch.object(runner, "verify_pex"), \
             patch.object(runner, "capture", return_value="new"), patch.object(runner.subprocess, "Popen") as launch:
            with self.assertRaisesRegex(ValueError, "Docker daemon changed"):
                runner.session(Path(tmp), record)
            launch.assert_not_called()


if __name__ == "__main__":
    unittest.main()
