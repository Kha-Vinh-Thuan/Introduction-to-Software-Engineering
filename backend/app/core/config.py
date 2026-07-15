from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "DataPilot"
    app_version: str = "1.0.0"
    debug: bool = False

    database_path: str = "postgresql://postgres:12345678@localhost:5432/postgres"

    anthropic_api_key: str = ""
    claude_model: str = "claude-haiku-4-5-20251001"

    openrouter_api_key: str = ""
    openrouter_model: str = "meta-llama/llama-3.3-70b-instruct:free"

    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]


settings = Settings()
