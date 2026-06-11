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

    database_path: str = "./data/datapilot.db"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]


settings = Settings()
