# Project Final Report

## Project
Python Docker Image Optimization – Reducing Docker Image Size Using Multi-Stage Builds

## Summary
The project packages a Flask notes API with PostgreSQL using two Docker builds: a deliberately less optimized full-Python baseline and a slim, multi-stage runtime image.

## Baseline build failure and fix
`requirements-dev.txt` includes `-r requirements.txt`. The baseline Dockerfile copied only `requirements-dev.txt`, so pip could not open `/app/requirements.txt`. `Dockerfile.baseline` now copies both requirement files before running pip. Its `COPY tests` instruction is absent, consistent with `tests/` being excluded from the Docker build context.

## Docker verification
Both commands completed successfully:

```powershell
docker build -f Dockerfile.baseline -t python-image-optimization:baseline .
docker build -f Dockerfile -t python-image-optimization:optimized .
```

The optimized Dockerfile uses a Python slim builder and runtime stage, carries only the runtime virtual environment and application/database source into the final stage, excludes development dependencies, and runs Gunicorn as the non-root `app` user.

### Local image measurements
The values below come from `docker image inspect ... --format='{{.Size}}'`. They are local image sizes in bytes representing the sum of uncompressed image layers. They are not compressed registry transfer sizes. Docker's `docker images` output also reported disk usage of 1.63GB (baseline) and 220MB (optimized) and content-size figures of 419MB and 53.4MB. Layer sharing/storage accounting can make disk-usage figures differ from the inspect total.

| Metric | Baseline | Optimized |
| --- | ---: | ---: |
| Base image | `python:3.12` | `python:3.12-slim` |
| Build approach | Single-stage | Multi-stage |
| Dependencies | Runtime + development | Runtime only |
| Runtime user | Root | Non-root `app` |
| Inspect size | 1,631,085,220 bytes / 1,631.09 MB / 1,555.52 MiB | 220,181,206 bytes / 220.18 MB / 209.98 MiB |

Saved: 1,410,904,014 bytes = 1,410.90 MB = 1,345.54 MiB
Reduction: `(1,631,085,220 - 220,181,206) / 1,631,085,220 * 100` = **86.50%**

## Runtime verification
Docker Compose reported the PostgreSQL service and optimized application as healthy. The baseline image was also run in the Compose network.

Both app containers were checked:

- `/health` returned status `ok`.
- `/ready` returned `ready` with database `connected`.
- Creating, listing, and deleting notes succeeded.
- Deleting a nonexistent note returned HTTP 404.
- Gunicorn startup logs were inspected.

The Compose stack used `postgres:16-alpine` and its named `postgres_data` volume. The volume was not removed.

## Python test status
The most recent previously recorded local pytest result was 5 passing tests. Docker build and endpoint validation were run during this verification. No Docker container pytest suite was executed.

## Files and configuration
- Flask app: `app/`
- PostgreSQL schema initialization: `db/init.sql`
- Tests: `tests/`
- Baseline image: `Dockerfile.baseline`
- Optimized multi-stage image: `Dockerfile`
- Compose: `docker-compose.yml`
- Build-context exclusions: `.dockerignore`
- Development environment example: `.env.example`

## Remaining work
- GitHub push/publication is not verified by this Docker run.
- No production credentials are supplied; change development-only `.env` values before any non-local use.
- Docker inspect sizes are machine- and image-version-specific and should be remeasured after base-image updates.
