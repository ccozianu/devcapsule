---
description: Using hosted models through your provider account, and running an open model locally with an agent that supports it.
weight: 4
updated: 2026-10-30
---
# Hosted and local models

Capsules have outbound internet access over Docker's `bridge` network by
default, so hosted frontier models work immediately after signing in—and you
can also point supported agents at an open-weight model running locally on your
computer's GPU or CPU.

## Hosted models through your vendor account

For hosted providers, authenticate inside the capsule once per checkout as
described in [Sign in and defaults](sign-in-and-defaults.md):

- **Subscription sign-in (recommended default):** run `claude`, `codex login`,
  or `antigravity` in the capsule terminal. Credentials stay in that agent's
  mode-`0700` persistent checkout slot rather than in container environment
  variables.
- **API keys or custom enterprise gateways:** bind declared secret inputs
  (`devcapsule project config bind codex/openai-api-key
  host-environment:OPENAI_API_KEY` or `antigravity-cli/gemini-api-key
  host-environment:GEMINI_API_KEY`) or set gateway variables per checkout with
  `devcapsule project config env set` (such as a corporate proxy or gateway
  base URL).

Select models using each CLI's native flag or config—for example, `codex -m
<model>`, `claude --model <model>`, or `/model` inside an interactive session.

## Running a local open model on your host

Running an inference server such as **Ollama**, **LM Studio**, **vLLM**, or
**llama.cpp** directly on your host machine keeps model weights and host GPU
drivers outside the container while letting coding agents inside the capsule
call its OpenAI-compatible HTTP API.

### Step 1: Make the host model server reachable from the capsule

Because a default `bridge` capsule has its own `localhost`, choose one of two
network paths depending on how your local server is bound:

1. **Keep the server bound to `127.0.0.1` and share host networking (`network
   host`):** if Ollama (`127.0.0.1:11434`) or LM Studio (`127.0.0.1:1234`)
   listens only on host loopback—the safest setting on laptops on shared
   Wi-Fi—grant `network host` for the session or checkout:

   ```bash
   devcapsule project run --authorize network host
   # or save for this checkout:
   devcapsule project config authorize network host
   ```

   Inside the capsule, the server is reachable at `http://127.0.0.1:11434`.

2. **Keep `bridge` isolation and route via `host.docker.internal`:** configure
   the host inference server to listen on your Docker bridge interface as well
   as `127.0.0.1`, pass `--add-host=host.docker.internal:host-gateway` (`project
   run -- --add-host=host.docker.internal:host-gateway` or `project config
   docker-args set`), and connect from the capsule to
   `http://host.docker.internal:11434`.

### Step 2: Connect OpenAI Codex to the local server

Ensure `codex-agent` is added to your checkout (`devcapsule project config add
codex-agent`), start your model server on the host (for example, `ollama serve`
and `ollama pull qwen2.5-coder:14b`), and verify connectivity from the capsule
terminal:

```bash
curl -fsS http://127.0.0.1:11434/api/tags
```

With `network host`, Codex's built-in open-source provider mode talks directly
to local Ollama or LM Studio without an OpenAI account:

```bash
codex --oss --local-provider ollama -m qwen2.5-coder:14b
# or for LM Studio on 127.0.0.1:1234:
codex --oss --local-provider lmstudio -m <loaded-model-id>
```

To use a `host.docker.internal` URL—or any other OpenAI-compatible server such
as `vllm` or `llama-server`—declare a custom provider in
`~/.codex/config.toml` inside the capsule (keeping top-level keys above the
first `[table]` header):

```toml
approval_policy = "never"
sandbox_mode = "danger-full-access"
model_provider = "local"
model = "qwen2.5-coder:14b"

[model_providers.local]
name = "Local OpenAI-compatible server"
base_url = "http://host.docker.internal:11434/v1"
```

Because `~/.codex/config.toml` lives in your checkout's persistent `codex/home`
slot, that provider definition survives container restarts and can be switched
per invocation with `codex -c model_provider="openai"` whenever you want to mix
local and hosted runs.
