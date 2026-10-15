"""Application settings loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_INSECURE_SECRET = "change-me-to-a-long-random-string-in-production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="Bharat Yatra", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=True, alias="DEBUG")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")
    cors_origins: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        alias="CORS_ORIGINS",
    )

    secret_key: str = Field(
        default=DEFAULT_INSECURE_SECRET,
        alias="SECRET_KEY",
    )
    access_token_expire_minutes: int = Field(
        default=30,
        alias="ACCESS_TOKEN_EXPIRE_MINUTES",
    )
    refresh_token_expire_days: int = Field(
        default=14,
        alias="REFRESH_TOKEN_EXPIRE_DAYS",
    )
    algorithm: str = Field(default="HS256", alias="ALGORITHM")

    database_url: str = Field(
        default=(
            "postgresql+psycopg2://bharatyatra:bharatyatra_dev_password"
            "@localhost:5432/bharatyatra"
        ),
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    celery_broker_url: str = Field(
        default="redis://localhost:6379/1",
        alias="CELERY_BROKER_URL",
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/2",
        alias="CELERY_RESULT_BACKEND",
    )

    ai_provider: str = Field(default="mock", alias="AI_PROVIDER")
    payment_provider: str = Field(default="mock", alias="PAYMENT_PROVIDER")
    otp_provider: str = Field(default="mock", alias="OTP_PROVIDER")
    otp_expire_minutes: int = Field(default=10, alias="OTP_EXPIRE_MINUTES")
    # Exposed only by MockOtpProvider in debug responses when true AND debug mode
    otp_debug_expose_code: bool = Field(default=True, alias="OTP_DEBUG_EXPOSE_CODE")

    rate_limit_enabled: bool = Field(default=True, alias="RATE_LIMIT_ENABLED")
    rate_limit_auth_per_minute: int = Field(
        default=30,
        alias="RATE_LIMIT_AUTH_PER_MINUTE",
        ge=1,
        le=1000,
    )
    security_headers_enabled: bool = Field(
        default=True,
        alias="SECURITY_HEADERS_ENABLED",
    )
    trusted_hosts: str = Field(
        default="*",
        alias="TRUSTED_HOSTS",
        description="Comma-separated hosts; use * to disable TrustedHostMiddleware",
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def trusted_hosts_list(self) -> list[str]:
        return [host.strip() for host in self.trusted_hosts.split(",") if host.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() in {"production", "prod"}

    @property
    def expose_otp_debug_code(self) -> bool:
        """Never expose OTP codes outside debug mode."""
        return bool(self.debug and self.otp_debug_expose_code)

    def validate_for_runtime(self) -> None:
        """Fail fast on insecure production configuration."""
        if self.debug and not self.is_production:
            return
        if self.secret_key == DEFAULT_INSECURE_SECRET or len(self.secret_key) < 32:
            raise RuntimeError(
                "Insecure SECRET_KEY for non-debug/production runtime. "
                "Set a strong SECRET_KEY (32+ chars) and DEBUG=false.",
            )
        if self.otp_debug_expose_code and self.is_production:
            raise RuntimeError(
                "OTP_DEBUG_EXPOSE_CODE must be false in production.",
            )


@lru_cache
def get_settings() -> Settings:
    return Settings()
