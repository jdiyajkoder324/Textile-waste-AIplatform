"""
Milestone 2 — Material Recognition & Waste Classification models.

IMPORTANT: These are brand-new tables. Nothing here modifies
app/models/waste.py, user.py, prediction.py, or recommendation.py.
Existing functionality is untouched.
"""
import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float, Integer, ForeignKey, Enum, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.base import Base


class ImageAnalysis(Base):
    """
    One row per uploaded image. Image bytes are stored directly in
    PostgreSQL (as requested) so they're visible/manageable via pgAdmin4.
    """
    __tablename__ = "image_analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    waste_batch = relationship("Waste", back_populates="analyses")

    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    image_data = Column(LargeBinary, nullable=False)

    # pipeline status: uploaded -> processing -> completed -> failed
    status = Column(String, default="uploaded", nullable=False)
    error_message = Column(Text, nullable=True)

    is_favorite = Column(Integer, default=0)  # 0/1 (kept as Integer for simple DB portability)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    owner = relationship("User", backref="image_analyses")

    material_prediction = relationship(
        "MaterialPrediction", back_populates="analysis",
        uselist=False, cascade="all, delete-orphan"
    )
    fabric_properties = relationship(
        "FabricProperties", back_populates="analysis",
        uselist=False, cascade="all, delete-orphan"
    )
    waste_classification = relationship(
        "WasteClassification", back_populates="analysis",
        uselist=False, cascade="all, delete-orphan"
    )
    defect_detection = relationship(
        "DefectDetection", back_populates="analysis",
        uselist=False, cascade="all, delete-orphan"
    )
    recyclability = relationship(
        "RecyclabilityAssessment", back_populates="analysis",
        uselist=False, cascade="all, delete-orphan"
    )
    sustainability = relationship(
        "SustainabilityScore", back_populates="analysis",
        uselist=False, cascade="all, delete-orphan"
    )
    recommendation = relationship(
        "AnalysisRecommendation", back_populates="analysis",
        uselist=False, cascade="all, delete-orphan"
    )
    reports = relationship(
        "AnalysisReport", back_populates="analysis",
        cascade="all, delete-orphan"
    )

    waste_batch = relationship("Waste", back_populates="analyses")


class MaterialPrediction(Base):
    __tablename__ = "material_predictions"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("image_analyses.id"), nullable=False, index=True)

    material = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)
    # list of {"material": str, "confidence": float} — top 5 predictions
    top_predictions = Column(JSON, nullable=True)
    explanation = Column(Text, nullable=True)

    analysis = relationship("ImageAnalysis", back_populates="material_prediction")


class FabricProperties(Base):
    __tablename__ = "fabric_properties"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("image_analyses.id"), nullable=False, index=True)

    texture = Column(String(100))
    thickness = Column(Float)          # mm (mock)
    softness = Column(Float)           # 0-100 scale
    stretchability = Column(Float)     # 0-100 scale
    weaving_pattern = Column(String(100))
    fabric_density = Column(Float)     # gsm (mock)
    surface_quality = Column(Float)    # 0-100 scale
    color_distribution = Column(JSON)  # {"dominant": "#hex", "palette": [...]}

    analysis = relationship("ImageAnalysis", back_populates="fabric_properties")


class WasteClassification(Base):
    __tablename__ = "waste_classifications"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("image_analyses.id"), nullable=False, index=True)

    category = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)
    # {"Pre-consumer Waste": 0.12, "Post-consumer Waste": 0.63, ...}
    category_scores = Column(JSON, nullable=True)

    analysis = relationship("ImageAnalysis", back_populates="waste_classification")


class DefectDetection(Base):
    __tablename__ = "defect_detections"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("image_analyses.id"), nullable=False, index=True)

    # list of {"defect": "Tear", "confidence": 0.8, "bbox": [x,y,w,h]}
    defects = Column(JSON, nullable=True)
    annotated_image_data = Column(LargeBinary, nullable=True)

    analysis = relationship("ImageAnalysis", back_populates="defect_detection")


class RecyclabilityAssessment(Base):
    __tablename__ = "recyclability_assessments"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("image_analyses.id"), nullable=False, index=True)

    overall_score = Column(Float, nullable=False)          # 0-100
    difficulty = Column(String(20), nullable=False)        # Easy / Medium / Hard
    recommended_method = Column(String(150))
    processing_complexity = Column(String(20))
    carbon_reduction_estimate = Column(Float)               # kg CO2e (mock)
    environmental_impact = Column(String(300))
    circular_economy_score = Column(Float)                  # 0-100

    analysis = relationship("ImageAnalysis", back_populates="recyclability")


class SustainabilityScore(Base):
    __tablename__ = "sustainability_scores"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("image_analyses.id"), nullable=False, index=True)

    water_saving_potential = Column(Float)      # liters (mock)
    energy_recovery = Column(Float)             # kWh (mock)
    carbon_footprint_reduction = Column(Float)  # kg CO2e (mock)
    waste_diversion_score = Column(Float)       # 0-100
    landfill_reduction_estimate = Column(Float) # kg (mock)
    circular_economy_contribution = Column(Float) # 0-100
    overall_rating = Column(String(20))         # e.g. "A", "B", "C"

    analysis = relationship("ImageAnalysis", back_populates="sustainability")


class AnalysisRecommendation(Base):
    """
    Kept separate from the existing batch-based `recommendations` table
    (app/models/recommendation.py) so nothing already using that table
    is affected.
    """
    __tablename__ = "analysis_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("image_analyses.id"), nullable=False, index=True)

    action = Column(String(100), nullable=False)  # Donate/Repair/Recycle/Reuse/Upcycle/...
    reason = Column(Text, nullable=True)
    priority = Column(Integer, default=1)  # 1 = primary recommendation

    analysis = relationship("ImageAnalysis", back_populates="recommendation")


class AnalysisReport(Base):
    __tablename__ = "analysis_reports"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("image_analyses.id"), nullable=False, index=True)

    format = Column(String(10), nullable=False)  # pdf / csv / json
    file_data = Column(LargeBinary, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    analysis = relationship("ImageAnalysis", back_populates="reports")


class AnalysisType(str, enum.Enum):
    MATERIAL_RECOGNITION = "material_recognition"
    WASTE_CLASSIFICATION = "waste_classification"
    DAMAGE_DETECTION = "damage_detection"
    FULL_PIPELINE = "full_pipeline"  # material + waste + sustainability in one go


class AnalysisStatus(str, enum.Enum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class AnalysisHistory(Base):
    __tablename__ = "analysis_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # optional link to an inventory/waste batch item (wired fully in Phase 3)
    waste_batch_id = Column(UUID(as_uuid=True), ForeignKey("waste_batches.id", ondelete="SET NULL"), nullable=True, index=True)

    analysis_type = Column(Enum(AnalysisType), default=AnalysisType.FULL_PIPELINE, nullable=False)
    status = Column(Enum(AnalysisStatus), default=AnalysisStatus.PROCESSING, nullable=False)

    # uploaded file reference
    image_path = Column(String, nullable=True)
    original_filename = Column(String, nullable=True)

    # Milestone 2 outputs
    detected_material = Column(String, nullable=True)
    material_confidence = Column(Float, nullable=True)
    waste_category = Column(String, nullable=True)
    damage_level = Column(String, nullable=True)

    # Milestone 3 scores (top-level, indexable/sortable columns)
    recyclability_score = Column(Float, nullable=True)
    reuse_score = Column(Float, nullable=True)
    sustainability_score = Column(Float, nullable=True)
    material_recovery_score = Column(Float, nullable=True)
    circularity_score = Column(Float, nullable=True)
    overall_score = Column(Float, nullable=True)

    recommendation_summary = Column(Text, nullable=True)

    # full raw result payloads — keeps every engine's complete output without
    # needing a new column every time a service adds a field
    material_result = Column(JSONB, nullable=True)
    waste_classification_result = Column(JSONB, nullable=True)
    sustainability_result = Column(JSONB, nullable=True)
    environmental_impact_result = Column(JSONB, nullable=True)
    recommendation_result = Column(JSONB, nullable=True)

    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="analysis_history")
    waste_batch = relationship("WasteBatch", back_populates="analyses")