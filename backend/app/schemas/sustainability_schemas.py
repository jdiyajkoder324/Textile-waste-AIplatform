"""
sustainability_schemas.py

Pydantic request/response schemas for Milestone 3 endpoints.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# --------------------------------------------------------------------------
# REQUEST SCHEMAS
# --------------------------------------------------------------------------

class SustainabilityAnalyzeRequest(BaseModel):
    textile_id: Optional[int] = Field(None, description="Existing waste batch / textile ID if available")
    material_type: str = Field(..., example="cotton")
    weight_kg: float = Field(..., gt=0, example=12.5)
    is_recycled: bool = Field(True, description="Whether this batch is being recycled vs land-filled")
    distance_km: float = Field(0.0, ge=0, description="Transport distance for footprint calc")

    # Waste diversion inputs
    recycled_kg: float = Field(0.0, ge=0)
    reused_kg: float = Field(0.0, ge=0)
    recovered_kg: float = Field(0.0, ge=0)
    landfilled_kg: float = Field(0.0, ge=0)

    # Score inputs (0-100 scale). All optional; default to a neutral 50.
    material_purity: Optional[float] = Field(50, ge=0, le=100)
    contamination_level: Optional[float] = Field(0, ge=0, le=100)
    damage_level: Optional[float] = Field(0, ge=0, le=100)
    fabric_condition: Optional[float] = Field(70, ge=0, le=100)
    durability: Optional[float] = Field(70, ge=0, le=100)
    usability: Optional[float] = Field(70, ge=0, le=100)
    environmental_benefit: Optional[float] = Field(60, ge=0, le=100)
    recoverability: Optional[float] = Field(60, ge=0, le=100)
    recycling_efficiency: Optional[float] = Field(60, ge=0, le=100)
    fiber_recovery: Optional[float] = Field(60, ge=0, le=100)
    fabric_quality: Optional[float] = Field(60, ge=0, le=100)
    resource_value: Optional[float] = Field(60, ge=0, le=100)
    processing_feasibility: Optional[float] = Field(60, ge=0, le=100)

    total_facility_landfill_kg: Optional[float] = Field(0.0, ge=0)


# --------------------------------------------------------------------------
# RESPONSE SCHEMAS
# --------------------------------------------------------------------------

class SustainabilityAnalyzeResponse(BaseModel):
    textile_id: Optional[int]
    material_type: str
    weight_kg: float

    carbon_footprint: Dict[str, Any]
    waste_diversion: Dict[str, Any]
    circular_economy: Dict[str, Any]
    resource_recovery: Dict[str, Any]
    benchmark: Dict[str, Any]

    environmental_report: Dict[str, Any]

    scores: Dict[str, Any]

    recommendations: List[str]

    generated_at: datetime = Field(default_factory=datetime.utcnow)


class DashboardSummaryResponse(BaseModel):
    total_waste_analyzed_kg: float
    total_batches: int
    total_co2_saved: float
    total_water_saved: float
    average_circularity_score: float
    average_waste_diverted_percentage: float
    rating_distribution: Dict[str, int]
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class HealthResponse(BaseModel):
    status: str
    module: str = "sustainability-intelligence"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
