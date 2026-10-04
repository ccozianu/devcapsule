"""Provider adapters for the same visual action/recognition protocol.

CLIs receive images and return a constrained decision. They have no browser
or filesystem write tool: only the harness applies actions through Playwright.
Thus the IDE's saved file remains an independent witness of the interaction.
"""
from __future__ import annotations

import base64
from dataclasses import dataclass
import json
import os
from pathlib import Path
import signal
import shutil
import subprocess
from functools import cache
from typing import Any, Protocol


DEFAULT_MODELS = {"codex": "gpt-6-astra", "claude": "claude-fable-5-1"}
ACTIONS = ("click", "double_click", "type", "press", "wait", "done", "fail")
DECISION_SCHEMA: dict[str, Any] = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "action": {"type": "string", "enum": list(ACTIONS)},
        "x": {"type": "integer", "minimum": 0, "maximum": 1599},
        "y": {"type": "integer", "minimum": 0, "maximum": 999},
        "text": {"type": "string"},
        "seconds": {"type": "integer", "minimum": 0, "maximum": 10},
        "reason": {"type": "string"},
    },
    "required": ["action", "x", "y", "text", "seconds", "reason"],
}


class DriverError(RuntimeError):
    """Missing provider access, invalid response or an exhausted invocation."""


@cache
def cli_identity(provider: str) -> dict[str, str | None]:
    executable = shutil.which(provider)
    version = subprocess.run([provider, "--version"], capture_output=True, text=True,
                             timeout=15, check=True).stdout.strip()
    return {"executable": executable, "version": version}


@dataclass(frozen=True)
class Decision:
    action: str
    x: int
    y: int
    text: str
    seconds: int
    reason: str

    @classmethod
    def parse(cls, value: object) -> Decision:
        if not isinstance(value, dict) or set(value) != set(DECISION_SCHEMA["required"]):
            raise DriverError("AI response does not match the decision contract")
        if value["action"] not in ACTIONS:
            raise DriverError("Unknown browser action")
        for field, upper in (("x", 1599), ("y", 999), ("seconds", 10)):
            if type(value[field]) is not int or not 0 <= value[field] <= upper:
                raise DriverError(f"Invalid action field {field}")
        if not all(isinstance(value[k], str) and len(value[k]) <= 4000 for k in ("text", "reason")):
            raise DriverError("Invalid action text")
        return cls(**value)


class VisualDriver(Protocol):
    def decide(self, prompt: str, images: tuple[Path, ...], evidence: Path, timeout: float) -> Decision: ...


@dataclass(frozen=True)
class CliDriver:
    provider: str = "codex"
    model: str = "gpt-6-astra"

    @classmethod
    def select(cls, provider: str, model: str | None = None) -> CliDriver:
        if provider not in DEFAULT_MODELS:
            raise DriverError(f"Unsupported AI provider: {provider}")
        return cls(provider, model or DEFAULT_MODELS[provider])

    def invocation(self, prompt: str, images: tuple[Path, ...], evidence: Path) -> tuple[list[str], str]:
        if self.provider == "codex":
            schema = evidence / "schema.json"
            schema.write_text(json.dumps(DECISION_SCHEMA), encoding="utf-8")
            return ([
                "codex", "exec", "--ignore-user-config", "--ignore-rules",
                "--disable", "shell_tool", "--disable", "hooks",
                "--skip-git-repo-check", "--ephemeral", "--sandbox", "read-only",
                "--model", self.model, "-c", 'model_reasoning_effort="medium"',
                "--json", "--output-schema", str(schema),
                "--output-last-message", str(evidence / "decision.json"),
                *[arg for path in images for arg in ("--image", str(path))], "-",
            ], prompt)
        content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
        for path in images:
            content.append({"type": "image", "source": {
                "type": "base64", "media_type": "image/png",
                "data": base64.b64encode(path.read_bytes()).decode("ascii"),
            }})
        return ([
            "claude", "--print", "--safe-mode", "--model", self.model,
            "--tools", "", "--no-session-persistence", "--input-format", "stream-json",
            "--output-format", "stream-json", "--verbose",
            "--json-schema", json.dumps(DECISION_SCHEMA),
        ], json.dumps({"type": "user", "message": {"role": "user", "content": content}}) + "\n")

    def decide(self, prompt: str, images: tuple[Path, ...], evidence: Path, timeout: float) -> Decision:
        evidence = evidence.resolve()
        evidence.mkdir(parents=True, exist_ok=False)
        argv, payload = self.invocation(prompt, images, evidence)
        (evidence / "prompt.txt").write_text(prompt, encoding="utf-8")
        metadata: dict[str, Any] = {"provider": self.provider, "requested_model": self.model,
                                    "reported_models": [], "timeout_seconds": timeout}
        process: subprocess.Popen[str] | None = None
        try:
            metadata["tool"] = cli_identity(self.provider)
            process = subprocess.Popen(argv, cwd=evidence, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, text=True, start_new_session=True)
            try:
                stdout, stderr = process.communicate(payload, timeout=timeout)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                stdout, stderr = process.communicate()
                (evidence / "events.jsonl").write_text(stdout, encoding="utf-8")
                (evidence / "stderr.txt").write_text(stderr, encoding="utf-8")
                raise DriverError(f"{self.provider}/{self.model} exceeded its time limit") from None
            (evidence / "events.jsonl").write_text(stdout, encoding="utf-8")
            (evidence / "stderr.txt").write_text(stderr, encoding="utf-8")
            metadata["exit_code"] = process.returncode
            if process.returncode:
                raise DriverError(f"{self.provider}/{self.model} exited {process.returncode}; see {evidence}")
            events = [json.loads(line) for line in stdout.splitlines() if line.strip()]
            if self.provider == "codex":
                metadata["usage"] = [event["usage"] for event in events if event.get("type") == "turn.completed"]
                # Codex exec JSONL currently omits model identity. Keep the explicit
                # CLI selection as evidence; never invent a server-reported model.
                value = json.loads((evidence / "decision.json").read_text(encoding="utf-8"))
            else:
                result: dict[str, Any] = next((event for event in reversed(events) if event.get("type") == "result"), {})
                usage = result.get("modelUsage", {})
                metadata["reported_models"] = list(usage)
                metadata["usage"] = usage
                if result.get("is_error") or self.model not in usage:
                    raise DriverError(f"Claude did not report a successful run with {self.model}")
                value = result.get("structured_output")
                (evidence / "decision.json").write_text(json.dumps(value), encoding="utf-8")
            return Decision.parse(value)
        except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
            raise DriverError(f"Invalid or unavailable {self.provider} driver: {exc}") from exc
        finally:
            (evidence / "invocation.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
