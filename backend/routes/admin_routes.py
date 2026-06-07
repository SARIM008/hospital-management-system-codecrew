from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from werkzeug.security import generate_password_hash

from models import db, User, Patient, Doctor, DoctorSchedule, Appointment, Admission
from routes.common import (
    role_required,
    serialize_doctor,
    serialize_schedule,
    serialize_patient,
    parse_int,
    parse_time,
    has_schedule_overlap,
)

admin_bp = Blueprint("admin_bp", __name__)


@admin_bp.post("/admin/doctors")
@role_required("admin")
def create_doctor():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    phone = (data.get("phone") or "")
    password = data.get("password") or ""
    specialization = (data.get("specialization") or "")
    consultation_fee = parse_int(data.get("consultation_fee"))

    if not name or not email or not phone or not password:
        return jsonify({"error": "name, email, phone and password are required"}), 400

    if User.query.filter((User.email == email) | (User.phone == phone)).first():
        return jsonify({"error": "email or phone already exists"}), 400

    user = User(
        name=name,
        email=email,
        phone=phone,
        password_hash=generate_password_hash(password),
        role="doctor",
    )
    db.session.add(user)
    db.session.flush()

    doctor = Doctor(
        user_id=user.id,
        specialization=specialization,
        consultation_fee=consultation_fee,
        is_active=True,
    )
    db.session.add(doctor)
    db.session.commit() 
    
    
    return jsonify({
        "message": "Doctor created successfully",
        "id": doctor.id 
    }), 201


@admin_bp.post("/admin/users/admin")
@role_required("admin")
def create_admin_user():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    phone = (data.get("phone") or "").strip()
    password = data.get("password") or ""

    if not name or not email or not phone or not password:
        return jsonify({"error": "name, email, phone and password are required"}), 400

    if User.query.filter((User.email == email) | (User.phone == phone)).first():
        return jsonify({"error": "email or phone already exists"}), 400

    user = User(
        name=name,
        email=email,
        phone=phone,
        password_hash=generate_password_hash(password),
        role="admin",
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Admin created successfully", "user": {"id": user.id, "name": user.name, "email": user.email, "phone": user.phone, "role": user.role}}), 201


@admin_bp.get("/admin/doctors")
@role_required("admin", "patient")
def get_doctors_admin():
    specialization = request.args.get("specialization")
    active = request.args.get("active")
    name = request.args.get("name")

    query = Doctor.query.join(User)
    if specialization:
        query = query.filter(Doctor.specialization.ilike(f"%{specialization}%"))
    if active is not None:
        query = query.filter(Doctor.is_active == (active.lower() == "true"))
    if name:
        query = query.filter(User.name.ilike(f"%{name}%"))

    doctors = query.order_by(User.name.asc()).all()
    return jsonify([serialize_doctor(doctor) for doctor in doctors]), 200


@admin_bp.put("/admin/doctors/<int:doctor_id>")
@role_required("admin")
def update_doctor(doctor_id):
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({"error": "Doctor not found"}), 404

    data = request.get_json() or {}
    user = doctor.user

    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    specialization = data.get("specialization")
    consultation_fee = data.get("consultation_fee")
    is_active = data.get("is_active")

    if email and email != user.email and User.query.filter_by(email=email.lower()).first():
        return jsonify({"error": "email already exists"}), 400
    if phone and phone != user.phone and User.query.filter_by(phone=phone).first():
        return jsonify({"error": "phone already exists"}), 400

    if name is not None:
        user.name = name.strip()
    if email is not None:
        user.email = email.strip().lower()
    if phone is not None:
        user.phone = phone.strip()
    if specialization is not None:
        doctor.specialization = specialization
    if consultation_fee is not None:
        doctor.consultation_fee = parse_int(consultation_fee)
    if is_active is not None:
        doctor.is_active = bool(is_active)

    db.session.commit()
    return jsonify({"message": "Doctor updated successfully", "doctor": serialize_doctor(doctor)}), 200


@admin_bp.delete("/admin/doctors/<int:doctor_id>")
@role_required("admin")
def deactivate_doctor(doctor_id):
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({"error": "Doctor not found"}), 404

    doctor.is_active = False
    db.session.commit()
    return jsonify({"message": "Doctor deactivated successfully", "doctor": serialize_doctor(doctor)}), 200


@admin_bp.post("/admin/doctors/<int:doctor_id>/schedules")
@role_required("admin")
def create_schedule(doctor_id):
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({"error": "Doctor not found"}), 404

    data = request.get_json() or {}
    days_of_week = data.get("days_of_week") or []
    start_time = parse_time(data.get("start_time"))
    end_time = parse_time(data.get("end_time"))
    slot_duration = parse_int(data.get("slot_duration"))

    if not days_of_week or start_time is None or end_time is None or slot_duration is None:
        return jsonify({"error": "days_of_week, start_time, end_time and slot_duration are required"}), 400

    if start_time >= end_time:
        return jsonify({"error": "start_time must be before end_time"}), 400

    if slot_duration <= 0:
        return jsonify({"error": "slot_duration must be greater than 0"}), 400

    created_schedules = []

    for day in days_of_week:
        day = parse_int(day)

        if day is None or day < 0 or day > 6:
            return jsonify({"error": "Each day_of_week must be between 0 and 6"}), 400

        if has_schedule_overlap(doctor_id, day, start_time, end_time):
            return jsonify({"error": f"Schedule overlaps for day {day}"}), 400

        schedule = DoctorSchedule(
            doctor_id=doctor_id,
            day_of_week=day,
            start_time=start_time,
            end_time=end_time,
            slot_duration=slot_duration,
        )
        db.session.add(schedule)
        created_schedules.append(schedule)

    db.session.commit()

    return jsonify({
        "message": "Schedules created successfully",
        "schedules": [serialize_schedule(schedule) for schedule in created_schedules]
    }), 201


@admin_bp.get("/admin/doctors/<int:doctor_id>/schedules")
@role_required("admin", "patient")
def get_schedules(doctor_id):
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({"error": "Doctor not found"}), 404

    schedules = DoctorSchedule.query.filter_by(doctor_id=doctor_id).order_by(DoctorSchedule.day_of_week.asc(), DoctorSchedule.start_time.asc()).all()
    return jsonify([serialize_schedule(schedule) for schedule in schedules]), 200


@admin_bp.put("/admin/doctors/<int:doctor_id>/schedules/<int:schedule_id>")
@role_required("admin")
def update_schedule(doctor_id, schedule_id):
    schedule = DoctorSchedule.query.filter_by(id=schedule_id, doctor_id=doctor_id).first()
    if not schedule:
        return jsonify({"error": "Schedule not found"}), 404

    data = request.get_json() or {}
    day_of_week = parse_int(data.get("day_of_week")) if data.get("day_of_week") is not None else schedule.day_of_week
    start_time = parse_time(data.get("start_time")) if data.get("start_time") is not None else schedule.start_time
    end_time = parse_time(data.get("end_time")) if data.get("end_time") is not None else schedule.end_time
    slot_duration = parse_int(data.get("slot_duration")) if data.get("slot_duration") is not None else schedule.slot_duration

    if day_of_week < 0 or day_of_week > 6:
        return jsonify({"error": "day_of_week must be between 0 and 6"}), 400
    if start_time >= end_time:
        return jsonify({"error": "start_time must be before end_time"}), 400
    if slot_duration <= 0:
        return jsonify({"error": "slot_duration must be greater than 0"}), 400
    if has_schedule_overlap(doctor_id, day_of_week, start_time, end_time, exclude_id=schedule.id):
        return jsonify({"error": "Schedule overlaps with an existing schedule"}), 400

    schedule.day_of_week = day_of_week
    schedule.start_time = start_time
    schedule.end_time = end_time
    schedule.slot_duration = slot_duration
    db.session.commit()

    return jsonify({"message": "Schedule updated successfully", "schedule": serialize_schedule(schedule)}), 200


@admin_bp.delete("/admin/doctors/<int:doctor_id>/schedules/<int:schedule_id>")
@role_required("admin")
def delete_schedule(doctor_id, schedule_id):
    schedule = DoctorSchedule.query.filter_by(id=schedule_id, doctor_id=doctor_id).first()
    if not schedule:
        return jsonify({"error": "Schedule not found"}), 404

    db.session.delete(schedule)
    db.session.commit()
    return jsonify({"message": "Schedule deleted successfully"}), 200




@admin_bp.get("/admin/patients")
@role_required("admin")
def get_patients_admin():
    name = request.args.get("name")
    gender = request.args.get("gender")

    
    query = Patient.query.join(User)
    if name:
        query = query.filter(User.name.ilike(f"%{name}%"))
    if gender:
        query = query.filter(Patient.gender == gender)

    patients = query.order_by(User.name.asc()).all()
    
   
    results = []
    for patient in patients:
        patient_data = serialize_patient(patient) 
        
        
        latest_admission = Admission.query.filter_by(patient_id=patient.id)\
            .order_by(Admission.created_at.desc()).first()
            
        latest_opd = OPDVisit.query.filter_by(patient_id=patient.id)\
            .order_by(OPDVisit.created_at.desc()).first()
        
       
        status = "REGISTERED" 
        
        # Determine active status based on the most recent event
        if latest_admission and latest_admission.status.lower() == "admitted":
            # If currently admitted, they are always IPD
            status = "IPD"
            
        elif latest_admission and latest_admission.status.lower() == "discharged":
            # If discharged, check if they had a newer OPD visit AFTER the discharge date
            if latest_opd and latest_opd.created_at > latest_admission.created_at:
                status = "OPD"
            else:
                status = "DISCHARGED"
                
        elif latest_opd:
            # If they have no admissions, but have an OPD record
            status = "OPD"
            
        # Inject the final calculated status into the dictionary
        patient_data["status"] = status
        results.append(patient_data)

    return jsonify(results), 200







import socket
from datetime import date
from flask import Blueprint, jsonify
from sqlalchemy import func
from models import db, Appointment, Admission, OPDVisit, DischargeRecord, Doctor
from routes.common import role_required 

@admin_bp.get("/admin/dashboard-stats")
@role_required("admin")
def get_dashboard_stats():
    today = date.today()

    # 1. Today's Appointments & Revenue
    # Filtering appointments for today
    today_appointments = Appointment.query.filter(func.date(Appointment.appointment_date) == today).all()
    today_appointments_count = len(today_appointments)
    
    # . TODAY'S REVENUE (Fixed to use OPDVisits)
    today_opd_visits = OPDVisit.query.filter(func.date(OPDVisit.visit_date) == today).all()
    today_revenue = 0
    for visit in today_opd_visits:
        # Assuming created_by is the user_id of the Doctor
        doctor = Doctor.query.filter_by(user_id=visit.created_by).first()
        if doctor and doctor.consultation_fee:
            today_revenue += doctor.consultation_fee

    # 2. Ward Capacity
    TOTAL_BEDS = 60
    active_ipd_count = Admission.query.filter_by(status="admitted").count()
    ward_capacity_pct = min(100, int((active_ipd_count / TOTAL_BEDS) * 100)) if TOTAL_BEDS else 0

    # 3. Total Healed (OPD + Discharged IPD)
    total_opd = OPDVisit.query.count()
    total_discharges = DischargeRecord.query.count()
    total_healed = total_opd + total_discharges

    # 4. Active Doctors
    active_doctors = Doctor.query.filter_by(is_active=True).count()

    # 5. Average Length of Stay (ALOS)
    discharges = DischargeRecord.query.join(Admission).all()
    total_days = 0
    valid_discharges = 0
    for d in discharges:
        if d.discharge_date and d.admission.admission_date:
            days = (d.discharge_date - d.admission.admission_date).days
            total_days += max(1, days) # Minimum 1 day stay
            valid_discharges += 1
    alos = round(total_days / valid_discharges, 1) if valid_discharges > 0 else 0

    # 6. AI Engine Ping Status (Checking port 5001)
    ai_status = "offline"
    try:
        # Attempts to open a 1-second connection to your AI port
        with socket.create_connection(("localhost", 5001), timeout=1):
            ai_status = "online"
    except Exception:
        ai_status = "offline"

    # 7. 7-Day Inflow (We generate a dummy array, ending with today's real count)
    seven_day_inflow = [12, 18, 15, 22, 19, 28, today_appointments_count]

    return jsonify({
        "today_appointments": today_appointments_count,
        "today_revenue": today_revenue,
        "active_ipd": active_ipd_count,
        "total_beds": TOTAL_BEDS,
        "ward_capacity_pct": ward_capacity_pct,
        "total_healed": total_healed,
        "active_doctors": active_doctors,
        "alos": alos,
        "ai_engine": ai_status,
        "seven_day_inflow": seven_day_inflow
    }), 200