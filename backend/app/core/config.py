from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SupportDesk AI"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"

    database_url: str

    backend_cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """
        Converts comma-separated CORS origins into a clean list.

        Example:
        BACKEND_CORS_ORIGINS=http://localhost:5173,https://your-app.vercel.app
        """
        return [
            origin.strip()
            for origin in self.backend_cors_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()