from datetime import datetime, timedelta
from jose import jwt
import os
from passlib.context import CryptContext
import os

SECRET_KEY = os.getenv("SECRET_KEY", "secret123")
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# password hash
def hash_password(password: str):
    return pwd_context.hash(password)


# verify password
def verify_password(password: str, hashed: str):
    return pwd_context.verify(password, hashed)


# create token
def create_access_token(data: dict, expires_minutes: int = 30):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)