"""Application configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+psycopg2://smartresort:smartresort@postgres:5432/smartresort"
    # Optional direct (non-pooled) URL used for migrations. Falls back to DATABASE_URL.
    DATABASE_URL_DIRECT: str = ""

    # Connection pool (tuned for managed/serverless Postgres such as Neon)
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_RECYCLE: int = 1800

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # JWT
    JWT_SECRET: str = "dev-secret-key-replace-in-production"
    JWT_REFRESH_SECRET: str = "dev-refresh-secret-replace-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Payment
    PAYMENT_PROVIDER_KEY: str = ""
    PAYMENT_PROVIDER_SECRET: str = ""

    # Firebase
    FIREBASE_PROJECT_ID: str = ""
    FIREBASE_CLIENT_EMAIL: str = ""
    FIREBASE_PRIVATE_KEY: str = ""

    # SMTP
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""

    # CORS
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]

    # Public URL of the customer web app, embedded in generated QR codes
    CUSTOMER_APP_URL: str = "http://localhost:5173"

    # Scheduled jobs (auto-assignment & escalation)
    CRON_ESCALATE_AFTER_MINUTES: int = 30
    CRON_BATCH_SIZE: int = 500
    # Shared secret for the /api/v1/cron trigger endpoint (free-tier scheduling).
    # Leave empty to disable the endpoint.
    CRON_TOKEN: str = ""

    @property
    def migration_database_url(self) -> str:
        """URL to use for Alembic migrations (prefers a direct connection)."""
        return self.DATABASE_URL_DIRECT or self.DATABASE_URL

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
