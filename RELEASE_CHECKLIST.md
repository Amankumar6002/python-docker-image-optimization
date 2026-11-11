# Release Checklist

Verification performed on 2026-11-11. Checkboxes represent completed work supported by local or remote evidence.

## Source and application
- [x] Existing Flask app preserved; title/description types are validated as strings.
- [x] App and tests compile with `python -m compileall app tests`.
- [x] Dependencies use separate runtime and development requirements.
- [x] Parameterized PostgreSQL statements remain in use.
- [x] Invalid input and missing-note responses tested.
- [x] Windows local entry point is `python -m app`; Linux containers use Gunicorn.
- [x] Responsive dashboard renders overview, image comparison, optimization, architecture, health, and project details.
- [x] Dashboard measurements are read and validated from host-generated JSON; missing and malformed reports show explicit unavailable states.
- [x] Existing Notes API remains functional and is not included in dashboard navigation.

## Docker
- [x] Docker Linux engine available.
- [x] Baseline build passes with both requirements files copied.
- [x] Baseline does not copy the ignored `tests/` directory.
- [x] Optimized multi-stage image builds successfully using Python Slim.
- [x] Runtime dependencies only; pytest and gcc absent from optimized image.
- [x] Optimized image runs as non-root user `app` (UID 999).
- [x] Gunicorn command, exposed port, and health check inspected.
- [x] Image comparison PowerShell script passes and rejects missing tags.
- [x] Inspect-based baseline/optimized comparison measured: 1,631,163,284 bytes vs 220,337,372 bytes.
- [x] Saved 1,410,825,912 bytes (1,410.83 MB / 1,345.47 MiB), or 86.49%.
- [x] PowerShell comparison script writes the measurement report; Compose mounts it read-only without Docker socket access.

## PostgreSQL and Compose
- [x] PostgreSQL service running and healthy.
- [x] Application service running and healthy.
- [x] Application database readiness confirmed connected.
- [x] Compose config uses `db` service hostname and health-based startup dependency.
- [x] Named volume `python-docker-image-optimization_postgres_data` confirmed and retained.
- [x] Note ID 7 was created, retrieved, persisted across app-only restart, then deleted; final notes response was `[]`.

## Testing
- [x] Docker-based pytest: 17 passed, 0 failed, exit code 0.
- [x] Dashboard report missing/valid/malformed cases and byte-based calculations covered.
- [x] Browser checks passed for displayed metrics, health statuses, navigation, and 390px responsive layout; zero page errors.
- [x] Live PostgreSQL readiness and notes CRUD integration tests passed.
- [x] Both baseline and optimized running containers exercised against PostgreSQL.
- [x] Health, readiness, invalid input (400), and missing note (404) verified.
- [x] `python -m compileall app tests` passed.
- [x] GitHub Actions workflow config includes Python 3.12 and PostgreSQL 16 service.
- [x] Docker-network PostgreSQL test suite passed: 17 tests, exit code 0.
- [x] GitHub Actions run #7 passed for dashboard commit `1986f30`.
- [x] Native Windows pytest database authentication limitation is documented and not counted as a pass.

## Kubernetes
- [x] Kubernetes manifests prepared for namespace, app, PostgreSQL, services, ConfigMaps, PVC, and placeholder Secret example.
- [x] Deployment script requires the Docker Desktop context and process-scoped credentials; no real Secret manifest is committed.
- [x] Local optimized image is present: `python-image-optimization:optimized`; latest inspected size remains the measured 220,337,372 bytes.
- [x] YAML syntax/resource references and PowerShell deployment-script syntax validated locally.
- [x] Kubernetes configuration published to `main`; GitHub Actions run #9 passed.
- [ ] Docker Desktop Kubernetes context available and cluster API healthy.
- [ ] Kubernetes API schema validation and `kubectl apply` completed.
- [ ] Flask and PostgreSQL Deployments/Pods ready; PVC bound.
- [ ] Kubernetes probes, DB readiness, dashboard, Notes API, and report endpoint verified.
- [ ] Notes persist across Flask Pod restart.
- [ ] Scale Flask Deployment to 3 replicas and back to 2; verify Pod counts.
- [ ] Capture actual Kubernetes runtime/image availability and deployment evidence.
- [ ] Do not delete the separate Kubernetes PVC or Compose PostgreSQL volume during cleanup.

## Security and repository
- [x] `.env`, `.venv`, Python caches, and local DB files excluded by Git ignore rules.
- [x] `.env`, `.venv`, tests, and local DB files excluded from Docker build context where appropriate.
- [x] No committed live secrets found in the source scan.
- [x] `.env.example` uses development-only placeholder values.
- [ ] Review and configure production secrets outside source control before deploying beyond local development.

## Documentation and publication
- [x] README describes dashboard/report workflow, architecture, Windows and Linux execution, Docker builds, APIs, tests, and current measured result.
- [x] `PROJECT_FINAL_REPORT.md` records dashboard evidence and outstanding items.
- [x] `compare_images.ps1` documents and reproduces inspect-based size comparison.
- [x] Publish dashboard implementation and documentation to the existing `main` branch.
- [x] Verify remote commit `1986f30` and its successful GitHub Actions run #7.

## Measurement definitions

The reported sizes use `docker image inspect ... --format='{{.Size}}'`. These are local uncompressed layer totals, not compressed registry sizes or Docker's local disk-use accounting. MB uses 1,000,000 bytes; MiB uses 1,048,576 bytes.

Do not delete `python-docker-image-optimization_postgres_data` or run `docker compose down -v` during cleanup.
