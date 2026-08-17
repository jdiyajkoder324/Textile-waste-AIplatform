"""
Routes: /api/recycling-recommendation, /api/recommendations
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models import (
    ImageAnalysis, MaterialClassification, WasteClassification,
    RecyclabilityAssessment, RecyclingRecommendation,
)
from schemas import RecyclingRecommendationOut
from services.recycling_engine import generate_recommendation

router = APIRouter(prefix="/api", tags=["Recycling Recommendation"])


@router.post("/recycling-recommendation", response_model=RecyclingRecommendationOut)
def recommend_recycling(image_id: str, db: Session = Depends(get_db)):
    image = db.query(ImageAnalysis).filter(ImageAnalysis.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    existing = db.query(RecyclingRecommendation).filter(RecyclingRecommendation.image_id == image_id).first()
    if existing:
        return existing

    material = db.query(MaterialClassification).filter(MaterialClassification.image_id == image_id).first()
    waste = db.query(WasteClassification).filter(WasteClassification.image_id == image_id).first()
    recyclability = db.query(RecyclabilityAssessment).filter(RecyclabilityAssessment.image_id == image_id).first()

    if not (material and waste and recyclability):
        raise HTTPException(
            status_code=400,
            detail="Run /api/material-classification, /api/waste-classification, "
                   "and /api/recyclability-assessment first",
        )

    material_dict = {"sustainability_score": material.sustainability_score, "material_name": material.material_name}
    waste_dict = {"waste_category": waste.waste_category}
    recyclability_dict = {
        "recyclability_percentage": recyclability.recyclability_percentage,
        "reuse_potential": recyclability.reuse_potential,
        "repairability_score": recyclability.repairability_score,
    }

    result = generate_recommendation(material_dict, waste_dict, recyclability_dict)

    record = RecyclingRecommendation(
        image_id=image.id,
        best_recycling_method=result["best_recycling_method"],
        ranked_methods=result["ranked_methods"],
        sustainability_score=result["sustainability_score"],
        environmental_impact_score=result["environmental_impact_score"],
        reuse_suggestions=result["reuse_suggestions"],
        waste_reduction_strategies=result["waste_reduction_strategies"],
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/recommendations", response_model=list[RecyclingRecommendationOut])
def list_recommendations(
    limit: int = Query(50, ge=1, le=200),
    method: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(RecyclingRecommendation).order_by(RecyclingRecommendation.created_at.desc())
    if method:
        query = query.filter(RecyclingRecommendation.best_recycling_method == method)
    return query.limit(limit).all()
