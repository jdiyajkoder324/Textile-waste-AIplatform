"""
Waste Classifier
-----------------
Combines material classification, damage detection, and contamination
detection outputs into the platform's 6 waste categories:
Recyclable, Reusable, Repairable, Upcyclable, Compostable, Hazardous.

Also runs a trained CNN (waste_proxy_cnn.pth, 96.9% acc on its own
training data) when an image is passed in. IMPORTANT CAVEAT: that model
was trained on Fashion-MNIST (28x28 grayscale garment icons), not real
textile-waste photos — it's a genuinely trained model, but its accuracy
on real photos will likely be much lower than 96.9% due to domain
mismatch. It's used as the primary signal here per your request, but
keep this caveat in mind for any report/demo.
"""
from typing import Dict, Any, Optional

import numpy as np

from app.ml_models.ml_inference import predict_waste_signal_ml

WASTE_CATEGORIES = [
    "Recyclable", "Reusable", "Repairable",
    "Upcyclable", "Compostable", "Hazardous Textile Waste",
]

NATURAL_FIBERS = {"Cotton", "Wool", "Silk", "Linen"}

DISPOSAL_MAP = {
    "Recyclable": "Drop off at a certified textile recycling facility for fiber recovery",
    "Reusable": "Donate or resell through second-hand / thrift channels",
    "Repairable": "Send for professional mending or DIY repair before reuse",
    "Upcyclable": "Redirect to upcycling / creative reuse workshops",
    "Compostable": "Compost through an industrial textile composting program (natural fiber only)",
    "Hazardous Textile Waste": "Handle via specialized hazardous-waste disposal channels",
}


def classify_waste(material_result: Dict[str, Any], damage_result: Dict[str, Any],
                    contamination_result: Dict[str, Any],
                    image_bgr: Optional[np.ndarray] = None) -> Dict[str, Any]:
    ml_signal = predict_waste_signal_ml(image_bgr) if image_bgr is not None else {"ml_available": False}

    material = material_result["material_name"]
    quality = material_result["fabric_quality"]
    damage_level = damage_result["damage_level"]
    damage_score = damage_result["damage_score"]
    contamination_pct = contamination_result["contamination_percentage"]

    scores = {c: 0.0 for c in WASTE_CATEGORIES}

    scores["Hazardous Textile Waste"] = max(0.0, contamination_pct * 1.4 - 20)

    if material in NATURAL_FIBERS:
        scores["Compostable"] = max(0.0, damage_score * 0.9 - contamination_pct * 0.3)
    else:
        scores["Compostable"] = max(0.0, damage_score * 0.15)

    if damage_level in ("Minor", "Moderate") and contamination_pct < 20:
        scores["Repairable"] = 70 - abs(damage_score - 30) * 0.8
    else:
        scores["Repairable"] = 15

    if damage_level in ("None", "Minor") and contamination_pct < 10 and quality in ("Excellent", "Good"):
        scores["Reusable"] = 85 - damage_score * 0.5 - contamination_pct
    else:
        scores["Reusable"] = 20

    scores["Upcyclable"] = 50 - abs(damage_score - 45) * 0.4 - max(0, contamination_pct - 15) * 0.5

    base_recyclable = 55 if material not in NATURAL_FIBERS else 40
    scores["Recyclable"] = base_recyclable - contamination_pct * 0.6 - damage_score * 0.1

    scores = {k: max(0.0, v) for k, v in scores.items()}
    total = sum(scores.values()) or 1.0
    normalized = {k: round(v / total * 100, 2) for k, v in scores.items()}
    ranked = sorted(normalized.items(), key=lambda x: -x[1])

    # --- Primary decision: trained CNN if available, else heuristic scoring ---
    if ml_signal.get("ml_available"):
        top_category = ml_signal["prediction"]
        top_score = ml_signal["confidence"]
        source = "ml_model_experimental"
    else:
        top_category, top_score = ranked[0]
        source = "heuristic"

    if damage_level == "None":
        condition = "Good"
    elif damage_level == "Minor":
        condition = "Lightly Worn"
    elif damage_level == "Moderate":
        condition = "Worn"
    else:
        condition = "Heavily Damaged"

    recyclability_percentage = round(max(0.0, 100 - contamination_pct * 0.8 - (
        {"None": 0, "Minor": 10, "Moderate": 30, "Severe": 55}[damage_level]
    )), 2)

    return {
        "waste_category": top_category,
        "waste_condition": condition,
        "damage_level": damage_level,
        "contamination_percentage": contamination_pct,
        "recyclability_percentage": recyclability_percentage,
        "disposal_method": DISPOSAL_MAP.get(top_category, DISPOSAL_MAP["Recyclable"]),
        "category_scores": normalized,
        "prediction_source": source,
        "ml_confidence": top_score if ml_signal.get("ml_available") else None,
    }
