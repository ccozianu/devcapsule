# Update the configuration-format names in the maintenance review

From: component-catalog
To: maintenance
Base revision: `6ce748d16ce684f619a697ff06581f1f540bb4e0`
Affected path: `engineering-docs/wip/2026-09-18-maintenance/configuration-correctness.md`

The owner asked for plain-English names and documentation. This branch renames
`configuration/documents.py` to `file_formats.py`, `Artifact` to
`ConfigurationFileKind`, `admit_document` to `validate_file_format`, and
`render_document` to `render_toml`. Behavior is unchanged. The source change is
on `ws-component-catalog/intellij-idea`; its checkpoint is being validated.

The IDE rename also changed a row in your review. That incidental edit was
reverted here because the report belongs to maintenance. Please decide whether
to apply the following updated link/names to the report as the code integrates,
or retain the report as a historical snapshot with an explicit source revision.
Accepting this item means maintaining that reference in your own workstream.
The sender has checked the new symbols and imports; the receiver should check
that this patch fits the intended date/scope of its report.

```diff
--- a/engineering-docs/wip/2026-09-18-maintenance/configuration-correctness.md
+++ b/engineering-docs/wip/2026-09-18-maintenance/configuration-correctness.md
@@ -21,7 +21,7 @@
 | Responsibility | Implementation |
 |---|---|
 | Public value API | [`configuration/__init__.py`](../../../devcapsule-src/devcapsule/configuration/__init__.py), [`model.py`](../../../devcapsule-src/devcapsule/configuration/model.py), [`resolution.py`](../../../devcapsule-src/devcapsule/configuration/resolution.py): `Configuration`, `Resolution` |
-| Artifact admission and complete serialization | [`documents.py`](../../../devcapsule-src/devcapsule/configuration/documents.py): `Artifact`, `admit_document`, `table`, codecs |
+| Configuration format checks and TOML output | [`file_formats.py`](../../../devcapsule-src/devcapsule/configuration/file_formats.py): `ConfigurationFileKind`, `validate_file_format`, `table`, `render_toml` |
 | Ordinary domains, resource bindings and authorization | [`values.py`](../../../devcapsule-src/devcapsule/configuration/values.py), [`bindings.py`](../../../devcapsule-src/devcapsule/configuration/bindings.py), [`authorization.py`](../../../devcapsule-src/devcapsule/configuration/authorization.py) |
 | A unique name and runtime effect per node | [`nodes.py`](../../../devcapsule-src/devcapsule/configuration/nodes.py): `NodeRegistry`, `build_node_registry` |
 | Complete assessment and host decisions | [`review.py`](../../../devcapsule-src/devcapsule/configuration/review.py): `ConfigurationReview`, `HostAccess` |
```
