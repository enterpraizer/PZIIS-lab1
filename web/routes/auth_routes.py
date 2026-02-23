"""Authentication web routes."""

from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from models.base import Role
from repositories.database import session_scope
from repositories.user_repository import UserRepository
from services.auth_service import AuthService
from utils.exceptions import AppError


auth_bp = Blueprint("auth", __name__)


@auth_bp.get("/")
def index():
    """Public entrypoint."""
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """User login page."""
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        with session_scope() as session:
            auth_service = AuthService(UserRepository(session))
            try:
                user = auth_service.login(username=username, password=password)
                login_user(user)
                flash("Вход выполнен успешно", "success")
                return redirect(url_for("auth.dashboard"))
            except AppError as exc:
                flash(str(exc), "danger")

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """User registration page."""
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        role = request.form.get("role", Role.ENTREPRENEUR.value)

        with session_scope() as session:
            auth_service = AuthService(UserRepository(session))
            try:
                auth_service.register(username=username, password=password, role=role)
                flash("Регистрация успешна. Войдите в аккаунт.", "success")
                return redirect(url_for("auth.login"))
            except AppError as exc:
                flash(str(exc), "danger")

    return render_template("register.html")


@auth_bp.get("/dashboard")
@login_required
def dashboard():
    """Role-aware dashboard."""
    return render_template("dashboard.html")


@auth_bp.post("/logout")
@login_required
def logout():
    """Logout endpoint."""
    logout_user()
    flash("Вы вышли из системы", "info")
    return redirect(url_for("auth.login"))
