"""
Damage & Contamination Detector
--------------------------------
Detects visual damage (tears, frays, holes) using a trained CNN
(damage_cnn_final.pth, 88% accuracy) when available, with a heuristic
edge/contour-based fallback when the trained model isn't loaded.

Contamination detection (stains, discoloration) remains heuristic-only
(HSV blob analysis) — no trained model exists for this yet.
"""
from typing import Dict, Any, List

import cv2
import numpy as np

from app.ml_models.ml_inference import predict_damage_ml


def detect_damage(image_bgr: np.ndarray) -> Dict[str, Any]:
    ml_result = predict_damage_ml(image_bgr)

    # --- Heuristic pass always runs too — gives bounding-box regions the CNN doesn't provide ---
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, (300, 300))

    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    irregular_contours = 0
    damage_regions: List[Dict[str, Any]] = []
    for c in contours:
        area = cv2.contourArea(c)
        if area < 15:
            continue
        perimeter = cv2.arcLength(c, True)
        if perimeter == 0:
            continue
        circularity = 4 * np.pi * area / (perimeter ** 2)
        if circularity < 0.25 and 15 < area < 900:
            irregular_contours += 1
            x, y, w, h = cv2.boundingRect(c)
            damage_regions.append({
                "x": int(x), "y": int(y), "width": int(w), "height": int(h),
                "circularity": round(float(circularity), 3),
            })
    damage_regions = damage_regions[:15]
    heuristic_score = min(100.0, irregular_contours * 2.2)

    # --- Primary decision: trained CNN if available, else heuristic fallback ---
    if ml_result.get("ml_available"):
        damage_detected = ml_result["prediction"] == "Defect"
        damage_score = round(ml_result["confidence"], 2) if damage_detected else round(100 - ml_result["confidence"], 2)

        if not damage_detected:
            damage_level = "None"
        elif damage_score < 40:
            damage_level = "Minor"
        elif damage_score < 70:
            damage_level = "Moderate"
        else:
            damage_level = "Severe"

        source = "ml_model"
        ml_confidence = ml_result["confidence"]
    else:
        damage_score = round(heuristic_score, 2)
        if damage_score < 8:
            damage_level, damage_detected = "None", False
        elif damage_score < 25:
            damage_level, damage_detected = "Minor", True
        elif damage_score < 55:
            damage_level, damage_detected = "Moderate", True
        else:
            damage_level, damage_detected = "Severe", True

        source = "heuristic_fallback"
        ml_confidence = None

    return {
        "damage_detected": damage_detected,
        "damage_level": damage_level,
        "damage_score": damage_score,
        "damage_regions": damage_regions,
        "irregular_edge_count": irregular_contours,
        "prediction_source": source,
        "ml_confidence": ml_confidence,
    }


def detect_contamination(image_bgr: np.ndarray) -> Dict[str, Any]:
    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
    hsv = cv2.resize(hsv, (300, 300))

    h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]

    stain_mask = (v < 60).astype(np.uint8)
    discoloration_mask = ((s < 30) & (v > 60) & (v < 200)).astype(np.uint8)

    total_pixels = v.size
    stain_pct = float(np.count_nonzero(stain_mask)) / total_pixels * 100
    discoloration_pct = float(np.count_nonzero(discoloration_mask)) / total_pixels * 100

    contamination_pct = round(min(100.0, stain_pct * 1.3 + discoloration_pct * 0.6), 2)

    contamination_types = []
    if stain_pct > 3:
        contamination_types.append("Stains")
    if discoloration_pct > 8:
        contamination_types.append("Discoloration")
    if contamination_pct > 35:
        contamination_types.append("Heavy Soiling")

    contamination_detected = contamination_pct > 5.0

    return {
        "contamination_detected": contamination_detected,
        "contamination_percentage": contamination_pct,
        "contamination_types": contamination_types,
        "stain_percentage": round(stain_pct, 2),
        "discoloration_percentage": round(discoloration_pct, 2),
    }
