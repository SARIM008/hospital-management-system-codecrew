import os
from datetime import date
from flask import Blueprint, jsonify, request
from models import db, Appointment, QueueEntry, OPDVisit, ConsultationRecord
from routes.common import role_required, get_current_doctor, serialize_appointment, serialize_queue_entry, serialize_opd_visit
from utils.transcription import transcription_service
from utils.ai_summarizer import ai_summarizer

doctor_bp = Blueprint("doctor_bp", __name__)


@doctor_bp.get("/doctor/overview")
@role_required("doctor")
def doctor_overview():
    doctor = get_current_doctor()
    if not doctor:
        return jsonify({"error": "Doctor profile not found"}), 404

    today = date.today()
    appointments_count = Appointment.query.filter_by(doctor_id=doctor.id, appointment_date=today).count()
    checked_in_count = Appointment.query.filter_by(doctor_id=doctor.id, appointment_date=today, status="checked_in").count()
    completed_count = Appointment.query.filter_by(doctor_id=doctor.id, appointment_date=today, status="completed").count()
    queue_count = QueueEntry.query.join(Appointment).filter(Appointment.doctor_id == doctor.id, Appointment.appointment_date == today).count()
    recent_visits_count = OPDVisit.query.join(Appointment).filter(Appointment.doctor_id == doctor.id).count()

    return jsonify({
        "date": today.isoformat(),
        "appointments_count": appointments_count,
        "checked_in_count": checked_in_count,
        "completed_count": completed_count,
        "queue_count": queue_count,
        "recent_visits_count": recent_visits_count,
    }), 200


@doctor_bp.get("/doctor/appointments")
@role_required("doctor")
def doctor_appointments():
    doctor = get_current_doctor()
    if not doctor:
        return jsonify({"error": "Doctor profile not found"}), 404

    today = date.today()
    # Fetch all appointments from today onwards for this doctor
    appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.appointment_date >= today
    ).order_by(Appointment.appointment_date.asc(), Appointment.appointment_time.asc()).all()
    
    return jsonify([serialize_appointment(item) for item in appointments]), 200


@doctor_bp.post("/doctor/appointments/<int:appointment_id>/record")
@role_required("doctor")
def save_consultation_recording(appointment_id):
    doctor = get_current_doctor()
    if not doctor:
        return jsonify({"error": "Doctor profile not found"}), 404

    appointment = Appointment.query.get(appointment_id)
    if not appointment or appointment.doctor_id != doctor.id:
        return jsonify({"error": "Appointment not found or unauthorized"}), 404

    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Ensure recordings directory exists
    recordings_dir = os.path.join("assets", "recordings")
    if not os.path.exists(recordings_dir):
        os.makedirs(recordings_dir)

    # Save audio file
    filename = f"consultation_{appointment_id}_{int(date.today().strftime('%Y%m%d'))}.webm"
    file_path = os.path.join(recordings_dir, filename)
    audio_file.save(file_path)

    try:
        # Transcribe audio using Whisper
        transcript = transcription_service.transcribe(file_path)

        # Create consultation record
        record = ConsultationRecord(
            appointment_id=appointment.id,
            patient_id=appointment.patient_id,
            doctor_id=doctor.id,
            audio_file_path=file_path,
            transcript_text=transcript
        )
        db.session.add(record)

        # Mark appointment as completed
        appointment.status = "completed"
        
        # Trigger AI Summarization
        summary = ai_summarizer.summarize_consultation(transcript)
        opd_visit = None
        if summary:
            opd_visit = OPDVisit(
                patient_id=appointment.patient_id,
                appointment_id=appointment.id,
                visit_date=date.today(),
                complaints=summary.get('complaints'),
                diagnosis=summary.get('diagnosis'),
                doctor_notes=summary.get('doctor_notes'),
                created_by=doctor.user_id
            )
            db.session.add(opd_visit)
            
            # Also update ConsultationRecord if we add summary field later, 
            # for now it's in OPDVisit
        
        db.session.commit()

        return jsonify({
            "message": "Consultation recorded, transcribed, and summarized by AI successfully",
            "transcript": transcript,
            "summary": summary,
            "appointment_id": appointment.id,
            "status": "completed",
            "opd_visit": serialize_opd_visit(opd_visit) if opd_visit else None
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Transcription or saving failed: {str(e)}"}), 500


@doctor_bp.get("/doctor/queue")
@role_required("doctor")
def doctor_queue():
    doctor = get_current_doctor()
    if not doctor:
        return jsonify({"error": "Doctor profile not found"}), 404

    today = date.today()
    queue_entries = QueueEntry.query.join(Appointment).filter(Appointment.doctor_id == doctor.id, Appointment.appointment_date == today).order_by(QueueEntry.queue_number.asc()).all()
    return jsonify([serialize_queue_entry(item) for item in queue_entries]), 200


@doctor_bp.get("/doctor/recent-visits")
@role_required("doctor")
def doctor_recent_visits():
    doctor = get_current_doctor()
    if not doctor:
        return jsonify({"error": "Doctor profile not found"}), 404

    visits = OPDVisit.query.join(Appointment).filter(Appointment.doctor_id == doctor.id).order_by(OPDVisit.created_at.desc()).limit(10).all()
    return jsonify([serialize_opd_visit(item) for item in visits]), 200


@doctor_bp.get("/doctor/appointments/<int:appointment_id>/transcript")
@role_required("doctor")
def get_appointment_transcript(appointment_id):
    doctor = get_current_doctor()
    if not doctor:
        return jsonify({"error": "Doctor profile not found"}), 404

    appointment = Appointment.query.get(appointment_id)
    if not appointment or appointment.doctor_id != doctor.id:
        return jsonify({"error": "Appointment not found or unauthorized"}), 404

    record = ConsultationRecord.query.filter_by(appointment_id=appointment_id).first()
    if not record:
        return jsonify({"error": "No transcription found for this appointment"}), 404

    # Look for an associated OPD Visit (the AI summary)
    opd_visit = OPDVisit.query.filter_by(appointment_id=appointment_id).first()

    return jsonify({
        "appointment_id": appointment_id,
        "transcript": record.transcript_text,
        "summary": serialize_opd_visit(opd_visit) if opd_visit else None
    }), 200


@doctor_bp.post("/doctor/appointments/<int:appointment_id>/summarize")
@role_required("doctor")
def re_summarize_consultation(appointment_id):
    doctor = get_current_doctor()
    if not doctor:
        return jsonify({"error": "Doctor profile not found"}), 404

    appointment = Appointment.query.get(appointment_id)
    if not appointment or appointment.doctor_id != doctor.id:
        return jsonify({"error": "Appointment not found or unauthorized"}), 404

    record = ConsultationRecord.query.filter_by(appointment_id=appointment_id).first()
    if not record:
        return jsonify({"error": "No transcription found for this appointment"}), 404

    summary = ai_summarizer.summarize_consultation(record.transcript_text)
    if not summary:
        return jsonify({"error": "AI summarization failed"}), 500

    opd_visit = OPDVisit.query.filter_by(appointment_id=appointment_id).first()
    if not opd_visit:
        opd_visit = OPDVisit(
            patient_id=appointment.patient_id,
            appointment_id=appointment.id,
            visit_date=date.today(),
            created_by=doctor.user_id
        )
        db.session.add(opd_visit)

    opd_visit.complaints = summary.get('complaints')
    opd_visit.diagnosis = summary.get('diagnosis')
    opd_visit.doctor_notes = summary.get('doctor_notes')
    
    db.session.commit()

    return jsonify({
        "message": "AI summary updated successfully",
        "summary": summary,
        "opd_visit": serialize_opd_visit(opd_visit)
    }), 200
