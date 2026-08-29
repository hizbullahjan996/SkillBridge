from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    # App
    app_name: str = "SkillBridge API"
    app_env: str = "development"
    debug: bool = True
    api_prefix: str = "/api"

    # Database
    database_url: str = "postgresql://postgres:password@localhost:5432/skillbridge"

    # Security
    secret_key: str = "change-me-to-a-random-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # ML
    ml_model_path: str = "../ml/models/skillbridge_career_classifier.joblib"

    # LLM
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"
    llm_api_key: str = ""
    llm_base_url: str = ""

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


settings = Settings()

_INSECURE_DEFAULTS = {"change-me-to-a-random-secret-key"}
if settings.is_production and settings.secret_key in _INSECURE_DEFAULTS:
    raise RuntimeError(
        "SECRET_KEY must be set to a secure random value in production. "
        "The default value is not allowed."
    )
