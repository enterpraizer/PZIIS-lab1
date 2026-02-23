"""REST API entrypoint."""

from __future__ import annotations

import logging

from flask import Flask, jsonify
from flask_jwt_extended import JWTManager

from api.routes.articles_api import articles_api_bp
from api.routes.auth_api import auth_api_bp
from api.routes.questions_api import questions_api_bp
from config import ApiConfig
from repositories.database import init_db


jwt = JWTManager()


def create_app() -> Flask:
    """Create API Flask app."""
    app = Flask(__name__)
    app.config.from_object(ApiConfig)

    _setup_logging(app)
    init_db()

    jwt.init_app(app)

    app.register_blueprint(auth_api_bp, url_prefix="/api")
    app.register_blueprint(articles_api_bp, url_prefix="/api")
    app.register_blueprint(questions_api_bp, url_prefix="/api")

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    return app


def _setup_logging(app: Flask) -> None:
    """Configure logging for API app."""
    level = getattr(logging, app.config.get("LOG_LEVEL", "INFO").upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5001)
