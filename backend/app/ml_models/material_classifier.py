"""
Material Classifier
--------------------
Dummy pretrained-style classifier that maps texture + color + sheen
statistics onto one of the platform's 10 supported fabric materials, plus
a plausible fiber-composition blend. Deterministic given the same image
statistics (seeded by an image hash) so repeated analysis is stable.

Swap point for a real model: replace `predict_material()` internals with a
trained TensorFlow/PyTorch inference call while keeping the same signature.
"""
import hashlib
from typing import Dict, Any

import numpy as np

MATERIAL_PROFILES = {
    # texture affinity, sheen affinity (0-1), category, base quality
    "Cotton":         {"texture": ["Woven", "Fine-weave", "Plain Weave"], "sheen": 0.15, "category": "Natural Fiber"},
    "Polyester":      {"texture": ["Smooth", "Textured"],                 "sheen": 0.65, "category": "Synthetic Fiber"},
    "Wool":           {"texture": ["Knit", "Rough", "Textured"],          "sheen": 0.10, "category": "Natural Fiber"},
    "Silk":           {"texture": ["Smooth", "Fine-weave"],               "sheen": 0.85, "category": "Natural Fiber"},
    "Linen":          {"texture": ["Woven", "Rough"],                     "sheen": 0.20, "category": "Natural Fiber"},
    "Denim":          {"texture": ["Ribbed", "Woven", "Rough"],           "sheen": 0.12, "category": "Natural Fiber"},
    "Nylon":          {"texture": ["Smooth", "Textured"],                 "sheen": 0.70, "category": "Synthetic Fiber"},
    "Rayon":          {"texture": ["Smooth", "Fine-weave"],               "sheen": 0.55, "category": "Semi-Synthetic Fiber"},
    "Acrylic":        {"texture": ["Knit", "Textured"],                   "sheen": 0.45, "category": "Synthetic Fiber"},
    "Mixed Fabrics":  {"texture": ["Woven", "Knit", "Textured", "Rough", "Smooth", "Ribbed", "Fine-weave"], "sheen": 0.40, "category": "Blended Fiber"},
}


def _image_seed(image_bgr: np.ndarray) -> int:
    h = hashlib.md5(image_bgr.tobytes()[:5000]).hexdigest()
    return int(h[:8], 16)


def _sheen_score(brightness: float, saturation: float) -> float:
    # High brightness + moderate-low saturation tends to correlate with sheen (silk/polyester)
    return float(min(1.0, max(0.0, (brightness / 255.0) * 0.7 + (1 - saturation / 255.0) * 0.3)))


def predict_material(texture_result: Dict[str, Any], color_result: Dict[str, Any],
                      image_bgr: np.ndarray) -> Dict[str, Any]:
    texture = texture_result["fabric_texture"]
    pattern = texture_result["fabric_pattern"]
    brightness = color_result["brightness"]
    saturation = color_result["saturation"]
    sheen = _sheen_score(brightness, saturation)

    seed = _image_seed(image_bgr)
    rng = np.random.default_rng(seed)

    scores = {}
    for material, profile in MATERIAL_PROFILES.items():
        score = 0.0
        if texture in profile["texture"]:
            score += 55.0
        else:
            score += 10.0
        score -= abs(profile["sheen"] - sheen) * 40.0
        # small deterministic jitter so results aren't perfectly tied
        score += rng.uniform(-4, 4)
        scores[material] = max(0.0, score)

    total = sum(scores.values()) or 1.0
    normalized = {m: round(s / total * 100, 2) for m, s in scores.items()}

    ranked = sorted(normalized.items(), key=lambda x: -x[1])
    top_material, top_score = ranked[0]

    # Build a plausible fiber composition (top 3 contributors + "Others")
    top_three = ranked[:3]
    composition_total = sum(v for _, v in top_three)
    fiber_composition = {m: round(v / composition_total * 100, 1) for m, v in top_three}
    accounted = sum(fiber_composition.values())
    if accounted < 100:
        fiber_composition["Others"] = round(100 - accounted, 1)

    is_blend = fiber_composition.get(top_material, 100) < 80
    blend_label = (
        f"{top_material} blend ({', '.join(list(fiber_composition.keys())[:3])})"
        if is_blend else f"Pure {top_material}"
    )

    quality_index = (top_score * 0.6) + (color_result["colorfulness"] * 0.1)
    quality_index = max(0, min(100, quality_index))
    if quality_index > 80:
        fabric_quality = "Excellent"
    elif quality_index > 60:
        fabric_quality = "Good"
    elif quality_index > 40:
        fabric_quality = "Fair"
    else:
        fabric_quality = "Poor"

    category = MATERIAL_PROFILES[top_material]["category"]

    # Sustainability leans toward natural/semi-synthetic fibers and away from synthetics
    sustainability_base = {
        "Natural Fiber": 78, "Semi-Synthetic Fiber": 60, "Synthetic Fiber": 38, "Blended Fiber": 55,
    }[category]
    sustainability_score = round(min(100, max(0, sustainability_base + (fabric_quality == "Excellent") * 5
                                               - (fabric_quality == "Poor") * 10)), 1)

    return {
        "material_name": top_material,
        "fabric_category": category,
        "fiber_composition": fiber_composition,
        "blend_identification": blend_label,
        "fabric_quality": fabric_quality,
        "fabric_texture": texture,
        "pattern_information": pattern,
        "color_information": color_result["dominant_colors"],
        "sustainability_score": sustainability_score,
        "material_confidence_percentage": round(top_score, 2),
        "all_scores": normalized,
    }