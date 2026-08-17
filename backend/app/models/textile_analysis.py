"""
Milestone 2 models — Material Recognition & Waste Classification.

Kept in a separate module with distinct table names (twip_*) so they cannot
collide with the existing app/models/prediction.py, recommendation.py, or
analysis.py, whatever those currently contain. Those files are left untouched.
"""
import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime,
    ForeignKey, LargeBinary, JSON,
)
from sqlalchemy.orm import relationship

from app.database.base import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class ImageAnalysis(Base):
    __tablename__ = "twip_image_analyses"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    waste_batch_id = Column(Integer, ForeignKey("waste_batches.id"), nullable=True, index=True)

    filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    image_data = Column(LargeBinary, nullable=False)
    file_size_bytes = Column(Integer, default=0)

    width = Column(Integer)
    height = Column(Integer)

    fabric_texture = Column(String(100))
    fabric_pattern = Column(String(100))
    dominant_colors = Column(JSON)
    damage_detected = Column(Boolean, default=False)
    damage_level = Column(String(50))
    damage_regions = Column(JSON)
    contamination_detected = Column(Boolean, default=False)
    contamination_percentage = Column(Float, default=0.0)
    contamination_types = Column(JSON)
    image_metadata = Column(JSON)
    fabric_confidence_score = Column(Float, default=0.0)
    image_quality_score = Column(Float, default=0.0)

    status = Column(String(30), default="processed")
    created_at = Column(DateTime, default=datetime.utcnow)

    material_classification = relationship(
        "MaterialClassification", back_populates="image", uselist=False, cascade="all, delete-orphan"
    )
    waste_classification = relationship(
        "WasteClassification", back_populates="image", uselist=False, cascade="all, delete-orphan"
    )
    recyclability_assessment = relationship(
        "RecyclabilityAssessment", back_populates="image", uselist=False, cascade="all, delete-orphan"
    )
    recommendation = relationship(
        "RecyclingRecommendation", back_populates="image", uselist=False, cascade="all, delete-orphan"
    )
    reports = relationship("AnalysisReport", back_populates="image", cascade="all, delete-orphan")


class MaterialClassification(Base):
    __tablename__ = "twip_material_classifications"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    image_id = Column(String(36), ForeignKey("twip_image_analyses.id"), nullable=False)

    material_name = Column(String(100), nullable=False)
    fabric_category = Column(String(100))
    fiber_composition = Column(JSON)
    blend_identification = Column(String(255))
    fabric_quality = Column(String(50))
    fabric_texture = Column(String(100))
    color_information = Column(JSON)
    pattern_information = Column(String(100))
    sustainability_score = Column(Float, default=0.0)
    material_confidence_percentage = Column(Float, default=0.0)

    created_at = Column(DateTime, default=datetime.utcnow)

    image = relationship("ImageAnalysis", back_populates="material_classification")


class WasteClassification(Base):
    __tablename__ = "twip_waste_classifications"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    image_id = Column(String(36), ForeignKey("twip_image_analyses.id"), nullable=False)

    waste_category = Column(String(50), nullable=False)
    waste_condition = Column(String(50))
    damage_level = Column(String(50))
    contamination_percentage = Column(Float, default=0.0)
    recyclability_percentage = Column(Float, default=0.0)
    disposal_method = Column(String(150))
    category_scores = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)

    image = relationship("ImageAnalysis", back_populates="waste_classification")


class RecyclabilityAssessment(Base):
    __tablename__ = "twip_recyclability_assessments"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    image_id = Column(String(36), ForeignKey("twip_image_analyses.id"), nullable=False)

    recyclability_percentage = Column(Float, default=0.0)
    reuse_potential = Column(Float, default=0.0)
    repairability_score = Column(Float, default=0.0)
    contamination_impact = Column(Float, default=0.0)
    disposal_recommendation = Column(String)
    assessment_notes = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)

    image = relationship("ImageAnalysis", back_populates="recyclability_assessment")


class RecyclingRecommendation(Base):
    __tablename__ = "twip_recycling_recommendations"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    image_id = Column(String(36), ForeignKey("twip_image_analyses.id"), nullable=False)

    best_recycling_method = Column(String(100))
    ranked_methods = Column(JSON)
    sustainability_score = Column(Float, default=0.0)
    environmental_impact_score = Column(Float, default=0.0)
    reuse_suggestions = Column(JSON)
    waste_reduction_strategies = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)

    image = relationship("ImageAnalysis", back_populates="recommendation")


class AnalysisReport(Base):
    __tablename__ = "twip_reports"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    image_id = Column(String(36), ForeignKey("twip_image_analyses.id"), nullable=False)

    report_format = Column(String(10), nullable=False)
    file_data = Column(LargeBinary, nullable=False)
    file_name = Column(String(255), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    image = relationship("ImageAnalysis", back_populates="reports")
