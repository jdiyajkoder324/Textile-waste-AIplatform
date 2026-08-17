# app/schemas/otp.py
from pydantic import BaseModel


class LoginStep1Request(BaseModel):
    email: str          # matches User.email — your login uses email, not username
    password: str


class LoginStep1Response(BaseModel):
    message: str
    otp_session_id: int
    email_hint: str     # masked, e.g. "d***@gmail.com"
    expires_in_seconds: int


class OTPVerifyRequest(BaseModel):
    otp_session_id: int
    otp: str


class OTPResendRequest(BaseModel):
    otp_session_id: int


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"