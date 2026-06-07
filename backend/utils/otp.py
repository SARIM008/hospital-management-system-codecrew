import random
from datetime import datetime, timedelta
from models import db, OTP


def generate_otp():
    return str(random.randint(1000, 9999))


def send_otp(phone):
    code = generate_otp()
    otp = OTP(
        phone=phone,
        otp_code=code,
        expires_at=datetime.utcnow() + timedelta(minutes=5),
        verified=False
    )
    db.session.add(otp)
    db.session.commit()
    print(f"OTP for {phone}: {code}")
    return True


def verify_otp(phone, code):
    otp = OTP.query.filter_by(phone=phone, otp_code=code, verified=False).order_by(OTP.created_at.desc()).first()
    if not otp:
        return False
    if otp.expires_at < datetime.utcnow():
        return False
    otp.verified = True
    db.session.commit()
    return True


def is_phone_verified(phone):
    otp = OTP.query.filter_by(phone=phone, verified=True).order_by(OTP.created_at.desc()).first()
    return True if otp else False