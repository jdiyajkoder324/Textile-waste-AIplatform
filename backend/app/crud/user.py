from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import verify_password

VALID_SELF_REGISTER_ROLES = {"Industry", "Recycler"}


def create_user(db: Session, user):

    # Only Industry/Recycler can self-register with a role.
    # Admin accounts should be created directly in the DB / by another Admin,
    # not through the public register endpoint.
    role = getattr(user, "role", None)
    if role not in VALID_SELF_REGISTER_ROLES:
        role = "Industry"

    db_user = User(
        name=user.name,
        email=user.email,
        password=user.password,
        role=role,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

def authenticate_user(db: Session, email: str, password: str):

    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user:
        return None

    result = verify_password(password, user.password)

    if not result:
        return None

    return user
