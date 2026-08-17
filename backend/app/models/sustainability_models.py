"""
sustainability_models.py

TASK 6 - Database Models for Milestone 3

    - SustainabilityMetrics
    - EnvironmentalImpact
    - WasteScore
    - CircularityAnalysis
    - RecommendationReport

NOTE: This file imports `Base` from app.database.base, matching the
confirmed TextileIntel project structure (backend/app/database/base.py).
"""

from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    DateTime,
    ForeignKey,
    JSON,
    Text,
)
from sqlalchemy.orm import relationship

from app.database.base import Base


class SustainabilityMetrics(Base):
    __tablename__ = "sustainability_metrics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    textile_id = Column(Integer, ForeignKey("waste_batches.id"), nullable=True, index=True)

    material_type = Column(String(100), nullable=False)
    weight_kg = Column(Float, nullable=False)

    carbon_current_emission = Column(Float, default=0.0)
    carbon_recycling_savings = Column(Float, default=0.0)
    carbon_net_savings = Column(Float, default=0.0)
    carbon_rating = Column(String(50), default="Average")

    diverted_percentage = Column(Float, default=0.0)
    recycled_percentage = Column(Float, default=0.0)
    reuse_percentage = Column(Float, default=0.0)
    recovery_percentage = Column(Float, default=0.0)

    sustainability_index = Column(Float, default=0.0)
    sustainability_rating = Column(String(50), default="Average")
    recommendations = Column(JSON, default=list)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EnvironmentalImpact(Base):
    __tablename__ = "environmental_impact"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    textile_id = Column(Integer, ForeignKey("waste_batches.id"), nullable=True, index=True)

    co2_saved = Column(Float, default=0.0)
    water_saved = Column(Float, default=0.0)
    landfill_saved = Column(Float, default=0.0)
    energy_saved = Column(Float, default=0.0)
    material_conserved = Column(Float, default=0.0)
    carbon_conserved = Column(Float, default=0.0)

    rating = Column(String(50), default="Average")
    recommendation = Column(Text, nullable=True)

    report_json = Column(JSON, default=dict)

    created_at = Column(DateTime, default=datetime.utcnow)


class WasteScore(Base):
    __tablename__ = "waste_scores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    textile_id = Column(Integer, ForeignKey("waste_batches.id"), nullable=True, index=True)

    recyclability = Column(Float, default=0.0)
    reuse = Column(Float, default=0.0)
    sustainability = Column(Float, default=0.0)
    recovery = Column(Float, default=0.0)
    circularity = Column(Float, default=0.0)
    category = Column(String(100), default="Moderate Recovery Potential")

    created_at = Column(DateTime, default=datetime.utcnow)


class CircularityAnalysis(Base):
    __tablename__ = "circularity_analysis"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    textile_id = Column(Integer, ForeignKey("waste_batches.id"), nullable=True, index=True)

    score = Column(Float, default=0.0)
    utilization = Column(Float, default=0.0)
    optimization = Column(Float, default=0.0)
    category = Column(String(100), default="Transitioning")

    recoverable_material = Column(Float, default=0.0)
    estimated_value = Column(Float, default=0.0)
    energy_recovery = Column(Float, default=0.0)
    resource_efficiency = Column(Float, default=0.0)

    created_at = Column(DateTime, default=datetime.utcnow)


class RecommendationReport(Base):
    __tablename__ = "recommendation_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    textile_id = Column(Integer, ForeignKey("waste_batches.id"), nullable=True, index=True)

    material_type = Column(String(100), nullable=False)
    circularity_score = Column(Float, default=0.0)
    recommendations = Column(JSON, default=list)

    created_at = Column(DateTime, default=datetime.utcnow)
