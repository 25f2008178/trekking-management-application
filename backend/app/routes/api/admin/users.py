import enum
from flask import request, jsonify
from app.extensions import db, security
from app.models import User, Role
from app.routes.api.admin import admin_bp


def user_to_dict(user: User) -> dict:
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "username": getattr(user, "username", None),
        "active": user.active,
        "roles": [r.name for r in user.roles] if user.roles else [],
        "is_staff": user.staff_profile is not None,
        "staff_status": user.staff_profile.status.value if user.staff_profile and isinstance(user.staff_profile.status, enum.Enum) else (str(user.staff_profile.status) if user.staff_profile else None),
        "bookings_count": len(user.bookings) if user.bookings else 0
    }


@admin_bp.route("/users", methods=["GET"])
def list_users():
    query = db.session.query(User)

    role_param = request.args.get("role")
    if role_param:
        if role_param.lower() != "all":
            query = query.filter(User.roles.any(Role.name == role_param.lower()))
    else:
        query = query.filter(User.roles.any(Role.name == "user"))

    active_param = request.args.get("active")
    if active_param is not None:
        if active_param.lower() in ["true", "1"]:
            query = query.filter(User.active == True)
        elif active_param.lower() in ["false", "0"]:
            query = query.filter(User.active == False)

    search_param = request.args.get("search")
    if search_param:
        search_filter = f"%{search_param}%"
        query = query.filter(
            (User.name.ilike(search_filter)) | (User.email.ilike(search_filter))
        )

    users = query.all()
    return jsonify([user_to_dict(u) for u in users]), 200


@admin_bp.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": f"User with id {user_id} not found."}), 404

    return jsonify(user_to_dict(user)), 200


@admin_bp.route("/users/<int:user_id>/status", methods=["PUT"])
def update_user_status(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": f"User with id {user_id} not found."}), 404

    data = request.get_json() or {}

    if "active" in data:
        active_val = bool(data["active"])
        if active_val:
            security.datastore.activate_user(user)
        else:
            security.datastore.deactivate_user(user)

    if "roles" in data and isinstance(data["roles"], list):
        current_roles = list(user.roles)
        for role_obj in current_roles:
            security.datastore.remove_role_from_user(user, role_obj)
        for role_name in data["roles"]:
            role_obj = security.datastore.find_or_create_role(role_name)
            security.datastore.add_role_to_user(user, role_obj)

    security.datastore.commit()
    return jsonify({
        "message": f"User {user_id} status updated successfully",
        "user": user_to_dict(user)
    }), 200
