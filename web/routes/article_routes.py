"""Article management web routes."""

from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from models.base import Role
from repositories.article_repository import ArticleRepository
from repositories.category_repository import CategoryRepository
from repositories.database import session_scope
from repositories.user_repository import UserRepository
from services.article_service import ArticleService
from utils.exceptions import AppError, AuthorizationError, NotFoundError


article_bp = Blueprint("articles", __name__, url_prefix="/articles")


@article_bp.get("/")
@login_required
def list_articles():
    """List articles with optional search and category filter."""
    query = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()

    with session_scope() as session:
        article_service = ArticleService(ArticleRepository(session), CategoryRepository(session))
        categories = article_service.list_categories()

        try:
            if query:
                articles = article_service.search_articles(query)
            elif category:
                articles = article_service.filter_articles_by_category(int(category))
            else:
                articles = article_service.list_articles()
        except (AppError, ValueError):
            flash("Некорректный фильтр или запрос", "danger")
            articles = article_service.list_articles()

    return render_template(
        "articles/list.html",
        articles=articles,
        categories=categories,
        selected_category=category,
        query=query,
    )


@article_bp.get("/<int:article_id>")
@login_required
def view_article(article_id: int):
    """View single article."""
    with session_scope() as session:
        article = ArticleRepository(session).get_by_id(article_id)
        if not article:
            flash("Статья не найдена", "danger")
            return redirect(url_for("articles.list_articles"))

    return render_template("articles/view.html", article=article)


@article_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_article():
    """Create article for consultant/admin."""
    if current_user.role not in {Role.CONSULTANT, Role.ADMIN}:
        flash("Недостаточно прав", "danger")
        return redirect(url_for("articles.list_articles"))

    with session_scope() as session:
        article_service = ArticleService(ArticleRepository(session), CategoryRepository(session))
        categories = article_service.list_categories()

        if request.method == "POST":
            try:
                category_id = int(request.form.get("category_id", "0"))
                current_db_user = UserRepository(session).get_by_id(current_user.id)
                if not current_db_user:
                    raise AuthorizationError("Пользователь не найден")

                article = article_service.create_article(
                    current_user=current_db_user,
                    title=request.form.get("title", ""),
                    content=request.form.get("content", ""),
                    category_id=category_id,
                )
                flash("Статья создана", "success")
                return redirect(url_for("articles.view_article", article_id=article.id))
            except (AppError, ValueError) as exc:
                flash(str(exc), "danger")

    return render_template("articles/create.html", categories=categories)


@article_bp.route("/<int:article_id>/edit", methods=["GET", "POST"])
@login_required
def edit_article(article_id: int):
    """Edit article for consultant/admin."""
    with session_scope() as session:
        article_service = ArticleService(ArticleRepository(session), CategoryRepository(session))
        current_db_user = UserRepository(session).get_by_id(current_user.id)
        article = ArticleRepository(session).get_by_id(article_id)
        categories = article_service.list_categories()

        if not article:
            flash("Статья не найдена", "danger")
            return redirect(url_for("articles.list_articles"))

        if request.method == "POST":
            try:
                if not current_db_user:
                    raise AuthorizationError("Пользователь не найден")

                article_service.update_article(
                    current_user=current_db_user,
                    article_id=article_id,
                    title=request.form.get("title", ""),
                    content=request.form.get("content", ""),
                    category_id=int(request.form.get("category_id", "0")),
                )
                flash("Статья обновлена", "success")
                return redirect(url_for("articles.view_article", article_id=article_id))
            except (AppError, ValueError) as exc:
                flash(str(exc), "danger")

    return render_template("articles/edit.html", article=article, categories=categories)


@article_bp.post("/<int:article_id>/delete")
@login_required
def delete_article(article_id: int):
    """Delete article for consultant/admin."""
    with session_scope() as session:
        article_service = ArticleService(ArticleRepository(session), CategoryRepository(session))
        current_db_user = UserRepository(session).get_by_id(current_user.id)

        try:
            if not current_db_user:
                raise AuthorizationError("Пользователь не найден")
            article_service.delete_article(current_user=current_db_user, article_id=article_id)
            flash("Статья удалена", "success")
        except (AppError, ValueError, NotFoundError) as exc:
            flash(str(exc), "danger")

    return redirect(url_for("articles.list_articles"))
