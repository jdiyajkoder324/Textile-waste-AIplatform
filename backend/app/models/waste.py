from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.base import Base


class Waste(Base):

    __tablename__ = "waste_batches"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # --- Ownership (NEW) ---
    # Nullable=True so existing rows created before this migration don't break.
    # New records will always have this set by the API layer.
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        index=True
    )

    # --- Original fields (kept for backward compatibility with Dashboard.jsx) ---
    batch_id = Column(
        String,
        unique=True,
        index=True
    )

    source = Column(
        String,
        nullable=True
    )

    collection_date = Column(
        String,
        nullable=True
    )

    # --- Inventory fields required by Milestone 1 (NEW) ---
    title = Column(
        String,
        nullable=True
    )

    description = Column(
        Text,
        nullable=True
    )

    fabric_type = Column(
        String
    )

    material = Column(
        String,
        nullable=True
    )

    color = Column(
        String,
        nullable=True
    )

    quantity = Column(
        Float
    )

    condition = Column(
        String
    )

    location = Column(
        String,
        nullable=True
    )

    # Kept the original column name (image_path) so nothing that already
    # reads/writes it breaks. The Inventory API exposes this as "image".
    image_path = Column(
        String,
        nullable=True
    )

    status = Column(
        String,
        default="Pending"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=True
    )

    owner = relationship("User", backref="waste_items")
