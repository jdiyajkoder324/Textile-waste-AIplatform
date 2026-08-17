"""
Milestone 1 — Waste batch CRUD + Inventory.

Reconstructed to match:
  - app/models/waste.py (the Waste model)
  - frontend services/api.js: getWastes, createWaste, updateWaste, deleteWaste,
    getInventory, uploadWasteImage

If you have a git history / backup of the ORIGINAL routes/waste.py, prefer
that over this file — this is a best-effort reconstruction based on the
Waste model's fields and what api.js expects the endpoints to look like.
"""
import os
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.waste import Waste

router = APIRouter(prefix="/waste", tags=["Waste"])

UPLOAD_DIR = "uploads/waste_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class WasteIn(BaseModel):
    batch_id: str
    fabric_type: str
    source: Optional[str] = None
    quantity: float
    condition: str
    collection_date: Optional[str] = None
    image_path: Optional[str] = ""
    status: Optional[str] = "Pending"
    title: Optional[str] = None
    description: Optional[str] = None
    material: Optional[str] = None
    color: Optional[str] = None
    location: Optional[str] = None


def _serialize(w: Waste) -> dict:
    return {
        "id": w.id,
        "batch_id": w.batch_id,
        "fabric_type": w.fabric_type,
        "source": w.source,
        "quantity": w.quantity,
        "condition": w.condition,
        "collection_date": w.collection_date,
        "image_path": w.image_path,
        "status": w.status,
        "title": w.title,
        "description": w.description,
        "material": w.material,
        "color": w.color,
        "location": w.location,
        "created_at": w.created_at.isoformat() if w.created_at else None,
    }


@router.get("/")
def list_waste(
    search: Optional[str] = None,
    fabric_type: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(1000, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    query = db.query(Waste)

    if search:
        like = f"%{search}%"
        query = query.filter(
            (Waste.batch_id.ilike(like)) | (Waste.source.ilike(like)) | (Waste.title.ilike(like))
        )
    if fabric_type:
        query = query.filter(Waste.fabric_type == fabric_type)
    if status:
        query = query.filter(Waste.status == status)

    total = query.count()
    items = (
        query.order_by(Waste.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    total_pages = max(1, (total + page_size - 1) // page_size)

    return {
        "items": [_serialize(w) for w in items],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.post("/")
def create_waste(payload: WasteIn, db: Session = Depends(get_db)):
    existing = db.query(Waste).filter(Waste.batch_id == payload.batch_id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Batch ID '{payload.batch_id}' already exists")

    waste = Waste(**payload.model_dump())
    db.add(waste)
    db.commit()
    db.refresh(waste)
    return _serialize(waste)


@router.put("/{waste_id}")
def update_waste(waste_id: int, payload: WasteIn, db: Session = Depends(get_db)):
    waste = db.query(Waste).filter(Waste.id == waste_id).first()
    if not waste:
        raise HTTPException(status_code=404, detail="Waste batch not found")

    for key, value in payload.model_dump().items():
        setattr(waste, key, value)

    db.commit()
    db.refresh(waste)
    return _serialize(waste)


@router.delete("/{waste_id}")
def delete_waste(waste_id: int, db: Session = Depends(get_db)):
    waste = db.query(Waste).filter(Waste.id == waste_id).first()
    if not waste:
        raise HTTPException(status_code=404, detail="Waste batch not found")

    db.delete(waste)
    db.commit()
    return {"success": True, "message": "Waste batch deleted"}


@router.post("/upload-image")
async def upload_waste_image(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1] or ".jpg"
    unique_name = f"{uuid.uuid4().hex}{ext}"
    dest_path = os.path.join(UPLOAD_DIR, unique_name)

    content = await file.read()
    with open(dest_path, "wb") as f:
        f.write(content)

    return {"image_path": f"/uploads/waste_images/{unique_name}"}
