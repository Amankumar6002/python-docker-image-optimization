# Release Checklist

## Project
Image Optimization (Python) – Reducing Docker Image Size Using Multi-Stage Builds

## Release readiness status
- [x] Source code created and organized
- [x] Flask application implemented
- [x] PostgreSQL configuration and dependency injection set up via environment variables
- [x] Docker baseline image defined
- [x] Optimized multi-stage Dockerfile defined
- [x] `.dockerignore` created
- [x] Docker Compose configuration created
- [x] Python tests implemented and passing
- [x] README documentation prepared
- [ ] Real Docker image builds executed on a machine with Docker Desktop or a running Docker engine
- [ ] Real image size comparison measured locally
- [ ] Compose stack fully validated in a running Docker environment

## Required checks before release
### 1. Local Python verification
- [x] Install dependencies with `pip install -r requirements-dev.txt`
- [x] Run `pytest -q`
- [x] Confirm all tests pass
- [x] Confirm local health endpoint works

### 2. Docker engine verification
- [ ] Confirm `docker --version` works
- [ ] Confirm `docker compose version` works
- [ ] Confirm `docker info` shows a healthy engine
- [ ] Ensure Docker Desktop is running

### 3. Docker image build verification
- [ ] Run baseline build: `docker build -f Dockerfile.baseline -t python-image-optimization:baseline .`
- [ ] Run optimized build: `docker build -f Dockerfile -t python-image-optimization:optimized .`
- [ ] Confirm both builds complete successfully
- [ ] Inspect both image sizes with `docker image inspect ... --format='{{.Size}}'`

### 4. Compose verification
- [ ] Run `docker compose up --build -d`
- [ ] Confirm PostgreSQL is healthy
- [ ] Confirm app container is healthy
- [ ] Confirm endpoints return expected HTTP results

### 5. API verification
- [ ] `GET /health`
- [ ] `GET /ready`
- [ ] `GET /api/notes`
- [ ] `POST /api/notes`
- [ ] `DELETE /api/notes/<id>`
- [ ] Invalid payload handling
- [ ] Missing note deletion behavior

### 6. GitHub preparation
- [ ] Confirm repo root contains all required files
- [ ] Ensure `.env` is not committed
- [ ] Review `.gitignore`
- [ ] Add project description and topics
- [ ] Add badges or screenshots if desired
- [ ] Create GitHub release notes

## Verified local results
- `pytest -q` completed successfully with 5 passing tests.
- Local app health check was validated via `python -m app` and `Invoke-RestMethod http://127.0.0.1:5000/health`.
- Readiness endpoint responded with a correct 503 when PostgreSQL was unavailable.

## Blocker encountered
Docker build and Compose validation are currently blocked in this environment because the Docker daemon is not running:

```powershell
docker info
```

Result:

```text
failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine; check if the path is correct and if the daemon is running: open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.
```

## Final sign-off note
The project is functionally ready for local Python validation and repository packaging, but the actual Docker image-size benchmarking must be performed on a machine with Docker Desktop running or a Linux Docker engine available.
