# FleetCore

FleetCore is a fleet operations starter with a React client, FastAPI API, and PostgreSQL, runnable with Docker Compose.

## Quick start with Docker Compose

1. Copy `.env.example` to `.env`.
2. Generate a private JWT signing key and set `JWT_SECRET_KEY` in `.env` to the output. PowerShell: `$bytes = New-Object byte[] 32; [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes); -join ($bytes | ForEach-Object { $_.ToString("x2") })`. Set `AUTH_COOKIE_SECURE=true` behind HTTPS in production.
3. Run `docker compose up --build -d`.
4. Apply schema migrations: `docker compose exec backend alembic upgrade head`.
5. Open the frontend at <http://localhost:5173>, API docs at <http://localhost:8000/docs>, and readiness at <http://localhost:8000/api/v1/health>.
6. Run backend tests with `docker compose exec backend python -m pytest -v`.

Migrations are explicit and do not run on application startup. Keep `.env` private and never commit real credentials or JWT keys.

## Authentication API

- `POST /api/v1/auth/register` accepts email, password, organization_name, and optional display_name; creates an owner membership.
- `POST /api/v1/auth/login` accepts email and password.
- Login/register return a short lived access token. The rotating refresh JWT is stored in an HttpOnly, SameSite=Strict cookie.
- `POST /api/v1/auth/refresh` rotates the refresh cookie and returns a new access token.
- `POST /api/v1/auth/logout` revokes the current refresh session and clears the cookie.
- `GET /api/v1/auth/me` requires `Authorization: Bearer <access_token>` and returns the user's current organization and role.

Access tokens expire after 15 minutes; refresh sessions expire after 7 days. Refresh JWTs are signed and their session IDs are stored in PostgreSQL so they can be rotated and revoked. Organization membership is rechecked for protected requests.

## Backend development without Compose

Requires Python 3.12+. From `backend/`, create and activate a virtual environment, then run `python -m pip install -r requirements.txt`. Set `DATABASE_URL` to a PostgreSQL SQLAlchemy URL and `JWT_SECRET_KEY` to a randomly generated key of at least 32 bytes. Run `alembic upgrade head`, then `uvicorn app.main:app --reload`. Run tests with `python -m pytest -v`.

## Repository

See [AGENTS.md](AGENTS.md) and [docs/architecture.md](docs/architecture.md).
