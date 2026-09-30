# Security assets

This directory collects security-focused source files, configuration, and manifests that were previously scattered across the repository.

- `java/`, `javascript/`, and `python/` contain authentication, authorization, key-handling, and verification code.
- `config/` contains database and service-hardening configuration.
- `manifests/` contains access-control and transaction whitelist data.
- `scripts/` contains security verification and credential-dependent integration scripts.

Deployment workflows and mixed-purpose application or server configuration remain in their original locations.

Credential-bearing scripts read values from environment variables. `config/Gemini-connection.json` uses `${GEMINI_AUTHORIZATION}` as a placeholder that the consuming client must expand; do not commit live credentials.
