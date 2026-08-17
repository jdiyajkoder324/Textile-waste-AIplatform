"""
sustainability_router.py

TASK 5 - FastAPI APIs

    POST /api/sustainability/analyze
    GET  /api/dashboard/summary
    GET  /health

This router follows the same pattern as your existing Milestone 1 / 2
routers: it depends on `get_db` for a DB session and `get_current_user`
for JWT-authenticated RBAC access. Adjust the two import lines marked
below ONLY IF your existing dependency module paths differ.
"""

from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.session import get_db
from app.core.auth import get_current_user

from app.schemas.sustainability_schemas import (
    SustainabilityAnalyzeRequest,
    SustainabilityAnalyzeResponse,
    DashboardSummaryResponse,
    HealthResponse,
)
from app.models.sustainability_models import (
    SustainabilityMetrics,
    EnvironmentalImpact,
    WasteScore,
    CircularityAnalysis,
    RecommendationReport,
)

from app.services.sustainability_engine import sustainability_engine
from app.services.environmental_impact_engine import environmental_impact_engine
from app.services.waste_scoring_engine import waste_scoring_engine
from app.services.recommendation_engine import recommendation_engine


router = APIRouter(prefix="/api", tags=["Sustainability Intelligence - Milestone 3"])


# --------------------------------------------------------------------------
# POST /api/sustainability/analyze
# --------------------------------------------------------------------------
@router.post(
    "/sustainability/analyze",
    response_model=SustainabilityAnalyzeResponse,
    status_code=status.HTTP_200_OK,
)
def analyze_sustainability(
    payload: SustainabilityAnalyzeRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        # ---------------- Waste Scoring Engine ----------------
        score_inputs = {
            "material_purity": payload.material_purity,
            "contamination_level": payload.contamination_level,
            "damage_level": payload.damage_level,
            "fabric_condition": payload.fabric_condition,
            "durability": payload.durability,
            "usability": payload.usability,
            "environmental_benefit": payload.environmental_benefit,
            "recoverability": payload.recoverability,
            "recycling_efficiency": payload.recycling_efficiency,
            "fiber_recovery": payload.fiber_recovery,
            "fabric_quality": payload.fabric_quality,
            "resource_value": payload.resource_value,
            "processing_feasibility": payload.processing_feasibility,
        }
        scores_result = waste_scoring_engine.generate_full_scores(score_inputs)
        scores = scores_result["scores"]

        # ---------------- Sustainability Intelligence Engine ----------------
        carbon_footprint = sustainability_engine.calculate_carbon_footprint(
            weight_kg=payload.weight_kg,
            material_type=payload.material_type,
            is_recycled=payload.is_recycled,
            distance_km=payload.distance_km,
        )
        waste_diversion = sustainability_engine.calculate_waste_diversion(
            total_weight_kg=payload.weight_kg,
            recycled_kg=payload.recycled_kg,
            reused_kg=payload.reused_kg,
            recovered_kg=payload.recovered_kg,
            landfilled_kg=payload.landfilled_kg,
        )
        circular_economy = sustainability_engine.calculate_circular_economy(
            recyclability_score=scores["recyclability"],
            material_condition_score=payload.fabric_condition,
            reuse_potential_score=scores["reuse"],
            processing_feasibility_score=payload.processing_feasibility,
        )
        resource_recovery = sustainability_engine.calculate_resource_recovery(
            weight_kg=payload.weight_kg,
            material_type=payload.material_type,
            recovery_efficiency=scores["recyclability"] / 100.0,
        )
        benchmark = sustainability_engine.benchmark_sustainability(
            carbon_footprint, waste_diversion, circular_economy, resource_recovery
        )

        # ---------------- Environmental Impact Assessment Engine ----------------
        environmental_report = environmental_impact_engine.generate_environmental_report(
            weight_kg=payload.weight_kg,
            material_type=payload.material_type,
            total_facility_landfill_kg=payload.total_facility_landfill_kg,
        )

        # ---------------- Recommendation Engine ----------------
        recommendations_result = recommendation_engine.generate_recommendations(
            material_type=payload.material_type,
            circularity_score=scores["circularity"],
            contamination_level=payload.contamination_level,
        )

        # ---------------- Persist to DB ----------------
        user_id = getattr(current_user, "id", None)

        sustainability_row = SustainabilityMetrics(
            user_id=user_id,
            textile_id=payload.textile_id,
            material_type=payload.material_type,
            weight_kg=payload.weight_kg,
            carbon_current_emission=carbon_footprint["carbon_footprint"]["current_emission"],
            carbon_recycling_savings=carbon_footprint["carbon_footprint"]["recycling_savings"],
            carbon_net_savings=carbon_footprint["carbon_footprint"]["net_savings"],
            carbon_rating=carbon_footprint["carbon_footprint"]["rating"],
            diverted_percentage=waste_diversion["waste_diversion"]["diverted_percentage"],
            recycled_percentage=waste_diversion["waste_diversion"]["recycled_percentage"],
            reuse_percentage=waste_diversion["waste_diversion"]["reuse_percentage"],
            recovery_percentage=waste_diversion["waste_diversion"]["recovery_percentage"],
            sustainability_index=benchmark["sustainability_index"],
            sustainability_rating=benchmark["rating"],
            recommendations=benchmark["recommendations"],
        )
        db.add(sustainability_row)

        env_row = EnvironmentalImpact(
            user_id=user_id,
            textile_id=payload.textile_id,
            co2_saved=environmental_report["environmental_report"]["co2_saved"],
            water_saved=environmental_report["environmental_report"]["water_saved"],
            landfill_saved=environmental_report["environmental_report"]["landfill_saved"],
            energy_saved=environmental_report["environmental_report"]["energy_saved"],
            material_conserved=environmental_report["environmental_report"]["details"]["resource_conservation"]["material_conserved"],
            carbon_conserved=environmental_report["environmental_report"]["details"]["resource_conservation"]["carbon_conserved"],
            rating=environmental_report["environmental_report"]["rating"],
            recommendation=environmental_report["environmental_report"]["recommendation"],
            report_json=environmental_report["environmental_report"],
        )
        db.add(env_row)

        score_row = WasteScore(
            user_id=user_id,
            textile_id=payload.textile_id,
            recyclability=scores["recyclability"],
            reuse=scores["reuse"],
            sustainability=scores["sustainability"],
            recovery=scores["recovery"],
            circularity=scores["circularity"],
            category=scores["category"],
        )
        db.add(score_row)

        circularity_row = CircularityAnalysis(
            user_id=user_id,
            textile_id=payload.textile_id,
            score=circular_economy["circular_economy"]["score"],
            utilization=circular_economy["circular_economy"]["utilization"],
            optimization=circular_economy["circular_economy"]["optimization"],
            category=circular_economy["circular_economy"]["category"],
            recoverable_material=resource_recovery["resource_recovery"]["recoverable_material"],
            estimated_value=resource_recovery["resource_recovery"]["estimated_value"],
            energy_recovery=resource_recovery["resource_recovery"]["energy_recovery"],
            resource_efficiency=resource_recovery["resource_recovery"]["resource_efficiency"],
        )
        db.add(circularity_row)

        recommendation_row = RecommendationReport(
            user_id=user_id,
            textile_id=payload.textile_id,
            material_type=payload.material_type,
            circularity_score=scores["circularity"],
            recommendations=recommendations_result["recommendations"],
        )
        db.add(recommendation_row)

        db.commit()

        return SustainabilityAnalyzeResponse(
            textile_id=payload.textile_id,
            material_type=payload.material_type,
            weight_kg=payload.weight_kg,
            carbon_footprint=carbon_footprint["carbon_footprint"],
            waste_diversion=waste_diversion["waste_diversion"],
            circular_economy=circular_economy["circular_economy"],
            resource_recovery=resource_recovery["resource_recovery"],
            benchmark=benchmark,
            environmental_report=environmental_report["environmental_report"],
            scores=scores,
            recommendations=recommendations_result["recommendations"],
            generated_at=datetime.utcnow(),
        )

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sustainability analysis failed: {str(exc)}",
        )


# --------------------------------------------------------------------------
# GET /api/dashboard/summary
# --------------------------------------------------------------------------
@router.get(
    "/dashboard/summary",
    response_model=DashboardSummaryResponse,
    status_code=status.HTTP_200_OK,
)
def dashboard_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        total_batches = db.query(func.count(SustainabilityMetrics.id)).scalar() or 0
        total_weight = db.query(func.sum(SustainabilityMetrics.weight_kg)).scalar() or 0.0

        total_co2_saved = db.query(func.sum(EnvironmentalImpact.co2_saved)).scalar() or 0.0
        total_water_saved = db.query(func.sum(EnvironmentalImpact.water_saved)).scalar() or 0.0

        avg_circularity = db.query(func.avg(WasteScore.circularity)).scalar() or 0.0
        avg_diverted = db.query(func.avg(SustainabilityMetrics.diverted_percentage)).scalar() or 0.0

        rating_rows = (
            db.query(SustainabilityMetrics.sustainability_rating, func.count(SustainabilityMetrics.id))
            .group_by(SustainabilityMetrics.sustainability_rating)
            .all()
        )
        rating_distribution: Dict[str, int] = {rating: count for rating, count in rating_rows}

        return DashboardSummaryResponse(
            total_waste_analyzed_kg=round(total_weight, 2),
            total_batches=total_batches,
            total_co2_saved=round(total_co2_saved, 2),
            total_water_saved=round(total_water_saved, 2),
            average_circularity_score=round(avg_circularity, 2),
            average_waste_diverted_percentage=round(avg_diverted, 2),
            rating_distribution=rating_distribution,
            last_updated=datetime.utcnow(),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Dashboard summary failed: {str(exc)}",
        )


# --------------------------------------------------------------------------
# GET /health
# --------------------------------------------------------------------------
@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
def health_check() -> Dict[str, Any]:
    return {
        "status": "ok",
        "module": "sustainability-intelligence",
        "timestamp": datetime.utcnow(),
    }
