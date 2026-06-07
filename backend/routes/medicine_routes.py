from sqlalchemy import or_
from flask import Blueprint, jsonify, request

from models import db, Patient, Medicine, MedicationAdministration, Admission, OPDVisit
from routes.common import role_required, get_current_user, get_current_patient, serialize_medicine, serialize_prescription

medicine_bp = Blueprint("medicine_bp", __name__)


@medicine_bp.get("/medicines")
def get_medicines():
    search = request.args.get("search")
    query = Medicine.query
    if search:
        query = query.filter(Medicine.medicine_name.ilike(f"%{search}%"))
    medicines = query.order_by(Medicine.medicine_name.asc()).all()
    return jsonify([serialize_medicine(item) for item in medicines]), 200


@medicine_bp.post("/medicines")
@role_required("admin")
def create_medicine():
    data = request.get_json() or {}
    medicine_name = (data.get("medicine_name") or "").strip()
    if not medicine_name:
        return jsonify({"error": "medicine_name is required"}), 400

    medicine = Medicine(
        medicine_name=medicine_name,
        type=data.get("type"),
        strength=data.get("strength"),
        unit=data.get("unit"),
    )
    db.session.add(medicine)
    db.session.commit()
    return jsonify({"message": "Medicine created successfully", "medicine": serialize_medicine(medicine)}), 201


@medicine_bp.put("/medicines/<int:medicine_id>")
@role_required("admin")
def update_medicine(medicine_id):
    medicine = Medicine.query.get(medicine_id)
    if not medicine:
        return jsonify({"error": "Medicine not found"}), 404

    data = request.get_json() or {}
    if data.get("medicine_name") is not None:
        medicine.medicine_name = data.get("medicine_name")
    if data.get("type") is not None:
        medicine.type = data.get("type")
    if data.get("strength") is not None:
        medicine.strength = data.get("strength")
    if data.get("unit") is not None:
        medicine.unit = data.get("unit")

    db.session.commit()
    return jsonify({"message": "Medicine updated successfully", "medicine": serialize_medicine(medicine)}), 200


@medicine_bp.get("/medicines/prescriptions")
@role_required("doctor", "admin")
def get_prescriptions():
    records = MedicationAdministration.query.order_by(MedicationAdministration.created_at.desc()).all()
    return jsonify([serialize_prescription(item) for item in records]), 200


@medicine_bp.get("/medicines/prescriptions/patient/<int:patient_id>")
@role_required("doctor", "admin", "patient")
def get_patient_prescriptions(patient_id):
    user = get_current_user()
    if user.role == "patient":
        patient = get_current_patient()
        if not patient or patient.id != patient_id:
            return jsonify({"error": "Forbidden"}), 403

    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    admission_ids = [item.id for item in Admission.query.filter_by(patient_id=patient_id).all()]
    opd_visit_ids = [item.id for item in OPDVisit.query.filter_by(patient_id=patient_id).all()]

    conditions = []
    if admission_ids:
        conditions.append(MedicationAdministration.admission_id.in_(admission_ids))
    if opd_visit_ids:
        conditions.append(MedicationAdministration.opd_visit_id.in_(opd_visit_ids))
    if not conditions:
        return jsonify([]), 200

    records = MedicationAdministration.query.filter(or_(*conditions)).order_by(MedicationAdministration.created_at.desc()).all()

    return jsonify([serialize_prescription(item) for item in records]), 200


@medicine_bp.get("/medicines/prescriptions/<int:prescription_id>")
@role_required("doctor", "admin", "patient")
def get_prescription_details(prescription_id):
    record = MedicationAdministration.query.get(prescription_id)
    if not record:
        return jsonify({"error": "Prescription not found"}), 404

    user = get_current_user()
    if user.role == "patient":
        patient = get_current_patient()
        record_patient_id = None
        if record.admission:
            record_patient_id = record.admission.patient_id
        elif record.opd_visit:
            record_patient_id = record.opd_visit.patient_id
        if not patient or patient.id != record_patient_id:
            return jsonify({"error": "Forbidden"}), 403

    return jsonify(serialize_prescription(record)), 200



# 1. API to GET the master list of medicines (for the dropdown)
@medicine_bp.get("/medicines")
@role_required("doctor", "admin")
def get_all_medicines():
    medicines = Medicine.query.all()
    # Assuming you have a serialize_medicine function. If not, just return a dict:
    return jsonify([{"id": m.id, "medicine_name": m.medicine_name, "type": m.type, "strength": m.strength} for m in medicines]), 200
