# Bug: Python-Owned PyCharm Image Build Emits Fragile Multiline `RUN` Shell Quoting

Date: 2026-07-16

Status: open

## Summary

The active Python-owned PyCharm image-build path now emits a generated
Dockerfile `RUN` line that embeds a multiline shell script as a single
shell-quoted argument list:

```text
RUN 'bash' '-euxo' 'pipefail' '-c' 'curl -fsSL https://deb.nodesource.com/setup_current.x | bash -
apt-get update
apt-get install -y --no-install-recommends nodejs
...
```

This fails during Docker build after the recent developer-tooling change that
bundles Node.js/npm plus Codex, Claude Code, and Gemini CLI in the PyCharm
image.

## Observed Failure

Reported build failure excerpt:

```text
Dockerfile:21
--------------------
  19 |     RUN 'sh' '-euxc' 'chmod +x /opt/pycharm/bin/pycharm.sh && ln -s /opt/pycharm/bin/pycharm.sh /usr/local/bin/pycharm && printf '"'"'%%ide-sudo ALL=(ALL) NOPASSWD:ALL\n'"'"' > /etc/sudoers.d/ide-sudo && chmod 0440 /etc/sudoers.d/ide-sudo && mkdir -p /ide-config /var/lib/docker /usr/local/share/docker4ide'
  20 |     RUN 'bash' '-euxo' 'pipefail' '-c' 'curl -fsSL https://deb.nodesource.com/setup_current.x | bash -
  21 | >>> apt-get update
  22 |     apt-get install -y --no-install-recommends nodejs
  23 |     npm install -g npm@latest
```

## Reproduction Evidence

Rendering the current PyCharm build spec produces:

```text
RUN 'bash' '-euxo' 'pipefail' '-c' 'curl -fsSL https://deb.nodesource.com/setup_current.x | bash -
apt-get update
apt-get install -y --no-install-recommends nodejs
npm install -g npm@latest
npm install -g @openai/codex
npm install -g --allow-scripts=@anthropic-ai/claude-code @anthropic-ai/claude-code@latest
npm install -g @google/gemini-cli
node --version
npm --version
codex --version
claude --version
gemini --version
npm cache clean --force
rm -rf /var/lib/apt/lists/*'
```

## Likely Cause

`render_build_context()` currently renders every `ExecStep` with shell-style
single-quoted argv tokens via `shell_join(step.args)`.

That approach is tolerable for one-line commands, but it becomes fragile when
an argument itself is a multiline shell script intended for `bash -c ...`.
The Dockerfile then contains a raw multiline single-quoted string inside a
shell-form `RUN`, which is much more error-prone and appears to break parsing
or execution in the real Docker build path.

## Suspect Files

- `devcapsule-src/devcapsule/image_build.py`
- `devcapsule-src/devcapsule/image_tooling.py`
- `devcapsule-src/devcapsule/configurations/pycharm/_image_build.py`

## Likely Fix Direction

One of these should be done:

1. teach `render_build_context()` to emit exec-form Docker `RUN` instructions
   for `ExecStep`, for example JSON-array style; or
2. keep shell-form `RUN`, but collapse multiline script bodies into a single
   safe one-line shell string joined with `&&` or `;`; or
3. introduce a dedicated build component for multiline shell scripts that
   writes a temporary script file into the build context and executes that file.

The first or third option is more robust than relying on shell-quoted multiline
strings.

## Verification Needed After Fix

1. Rendered Dockerfile no longer contains raw multiline single-quoted shell
   bodies in `RUN`.
2. `devcapsule pycharm build ...` succeeds on a real host Docker build.
3. The resulting image contains working `node`, `npm`, `codex`, `claude`, and
   `gemini` commands.
