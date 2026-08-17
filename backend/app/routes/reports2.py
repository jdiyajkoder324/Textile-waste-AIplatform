from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.report_history import ReportHistory, ReportType, ReportFormat
from app.schemas.report_history import ReportHistoryListResponse
from app.services.report_export_service import generate_pdf_report, generate_excel_report

router = APIRouter(prefix="/api/reports", tags=["Reports & Export"])

MEDIA_TYPES = {
    "pdf": "application/pdf",
    "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}
EXTENSIONS = {"pdf": "pdf", "excel": "xlsx"}

VALID_TYPES = {t.value for t in ReportType}


@router.get("/generate")
def generate_report(
    report_type: str = Query(..., description="waste_classification | recycling | sustainability | environmental_impact | circular_economy"),
    format: str = Query("pdf", pattern="^(pdf|excel)$"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if report_type not in VALID_TYPES:
        raise HTTPException(400, f"Invalid report_type. Must be one of: {', '.join(VALID_TYPES)}")

    try:
        if format == "pdf":
            file_bytes = generate_pdf_report(db, report_type, start_date, end_date, current_user)
        else:
            file_bytes = generate_excel_report(db, report_type, start_date, end_date, current_user)
    except Exception as exc:
        raise HTTPException(500, f"Report generation failed: {exc}")

    ext = EXTENSIONS[format]
    file_name = f"{report_type}-report-{date.today().isoformat()}.{ext}"

    record = ReportHistory(
        user_id=current_user.id,
        report_type=ReportType(report_type),
        format=ReportFormat.PDF if format == "pdf" else ReportFormat.EXCEL,
        date_range_start=start_date,
        date_range_end=end_date,
        file_name=file_name,
        file_data=file_bytes,
    )
    db.add(record)
    db.commit()

    return Response(
        content=file_bytes,
        media_type=MEDIA_TYPES[format],
        headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
    )


@router.get("/history", response_model=ReportHistoryListResponse)
def get_report_history(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(ReportHistory)
    if current_user.role != "Admin":
        query = query.filter(ReportHistory.user_id == current_user.id)

    total = query.count()
    items = query.order_by(ReportHistory.created_at.desc()).limit(limit).all()
    return ReportHistoryListResponse(items=items, total=total)


@router.get("/history/{report_id}/download")
def download_past_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = db.query(ReportHistory).filter(ReportHistory.id == report_id).first()
    if not record:
        raise HTTPException(404, "Report not found")
    if record.user_id != current_user.id and current_user.role != "Admin":
        raise HTTPException(403, "Not authorized")

    fmt = record.format.value
    return Response(
        content=record.file_data,
        media_type=MEDIA_TYPES[fmt],
        headers={"Content-Disposition": f'attachment; filename="{record.file_name}"'},
    )