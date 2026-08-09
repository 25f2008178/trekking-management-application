import enum
from flask import request, jsonify
from flask_security import auth_required, current_user

from app.cache import invalidate_cache_pattern
from app.extensions import db
from app.models import Booking, BookingStatus, Trek, TrekStatus
from app.routes.api.user import user_bp


def booking_to_dict(booking: Booking) -> dict:
    return {
        "id": booking.id,
        "user_id": booking.user_id,
        "trek_id": booking.trek_id,
        "booking_date": booking.booking_date.isoformat() if booking.booking_date else None,
        "status": booking.status.value if isinstance(booking.status, enum.Enum) else str(booking.status),
        "trek": {
            "id": booking.trek.id,
            "trek_name": booking.trek.trek_name,
            "location": booking.trek.location,
            "difficulty": booking.trek.difficulty.value if isinstance(booking.trek.difficulty, enum.Enum) else str(booking.trek.difficulty),
            "duration": booking.trek.duration,
            "available_slots": booking.trek.available_slots,
            "status": booking.trek.status.value if isinstance(booking.trek.status, enum.Enum) else str(booking.trek.status),
            "start_date": booking.trek.start_date.isoformat() if booking.trek.start_date else None,
            "end_date": booking.trek.end_date.isoformat() if booking.trek.end_date else None,
        } if booking.trek else None
    }


@user_bp.route("/bookings", methods=["POST"])
@auth_required()
def create_booking():
    data = request.get_json() or {}
    trek_id = data.get("trek_id")

    if not trek_id:
        return jsonify({"error": "trek_id is required to create a booking."}), 400

    trek = db.session.get(Trek, trek_id)
    if not trek or trek.status != TrekStatus.OPEN:
        return jsonify({"error": "Bookings can only be created for treks with status Open."}), 400

    if trek.available_slots <= 0:
        return jsonify({"error": "No available slots left for this trek."}), 400

    existing_active = db.session.query(Booking).filter(
        Booking.user_id == current_user.id,
        Booking.trek_id == trek.id,
        Booking.status == BookingStatus.BOOKED
    ).first()

    if existing_active:
        return jsonify({"error": "You already have an active booking for this trek."}), 400

    booking = Booking(
        user_id=current_user.id,
        trek_id=trek.id,
        status=BookingStatus.BOOKED
    )
    trek.available_slots -= 1

    db.session.add(booking)
    db.session.commit()

    invalidate_cache_pattern("treks:*")

    return jsonify({
        "message": "Trek booked successfully",
        "booking": booking_to_dict(booking)
    }), 201


@user_bp.route("/bookings", methods=["GET"])
@auth_required()
def list_bookings():
    query = db.session.query(Booking).filter(Booking.user_id == current_user.id)

    status_param = request.args.get("status")
    if status_param:
        try:
            status_enum = BookingStatus(status_param.capitalize())
            query = query.filter(Booking.status == status_enum)
        except ValueError:
            pass

    bookings = query.order_by(Booking.booking_date.desc()).all()
    return jsonify([booking_to_dict(b) for b in bookings]), 200


@user_bp.route("/bookings/<int:booking_id>", methods=["GET"])
@auth_required()
def get_booking(booking_id):
    booking = db.session.get(Booking, booking_id)
    if not booking or booking.user_id != current_user.id:
        return jsonify({"error": f"Booking with id {booking_id} not found."}), 404

    return jsonify(booking_to_dict(booking)), 200


@user_bp.route("/bookings/<int:booking_id>/cancel", methods=["PUT", "POST"])
@auth_required()
def cancel_booking(booking_id):
    booking = db.session.get(Booking, booking_id)
    if not booking or booking.user_id != current_user.id:
        return jsonify({"error": f"Booking with id {booking_id} not found."}), 404

    if booking.status == BookingStatus.CANCELLED:
        return jsonify({"error": "Booking is already cancelled."}), 400

    if booking.status == BookingStatus.COMPLETED:
        return jsonify({"error": "Cannot cancel a completed trek booking."}), 400

    booking.status = BookingStatus.CANCELLED

    if booking.trek:
        booking.trek.available_slots += 1

    db.session.commit()

    invalidate_cache_pattern("treks:*")

    return jsonify({
        "message": "Booking cancelled successfully",
        "booking": booking_to_dict(booking)
    }), 200
