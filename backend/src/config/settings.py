"""Application configuration, loaded from environment with Pydantic Settings."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Stack
    environment: str = "development"
    debug: bool = True
    secret_key: str = ""

    # Database — MUST be set via DATABASE_URL env var in production
    database_url: str = "postgresql+psycopg2://cmp:<password>@localhost:5432/cmp"
    database_pool_size: int = 20
    database_max_overflow: int = 40

    # Admin — MUST be overridden via env vars in production
    admin_email: str = "admin@cmp.local"
    admin_password: str = ""

    # Encryption — MUST be set via ENCRYPTION_KEY env var in production
    encryption_key: str = ""

    # JWT — MUST be set via JWT_SECRET env var in production
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    sdk_token_ttl_minutes: int = 15
    api_token_ttl_minutes: int = 60
    refresh_token_ttl_days: int = 30

    # AWS
    aws_region: str = "ap-south-1"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    s3_bucket: str = "cmp-audit-logs"
    ses_source_email: str = "noreply@cmp.example.com"
    sns_sender_id: str = "CMP"

    # Webhook
    webhook_retry_max: int = 5
    webhook_retry_backoff_base: int = 60

    # SLA (seconds)
    sla_rights_request: int = 7_776_000  # 90 days
    sla_grievance: int = 259_200  # 3 days

    # Rate limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000

    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:8000"

    # Logging
    log_level: str = "DEBUG"
    log_format: str = "json"


settings = Settings()
