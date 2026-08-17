"""
Texture Analyzer
----------------
Extracts real, measurable texture statistics from an image using OpenCV
and maps them onto human-readable fabric texture / pattern labels
(heuristic — no trained model exists for readable labels).

Additionally runs a trained CNN (pattern_texture_cnn.pth, 69.4% accuracy,
18 classes) that predicts a numeric texture *cluster* — a real learned
signal, but without human-readable names (the source dataset didn't
provide a name mapping for these classes). Exposed as `ml_texture_cluster`
alongside the heuristic labels.
"""
from typing import Dict, Any

import cv2
import numpy as np

from app.ml_models.ml_inference import predict_texture_cluster_ml

TEXTURE_LABELS = ["Smooth", "Woven", "Ribbed", "Knit", "Rough", "Textured", "Fine-weave"]
PATTERN_LABELS = ["Solid", "Striped", "Checked", "Printed", "Floral", "Geometric", "Plain Weave"]


def _edge_density(gray: np.ndarray) -> float:
    edges = cv2.Canny(gray, 60, 160)
    return float(np.count_nonzero(edges)) / float(edges.size)


def _local_variance(gray: np.ndarray, k: int = 9) -> float:
    mean = cv2.blur(gray.astype(np.float32), (k, k))
    sq_mean = cv2.blur((gray.astype(np.float32)) ** 2, (k, k))
    variance = sq_mean - mean ** 2
    return float(np.mean(variance))


def _directional_energy(gray: np.ndarray) -> Dict[str, float]:
    """Approximate GLCM-style directional gradient energy (horizontal vs vertical)."""
    sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    return {
        "horizontal_energy": float(np.mean(np.abs(sobel_x))),
        "vertical_energy": float(np.mean(np.abs(sobel_y))),
    }


def analyze_texture(image_bgr: np.ndarray) -> Dict[str, Any]:
    ml_result = predict_texture_cluster_ml(image_bgr)

    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, (256, 256))

    edge_density = _edge_density(gray)
    variance = _local_variance(gray)
    energy = _directional_energy(gray)
    laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())

    directional_ratio = energy["horizontal_energy"] / (energy["vertical_energy"] + 1e-6)

    if edge_density < 0.03 and variance < 150:
        texture = "Smooth"
    elif edge_density > 0.15 and variance > 700:
        texture = "Rough"
    elif 0.6 <= directional_ratio <= 1.6 and variance > 300:
        texture = "Woven"
    elif directional_ratio > 1.8:
        texture = "Ribbed"
    elif variance > 500:
        texture = "Textured"
    elif variance > 200:
        texture = "Knit"
    else:
        texture = "Fine-weave"

    f = np.fft.fft2(gray)
    fshift = np.fft.fftshift(f)
    magnitude = np.abs(fshift)
    magnitude[magnitude.shape[0] // 2, magnitude.shape[1] // 2] = 0
    peak_ratio = float(np.max(magnitude) / (np.mean(magnitude) + 1e-6))

    if peak_ratio > 40 and edge_density > 0.08:
        pattern = "Geometric"
    elif peak_ratio > 25:
        pattern = "Striped" if directional_ratio > 1.4 or directional_ratio < 0.7 else "Checked"
    elif edge_density > 0.12:
        pattern = "Printed"
    elif variance < 100:
        pattern = "Solid"
    else:
        pattern = "Plain Weave"

    texture_confidence = round(min(99.0, 55 + edge_density * 150 + min(variance, 400) / 20), 2)

    return {
        "fabric_texture": texture,
        "fabric_pattern": pattern,
        "texture_confidence": texture_confidence,
        "ml_texture_cluster": ml_result.get("texture_cluster") if ml_result.get("ml_available") else None,
        "ml_cluster_confidence": ml_result.get("confidence") if ml_result.get("ml_available") else None,
        "prediction_source": "ml_model" if ml_result.get("ml_available") else "heuristic_only",
        "raw_stats": {
            "edge_density": round(edge_density, 5),
            "local_variance": round(variance, 3),
            "laplacian_variance": round(laplacian_var, 3),
            "directional_ratio": round(directional_ratio, 3),
            "fft_peak_ratio": round(peak_ratio, 3),
        },
    }
