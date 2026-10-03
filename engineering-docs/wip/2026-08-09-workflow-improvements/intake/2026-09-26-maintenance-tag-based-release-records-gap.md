# Definition gap: where a tag-based maintenance release keeps its workstream records

Sent: 2026-09-26
From: `maintenance`, exercising judgment where the definition is silent.

*Taking A Release Over* rule 2 says the status file is edited on the release
branch and published from there, which works when the release is cut from
`main`, where the working branch's records already are. A maintenance release
cut from the prior final tag, the path *Releases* and the runbook both allow,
starts from a tree whose registry and status file are a release old; editing
or publishing them from the release branch would regress the live state.

For 0.2.15 maintenance kept its records on `ws-maintenance/post-0.2.14`,
published from there, and let the release branch carry only source, version
and release documents, with the row naming the release branch as required.
Recorded in maintenance's status file under *Release 0.2.15*. Please settle
the rule for tag-based cuts in the definition; the choice above is one option.
