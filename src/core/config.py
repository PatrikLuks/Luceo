from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "case_sensitive": False}

    # App
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "info"

    # Database
    postgres_user: str = "luceo"
    postgres_password: str = "changeme"
    postgres_db: str = "luceo"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    # Auth
    jwt_secret: str = "changeme-generate-a-real-secret"
    jwt_expiration_hours: int = 24

    # Anthropic
    anthropic_api_key: str = ""

    # Encryption
    encryption_key: str = "changeme-generate-a-real-key"

    # CORS
    cors_allowed_origins: str = ""  # Comma-separated origins for production

    # GDPR
    data_region: str = "eu-central"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def database_url_sync(self) -> str:
        """Sync URL for Alembic migrations."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()


def validate_production_settings() -> None:
    """Ensure critical secrets are set in non-development environments."""
    if settings.app_env == "development":
        return
    errors = []
    if settings.jwt_secret.startswith("changeme"):
        errors.append("jwt_secret must be set to a real secret in production")
    if settings.encryption_key.startswith("changeme"):
        errors.append("encryption_key must be a 64-char hex string in production")
    if not settings.anthropic_api_key:
        errors.append("anthropic_api_key must be set in production")
    if errors:
        raise RuntimeError(f"Production configuration errors: {'; '.join(errors)}")
