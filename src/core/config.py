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
    jwt_expiration_hours: int = 1  # Short-lived access token (use refresh tokens)
    refresh_token_expiry_days: int = 30

    # Anthropic
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"

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
    if settings.jwt_secret.startswith("changeme") or len(settings.jwt_secret) < 32:
        errors.append("jwt_secret must be a real secret (min 32 chars) in production")
    enc = settings.encryption_key
    if enc.startswith("changeme") or len(enc) < 64:
        errors.append("encryption_key must be a 64-char hex string in production")
    if not settings.anthropic_api_key:
        errors.append("anthropic_api_key must be set in production")
    if settings.postgres_password.startswith("changeme"):
        errors.append("postgres_password must be set to a real password in production")
    if errors:
        raise RuntimeError(f"Production configuration errors: {'; '.join(errors)}")
