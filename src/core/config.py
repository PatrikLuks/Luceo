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
