from typing import Dict, Any

RECYCLING_METHODS = [
    "Fiber Recycling", "Mechanical Recycling", "Chemical Recycling",
    "Fabric Reuse", "Donation", "Upcycling", "Industrial Recovery",
]

SYNTHETIC_MATERIALS = {"Polyester", "Nylon", "Acrylic", "Rayon"}
NATURAL_MATERIALS = {"Cotton", "Wool", "Silk", "Linen", "Denim"}


def generate_recommendation(material_result: Dict[str, Any], waste_result: Dict[str, Any],
                             recyclability_result: Dict[str, Any]) -> Dict[str, Any]:
    material = material_result["material_name"]
    waste_category = waste_result["waste_category"]
    recyclability = recyclability_result["recyclability_percentage"]
    reuse_potential = recyclability_result["reuse_potential"]
    repairability = recyclability_result["repairability_score"]
    sustainability_base = material_result["sustainability_score"]

    scores = {m: 0.0 for m in RECYCLING_METHODS}

    if material in SYNTHETIC_MATERIALS:
        scores["Chemical Recycling"] = 60 + recyclability * 0.3
        scores["Fiber Recycling"] = 55 + recyclability * 0.25
        scores["Industrial Recovery"] = 45 + recyclability * 0.2
    else:
        scores["Fiber Recycling"] = 50 + recyclability * 0.3
        scores["Mechanical Recycling"] = 55 + recyclability * 0.25

    scores["Fabric Reuse"] = reuse_potential * 0.9
    scores["Donation"] = reuse_potential * 0.85 if waste_category in ("Reusable", "Repairable") else reuse_potential * 0.3
    scores["Upcycling"] = (100 - recyclability) * 0.5 + repairability * 0.2
    scores["Industrial Recovery"] += recyclability * 0.15

    if waste_category == "Hazardous Textile Waste":
        for m in scores:
            scores[m] *= 0.2
        scores["Industrial Recovery"] = 35.0

    ranked = sorted(scores.items(), key=lambda x: -x[1])
    ranked_methods = [{"method": m, "score": round(max(0.0, s), 2)} for m, s in ranked]
    best_method = ranked_methods[0]["method"]

    environmental_impact_score = round(min(100, max(0, (
        sustainability_base * 0.5 + recyclability * 0.3 + reuse_potential * 0.2
    ))), 2)

    reuse_suggestions = []
    if reuse_potential > 60:
        reuse_suggestions.append("Suitable for direct resale via thrift or online second-hand platforms")
    if repairability > 50:
        reuse_suggestions.append("Minor repairs could extend usable life significantly")
    if material in NATURAL_MATERIALS:
        reuse_suggestions.append("Natural fiber content supports composting as an end-of-life option")
    if not reuse_suggestions:
        reuse_suggestions.append("Best suited for material recovery rather than direct reuse")

    waste_reduction_strategies = [
        f"Prioritize {best_method.lower()} to maximize material recovery value",
        "Sort textile waste by fiber type at collection point to improve downstream recycling yield",
        "Educate contributors on contamination-free disposal to raise recyclability scores",
    ]
    if waste_category == "Compostable":
        waste_reduction_strategies.append("Route to industrial textile composting to divert from landfill")

    return {
        "best_recycling_method": best_method,
        "ranked_methods": ranked_methods,
        "sustainability_score": sustainability_base,
        "environmental_impact_score": environmental_impact_score,
        "reuse_suggestions": reuse_suggestions,
        "waste_reduction_strategies": waste_reduction_strategies,
    }
