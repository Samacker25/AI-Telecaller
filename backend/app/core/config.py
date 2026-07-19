"""Application configuration loaded exclusively from environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application settings.

    Values come from environment variables (or a local .env file in development).
    Secrets must never be hardcoded or committed.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    app_name: str = "AI Telecaller"
    app_version: str = "0.1.0"
    app_env: Literal["development", "staging", "production"] = "development"
    debug: bool = False
    log_level: str = "INFO"
    api_v1_prefix: str = "/api/v1"

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_telecaller"

    # Auth
    # Development-only default; production must set JWT_SECRET via environment.
    # HS256 requires at least 32 bytes (RFC 7518).
    jwt_secret: str = "change-me-in-production-min-32-byte-secret"  # noqa: S105
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    # AI providers
    gemini_api_key: str = ""
    pinecone_api_key: str = ""
    pinecone_index: str = ""

    # Knowledge ingestion
    embedding_model: str = "gemini-embedding-001"
    embedding_dimension: int = 768
    chunk_size: int = 1200  # target chunk length in characters
    chunk_overlap: int = 200  # characters carried over between adjacent chunks

    # Uploads
    upload_directory: str = "uploads"
    max_upload_size: int = 10 * 1024 * 1024  # 10 MB

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    """Return the cached settings instance."""
    return Settings()
