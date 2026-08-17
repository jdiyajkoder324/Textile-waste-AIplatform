from typing import Dict, Any

from app.ml_models.waste_classifier import classify_waste


def run_waste_classification(image_analysis_output: Dict[str, Any],
                              material_result: Dict[str, Any]) -> Dict[str, Any]:
    return classify_waste(
        material_result=material_result,
        damage_result=image_analysis_output["damage_result"],
        contamination_result=image_analysis_output["contamination_result"],
    )


def run_recyclability_assessment(image_analysis_output: Dict[str, Any],
                                  waste_result: Dict[str, Any]) -> Dict[str, Any]:
    damage_result = image_analysis_output["damage_result"]
    contamination_result = image_analysis_output["contamination_result"]

    damage_score = damage_result["damage_score"]
    contamination_pct = contamination_result["contamination_percentage"]

    reuse_potential = round(max(0.0, 100 - damage_score * 0.9 - contamination_pct * 0.6), 2)
    repairability_score = round(max(0.0, 100 - abs(damage_score - 35) * 1.2), 2)
    contamination_impact = round(min(100.0, contamination_pct * 1.1), 2)

    recyclability_percentage = waste_result["recyclability_percentage"]

    if waste_result["waste_category"] == "Hazardous Textile Waste":
        recommendation = ("This item shows significant contamination and should be routed to a "
                           "specialized hazardous textile waste handler rather than standard recycling.")
    elif recyclability_percentage > 70:
        recommendation = "High recyclability — suitable for standard fiber recovery or mechanical recycling."
    elif recyclability_percentage > 40:
        recommendation = "Moderate recyclability — consider reuse, repair, or partial fiber recovery."
    else:
        recommendation = "Low recyclability — prioritize reuse/upcycling or composting (if natural fiber)."

    notes = (
        f"Damage score {damage_score}/100, contamination {contamination_pct}% observed. "
        f"Waste category predicted as '{waste_result['waste_category']}'."
    )

    return {
        "recyclability_percentage": recyclability_percentage,
        "reuse_potential": reuse_potential,
        "repairability_score": repairability_score,
        "contamination_impact": contamination_impact,
        "disposal_recommendation": recommendation,
        "assessment_notes": notes,
    }
