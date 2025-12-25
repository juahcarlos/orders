from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str = "..."
    POSTGRES_USER: str = "..."
    POSTGRES_PASSWORD: str = "..."

    # JWT
    secret_key: str = "..."
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # API
    api_prefix: str = "/api"
    debug: bool = False

    # CORS (replace mycompany.com with a real company domain)
    origins: str = "https://mycompany.com,http://localhost,http://localhost:3000"

    register_limit: str = "60/minute"
    token_limit: str = "120/minute"
    hour_max_limit: str = "72000/hour"
    minute_max_limit: str = "1200/minute"
    storage_uri: str = "redis://redis:6379/1"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        if not self.origins:
            return []
        return [origin.strip() for origin in self.origins.split(",")]


settings = Settings()
