# Python Docker Image Optimization

**Reducing Docker image size with Python Slim images and multi-stage builds**

This project is a Flask and PostgreSQL application with a responsive Docker image optimization dashboard. It compares a deliberately unoptimized single-stage Docker image with a multi-stage production image built on `python:3.12-slim`.

## Objectives

- Keep the same Flask and PostgreSQL behavior in both images.
- Exclude development packages and build-only files from the optimized runtime.
- Run the optimized Linux container as a non-root user under Gunicorn.
- Measure local Docker image sizes from Docker inspection rather than estimating them.

The original 1.5 GB scenario is a reference point, not a promised baseline result. The actual sizes depend on the resolved base image, architecture, Docker version, and installed packages.

## Stack and features

- Python 3.12, Flask, Gunicorn and psycopg 3
- PostgreSQL 16 Alpine
- Docker, Docker Compose, PowerShell and pytest
- Health and database-readiness endpoints
- Parameterized SQL, note validation and CRUD API
- Compose health checks and a persistent named database volume
- GitHub Actions workflow with a PostgreSQL service
- Responsive dashboard with measured image sizes and live application/database status
- Host-generated JSON measurement report; the Flask container has no Docker socket access

## Architecture

```text
PowerShell / HTTP client
          |
          v
Flask dashboard + API + Gunicorn container (port 5000)
          |
          | Compose network; DB_HOST=db
          v
PostgreSQL container (port 5432)
          |
          v
Named volume: postgres_data

Docker host -- compare_images.ps1 --> reports/image-comparison.json
                                      (read-only bind mount; no Docker socket)
```

`Dockerfile.baseline` packages runtime and pytest dependencies in one full Python image. `Dockerfile` installs only runtime requirements into a virtual environment in a slim builder stage, then copies that environment and the app into a separate slim runtime stage.

## Project layout

```text
python-docker-image-optimization/
├── app/
│   ├── __init__.py
│   ├── __main__.py       # Windows/local Flask development entry point
│   ├── config.py
│   ├── dashboard.py      # Safely reads and validates the host-generated report
│   ├── database.py
│   ├── routes.py
│   ├── static/           # Dashboard CSS and JavaScript
│   └── templates/        # Server-rendered dashboard
├── db/
│   └── init.sql
├── reports/
│   └── image-comparison.json
├── tests/
│   ├── conftest.py
│   ├── test_app.py
│   ├── test_dashboard.py
│   ├── test_database_integration.py
│   ├── test_notes_integration.py
│   └── test_validation_integration.py
├── .github/workflows/tests.yml
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── Dockerfile.baseline
├── docker-compose.yml
├── compare_images.ps1
├── pytest.ini
├── requirements.txt
├── requirements-dev.txt
├── PROJECT_FINAL_REPORT.md
└── RELEASE_CHECKLIST.md
```

## Docker image approach

### Baseline

The baseline uses the full `python:3.12` image and installs runtime plus development requirements in a single stage. `requirements-dev.txt` includes `-r requirements.txt`, so the baseline copies both files before pip installs them. Tests are excluded from the build context and are not copied into the runtime image.

### Optimized image

The optimized Dockerfile uses two `python:3.12-slim` stages:

1. **Builder:** creates `/opt/venv` and installs `requirements.txt` without pip cache.
2. **Runtime:** copies only the runtime virtual environment, application and database schema; creates an `app` user; and starts Gunicorn on `0.0.0.0:5000`.

The final image has no pytest dependency and no `gcc` executable. Docker inspect confirmed the configured user is `app` (UID 999 in the measured image).

### `.dockerignore`

`.dockerignore` reduces the files sent to the Docker build context and prevents ignored files from being copied into an image layer. It does **not** shrink the final image for files that were never copied into an image. This project excludes Git data, virtual environments, caches, tests, local env files, local database files, and temporary files while retaining both requirements files and the `app/` and `db/` directories.

## Windows development and Linux container runtime

Gunicorn is the production server in the Linux container; it is not the native Windows development server. On Windows, run:

```powershell
python -m app
```

This uses `app/__main__.py` to start Flask using `APP_HOST` and `APP_PORT`. For Docker, the Dockerfiles start Gunicorn in the container.

## Setup and run

Requirements: Python 3.12, Docker Desktop with Linux containers, and Docker Compose.

```powershell
Set-Location "C:\Users\vikas\Image Optimization\python-docker-image-optimization"
Copy-Item .env.example .env
```

Edit `.env` with development-only database settings before starting the Compose services. Do not commit `.env`; `.env.example` is tracked and contains placeholders.

```powershell
docker context use desktop-linux
docker info
docker build -f Dockerfile.baseline -t python-image-optimization:baseline .
docker build -f Dockerfile -t python-image-optimization:optimized .
.\compare_images.ps1
docker compose up --build -d
docker compose ps
docker compose logs --tail=100 app
docker compose logs --tail=100 db
```

`compare_images.ps1` writes the measured values to `reports/image-comparison.json`. Compose mounts that directory read-only into the app. Re-run the script after rebuilding either image so the dashboard report reflects the current tags. Compose waits for PostgreSQL's health check before starting the app. Database data is persisted in the named `postgres_data` volume. Do not use `docker compose down -v` if the volume may contain data.

## Optimization dashboard

Open [http://localhost:5000](http://localhost:5000) for the dashboard. Its sections cover measured image sizes, build techniques, application architecture, live Flask/PostgreSQL health, and project details. The Refresh button reloads measurements and checks service status; the status cards also refresh every 30 seconds.

The dashboard gets measurements from `GET /api/optimization`, which reads and validates `reports/image-comparison.json` and calculates saved size and reduction from the recorded byte counts. If the report is missing, it displays: “Docker image measurements are not available yet. Build both Docker images and execute compare_images.ps1.” The API returns an unavailable response rather than fabricated or hard-coded measurements.

The PowerShell script runs on the Docker host. The Flask container only reads the report via a read-only bind mount; it neither mounts the Docker socket nor runs Docker commands. The existing Notes API remains available for tests and demonstrations, but is not part of dashboard navigation.

## API

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Flask process health |
| GET | `/ready` | PostgreSQL connectivity readiness |
| GET | `/` | Responsive Docker optimization dashboard |
| GET | `/api/optimization` | Validated measurements and derived comparison metrics |
| GET | `/api/notes` | List notes |
| POST | `/api/notes` | Create a note with string `title` and `description` |
| DELETE | `/api/notes/<id>` | Delete a note; returns 404 if missing |

Example PowerShell requests:

```powershell
Invoke-RestMethod http://localhost:5000/health
Invoke-RestMethod http://localhost:5000/ready

$body = @{
    title = "Docker verification"
    description = "A sample note"
} | ConvertTo-Json

$created = Invoke-RestMethod `
    -Uri http://localhost:5000/api/notes `
    -Method Post `
    -ContentType "application/json" `
    -Body $body

Invoke-RestMethod http://localhost:5000/api/notes
Invoke-RestMethod `
    -Uri "http://localhost:5000/api/notes/$($created.note.id)" `
    -Method Delete
```

## Tests and CI

The tests cover route behavior, dashboard rendering and report handling, real PostgreSQL readiness and note persistence, input validation, and missing-note deletion. The integration fixtures initialize the idempotent schema from `db/init.sql` and clean up their own uniquely named test notes.

For CI, `.github/workflows/tests.yml` provides PostgreSQL 16 with a health check, installs Python 3.12 dependencies, and runs pytest.

The integration suite needs a reachable PostgreSQL with the same `DB_*` environment values as the test process. With the Compose database already running, the verified Docker-based test command is:

```powershell
$project = (Get-Location).Path
$containerEnv = docker inspect python-docker-image-optimization-app-1 `
    --format '{{range .Config.Env}}{{println .}}{{end}}'
$dockerArgs = @(
    "run", "--rm",
    "--network", "python-docker-image-optimization_default",
    "-v", "${project}:/project",
    "--workdir", "/project"
)
foreach ($entry in $containerEnv) {
    if ($entry -match "^DB_(NAME|USER|PASSWORD|PORT)=") {
        $dockerArgs += @("--env", $entry)
    }
}
$dockerArgs += @(
    "--env", "DB_HOST=db",
    "python-image-optimization:baseline",
    "python", "-m", "pytest", "-v"
)
docker @dockerArgs
```

The baseline image includes pytest; the optimized runtime intentionally does not. Run the lightweight Python syntax check with:

```powershell
python -m compileall app tests
```

## Build and compare image sizes

```powershell
docker build -f Dockerfile.baseline -t python-image-optimization:baseline .
docker build -f Dockerfile -t python-image-optimization:optimized .
docker images python-image-optimization
docker image inspect python-image-optimization:baseline --format='{{.Size}}'
docker image inspect python-image-optimization:optimized --format='{{.Size}}'
.\compare_images.ps1
```

`compare_images.ps1` verifies both tags exist, reports inspect sizes in bytes, MB (1,000,000 bytes), MiB (1,048,576 bytes), and computes space saved and reduction. It accepts optional `-BaselineImage` and `-OptimizedImage` tag arguments.

### Current measured result

Measured after rebuilding both images from the current source:

| Measure | Baseline | Optimized |
|---|---:|---:|
| Base | `python:3.12` | `python:3.12-slim` |
| Strategy | Single-stage | Multi-stage |
| Dependencies | Runtime + development | Runtime only |
| Image inspect size | 1,631,163,284 bytes (1,631.16 MB / 1,555.60 MiB) | 220,337,372 bytes (220.34 MB / 210.13 MiB) |

**Saved:** 1,410,825,912 bytes (1,410.83 MB / 1,345.47 MiB)

**Reduction:** 86.49%

Calculation: `(1,631,163,284 - 220,337,372) / 1,631,163,284 * 100 = 86.49%`.

These are local Docker image inspect size totals, not compressed registry sizes. `docker images` disk usage is a different metric that can depend on shared layers and Docker's storage accounting.

## Verification notes

- The original baseline build failure was caused by copying only `requirements-dev.txt` even though it includes `requirements.txt`. Both files are now copied before installation.
- Both current images built successfully.
- Both baseline and optimized containers were run against the Compose PostgreSQL service. Health, readiness, create/list/delete, invalid payload, and missing-note behavior were checked.
- The final recorded API test passed `GET /health`, `GET /ready`, `GET /api/notes`, `POST /api/notes`, and `DELETE /api/notes/7`.
- Note ID 7 was created, retrieved, persisted across an application-container restart, and then deleted. The final `GET /api/notes` returned an empty array (`[]`).
- Docker Compose reported both the Flask app and PostgreSQL containers healthy. The named PostgreSQL volume was preserved.
- The Docker-based pytest run passed all 17 tests; `compileall` passed. Browser validation also checked the rendered metrics, both operational status cards, section navigation, and a 390px-wide layout with no horizontal page overflow.
- Docker inspect and runtime checks confirmed the optimized user, Gunicorn command, port, app/schema files, and absence of pytest and gcc.
- GitHub Actions run [#7](https://github.com/Amankumar6002/python-docker-image-optimization/actions/runs/43063834844) passed for dashboard commit `1986f30c5d1760538ad389db9fd53c3817ef7a3c`.

Native Windows pytest could not authenticate against PostgreSQL at `localhost:5432`, including when the active Compose app's `DB_*` settings were forwarded to the host test process. This is an environment configuration limitation, not a passing native-host integration run. The full 17-test suite passed inside Docker on the Compose network. CI uses its separately configured PostgreSQL service.

## Future improvements

- Add a dedicated database migration tool for evolving schemas.
- Add structured application logging and request IDs.
- Pin base images by digest and automate dependency update review.
- Add container vulnerability scanning and deployment-specific secret management.

## Conclusion

This project demonstrates a measurable local image-size reduction while retaining the tested Flask and PostgreSQL behavior. The result is specific to the current Docker engine and image tags; rerun the comparison after changing dependencies or base images.
