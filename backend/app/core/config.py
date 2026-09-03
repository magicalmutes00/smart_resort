"""Application configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:pratheesh1004@db.ccobvieckisfmmdyeeim.supabase.co:5432/postgres?sslmode=require"

    # Redis
    REDIS_URL: str = "redis://red-dacq81mk1f9s73aaang0:6379"

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

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
