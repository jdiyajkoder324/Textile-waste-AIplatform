from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class MaterialPredictionResponse(BaseModel):
    material: str
    confidence: float
    top_predictions: Optional[List[Dict[str, Any]]] = None
    explanation: Optional[str] = None

    class Config:
        from_attributes = True


class FabricPropertiesResponse(BaseModel):
    texture: Optional[str] = None
    thickness: Optional[float] = None
    softness: Optional[float] = None
    stretchability: Optional[float] = None
    weaving_pattern: Optional[str] = None
    fabric_density: Optional[float] = None
    surface_quality: Optional[float] = None
    color_distribution: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class WasteClassificationResponse(BaseModel):
    category: str
    confidence: float
    category_scores: Optional[Dict[str, float]] = None

    class Config:
        from_attributes = True


class DefectDetectionResponse(BaseModel):
    defects: Optional[List[Dict[str, Any]]] = None
    has_annotated_image: bool = False

    class Config:
        from_attributes = True


class RecyclabilityResponse(BaseModel):
    overall_score: float
    difficulty: str
    recommended_method: Optional[str] = None
    processing_complexity: Optional[str] = None
    carbon_reduction_estimate: Optional[float] = None
    environmental_impact: Optional[str] = None
    circular_economy_score: Optional[float] = None

    class Config:
        from_attributes = True


class SustainabilityResponse(BaseModel):
    water_saving_potential: Optional[float] = None
    energy_recovery: Optional[float] = None
    carbon_footprint_reduction: Optional[float] = None
    waste_diversion_score: Optional[float] = None
    landfill_reduction_estimate: Optional[float] = None
    circular_economy_contribution: Optional[float] = None
    overall_rating: Optional[str] = None

    class Config:
        from_attributes = True


class RecommendationResponse(BaseModel):
    action: str
    reason: Optional[str] = None
    priority: int

    class Config:
        from_attributes = True


class AnalysisSummaryResponse(BaseModel):
    """Lightweight shape used in history / list views."""
    id: int
    waste_batch_id: Optional[int] = None
    filename: str
    status: str
    is_favorite: bool
    created_at: datetime
    material: Optional[str] = None
    waste_category: Optional[str] = None
    recyclability_score: Optional[float] = None

    class Config:
        from_attributes = True


class AnalysisDetailResponse(BaseModel):
    """Full shape used in the Analysis Result page."""
    id: int
    waste_batch_id: Optional[int] = None
    filename: str
    status: str
    is_favorite: bool
    error_message: Optional[str] = None
    created_at: datetime

    material_prediction: Optional[MaterialPredictionResponse] = None
    fabric_properties: Optional[FabricPropertiesResponse] = None
    waste_classification: Optional[WasteClassificationResponse] = None
    defect_detection: Optional[DefectDetectionResponse] = None
    recyclability: Optional[RecyclabilityResponse] = None
    sustainability: Optional[SustainabilityResponse] = None
    recommendation: Optional[RecommendationResponse] = None

    class Config:
        from_attributes = True


class PaginatedHistoryResponse(BaseModel):
    items: List[AnalysisSummaryResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class DashboardStatsResponse(BaseModel):
    total_images_analyzed: int
    materials_detected: Dict[str, int]
    waste_categories: Dict[str, int]
    average_recyclability_score: float
    average_sustainability_score: float
    most_common_material: Optional[str] = None
    most_common_waste_category: Optional[str] = None
    recent_analyses: List[AnalysisSummaryResponse]
