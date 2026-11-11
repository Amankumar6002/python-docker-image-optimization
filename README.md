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
└── .venv/
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

Important: this environment does not currently have a live Docker daemon, so the actual image-size values were not measurable here. Run the commands above on a machine with Docker Desktop or a Linux Docker engine running, then replace the placeholders below with the actual values.

| Metric | Original image | Optimized image |
| --- | ---: | ---: |
| Base image | Full Python | Python slim |
| Dockerfile | Single-stage | Multi-stage |
| Dependencies | Runtime + development | Runtime only |
| Build tools | Kept in final image | Excluded from final image |
| Measured image size | `<baseline size>` | `<optimized size>` |
| Space saved | `<original - optimized>` | — |
| Percentage reduction | `<((original - optimized) / original) * 100>` | — |

## Notes on Docker optimization

This project demonstrates that a multi-stage build, slim base image, and careful `.dockerignore` usage significantly reduce the final image size without changing the application behavior.

## Conclusion

Using a slim Python base image with a multi-stage build and only the runtime dependencies creates a smaller, more efficient container that is easier to deploy and maintain.
