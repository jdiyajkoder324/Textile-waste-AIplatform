# app/core/otp_utils.py
import secrets
import hashlib
from datetime import datetime, timedelta

OTP_LENGTH = 6
OTP_EXPIRY_MINUTES = 5
OTP_RESEND_COOLDOWN_SECONDS = 60
OTP_MAX_ATTEMPTS = 5


def generate_otp() -> str:
    """Cryptographically secure numeric OTP, e.g. '482913'."""
    return "".join(secrets.choice("0123456789") for _ in range(OTP_LENGTH))


def hash_otp(otp: str) -> str:
    """One-way hash — never store the raw OTP in DB."""
    return hashlib.sha256(otp.encode()).hexdigest()


def verify_otp_hash(otp: str, otp_hash: str) -> bool:
    return secrets.compare_digest(hash_otp(otp), otp_hash)


def get_expiry_time() -> datetime:
    return datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)


def is_expired(expires_at: datetime) -> bool:
    return datetime.utcnow() > expires_at


def cooldown_remaining_seconds(last_sent_at: datetime) -> int:
    elapsed = (datetime.utcnow() - last_sent_at).total_seconds()
    remaining = OTP_RESEND_COOLDOWN_SECONDS - elapsed
    return max(0, int(remaining))