"""
Route: /api/analysis-report

Generates a downloadable report (PDF, CSV, or JSON) for a fully-analyzed
image and stores a copy of the generated file in the Reports table.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from models import (
    ImageAnalysis, MaterialClassification, WasteClassification,
    RecyclabilityAssessment, RecyclingRecommendation, Report,
)
from services.report_engine import generate_pdf_report, generate_csv_report, generate_json_report

router = APIRouter(prefix="/api", tags=["Reports"])

MEDIA_TYPES = {
    "pdf": "application/pdf",
    "csv": "text/csv",
    "json": "application/json",
}


@router.get("/analysis-report")
def get_analysis_report(
    image_id: str,
    format: str = Query("pdf", pattern="^(pdf|csv|json)$"),
    db: Session = Depends(get_db),
):
    image = db.query(ImageAnalysis).filter(ImageAnalysis.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    material = db.query(MaterialClassification).filter(MaterialClassification.image_id == image_id).first()
    waste = db.query(WasteClassification).filter(WasteClassification.image_id == image_id).first()
    recyclability = db.query(RecyclabilityAssessment).filter(RecyclabilityAssessment.image_id == image_id).first()
    recommendation = db.query(RecyclingRecommendation).filter(
        RecyclingRecommendation.image_id == image_id
    ).first()

    if format == "pdf":
        file_bytes = generate_pdf_report(image, material, waste, recyclability, recommendation)
    elif format == "csv":
        file_bytes = generate_csv_report(image, material, waste, recyclability, recommendation)
    else:
        file_bytes = generate_json_report(image, material, waste, recyclability, recommendation)

    file_name = f"analysis-report-{image_id[:8]}.{format}"

    report_record = Report(
        image_id=image.id, report_format=format, file_data=file_bytes, file_name=file_name,
    )
    db.add(report_record)
    db.commit()

    return Response(
        content=file_bytes,
        media_type=MEDIA_TYPES[format],
        headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
    )
