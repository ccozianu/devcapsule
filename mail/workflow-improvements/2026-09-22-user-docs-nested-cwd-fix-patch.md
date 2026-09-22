# Patch: fix the nested-directory coordination data loss, keep claims across publish

From: user-docs (the pair working here found it while migrating)
To: workflow-improvements
Date: 2026-09-22

Answers maintenance's 2026-09-22 data-loss report in your mailbox. Prepared on
`ws-user-docs/first-session` and delivered as a patch under *A misplaced change
travels to its owner as a patch*, since the coordination tool is your
deliverable and this pair is selected on user-docs. Reverted from the sender's
checkout after delivery; nothing was committed on the wrong branch.

## What it fixes

1. **The data loss.** `_Git` ran every command with the supplied directory as
   cwd, and `_tree_entries` used `git ls-tree -r` without `--full-tree`, so a
   command run from a subdirectory listed only that subtree and rebuilt the
   coordination tree without everyone else's mail, state, and claims. Now
   `_Git` resolves the repository top level from any directory and runs there,
   and the listing is `--full-tree`. `publish` and `take` locate the
   workstream directory from that top level, so `--project ..` from a nested
   cwd works too.
2. **Claims dropped by publish.** `publish` replaced everything under
   `state/<name>/` with the status file and log, deleting a live claim. It now
   carries the claim through; `--retire` still removes all.
3. **Next step from a combined heading**, such as user-docs'
   *Last Task And Planned Next Step*, which `status` and `brief` showed as
   empty.

## Validation

Base revision: `25323a3b70ebd060e0b473601ba7f179c06a9f9a` (current `main`). Paths: the module and its tests.
Tests: three new regression tests, one reproducing the nested-directory loss
end to end against a bare remote (send, publish, claim, take from a nested
cwd, asserting every pre-existing entry survives), one for claim survival,
one for the heading; 47 passed with the CLI suite; syntax and typecheck pass.
Patch SHA-256: `ccf9fa40a4c5eb6c7d5f414b5539f51cb0236d4dbecbee1d473a69d54d5d2882`.

## Suggested handling

Apply on a branch of its own from `main`, not on `ws-workflow-improvements/v1`,
which the owner is holding until after the 0.2.14 cut: this is a data-loss fix
in a tool that is on `main` and in the release, and it should not wait behind
held rule text. Whether it enters 0.2.14 is `project-management`'s scoping.

```diff
diff --git a/devcapsule-src/devcapsule/workflow_coordination.py b/devcapsule-src/devcapsule/workflow_coordination.py
index 4a02e87..68950bf 100644
--- a/devcapsule-src/devcapsule/workflow_coordination.py
+++ b/devcapsule-src/devcapsule/workflow_coordination.py
@@ -82,10 +82,23 @@ class MailItem:
 
 
 class _Git:
-    """The few git invocations this module needs, run in one repository."""
+    """The few git invocations this module needs, run in one repository.
+
+    ``root`` may be any directory inside the checkout; every command runs at
+    the repository's top level, so a nested working directory never narrows
+    what git sees. That narrowing is what once made a send from a
+    subdirectory rebuild the coordination tree without everyone else's files.
+    """
 
     def __init__(self, root: Path) -> None:
-        self.root = root
+        completed = subprocess.run(
+            ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
+            capture_output=True,
+            text=True,
+        )
+        if completed.returncode != 0:
+            raise WorkflowMailError(f"{root} is not inside a git repository")
+        self.root = Path(completed.stdout.strip())
 
     def run(self, *args: str, stdin: str | None = None) -> str:
         completed = subprocess.run(
@@ -215,7 +228,7 @@ def take(
     items = _items_for(_tree_entries(git, tip), name)
     if not items:
         return []
-    intake = _intake_directory(root, name)
+    intake = _intake_directory(git.root, name)
     written: list[Path] = []
     for item in items:
         content = git.run("cat-file", "-p", item.blob)
@@ -374,7 +387,7 @@ def publish(
     git = _Git(root)
     wanted: dict[str, str] = {}
     if not retire:
-        directory = _workstream_directory(root, name)
+        directory = _workstream_directory(git.root, name)
         status = directory / STATE_FILES[0]
         if not status.is_file():
             raise WorkflowMailError(f"{status} does not exist; nothing to publish")
@@ -390,6 +403,11 @@ def publish(
         tip = _fetch_tip(git, remote, branch)
         entries = _tree_entries(git, tip) if tip else {README_PATH: _readme_blob(git)}
         current = {path: blob for path, blob in entries.items() if path.startswith(prefix)}
+        if not retire:
+            # A live claim is not a record; publishing must not drop it.
+            claim_path = prefix + CLAIM_FILE
+            if claim_path in current:
+                wanted = {**wanted, claim_path: current[claim_path]}
         if current == wanted:
             return None
         for path in current:
@@ -571,7 +589,7 @@ def _parse_status(name: str, text: str) -> WorkstreamState:
             heading = line[3:].strip()
             if heading == "Branch Association" and not branch:
                 branch = _first_paragraph(lines, index + 1)
-            elif heading in ("Planned Next Step", "Next Resumable Task") and not next_step:
+            elif ("Next Step" in heading or "Next Resumable Task" in heading) and not next_step:
                 next_step = _first_paragraph(lines, index + 1)
     return WorkstreamState(name, state, branch, next_step)
 
@@ -752,7 +770,7 @@ def _fetch_tip(git: _Git, remote: str, branch: str) -> str | None:
 def _tree_entries(git: _Git, commit: str) -> dict[str, str]:
     """Every blob in the commit's tree, as path -> blob sha."""
     entries: dict[str, str] = {}
-    for line in git.run("ls-tree", "-r", "-z", commit).split("\0"):
+    for line in git.run("ls-tree", "-r", "-z", "--full-tree", commit).split("\0"):
         if not line:
             continue
         meta, _, path = line.partition("\t")
diff --git a/devcapsule-src/tests/test_workflow_coordination.py b/devcapsule-src/tests/test_workflow_coordination.py
index 3ebf24b..490552b 100644
--- a/devcapsule-src/tests/test_workflow_coordination.py
+++ b/devcapsule-src/tests/test_workflow_coordination.py
@@ -390,3 +390,59 @@ def test_brief_prints_the_session_context(repos, capsys) -> None:
     assert "claim recorded for 12 h" in capsys.readouterr().out
     assert cli.main(["workflow", "claim", "--project", str(sender), "--release"]) == 0
     assert "claim released" in capsys.readouterr().out
+
+
+def test_publish_keeps_a_live_claim(repos) -> None:
+    _origin, sender, _recipient = repos
+    status_file(sender, "alpha", "active", "x")
+    publish(sender, "alpha")
+    claim(sender, "alpha", "still here")
+    status_file(sender, "alpha", "active", "y")  # something changed, so publish commits
+
+    publish(sender, "alpha")
+
+    row = list_state(sender)[0]
+    assert row.claim is not None and row.claim.slice == "still here"
+
+
+def test_commands_from_a_nested_directory_preserve_everyone_else(repos) -> None:
+    """Regression for the 2026-09-22 coordination data loss: a send run from a
+    subdirectory rebuilt the tree from a cwd-limited listing and dropped every
+    other mailbox, state, and claim."""
+    origin, sender, recipient = repos
+    status_file(sender, "alpha", "active", "x")
+    status_file(recipient, "beta", "active", "y")
+    publish(sender, "alpha")
+    publish(recipient, "beta")
+    claim(recipient, "beta", "reviewing")
+    send(recipient, "alpha", item(recipient, "2026-09-22-beta-first.md"))
+    before = set(git(origin, "ls-tree", "-r", "--name-only", "coordination").split())
+    assert len(before) == 5
+
+    nested = sender / "devcapsule-src" / "deeper"
+    nested.mkdir(parents=True)
+    send(nested, "beta", item(sender, "2026-09-22-alpha-nested.md"))
+    status_file(sender, "alpha", "active", "changed from nested")
+    publish(nested, "alpha")
+    claim(nested, "alpha", "from nested")
+
+    after = set(git(origin, "ls-tree", "-r", "--name-only", "coordination").split())
+    assert before <= after
+    assert "mail/beta/2026-09-22-alpha-nested.md" in after
+    assert list_state(nested)[0].state == "active"
+    assert check(nested, "alpha")[0].name == "2026-09-22-beta-first.md"
+    # Taking from a nested directory still writes into the repository's intake.
+    taken = take(nested, "alpha")
+    assert taken == [sender / "engineering-docs/wip/2026-09-19-alpha/intake/2026-09-22-beta-first.md"]
+
+
+def test_next_step_is_read_from_a_combined_heading(repos) -> None:
+    _origin, sender, _recipient = repos
+    path = sender / "engineering-docs/wip/2026-09-19-alpha/CURRENT-STATUS.md"
+    path.write_text(
+        "# S\n\nState: active\n\nBranch association: `ws-alpha/v1`\n\n"
+        "## Last Task And Planned Next Step\n\nDo the thing.\n",
+        encoding="utf-8",
+    )
+    publish(sender, "alpha")
+    assert list_state(sender)[0].next_step == "Do the thing."
```
