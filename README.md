# Image Optimization (Python) – Reducing Docker Image Size Using Multi-Stage Builds

## Overview

This project demonstrates how to reduce a Python Docker image from a large, bloated baseline to a much smaller, production-ready optimized image using a slim base image, a multi-stage build, and careful dependency management.

## Problem statement

A Python Flask backend with PostgreSQL was originally packaged using a large Docker image and included development dependencies. The goal is to shrink the image size while preserving the same application behavior and PostgreSQL connectivity.

## Technologies used

- Python 3.12
- Flask
- PostgreSQL
- Docker
- Docker Compose
- pytest
- Gunicorn

## Architecture

The application exposes a small REST API and checks database readiness before serving requests. It runs in a container and connects to a PostgreSQL container over the Docker Compose network.

## Folder structure

```text
python-docker-image-optimization/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   └── routes.py
├── db/
│   └── init.sql
├── tests/
│   └── test_app.py
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── Dockerfile.baseline
├── docker-compose.yml
├── README.md
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
└── .github/workflows/tests.yml
```

## Build and run

### Windows PowerShell

```powershell
cd "C:\Users\vikas\Image Optimization\python-docker-image-optimization"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

### Run the application locally without Docker

This project is built for Linux containers, so the containerized production server uses Gunicorn. For a quick local Windows check, start the Flask app package directly:

```powershell
python -m app
```

The app will start on `http://127.0.0.1:5000`.

### Run the database and application with Docker Compose

```powershell
docker compose up --build -d
```

> Docker Desktop must be running before `docker compose` commands work. If the Docker daemon is unavailable, the commands cannot be executed in this environment.

### Check the API

```powershell
Invoke-RestMethod -Uri http://localhost:5000/health
Invoke-RestMethod -Uri http://localhost:5000/ready
```

## API endpoints

- `GET /health` – returns application health info
- `GET /ready` – checks PostgreSQL connectivity
- `GET /api/notes` – fetches all notes
- `POST /api/notes` – creates a note
- `DELETE /api/notes/<id>` – deletes a note

## Testing

```powershell
pytest -q
```

## Docker image comparison

The project includes both a baseline image and an optimized multi-stage image. Build both images and compare their sizes.

```powershell
docker build -f Dockerfile.baseline -t python-image-optimization:baseline .
docker build -f Dockerfile -t python-image-optimization:optimized .
docker images
docker image inspect python-image-optimization:baseline --format='{{.Size}}'
docker image inspect python-image-optimization:optimized --format='{{.Size}}'
```

The baseline build originally failed because `requirements-dev.txt` includes `-r requirements.txt`, but `Dockerfile.baseline` copied only `requirements-dev.txt` into the build image. The include therefore pointed to a missing `/app/requirements.txt`. The fix copies both requirements files before installing the development set. The `tests/` copy instruction is absent, so the baseline does not try to copy a directory excluded by `.dockerignore`.

Both images were built locally and measured with `docker image inspect ... --format='{{.Size}}'`. These are Docker's local uncompressed image-size totals in bytes, not compressed registry transfer sizes. `docker images` additionally reported local disk usage of 1.63GB for baseline and 220MB for optimized, and content-size figures of 419MB and 53.4MB respectively. Docker local disk usage can differ due to layer sharing and storage accounting; use the inspect values consistently for this comparison.

| Metric | Baseline image | Optimized image |
| --- | ---: | ---: |
| Base image | `python:3.12` | `python:3.12-slim` |
| Build strategy | Single-stage | Multi-stage |
| Dependencies | Runtime + development | Runtime only |
| Runtime user | Root (baseline comparison) | Non-root `app` |
| Docker inspect size | 1,631,085,220 bytes (1,631.09 MB / 1,555.52 MiB) | 220,181,206 bytes (220.18 MB / 209.98 MiB) |
| Space saved | 1,410,904,014 bytes (1,410.90 MB / 1,345.54 MiB) | — |
| Reduction | 86.50% | — |

Calculation:

```text
(1,631,085,220 - 220,181,206) / 1,631,085,220 * 100 = 86.50%
```

Verification commands:

```powershell
docker image inspect python-image-optimization:baseline --format='{{.Size}}'
docker image inspect python-image-optimization:optimized --format='{{.Size}}'
docker images python-image-optimization
```

The `.dockerignore` file reduces the build context by excluding Git data, virtual environments, caches, tests, secrets files and local database files. It reduces final image size only when an excluded file would otherwise be copied into an image layer. `requirements.txt`, `requirements-dev.txt`, `app/`, and `db/` remain available to Docker.

## Notes on Docker optimization

Runtime verification used the Docker Compose PostgreSQL service. Both baseline and optimized containers returned success for `/health` and `/ready`; each also created, listed, and deleted a note. Deleting a nonexistent note returned HTTP 404. Compose reported both the PostgreSQL service and optimized app as healthy.

The optimized container runs Gunicorn as the non-root `app` user. On Windows, run `python -m app` for a local development server; Gunicorn is intended for the Linux container.

## Conclusion

Using a slim Python base image, multi-stage build, and runtime-only dependencies reduced the measured local image size by 86.50% while preserving the tested API and database behavior.
