"""
ML Inference Loader
--------------------
Lazily loads the 3 trained models (damage_cnn, pattern_texture_cnn,
waste_proxy_cnn) and exposes simple predict_*() functions.

Each function is defensive: if the .pth file is missing, or torch/timm
aren't installed, or loading fails for any reason, it returns
{"ml_available": False} instead of raising — so callers can safely check
`if result["ml_available"]:` and fall back to the existing heuristic
functions without any behavior change.

Place this file at: app/ml_models/ml_inference.py
Trained weights expected at: app/ml_models/trained/*.pth and *_labels.json
"""
import json
import os
from typing import Dict, Any

import cv2
import numpy as np

TRAINED_DIR = os.path.join(os.path.dirname(__file__), "trained")

_damage_model = None
_damage_labels = None
_texture_model = None
_texture_labels = None
_waste_model = None
_waste_labels = None

_TORCH_OK = True
try:
    import torch
    import torch.nn as nn
    import timm
    from torchvision import transforms
except ImportError:
    _TORCH_OK = False


# ---- Custom small CNN architecture (must match training script exactly) ----
if _TORCH_OK:
    class WasteProxyCNN(nn.Module):
        def __init__(self, num_classes):
            super().__init__()
            self.features = nn.Sequential(
                nn.Conv2d(1, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
                nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            )
            self.classifier = nn.Sequential(
                nn.Flatten(), nn.Linear(64 * 7 * 7, 128), nn.ReLU(),
                nn.Dropout(0.3), nn.Linear(128, num_classes)
            )

        def forward(self, x):
            return self.classifier(self.features(x))

    _EFFNET_TFM = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])


def _load_json(path):
    with open(path, "r") as f:
        return json.load(f)


def _get_damage_model():
    global _damage_model, _damage_labels
    if _damage_model is not None:
        return _damage_model, _damage_labels
    if not _TORCH_OK:
        return None, None
    pth = os.path.join(TRAINED_DIR, "damage_cnn_final.pth")
    labels_path = os.path.join(TRAINED_DIR, "damage_labels_final.json")
    if not (os.path.exists(pth) and os.path.exists(labels_path)):
        return None, None
    try:
        labels = _load_json(labels_path)
        model = timm.create_model("efficientnet_b0", pretrained=False, num_classes=len(labels))
        model.load_state_dict(torch.load(pth, map_location="cpu"))
        model.eval()
        _damage_model, _damage_labels = model, labels
        return model, labels
    except Exception:
        return None, None


def _get_texture_model():
    global _texture_model, _texture_labels
    if _texture_model is not None:
        return _texture_model, _texture_labels
    if not _TORCH_OK:
        return None, None
    pth = os.path.join(TRAINED_DIR, "pattern_texture_cnn.pth")
    labels_path = os.path.join(TRAINED_DIR, "pattern_texture_labels.json")
    if not (os.path.exists(pth) and os.path.exists(labels_path)):
        return None, None
    try:
        labels = _load_json(labels_path)
        model = timm.create_model("efficientnet_b0", pretrained=False, num_classes=len(labels))
        model.load_state_dict(torch.load(pth, map_location="cpu"))
        model.eval()
        _texture_model, _texture_labels = model, labels
        return model, labels
    except Exception:
        return None, None


def _get_waste_model():
    global _waste_model, _waste_labels
    if _waste_model is not None:
        return _waste_model, _waste_labels
    if not _TORCH_OK:
        return None, None
    pth = os.path.join(TRAINED_DIR, "waste_proxy_cnn.pth")
    labels_path = os.path.join(TRAINED_DIR, "waste_proxy_labels.json")
    if not (os.path.exists(pth) and os.path.exists(labels_path)):
        return None, None
    try:
        labels = _load_json(labels_path)
        model = WasteProxyCNN(len(labels))
        model.load_state_dict(torch.load(pth, map_location="cpu"))
        model.eval()
        _waste_model, _waste_labels = model, labels
        return model, labels
    except Exception:
        return None, None


def predict_damage_ml(image_bgr: np.ndarray) -> Dict[str, Any]:
    """Real CNN prediction: Defect / NoDefect. Trained on real fabric photos (88% acc)."""
    model, labels = _get_damage_model()
    if model is None:
        return {"ml_available": False}
    try:
        rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        tensor = _EFFNET_TFM(rgb).unsqueeze(0)
        with torch.no_grad():
            probs = torch.softmax(model(tensor), dim=1)[0]
            idx = int(torch.argmax(probs).item())
        return {
            "ml_available": True,
            "prediction": labels[idx],
            "confidence": round(float(probs[idx]) * 100, 2),
        }
    except Exception:
        return {"ml_available": False}


def predict_texture_cluster_ml(image_bgr: np.ndarray) -> Dict[str, Any]:
    """Real CNN prediction: numeric texture cluster (0-17, no human labels available)."""
    model, labels = _get_texture_model()
    if model is None:
        return {"ml_available": False}
    try:
        rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        tensor = _EFFNET_TFM(rgb).unsqueeze(0)
        with torch.no_grad():
            probs = torch.softmax(model(tensor), dim=1)[0]
            idx = int(torch.argmax(probs).item())
        return {
            "ml_available": True,
            "texture_cluster": labels[idx],
            "confidence": round(float(probs[idx]) * 100, 2),
        }
    except Exception:
        return {"ml_available": False}


def predict_waste_signal_ml(image_bgr: np.ndarray) -> Dict[str, Any]:
    """
    EXPERIMENTAL — trained on Fashion-MNIST (28x28 grayscale garment icons),
    NOT real textile-waste photos. Domain mismatch means this is a weak,
    unreliable signal on real images. Treat as experimental only; the
    heuristic classify_waste() remains the primary/trusted result.
    """
    model, labels = _get_waste_model()
    if model is None:
        return {"ml_available": False}
    try:
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, (28, 28)).astype(np.float32) / 255.0
        tensor = torch.tensor(gray).unsqueeze(0).unsqueeze(0)  # (1,1,28,28)
        with torch.no_grad():
            probs = torch.softmax(model(tensor), dim=1)[0]
            idx = int(torch.argmax(probs).item())
        return {
            "ml_available": True,
            "prediction": labels[idx],
            "confidence": round(float(probs[idx]) * 100, 2),
            "note": "experimental — trained on non-textile proxy dataset, low real-world reliability",
        }
    except Exception:
        return {"ml_available": False}
