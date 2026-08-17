from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from app.database.base import Base


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)

    batch_id = Column(String(50), nullable=False)

    recommendation = Column(String(500))

    created_at = Column(DateTime, default=datetime.utcnow)