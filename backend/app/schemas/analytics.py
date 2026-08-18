from datetime import date, datetime
from typing import Optional, Dict, List, Any
from pydantic import BaseModel


class DateRangeFilter(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class RecyclerDashboardResponse(BaseModel):
    total_waste_received_kg: float
    pending_waste_kg: float
    processed_waste_kg: float
    waste_by_material: Dict[str, float]
    waste_by_category: Dict[str, int]
    recycling_opportunities: int
    reuse_opportunities: int
    material_recovery_avg_pct: float
    waste_diversion_avg_pct: float
    processing_trend: List[Dict[str, Any]]  # [{date: str, processed_kg: float}]


class SustainabilityDashboardResponse(BaseModel):
    overall_sustainability_score: float
    circularity_score: float
    recyclability_score: float
    reuse_score: float
    material_recovery_score: float
    total_co2_saved_kg: float
    total_water_saved_l: float
    total_landfill_saved_kg: float
    waste_diversion_pct: float
    recycling_rate_pct: float
    reuse_rate_pct: float
    sustainability_trend: List[Dict[str, Any]]  # [{date: str, index: float}]
    rating_distribution: Dict[str, int]


class ManufacturerDashboardResponse(BaseModel):
    total_production_waste_kg: float
    waste_generation_trend: List[Dict[str, Any]]  # [{date: str, kg: float}]
    waste_by_material: Dict[str, float]
    waste_by_category: Dict[str, int]
    recycling_opportunities: int
    reuse_opportunities: int
    material_recovery_potential_kg: float
    sustainability_performance_score: float
    waste_reduction_trend: List[Dict[str, Any]]


class AdminDashboardResponse(BaseModel):
    total_users: int
    users_by_role: Dict[str, int]
    active_users_30d: int
    total_waste_records: int
    total_analyses: int
    total_recommendations: int
    total_reports: int
    recent_activity: List[Dict[str, str]]  # [{type, description, timestamp}]
    system_status: str