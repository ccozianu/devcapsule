---
status: confirmed
severity: untriaged
target: none
owner: maintenance
opened: 2026-07-16
requirements: []
---

# Bug: Python-Owned PyCharm Image Build Emits Fragile Multiline `RUN` Shell Quoting

Date: 2026-07-16

Status note (pre-vocabulary, kept as evidence): open

## Release Disposition And Required Follow-Up — 2026-09-22

Owner decision: **deferred for 0.2.14 unless the defect recurs during the
release E2E campaign**. A recurrence reopens the release disposition for
investigation and repair. Successful base and derived image builds support
the current recipes; they do not establish that generic execution rendering
is correct. The bug remains open, with no fix version assigned.

Current renderer-only reproduction: applying
`ExecComponent(("sh", "-c", "echo first\necho second"))` preserves the arguments
in the plan but emits a shell-form `RUN` containing the literal newline.
The renderer therefore still allows script contents to cross Dockerfile
instruction boundaries. No new Docker build was run for this reproduction.
The current tooling recipes join commands on one line and avoid this trigger.

The follow-up is due a clean redesign of how images are composed from
components, including `image_build.py` and its collaborating modules, around
**documented, unit-testable contracts**. Document valid inputs, argument
preservation and explicit shell interpretation, composition and operation
ordering, contribution/export boundaries, and context ownership, cleanup and
failure behavior. Public contracts and relevant explanatory comments must
make those semantics explicit; dataclass fields and type annotations alone
do not do so. Establish focused contract tests before restructuring the code,
and retain real-build validation for the supported recipes.

This is broader than a quoting patch or a comment-only cleanup. The existing
recipe tests do not sufficiently protect those shared contracts; 45 relevant
image-build, base-image and materialization unit tests passed during review,
despite the rendering defect above. Defer the redesign to work after this
release to avoid expanding stabilization into an inadequately protected
refactor, subject to the E2E recurrence condition.

## Summary

At the original 2026-07-16 report, the Python-owned PyCharm image-build path emitted a generated
Dockerfile `RUN` line that embeds a multiline shell script as a single
shell-quoted argument list:

```text
RUN 'bash' '-euxo' 'pipefail' '-c' 'curl -fsSL https://deb.nodesource.com/setup_current.x | bash -
apt-get update
apt-get install -y --no-install-recommends nodejs
...
```

This failed during Docker build after the developer-tooling change that
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

Rendering the PyCharm build spec at the time of the original report produced:

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
- `devcapsule-src/devcapsule/launch/pycharm/_image_build.py`

## Historical Fix Suggestions

These original suggestions are retained as investigation history. The
contract-led redesign above supersedes them as the follow-up direction;
flattening arbitrary scripts with `&&` or `;` can change their semantics.

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

1. Document the composition and execution contracts and test their guarantees,
   including literal argument preservation for multiline and quoted inputs.
2. Verify the generated context and Dockerfile implement those contracts,
   with supported base and derived recipes succeeding in real Docker builds.
3. Validate tools appropriate to each selected recipe. The original Gemini
   installation above is historical evidence, not a current requirement;
   agent-neutral bases and explicitly selected agent components still apply.
