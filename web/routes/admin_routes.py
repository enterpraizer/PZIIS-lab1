"""Admin panel web routes."""

from __future__ import annotations

from functools import wraps

from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from models.article import Article
from models.base import Role
from models.question import Question
from models.user import User
from repositories.article_repository import ArticleRepository
from repositories.category_repository import CategoryRepository
from repositories.database import session_scope
from repositories.user_repository import UserRepository
from services.admin_service import AdminService
from services.article_service import ArticleService
from utils.exceptions import AppError


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(view_func):
    """Require admin role for web routes."""

    @wraps(view_func)
    @login_required
    def wrapper(*args, **kwargs):
        if current_user.role != Role.ADMIN:
            abort(403)
        return view_func(*args, **kwargs)

    return wrapper


@admin_bp.get("/")
@admin_required
def dashboard():
    """Admin dashboard with aggregate stats."""
    with session_scope() as session:
        stats = {
            "users": session.query(User).count(),
            "articles": session.query(Article).count(),
            "questions": session.query(Question).count(),
        }
    return render_template("admin/dashboard.html", stats=stats)


@admin_bp.get("/users")
@admin_required
def users():
    """List all users."""
    with session_scope() as session:
        user_list = UserRepository(session).list_all()
    return render_template("admin/users.html", users=user_list)


@admin_bp.post("/users/<int:user_id>/block")
@admin_required
def block_user(user_id: int):
    """Block selected user."""
    with session_scope() as session:
        service = AdminService(UserRepository(session))
        admin_user = UserRepository(session).get_by_id(current_user.id)
        try:
            if admin_user:
                service.block_user(admin_user, user_id)
                flash("Пользователь заблокирован", "success")
        except AppError as exc:
            flash(str(exc), "danger")
    return redirect(url_for("admin.users"))


@admin_bp.post("/users/<int:user_id>/unblock")
@admin_required
def unblock_user(user_id: int):
    """Unblock selected user."""
    with session_scope() as session:
        service = AdminService(UserRepository(session))
        admin_user = UserRepository(session).get_by_id(current_user.id)
        try:
            if admin_user:
                service.unblock_user(admin_user, user_id)
                flash("Пользователь разблокирован", "success")
        except AppError as exc:
            flash(str(exc), "danger")
    return redirect(url_for("admin.users"))


@admin_bp.post("/users/<int:user_id>/delete")
@admin_required
def delete_user(user_id: int):
    """Delete selected user."""
    with session_scope() as session:
        service = AdminService(UserRepository(session))
        admin_user = UserRepository(session).get_by_id(current_user.id)
        try:
            if admin_user:
                service.delete_user(admin_user, user_id)
                flash("Пользователь удален", "success")
        except AppError as exc:
            flash(str(exc), "danger")
    return redirect(url_for("admin.users"))


@admin_bp.get("/articles")
@admin_required
def articles():
    """List all articles for admin."""
    with session_scope() as session:
        service = ArticleService(ArticleRepository(session), CategoryRepository(session))
        article_list = service.list_articles()
    return render_template("admin/articles.html", articles=article_list)


@admin_bp.post("/articles/<int:article_id>/delete")
@admin_required
def delete_article(article_id: int):
    """Delete article as admin."""
    with session_scope() as session:
        service = ArticleService(ArticleRepository(session), CategoryRepository(session))
        admin_user = UserRepository(session).get_by_id(current_user.id)
        try:
            if admin_user:
                service.delete_article(admin_user, article_id)
                flash("Статья удалена", "success")
        except AppError as exc:
            flash(str(exc), "danger")
    return redirect(url_for("admin.articles"))
