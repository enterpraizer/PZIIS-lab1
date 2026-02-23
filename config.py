"""Application configuration for Flask web and API apps."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class BaseConfig:
    """Base runtime configuration."""

    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change-me-too")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///business_help.db")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


class WebConfig:
    """Flask Web configuration."""

    SECRET_KEY = BaseConfig.SECRET_KEY
    SQLALCHEMY_DATABASE_URI = BaseConfig.DATABASE_URL
    LOG_LEVEL = BaseConfig.LOG_LEVEL


class ApiConfig:
    """Flask API configuration."""

    SECRET_KEY = BaseConfig.SECRET_KEY
    JWT_SECRET_KEY = BaseConfig.JWT_SECRET_KEY
    SQLALCHEMY_DATABASE_URI = BaseConfig.DATABASE_URL
    LOG_LEVEL = BaseConfig.LOG_LEVEL
