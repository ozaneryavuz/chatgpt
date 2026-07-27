from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str
    token_secret: str
    token_ttl_seconds: int
    allowed_origins: tuple[str, ...]


def load_settings() -> Settings:
    origins = tuple(
        item.strip()
        for item in os.getenv("ALO186_ALLOWED_ORIGINS", "http://localhost:8000").split(",")
        if item.strip()
    )
    return Settings(
        database_url=os.getenv("ALO186_DATABASE_URL", "sqlite:///./alo186_continuity.db"),
        token_secret=os.getenv(
            "ALO186_TOKEN_SECRET",
            "development-only-secret-change-before-production",
        ),
        token_ttl_seconds=int(os.getenv("ALO186_TOKEN_TTL_SECONDS", "28800")),
        allowed_origins=origins,
    )


settings = load_settings()
