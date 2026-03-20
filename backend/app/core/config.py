from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # SQLite fallback for Hugging Face / local-no-Postgres setups
    DATABASE_URL: str = "sqlite:////tmp/mindwatch.db"

    SECRET_KEY: str = "change-me-in-production-mindwatch-secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/auth/google/callback"

    SPOTIFY_CLIENT_ID: str = ""
    SPOTIFY_CLIENT_SECRET: str = ""
    SPOTIFY_REDIRECT_URI: str = "http://127.0.0.1:8000/api/connectors/spotify/callback"

    GOOGLE_FIT_REDIRECT_URI: str = "http://localhost:8000/api/connectors/googlefit/callback"

    GEMINI_API_KEY: str = ""

    FRONTEND_URL: str = "http://localhost:5173"


settings = Settings()
