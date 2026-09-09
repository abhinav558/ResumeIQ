"""
ResumeIQ - Application Configuration.

Centralized, typed configuration for the ResumeIQ backend.

Configuration is loaded from environment variables and .env.
No application code should hard-code deployment-specific values.
"""

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application-wide configuration.

    Environment variables override values defined here.
    """

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------

    app_name: str = "ResumeIQ API"

    app_version: str = "1.0.0"

    app_description: str = (
        "AI Powered Resume Analysis Platform"
    )

    environment: str = "development"

    debug: bool = False

    # ------------------------------------------------------------------
    # API
    # ------------------------------------------------------------------

    api_prefix: str = "/api"

    # ------------------------------------------------------------------
    # CORS
    # ------------------------------------------------------------------

    cors_origins: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:5174",
        ]
    )

    # ------------------------------------------------------------------
    # Upload Security
    # ------------------------------------------------------------------

    max_upload_size_mb: int = Field(
        default=10,
        ge=1,
        le=50,
    )

    allowed_extensions: List[str] = Field(
        default_factory=lambda: [
            ".pdf",
            ".docx",
            ".txt",
        ]
    )

    # ------------------------------------------------------------------
    # Configuration Loading
    # ------------------------------------------------------------------

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # Validators
    # ------------------------------------------------------------------

    @field_validator("environment")
    @classmethod
    def validate_environment(
        cls,
        value: str,
    ) -> str:
        """
        Validate the application environment.
        """

        normalized = value.strip().lower()

        allowed = {
            "development",
            "testing",
            "production",
        }

        if normalized not in allowed:
            raise ValueError(
                "environment must be one of: "
                "development, testing, production"
            )

        return normalized

    @field_validator("allowed_extensions")
    @classmethod
    def normalize_extensions(
        cls,
        value: List[str],
    ) -> List[str]:
        """
        Normalize and deduplicate upload extensions.
        """

        normalized = []

        for extension in value:
            extension = extension.strip().lower()

            if not extension:
                continue

            if not extension.startswith("."):
                extension = f".{extension}"

            normalized.append(extension)

        return list(dict.fromkeys(normalized))


@lru_cache
def get_settings() -> Settings:
    """
    Return a cached application settings instance.

    Caching ensures the application does not repeatedly parse
    environment configuration during every request.
    """

    return Settings()


settings = get_settings()