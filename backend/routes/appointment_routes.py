from flask import Blueprint, jsonify, request
from datetime import time 
from flask_jwt_extended import get_jwt_identity # Make sure this is imported
from models import db, User, Doctor, Appointment, Patient
from routes.common import (
    role_required,
    get_current_patient,
    parse_date,
    parse_time,
    serialize_appointment,
    get_schedule_for_doctor_on_date,
    schedule_contains_time,
)

appointment_bp = Blueprint("appointment_bp", __name__)


@appointment_bp.post("/appointments/book")
@role_required("patient", "admin")
def book_appointment():
    data = request.get_json() or {}
    
    # 1. Identity Check
    user_id = get_jwt_identity() 
    current_user = User.query.get(user_id) # Gets the token info of whoever is logged in
    
    if current_user and current_user.role == "admin":
        patient_id = data.get("patient_id")
        patient = Patient.query.get(patient_id)
    else:
        patient = get_current_patient()

    if not patient:
        return jsonify({"error": "Patient profile not found"}), 404
    
    doctor_id = data.get("doctor_id")
    appointment_date = parse_date(data.get("appointment_date", ""))
    appointment_time = parse_time(data.get("appointment_time", ""))

    if not doctor_id or not appointment_date or not appointment_time:
        return jsonify({"error": "doctor_id, appointment_date and appointment_time are required"}), 400

    doctor = Doctor.query.get(doctor_id)
    if not doctor or not doctor.is_active:
        return jsonify({"error": "Doctor not found or inactive"}), 404

    schedules = get_schedule_for_doctor_on_date(doctor.id, appointment_date)

    

    # --- CROWD CONTROL CHECK ---
    from datetime import time
    hour = appointment_time.hour
    start_time = time(hour, 0)
    end_time = time(hour, 59, 59)
    
    hourly_count = Appointment.query.filter_by(
        appointment_date=appointment_date, 
        status="scheduled"
    ).filter(
        Appointment.appointment_time >= start_time, 
        Appointment.appointment_time <= end_time
    ).count()

    # Get the live, persistent config from the file
    current_config = get_clinic_config()

    if hourly_count >= current_config["max_hourly_patients"]:
        return jsonify({"error": f"Clinic capacity reached ({current_config['max_hourly_patients']}/hr). Please select a different hour."}), 400
    # ---------------------------

    if not schedules:
        return jsonify({"error": "Doctor is not scheduled on this date"}), 400

    valid_slot = any(schedule_contains_time(schedule, appointment_time) for schedule in schedules)
    if not valid_slot:
        return jsonify({"error": "Requested time is not a valid slot"}), 400

    existing = Appointment.query.filter_by(doctor_id=doctor.id, appointment_date=appointment_date, appointment_time=appointment_time).first()
    if existing and existing.status != "cancelled":
        return jsonify({"error": "This slot is already booked"}), 400

    appointment = Appointment(
        patient_id=patient.id,
        doctor_id=doctor.id,
        appointment_date=appointment_date,
        appointment_time=appointment_time,
        status="scheduled",
    )
    db.session.add(appointment)
    db.session.commit()

    return jsonify({"message": "Appointment booked successfully", "appointment": serialize_appointment(appointment)}), 201


@appointment_bp.get("/appointments")
@role_required("patient")
def get_my_appointments():
    patient = get_current_patient()
    if not patient:
        return jsonify({"error": "Patient profile not found"}), 404

    appointments = Appointment.query.filter_by(patient_id=patient.id).order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc()).all()
    return jsonify([serialize_appointment(item) for item in appointments]), 200


@appointment_bp.post("/appointments/<int:appointment_id>/cancel")
@role_required("patient")
def cancel_appointment(appointment_id):
    patient = get_current_patient()
    if not patient:
        return jsonify({"error": "Patient profile not found"}), 404

    appointment = Appointment.query.get(appointment_id)
    if not appointment or appointment.patient_id != patient.id:
        return jsonify({"error": "Appointment not found"}), 404
    if appointment.status == "cancelled":
        return jsonify({"error": "Appointment is already cancelled"}), 400
    if appointment.status == "completed":
        return jsonify({"error": "Completed appointment cannot be cancelled"}), 400

    appointment.status = "cancelled"
    db.session.commit()
    return jsonify({"message": "Appointment cancelled successfully", "appointment": serialize_appointment(appointment)}), 200



@appointment_bp.get("/admin/appointments")
@role_required("admin", "doctor")
def get_all_appointments():
    date_str = request.args.get("date")
    query = Appointment.query
    
    if date_str:
        # Filter by the requested date
        query = query.filter_by(appointment_date=parse_date(date_str))
        
    # Order by time so the list flows from morning to evening
    appointments = query.order_by(Appointment.appointment_time.asc()).all()
    return jsonify([serialize_appointment(item) for item in appointments]), 200


import json
import os

# Define the file path (saves in the root of your backend folder)
CONFIG_FILE = "clinic_config.json"

def get_clinic_config():
    # If the file doesn't exist yet, create it with the default limit of 10
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump({"max_hourly_patients": 10}, f)
            
    # Read the file and return the config
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_clinic_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

@appointment_bp.get("/admin/config")
@role_required("admin")
def get_config():
    return jsonify(get_clinic_config()), 200

@appointment_bp.post("/admin/config")
@role_required("admin")
def update_config():
    data = request.get_json() or {}
    config = get_clinic_config() # Read current
    
    if "max_hourly_patients" in data:
        config["max_hourly_patients"] = int(data["max_hourly_patients"])
        save_clinic_config(config) # Save to file
        
    return jsonify(config), 200