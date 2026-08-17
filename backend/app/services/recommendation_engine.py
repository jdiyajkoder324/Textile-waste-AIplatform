"""
recommendation_engine.py

TASK 4 - Recommendation Engine

Generates actionable recommendations based on material type and computed
circularity/waste scores.
"""

from typing import List, Dict, Any


MATERIAL_RECOMMENDATIONS: Dict[str, List[str]] = {
    "cotton": [
        "Mechanical recycling",
        "Fiber recovery",
        "Donation",
        "Upcycling",
    ],
    "polyester": [
        "Chemical recycling",
        "Textile recovery",
    ],
    "denim": [
        "Mechanical recycling",
        "Upcycling into new denim products",
    ],
    "silk": [
        "Donation / resale (high value material)",
        "Careful mechanical recycling",
    ],
    "wool": [
        "Fiber recovery",
        "Reuse in insulation products",
    ],
    "jute": [
        "Composting",
        "Fiber recovery",
    ],
    "mixed": [
        "Material separation",
        "Send to specialised blended-fabric recycler",
    ],
}


class RecommendationEngine:

    def generate_recommendations(
        self,
        material_type: str,
        circularity_score: float,
        contamination_level: float = 0.0,
    ) -> Dict[str, Any]:
        recommendations: List[str] = []

        material_key = (material_type or "mixed").strip().lower()
        is_blended = material_key in ("mixed", "blended") or "/" in (material_type or "")

        if is_blended:
            recommendations.extend(MATERIAL_RECOMMENDATIONS["mixed"])
        else:
            recommendations.extend(
                MATERIAL_RECOMMENDATIONS.get(material_key, MATERIAL_RECOMMENDATIONS["mixed"])
            )

        # Score-driven overrides / additions
        if circularity_score < 40:
            recommendations.append("Disposal recommendation — low recovery viability.")
        elif circularity_score >= 75:
            recommendations.append("Recycling recommendation — strong circularity potential.")

        if contamination_level and contamination_level > 60:
            recommendations.append("Decontamination required before any recovery pathway.")

        # De-duplicate while preserving order
        seen = set()
        deduped = []
        for r in recommendations:
            if r not in seen:
                deduped.append(r)
                seen.add(r)

        return {"recommendations": deduped}


recommendation_engine = RecommendationEngine()
