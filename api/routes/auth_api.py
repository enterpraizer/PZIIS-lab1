"""Authentication API routes."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

from repositories.database import session_scope
from repositories.user_repository import UserRepository
from services.auth_service import AuthService
from utils.exceptions import AppError


auth_api_bp = Blueprint("auth_api", __name__)


@auth_api_bp.post("/register")
def register():
    """Register user via API."""
    payload = request.get_json(silent=True) or {}

    with session_scope() as session:
        service = AuthService(UserRepository(session))
        try:
            user = service.register(
                username=payload.get("username", ""),
                password=payload.get("password", ""),
                role=payload.get("role", "entrepreneur"),
            )
            return (
                jsonify(
                    {
                        "id": user.id,
                        "username": user.username,
                        "role": user.role.value,
                    }
                ),
                201,
            )
        except AppError as exc:
            return jsonify({"error": str(exc)}), 400


@auth_api_bp.post("/login")
def login():
    """Authenticate and return JWT."""
    payload = request.get_json(silent=True) or {}

    with session_scope() as session:
        service = AuthService(UserRepository(session))
        try:
            user = service.login(
                username=payload.get("username", ""),
                password=payload.get("password", ""),
            )
            token = create_access_token(
                identity=str(user.id),
                additional_claims={"role": user.role.value, "username": user.username},
            )
            return jsonify({"access_token": token})
        except AppError as exc:
            return jsonify({"error": str(exc)}), 401
