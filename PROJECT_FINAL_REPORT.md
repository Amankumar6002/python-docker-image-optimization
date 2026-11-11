# Project Final Report

## Project title
Python Docker Image Optimization – Reducing Docker Image Size Using Multi-Stage Builds

## Objective
Create a complete, practical Python project that demonstrates how to reduce a bloated Docker image into a smaller, production-ready container using:

- a slim Python base image
- a multi-stage Docker build
- minimal runtime dependencies
- `.dockerignore`
- careful application packaging
- PostgreSQL connectivity with environment variables

## Summary of implementation
The project includes:

- Flask application with note API endpoints
- PostgreSQL connection layer using environment variables
- Docker baseline image (`Dockerfile.baseline`)
- Optimized multi-stage image (`Dockerfile`)
- Docker Compose service for PostgreSQL and the app
- `.dockerignore`, `.gitignore`, and `.env.example`
- pytest-based checks for app behavior
- README documentation for setup and usage

## Files created
- `app/__init__.py`
- `app/__main__.py`
- `app/config.py`
- `app/database.py`
- `app/routes.py`
- `db/init.sql`
- `tests/test_app.py`
- `Dockerfile`
- `Dockerfile.baseline`
- `docker-compose.yml`
- `.dockerignore`
- `.gitignore`
- `.env.example`
- `requirements.txt`
- `requirements-dev.txt`
- `pytest.ini`
- `README.md`

## Verified status
### Python validation
Executed successfully:

```powershell
cd "C:\Users\vikas\Image Optimization\python-docker-image-optimization"
pytest -q
```

Result:

```text
5 passed in 0.88s
```

### Local app startup validation
Executed successfully:

```powershell
cd "C:\Users\vikas\Image Optimization\python-docker-image-optimization"
python -m app
```

Health check result:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:5000/health
```

Output:

```text
service            status
-------            ------
image-optimization ok
```

### Readiness validation
When PostgreSQL was unavailable, the application correctly returned an HTTP 503 response with a database-unavailable message.

## Docker status
Docker is installed, but the local daemon is not running in this environment. The runtime status is therefore blocked for actual image builds and Compose verification.

Command attempted:

```powershell
docker info
```

Observed result:

```text
failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine; check if the path is correct and if the daemon is running: open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.
```

## What remains to complete on a Docker-enabled machine
1. Build the baseline image
2. Build the optimized image
3. Inspect image sizes
4. Compute size saved and percentage reduction
5. Start the full Compose stack
6. Validate health and database endpoints
7. Create and delete notes through the API
8. Confirm PostgreSQL persistence and network configuration

## Final image comparison formula
The final project expects the following values to be measured from Docker:

```text
Image Size Saved = Original Image Size - Optimized Image Size
Percentage Reduction = ((Original Image Size - Optimized Image Size) / Original Image Size) * 100
```

Important: the project intentionally does not report a size reduction without actual local Docker image inspection results.

## Recommendation
The implementation is ready for GitHub and release packaging, but true final Docker benchmarking must be completed on a machine with Docker Desktop running or a Linux Docker engine available.

## Final conclusion
The codebase is clean, functionally validated at the Python layer, and structurally ready for Docker optimization work. The final Docker proof step remains dependent on the availability of a live Docker daemon.
