# Project Final Report

**Verification date:** 2026-11-11

**Project:** Python Docker Image Optimization – Reducing Docker Image Size Using Multi-Stage Builds
**Workspace:** `C:\Users\vikas\Image Optimization\python-docker-image-optimization`

## Summary

The Flask notes API and PostgreSQL integration were retained. The baseline image build error was fixed, both images were rebuilt from current source, the services and API were exercised against PostgreSQL, the app-only restart persistence check passed, and a reusable PowerShell image comparison script was added.

## Verification status

| Area | Status | Evidence |
|---|---|---|
| Docker engine | PASS | Docker Desktop Linux engine 29.9.2 responded to `docker info`. |
| Baseline build | PASS | `docker build -f Dockerfile.baseline -t python-image-optimization:baseline .` exited 0. |
| Optimized build | PASS | `docker build -f Dockerfile -t python-image-optimization:optimized .` exited 0. |
| Image size comparison | PASS | Current image tags inspected; `compare_images.ps1` calculated the results below. |
| Optimized image audit | PASS | `user=app`, UID 999, port 5000, Gunicorn command, health check, app/schema files present; pytest and gcc absent. |
| Compose/PostgreSQL | PASS | Both services showed healthy; `/ready` returned `ready` / `connected`. |
| API | PASS | Health, readiness, create/list/delete, invalid payload (400), and missing note (404) verified. |
| Persistence | PASS | Unique note remained after restarting only the app service; test note was then deleted. |
| PostgreSQL volume | PASS | `python-docker-image-optimization_postgres_data` remained present; no volume deletion performed. |
| Python compilation | PASS | `python -m compileall app tests` exited 0. |
| Automated tests | PASS | Docker-based pytest run: 13 passed, 0 failed, exit code 0. |
| Windows host pytest DB connection | BLOCKED | Direct host connection to `localhost:5432` returned PostgreSQL authentication failure for `appuser`; this is not counted as a native Windows DB test pass. |
| GitHub Actions | PASS | Runs #3 and #4 completed successfully. Run #3 included PostgreSQL service initialization and pytest for commit `00b227b789b65822bad2f5be11e12162e8f16898`; run #4 passed for commit `6230af8b4409d7f20e14beb61303b638e857dd6c`. |
| GitHub publication | PASS | Commit `6230af8b4409d7f20e14beb61303b638e857dd6c` was pushed to `main`; remote head matched and GitHub showed the expected project files. |

## Baseline build correction

`requirements-dev.txt` includes `-r requirements.txt`, but the baseline previously copied only `requirements-dev.txt`. Pip consequently could not find `/app/requirements.txt`. `Dockerfile.baseline` now copies both requirements files before installing the development set. The baseline does not copy `tests/`, because tests remain excluded from the Docker build context.

## Measured local image sizes

Measured after rebuilding both images using Docker image inspect size values (uncompressed local image layer totals):

| Metric | Baseline | Optimized |
|---|---:|---:|
| Base image | `python:3.12` | `python:3.12-slim` |
| Build strategy | Single-stage | Multi-stage |
| Dependencies | Runtime + development | Runtime only |
| Inspect size | 1,631,085,307 bytes (1,631.09 MB / 1,555.52 MiB) | 220,181,371 bytes (220.18 MB / 209.98 MiB) |
| Space saved | 1,410,903,936 bytes (1,410.90 MB / 1,345.54 MiB) | — |
| Reduction | 86.50% | — |

Formula: `(1,631,085,307 - 220,181,371) / 1,631,085,307 * 100` = **86.50%**.

These are not compressed registry sizes and should not be confused with `docker images` disk usage or content-size columns.

## Runtime and data verification

- Both current images were built successfully.
- The Compose app and PostgreSQL containers were healthy.
- Both the optimized app and a separately run baseline container returned successful `/health` and `/ready` responses.
- Each container was tested for note creation, list visibility, and deletion.
- Invalid non-string note input returned HTTP 400; nonexistent note deletion returned HTTP 404.
- The final recorded API test passed `GET /health`, `GET /ready`, `GET /api/notes`, `POST /api/notes`, and `DELETE /api/notes/7`.
- Note ID 7 was created, retrieved, retained across an application-container restart, and then deleted. The final `GET /api/notes` response was `[]`.
- The named PostgreSQL volume was preserved.

## Security and source handling

- No real API key, GitHub token, private key, or committed `.env` was found in the repository source scan.
- `.env`, `.venv`, Python caches, local database files, and tests are excluded from the Docker build context; local env and database files are ignored by Git.
- `.env.example` contains development placeholders only.
- Optimized runtime inspection confirmed non-root `app` execution and absence of pytest and gcc.
- The sample `change-me` value is development-only; configure a strong secret outside source control for non-local deployment.

## Remaining work

1. If running pytest natively on Windows, set `DB_*` environment values that match the reachable PostgreSQL instance; alternatively use the Docker test command in the README.
2. Configure production secrets outside source control before deploying beyond local development.

The image sizes are specific to the Docker engine and base-image versions used here. Rebuild and rerun `compare_images.ps1` after changing those inputs.
