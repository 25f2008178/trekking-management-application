import enum
from flask import request, jsonify
from flask_security import current_user
from app.extensions import db
from app.models import Trek, TrekStatus, Booking, BookingStatus
from app.routes.api.staff import staff_bp


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
        "bookings_count": len(trek.bookings) if trek.bookings else 0
    }


def booking_to_dict(booking: Booking) -> dict:
    return {
        "booking_id": booking.id,
        "user_id": booking.user_id,
        "name": booking.user.name if booking.user else None,
        "email": booking.user.email if booking.user else None,
        "booking_date": booking.booking_date.isoformat() if booking.booking_date else None,
        "status": booking.status.value if isinstance(booking.status, enum.Enum) else str(booking.status)
    }


@staff_bp.route("/treks", methods=["GET"])
def list_assigned_treks():
    staff_profile_id = current_user.staff_profile.id
    query = db.session.query(Trek).filter(Trek.assigned_staff_id == staff_profile_id)

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


@staff_bp.route("/treks/<int:trek_id>", methods=["GET"])
def get_assigned_trek(trek_id):
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return jsonify({"error": f"Trek with id {trek_id} not found."}), 404

    if trek.assigned_staff_id != current_user.staff_profile.id:
        return jsonify({"error": "Forbidden. This trek is not assigned to you."}), 403

    return jsonify(trek_to_dict(trek)), 200


@staff_bp.route("/treks/<int:trek_id>", methods=["PUT"])
def update_assigned_trek(trek_id):
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return jsonify({"error": f"Trek with id {trek_id} not found."}), 404

    if trek.assigned_staff_id != current_user.staff_profile.id:
        return jsonify({"error": "Forbidden. This trek is not assigned to you."}), 403

    data = request.get_json() or {}

    if "available_slots" in data:
        try:
            slots = int(data["available_slots"])
            if slots < 0:
                return jsonify({"error": "available_slots cannot be negative."}), 400
            trek.available_slots = slots
        except (ValueError, TypeError):
            return jsonify({"error": "available_slots must be a valid integer."}), 400

    if "status" in data:
        raw_status = str(data["status"]).capitalize()
        allowed_statuses = [TrekStatus.OPEN, TrekStatus.CLOSED, TrekStatus.COMPLETED]
        try:
            status_enum = TrekStatus(raw_status)
            if status_enum not in allowed_statuses:
                return jsonify({
                    "error": f"Staff members can only set trek status to: {[s.value for s in allowed_statuses]}"
                }), 400
            trek.status = status_enum
        except ValueError:
            return jsonify({
                "error": f"Invalid trek status. Allowed values: {[s.value for s in allowed_statuses]}"
            }), 400

    db.session.commit()
    return jsonify({"message": "Trek details updated successfully", "trek": trek_to_dict(trek)}), 200


@staff_bp.route("/treks/<int:trek_id>/users", methods=["GET"])
def get_registered_users(trek_id):
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return jsonify({"error": f"Trek with id {trek_id} not found."}), 404

    if trek.assigned_staff_id != current_user.staff_profile.id:
        return jsonify({"error": "Forbidden. This trek is not assigned to you."}), 403

    registered_users = [booking_to_dict(b) for b in trek.bookings]
    return jsonify({
        "trek_id": trek.id,
        "trek_name": trek.trek_name,
        "total_registered": len(registered_users),
        "registered_users": registered_users
    }), 200


@staff_bp.route("/treks/<int:trek_id>/complete", methods=["PUT"])
def mark_trek_completed(trek_id):
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return jsonify({"error": f"Trek with id {trek_id} not found."}), 404

    if trek.assigned_staff_id != current_user.staff_profile.id:
        return jsonify({"error": "Forbidden. This trek is not assigned to you."}), 403

    trek.status = TrekStatus.COMPLETED

    for booking in trek.bookings:
        if booking.status == BookingStatus.BOOKED:
            booking.status = BookingStatus.COMPLETED

    db.session.commit()
    return jsonify({
        "message": "Trek marked as completed successfully",
        "trek": trek_to_dict(trek)
    }), 200
