"""
Admin-only User Management — list, update role, delete platform users.
Mirrors the dict-serialization pattern used in app/routes/waste.py.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.auth import require_role
from app.models.user import User

router = APIRouter(prefix="/api/admin/users", tags=["Admin - User Management"])


class UserRoleUpdate(BaseModel):
    role: str  # "Industry" | "Recycler" | "Admin"


def _serialize(u: User) -> dict:
    return {
        "id": u.id,
        "name": u.name,
        "email": u.email,
        "role": u.role,
    }


@router.get("")
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Admin")),
):
    users = db.query(User).order_by(User.id).all()
    return {"items": [_serialize(u) for u in users], "total": len(users)}


@router.put("/{user_id}/role")
def update_user_role(
    user_id: int,
    payload: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Admin")),
):
    if payload.role not in ("Industry", "Recycler", "Admin"):
        raise HTTPException(status_code=400, detail="Invalid role")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = payload.role
    db.commit()
    db.refresh(user)
    return _serialize(user)


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Admin")),
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot delete your own account")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"success": True, "message": "User deleted"}