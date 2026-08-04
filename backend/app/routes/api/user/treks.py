import enum
from flask import request, jsonify
from app.extensions import db
from app.models import Trek, TrekDifficulty, TrekStatus
from app.routes.api.user import user_bp


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
        "assigned_staff": {
            "id": trek.assigned_staff.id,
            "name": trek.assigned_staff.user.name,
        } if trek.assigned_staff and trek.assigned_staff.user else None
    }


@user_bp.route("/treks", methods=["GET"])
def list_treks():
    query = db.session.query(Trek).filter(
        Trek.status.in_([TrekStatus.APPROVED, TrekStatus.OPEN])
    )

    difficulty_param = request.args.get("difficulty")
    if difficulty_param:
        try:
            diff_enum = TrekDifficulty(difficulty_param.capitalize())
            query = query.filter(Trek.difficulty == diff_enum)
        except ValueError:
            pass

    location_param = request.args.get("location")
    if location_param:
        query = query.filter(Trek.location.ilike(f"%{location_param}%"))

    duration_param = request.args.get("duration")
    if duration_param:
        try:
            query = query.filter(Trek.duration == int(duration_param))
        except ValueError:
            pass

    min_duration = request.args.get("min_duration")
    if min_duration:
        try:
            query = query.filter(Trek.duration >= int(min_duration))
        except ValueError:
            pass

    max_duration = request.args.get("max_duration")
    if max_duration:
        try:
            query = query.filter(Trek.duration <= int(max_duration))
        except ValueError:
            pass

    search_param = request.args.get("search")
    if search_param:
        search_filter = f"%{search_param}%"
        query = query.filter(
            (Trek.trek_name.ilike(search_filter)) | (Trek.location.ilike(search_filter))
        )

    status_param = request.args.get("status")
    if status_param:
        try:
            status_enum = TrekStatus(status_param.capitalize())
            if status_enum in [TrekStatus.APPROVED, TrekStatus.OPEN]:
                query = query.filter(Trek.status == status_enum)
        except ValueError:
            pass

    treks = query.all()
    return jsonify([trek_to_dict(t) for t in treks]), 200


@user_bp.route("/treks/<int:trek_id>", methods=["GET"])
def get_trek(trek_id):
    trek = db.session.get(Trek, trek_id)
    if not trek or trek.status not in [TrekStatus.APPROVED, TrekStatus.OPEN]:
        return jsonify({"error": f"Trek with id {trek_id} not found or not available."}), 404

    return jsonify(trek_to_dict(trek)), 200
