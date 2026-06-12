from dataclasses import dataclass
import os
from typing import List


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "AI Python Practice Assistant API")
    app_env: str = os.getenv("APP_ENV", "development")
    debug: bool = _get_bool("DEBUG", True)
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/app.db")
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-change-me")
    access_token_expire_minutes: int = _get_int("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24)
    code_run_timeout_seconds: int = _get_int("CODE_RUN_TIMEOUT_SECONDS", 3)
    code_output_limit: int = _get_int("CODE_OUTPUT_LIMIT", 4000)
    frontend_origins: str = os.getenv(
        "FRONTEND_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.frontend_origins.split(",") if origin.strip()]


settings = Settings()
