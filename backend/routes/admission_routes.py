from flask import Blueprint, jsonify, request

from models import (
    db,
    Patient,
    Admission,
    AdmissionComplaint,
    Vital,
    ProgressNote,
    DischargeRecord,
)
from routes.common import (
    role_required,
    get_current_user,
    get_current_patient,
    parse_date,
    serialize_admission,
    serialize_complaint,
    serialize_vital,
    serialize_progress_note,
    serialize_discharge,
)

admission_bp = Blueprint("admission_bp", __name__)


@admission_bp.get("/my/admissions")
@role_required("patient")
def get_my_admissions():
    patient = get_current_patient()
    if not patient:
        return jsonify({"error": "Patient profile not found"}), 404

    admissions = Admission.query.filter_by(patient_id=patient.id).order_by(Admission.admission_date.desc()).all()
    return jsonify([serialize_admission(item) for item in admissions]), 200


@admission_bp.post("/admissions")
@role_required("doctor", "admin")
def create_admission():
    data = request.get_json() or {}
    patient_id = data.get("patient_id")
    admission_date = parse_date(data.get("admission_date", ""))
    provisional_diagnosis = data.get("provisional_diagnosis")
    status = (data.get("status") or "admitted").strip().lower()

    if not patient_id or not admission_date:
        return jsonify({"error": "patient_id and admission_date are required"}), 400

    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    admission = Admission(
        patient_id=patient_id,
        admission_date=admission_date,
        provisional_diagnosis=provisional_diagnosis,
        status=status,
        created_by=get_current_user().id,
    )
    db.session.add(admission)
    db.session.commit()
    return jsonify({"message": "Admission created successfully", "admission": serialize_admission(admission)}), 201


@admission_bp.get("/admissions")
@role_required("doctor", "admin")
def get_admissions():
    patient_id = request.args.get("patient_id", type=int)
    status = request.args.get("status")
    start_date = parse_date(request.args.get("start_date", "")) if request.args.get("start_date") else None
    end_date = parse_date(request.args.get("end_date", "")) if request.args.get("end_date") else None

    query = Admission.query
    if patient_id:
        query = query.filter_by(patient_id=patient_id)
    if status:
        query = query.filter_by(status=status)
    if start_date:
        query = query.filter(Admission.admission_date >= start_date)
    if end_date:
        query = query.filter(Admission.admission_date <= end_date)

    admissions = query.order_by(Admission.admission_date.desc(), Admission.created_at.desc()).all()
    return jsonify([serialize_admission(item) for item in admissions]), 200


@admission_bp.get("/admissions/<int:admission_id>")
@role_required("doctor", "admin", "patient") # Patient allowed
def get_admission_details(admission_id):
    admission = Admission.query.get(admission_id)
    if not admission:
        return jsonify({"error": "Admission not found"}), 404

    current_user = get_current_user()
    
    # SECURITY CHECK: Match Patient ID, not User ID
    if current_user.role == "patient":
        patient_profile = get_current_patient()
        if not patient_profile or str(admission.patient_id) != str(patient_profile.id):
            return jsonify({"error": "Unauthorized access to medical records"}), 403

    return jsonify({
        "admission": serialize_admission(admission),
        "complaints": [serialize_complaint(item) for item in admission.complaints],
        "vitals": [serialize_vital(item) for item in admission.vitals],
        "progress_notes": [serialize_progress_note(item) for item in admission.progress_notes],
        "discharge_record": serialize_discharge(admission.discharge_record) if admission.discharge_record else None,
    }), 200

@admission_bp.put("/admissions/<int:admission_id>")
@role_required("doctor", "admin")
def update_admission(admission_id):
    admission = Admission.query.get(admission_id)
    if not admission:
        return jsonify({"error": "Admission not found"}), 404

    data = request.get_json() or {}
    if data.get("admission_date") is not None:
        admission_date = parse_date(data.get("admission_date"))
        if not admission_date:
            return jsonify({"error": "Invalid admission_date"}), 400
        admission.admission_date = admission_date
    if data.get("provisional_diagnosis") is not None:
        admission.provisional_diagnosis = data.get("provisional_diagnosis")
    if data.get("status") is not None:
        admission.status = data.get("status")

    db.session.commit()
    return jsonify({"message": "Admission updated successfully", "admission": serialize_admission(admission)}), 200


@admission_bp.post("/admissions/<int:admission_id>/discharge")
@role_required("doctor", "admin")
def discharge_patient(admission_id):
    admission = Admission.query.get(admission_id)
    if not admission:
        return jsonify({"error": "Admission not found"}), 404
    if admission.discharge_record:
        return jsonify({"error": "Admission is already discharged"}), 400

    data = request.get_json() or {}
    discharge_date = parse_date(data.get("discharge_date", ""))
    if not discharge_date:
        return jsonify({"error": "discharge_date is required"}), 400

    record = DischargeRecord(
        admission_id=admission.id,
        discharge_date=discharge_date,
        medicine_days_prescribed=data.get("medicine_days_prescribed"),
        final_diagnosis=data.get("final_diagnosis"),
        treatment_summary=data.get("treatment_summary"),
        follow_up_instructions=data.get("follow_up_instructions"),
        diet_instructions=data.get("diet_instructions"),
        created_by=get_current_user().id,
    )
    admission.status = "discharged"
    db.session.add(record)
    db.session.commit()

    return jsonify({"message": "Patient discharged successfully", "discharge_record": serialize_discharge(record)}), 201


@admission_bp.get("/admissions/patients/<int:patient_id>")
@role_required("doctor", "admin")
def get_patient_admissions(patient_id):
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    admissions = Admission.query.filter_by(patient_id=patient_id).order_by(Admission.admission_date.desc()).all()
    return jsonify([serialize_admission(item) for item in admissions]), 200


@admission_bp.post("/admissions/<int:admission_id>/complaints")
@role_required("doctor", "admin")
def add_complaint(admission_id):
    admission = Admission.query.get(admission_id)
    if not admission:
        return jsonify({"error": "Admission not found"}), 404

    data = request.get_json() or {}
    complaint_text = (data.get("complaint_text") or "").strip()
    if not complaint_text:
        return jsonify({"error": "complaint_text is required"}), 400

    complaint = AdmissionComplaint(admission_id=admission_id, complaint_text=complaint_text)
    db.session.add(complaint)
    db.session.commit()
    return jsonify({"message": "Complaint added successfully", "complaint": serialize_complaint(complaint)}), 201


@admission_bp.get("/admissions/<int:admission_id>/complaints")
@role_required("doctor", "admin")
def get_complaints(admission_id):
    admission = Admission.query.get(admission_id)
    if not admission:
        return jsonify({"error": "Admission not found"}), 404

    complaints = AdmissionComplaint.query.filter_by(admission_id=admission_id).all()
    return jsonify([serialize_complaint(item) for item in complaints]), 200


@admission_bp.delete("/admissions/complaints/<int:complaint_id>")
@role_required("doctor", "admin")
def delete_complaint(complaint_id):
    complaint = AdmissionComplaint.query.get(complaint_id)
    if not complaint:
        return jsonify({"error": "Complaint not found"}), 404

    db.session.delete(complaint)
    db.session.commit()
    return jsonify({"message": "Complaint deleted successfully"}), 200


@admission_bp.post("/admissions/<int:admission_id>/vitals")
@role_required("doctor", "admin")
def add_vitals(admission_id):
    admission = Admission.query.get(admission_id)
    if not admission:
        return jsonify({"error": "Admission not found"}), 404

    data = request.get_json() or {}
    record_date = parse_date(data.get("record_date", ""))
    if not record_date:
        return jsonify({"error": "record_date is required"}), 400

    vital = Vital(
        admission_id=admission_id,
        record_date=record_date,
        systolic_bp=data.get("systolic_bp"),
        diastolic_bp=data.get("diastolic_bp"),
        pulse=data.get("pulse"),
        spo2=data.get("spo2"),
        rbs=data.get("rbs"),
        temperature=data.get("temperature"),
        recorded_by=get_current_user().id,
    )
    db.session.add(vital)
    db.session.commit()
    return jsonify({"message": "Vitals recorded successfully", "vital": serialize_vital(vital)}), 201


@admission_bp.get("/admissions/<int:admission_id>/vitals")
@role_required("doctor", "admin")
def get_vitals(admission_id):
    admission = Admission.query.get(admission_id)
    if not admission:
        return jsonify({"error": "Admission not found"}), 404

    vitals = Vital.query.filter_by(admission_id=admission_id).order_by(Vital.record_date.desc(), Vital.created_at.desc()).all()
    return jsonify([serialize_vital(item) for item in vitals]), 200


@admission_bp.get("/admissions/<int:admission_id>/vitals/latest")
@role_required("doctor", "admin", "patient") # ADDED PATIENT HERE
def get_latest_vitals(admission_id):
    admission = Admission.query.get(admission_id)
    if not admission:
        return jsonify({"error": "Admission not found"}), 404

    current_user = get_current_user()
    
    # SECURITY CHECK: Match Patient ID, not User ID
    if current_user.role == "patient":
        patient_profile = get_current_patient()
        if not patient_profile or str(admission.patient_id) != str(patient_profile.id):
            return jsonify({"error": "Unauthorized access to medical records"}), 403

    vital = Vital.query.filter_by(admission_id=admission_id).order_by(Vital.record_date.desc(), Vital.created_at.desc()).first()
    if not vital:
        return jsonify({"error": "No vitals found"}), 404

    return jsonify(serialize_vital(vital)), 200


@admission_bp.post("/admissions/<int:admission_id>/progress-notes")
@role_required("doctor", "admin")
def add_progress_note(admission_id):
    admission = Admission.query.get(admission_id)
    if not admission:
        return jsonify({"error": "Admission not found"}), 404

    data = request.get_json() or {}
    note_date = parse_date(data.get("note_date", ""))
    note_text = (data.get("note_text") or "").strip()
    if not note_date or not note_text:
        return jsonify({"error": "note_date and note_text are required"}), 400

    note = ProgressNote(
        admission_id=admission_id,
        note_date=note_date,
        note_text=note_text,
        recorded_by=get_current_user().id,
    )
    db.session.add(note)
    db.session.commit()
    return jsonify({"message": "Progress note added successfully", "progress_note": serialize_progress_note(note)}), 201


@admission_bp.get("/admissions/<int:admission_id>/progress-notes")
@role_required("doctor", "admin")
def get_progress_notes(admission_id):
    admission = Admission.query.get(admission_id)
    if not admission:
        return jsonify({"error": "Admission not found"}), 404

    notes = ProgressNote.query.filter_by(admission_id=admission_id).order_by(ProgressNote.note_date.desc(), ProgressNote.created_at.desc()).all()
    return jsonify([serialize_progress_note(item) for item in notes]), 200



from models import db, Admission, Medicine, MedicationAdministration
from flask import request, jsonify
from routes.common import parse_date # Assuming this is your date parser


# 2. API to POST a new medication to a specific admission
@admission_bp.post("/admissions/<int:admission_id>/medications")
@role_required("doctor", "admin")
def add_admission_medication(admission_id):
    admission = Admission.query.get(admission_id)
    if not admission:
        return jsonify({"error": "Admission not found"}), 404

    data = request.get_json() or {}
    
    # Required fields
    medicine_id = data.get("medicine_id")
    dosage = data.get("dosage")
    frequency = data.get("frequency")
    start_date = parse_date(data.get("start_date", ""))
    
    if not medicine_id or not dosage or not frequency or not start_date:
        return jsonify({"error": "medicine_id, dosage, frequency, and start_date are required"}), 400

    new_med = MedicationAdministration(
        admission_id=admission_id,
        medicine_id=medicine_id,
        dosage=dosage,
        route=data.get("route", "Oral"), # Default to Oral if not provided
        frequency=frequency,
        start_date=start_date,
        end_date=parse_date(data.get("end_date", "")) if data.get("end_date") else None,
        notes=data.get("notes", ""),
        prescribed_by=get_current_user().id # Since the nurse is logging it, their ID goes here
    )
    
    db.session.add(new_med)
    db.session.commit()
    
    # Assuming you have serialize_prescription. Adjust as needed.
    return jsonify({"message": "Medication added successfully"}), 201

@admission_bp.get("/admissions/<int:admission_id>/medications")
@role_required("doctor", "admin", "patient") # ADDED PATIENT HERE
def get_admission_medications(admission_id):
    admission = Admission.query.get(admission_id)
    if not admission:
        return jsonify({"error": "Admission not found"}), 404
        
    current_user = get_current_user()
    
    # SECURITY CHECK: Match Patient ID, not User ID
    # SECURITY CHECK: Bulletproof string matching using your helper
    if current_user.role == "patient":
        patient_profile = get_current_patient()
        if not patient_profile or str(admission.patient_id) != str(patient_profile.id):
            return jsonify({"error": "Unauthorized access to medical records"}), 403
            
    records = MedicationAdministration.query.filter_by(admission_id=admission_id).order_by(MedicationAdministration.created_at.desc()).all()
    
    results = []
    for r in records:
        results.append({
            "id": r.id,
            "medicine_name": r.medicine.medicine_name if r.medicine else "Unknown",
            "dosage": r.dosage,
            "frequency": r.frequency,
            "route": r.route,
            "start_date": r.start_date.isoformat() if r.start_date else None,
            "end_date": r.end_date.isoformat() if r.end_date else None,
            "notes": r.notes
        })
        
    return jsonify(results), 200