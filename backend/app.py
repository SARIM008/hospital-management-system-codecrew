from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from werkzeug.security import generate_password_hash

from models import db, User
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.public_doctor_routes import public_doctor_bp
from routes.doctor_routes import doctor_bp
from routes.appointment_routes import appointment_bp
from routes.opd_routes import opd_bp
from routes.admission_routes import admission_bp
from routes.medicine_routes import medicine_bp
from routes.sop_routes import sop_bp


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///hospital.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = "super-secret-change-this"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False

    db.init_app(app)
    CORS(app)
    JWTManager(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(public_doctor_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(appointment_bp)
    app.register_blueprint(opd_bp)
    app.register_blueprint(admission_bp)
    app.register_blueprint(medicine_bp)
    app.register_blueprint(sop_bp)

    with app.app_context():
        db.create_all()
        existing_admin = User.query.filter_by(phone="admin").first()
        if not existing_admin:
            admin = User(
                name="Admin",
                email="admin@hospital.com",
                phone="123",
                password_hash=generate_password_hash("123"),
                role="admin",
            )
            db.session.add(admin)
            db.session.commit()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
