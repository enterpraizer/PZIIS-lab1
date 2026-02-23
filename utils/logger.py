"""Logging configuration."""

from __future__ import annotations

import logging

from utils.config import config


def setup_logging() -> None:
    """Configure root logging for the application."""
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
