import math
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
import io

from app.database.session import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.analysis import ImageAnalysis, AnalysisReport
from app.schemas.analysis import (
    AnalysisDetailResponse, AnalysisSummaryResponse, PaginatedHistoryResponse,
    DashboardStatsResponse,
)
from app.services import image_processing
from app.services.prediction_pipeline import run_pipeline
from app.services.report_generator import generate_report
from app.services.analysis_history_service import (
    start_analysis_record, complete_analysis_record, fail_analysis_record,
)
from app.models.analysis_history import AnalysisType
from app.models.waste import Waste


router = APIRouter(prefix="/analysis", tags=["Analysis"])


def _load_full(db: Session, analysis_id: int, user: User) -> ImageAnalysis:
    analysis = (
        db.query(ImageAnalysis)
        .options(
            joinedload(ImageAnalysis.material_prediction),
            joinedload(ImageAnalysis.fabric_properties),
            joinedload(ImageAnalysis.waste_classification),
            joinedload(ImageAnalysis.defect_detection),
            joinedload(ImageAnalysis.recyclability),
            joinedload(ImageAnalysis.sustainability),
            joinedload(ImageAnalysis.recommendation),
        )
        .filter(ImageAnalysis.id == analysis_id)
        .first()
    )
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    if analysis.user_id is not None and analysis.user_id != user.id and user.role != "Admin":
        raise HTTPException(status_code=403, detail="Not authorized to view this analysis")
    return analysis


# ---------------------------------------------------------------------------
# UPLOAD + FULL PIPELINE
# Covers spec endpoints: /analysis/upload, /analysis/classify, /analysis/material,
# /analysis/waste, /analysis/recyclability — all computed together in one pass
# since each stage depends on the previous one's output.
# ---------------------------------------------------------------------------
@router.post("/upload", response_model=AnalysisDetailResponse)
async def upload_and_analyze(
    file: UploadFile = File(...),
    waste_batch_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    raw_bytes = await file.read()

    try:
        image_processing.validate_image(file.content_type, raw_bytes)
    except image_processing.ImageValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    waste_batch = None
    if waste_batch_id is not None:
        waste_batch = db.query(Waste).filter(Waste.id == waste_batch_id).first()
        if not waste_batch:
            raise HTTPException(status_code=404, detail="Waste batch not found")
        if waste_batch.user_id is not None and waste_batch.user_id != current_user.id and current_user.role != "Admin":
            raise HTTPException(status_code=403, detail="Not authorized to analyze this waste batch")

    analysis = ImageAnalysis(
        user_id=current_user.id,
        waste_batch_id = waste_batch_id,
        filename=file.filename,
        content_type=file.content_type,
        file_size=len(raw_bytes),
        image_data=raw_bytes,
        status="uploaded",
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    analysis = run_pipeline(db, analysis)

    if analysis.status == "failed":
        raise HTTPException(status_code=500, detail=f"Analysis pipeline failed: {analysis.error_message}")

    if waste_batch is not None and analysis.status == "completed":
        waste_batch.status = "Analyzed"
        db.commit()

    return _load_full(db, analysis.id, current_user)


# ---------------------------------------------------------------------------
# HISTORY — search / filter / sort / pagination (Feature 11)
# ---------------------------------------------------------------------------
@router.get("/history", response_model=PaginatedHistoryResponse)
def get_history(
    search: Optional[str] = None,
    material: Optional[str] = None,
    waste_category: Optional[str] = None,
    favorites_only: bool = False,
    sort_by: str = Query("created_at", pattern="^(created_at|filename)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(ImageAnalysis).options(
        joinedload(ImageAnalysis.material_prediction),
        joinedload(ImageAnalysis.waste_classification),
        joinedload(ImageAnalysis.recyclability),
    )

    if current_user.role != "Admin":
        query = query.filter(ImageAnalysis.user_id == current_user.id)

    if search:
        query = query.filter(ImageAnalysis.filename.ilike(f"%{search}%"))

    if favorites_only:
        query = query.filter(ImageAnalysis.is_favorite == 1)

    total = query.count()
    total_pages = max(math.ceil(total / page_size), 1)
    page = max(page, 1)

    sort_column = ImageAnalysis.created_at if sort_by == "created_at" else ImageAnalysis.filename
    sort_column = sort_column.desc() if sort_order == "desc" else sort_column.asc()

    rows = (
        query.order_by(sort_column)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    # Optional in-memory filters on joined fields (material / waste_category)
    def matches(a):
        if material and (not a.material_prediction or a.material_prediction.material != material):
            return False
        if waste_category and (not a.waste_classification or a.waste_classification.category != waste_category):
            return False
        return True

    items = []
    for a in rows:
        if not matches(a):
            continue
        items.append(AnalysisSummaryResponse(
            id=a.id,
            filename=a.filename,
            status=a.status,
            is_favorite=bool(a.is_favorite),
            created_at=a.created_at,
            material=a.material_prediction.material if a.material_prediction else None,
            waste_category=a.waste_classification.category if a.waste_classification else None,
            recyclability_score=a.recyclability.overall_score if a.recyclability else None,
        ))

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


# ---------------------------------------------------------------------------
# DASHBOARD STATS (Feature 10)
# ---------------------------------------------------------------------------
@router.get("/dashboard-stats", response_model=DashboardStatsResponse)
def dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(ImageAnalysis).options(
        joinedload(ImageAnalysis.material_prediction),
        joinedload(ImageAnalysis.waste_classification),
        joinedload(ImageAnalysis.recyclability),
        joinedload(ImageAnalysis.sustainability),
    )
    if current_user.role != "Admin":
        query = query.filter(ImageAnalysis.user_id == current_user.id)

    analyses = query.filter(ImageAnalysis.status == "completed").all()

    materials, categories = {}, {}
    recy_scores, sus_scores = [], []

    for a in analyses:
        if a.material_prediction:
            materials[a.material_prediction.material] = materials.get(a.material_prediction.material, 0) + 1
        if a.waste_classification:
            categories[a.waste_classification.category] = categories.get(a.waste_classification.category, 0) + 1
        if a.recyclability:
            recy_scores.append(a.recyclability.overall_score)
        if a.sustainability:
            sus_scores.append(a.sustainability.waste_diversion_score or 0)

    recent = sorted(analyses, key=lambda a: a.created_at, reverse=True)[:5]

    return {
        "total_images_analyzed": len(analyses),
        "materials_detected": materials,
        "waste_categories": categories,
        "average_recyclability_score": round(sum(recy_scores) / len(recy_scores), 1) if recy_scores else 0,
        "average_sustainability_score": round(sum(sus_scores) / len(sus_scores), 1) if sus_scores else 0,
        "most_common_material": max(materials, key=materials.get) if materials else None,
        "most_common_waste_category": max(categories, key=categories.get) if categories else None,
        "recent_analyses": [
            AnalysisSummaryResponse(
                id=a.id, filename=a.filename, status=a.status,
                is_favorite=bool(a.is_favorite), created_at=a.created_at,
                material=a.material_prediction.material if a.material_prediction else None,
                waste_category=a.waste_classification.category if a.waste_classification else None,
                recyclability_score=a.recyclability.overall_score if a.recyclability else None,
            ) for a in recent
        ],
    }


# ---------------------------------------------------------------------------
# SINGLE ANALYSIS DETAIL / DELETE / FAVORITE
# ---------------------------------------------------------------------------
@router.get("/{analysis_id}", response_model=AnalysisDetailResponse)
def get_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _load_full(db, analysis_id, current_user)


@router.delete("/{analysis_id}")
def delete_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analysis = _load_full(db, analysis_id, current_user)
    db.delete(analysis)
    db.commit()
    return {"message": "Analysis deleted successfully"}


@router.patch("/{analysis_id}/favorite")
def toggle_favorite(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analysis = _load_full(db, analysis_id, current_user)
    analysis.is_favorite = 0 if analysis.is_favorite else 1
    db.commit()
    return {"id": analysis.id, "is_favorite": bool(analysis.is_favorite)}


# ---------------------------------------------------------------------------
# IMAGE SERVING (images live in Postgres, not disk)
# ---------------------------------------------------------------------------
@router.get("/{analysis_id}/image")
def get_analysis_image(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analysis = _load_full(db, analysis_id, current_user)
    return StreamingResponse(io.BytesIO(analysis.image_data), media_type=analysis.content_type)


@router.get("/{analysis_id}/image/annotated")
def get_annotated_image(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analysis = _load_full(db, analysis_id, current_user)
    if not analysis.defect_detection or not analysis.defect_detection.annotated_image_data:
        raise HTTPException(status_code=404, detail="No annotated image available (no defects detected)")
    return StreamingResponse(
        io.BytesIO(analysis.defect_detection.annotated_image_data), media_type="image/jpeg"
    )


# ---------------------------------------------------------------------------
# REPORT GENERATION (Feature 9) — /analysis/report/{id}?format=pdf|csv|json
# ---------------------------------------------------------------------------
@router.get("/report/{analysis_id}")
def download_report(
    analysis_id: int,
    format: str = Query("pdf", pattern="^(pdf|csv|json)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analysis = _load_full(db, analysis_id, current_user)

    try:
        file_bytes, media_type = generate_report(analysis, format)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Persist a copy of the generated report
    report_row = AnalysisReport(
        analysis_id=analysis.id, format=format, file_data=file_bytes,
        generated_at=datetime.utcnow(),
    )
    db.add(report_row)
    db.commit()

    extension = format
    filename = f"analysis_{analysis.id}_report.{extension}"

    return StreamingResponse(
        io.BytesIO(file_bytes),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

@router.post("/analyze")
def analyze_textile(
    file: UploadFile,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    image_path = save_uploaded_file(file)  # <- your existing upload-save function

    # 1. create the record FIRST, before running the pipeline
    record = start_analysis_record(
        db, user_id=current_user.id,
        analysis_type=AnalysisType.FULL_PIPELINE,
        image_path=image_path,
        original_filename=file.filename,
    )

    try:
        material_result = run_material_recognition(image_path)       # <- your Milestone 2 function
        waste_result = classify_waste(material_result)                # <- your Milestone 2 function
        sustainability_result = run_sustainability_engine(material_result, waste_result)  # <- Milestone 3
        env_impact = calculate_environmental_impact(sustainability_result)                # <- Milestone 3
        recommendation = generate_recommendation(sustainability_result, env_impact)        # <- Milestone 3

        complete_analysis_record(
            db, record,
            material_result=material_result,
            waste_classification_result=waste_result,
            sustainability_result=sustainability_result,
            environmental_impact_result=env_impact,
            recommendation_result=recommendation,
        )

        return {
            "analysis_id": record.id,
            "material_result": material_result,
            "waste_result": waste_result,
            "sustainability_result": sustainability_result,
            "environmental_impact": env_impact,
            "recommendation": recommendation,
        }

    except Exception as e:
        fail_analysis_record(db, record, str(e))
        raise HTTPException(500, f"Analysis failed: {e}")

import os

@router.post("/analyze-from-batch/{waste_batch_id}", response_model=AnalysisDetailResponse)
def analyze_from_batch(
    waste_batch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    waste_batch = db.query(Waste).filter(Waste.id == waste_batch_id).first()
    if not waste_batch:
        raise HTTPException(status_code=404, detail="Waste batch not found")
    if waste_batch.user_id is not None and waste_batch.user_id != current_user.id and current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Not authorized to analyze this waste batch")
    if not waste_batch.image_path or not os.path.exists(waste_batch.image_path):
        raise HTTPException(status_code=400, detail="This waste batch has no image on file to analyze")

    with open(waste_batch.image_path, "rb") as f:
        raw_bytes = f.read()

    content_type = "image/jpeg"
    if waste_batch.image_path.lower().endswith(".png"):
        content_type = "image/png"

    try:
        image_processing.validate_image(content_type, raw_bytes)
    except image_processing.ImageValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    analysis = ImageAnalysis(
        user_id=current_user.id,
        waste_batch_id=waste_batch.id,
        filename=os.path.basename(waste_batch.image_path),
        content_type=content_type,
        file_size=len(raw_bytes),
        image_data=raw_bytes,
        status="uploaded",
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    analysis = run_pipeline(db, analysis)

    if analysis.status == "failed":
        raise HTTPException(status_code=500, detail=f"Analysis pipeline failed: {analysis.error_message}")

    if analysis.status == "completed":
        waste_batch.status = "Analyzed"
        db.commit()

    return _load_full(db, analysis.id, current_user)

@router.get("/by-batch/{waste_batch_id}", response_model=list[AnalysisSummaryResponse])
def get_analyses_for_batch(
    waste_batch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    waste_batch = db.query(Waste).filter(Waste.id == waste_batch_id).first()
    if not waste_batch:
        raise HTTPException(status_code=404, detail="Waste batch not found")
    if waste_batch.user_id is not None and waste_batch.user_id != current_user.id and current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    rows = (
        db.query(ImageAnalysis)
        .options(
            joinedload(ImageAnalysis.material_prediction),
            joinedload(ImageAnalysis.waste_classification),
            joinedload(ImageAnalysis.recyclability),
        )
        .filter(ImageAnalysis.waste_batch_id == waste_batch_id)
        .order_by(ImageAnalysis.created_at.desc())
        .all()
    )

    return [
        AnalysisSummaryResponse(
            id=a.id, filename=a.filename, status=a.status,
            is_favorite=bool(a.is_favorite), created_at=a.created_at,
            material=a.material_prediction.material if a.material_prediction else None,
            waste_category=a.waste_classification.category if a.waste_classification else None,
            recyclability_score=a.recyclability.overall_score if a.recyclability else None,
        ) for a in rows
    ]