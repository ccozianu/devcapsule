# User setup guide: PyCharm AI plugin and ChatGPT subscription

This guide records the PyCharm AI Assistant / Codex setup that was validated
for the original Dockerized PyCharm environment under `docker4pycharm/`.
Treat it as historical/reference user setup for that PyCharm MVP. Active
framework development now happens under `devcapsule-src/`, and current CLI
usage belongs in `devcapsule-src/README.md`.

## Recommended PyCharm plugin

Install the official JetBrains AI Assistant plugin and use Codex from inside JetBrains AI Chat.

Do **not** start with an arbitrary third-party plugin named “ChatGPT”, “GPT”, or similar. Several third-party plugins exist, but the current supported route for using OpenAI Codex from PyCharm is through JetBrains AI Assistant / JetBrains AI Chat.

As of the documentation checked on 2026-06-18:

- OpenAI documents Codex IDE support for JetBrains IDEs, including PyCharm.
- JetBrains documents Codex as integrated into JetBrains AI Chat starting with JetBrains IDE version 2025.3.
- The JetBrains/OpenAI path supports authentication using a ChatGPT account, an OpenAI API key, or a JetBrains AI subscription.
- ChatGPT Plus, Pro, Business, Edu, and Enterprise plans include Codex according to OpenAI’s Codex IDE documentation.

## Before installing

Use a recent PyCharm build. For Codex inside JetBrains AI Chat, prefer PyCharm 2025.3 or newer.

For this Docker project, that means the PyCharm `.tar.gz` or unpacked PyCharm directory supplied to `docker4pycharm/build-image.sh` should ideally be PyCharm 2025.3+.

Example rebuild:

```bash
cd docker4pycharm

./build-image.sh \
  --pycharm /path/to/pycharm-2025.3-or-newer.tar.gz \
  --image pycharm-isolated:latest
```

Then run PyCharm:

```bash
./run-pycharm-container.sh \
  --project /path/to/this/repository \
  --ssh-agent \
  --git-identity-from-host
```

## Git identity and GitHub access

For normal development, launch PyCharm with a Git author identity and one
explicit remote credential path.

To reuse only the host global Git identity values:

```bash
./run-pycharm-container.sh \
  --project /path/to/this/repository \
  --ssh-agent \
  --git-identity-from-host
```

To set identity explicitly:

```bash
./run-pycharm-container.sh \
  --project /path/to/this/repository \
  --ssh-agent \
  --git-user-name "Your Name" \
  --git-user-email you@example.com
```

For GitHub remotes, prefer SSH agent forwarding when your host agent already
has a suitable key:

```bash
ssh-add -l
./run-pycharm-container.sh \
  --project /path/to/this/repository \
  --ssh-agent \
  --git-identity-from-host
```

For HTTPS GitHub remotes, pass a token as a temporary secret:

```bash
export GITHUB_TOKEN=ghp_...
./run-pycharm-container.sh \
  --project /path/to/this/repository \
  --git-identity-from-host \
  --git-token-env GITHUB_TOKEN
```

Do not mount host `~/.ssh`, `~/.gitconfig`, or credential-manager directories
into the IDE container. The launcher passes only the requested identity values,
SSH agent socket, or token secret.

## Install JetBrains AI Assistant in PyCharm

Inside the Dockerized PyCharm window:

1. Open **Settings** / **Preferences**.
2. Go to **Plugins**.
3. Open the **Marketplace** tab.
4. Search for **AI Assistant**.
5. Install **JetBrains AI Assistant**.
6. Restart PyCharm if prompted.

Alternative: if the JetBrains AI widget or AI Chat tool window is visible in the IDE, click **Let’s Go** or **Install Plugin** and follow the prompts.

## Connect it to your ChatGPT subscription

After JetBrains AI Assistant is installed:

1. Open the **JetBrains AI** widget or **AI Chat** tool window.
2. Complete the first-run activation prompts and accept the applicable JetBrains/OpenAI terms if you agree with them.
3. In AI Chat, open the model/agent picker.
4. Choose **Codex**.
5. When authentication is requested, choose the **ChatGPT account** option.
6. Sign in with the same account that has your active ChatGPT subscription.
7. Return to PyCharm and confirm that Codex is available in the AI Chat agent picker.

Use your ChatGPT subscription path first. Use an OpenAI API key only if you intentionally want API-key billing or if the ChatGPT account login flow does not work reliably inside the Dockerized IDE.

## Container-specific login notes

Because PyCharm runs inside a container, the browser-based sign-in flow may need validation.

Expected possibilities:

- The plugin may open a login URL and allow normal browser sign-in.
- The plugin may offer a copy/paste login URL that you can open in the host browser.
- The localhost callback may fail if the browser opens on the host while the callback listener is inside the container.

If login fails, try these in order:

1. Look for a **copy link**, **manual sign-in**, or **device-code** style option in the plugin login window.
2. Retry from a freshly started PyCharm container.
3. Confirm the container has normal network access.
4. As a fallback, use an OpenAI API key authentication path or JetBrains AI subscription path if acceptable.
5. Record exactly what failed before changing the Docker launcher.

Do not broaden Docker access casually just to make login work. Any relaxation such as host networking, browser bridging, or extra mounts should become an explicit, documented launcher option.

## What to ask the future ChatGPT development agent to do

Once PyCharm is running and JetBrains AI Assistant/Codex is connected, open this repository in the Dockerized IDE and ask the development agent something like:

```text
Read README.md, CURRENT-STATUS.md, index.md, REQUIREMENTS.md, WORKFLOW.md, and devcapsule-src/README.md. Continue the DevCapsule project. Treat devcapsule-src as the active Python distribution project and docker4pycharm as the historical PyCharm reference baseline. Preserve the isolation model: only the selected project, IDE state, IDE plugins, X11 runtime resources, and narrowly scoped credential resources should be mounted. Work from the current task in CURRENT-STATUS.md.
```

## Links to re-check later

Plugin behavior and account/subscription rules can change. Before making major changes to the AI plugin integration, re-check:

- OpenAI Codex IDE extension documentation: https://developers.openai.com/codex/ide
- JetBrains Codex integration announcement: https://blog.jetbrains.com/ai/2026/01/codex-in-jetbrains-ides/
- JetBrains AI Assistant install guide: https://www.jetbrains.com/help/ai-assistant/installation-guide-ai-assistant.html
- JetBrains AI Assistant Marketplace page: https://plugins.jetbrains.com/plugin/22282-jetbrains-ai-assistant
