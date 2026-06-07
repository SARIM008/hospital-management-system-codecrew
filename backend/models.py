from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(50), unique=True, nullable=False)

    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(20), default="patient")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    doctor = db.relationship("Doctor", back_populates="user", uselist=False)
    patient = db.relationship("Patient", back_populates="user", uselist=False)


class Patient(db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True)

    user = db.relationship("User", back_populates="patient")

    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    address = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    appointments = db.relationship("Appointment", back_populates="patient", cascade="all, delete")
    opd_visits = db.relationship("OPDVisit", back_populates="patient", cascade="all, delete")
    admissions = db.relationship("Admission", back_populates="patient", cascade="all, delete")
    followups = db.relationship("FollowUpRecord", back_populates="patient", cascade="all, delete")
    reminders = db.relationship("Reminder", back_populates="patient", cascade="all, delete")


class Doctor(db.Model):
    __tablename__ = "doctors"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True)

    user = db.relationship("User", back_populates="doctor")

    specialization = db.Column(db.String(255))
    consultation_fee = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=True)

    schedules = db.relationship("DoctorSchedule", back_populates="doctor", cascade="all, delete")
    appointments = db.relationship("Appointment", back_populates="doctor")


class DoctorSchedule(db.Model):
    __tablename__ = "doctor_schedules"

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"))

    day_of_week = db.Column(db.Integer)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)

    slot_duration = db.Column(db.Integer)

    doctor = db.relationship("Doctor", back_populates="schedules")


class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"))
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"))

    appointment_date = db.Column(db.Date, index=True)
    appointment_time = db.Column(db.Time)

    status = db.Column(db.String(30), default="scheduled")

    checked_in_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship("Patient", back_populates="appointments")
    doctor = db.relationship("Doctor", back_populates="appointments")
    queue_entry = db.relationship("QueueEntry", back_populates="appointment", uselist=False, cascade="all, delete")
    opd_visit = db.relationship("OPDVisit", back_populates="appointment", uselist=False)

    __table_args__ = (
        db.UniqueConstraint("doctor_id", "appointment_date", "appointment_time"),
    )


class QueueEntry(db.Model):
    __tablename__ = "queue_entries"

    id = db.Column(db.Integer, primary_key=True)

    appointment_id = db.Column(db.Integer, db.ForeignKey("appointments.id"))
    queue_number = db.Column(db.Integer)
    status = db.Column(db.String(20))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    appointment = db.relationship("Appointment", back_populates="queue_entry")


class OPDVisit(db.Model):
    __tablename__ = "opd_visits"

    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"))
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointments.id"), nullable=True)

    visit_date = db.Column(db.Date)

    complaints = db.Column(db.Text)
    diagnosis = db.Column(db.Text)
    doctor_notes = db.Column(db.Text)

    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship("Patient", back_populates="opd_visits")
    appointment = db.relationship("Appointment", back_populates="opd_visit")
    medications = db.relationship("MedicationAdministration", back_populates="opd_visit", cascade="all, delete")


class Admission(db.Model):
    __tablename__ = "admissions"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"))

    admission_date = db.Column(db.Date, index=True)
    provisional_diagnosis = db.Column(db.Text)
    status = db.Column(db.String(20))

    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship("Patient", back_populates="admissions")
    complaints = db.relationship("AdmissionComplaint", back_populates="admission", cascade="all, delete")
    vitals = db.relationship("Vital", back_populates="admission", cascade="all, delete")
    progress_notes = db.relationship("ProgressNote", back_populates="admission", cascade="all, delete")
    medications = db.relationship("MedicationAdministration", back_populates="admission", cascade="all, delete")
    discharge_record = db.relationship("DischargeRecord", back_populates="admission", uselist=False, cascade="all, delete")
    reminders = db.relationship("Reminder", back_populates="admission", cascade="all, delete")
    followups = db.relationship("FollowUpRecord", back_populates="admission", cascade="all, delete")


class AdmissionComplaint(db.Model):
    __tablename__ = "admission_complaints"

    id = db.Column(db.Integer, primary_key=True)
    admission_id = db.Column(db.Integer, db.ForeignKey("admissions.id"))

    complaint_text = db.Column(db.Text)

    admission = db.relationship("Admission", back_populates="complaints")


class Vital(db.Model):
    __tablename__ = "vitals"

    id = db.Column(db.Integer, primary_key=True)
    admission_id = db.Column(db.Integer, db.ForeignKey("admissions.id"))

    record_date = db.Column(db.Date)
    systolic_bp = db.Column(db.Integer)
    diastolic_bp = db.Column(db.Integer)
    pulse = db.Column(db.Integer)
    spo2 = db.Column(db.Integer)
    rbs = db.Column(db.Integer)
    temperature = db.Column(db.String(20))

    recorded_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    admission = db.relationship("Admission", back_populates="vitals")


class ProgressNote(db.Model):
    __tablename__ = "progress_notes"

    id = db.Column(db.Integer, primary_key=True)
    admission_id = db.Column(db.Integer, db.ForeignKey("admissions.id"))

    note_date = db.Column(db.Date)
    note_text = db.Column(db.Text)

    recorded_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    admission = db.relationship("Admission", back_populates="progress_notes")


class Medicine(db.Model):
    __tablename__ = "medicines"

    id = db.Column(db.Integer, primary_key=True)
    medicine_name = db.Column(db.String(255), index=True)
    type = db.Column(db.String(50))
    strength = db.Column(db.String(100))
    unit = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    medication_records = db.relationship("MedicationAdministration", back_populates="medicine")


class MedicationAdministration(db.Model):
    __tablename__ = "medication_administration"

    id = db.Column(db.Integer, primary_key=True)

    admission_id = db.Column(db.Integer, db.ForeignKey("admissions.id"), nullable=True)
    opd_visit_id = db.Column(db.Integer, db.ForeignKey("opd_visits.id"), nullable=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey("medicines.id"))

    dosage = db.Column(db.String(100))
    route = db.Column(db.String(50))
    frequency = db.Column(db.String(50))

    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)

    notes = db.Column(db.Text)
    prescribed_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    admission = db.relationship("Admission", back_populates="medications")
    opd_visit = db.relationship("OPDVisit", back_populates="medications")
    medicine = db.relationship("Medicine", back_populates="medication_records")


class DischargeRecord(db.Model):
    __tablename__ = "discharge_records"

    id = db.Column(db.Integer, primary_key=True)
    admission_id = db.Column(db.Integer, db.ForeignKey("admissions.id"), unique=True)

    discharge_date = db.Column(db.Date)
    medicine_days_prescribed = db.Column(db.Integer)

    final_diagnosis = db.Column(db.Text)
    treatment_summary = db.Column(db.Text)
    follow_up_instructions = db.Column(db.Text)
    diet_instructions = db.Column(db.Text)

    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    admission = db.relationship("Admission", back_populates="discharge_record")


class FollowUpRecord(db.Model):
    __tablename__ = "follow_up_records"

    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"))
    admission_id = db.Column(db.Integer, db.ForeignKey("admissions.id"))

    followup_date = db.Column(db.Date)
    followup_status = db.Column(db.String(100))

    notes = db.Column(db.Text)
    recorded_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship("Patient", back_populates="followups")
    admission = db.relationship("Admission", back_populates="followups")


class Reminder(db.Model):
    __tablename__ = "reminders"

    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"))
    admission_id = db.Column(db.Integer, db.ForeignKey("admissions.id"), nullable=True)

    reminder_type = db.Column(db.String(50))
    reminder_date = db.Column(db.Date)
    status = db.Column(db.String(20))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship("Patient", back_populates="reminders")
    admission = db.relationship("Admission", back_populates="reminders")



from datetime import datetime


class SOPDocument(db.Model):
    __tablename__ = "sop_documents"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(100), default="General")
    uploaded_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ConsultationRecord(db.Model):
    __tablename__ = "consultation_records"

    id = db.Column(db.Integer, primary_key=True)

    appointment_id = db.Column(db.Integer, db.ForeignKey("appointments.id"), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False)

    audio_file_path = db.Column(db.String(255), nullable=True)
    transcript_text = db.Column(db.Text, nullable=True)

    structured_notes_json = db.Column(db.JSON, nullable=True)
    summary = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)