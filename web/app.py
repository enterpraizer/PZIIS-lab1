"""Flask web GUI application."""

from __future__ import annotations

import logging

from flask import Flask, render_template
from flask_login import current_user

from config import WebConfig
from repositories.database import init_db, session_scope
from repositories.user_repository import UserRepository
from web.extensions import login_manager
from web.routes.admin_routes import admin_bp
from web.routes.article_routes import article_bp
from web.routes.auth_routes import auth_bp
from web.routes.question_routes import question_bp


def create_app() -> Flask:
    """Application factory for web UI."""
    app = Flask(__name__, template_folder="templates", static_folder="../static")
    app.config.from_object(WebConfig)

    _setup_logging(app)
    init_db()

    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id: str):
        with session_scope() as session:
            user = UserRepository(session).get_by_id(int(user_id))
            if user and user.is_blocked:
                return None
            return user

    app.register_blueprint(auth_bp)
    app.register_blueprint(article_bp)
    app.register_blueprint(question_bp)
    app.register_blueprint(admin_bp)

    @app.context_processor
    def inject_globals():
        return {"current_role": getattr(current_user, "role", None)}

    @app.errorhandler(403)
    def forbidden(_):
        return render_template("base.html", content="Доступ запрещен"), 403

    return app


def _setup_logging(app: Flask) -> None:
    """Configure Flask app logger."""
    level = getattr(logging, app.config.get("LOG_LEVEL", "INFO").upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
