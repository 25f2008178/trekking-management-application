import enum
from datetime import datetime
from flask import request, jsonify
from app.extensions import db
from app.models import Trek, TrekDifficulty, TrekStatus, StaffProfile
from app.routes.api.admin import admin_bp


def parse_iso_datetime(dt_str):
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except ValueError:
        return None


def trek_to_dict(trek: Trek) -> dict:
    return {
        "id": trek.id,
        "trek_name": trek.trek_name,
        "location": trek.location,
        "difficulty": trek.difficulty.value if isinstance(trek.difficulty, enum.Enum) else str(trek.difficulty),
        "duration": trek.duration,
        "available_slots": trek.available_slots,
        "status": trek.status.value if isinstance(trek.status, enum.Enum) else str(trek.status),
        "start_date": trek.start_date.isoformat() if trek.start_date else None,
        "end_date": trek.end_date.isoformat() if trek.end_date else None,
        "assigned_staff_id": trek.assigned_staff_id,
        "assigned_staff": {
            "id": trek.assigned_staff.id,
            "user_id": trek.assigned_staff.user_id,
            "name": trek.assigned_staff.user.name,
            "email": trek.assigned_staff.user.email,
            "status": trek.assigned_staff.status.value if isinstance(trek.assigned_staff.status, enum.Enum) else str(trek.assigned_staff.status)
        } if trek.assigned_staff else None,
        "bookings_count": len(trek.bookings) if trek.bookings else 0
    }


@admin_bp.route("/treks", methods=["GET"])
def list_treks():
    query = db.session.query(Trek)

    difficulty_param = request.args.get("difficulty")
    if difficulty_param:
        try:
            diff_enum = TrekDifficulty(difficulty_param.capitalize())
            query = query.filter(Trek.difficulty == diff_enum)
        except ValueError:
            pass

    status_param = request.args.get("status")
    if status_param:
        try:
            status_enum = TrekStatus(status_param.capitalize())
            query = query.filter(Trek.status == status_enum)
        except ValueError:
            pass

    search_param = request.args.get("search")
    if search_param:
        search_filter = f"%{search_param}%"
        query = query.filter(
            (Trek.trek_name.ilike(search_filter)) | (Trek.location.ilike(search_filter))
        )

    treks = query.all()
    return jsonify([trek_to_dict(t) for t in treks]), 200


@admin_bp.route("/treks", methods=["POST"])
def create_trek():
    data = request.get_json() or {}

    trek_name = data.get("trek_name")
    location = data.get("location")
    difficulty_raw = data.get("difficulty")
    duration = data.get("duration")

    if not trek_name or not location or not difficulty_raw or duration is None:
        return jsonify({"error": "trek_name, location, difficulty, and duration are required fields."}), 400

    try:
        difficulty = TrekDifficulty(difficulty_raw.capitalize())
    except ValueError:
        return jsonify({"error": f"Invalid difficulty level. Must be one of: {[e.value for e in TrekDifficulty]}"}), 400

    status_raw = data.get("status", TrekStatus.PENDING.value)
    try:
        status = TrekStatus(status_raw.capitalize())
    except ValueError:
        return jsonify({"error": f"Invalid status. Must be one of: {[e.value for e in TrekStatus]}"}), 400

    assigned_staff_id = data.get("assigned_staff_id")
    if assigned_staff_id:
        staff = db.session.get(StaffProfile, assigned_staff_id)
        if not staff:
            return jsonify({"error": f"StaffProfile with id {assigned_staff_id} not found."}), 404

    trek = Trek(
        trek_name=trek_name,
        location=location,
        difficulty=difficulty,
        duration=int(duration),
        available_slots=int(data.get("available_slots", 0)),
        status=status,
        start_date=parse_iso_datetime(data.get("start_date")),
        end_date=parse_iso_datetime(data.get("end_date")),
        assigned_staff_id=assigned_staff_id
    )

    db.session.add(trek)
    db.session.commit()

    return jsonify({"message": "Trek route created successfully", "trek": trek_to_dict(trek)}), 201


@admin_bp.route("/treks/<int:trek_id>", methods=["GET"])
def get_trek(trek_id):
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return jsonify({"error": f"Trek with id {trek_id} not found."}), 404

    return jsonify(trek_to_dict(trek)), 200


@admin_bp.route("/treks/<int:trek_id>", methods=["PUT"])
def update_trek(trek_id):
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return jsonify({"error": f"Trek with id {trek_id} not found."}), 404

    data = request.get_json() or {}

    if "trek_name" in data:
        trek.trek_name = data["trek_name"]
    if "location" in data:
        trek.location = data["location"]
    if "difficulty" in data:
        try:
            trek.difficulty = TrekDifficulty(data["difficulty"].capitalize())
        except ValueError:
            return jsonify({"error": f"Invalid difficulty. Must be one of: {[e.value for e in TrekDifficulty]}"}), 400
    if "duration" in data:
        trek.duration = int(data["duration"])
    if "available_slots" in data:
        trek.available_slots = int(data["available_slots"])
    if "status" in data:
        try:
            trek.status = TrekStatus(data["status"].capitalize())
        except ValueError:
            return jsonify({"error": f"Invalid status. Must be one of: {[e.value for e in TrekStatus]}"}), 400
    if "start_date" in data:
        trek.start_date = parse_iso_datetime(data["start_date"])
    if "end_date" in data:
        trek.end_date = parse_iso_datetime(data["end_date"])
    if "assigned_staff_id" in data:
        staff_id = data["assigned_staff_id"]
        if staff_id is not None:
            staff = db.session.get(StaffProfile, staff_id)
            if not staff:
                return jsonify({"error": f"StaffProfile with id {staff_id} not found."}), 404
        trek.assigned_staff_id = staff_id

    db.session.commit()
    return jsonify({"message": "Trek route updated successfully", "trek": trek_to_dict(trek)}), 200


@admin_bp.route("/treks/<int:trek_id>", methods=["DELETE"])
def delete_trek(trek_id):
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return jsonify({"error": f"Trek with id {trek_id} not found."}), 404

    db.session.delete(trek)
    db.session.commit()
    return jsonify({"message": f"Trek route {trek_id} removed successfully."}), 200


@admin_bp.route("/treks/<int:trek_id>/assign", methods=["PUT"])
def assign_staff_to_trek(trek_id):
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return jsonify({"error": f"Trek with id {trek_id} not found."}), 404

    data = request.get_json() or {}
    staff_id = data.get("staff_id")

    if staff_id is not None:
        staff = db.session.get(StaffProfile, staff_id)
        if not staff:
            return jsonify({"error": f"StaffProfile with id {staff_id} not found."}), 404
        trek.assigned_staff_id = staff.id
    else:
        trek.assigned_staff_id = None

    db.session.commit()
    return jsonify({"message": "Staff assignment updated successfully", "trek": trek_to_dict(trek)}), 200
