# app/services/analysis_history_service.py
from uuid import UUID
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, or_

from app.models.analysis_history import AnalysisHistory, AnalysisType, AnalysisStatus


def start_analysis_record(
    db: Session,
    user_id: UUID,
    analysis_type: AnalysisType = AnalysisType.FULL_PIPELINE,
    image_path: Optional[str] = None,
    original_filename: Optional[str] = None,
    waste_batch_id: Optional[UUID] = None,
) -> AnalysisHistory:
    """Call this the moment an analysis begins, so even a mid-pipeline crash
    leaves a 'failed' record instead of silently losing the attempt."""
    record = AnalysisHistory(
        user_id=user_id,
        waste_batch_id=waste_batch_id,
        analysis_type=analysis_type,
        status=AnalysisStatus.PROCESSING,
        image_path=image_path,
        original_filename=original_filename,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def complete_analysis_record(
    db: Session,
    record: AnalysisHistory,
    material_result: Optional[dict] = None,
    waste_classification_result: Optional[dict] = None,
    sustainability_result: Optional[dict] = None,
    environmental_impact_result: Optional[dict] = None,
    recommendation_result: Optional[dict] = None,
) -> AnalysisHistory:
    """Call this after your pipeline finishes, passing whatever each engine returned."""
    if material_result:
        record.material_result = material_result
        record.detected_material = material_result.get("material") or material_result.get("predicted_class")
        record.material_confidence = material_result.get("confidence")
        record.damage_level = material_result.get("damage_level")

    if waste_classification_result:
        record.waste_classification_result = waste_classification_result
        record.waste_category = waste_classification_result.get("category") or waste_classification_result.get("waste_category")

    if sustainability_result:
        record.sustainability_result = sustainability_result
        record.recyclability_score = sustainability_result.get("recyclability_score")
        record.reuse_score = sustainability_result.get("reuse_score")
        record.sustainability_score = sustainability_result.get("sustainability_score")
        record.material_recovery_score = sustainability_result.get("material_recovery_score")
        record.circularity_score = sustainability_result.get("circularity_score")
        record.overall_score = sustainability_result.get("overall_score") or sustainability_result.get("circularity_score")

    if environmental_impact_result:
        record.environmental_impact_result = environmental_impact_result

    if recommendation_result:
        record.recommendation_result = recommendation_result
        record.recommendation_summary = recommendation_result.get("summary") or recommendation_result.get("recommendation")

    record.status = AnalysisStatus.COMPLETED
    db.commit()
    db.refresh(record)
    return record


def fail_analysis_record(db: Session, record: AnalysisHistory, error_message: str) -> AnalysisHistory:
    record.status = AnalysisStatus.FAILED
    record.error_message = error_message[:2000]
    db.commit()
    db.refresh(record)
    return record


def get_user_history(
    db: Session,
    user_id: UUID,
    page: int = 1,
    page_size: int = 10,
    search: Optional[str] = None,
    sort: str = "latest",  # "latest" | "oldest"
) -> tuple[list[AnalysisHistory], int]:
    query = db.query(AnalysisHistory).filter(AnalysisHistory.user_id == user_id)  # <- user-scoped, hard filter

    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(
                AnalysisHistory.detected_material.ilike(like),
                AnalysisHistory.waste_category.ilike(like),
                AnalysisHistory.original_filename.ilike(like),
            )
        )

    total = query.count()
    order_col = desc(AnalysisHistory.created_at) if sort == "latest" else asc(AnalysisHistory.created_at)
    items = query.order_by(order_col).offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def get_analysis_detail(db: Session, user_id: UUID, analysis_id: UUID) -> Optional[AnalysisHistory]:
    """user_id filter here is what prevents cross-user access — never drop this."""
    return db.query(AnalysisHistory).filter(
        AnalysisHistory.id == analysis_id,
        AnalysisHistory.user_id == user_id,
    ).first()


def delete_analysis(db: Session, user_id: UUID, analysis_id: UUID) -> bool:
    record = get_analysis_detail(db, user_id, analysis_id)
    if not record:
        return False
    db.delete(record)
    db.commit()
    return True