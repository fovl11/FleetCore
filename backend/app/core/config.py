import os
from functools import cached_property

class Settings:
    @cached_property
    def database_url(self) -> str:
        return os.getenv("DATABASE_URL", "postgresql+psycopg://fleetcore:fleetcore_local@localhost:5432/fleetcore")

    @cached_property
    def cors_origins(self) -> list[str]:
        return [value.strip() for value in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if value.strip()]

    @property
    def jwt_secret_key(self) -> str | None:
        return os.getenv("JWT_SECRET_KEY")

    @property
    def auth_cookie_secure(self) -> bool:
        return os.getenv("AUTH_COOKIE_SECURE", "false").lower() in {"1", "true", "yes"}

settings = Settings()
