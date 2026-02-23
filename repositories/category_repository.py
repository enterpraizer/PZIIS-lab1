"""Category repository."""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from models.category import Category


class CategoryRepository:
    """Data access for categories."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def list_all(self) -> List[Category]:
        return self.session.query(Category).order_by(Category.name.asc()).all()

    def get_by_name(self, name: str) -> Optional[Category]:
        return self.session.query(Category).filter(Category.name == name).first()

    def get_by_id(self, category_id: int) -> Optional[Category]:
        return self.session.get(Category, category_id)
