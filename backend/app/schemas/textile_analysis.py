from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, ConfigDict


class ImageAnalysisOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    content_type: str
    file_size_bytes: int
    width: Optional[int] = None
    height: Optional[int] = None
    fabric_texture: Optional[str] = None
    fabric_pattern: Optional[str] = None
    dominant_colors: Optional[List[Dict[str, Any]]] = None
    damage_detected: bool = False
    damage_level: Optional[str] = None
    damage_regions: Optional[List[Dict[str, Any]]] = None
    contamination_detected: bool = False
    contamination_percentage: float = 0.0
    contamination_types: Optional[List[str]] = None
    image_metadata: Optional[Dict[str, Any]] = None
    fabric_confidence_score: float = 0.0
    image_quality_score: float = 0.0
    status: str
    created_at: datetime


class MaterialClassificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    image_id: str
    material_name: str
    fabric_category: Optional[str] = None
    fiber_composition: Optional[Dict[str, float]] = None
    blend_identification: Optional[str] = None
    fabric_quality: Optional[str] = None
    fabric_texture: Optional[str] = None
    color_information: Optional[List[Dict[str, Any]]] = None
    pattern_information: Optional[str] = None
    sustainability_score: float = 0.0
    material_confidence_percentage: float = 0.0
    created_at: datetime


class WasteClassificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    image_id: str
    waste_category: str
    waste_condition: Optional[str] = None
    damage_level: Optional[str] = None
    contamination_percentage: float = 0.0
    recyclability_percentage: float = 0.0
    disposal_method: Optional[str] = None
    category_scores: Optional[Dict[str, float]] = None
    created_at: datetime


class RecyclabilityAssessmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    image_id: str
    recyclability_percentage: float
    reuse_potential: float
    repairability_score: float
    contamination_impact: float
    disposal_recommendation: Optional[str] = None
    assessment_notes: Optional[str] = None
    created_at: datetime


class RecyclingRecommendationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    image_id: str
    best_recycling_method: str
    ranked_methods: Optional[List[Dict[str, Any]]] = None
    sustainability_score: float
    environmental_impact_score: float
    reuse_suggestions: Optional[List[str]] = None
    waste_reduction_strategies: Optional[List[str]] = None
    created_at: datetime


class FullAnalysisOut(BaseModel):
    image_analysis: ImageAnalysisOut
    material_classification: MaterialClassificationOut
    waste_classification: WasteClassificationOut
    recyclability_assessment: RecyclabilityAssessmentOut
    recycling_recommendation: RecyclingRecommendationOut
