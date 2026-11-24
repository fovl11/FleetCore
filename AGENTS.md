# FleetCore — architecture rules

## Product boundary
FleetCore is a fleet operations application. The initial slice provides a service health endpoint and a responsive fleet overview shell. Business features should be added as small vertical slices with API, persistence, UI, and documentation where applicable.

## Repository layout
- `backend/`: Python API and persistence.
- `frontend/`: browser application.
- `docs/`: product, architecture, and local development notes.
- `compose.yaml`: local orchestration for app services and PostgreSQL.

## Backend rules
- Keep HTTP routing in `app/api`; application configuration in `app/core`; persistence setup in `app/db`.
- Routers must be mounted through the central API router. Do not put business logic in route handlers as the domain grows.
- Validate external input and output with Pydantic schemas. Keep secrets and environment-specific configuration out of source control.
- Use SQLAlchemy 2.x patterns and Alembic migrations for persisted business data. Never create production schema implicitly on startup.
- Expose liveness/readiness separately once external dependencies need to be checked. Do not leak credentials or stack traces in API responses.

## Frontend rules
- Keep reusable UI in `src/components`, API access in `src/lib`, and page composition at the application entry point.
- Read the API origin from `VITE_API_BASE_URL`; avoid hard-coded deployment hosts.
- Handle loading, empty, and error states for remote data. Keep presentation components independent of transport details.
- Use semantic HTML, keyboard-accessible controls, and responsive layouts.

## Cross-cutting rules
- Services communicate over Compose service names internally; browser-facing API URLs must be reachable from the browser.
- Persist database state in a named volume. Do not commit local environment files, credentials, generated builds, or dependency caches.
- Update README/docs when setup, service boundaries, or operational behavior changes.
- Keep defaults safe for local development and document any required production hardening.
