from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash, generate_password_hash

from models import db, User, Patient
from routes.common import serialize_patient, serialize_user

auth_bp = Blueprint("auth_bp", __name__)


@auth_bp.post("/signup")
def signup():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    phone = (data.get("phone") or "")
    password = data.get("password") or ""
    age = data.get("age")
    gender = data.get("gender")
    address = data.get("address")

    if not name or not email or not phone or not password:
        return jsonify({"error": "name, email, phone and password are required"}), 400

    if User.query.filter((User.email == email) | (User.phone == phone)).first():
        return jsonify({"error": "email or phone already exists"}), 400

    user = User(
        name=name,
        email=email,
        phone=phone,
        password_hash=generate_password_hash(password),
        role="patient",
    )
    db.session.add(user)
    db.session.flush()

    patient = Patient(
        user_id=user.id,
        age=age,
        gender=gender,
        address=address,
    )
    db.session.add(patient)
    db.session.commit()

    return jsonify({
        "message": "Patient registered successfully",
        "user": serialize_user(user),
        "patient": serialize_patient(patient),
    }), 201


@auth_bp.post("/login")
def login():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not password or (not email):
        return jsonify({"error": "email or phone, and password are required"}), 400

    user = None
    if email:
        user = User.query.filter_by(email=email).first()
    

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})

    return jsonify({
        "token": token,
        "user": serialize_user(user),
    }), 200
