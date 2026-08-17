"""
Routes: /api/material-classification, /api/material-history
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models import ImageAnalysis, MaterialClassification
from schemas import MaterialClassificationOut
from services.image_engine import run_image_analysis
from services.material_engine import run_material_classification

router = APIRouter(prefix="/api", tags=["Material Classification"])


@router.post("/material-classification", response_model=MaterialClassificationOut)
def classify_material(image_id: str, db: Session = Depends(get_db)):
    """Re-runs / fetches material classification for an already-uploaded image."""
    image = db.query(ImageAnalysis).filter(ImageAnalysis.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    existing = db.query(MaterialClassification).filter(MaterialClassification.image_id == image_id).first()
    if existing:
        return existing

    analysis_output = run_image_analysis(image.image_data, image.filename, image.content_type)
    result = run_material_classification(analysis_output)

    record = MaterialClassification(
        image_id=image.id,
        material_name=result["material_name"],
        fabric_category=result["fabric_category"],
        fiber_composition=result["fiber_composition"],
        blend_identification=result["blend_identification"],
        fabric_quality=result["fabric_quality"],
        fabric_texture=result["fabric_texture"],
        color_information=result["color_information"],
        pattern_information=result["pattern_information"],
        sustainability_score=result["sustainability_score"],
        material_confidence_percentage=result["material_confidence_percentage"],
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/material-history", response_model=list[MaterialClassificationOut])
def material_history(
    limit: int = Query(50, ge=1, le=200),
    material_name: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(MaterialClassification).order_by(MaterialClassification.created_at.desc())
    if material_name:
        query = query.filter(MaterialClassification.material_name == material_name)
    return query.limit(limit).all()
