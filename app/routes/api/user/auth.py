from flask import request, jsonify
from flask_security import auth_required, current_user
from flask_security.utils import hash_password

from app.extensions import db, security
from app.models import User
from app.routes.api.user import user_bp


def user_to_dict(user: User) -> dict:
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "active": user.active,
        "roles": [r.name for r in user.roles] if user.roles else []
    }


@user_bp.route("/profile", methods=["GET"])
@auth_required()
def get_profile():
    return jsonify(user_to_dict(current_user)), 200


@user_bp.route("/profile", methods=["PUT"])
@auth_required()
def update_profile():
    data = request.get_json() or {}

    if "name" in data and data["name"]:
        current_user.name = data["name"]

    if "email" in data and data["email"]:
        new_email = data["email"]
        if new_email != current_user.email:
            existing = security.datastore.find_user(email=new_email)
            if existing and existing.id != current_user.id:
                return jsonify({"error": "Email is already taken by another user."}), 400
            current_user.email = new_email

    if "password" in data and data["password"]:
        current_user.password = hash_password(data["password"])

    security.datastore.commit()

    return jsonify({
        "message": "Profile updated successfully",
        "user": user_to_dict(current_user)
    }), 200
