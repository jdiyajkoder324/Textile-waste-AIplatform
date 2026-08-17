"""
Milestone 2 — Material Recognition & Waste Classification.

This single router replaces the earlier, broken material.py / recycling.py /
reports.py / image_analysis.py route files (which used flat imports like
`from database import get_db` that don't work inside the app.* package).
Point main.py at THIS router only for Milestone 2 functionality; the old
files can stay on disk unused, or be deleted once this is confirmed working.
"""
from typing import Optional

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Form, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import or_
from sqlalchemy.orm import joinedload
import math as _math
from app.core.auth import get_current_user
from app.models.user import User

from app.database import get_db
from app.models.textile_analysis import (
    ImageAnalysis, MaterialClassification, WasteClassification,
    RecyclabilityAssessment, RecyclingRecommendation, AnalysisReport,
)
from app.schemas.textile_analysis import (
    ImageAnalysisOut, MaterialClassificationOut, WasteClassificationOut,
    RecyclabilityAssessmentOut, RecyclingRecommendationOut, FullAnalysisOut,
)
from app.services.pipeline import run_full_pipeline
from app.services.image_engine import run_image_analysis
from app.services.material_engine import run_material_classification
from app.services.waste_engine import run_waste_classification, run_recyclability_assessment
from app.services.recycling_engine import generate_recommendation
from app.services.report_engine import generate_pdf_report, generate_csv_report, generate_json_report

router = APIRouter(prefix="/api", tags=["Material Recognition & Waste Classification"])

ALLOWED_IMAGE_TYPES = ("image/jpeg", "image/png", "image/jpg", "image/webp", "image/bmp")
MAX_IMAGE_SIZE_MB = 15


def _validate_image(file: UploadFile, content: bytes):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported image type: {file.content_type}")
    if len(content) / (1024 * 1024) > MAX_IMAGE_SIZE_MB:
        raise HTTPException(status_code=400, detail=f"Image exceeds {MAX_IMAGE_SIZE_MB}MB limit")


# ---------------------------------------------------------------------------
# Upload + full pipeline
# ---------------------------------------------------------------------------
@router.post("/upload-image", response_model=FullAnalysisOut)
async def upload_image(file: UploadFile = File(...), waste_batch_id: Optional[str] = Form(None), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    content = await file.read()
    _validate_image(file, content)

    image_record = ImageAnalysis(
        filename=file.filename,
        content_type=file.content_type,
        image_data=content,
        file_size_bytes=len(content),
        status="processing",
        user_id=current_user.id,          # NEW
        waste_batch_id=waste_batch_id,
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
    if image_id:
        record = db.query(ImageAnalysis).filter(ImageAnalysis.id == image_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="Image not found")
        return ImageAnalysisOut.model_validate(record)

    if not file:
        raise HTTPException(status_code=400, detail="Provide either image_id or file")

    content = await file.read()
    _validate_image(file, content)
    result = run_image_analysis(content, file.filename, file.content_type)

    record = ImageAnalysis(
        filename=file.filename, content_type=file.content_type, image_data=content,
        file_size_bytes=len(content), width=result["width"], height=result["height"],
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
def get_image_preview(image_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user),):
    record = db.query(ImageAnalysis).filter(ImageAnalysis.id == image_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Image not found")
    if record.user_id is not None and record.user_id != current_user.id and current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Not authorized to view this image")
    return Response(content=record.image_data, media_type=record.content_type)


# ---------------------------------------------------------------------------
# Granular, idempotent endpoints
# ---------------------------------------------------------------------------
def _get_or_build_material(db: Session, image: ImageAnalysis, analysis_output=None):
    existing = db.query(MaterialClassification).filter(MaterialClassification.image_id == image.id).first()
    if existing:
        return existing, analysis_output
    if analysis_output is None:
        analysis_output = run_image_analysis(image.image_data, image.filename, image.content_type)
    result = run_material_classification(analysis_output)
    record = MaterialClassification(
        image_id=image.id, material_name=result["material_name"], fabric_category=result["fabric_category"],
        fiber_composition=result["fiber_composition"], blend_identification=result["blend_identification"],
        fabric_quality=result["fabric_quality"], fabric_texture=result["fabric_texture"],
        color_information=result["color_information"], pattern_information=result["pattern_information"],
        sustainability_score=result["sustainability_score"],
        material_confidence_percentage=result["material_confidence_percentage"],
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record, analysis_output


@router.post("/material-classification", response_model=MaterialClassificationOut)
def classify_material(image_id: str, db: Session = Depends(get_db)):
    image = db.query(ImageAnalysis).filter(ImageAnalysis.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    record, _ = _get_or_build_material(db, image)
    return record


@router.post("/waste-classification", response_model=WasteClassificationOut)
def classify_waste(image_id: str, db: Session = Depends(get_db)):
    image = db.query(ImageAnalysis).filter(ImageAnalysis.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    existing = db.query(WasteClassification).filter(WasteClassification.image_id == image_id).first()
    if existing:
        return existing

    analysis_output = run_image_analysis(image.image_data, image.filename, image.content_type)
    material, analysis_output = _get_or_build_material(db, image, analysis_output)

    material_dict = {"material_name": material.material_name, "fabric_quality": material.fabric_quality}
    result = run_waste_classification(analysis_output, material_dict)

    record = WasteClassification(
        image_id=image.id, waste_category=result["waste_category"], waste_condition=result["waste_condition"],
        damage_level=result["damage_level"], contamination_percentage=result["contamination_percentage"],
        recyclability_percentage=result["recyclability_percentage"], disposal_method=result["disposal_method"],
        category_scores=result["category_scores"],
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.post("/recyclability-assessment", response_model=RecyclabilityAssessmentOut)
def assess_recyclability(image_id: str, db: Session = Depends(get_db)):
    image = db.query(ImageAnalysis).filter(ImageAnalysis.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    existing = db.query(RecyclabilityAssessment).filter(RecyclabilityAssessment.image_id == image_id).first()
    if existing:
        return existing

    waste = db.query(WasteClassification).filter(WasteClassification.image_id == image_id).first()
    if not waste:
        raise HTTPException(status_code=400, detail="Run /api/waste-classification first")

    analysis_output = run_image_analysis(image.image_data, image.filename, image.content_type)
    waste_dict = {"waste_category": waste.waste_category, "recyclability_percentage": waste.recyclability_percentage}
    result = run_recyclability_assessment(analysis_output, waste_dict)

    record = RecyclabilityAssessment(
        image_id=image.id, recyclability_percentage=result["recyclability_percentage"],
        reuse_potential=result["reuse_potential"], repairability_score=result["repairability_score"],
        contamination_impact=result["contamination_impact"],
        disposal_recommendation=result["disposal_recommendation"], assessment_notes=result["assessment_notes"],
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


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
        image_id=image.id, best_recycling_method=result["best_recycling_method"],
        ranked_methods=result["ranked_methods"], sustainability_score=result["sustainability_score"],
        environmental_impact_score=result["environmental_impact_score"],
        reuse_suggestions=result["reuse_suggestions"],
        waste_reduction_strategies=result["waste_reduction_strategies"],
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


# ---------------------------------------------------------------------------
# History / listing
# ---------------------------------------------------------------------------
@router.get("/material-history", response_model=list[MaterialClassificationOut])
def material_history(limit: int = Query(50, ge=1, le=200), db: Session = Depends(get_db)):
    return db.query(MaterialClassification).order_by(MaterialClassification.created_at.desc()).limit(limit).all()


@router.get("/waste-history", response_model=list[WasteClassificationOut])
def waste_history(limit: int = Query(50, ge=1, le=200), db: Session = Depends(get_db)):
    return db.query(WasteClassification).order_by(WasteClassification.created_at.desc()).limit(limit).all()


@router.get("/recommendations", response_model=list[RecyclingRecommendationOut])
def list_recommendations(limit: int = Query(50, ge=1, le=200), db: Session = Depends(get_db)):
    return db.query(RecyclingRecommendation).order_by(RecyclingRecommendation.created_at.desc()).limit(limit).all()


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------
MEDIA_TYPES = {"pdf": "application/pdf", "csv": "text/csv", "json": "application/json"}


@router.get("/analysis-report")
def get_analysis_report(image_id: str, format: str = Query("pdf", pattern="^(pdf|csv|json)$"),
                         db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    image = db.query(ImageAnalysis).filter(ImageAnalysis.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    if image.user_id is not None and image.user_id != current_user.id and current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    material = db.query(MaterialClassification).filter(MaterialClassification.image_id == image_id).first()
    waste = db.query(WasteClassification).filter(WasteClassification.image_id == image_id).first()
    recyclability = db.query(RecyclabilityAssessment).filter(RecyclabilityAssessment.image_id == image_id).first()
    recommendation = db.query(RecyclingRecommendation).filter(RecyclingRecommendation.image_id == image_id).first()

    if format == "pdf":
        file_bytes = generate_pdf_report(image, material, waste, recyclability, recommendation)
    elif format == "csv":
        file_bytes = generate_csv_report(image, material, waste, recyclability, recommendation)
    else:
        file_bytes = generate_json_report(image, material, waste, recyclability, recommendation)

    file_name = f"analysis-report-{image_id[:8]}.{format}"
    db.add(AnalysisReport(image_id=image.id, report_format=format, file_data=file_bytes, file_name=file_name))
    db.commit()

    return Response(
        content=file_bytes, media_type=MEDIA_TYPES[format],
        headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
    )

@router.get("/my-analyses")
def my_analyses(
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(ImageAnalysis).options(
        joinedload(ImageAnalysis.material_classification),
        joinedload(ImageAnalysis.waste_classification),
        joinedload(ImageAnalysis.recyclability_assessment),
    ).filter(ImageAnalysis.user_id == current_user.id)   # <- hard user filter

    if search:
        query = query.filter(ImageAnalysis.filename.ilike(f"%{search}%"))

    total = query.count()
    total_pages = max(_math.ceil(total / page_size), 1)

    order_col = ImageAnalysis.created_at.desc() if sort_order == "desc" else ImageAnalysis.created_at.asc()
    rows = query.order_by(order_col).offset((page - 1) * page_size).limit(page_size).all()

    items = [
        {
            "id": a.id,
            "filename": a.filename,
            "status": a.status,
            "created_at": a.created_at,
            "waste_batch_id": a.waste_batch_id,
            "material": a.material_classification.material_name if a.material_classification else None,
            "waste_category": a.waste_classification.waste_category if a.waste_classification else None,
            "recyclability_percentage": (
                a.recyclability_assessment.recyclability_percentage if a.recyclability_assessment else None
            ),
        }
        for a in rows
    ]

    return {"items": items, "total": total, "page": page, "page_size": page_size, "total_pages": total_pages}

@router.get("/analysis/{image_id}/full", response_model=FullAnalysisOut)
def get_full_analysis(
    image_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    image = db.query(ImageAnalysis).filter(ImageAnalysis.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Analysis not found")
    if image.user_id is not None and image.user_id != current_user.id and current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Not authorized to view this analysis")

    if not (image.material_classification and image.waste_classification
            and image.recyclability_assessment and image.recommendation):
        raise HTTPException(status_code=400, detail="Analysis pipeline incomplete for this image")

    return FullAnalysisOut(
        image_analysis=ImageAnalysisOut.model_validate(image),
        material_classification=image.material_classification,
        waste_classification=image.waste_classification,
        recyclability_assessment=image.recyclability_assessment,
        recycling_recommendation=image.recommendation,
    )

@router.delete("/analysis/{image_id}")
def delete_analysis(
    image_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    image = db.query(ImageAnalysis).filter(ImageAnalysis.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Analysis not found")
    if image.user_id is not None and image.user_id != current_user.id and current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    db.delete(image)
    db.commit()
    return {"message": "Deleted successfully"}