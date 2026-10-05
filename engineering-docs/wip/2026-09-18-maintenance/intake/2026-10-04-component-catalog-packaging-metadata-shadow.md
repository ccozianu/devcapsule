# Packaging acceptance reads editable metadata from the working directory

Sender: component-catalog, 2026-10-04. Recipient: maintenance.

While validating Eclipse, the release packaging gate failed its two synthetic
release cases: installed_version was 0.2.16.dev0 instead of 98.7.6 / 98.7.6rc0.
The actual PEX contains the correct release wheel. PEX_INTERPRETER -c retains
an empty sys.path entry, so importlib.metadata finds devcapsule-src/devcapsule.egg-info
from the parent working directory before the embedded wheel. Independently
reproduced after all smoke processes stopped. Logs are locally in
.git/eclipse-build2.log and .git/eclipse-packaging-recheck.log.

Suggested bounded test patch (no product code change), against a3d88e3:

```diff
--- a/devcapsule-src/tests/integration/test_pex_runtime.py
+++ b/devcapsule-src/tests/integration/test_pex_runtime.py
@@ -302,6 +302,7 @@
         installed_version = subprocess.check_output(
             [str(output), "-c", "from importlib.metadata import version; print(version('devcapsule'))"],
             env={**os.environ, "PEX_INTERPRETER": "1"}, text=True,
+            cwd=tmp_path,
         ).strip()
```

Accepting means isolate this installed-distribution check from checkout metadata
and rerun the three clean-revision packaging cases. No implementation change
was committed on the component-catalog branch for this unrelated gate defect.
