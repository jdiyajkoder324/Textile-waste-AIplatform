"""
Image Analysis Engine — coordinates OpenCV/Pillow preprocessing and the
texture, color, damage, and contamination ML modules.
"""
from typing import Dict, Any

import cv2
import numpy as np
from PIL import Image
import io

from app.ml_models.texture_analyzer import analyze_texture
from app.ml_models.color_analyzer import analyze_color
from app.ml_models.contamination_detector import detect_damage, detect_contamination


def load_image_bgr(image_bytes: bytes):
    pil_image = Image.open(io.BytesIO(image_bytes))
    pil_image = pil_image.convert("RGB")
    width, height = pil_image.size
    np_rgb = np.array(pil_image)
    bgr = cv2.cvtColor(np_rgb, cv2.COLOR_RGB2BGR)
    return bgr, width, height


def compute_quality_score(image_bgr: np.ndarray, damage_score: float, contamination_pct: float) -> float:
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
    sharpness_score = min(100, sharpness / 8)
    brightness = float(np.mean(gray))
    exposure_penalty = abs(brightness - 130) / 130 * 30

    quality = sharpness_score - exposure_penalty - damage_score * 0.3 - contamination_pct * 0.2
    return round(max(0.0, min(100.0, quality)), 2)


def run_image_analysis(image_bytes: bytes, filename: str, content_type: str) -> Dict[str, Any]:
    image_bgr, width, height = load_image_bgr(image_bytes)

    texture_result = analyze_texture(image_bgr)
    color_result = analyze_color(image_bgr)
    damage_result = detect_damage(image_bgr)
    contamination_result = detect_contamination(image_bgr)

    quality_score = float(compute_quality_score(
    image_bgr, damage_result["damage_score"], contamination_result["contamination_percentage"]
    ))

    fabric_confidence = round(min(99.0, 60 + texture_result["texture_confidence"] * 0.35), 2)

    metadata = {
        "original_filename": filename,
        "content_type": content_type,
        "width": width,
        "height": height,
        "aspect_ratio": round(width / height, 3) if height else None,
        "size_bytes": len(image_bytes),
    }

    return {
        "width": width,
        "height": height,
        "image_metadata": metadata,
        "texture_result": texture_result,
        "color_result": color_result,
        "damage_result": damage_result,
        "contamination_result": contamination_result,
        "fabric_confidence_score": fabric_confidence,
        "image_quality_score": quality_score,
        "image_bgr": image_bgr,
    }
