"""Application configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Config:
    """Runtime configuration loaded from environment variables."""

    database_url: str = os.getenv("DATABASE_URL", "sqlite:///business_help.db")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


config = Config()
