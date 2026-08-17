'''from fastapi import APIRouter
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.auth import RegisterRequest, LoginRequest
from fastapi import Depends
from app.core.auth import get_current_user
from fastapi import HTTPException

router = APIRouter()

fake_db = {}

@router.post("/register")
def register(data: RegisterRequest):

    hashed = hash_password(data.password)
    fake_db[data.email] = hashed

    return {"message": "User registered"}

@router.post("/login")
def login(data: LoginRequest):

    if data.email not in fake_db:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(data.password, fake_db[data.email]):
        raise HTTPException(status_code=400, detail="Wrong password")

    token = create_access_token({"sub": data.email})

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.get("/profile")
def profile(
    user_email: str = Depends(get_current_user)
):

    return {
        "message": "Profile Access Granted",
        "email": user_email
    }
    '''

"""
Authentication routes: register & login. JWT-based, matching the platform's
existing auth pattern. Authentication is optional for analysis endpoints but
enables per-user history tracking when used.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import UserCreate, UserLogin, Token, UserOut
from utils.security import hash_password, verify_password, create_access_token
from app.models.otp import OTPPurpose
from app.services.otp_service import create_and_send_otp, resend_otp, verify_otp, mask_email
from app.schemas.otp import LoginStep1Request, LoginStep1Response, OTPVerifyRequest, OTPResendRequest, TokenResponse



router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(
        (User.username == payload.username) | (User.email == payload.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already registered")

    user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.id, "username": user.username})
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token({"sub": user.id, "username": user.username})
    return Token(access_token=token, user=UserOut.model_validate(user))



@router.post("/login", response_model=LoginStep1Response)
def login_step1(payload: LoginStep1Request, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.username, payload.password)  # <- your existing function
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid username or password")

    otp_record = create_and_send_otp(db, user, purpose=OTPPurpose.LOGIN_2FA)

    return LoginStep1Response(
        message="OTP sent to your registered email",
        otp_session_id=otp_record.id,
        email_hint=mask_email(user.email),
        expires_in_seconds=300,
    )


@router.post("/verify-otp", response_model=TokenResponse)
def login_step2(payload: OTPVerifyRequest, db: Session = Depends(get_db)):
    user = verify_otp(db, payload.otp_session_id, payload.otp)
    access_token = create_access_token({"sub": str(user.id), "role": user.role})  # <- your existing JWT function
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