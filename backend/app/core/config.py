"""
Centralised application configuration.
All settings are read from environment variables.
Falls back to SQLite when IS_LOCAL=true and POSTGRES_HOST is unset.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # ── Auth ──────────────────────────────────────────────────
    jwt_secret: str = "changeme-super-secret"
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 8

    # ── PostgreSQL ────────────────────────────────────────────
    postgres_host: str = ""
    postgres_port: int = 5432
    postgres_name: str = ""
    postgres_user: str = ""
    postgres_pass: str = ""

    # ── Environment flag ──────────────────────────────────────
    is_local: str = "true"        # "true" → no SSL, "false" → sslmode=require

    # ── App ───────────────────────────────────────────────────
    app_title: str = "Team Management API"
    app_version: str = "1.0.0"
    cors_origins: list[str] = ["*"]

    @property
    def database_url(self) -> str:
        """
        Build the SQLAlchemy database URL.
        • POSTGRES_HOST set  → PostgreSQL (SSL enforced outside IS_LOCAL)
        • POSTGRES_HOST unset + IS_LOCAL=true → SQLite fallback
        """
        if not self.postgres_host:
            return "sqlite:///./team_management.db"

        base = (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_pass}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_name}"
        )
        if self.is_local.lower() != "true":
            base += "?sslmode=require"
        return base

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    return Settings()
