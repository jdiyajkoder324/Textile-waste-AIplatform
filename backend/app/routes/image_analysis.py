"""
Routes: /api/upload-image, /api/image-analysis

Uploading an image runs the ENTIRE analysis pipeline (image -> material ->
waste -> recyclability -> recommendation) in one call so the frontend can
render the full dashboard immediately after upload. /api/image-analysis
exposes the low-level image-analysis-only result for a given image_id.
"""
from typing import Optional

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Form
from sqlalchemy.orm import Session

from database import get_db
from config import settings
from models import ImageAnalysis
from schemas import ImageAnalysisOut, FullAnalysisOut, MessageResponse
from utils.dependencies import get_current_user_optional
from services.pipeline import run_full_pipeline

router = APIRouter(prefix="/api", tags=["Image Analysis"])


def _validate_image(file: UploadFile, content: bytes):
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported image type: {file.content_type}")
    size_mb = len(content) / (1024 * 1024)
    if size_mb > settings.MAX_IMAGE_SIZE_MB:
        raise HTTPException(status_code=400, detail=f"Image exceeds {settings.MAX_IMAGE_SIZE_MB}MB limit")


@router.post("/upload-image", response_model=FullAnalysisOut)
async def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    """Uploads a textile image and runs the full analysis pipeline."""
    content = await file.read()
    _validate_image(file, content)

    image_record = ImageAnalysis(
        user_id=current_user.id if current_user else None,
        filename=file.filename,
        content_type=file.content_type,
        image_data=content,
        file_size_bytes=len(content),
        status="processing",
    )
    db.add(image_record)
    db.commit()
    db.refresh(image_record)

    try:
        image, material, waste, recyclability, recommendation = run_full_pipeline(db, image_record, content)
    except Exception as exc:
        image_record.status = "failed"
        db.commit()
        raise HTTPException(status_code=422, detail=f"Analysis failed: {exc}") from exc

    return FullAnalysisOut(
        image_analysis=ImageAnalysisOut.model_validate(image),
        material_classification=material,
        waste_classification=waste,
        recyclability_assessment=recyclability,
        recycling_recommendation=recommendation,
    )


@router.post("/image-analysis", response_model=ImageAnalysisOut)
async def image_analysis_only(
    image_id: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    """
    Returns image-analysis-only output (texture/color/damage/contamination).
    Accepts either an existing image_id, or a fresh file upload (analyzed
    without persisting downstream material/waste records).
    """
    if image_id:
        record = db.query(ImageAnalysis).filter(ImageAnalysis.id == image_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="Image not found")
        return ImageAnalysisOut.model_validate(record)

    if not file:
        raise HTTPException(status_code=400, detail="Provide either image_id or file")

    content = await file.read()
    _validate_image(file, content)
    from services.image_engine import run_image_analysis
    result = run_image_analysis(content, file.filename, file.content_type)

    record = ImageAnalysis(
        filename=file.filename,
        content_type=file.content_type,
        image_data=content,
        file_size_bytes=len(content),
        width=result["width"],
        height=result["height"],
        fabric_texture=result["texture_result"]["fabric_texture"],
        fabric_pattern=result["texture_result"]["fabric_pattern"],
        dominant_colors=result["color_result"]["dominant_colors"],
        damage_detected=result["damage_result"]["damage_detected"],
        damage_level=result["damage_result"]["damage_level"],
        damage_regions=result["damage_result"]["damage_regions"],
        contamination_detected=result["contamination_result"]["contamination_detected"],
        contamination_percentage=result["contamination_result"]["contamination_percentage"],
        contamination_types=result["contamination_result"]["contamination_types"],
        image_metadata=result["image_metadata"],
        fabric_confidence_score=result["fabric_confidence_score"],
        image_quality_score=result["image_quality_score"],
        status="processed",
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return ImageAnalysisOut.model_validate(record)


@router.get("/image/{image_id}/preview")
def get_image_preview(image_id: str, db: Session = Depends(get_db)):
    from fastapi.responses import Response
    record = db.query(ImageAnalysis).filter(ImageAnalysis.id == image_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Image not found")
    return Response(content=record.image_data, media_type=record.content_type)
