import os
from functools import lru_cache
from typing import List


class Settings:
    """
    Central configuration, read from environment variables (.env in
    development). Never commit real secrets — see .env.example.
    """

    PROJECT_NAME: str = "Fasal API"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql+psycopg2://fasal:fasal@localhost:5432/fasal"
    )
    # Used by tests / local quick-start without a running Postgres instance.
    TEST_DATABASE_URL: str = os.getenv("TEST_DATABASE_URL", "sqlite:///./test.db")

    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

    CORS_ORIGINS: List[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://localhost:3000,https://jamalgattu.github.io",
        ).split(",")
        if origin.strip()
    ]

    # Default weights for the supply-demand matching engine. Must sum to 1.0;
    # the engine normalizes them defensively if they don't.
    MATCH_WEIGHT_PRICE: float = float(os.getenv("MATCH_WEIGHT_PRICE", "0.25"))
    MATCH_WEIGHT_DISTANCE: float = float(os.getenv("MATCH_WEIGHT_DISTANCE", "0.20"))
    MATCH_WEIGHT_QUALITY: float = float(os.getenv("MATCH_WEIGHT_QUALITY", "0.20"))
    MATCH_WEIGHT_AVAILABILITY: float = float(os.getenv("MATCH_WEIGHT_AVAILABILITY", "0.20"))
    MATCH_WEIGHT_RELIABILITY: float = float(os.getenv("MATCH_WEIGHT_RELIABILITY", "0.15"))
    MATCH_MAX_DISTANCE_KM: float = float(os.getenv("MATCH_MAX_DISTANCE_KM", "300"))


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
