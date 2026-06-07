from flask import Blueprint, jsonify, request

from models import Doctor, User, Appointment
from routes.common import serialize_doctor, parse_date, build_slots, get_schedule_for_doctor_on_date

public_doctor_bp = Blueprint("public_doctor_bp", __name__)


@public_doctor_bp.get("/doctors")
def get_active_doctors():
    specialization = request.args.get("specialization")
    name = request.args.get("name")

    query = Doctor.query.join(User).filter(Doctor.is_active == True)
    if specialization:
        query = query.filter(Doctor.specialization.ilike(f"%{specialization}%"))
    if name:
        query = query.filter(User.name.ilike(f"%{name}%"))

    doctors = query.order_by(User.name.asc()).all()
    return jsonify([serialize_doctor(doctor) for doctor in doctors]), 200


@public_doctor_bp.get("/doctors/<int:doctor_id>/availability")
def get_doctor_availability(doctor_id):
    doctor = Doctor.query.get(doctor_id)
    if not doctor or not doctor.is_active:
        return jsonify({"error": "Doctor not found"}), 404

    appointment_date = parse_date(request.args.get("date", ""))
    if not appointment_date:
        return jsonify({"error": "Valid date query param is required in YYYY-MM-DD format"}), 400

    schedules = get_schedule_for_doctor_on_date(doctor_id, appointment_date)
    slots = []
    for schedule in schedules:
        slots.extend(build_slots(schedule))

    booked = {
        appointment.appointment_time.strftime("%H:%M")
        for appointment in Appointment.query.filter_by(doctor_id=doctor_id, appointment_date=appointment_date).filter(Appointment.status != "cancelled").all()
    }

    all_slots_str = [slot.strftime("%H:%M") for slot in sorted(slots)]
    available_slots = [slot for slot in all_slots_str if slot not in booked]

    return jsonify({
        "doctor": serialize_doctor(doctor),
        "date": appointment_date.isoformat(),
        "available_slots": available_slots,  # Used by the booking dropdown
        "booked_slots": list(booked),        # NEW: Used by the visual roster
        "all_slots": all_slots_str           # NEW: Used by the visual roster
    }), 200
