# Local development

Requirements: Docker Engine with the Compose plugin. For editing without containers, use Python 3.12+ and Node.js 22+.

## Compose

Copy `.env.example` to `.env`, then run `docker compose up --build`. Compose exposes the web app on port 5173, API on 8000, and PostgreSQL on 5432. The database uses a named volume so its data survives container restarts.

## Backend without Compose

From `backend/`, install `requirements.txt`, then run `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`.

## Frontend without Compose

From `frontend/`, run `npm install` and `npm run dev -- --host 0.0.0.0`. Set `VITE_API_BASE_URL` to the API origin (default `http://localhost:8000`).
