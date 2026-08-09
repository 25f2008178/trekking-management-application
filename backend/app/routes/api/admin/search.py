from sqlalchemy import cast, String
from flask import request, jsonify
from app.extensions import db
from app.models import User, Role, StaffProfile, Trek
from app.routes.api.admin import admin_bp
from app.routes.api.admin.users import user_to_dict
from app.routes.api.admin.staff import staff_to_dict
from app.routes.api.admin.treks import trek_to_dict


@admin_bp.route("/search_users", methods=["GET"])
def search_users():
    query_str = request.args.get("q", "").strip()
    if not query_str:
        return jsonify([]), 200

    search_filter = f"%{query_str}%"
    matching_users = db.session.query(User).filter(
        User.roles.any(Role.name == "user"),
        (User.name.ilike(search_filter)) | (User.email.ilike(search_filter))
    ).all()

    return jsonify([user_to_dict(u) for u in matching_users]), 200


@admin_bp.route("/search_staff", methods=["GET"])
def search_staff():
    query_str = request.args.get("q", "").strip()
    if not query_str:
        return jsonify([]), 200

    search_filter = f"%{query_str}%"
    matching_staff = db.session.query(StaffProfile).join(User).filter(
        (User.name.ilike(search_filter)) | (User.email.ilike(search_filter))
    ).all()

    return jsonify([staff_to_dict(s) for s in matching_staff]), 200


@admin_bp.route("/search_treks", methods=["GET"])
def search_treks():
    query_str = request.args.get("q", "").strip()
    if not query_str:
        return jsonify([]), 200

    clean_search = query_str.lstrip("#")
    search_filter = f"%{clean_search}%"
    matching_treks = db.session.query(Trek).filter(
        (Trek.trek_name.ilike(search_filter))
        | (Trek.location.ilike(search_filter))
        | (cast(Trek.id, String).ilike(search_filter))
    ).all()

    return jsonify([trek_to_dict(t) for t in matching_treks]), 200
