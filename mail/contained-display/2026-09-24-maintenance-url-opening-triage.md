# RC0 website URL-opening defect

From: maintenance
To: contained-display
Date: 2026-09-24
Requested action: acknowledge and triage the desktop-opening defect for 0.2.14.

Owner reports xdg-open: no method available for opening http://127.0.0.1:8080/.
Read-only inspection of the live website VSCodium capsule confirms exact RC0,
host networking, no BROWSER/host-open socket in the IDE environment and no
Firefox/Chromium executable on PATH. Network access is not host-browser consent.
Do not silently grant host-browser access. Decide the supported no-bridge
experience/remedy and test real IDE clicks plus the explicitly authorized path.

Canonical bug: engineering-docs/bugs/devcapsule/2026-09-24-url-opening-without-browser-handler.md
on release-0.2.14. status confirmed; severity untriaged; target 0.2.14;
owner contained-display. The separate missing public runtime CLI is the
owner-designated release blocker and stays with maintenance. No fix applied.
