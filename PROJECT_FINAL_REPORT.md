# Project Final Report

**Verification date:** 2026-11-11

**Project:** Python Docker Image Optimization – Reducing Docker Image Size Using Multi-Stage Builds
**Workspace:** `C:\Users\vikas\Image Optimization\python-docker-image-optimization`

## Summary

The Flask notes API and PostgreSQL integration were retained and extended with a responsive Docker image optimization dashboard. Both Dockerfiles were rebuilt; the PowerShell comparison script generated a JSON report from current Docker inspect sizes. Dashboard, API, health, responsive layout, and PostgreSQL-backed behavior were verified. The named database volume was retained.

## Verification status

| Area | Status | Evidence |
|---|---|---|
| Docker engine | PASS | Docker Desktop Linux engine 29.9.2 responded to `docker info`. |
| Baseline build | PASS | `docker build -f Dockerfile.baseline -t python-image-optimization:baseline .` exited 0. |
| Optimized build | PASS | `docker build -f Dockerfile -t python-image-optimization:optimized .` exited 0. |
| Image size comparison | PASS | Current image tags inspected; `compare_images.ps1` calculated the results below. |
| Optimized image audit | PASS | `user=app`, UID 999, port 5000, Gunicorn command, health check, app/schema files present; pytest and gcc absent. |
| Compose/PostgreSQL | PASS | Both services showed healthy; `/ready` returned `ready` / `connected`. |
| Dashboard | PASS | Dashboard rendered from Flask; measurements loaded from the generated report; missing and malformed report states covered. |
| Browser checks | PASS | Playwright verified measured values, application/database status, section navigation, and a 390px viewport without horizontal overflow; zero page errors. |
| Report mount | PASS | Host report mounted at `/app/reports` read-only (`RW=false`); no Docker socket mount. |
| API | PASS | Health, readiness, create/list/delete, invalid payload (400), and missing note (404) verified. |
| Persistence | PASS | Unique note remained after restarting only the app service; test note was then deleted. |
| PostgreSQL volume | PASS | `python-docker-image-optimization_postgres_data` remained present; no volume deletion performed. |
| Python compilation | PASS | `python -m compileall app tests` exited 0. |
| Automated tests | PASS | Docker-based pytest run: 17 passed, 0 failed, exit code 0. |
| Windows host pytest DB connection | BLOCKED | Host connection to `localhost:5432` returned PostgreSQL authentication failure, including when using the active Compose app settings; this is not counted as a native Windows DB test pass. |
| GitHub Actions | PASS | Workflow run [#7](https://github.com/Amankumar6002/python-docker-image-optimization/actions/runs/43063834844) completed successfully for dashboard commit `1986f30c5d1760538ad389db9fd53c3817ef7a3c`. |
| GitHub publication | PASS | Dashboard implementation and docs are published to the public repository's `main` branch; the pushed commit and README are visible remotely. |

## Baseline build correction

`requirements-dev.txt` includes `-r requirements.txt`, but the baseline previously copied only `requirements-dev.txt`. Pip consequently could not find `/app/requirements.txt`. `Dockerfile.baseline` now copies both requirements files before installing the development set. The baseline does not copy `tests/`, because tests remain excluded from the Docker build context.

## Measured local image sizes

Measured after rebuilding both images using Docker image inspect size values (uncompressed local image layer totals):

| Metric | Baseline | Optimized |
|---|---:|---:|
| Base image | `python:3.12` | `python:3.12-slim` |
| Build strategy | Single-stage | Multi-stage |
| Dependencies | Runtime + development | Runtime only |
| Inspect size | 1,631,163,284 bytes (1,631.16 MB / 1,555.60 MiB) | 220,337,372 bytes (220.34 MB / 210.13 MiB) |
| Space saved | 1,410,825,912 bytes (1,410.83 MB / 1,345.47 MiB) | — |
| Reduction | 86.49% | — |

Formula: `(1,631,163,284 - 220,337,372) / 1,631,163,284 * 100` = **86.49%**.

These are not compressed registry sizes and should not be confused with `docker images` disk usage or content-size columns.

## Runtime and data verification

- Both current images were rebuilt successfully after adding the dashboard.
- `compare_images.ps1` produced `reports/image-comparison.json` from Docker inspect values; the dashboard reads it through a read-only Compose mount.
- `GET /` rendered the dashboard; `GET /api/optimization` returned the current measured sizes and calculations. Missing and malformed report cases returned explicit unavailable responses in tests.
- Browser verification confirmed the measured metric values, `/health` and `/ready` status cards, section navigation, and mobile layout.
- The Compose app and PostgreSQL containers were healthy.
- Both the optimized app and a separately run baseline container returned successful `/health` and `/ready` responses.
- Each container was tested for note creation, list visibility, and deletion.
- Invalid non-string note input returned HTTP 400; nonexistent note deletion returned HTTP 404.
- The final recorded API test passed `GET /health`, `GET /ready`, `GET /api/notes`, `POST /api/notes`, and `DELETE /api/notes/7`.
- Note ID 7 was created, retrieved, retained across an application-container restart, and then deleted. The final `GET /api/notes` response was `[]`.
- The named PostgreSQL volume was preserved.
- Docker-based pytest passed: 17 passed, 0 failed, exit code 0. `python -m compileall app tests` passed.

## Security and source handling

- No real API key, GitHub token, private key, or committed `.env` was found in the repository source scan.
- `.env`, `.venv`, Python caches, local database files, and tests are excluded from the Docker build context; local env and database files are ignored by Git.
- `.env.example` contains development placeholders only.
- Optimized runtime inspection confirmed non-root `app` execution and absence of pytest and gcc.
- The sample `change-me` value is development-only; configure a strong secret outside source control for non-local deployment.

## Remaining work

1. If native Windows PostgreSQL testing is required, configure a host-reachable database with matching authentication; otherwise use the verified Docker test command in the README.
2. Configure production secrets outside source control before deploying beyond local development.

The image sizes are specific to the Docker engine and base-image versions used here. Rebuild and rerun `compare_images.ps1` after changing those inputs.
