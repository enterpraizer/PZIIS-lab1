"""Article business logic."""

from __future__ import annotations

import logging
from typing import List

from models.article import Article
from models.base import Role
from models.category import Category
from models.user import User
from repositories.article_repository import ArticleRepository
from repositories.category_repository import CategoryRepository
from utils.exceptions import AuthorizationError, NotFoundError
from utils.validators import validate_non_empty

logger = logging.getLogger(__name__)


class ArticleService:
    """Business operations for articles and categories."""

    def __init__(
        self,
        article_repository: ArticleRepository,
        category_repository: CategoryRepository,
    ) -> None:
        self.article_repository = article_repository
        self.category_repository = category_repository

    def list_articles(self) -> List[Article]:
        return self.article_repository.list_all()

    def list_categories(self) -> List[Category]:
        return self.category_repository.list_all()

    def filter_articles_by_category(self, category_id: int) -> List[Article]:
        category = self.category_repository.get_by_id(category_id)
        if not category:
            raise NotFoundError("Category not found")
        return self.article_repository.filter_by_category(category_id)

    def search_articles(self, query: str) -> List[Article]:
        clean_query = validate_non_empty(query, "Search query", max_length=200)
        return self.article_repository.search(clean_query)

    def create_article(
        self,
        current_user: User,
        title: str,
        content: str,
        category_id: int,
    ) -> Article:
        if current_user.role not in {Role.CONSULTANT, Role.ADMIN}:
            raise AuthorizationError("Only consultant or admin can create articles")

        category = self.category_repository.get_by_id(category_id)
        if not category:
            raise NotFoundError("Category not found")

        article = Article(
            title=validate_non_empty(title, "Title", max_length=200),
            content=validate_non_empty(content, "Content", max_length=10000),
            category_id=category.id,
            author_id=current_user.id,
        )
        created = self.article_repository.create(article)
        logger.info("Article id=%s created by '%s'", created.id, current_user.username)
        return created

    def update_article(
        self,
        current_user: User,
        article_id: int,
        title: str,
        content: str,
        category_id: int,
    ) -> Article:
        article = self.article_repository.get_by_id(article_id)
        if not article:
            raise NotFoundError("Article not found")

        if current_user.role not in {Role.CONSULTANT, Role.ADMIN}:
            raise AuthorizationError("Only consultant or admin can edit articles")

        if current_user.role == Role.CONSULTANT and article.author_id != current_user.id:
            raise AuthorizationError("Consultant can edit only own articles")

        category = self.category_repository.get_by_id(category_id)
        if not category:
            raise NotFoundError("Category not found")

        article.title = validate_non_empty(title, "Title", max_length=200)
        article.content = validate_non_empty(content, "Content", max_length=10000)
        article.category_id = category_id
        logger.info("Article id=%s updated by '%s'", article.id, current_user.username)
        return article

    def delete_article(self, current_user: User, article_id: int) -> None:
        article = self.article_repository.get_by_id(article_id)
        if not article:
            raise NotFoundError("Article not found")

        if current_user.role not in {Role.CONSULTANT, Role.ADMIN}:
            raise AuthorizationError("Only consultant or admin can delete articles")

        if current_user.role == Role.CONSULTANT and article.author_id != current_user.id:
            raise AuthorizationError("Consultant can delete only own articles")

        self.article_repository.delete(article)
        logger.info("Article id=%s deleted by '%s'", article.id, current_user.username)
