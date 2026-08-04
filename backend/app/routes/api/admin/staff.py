import enum
from flask import request, jsonify
from flask_security.utils import hash_password
from app.extensions import db, security
from app.models import User, StaffProfile, StaffStatus
from app.routes.api.admin import admin_bp


def staff_to_dict(staff: StaffProfile) -> dict:
    return {
        "id": staff.id,
        "user_id": staff.user_id,
        "name": staff.user.name,
        "email": staff.user.email,
        "username": getattr(staff.user, "username", None),
        "active": staff.user.active,
        "status": staff.status.value if isinstance(staff.status, enum.Enum) else str(staff.status),
        "assigned_treks": [
            {
                "id": t.id,
                "trek_name": t.trek_name,
                "location": t.location,
                "status": t.status.value if isinstance(t.status, enum.Enum) else str(t.status)
            } for t in staff.assigned_treks
        ] if staff.assigned_treks else []
    }


@admin_bp.route("/staff", methods=["GET"])
def list_staff():
    query = db.session.query(StaffProfile).join(User)

    status_param = request.args.get("status")
    if status_param:
        try:
            status_enum = StaffStatus(status_param.title())
            query = query.filter(StaffProfile.status == status_enum)
        except ValueError:
            pass

    search_param = request.args.get("search")
    if search_param:
        search_filter = f"%{search_param}%"
        query = query.filter(
            (User.name.ilike(search_filter)) | (User.email.ilike(search_filter))
        )

    staff_members = query.all()
    return jsonify([staff_to_dict(s) for s in staff_members]), 200


@admin_bp.route("/staff", methods=["POST"])
def add_staff():
    data = request.get_json() or {}

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    username = data.get("username")
    status_raw = data.get("status", StaffStatus.ACTIVE.value)

    if not name or not email or not password:
        return jsonify({"error": "name, email, and password are required fields."}), 400

    try:
        status = StaffStatus(status_raw.title())
    except ValueError:
        return jsonify({"error": f"Invalid staff status. Must be one of: {[e.value for e in StaffStatus]}"}), 400

    staff_role = security.datastore.find_or_create_role("staff")
    user = security.datastore.find_user(email=email)

    if user:
        if not security.datastore.has_role(user, "staff"):
            security.datastore.add_role_to_user(user, staff_role)
    else:
        hashed_pw = hash_password(password)
        user = security.datastore.create_user(
            name=name,
            email=email,
            password=hashed_pw,
            username=username
        )
        security.datastore.add_role_to_user(user, staff_role)

    if not user.staff_profile:
        staff_profile = StaffProfile(user=user, status=status)
        db.session.add(staff_profile)
    else:
        staff_profile = user.staff_profile
        staff_profile.status = status

    security.datastore.commit()

    return jsonify({"message": "Staff member created successfully", "staff": staff_to_dict(staff_profile)}), 201


@admin_bp.route("/staff/<int:staff_id>", methods=["GET"])
def get_staff(staff_id):
    staff = db.session.get(StaffProfile, staff_id)
    if not staff:
        return jsonify({"error": f"Staff member with id {staff_id} not found."}), 404

    return jsonify(staff_to_dict(staff)), 200


@admin_bp.route("/staff/<int:staff_id>", methods=["PUT"])
def update_staff(staff_id):
    staff = db.session.get(StaffProfile, staff_id)
    if not staff:
        return jsonify({"error": f"Staff member with id {staff_id} not found."}), 404

    data = request.get_json() or {}

    if "name" in data:
        staff.user.name = data["name"]
    if "email" in data:
        staff.user.email = data["email"]
    if "status" in data:
        try:
            staff.status = StaffStatus(data["status"].title())
        except ValueError:
            return jsonify({"error": f"Invalid staff status. Must be one of: {[e.value for e in StaffStatus]}"}), 400

    db.session.commit()
    return jsonify({"message": "Staff details updated successfully", "staff": staff_to_dict(staff)}), 200


@admin_bp.route("/staff/<int:staff_id>/status", methods=["PUT"])
def update_staff_status(staff_id):
    staff = db.session.get(StaffProfile, staff_id)
    if not staff:
        return jsonify({"error": f"Staff member with id {staff_id} not found."}), 404

    data = request.get_json() or {}
    status_raw = data.get("status")

    if status_raw:
        try:
            staff.status = StaffStatus(status_raw.title())
        except ValueError:
            return jsonify({"error": f"Invalid staff status. Must be one of: {[e.value for e in StaffStatus]}"}), 400

    if "active" in data:
        active_val = bool(data["active"])
        if active_val:
            security.datastore.activate_user(staff.user)
        else:
            security.datastore.deactivate_user(staff.user)

    security.datastore.commit()
    return jsonify({"message": "Staff status updated successfully", "staff": staff_to_dict(staff)}), 200
