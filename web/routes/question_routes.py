"""Question routes."""

from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from models.base import Role
from repositories.database import session_scope
from repositories.question_repository import QuestionRepository
from repositories.user_repository import UserRepository
from services.qa_service import QAService
from utils.exceptions import AppError, AuthorizationError


question_bp = Blueprint("questions", __name__, url_prefix="/questions")


@question_bp.get("/")
@login_required
def list_questions():
    """List all questions."""
    with session_scope() as session:
        questions = QAService(QuestionRepository(session)).list_questions()
    return render_template("questions/list.html", questions=questions)


@question_bp.route("/create", methods=["POST"])
@login_required
def create_question():
    """Create question by entrepreneur/admin."""
    with session_scope() as session:
        service = QAService(QuestionRepository(session))
        current_db_user = UserRepository(session).get_by_id(current_user.id)

        try:
            if not current_db_user:
                raise AuthorizationError("Пользователь не найден")
            question = service.ask_question(
                current_user=current_db_user,
                text=request.form.get("text", ""),
            )
            flash(f"Вопрос создан (ID: {question.id})", "success")
        except AppError as exc:
            flash(str(exc), "danger")

    return redirect(url_for("questions.list_questions"))


@question_bp.get("/<int:question_id>")
@login_required
def view_question(question_id: int):
    """View question details and answers."""
    with session_scope() as session:
        question = QuestionRepository(session).get_question(question_id)
        if not question:
            flash("Вопрос не найден", "danger")
            return redirect(url_for("questions.list_questions"))

    return render_template("questions/view.html", question=question)


@question_bp.post("/<int:question_id>/answer")
@login_required
def answer_question(question_id: int):
    """Answer question by consultant/admin."""
    if current_user.role not in {Role.CONSULTANT, Role.ADMIN}:
        flash("Недостаточно прав", "danger")
        return redirect(url_for("questions.view_question", question_id=question_id))

    with session_scope() as session:
        service = QAService(QuestionRepository(session))
        current_db_user = UserRepository(session).get_by_id(current_user.id)
        try:
            if not current_db_user:
                raise AuthorizationError("Пользователь не найден")
            service.answer_question(
                current_user=current_db_user,
                question_id=question_id,
                text=request.form.get("text", ""),
            )
            flash("Ответ добавлен", "success")
        except AppError as exc:
            flash(str(exc), "danger")

    return redirect(url_for("questions.view_question", question_id=question_id))
