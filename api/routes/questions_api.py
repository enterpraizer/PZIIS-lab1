"""Questions API routes."""

from __future__ import annotations

from functools import wraps

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from models.user import User
from repositories.database import session_scope
from repositories.question_repository import QuestionRepository
from repositories.user_repository import UserRepository
from services.qa_service import QAService
from utils.exceptions import AppError, AuthorizationError


questions_api_bp = Blueprint("questions_api", __name__)


def _question_to_dict(question) -> dict:
    return {
        "id": question.id,
        "text": question.text,
        "author": question.author.username,
        "author_id": question.author_id,
        "created_at": question.created_at.isoformat(),
        "answers": [
            {
                "id": answer.id,
                "text": answer.text,
                "author": answer.author.username,
                "author_id": answer.author_id,
                "created_at": answer.created_at.isoformat(),
            }
            for answer in question.answers
        ],
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


@questions_api_bp.get("/questions")
def list_questions():
    """List all questions."""
    with session_scope() as session:
        service = QAService(QuestionRepository(session))
        return jsonify([_question_to_dict(q) for q in service.list_questions()])


@questions_api_bp.post("/questions")
@roles_required("entrepreneur", "admin")
def create_question():
    """Create question via API."""
    payload = request.get_json(silent=True) or {}
    with session_scope() as session:
        service = QAService(QuestionRepository(session))
        try:
            user = _get_current_user(session)
            question = service.ask_question(
                current_user=user,
                text=payload.get("text", ""),
            )
            question = QuestionRepository(session).get_question(question.id)
            return jsonify(_question_to_dict(question)), 201
        except AppError as exc:
            return jsonify({"error": str(exc)}), 400
