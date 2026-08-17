from datetime import datetime, timedelta, date
from typing import Optional
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.waste import Waste
from app.models.textile_analysis import ImageAnalysis, MaterialClassification, WasteClassification, RecyclingRecommendation
from app.models.sustainability_models import SustainabilityMetrics, EnvironmentalImpact, WasteScore, CircularityAnalysis, RecommendationReport


def _apply_date_range(query, column, start_date: Optional[date], end_date: Optional[date]):
    if start_date:
        query = query.filter(column >= start_date)
    if end_date:
        query = query.filter(column <= end_date)
    return query


def get_recycler_dashboard(db: Session, start_date=None, end_date=None, material_type=None, waste_category=None):
    batch_query = db.query(Waste)
    batch_query = _apply_date_range(batch_query, Waste.created_at, start_date, end_date)
    if material_type:
        batch_query = batch_query.filter(Waste.fabric_type == material_type)

    batches = batch_query.all()
    total_received = sum(b.quantity or 0 for b in batches)
    pending = sum(b.quantity or 0 for b in batches if b.status == "Pending")
    processed = sum(b.quantity or 0 for b in batches if b.status == "Processed")

    waste_by_material = {}
    for b in batches:
        key = b.fabric_type or "Other"
        waste_by_material[key] = waste_by_material.get(key, 0) + (b.quantity or 0)

    wc_query = db.query(WasteClassification)
    if waste_category:
        wc_query = wc_query.filter(WasteClassification.waste_category == waste_category)
    waste_by_category = {}
    for row in wc_query.all():
        waste_by_category[row.waste_category] = waste_by_category.get(row.waste_category, 0) + 1

    recycling_opps = wc_query.filter(WasteClassification.waste_category == "Recyclable").count()
    reuse_opps = wc_query.filter(WasteClassification.waste_category == "Reusable").count()

    avg_recovery = db.query(func.avg(WasteScore.recovery)).scalar() or 0.0
    avg_diversion = db.query(func.avg(SustainabilityMetrics.diverted_percentage)).scalar() or 0.0

    # processing trend — batches processed per day, last 14 days
    trend_rows = (
        db.query(func.date(Waste.created_at).label("day"), func.sum(Waste.quantity).label("kg"))
        .filter(Waste.status == "Processed")
        .group_by(func.date(Waste.created_at))
        .order_by(func.date(Waste.created_at).desc())
        .limit(14)
        .all()
    )
    processing_trend = [{"date": str(r.day), "processed_kg": float(r.kg or 0)} for r in reversed(trend_rows)]

    return {
        "total_waste_received_kg": round(total_received, 2),
        "pending_waste_kg": round(pending, 2),
        "processed_waste_kg": round(processed, 2),
        "waste_by_material": waste_by_material,
        "waste_by_category": waste_by_category,
        "recycling_opportunities": recycling_opps,
        "reuse_opportunities": reuse_opps,
        "material_recovery_avg_pct": round(avg_recovery, 1),
        "waste_diversion_avg_pct": round(avg_diversion, 1),
        "processing_trend": processing_trend,
    }


def get_sustainability_dashboard(db: Session, start_date=None, end_date=None):
    score_q = db.query(WasteScore)
    score_q = _apply_date_range(score_q, WasteScore.created_at, start_date, end_date)
    scores = score_q.all()

    avg = lambda field: (sum(getattr(s, field) or 0 for s in scores) / len(scores)) if scores else 0.0

    env_totals = db.query(
        func.sum(EnvironmentalImpact.co2_saved),
        func.sum(EnvironmentalImpact.water_saved),
        func.sum(EnvironmentalImpact.landfill_saved),
    ).first()

    metrics_q = db.query(SustainabilityMetrics)
    metrics_q = _apply_date_range(metrics_q, SustainabilityMetrics.created_at, start_date, end_date)
    metrics = metrics_q.all()
    avg_diversion = (sum(m.diverted_percentage or 0 for m in metrics) / len(metrics)) if metrics else 0.0
    avg_recycled = (sum(m.recycled_percentage or 0 for m in metrics) / len(metrics)) if metrics else 0.0
    avg_reuse = (sum(m.reuse_percentage or 0 for m in metrics) / len(metrics)) if metrics else 0.0

    rating_rows = (
        db.query(SustainabilityMetrics.sustainability_rating, func.count(SustainabilityMetrics.id))
        .group_by(SustainabilityMetrics.sustainability_rating)
        .all()
    )
    rating_distribution = {r: c for r, c in rating_rows}

    trend_rows = (
        db.query(func.date(SustainabilityMetrics.created_at).label("day"), func.avg(SustainabilityMetrics.sustainability_index).label("idx"))
        .group_by(func.date(SustainabilityMetrics.created_at))
        .order_by(func.date(SustainabilityMetrics.created_at).desc())
        .limit(14)
        .all()
    )
    sustainability_trend = [{"date": str(r.day), "index": round(float(r.idx or 0), 1)} for r in reversed(trend_rows)]

    return {
        "overall_sustainability_score": round(avg("sustainability"), 1),
        "circularity_score": round(avg("circularity"), 1),
        "recyclability_score": round(avg("recyclability"), 1),
        "reuse_score": round(avg("reuse"), 1),
        "material_recovery_score": round(avg("recovery"), 1),
        "total_co2_saved_kg": round(env_totals[0] or 0, 2),
        "total_water_saved_l": round(env_totals[1] or 0, 2),
        "total_landfill_saved_kg": round(env_totals[2] or 0, 2),
        "waste_diversion_pct": round(avg_diversion, 1),
        "recycling_rate_pct": round(avg_recycled, 1),
        "reuse_rate_pct": round(avg_reuse, 1),
        "sustainability_trend": sustainability_trend,
        "rating_distribution": rating_distribution,
    }


def get_manufacturer_dashboard(db: Session, user_id: int, start_date=None, end_date=None):
    # scoped to this manufacturer's own batches
    batch_query = db.query(Waste).filter(Waste.user_id == user_id)
    batch_query = _apply_date_range(batch_query, Waste.created_at, start_date, end_date)
    batches = batch_query.all()

    total_waste = sum(b.quantity or 0 for b in batches)

    waste_by_material = {}
    for b in batches:
        key = b.fabric_type or "Other"
        waste_by_material[key] = waste_by_material.get(key, 0) + (b.quantity or 0)

    trend_rows = (
        db.query(func.date(Waste.created_at).label("day"), func.sum(Waste.quantity).label("kg"))
        .filter(Waste.user_id == user_id)
        .group_by(func.date(Waste.created_at))
        .order_by(func.date(Waste.created_at).desc())
        .limit(14)
        .all()
    )
    generation_trend = [{"date": str(r.day), "kg": float(r.kg or 0)} for r in reversed(trend_rows)]

    batch_ids = [b.id for b in batches]
    wc_rows = db.query(WasteClassification).join(ImageAnalysis, WasteClassification.image_id == ImageAnalysis.id).filter(
        ImageAnalysis.waste_batch_id.in_(batch_ids)
    ).all() if batch_ids else []

    waste_by_category = {}
    for row in wc_rows:
        waste_by_category[row.waste_category] = waste_by_category.get(row.waste_category, 0) + 1
    recycling_opps = sum(1 for r in wc_rows if r.waste_category == "Recyclable")
    reuse_opps = sum(1 for r in wc_rows if r.waste_category == "Reusable")
    recovery_potential = sum(r.recyclability_percentage or 0 for r in wc_rows) / len(wc_rows) * total_waste / 100 if wc_rows else 0

    score_q = db.query(WasteScore).filter(WasteScore.user_id == user_id)
    scores = score_q.all()
    avg_sustainability = (sum(s.sustainability or 0 for s in scores) / len(scores)) if scores else 0.0

    return {
        "total_production_waste_kg": round(total_waste, 2),
        "waste_generation_trend": generation_trend,
        "waste_by_material": waste_by_material,
        "waste_by_category": waste_by_category,
        "recycling_opportunities": recycling_opps,
        "reuse_opportunities": reuse_opps,
        "material_recovery_potential_kg": round(recovery_potential, 2),
        "sustainability_performance_score": round(avg_sustainability, 1),
        "waste_reduction_trend": generation_trend,  # same series; frontend can diff/interpret
    }


def get_admin_dashboard(db: Session):
    total_users = db.query(func.count(User.id)).scalar() or 0
    role_rows = db.query(User.role, func.count(User.id)).group_by(User.role).all()
    users_by_role = {r: c for r, c in role_rows}

    total_waste_records = db.query(func.count(Waste.id)).scalar() or 0
    total_analyses = db.query(func.count(ImageAnalysis.id)).scalar() or 0
    total_recommendations = db.query(func.count(RecyclingRecommendation.id)).scalar() or 0

    recent_batches = db.query(Waste).order_by(Waste.created_at.desc()).limit(5).all()
    recent_activity = [
        {"type": "waste_batch", "description": f"Batch {b.batch_id or b.id} logged", "timestamp": str(b.created_at)}
        for b in recent_batches
    ]

    return {
        "total_users": total_users,
        "users_by_role": users_by_role,
        "active_users_30d": total_users,  # no last-login tracking yet — see note below
        "total_waste_records": total_waste_records,
        "total_analyses": total_analyses,
        "total_recommendations": total_recommendations,
        "total_reports": 0,  # wired in Phase 3 once report history table exists
        "recent_activity": recent_activity,
        "system_status": "healthy",
    }