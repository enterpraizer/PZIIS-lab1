"""Q&A business logic."""

from __future__ import annotations

import logging
from typing import List

from models.base import Role
from models.question import Answer, Question
from models.user import User
from repositories.question_repository import QuestionRepository
from utils.exceptions import AuthorizationError, NotFoundError
from utils.validators import validate_non_empty

logger = logging.getLogger(__name__)


class QAService:
    """Business operations for questions and answers."""

    def __init__(self, question_repository: QuestionRepository) -> None:
        self.question_repository = question_repository

    def ask_question(self, current_user: User, text: str) -> Question:
        if current_user.role not in {Role.ENTREPRENEUR, Role.ADMIN}:
            raise AuthorizationError("Only entrepreneur or admin can ask questions")

        question = Question(
            text=validate_non_empty(text, "Question", max_length=5000),
            author_id=current_user.id,
        )
        created = self.question_repository.create_question(question)
        logger.info("Question id=%s created by '%s'", created.id, current_user.username)
        return created

    def list_questions(self) -> List[Question]:
        return self.question_repository.list_questions()

    def answer_question(self, current_user: User, question_id: int, text: str) -> Answer:
        if current_user.role not in {Role.CONSULTANT, Role.ADMIN}:
            raise AuthorizationError("Only consultant or admin can answer questions")

        question = self.question_repository.get_question(question_id)
        if not question:
            raise NotFoundError("Question not found")

        answer = Answer(
            text=validate_non_empty(text, "Answer", max_length=5000),
            question_id=question.id,
            author_id=current_user.id,
        )
        created = self.question_repository.create_answer(answer)
        logger.info(
            "Answer id=%s for question id=%s created by '%s'",
            created.id,
            question.id,
            current_user.username,
        )
        return created
