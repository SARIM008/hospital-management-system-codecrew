from datetime import date

from flask import Blueprint, jsonify, request

from models import db, Appointment, OPDVisit, Medicine, MedicationAdministration, Patient
from routes.common import role_required, get_current_user, get_current_doctor, parse_date, serialize_opd_visit, serialize_prescription

opd_bp = Blueprint("opd_bp", __name__)


@opd_bp.post("/opd/start/<int:appointment_id>")
@role_required("doctor")
def start_consultation(appointment_id):
    doctor = get_current_doctor()
    if not doctor:
        return jsonify({"error": "Doctor profile not found"}), 404

    appointment = Appointment.query.get(appointment_id)
    if not appointment or appointment.doctor_id != doctor.id:
        return jsonify({"error": "Appointment not found"}), 404
    if appointment.status == "cancelled":
        return jsonify({"error": "Cancelled appointment cannot start consultation"}), 400

    visit = appointment.opd_visit
    if not visit:
        visit = OPDVisit(
            patient_id=appointment.patient_id,
            appointment_id=appointment.id,
            visit_date=appointment.appointment_date or date.today(),
            created_by=get_current_user().id,
        )
        db.session.add(visit)

    appointment.status = "in_consultation"
    if appointment.queue_entry:
        appointment.queue_entry.status = "in_consultation"
    db.session.commit()

    return jsonify({"message": "Consultation started successfully", "opd_visit": serialize_opd_visit(visit)}), 200


@opd_bp.post("/opd/complete/<int:appointment_id>")
@role_required("doctor")
def complete_consultation(appointment_id):
    doctor = get_current_doctor()
    if not doctor:
        return jsonify({"error": "Doctor profile not found"}), 404

    appointment = Appointment.query.get(appointment_id)
    if not appointment or appointment.doctor_id != doctor.id:
        return jsonify({"error": "Appointment not found"}), 404
    if appointment.status == "cancelled":
        return jsonify({"error": "Cancelled appointment cannot be completed"}), 400

    data = request.get_json() or {}
    complaints = data.get("complaints")
    diagnosis = data.get("diagnosis")
    doctor_notes = data.get("doctor_notes")
    medications = data.get("medications") or []

    visit = appointment.opd_visit
    if not visit:
        visit = OPDVisit(
            patient_id=appointment.patient_id,
            appointment_id=appointment.id,
            visit_date=appointment.appointment_date or date.today(),
            created_by=get_current_user().id,
        )
        db.session.add(visit)
        db.session.flush()

    visit.complaints = complaints
    visit.diagnosis = diagnosis
    visit.doctor_notes = doctor_notes
    appointment.status = "completed"
    if appointment.queue_entry:
        appointment.queue_entry.status = "completed"

    created_prescriptions = []
    for item in medications:
        medicine_id = item.get("medicine_id")
        medicine = Medicine.query.get(medicine_id)
        if not medicine:
            continue
        start_date = parse_date(item.get("start_date", ""))
        end_date = parse_date(item.get("end_date", ""))
        record = MedicationAdministration(
            opd_visit_id=visit.id,
            medicine_id=medicine.id,
            dosage=item.get("dosage"),
            route=item.get("route"),
            frequency=item.get("frequency"),
            start_date=start_date,
            end_date=end_date,
            notes=item.get("notes"),
            prescribed_by=get_current_user().id,
        )
        db.session.add(record)
        created_prescriptions.append(record)

    db.session.commit()

    return jsonify({
        "message": "Consultation completed successfully",
        "opd_visit": serialize_opd_visit(visit),
        "prescriptions": [serialize_prescription(item) for item in created_prescriptions],
    }), 200


from routes.common import role_required, get_current_user # Ensure get_current_user is imported

@opd_bp.get("/opd_visits/<int:visit_id>")
@role_required("doctor", "admin", "patient") 
def get_opd_visit_details(visit_id):
    visit = OPDVisit.query.get_or_404(visit_id)
    current_user = get_current_user()

    # Apply the security check
    if current_user.role == "patient":
        patient_profile = Patient.query.filter_by(user_id=current_user.id).first()
        if not patient_profile or visit.patient_id != patient_profile.id:
            return jsonify({"error": "Unauthorized access to medical records"}), 403
    
    from models import User
    doctor = User.query.get(visit.created_by)
    doctor_name = doctor.name if doctor else "Unknown Doctor"

    return jsonify({
        "id": visit.id,
        "visit_date": visit.visit_date.isoformat() if visit.visit_date else None,
        "time": visit.created_at.strftime("%I:%M %p") if visit.created_at else None,
        "doctor_name": doctor_name,
        "complaints": visit.complaints,
        "diagnosis": visit.diagnosis,
        "doctor_notes": visit.doctor_notes
    }), 200