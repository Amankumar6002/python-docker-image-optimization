# Release Checklist

## Verified
- [x] Flask API and PostgreSQL integration are configured through environment variables.
- [x] Baseline Dockerfile uses `python:3.12` and installs runtime plus development requirements.
- [x] Baseline copies both `requirements.txt` and `requirements-dev.txt`.
- [x] Baseline does not copy `tests/`, which `.dockerignore` excludes.
- [x] Optimized Dockerfile uses Python slim multi-stage build and runtime-only dependencies.
- [x] Optimized runtime uses the non-root `app` user and Gunicorn.
- [x] `.dockerignore` excludes Git data, virtual environments, caches, tests, env files, local DB files, and temporary files while retaining files needed for builds.
- [x] Baseline image build succeeded.
- [x] Optimized image build succeeded.
- [x] Compose PostgreSQL and optimized app reported healthy.
- [x] Baseline and optimized app containers returned success for `/health` and `/ready`.
- [x] Both images created, listed, and deleted notes; nonexistent deletion returned HTTP 404.

## Measured local Docker image sizes
Measured with `docker image inspect`:

- Baseline: 1,631,085,220 bytes (1,631.09 MB / 1,555.52 MiB)
- Optimized: 220,181,206 bytes (220.18 MB / 209.98 MiB)
- Saved: 1,410,904,014 bytes (1,410.90 MB / 1,345.54 MiB)
- Reduction: 86.50%

These are local Docker image inspect sizes (uncompressed layer totals), not compressed registry sizes. The `docker images` output reported 1.63GB / 220MB disk usage and 419MB / 53.4MB content size. Those are different Docker storage measures.

## Reproduce the verification
```powershell
docker build -f Dockerfile.baseline -t python-image-optimization:baseline .
docker build -f Dockerfile -t python-image-optimization:optimized .
docker image inspect python-image-optimization:baseline --format='{{.Size}}'
docker image inspect python-image-optimization:optimized --format='{{.Size}}'
docker compose up --build -d
docker compose ps
docker compose logs app
docker compose logs db
```

## Remaining release checks
- [ ] Confirm intended GitHub repository remote and push the verified changes without force-pushing.
- [ ] Confirm GitHub Actions test workflow status after push.
- [ ] Replace development-only credentials before any non-local deployment.
- [ ] Re-run image measurements after changing pinned dependencies or base image versions.

The existing Compose PostgreSQL volume was retained; do not remove it during cleanup if it may contain user data.
