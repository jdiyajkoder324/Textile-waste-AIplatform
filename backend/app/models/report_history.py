import enum
from datetime import date, datetime
from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Enum, LargeBinary
from sqlalchemy.orm import relationship
from app.database.base import Base


class ReportType(str, enum.Enum):
    WASTE_CLASSIFICATION = "waste_classification"
    RECYCLING = "recycling"
    SUSTAINABILITY = "sustainability"
    ENVIRONMENTAL_IMPACT = "environmental_impact"
    CIRCULAR_ECONOMY = "circular_economy"


class ReportFormat(str, enum.Enum):
    PDF = "pdf"
    EXCEL = "excel"


class ReportHistory(Base):
    __tablename__ = "report_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    report_type = Column(Enum(ReportType), nullable=False)
    format = Column(Enum(ReportFormat), nullable=False)

    date_range_start = Column(Date, nullable=True)
    date_range_end = Column(Date, nullable=True)

    file_name = Column(String(255), nullable=False)
    file_data = Column(LargeBinary, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = relationship("User", backref="report_history")