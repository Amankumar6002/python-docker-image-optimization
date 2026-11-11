# Release Checklist

Verification performed on 2026-11-11. Checkboxes represent completed work supported by local or remote evidence.

## Source and application
- [x] Existing Flask app preserved; title/description types are validated as strings.
- [x] App and tests compile with `python -m compileall app tests`.
- [x] Dependencies use separate runtime and development requirements.
- [x] Parameterized PostgreSQL statements remain in use.
- [x] Invalid input and missing-note responses tested.
- [x] Windows local entry point is `python -m app`; Linux containers use Gunicorn.

## Docker
- [x] Docker Linux engine available.
- [x] Baseline build passes with both requirements files copied.
- [x] Baseline does not copy the ignored `tests/` directory.
- [x] Optimized multi-stage image builds successfully using Python Slim.
- [x] Runtime dependencies only; pytest and gcc absent from optimized image.
- [x] Optimized image runs as non-root user `app` (UID 999).
- [x] Gunicorn command, exposed port, and health check inspected.
- [x] Image comparison PowerShell script passes and rejects missing tags.
- [x] Inspect-based baseline/optimized comparison measured: 1,631,085,307 bytes vs 220,181,371 bytes.
- [x] Saved 1,410,903,936 bytes (1,410.90 MB / 1,345.54 MiB), or 86.50%.

## PostgreSQL and Compose
- [x] PostgreSQL service running and healthy.
- [x] Application service running and healthy.
- [x] Application database readiness confirmed connected.
- [x] Compose config uses `db` service hostname and health-based startup dependency.
- [x] Named volume `python-docker-image-optimization_postgres_data` confirmed and retained.
- [x] Note ID 7 was created, retrieved, persisted across app-only restart, then deleted; final notes response was `[]`.

## Testing
- [x] Docker-based pytest: 13 passed, 0 failed, exit code 0.
- [x] Live PostgreSQL readiness and notes CRUD integration tests passed.
- [x] Both baseline and optimized running containers exercised against PostgreSQL.
- [x] Health, readiness, invalid input (400), and missing note (404) verified.
- [x] `python -m compileall app tests` passed.
- [x] GitHub Actions workflow config includes Python 3.12 and PostgreSQL 16 service.
- [x] Docker-network PostgreSQL test suite passed: 13 tests, exit code 0.
- [x] GitHub Actions runs #3 and #4 passed; #3 ran the PostgreSQL-backed pytest job.
- [x] Native Windows pytest database authentication limitation is documented and not counted as a pass.

## Security and repository
- [x] `.env`, `.venv`, Python caches, and local DB files excluded by Git ignore rules.
- [x] `.env`, `.venv`, tests, and local DB files excluded from Docker build context where appropriate.
- [x] No committed live secrets found in the source scan.
- [x] `.env.example` uses development-only placeholder values.
- [ ] Review and configure production secrets outside source control before deploying beyond local development.

## Documentation and publication
- [x] README describes architecture, Windows and Linux execution, Docker build/size measurement, APIs, tests, and measured result.
- [x] `PROJECT_FINAL_REPORT.md` records evidence and outstanding items.
- [x] `compare_images.ps1` documents and reproduces inspect-based size comparison.
- [x] Commit and push final measurement/API documentation updates to existing `main`.
- [x] Verify remote `main` and README publication; GitHub Actions runs #3 and #4 passed.

## Measurement definitions

The reported sizes use `docker image inspect ... --format='{{.Size}}'`. These are local uncompressed layer totals, not compressed registry sizes or Docker's local disk-use accounting. MB uses 1,000,000 bytes; MiB uses 1,048,576 bytes.

Do not delete `python-docker-image-optimization_postgres_data` or run `docker compose down -v` during cleanup.
