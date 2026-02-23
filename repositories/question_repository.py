"""Question and answer repository."""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from models.question import Answer, Question


class QuestionRepository:
    """Data access for questions and answers."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create_question(self, question: Question) -> Question:
        self.session.add(question)
        self.session.flush()
        return question

    def list_questions(self) -> List[Question]:
        return (
            self.session.query(Question)
            .options(
                joinedload(Question.author),
                joinedload(Question.answers).joinedload(Answer.author),
            )
            .order_by(Question.created_at.desc())
            .all()
        )

    def get_question(self, question_id: int) -> Optional[Question]:
        return (
            self.session.query(Question)
            .options(
                joinedload(Question.author),
                joinedload(Question.answers).joinedload(Answer.author),
            )
            .filter(Question.id == question_id)
            .first()
        )

    def create_answer(self, answer: Answer) -> Answer:
        self.session.add(answer)
        self.session.flush()
        return answer
