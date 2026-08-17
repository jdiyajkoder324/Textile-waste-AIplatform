from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.report_history import ReportType, ReportFormat


class ReportHistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    report_type: ReportType
    format: ReportFormat
    date_range_start: Optional[date]
    date_range_end: Optional[date]
    file_name: str
    created_at: datetime


class ReportHistoryListResponse(BaseModel):
    items: list[ReportHistoryOut]
    total: int