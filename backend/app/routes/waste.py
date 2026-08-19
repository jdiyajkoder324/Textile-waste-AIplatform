"""
Milestone 1 — Waste batch CRUD + Inventory.

Fixed version: uses the proper WasteCreate / WasteUpdate schemas
(from app/schemas/waste.py) instead of a single strict WasteIn model.
This is what was causing 422 errors on PUT /waste/{id} — the update
endpoint was validating against a model that required batch_id, even
though updates should only need to send the fields being changed.

user_id fix: create_waste now wires the authenticated user via
app.core.auth.get_current_user (the same dependency analytics.py uses),
so every new batch is correctly attributed. Previously user_id was
never set, which is why Manufacturer/Recycler/Admin dashboards — which
filter by current_user.id — showed "No batches logged yet" even though
batches existed in the table.
"""
import os
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.waste import Waste
from app.schemas.waste import WasteCreate, WasteUpdate, WasteResponse, PaginatedWasteResponse

router = APIRouter(prefix="/waste", tags=["Waste"])

UPLOAD_DIR = "uploads/waste_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)


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


def _generate_batch_id(db: Session) -> str:
    # e.g. TX-4821 style, matching the placeholder shown in the UI.
    # Retries on the rare collision instead of trusting one random draw.
    for _ in range(5):
        candidate = f"TX-{uuid.uuid4().hex[:4].upper()}"
        if not db.query(Waste).filter(Waste.batch_id == candidate).first():
            return candidate
    # Fallback: fully unique, can't collide.
    return f"TX-{uuid.uuid4().hex[:8].upper()}"


@router.post("/")
def create_waste(
    payload: WasteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = payload.model_dump()

    # Always attribute the batch to whoever is logged in. This was
    # previously missing entirely, so every batch got user_id=None and
    # never showed up on the role dashboards (which filter by user_id).
    data["user_id"] = current_user.id

    # The DB column "batch_id" is NOT NULL, but the schema allows it to be
    # omitted (e.g. from the Quick Log form). Auto-generate one instead of
    # letting the insert hit an IntegrityError.
    if not data.get("batch_id"):
        data["batch_id"] = _generate_batch_id(db)
    else:
        existing = db.query(Waste).filter(Waste.batch_id == data["batch_id"]).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Batch ID '{data['batch_id']}' already exists")

    waste = Waste(**data)
    db.add(waste)
    db.commit()
    db.refresh(waste)
    return _serialize(waste)

'''
@router.put("/{waste_id}")
def update_waste(waste_id: int, payload: WasteUpdate, db: Session = Depends(get_db)):
    waste = db.query(Waste).filter(Waste.id == waste_id).first()
    if not waste:
        raise HTTPException(status_code=404, detail="Waste batch not found")

    # exclude_unset=True: only touch fields the client actually sent,
    # so a partial edit (no batch_id, no source, etc.) doesn't wipe
    # out existing values with None.
    update_data = payload.model_dump(exclude_unset=True)

    if "batch_id" in update_data and update_data["batch_id"]:
        conflict = (
            db.query(Waste)
            .filter(Waste.batch_id == update_data["batch_id"], Waste.id != waste_id)
            .first()
        )
        if conflict:
            raise HTTPException(status_code=400, detail=f"Batch ID '{update_data['batch_id']}' already exists")

    for key, value in update_data.items():
        setattr(waste, key, value)

    db.commit()
    db.refresh(waste)
    return _serialize(waste)'''


'''@router.delete("/{waste_id}")
def delete_waste(waste_id: int, db: Session = Depends(get_db)):
    waste = db.query(Waste).filter(Waste.id == waste_id).first()
    if not waste:
        raise HTTPException(status_code=404, detail="Waste batch not found")

    db.delete(waste)
    db.commit()
    return {"success": True, "message": "Waste batch deleted"}'''


@router.post("/upload-image")
async def upload_waste_image(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1] or ".jpg"
    unique_name = f"{uuid.uuid4().hex}{ext}"
    dest_path = os.path.join(UPLOAD_DIR, unique_name)

    content = await file.read()
    with open(dest_path, "wb") as f:
        f.write(content)

    return {"image_path": f"/uploads/waste_images/{unique_name}"}

@router.put("/{waste_id}")
def update_waste(
    waste_id: int,
    payload: WasteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    waste = db.query(Waste).filter(Waste.id == waste_id).first()
    if not waste:
        raise HTTPException(status_code=404, detail="Waste batch not found")

    # Only the batch owner or an Admin can edit it.
    if current_user.role != "Admin" and waste.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this batch")

    update_data = payload.model_dump(exclude_unset=True)

    if "batch_id" in update_data and update_data["batch_id"]:
        conflict = (
            db.query(Waste)
            .filter(Waste.batch_id == update_data["batch_id"], Waste.id != waste_id)
            .first()
        )
        if conflict:
            raise HTTPException(status_code=400, detail=f"Batch ID '{update_data['batch_id']}' already exists")

    for key, value in update_data.items():
        setattr(waste, key, value)

    db.commit()
    db.refresh(waste)
    return _serialize(waste)


@router.delete("/{waste_id}")
def delete_waste(
    waste_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    waste = db.query(Waste).filter(Waste.id == waste_id).first()
    if not waste:
        raise HTTPException(status_code=404, detail="Waste batch not found")

    # Only the batch owner or an Admin can delete it.
    if current_user.role != "Admin" and waste.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this batch")

    db.delete(waste)
    db.commit()
    return {"success": True, "message": "Waste batch deleted"}