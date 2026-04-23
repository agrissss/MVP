"""Konfigurācijas noslāņošana — vides mainīgie ar saprātīgiem noklusējumiem."""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data.db")
    cors_origins: list[str] = None  # type: ignore[assignment]
    user_agent: str = os.getenv("USER_AGENT", "TiesibuAktuParluks/1.0 (+https://example.lv)")
    fetch_delay_sec: float = float(os.getenv("FETCH_DELAY_SEC", "2.0"))

    def __post_init__(self) -> None:
        raw = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")
        self.cors_origins = [o.strip() for o in raw.split(",") if o.strip()]


settings = Settings()
