# AI Learning adopter gaps for sequencing

From: sample-projects
To: project-management
Date: 2026-10-22
Requirements: R-CONFIG-001, R-PRODUCT-002

The owner requested an independent TypeScript/Prisma/PostgreSQL sample, VSCodium,
Google/password authentication, and database scripts that never expose the
password in agent output. Bootstrap used the shipped /usr/local/bin/devcapsule0
0.3.0rc2 (e5b5a8b73309959f9407e115dcb3acd8707d6050), not a modified CLI.
`project init --required postgresql-client --local frontend-ide`, workflow
bootstrap and offline configuration checks succeeded. No capsule was launched,
no database credentials were read, and no remote was invented.

Please sequence these nonblocking capability questions, not bugs:

1. A Node/TypeScript adopter cannot express a Node SDK major in the current
   shared capability contract. docs/configuration/capabilities.md lists Python
   and .NET only; this sample relies on the pinned base's Node 22 plus its npm
   engines range. Decide whether Node is a first-class required SDK in 0.3.x.
2. Project-specific database and SMTP secrets lack the component-declared secret
   input path. configuration/bindings.py resolves component_secret_inputs only.
   The owner currently supplies environment variables in their own capsule
   terminal; sample TypeScript scripts read them directly, never construct
   secret-bearing shell arguments, and suppress raw failures. This is workflow
   discipline, not a separate OS-level barrier between agent and application.
   Decide whether project-owned secret declarations and safe execution/output
   contracts belong in the apparatus. No parent configuration was hand-edited
   to work around a missing command.

The existing service-dependency and network/port limitations were already
accepted for samples. They are not reopened here. SMTP provider and child remote
URL are owner inputs still pending, not DevCapsule defects. No product change
was made on sample-projects. An acknowledgement as backlog is sufficient; any
implementation belongs to the workstream selected by project-management/owner.
