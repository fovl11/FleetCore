# Architecture

## Runtime shape

The browser loads the React application from Vite. The application calls the FastAPI JSON API using `VITE_API_BASE_URL`. Compose runs the API and PostgreSQL on a private network; PostgreSQL data is stored in a named volume.

## Initial boundaries

- **Frontend:** navigation shell and dashboard overview.
- **Backend:** versioned HTTP API; health route is the first endpoint.
- **Database:** PostgreSQL is provisioned for upcoming fleet entities. Schema changes will use Alembic migrations as persistence is introduced.

## Growth path

Implement fleet capabilities as vertical slices. A vehicle slice, for example, owns its API schemas, domain/application behavior, persistence mapping and migration, frontend API client, and UI. Keep transport and presentation concerns separated. Add authentication and authorization before exposing operational data outside a trusted local environment.
