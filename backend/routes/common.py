from datetime import datetime, date, time, timedelta
from functools import wraps

from flask import jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, verify_jwt_in_request

from models import (
    db,
    User,
    Patient,
    Doctor,
    DoctorSchedule,
    Appointment,
    QueueEntry,
    OPDVisit,
    Admission,
    AdmissionComplaint,
    Vital,
    ProgressNote,
    Medicine,
    MedicationAdministration,
    DischargeRecord,
    FollowUpRecord,
    Reminder,
)


def parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except Exception:
        return None


def parse_time(value):
    try:
        return datetime.strptime(value, "%H:%M").time()
    except Exception:
        return None


def parse_int(value):
    try:
        return int(value)
    except Exception:
        return None


def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            role = claims.get("role")
            if role not in roles:
                return jsonify({"error": "Forbidden"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def get_current_user():
    user_id = get_jwt_identity()
    try:
        user_id = int(user_id)
    except Exception:
        pass
    return User.query.get(user_id)


def get_current_patient():
    user = get_current_user()
    if not user:
        return None
    return Patient.query.filter_by(user_id=user.id).first()


def get_current_doctor():
    user = get_current_user()
    if not user:
        return None
    return Doctor.query.filter_by(user_id=user.id).first()


def serialize_user(user):
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "role": user.role,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


def serialize_patient(patient):
    return {
        "id": patient.id,
        "user_id": patient.user_id,
        "name": patient.user.name if patient.user else None,
        "email": patient.user.email if patient.user else None,
        "phone": patient.user.phone if patient.user else None,
        "age": patient.age,
        "gender": patient.gender,
        "address": patient.address,
        "created_at": patient.created_at.isoformat() if patient.created_at else None,
    }


def serialize_doctor(doctor):
    return {
        "id": doctor.id,
        "user_id": doctor.user_id,
        "name": doctor.user.name if doctor.user else None,
        "email": doctor.user.email if doctor.user else None,
        "phone": doctor.user.phone if doctor.user else None,
        "specialization": doctor.specialization,
        "consultation_fee": doctor.consultation_fee,
        "is_active": doctor.is_active,
    }


def serialize_schedule(schedule):
    return {
        "id": schedule.id,
        "doctor_id": schedule.doctor_id,
        "day_of_week": schedule.day_of_week,
        "start_time": schedule.start_time.strftime("%H:%M") if schedule.start_time else None,
        "end_time": schedule.end_time.strftime("%H:%M") if schedule.end_time else None,
        "slot_duration": schedule.slot_duration,
    }


def serialize_appointment(appointment):
    data = {
        "id": appointment.id,
        "patient_id": appointment.patient_id,
        "doctor_id": appointment.doctor_id,
        "patient_name": appointment.patient.user.name if appointment.patient and appointment.patient.user else None,
        "doctor_name": appointment.doctor.user.name if appointment.doctor and appointment.doctor.user else None,
        "appointment_date": appointment.appointment_date.isoformat() if appointment.appointment_date else None,
        "appointment_time": appointment.appointment_time.strftime("%H:%M") if appointment.appointment_time else None,
        "status": appointment.status,
        "checked_in_at": appointment.checked_in_at.isoformat() if appointment.checked_in_at else None,
        "created_at": appointment.created_at.isoformat() if appointment.created_at else None,
    }
    if appointment.opd_visit:
        data["opd_visit"] = {
            "id": appointment.opd_visit.id,
            "complaints": appointment.opd_visit.complaints,
            "diagnosis": appointment.opd_visit.diagnosis,
            "notes": appointment.opd_visit.doctor_notes
        }
    return data


def serialize_queue_entry(entry):
    appointment = entry.appointment
    return {
        "id": entry.id,
        "appointment_id": entry.appointment_id,
        "queue_number": entry.queue_number,
        "status": entry.status,
        "created_at": entry.created_at.isoformat() if entry.created_at else None,
        "appointment": serialize_appointment(appointment) if appointment else None,
    }


def serialize_opd_visit(visit):
    return {
        "id": visit.id,
        "patient_id": visit.patient_id,
        "appointment_id": visit.appointment_id,
        "visit_date": visit.visit_date.isoformat() if visit.visit_date else None,
        "complaints": visit.complaints,
        "diagnosis": visit.diagnosis,
        "doctor_notes": visit.doctor_notes,
        "created_by": visit.created_by,
        "created_at": visit.created_at.isoformat() if visit.created_at else None,
    }


# def serialize_admission(admission):
#     return {
#         "id": admission.id,
#         "patient_id": admission.patient_id,
#         "patient_name": admission.patient.user.name if admission.patient and admission.patient.user else None,
#         "admission_date": admission.admission_date.isoformat() if admission.admission_date else None,
#         "provisional_diagnosis": admission.provisional_diagnosis,
#         "status": admission.status,
#         "created_by": admission.created_by,
#         "created_at": admission.created_at.isoformat() if admission.created_at else None,
#     }

def serialize_admission(admission):
    # Safely handle dates (checks if it's an object with .isoformat() or just a string)
    ad_date = admission.admission_date
    cr_date = admission.created_at
    
    formatted_ad_date = ad_date.isoformat() if hasattr(ad_date, 'isoformat') else str(ad_date) if ad_date else None
    formatted_cr_date = cr_date.isoformat() if hasattr(cr_date, 'isoformat') else str(cr_date) if cr_date else None

    # Safely extract patient name without crashing if relationships are missing
    patient_name = "Unknown Patient"
    if admission.patient and admission.patient.user:
        patient_name = admission.patient.user.name

    data = {
        "id": admission.id,
        "patient_id": admission.patient_id,
        "patient_name": patient_name,
        "admission_date": formatted_ad_date,
        "provisional_diagnosis": admission.provisional_diagnosis,
        "status": admission.status,
        "created_by": admission.created_by,
        "created_at": formatted_cr_date,
    }
    
    if admission.discharge_record:
        dis_date = admission.discharge_record.discharge_date
        formatted_dis_date = dis_date.isoformat() if hasattr(dis_date, 'isoformat') else str(dis_date) if dis_date else None
        data["discharge_record"] = {
            "discharge_date": formatted_dis_date,
            "treatment_summary": admission.discharge_record.treatment_summary,
            "medicine_days_prescribed": admission.discharge_record.medicine_days_prescribed
        }
    return data

def serialize_complaint(complaint):
    return {
        "id": complaint.id,
        "admission_id": complaint.admission_id,
        "complaint_text": complaint.complaint_text,
    }


def serialize_vital(vital):
    return {
        "id": vital.id,
        "admission_id": vital.admission_id,
        "record_date": vital.record_date.isoformat() if vital.record_date else None,
        "systolic_bp": vital.systolic_bp,
        "diastolic_bp": vital.diastolic_bp,
        "pulse": vital.pulse,
        "spo2": vital.spo2,
        "rbs": vital.rbs,
        "temperature": vital.temperature,
        "recorded_by": vital.recorded_by,
        "created_at": vital.created_at.isoformat() if vital.created_at else None,
    }


def serialize_progress_note(note):
    return {
        "id": note.id,
        "admission_id": note.admission_id,
        "note_date": note.note_date.isoformat() if note.note_date else None,
        "note_text": note.note_text,
        "recorded_by": note.recorded_by,
        "created_at": note.created_at.isoformat() if note.created_at else None,
    }


def serialize_medicine(medicine):
    return {
        "id": medicine.id,
        "medicine_name": medicine.medicine_name,
        "type": medicine.type,
        "strength": medicine.strength,
        "unit": medicine.unit,
        "created_at": medicine.created_at.isoformat() if medicine.created_at else None,
    }


def serialize_prescription(record):
    patient = None
    if record.admission and record.admission.patient:
        patient = record.admission.patient
    if record.opd_visit and record.opd_visit.patient:
        patient = record.opd_visit.patient
    return {
        "id": record.id,
        "admission_id": record.admission_id,
        "opd_visit_id": record.opd_visit_id,
        "patient_id": patient.id if patient else None,
        "patient_name": patient.user.name if patient and patient.user else None,
        "medicine": serialize_medicine(record.medicine) if record.medicine else None,
        "dosage": record.dosage,
        "route": record.route,
        "frequency": record.frequency,
        "start_date": record.start_date.isoformat() if record.start_date else None,
        "end_date": record.end_date.isoformat() if record.end_date else None,
        "notes": record.notes,
        "prescribed_by": record.prescribed_by,
        "created_at": record.created_at.isoformat() if record.created_at else None,
    }


def serialize_discharge(record):
    return {
        "id": record.id,
        "admission_id": record.admission_id,
        "discharge_date": record.discharge_date.isoformat() if record.discharge_date else None,
        "medicine_days_prescribed": record.medicine_days_prescribed,
        "final_diagnosis": record.final_diagnosis,
        "treatment_summary": record.treatment_summary,
        "follow_up_instructions": record.follow_up_instructions,
        "diet_instructions": record.diet_instructions,
        "created_by": record.created_by,
        "created_at": record.created_at.isoformat() if record.created_at else None,
    }


def serialize_followup(record):
    return {
        "id": record.id,
        "patient_id": record.patient_id,
        "admission_id": record.admission_id,
        "followup_date": record.followup_date.isoformat() if record.followup_date else None,
        "followup_status": record.followup_status,
        "notes": record.notes,
        "recorded_by": record.recorded_by,
        "created_at": record.created_at.isoformat() if record.created_at else None,
    }


def serialize_reminder(reminder):
    return {
        "id": reminder.id,
        "patient_id": reminder.patient_id,
        "admission_id": reminder.admission_id,
        "reminder_type": reminder.reminder_type,
        "reminder_date": reminder.reminder_date.isoformat() if reminder.reminder_date else None,
        "status": reminder.status,
        "created_at": reminder.created_at.isoformat() if reminder.created_at else None,
    }


def build_slots(schedule):
    slots = []
    current_dt = datetime.combine(date.today(), schedule.start_time)
    end_dt = datetime.combine(date.today(), schedule.end_time)
    while current_dt < end_dt:
        slots.append(current_dt.time())
        current_dt += timedelta(minutes=schedule.slot_duration)
    return slots


def schedule_contains_time(schedule, slot_time):
    return slot_time in build_slots(schedule)


def get_schedule_for_doctor_on_date(doctor_id, appointment_date):
    day_of_week = appointment_date.weekday()
    return DoctorSchedule.query.filter_by(doctor_id=doctor_id, day_of_week=day_of_week).all()


def has_schedule_overlap(doctor_id, day_of_week, start_time, end_time, exclude_id=None):
    query = DoctorSchedule.query.filter_by(doctor_id=doctor_id, day_of_week=day_of_week)
    if exclude_id:
        query = query.filter(DoctorSchedule.id != exclude_id)
    schedules = query.all()
    for schedule in schedules:
        if start_time < schedule.end_time and end_time > schedule.start_time:
            return True
    return False


def find_patient_by_id_or_404(patient_id):
    return Patient.query.get(patient_id)


def appointment_belongs_to_patient(appointment, patient):
    return appointment and patient and appointment.patient_id == patient.id


def patient_owns_patient_id(patient, patient_id):
    return patient and patient.id == patient_id
