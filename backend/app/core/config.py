from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SupportDesk AI"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"

    database_url: str
    test_database_url: str | None = None

    backend_cors_origins: str = "http://localhost:5173"

    enable_demo_seed: bool = True

    # LLM settings
    llm_api_key: str | None = None
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4.1-mini"
    llm_timeout_seconds: int = 30
    enable_llm_fallback: bool = True

    # n8n automation settings
    n8n_webhook_ticket_created_url: str | None = None
    n8n_webhook_ai_completed_url: str | None = None
    enable_n8n_automation: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.backend_cors_origins.split(",")
            if origin.strip()
        ]

    @property
    def has_llm_api_key(self) -> bool:
        return bool(self.llm_api_key and self.llm_api_key.strip())

    @property
    def has_ticket_created_webhook(self) -> bool:
        return bool(
            self.n8n_webhook_ticket_created_url
            and self.n8n_webhook_ticket_created_url.strip()
        )

    @property
    def has_ai_completed_webhook(self) -> bool:
        return bool(
            self.n8n_webhook_ai_completed_url
            and self.n8n_webhook_ai_completed_url.strip()
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()