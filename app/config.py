from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    app_name: str = "examate-rag"
    environment: str = "local"

    openai_api_key: SecretStr | None = None
    database_url: SecretStr | None = None

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:1.5b"


@lru_cache
def get_settings() -> Settings:
    return Settings()
