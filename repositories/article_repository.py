"""Article repository."""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from models.article import Article


class ArticleRepository:
    """Data access for articles."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, article: Article) -> Article:
        self.session.add(article)
        self.session.flush()
        return article

    def get_by_id(self, article_id: int) -> Optional[Article]:
        return (
            self.session.query(Article)
            .options(joinedload(Article.author), joinedload(Article.category))
            .filter(Article.id == article_id)
            .first()
        )

    def list_all(self) -> List[Article]:
        return (
            self.session.query(Article)
            .options(joinedload(Article.author), joinedload(Article.category))
            .order_by(Article.created_at.desc())
            .all()
        )

    def filter_by_category(self, category_id: int) -> List[Article]:
        return (
            self.session.query(Article)
            .options(joinedload(Article.author), joinedload(Article.category))
            .filter(Article.category_id == category_id)
            .order_by(Article.created_at.desc())
            .all()
        )

    def search(self, query: str) -> List[Article]:
        q = f"%{query.lower()}%"
        return (
            self.session.query(Article)
            .options(joinedload(Article.author), joinedload(Article.category))
            .filter(
                or_(
                    Article.title.ilike(q),
                    Article.content.ilike(q),
                )
            )
            .order_by(Article.created_at.desc())
            .all()
        )

    def delete(self, article: Article) -> None:
        self.session.delete(article)
