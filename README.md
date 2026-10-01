# Trust-Main

The repository is organized into two modules:

- [`trust/`](trust/) contains Trust and legacy Trust applications, administration,
  shared platform assets, and its documentation.
- [`firstresponders/`](firstresponders/) contains first-responder, dispatch,
  forensic, police, fire, and scene-preservation assets.

The original directory structure is preserved inside each module. GitHub
workflows remain under `.github/workflows/` so GitHub Actions can discover and
run them; their commands reference the module paths. The shared agency schema
remains at [`asset/SQL/agencies/joint.sql`](asset/SQL/agencies/joint.sql).

Build the Trust container from the repository root with
`docker build -f trust/Dockerfile .`; start the compose stack with
`docker compose -f trust/docker-compose.yml up`.
