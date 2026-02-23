"""Articles API routes."""

from __future__ import annotations

from functools import wraps

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from models.user import User
from repositories.article_repository import ArticleRepository
from repositories.category_repository import CategoryRepository
from repositories.database import session_scope
from repositories.user_repository import UserRepository
from services.article_service import ArticleService
from utils.exceptions import AppError, AuthorizationError


articles_api_bp = Blueprint("articles_api", __name__)


def _article_to_dict(article) -> dict:
    return {
        "id": article.id,
        "title": article.title,
        "content": article.content,
        "category": article.category.name,
        "category_id": article.category_id,
        "author": article.author.username,
        "author_id": article.author_id,
        "created_at": article.created_at.isoformat(),
    }


def roles_required(*roles: str):
    """Require one of JWT role claims."""

    def decorator(func):
        @wraps(func)
        @jwt_required()
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            role = claims.get("role")
            if role not in roles:
                return jsonify({"error": "Forbidden"}), 403
            return func(*args, **kwargs)

        return wrapper

    return decorator


def _get_current_user(session) -> User:
    user_id = int(get_jwt_identity())
    user = UserRepository(session).get_by_id(user_id)
    if not user:
        raise AuthorizationError("User not found")
    return user


@articles_api_bp.get("/articles")
def list_articles():
    """List articles."""
    with session_scope() as session:
        service = ArticleService(ArticleRepository(session), CategoryRepository(session))
        return jsonify([_article_to_dict(a) for a in service.list_articles()])


@articles_api_bp.get("/articles/<int:article_id>")
def get_article(article_id: int):
    """Get article details."""
    with session_scope() as session:
        article = ArticleRepository(session).get_by_id(article_id)
        if not article:
            return jsonify({"error": "Article not found"}), 404
        return jsonify(_article_to_dict(article))


@articles_api_bp.post("/articles")
@roles_required("consultant", "admin")
def create_article():
    """Create article via API."""
    payload = request.get_json(silent=True) or {}
    with session_scope() as session:
        service = ArticleService(ArticleRepository(session), CategoryRepository(session))
        try:
            user = _get_current_user(session)
            article = service.create_article(
                current_user=user,
                title=payload.get("title", ""),
                content=payload.get("content", ""),
                category_id=int(payload.get("category_id", 0)),
            )
            article = ArticleRepository(session).get_by_id(article.id)
            return jsonify(_article_to_dict(article)), 201
        except (AppError, ValueError) as exc:
            return jsonify({"error": str(exc)}), 400


@articles_api_bp.put("/articles/<int:article_id>")
@roles_required("consultant", "admin")
def update_article(article_id: int):
    """Update article via API."""
    payload = request.get_json(silent=True) or {}
    with session_scope() as session:
        service = ArticleService(ArticleRepository(session), CategoryRepository(session))
        try:
            user = _get_current_user(session)
            article = service.update_article(
                current_user=user,
                article_id=article_id,
                title=payload.get("title", ""),
                content=payload.get("content", ""),
                category_id=int(payload.get("category_id", 0)),
            )
            article = ArticleRepository(session).get_by_id(article.id)
            return jsonify(_article_to_dict(article))
        except (AppError, ValueError) as exc:
            return jsonify({"error": str(exc)}), 400


@articles_api_bp.delete("/articles/<int:article_id>")
@roles_required("consultant", "admin")
def delete_article(article_id: int):
    """Delete article via API."""
    with session_scope() as session:
        service = ArticleService(ArticleRepository(session), CategoryRepository(session))
        try:
            user = _get_current_user(session)
            service.delete_article(current_user=user, article_id=article_id)
            return jsonify({"status": "deleted"})
        except AppError as exc:
            return jsonify({"error": str(exc)}), 400
