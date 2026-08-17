from sqlalchemy import Column, Integer, String, Float

from app.database.base import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)

    batch_id = Column(String(50), nullable=False)

    material = Column(String(100))

    recyclability = Column(String(100))

    confidence = Column(Float)