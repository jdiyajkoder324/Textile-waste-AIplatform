from sqlalchemy.orm import Session

from app.models.textile_analysis import (
    ImageAnalysis, MaterialClassification, WasteClassification,
    RecyclabilityAssessment, RecyclingRecommendation,
)
from app.services.image_engine import run_image_analysis
from app.services.material_engine import run_material_classification
from app.services.waste_engine import run_waste_classification, run_recyclability_assessment
from app.services.recycling_engine import generate_recommendation


def run_full_pipeline(db: Session, image_record: ImageAnalysis, image_bytes: bytes):
    analysis_output = run_image_analysis(image_bytes, image_record.filename, image_record.content_type)

    image_record.width = analysis_output["width"]
    image_record.height = analysis_output["height"]
    image_record.fabric_texture = analysis_output["texture_result"]["fabric_texture"]
    image_record.fabric_pattern = analysis_output["texture_result"]["fabric_pattern"]
    image_record.dominant_colors = analysis_output["color_result"]["dominant_colors"]
    image_record.damage_detected = analysis_output["damage_result"]["damage_detected"]
    image_record.damage_level = analysis_output["damage_result"]["damage_level"]
    image_record.damage_regions = analysis_output["damage_result"]["damage_regions"]
    image_record.contamination_detected = analysis_output["contamination_result"]["contamination_detected"]
    image_record.contamination_percentage = analysis_output["contamination_result"]["contamination_percentage"]
    image_record.contamination_types = analysis_output["contamination_result"]["contamination_types"]
    image_record.image_metadata = analysis_output["image_metadata"]
    image_record.fabric_confidence_score = analysis_output["fabric_confidence_score"]
    image_record.image_quality_score = analysis_output["image_quality_score"]
    image_record.status = "processed"

    material_result = run_material_classification(analysis_output)
    material_record = MaterialClassification(
        image_id=image_record.id,
        material_name=material_result["material_name"],
        fabric_category=material_result["fabric_category"],
        fiber_composition=material_result["fiber_composition"],
        blend_identification=material_result["blend_identification"],
        fabric_quality=material_result["fabric_quality"],
        fabric_texture=material_result["fabric_texture"],
        color_information=material_result["color_information"],
        pattern_information=material_result["pattern_information"],
        sustainability_score=material_result["sustainability_score"],
        material_confidence_percentage=material_result["material_confidence_percentage"],
    )

    waste_result = run_waste_classification(analysis_output, material_result)
    waste_record = WasteClassification(
        image_id=image_record.id,
        waste_category=waste_result["waste_category"],
        waste_condition=waste_result["waste_condition"],
        damage_level=waste_result["damage_level"],
        contamination_percentage=waste_result["contamination_percentage"],
        recyclability_percentage=waste_result["recyclability_percentage"],
        disposal_method=waste_result["disposal_method"],
        category_scores=waste_result["category_scores"],
    )

    recyclability_result = run_recyclability_assessment(analysis_output, waste_result)
    recyclability_record = RecyclabilityAssessment(
        image_id=image_record.id,
        recyclability_percentage=recyclability_result["recyclability_percentage"],
        reuse_potential=recyclability_result["reuse_potential"],
        repairability_score=recyclability_result["repairability_score"],
        contamination_impact=recyclability_result["contamination_impact"],
        disposal_recommendation=recyclability_result["disposal_recommendation"],
        assessment_notes=recyclability_result["assessment_notes"],
    )

    recommendation_result = generate_recommendation(material_result, waste_result, recyclability_result)
    recommendation_record = RecyclingRecommendation(
        image_id=image_record.id,
        best_recycling_method=recommendation_result["best_recycling_method"],
        ranked_methods=recommendation_result["ranked_methods"],
        sustainability_score=recommendation_result["sustainability_score"],
        environmental_impact_score=recommendation_result["environmental_impact_score"],
        reuse_suggestions=recommendation_result["reuse_suggestions"],
        waste_reduction_strategies=recommendation_result["waste_reduction_strategies"],
    )

    db.add(image_record)
    db.add(material_record)
    db.add(waste_record)
    db.add(recyclability_record)
    db.add(recommendation_record)
    db.commit()

    db.refresh(image_record)
    db.refresh(material_record)
    db.refresh(waste_record)
    db.refresh(recyclability_record)
    db.refresh(recommendation_record)

    return image_record, material_record, waste_record, recyclability_record, recommendation_record
