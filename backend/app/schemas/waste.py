from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime, date


class WasteBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    fabric_type: str
    material: Optional[str] = None
    color: Optional[str] = None
    quantity: float
    condition: str
    location: Optional[str] = None
    status: Optional[str] = "Pending"

    # Legacy fields kept optional so the existing Dashboard.jsx keeps working
    batch_id: Optional[str] = None
    source: Optional[str] = None
    collection_date: Optional[str] = None
    image_path: Optional[str] = None


class WasteCreate(WasteBase):
    pass


class WasteUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    fabric_type: Optional[str] = None
    material: Optional[str] = None
    color: Optional[str] = None
    quantity: Optional[float] = None
    condition: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None
    batch_id: Optional[str] = None
    source: Optional[str] = None
    collection_date: Optional[str] = None
    image_path: Optional[str] = None


class WasteResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    fabric_type: Optional[str] = None
    material: Optional[str] = None
    color: Optional[str] = None
    quantity: Optional[float] = None
    condition: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None
    batch_id: Optional[str] = None
    source: Optional[str] = None
    collection_date: Optional[str] = None
    image_path: Optional[str] = None
    created_at: Optional[datetime] = None

    @field_validator("collection_date", mode="before")
    @classmethod
    def _coerce_collection_date(cls, value):
        # Your DB column is physically a DATE type even though the model
        # treats it as String — this converts whatever comes back (a
        # real date object OR a plain string) into a clean string.
        if value is None:
            return value
        if isinstance(value, (date, datetime)):
            return value.isoformat()
        return str(value)

    class Config:
        from_attributes = True


class PaginatedWasteResponse(BaseModel):
    items: list[WasteResponse]
    total: int
    page: int
    page_size: int
    total_pages: int