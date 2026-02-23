"""Application entry point."""

from __future__ import annotations

import logging

from repositories.database import healthcheck, init_db
from ui.cli import CLI
from utils.logger import setup_logging


def main() -> None:
    """Initialize and run CLI application."""
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        init_db()
        healthcheck()
        logger.info("Database initialized successfully")
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to initialize database: %s", exc)
        raise SystemExit(1) from exc

    CLI().run()


if __name__ == "__main__":
    main()
