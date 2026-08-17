"""
Color Analyzer
--------------
Uses OpenCV k-means clustering on pixel colors to extract the dominant
color palette of a textile image, along with basic colorfulness/brightness
metrics used elsewhere in the pipeline (e.g. sustainability & quality scoring).
"""
from typing import Dict, Any, List

import cv2
import numpy as np


def _rgb_to_hex(rgb) -> str:
    return "#{:02x}{:02x}{:02x}".format(int(rgb[0]), int(rgb[1]), int(rgb[2]))


def analyze_color(image_bgr: np.ndarray, k: int = 5) -> Dict[str, Any]:
    small = cv2.resize(image_bgr, (150, 150), interpolation=cv2.INTER_AREA)
    rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
    pixels = rgb.reshape(-1, 3).astype(np.float32)

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.5)
    k = max(1, min(k, len(np.unique(pixels.reshape(-1, 3), axis=0))))
    _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 8, cv2.KMEANS_PP_CENTERS)

    counts = np.bincount(labels.flatten(), minlength=k)
    total = counts.sum()

    order = np.argsort(-counts)
    dominant_colors: List[Dict[str, Any]] = []
    for idx in order:
        center = centers[idx]
        pct = round(float(counts[idx]) / float(total) * 100, 2)
        dominant_colors.append({
            "hex": _rgb_to_hex(center),
            "rgb": [int(c) for c in center],
            "percentage": pct,
        })

    # Colorfulness metric (Hasler & Süsstrunk approximation)
    r, g, b = rgb[:, :, 0].astype(float), rgb[:, :, 1].astype(float), rgb[:, :, 2].astype(float)
    rg = r - g
    yb = 0.5 * (r + g) - b
    colorfulness = float(np.sqrt(np.std(rg) ** 2 + np.std(yb) ** 2) +
                         0.3 * np.sqrt(np.mean(rg) ** 2 + np.mean(yb) ** 2))

    hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
    brightness = float(np.mean(hsv[:, :, 2]))
    saturation = float(np.mean(hsv[:, :, 1]))

    primary_hex = dominant_colors[0]["hex"] if dominant_colors else "#000000"

    return {
        "dominant_colors": dominant_colors,
        "primary_color": primary_hex,
        "colorfulness": round(colorfulness, 2),
        "brightness": round(brightness, 2),
        "saturation": round(saturation, 2),
    }
