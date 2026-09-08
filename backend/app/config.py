"""Configuration settings for AI Recruitment Agent."""
from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "AI Recruitment Agent"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    # LLM Settings
    LLM_PROVIDER: str = "gemini"  # "gemini", "openai", or "mock"
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Database
    DATABASE_URL: str = "sqlite:///./recruitment.db"

    # Agent Limits
    MAX_AGENT_STEPS: int = 12
    MAX_FILE_SIZE_MB: int = 10

    # Scoring Weights (Total 1.0)
    WEIGHT_SKILLS: float = 0.50
    WEIGHT_EXPERIENCE: float = 0.20
    WEIGHT_EDUCATION: float = 0.10
    WEIGHT_PREFERRED_SKILLS: float = 0.10
    WEIGHT_PROJECTS: float = 0.10

    # Match Thresholds
    THRESHOLD_STRONG_MATCH: int = 85
    THRESHOLD_MATCH: int = 70
    THRESHOLD_POTENTIAL_MATCH: int = 50

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ]


settings = Settings()
