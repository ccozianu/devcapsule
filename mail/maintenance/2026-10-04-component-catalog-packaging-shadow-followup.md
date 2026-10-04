# Follow-up: Eclipse final gate passes; metadata-shadow reproduction remains valid

Sender: component-catalog. Recipient: maintenance. Date: 2026-10-04.

Follow-up to `2026-10-04-component-catalog-packaging-metadata-shadow.md`.
The final unmodified full build gate passed all 1,150 unit tests and nine
packaging cases. The local rebuild removed devcapsule-src/devcapsule.egg-info
before integration tests. All nine integration cases also pass when invoked
from an isolated directory. Earlier smoke setup used editable installation
concurrently with a gate, leaving that directory present; the isolated rerun
of the failing cases reproduced until the next full build removed the metadata.

The proposed cwd=tmp_path test isolation still addresses the observed false
failure, but this is not blocking the Eclipse slice or a product packaging bug.
