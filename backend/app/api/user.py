from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.security import hash_password, verify_password, create_access_token

from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserLogin,
)

from app.crud.user import (
    create_user,
    authenticate_user,
)

from app.core.auth import get_current_user
from app.models.user import User
from app.models.otp import OTPPurpose
from app.services.otp_service import create_and_send_otp, resend_otp, verify_otp, mask_email
from app.schemas.otp import (
    LoginStep1Request, LoginStep1Response,
    OTPVerifyRequest, OTPResendRequest, TokenResponse,
)

router = APIRouter()



@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(user.password)
    user.password = hashed

    return create_user(db, user)


@router.post("/login", response_model=LoginStep1Response)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    db_user = authenticate_user(db, payload.email, payload.password)

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    otp_record = create_and_send_otp(db, db_user, purpose=OTPPurpose.LOGIN_2FA)

    return LoginStep1Response(
        message="OTP sent to your registered email",
        otp_session_id=otp_record.id,
        email_hint=mask_email(db_user.email),
        expires_in_seconds=300,
    )


@router.post("/verify-otp", response_model=TokenResponse)
def login_step2(payload: OTPVerifyRequest, db: Session = Depends(get_db)):
    user = verify_otp(db, payload.otp_session_id, payload.otp)
    access_token = create_access_token({"sub": user.email})
    return TokenResponse(access_token=access_token)


@router.post("/resend-otp", response_model=LoginStep1Response)
def resend_otp_endpoint(payload: OTPResendRequest, db: Session = Depends(get_db)):
    otp_record = resend_otp(db, payload.otp_session_id)
    user = db.query(User).filter(User.id == otp_record.user_id).first()
    return LoginStep1Response(
        message="OTP resent",
        otp_session_id=otp_record.id,
        email_hint=mask_email(user.email),
        expires_in_seconds=300,
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user