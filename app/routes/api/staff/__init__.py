from flask import Blueprint, jsonify
from flask_security import auth_required, roles_accepted, current_user

staff_bp = Blueprint("staff", __name__)


@staff_bp.before_request
@auth_required()
@roles_accepted("staff")
def check_staff_access():
    if not hasattr(current_user, "staff_profile") or current_user.staff_profile is None:
        return jsonify({"error": "Access denied. No active staff profile found."}), 403

