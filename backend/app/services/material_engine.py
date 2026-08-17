from typing import Dict, Any

from app.ml_models.material_classifier import predict_material


def run_material_classification(image_analysis_output: Dict[str, Any]) -> Dict[str, Any]:
    return predict_material(
        texture_result=image_analysis_output["texture_result"],
        color_result=image_analysis_output["color_result"],
        image_bgr=image_analysis_output["image_bgr"],
    )
