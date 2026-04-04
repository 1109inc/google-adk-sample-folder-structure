"""
File: app/core/config.py
Purpose: Centralized application configuration.

What this file does:
- Defines strongly-typed settings for the app
- Reads values from environment variables and .env
- Exposes one shared `settings` object to the rest of the codebase
- Mirrors selected API keys into os.environ for SDKs that expect them there
"""

import os
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Basic application metadata.
    APP_NAME: str = "My FastAPI App"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # Frontend origins allowed by the browser through CORS.
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # Main relational database used by the FastAPI app itself.
    DATABASE_URL: str

    # Separate database URL used by the ADK session service.
    SESSION_DB_URL: str

    # Security and AI provider credentials.
    SECRET_KEY: str
    GOOGLE_API_KEY: str
    OPENAI_API_KEY: str
    GPT5_NANO_API_KEY: str
    GEMINI_2_5_FLASH_LITE_API_KEY: str
    ANTHROPIC_API_KEY: str
    GROK_API_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        # Load local environment variables from a .env file in the project root.
        env_file = ".env"


# Create one settings object that the app imports everywhere.
settings = Settings()

# Some SDKs read credentials only from os.environ, so we mirror values there
# after pydantic has loaded them from the environment/.env file.
os.environ.setdefault("GOOGLE_API_KEY", settings.GOOGLE_API_KEY)
os.environ.setdefault("GEMINI_2_5_FLASH_LITE_API_KEY", settings.GEMINI_2_5_FLASH_LITE_API_KEY)
os.environ.setdefault("OPENAI_API_KEY", settings.OPENAI_API_KEY)
os.environ.setdefault("ANTHROPIC_API_KEY", settings.ANTHROPIC_API_KEY)
os.environ.setdefault("GROK_API_KEY", settings.GROK_API_KEY)
