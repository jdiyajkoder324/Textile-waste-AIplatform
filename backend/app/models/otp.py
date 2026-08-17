# app/models/otp.py
import enum
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database.base import Base


class OTPPurpose(str, enum.Enum):
    LOGIN_2FA = "login_2fa"
    PASSWORD_RESET = "password_reset"


class OTPVerification(Base):
    __tablename__ = "otp_verifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # never store the raw OTP — only its hash
    otp_hash = Column(String, nullable=False)

    purpose = Column(Enum(OTPPurpose), default=OTPPurpose.LOGIN_2FA, nullable=False)

    attempts = Column(Integer, default=0, nullable=False)
    max_attempts = Column(Integer, default=5, nullable=False)

    is_verified = Column(Boolean, default=False, nullable=False)
    is_invalidated = Column(Boolean, default=False, nullable=False)  # set True after resend/use

    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_sent_at = Column(DateTime, default=datetime.utcnow, nullable=False)  # for resend cooldown

    user = relationship("User", backref="otp_verifications")