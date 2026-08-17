# app/services/otp_service.py
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.otp import OTPVerification, OTPPurpose
from app.models.user import User
from app.core.otp_utils import (
    generate_otp, hash_otp, verify_otp_hash,
    get_expiry_time, is_expired, cooldown_remaining_seconds,
)
from app.core.email_utils import send_otp_email


def mask_email(email: str) -> str:
    name, domain = email.split("@")
    if len(name) <= 2:
        masked = name[0] + "*"
    else:
        masked = name[0] + "*" * (len(name) - 2) + name[-1]
    return f"{masked}@{domain}"


def create_and_send_otp(db: Session, user: User, purpose: OTPPurpose = OTPPurpose.LOGIN_2FA) -> OTPVerification:
    # invalidate any previous unverified OTPs for this user+purpose
    db.query(OTPVerification).filter(
        OTPVerification.user_id == user.id,
        OTPVerification.purpose == purpose,
        OTPVerification.is_verified == False,
        OTPVerification.is_invalidated == False,
    ).update({"is_invalidated": True})

    otp_plain = generate_otp()
    record = OTPVerification(
        user_id=user.id,
        otp_hash=hash_otp(otp_plain),
        purpose=purpose,
        expires_at=get_expiry_time(),
        last_sent_at=datetime.utcnow(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    send_otp_email(user.email, otp_plain, purpose=purpose.value)
    return record


def resend_otp(db: Session, otp_session_id: int) -> OTPVerification:
    record = db.query(OTPVerification).filter(OTPVerification.id == otp_session_id).first()
    if not record or record.is_invalidated or record.is_verified:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid or expired session. Please log in again.")

    remaining = cooldown_remaining_seconds(record.last_sent_at)
    if remaining > 0:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, f"Please wait {remaining}s before resending.")

    user = db.query(User).filter(User.id == record.user_id).first()
    record.is_invalidated = True
    db.commit()

    return create_and_send_otp(db, user, purpose=record.purpose)


def verify_otp(db: Session, otp_session_id: int, otp_input: str) -> User:
    record = db.query(OTPVerification).filter(OTPVerification.id == otp_session_id).first()
    if not record or record.is_invalidated:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid or expired session. Please log in again.")

    if record.is_verified:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "OTP already used.")

    if is_expired(record.expires_at):
        record.is_invalidated = True
        db.commit()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "OTP expired. Please request a new one.")

    if record.attempts >= record.max_attempts:
        record.is_invalidated = True
        db.commit()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Too many incorrect attempts. Please request a new OTP.")

    if not verify_otp_hash(otp_input, record.otp_hash):
        record.attempts += 1
        db.commit()
        remaining = record.max_attempts - record.attempts
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Incorrect OTP. {remaining} attempt(s) remaining.")

    record.is_verified = True
    db.commit()

    user = db.query(User).filter(User.id == record.user_id).first()
    return user