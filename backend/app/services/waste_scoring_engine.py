"""
waste_scoring_engine.py

TASK 3 - Waste Scoring Engine

Produces:
    - Recyclability score      (0-100)
    - Reuse score               (0-100)
    - Sustainability score      (0-100)
    - Material recovery score   (0-100)
    - Circularity score         (0-100, weighted composite)
    - Category label

All inputs are expected on a 0-100 (or 0-1, auto-scaled) scale from the
upstream ML pipeline (contamination_detector.py, texture_analyzer.py, etc.)
so this engine stays purely mathematical / deterministic and easy to unit
test.
"""

from typing import Dict, Any

from app.utils.sustainability_config import (
    CIRCULARITY_WEIGHTS,
    CIRCULARITY_CATEGORY_THRESHOLDS,
    categorize,
)


def _clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(value, hi))


def _to_100_scale(value: float) -> float:
    """Accept either a 0-1 fraction or an already-0-100 value."""
    if value is None:
        return 0.0
    return value * 100 if 0 <= value <= 1 else value


class WasteScoringEngine:

    # ------------------------------------------------------------------
    # 1. RECYCLABILITY SCORE
    # ------------------------------------------------------------------
    def calculate_recyclability_score(
        self,
        material_purity: float,
        contamination_level: float,
        damage_level: float,
    ) -> float:
        """
        material_purity:       0-100 (higher = purer / easier to recycle)
        contamination_level:   0-100 (higher = more contaminated, worse)
        damage_level:          0-100 (higher = more damaged, worse)
        """
        purity = _to_100_scale(material_purity)
        contamination = _to_100_scale(contamination_level)
        damage = _to_100_scale(damage_level)

        score = (purity * 0.5) + ((100 - contamination) * 0.3) + ((100 - damage) * 0.2)
        return round(_clamp(score), 2)

    # ------------------------------------------------------------------
    # 2. REUSE SCORE
    # ------------------------------------------------------------------
    def calculate_reuse_score(
        self,
        fabric_condition: float,
        durability: float,
        usability: float,
    ) -> float:
        condition = _to_100_scale(fabric_condition)
        durability = _to_100_scale(durability)
        usability = _to_100_scale(usability)

        score = (condition * 0.4) + (durability * 0.3) + (usability * 0.3)
        return round(_clamp(score), 2)

    # ------------------------------------------------------------------
    # 3. SUSTAINABILITY SCORE
    # ------------------------------------------------------------------
    def calculate_sustainability_score(
        self,
        environmental_benefit: float,
        recoverability: float,
        recycling_efficiency: float,
    ) -> float:
        benefit = _to_100_scale(environmental_benefit)
        recoverability = _to_100_scale(recoverability)
        efficiency = _to_100_scale(recycling_efficiency)

        score = (benefit * 0.4) + (recoverability * 0.3) + (efficiency * 0.3)
        return round(_clamp(score), 2)

    # ------------------------------------------------------------------
    # 4. MATERIAL RECOVERY SCORE
    # ------------------------------------------------------------------
    def calculate_material_recovery_score(
        self,
        fiber_recovery: float,
        fabric_quality: float,
        resource_value: float,
    ) -> float:
        fiber = _to_100_scale(fiber_recovery)
        quality = _to_100_scale(fabric_quality)
        value = _to_100_scale(resource_value)

        score = (fiber * 0.4) + (quality * 0.35) + (value * 0.25)
        return round(_clamp(score), 2)

    # ------------------------------------------------------------------
    # 5. CIRCULARITY SCORE (weighted composite, out of 100)
    # ------------------------------------------------------------------
    def calculate_circularity_score(
        self,
        recyclability: float,
        material_condition: float,
        reuse_potential: float,
        environmental_benefit: float,
        processing_feasibility: float,
    ) -> float:
        w = CIRCULARITY_WEIGHTS
        score = (
            _to_100_scale(recyclability) * w["recyclability"]
            + _to_100_scale(material_condition) * w["condition"]
            + _to_100_scale(reuse_potential) * w["reuse_potential"]
            + _to_100_scale(environmental_benefit) * w["environmental_benefit"]
            + _to_100_scale(processing_feasibility) * w["processing_feasibility"]
        )
        return round(_clamp(score), 2)

    # ------------------------------------------------------------------
    # FULL SCORE BUNDLE
    # ------------------------------------------------------------------
    def generate_full_scores(self, inputs: Dict[str, float]) -> Dict[str, Any]:
        """
        inputs expects the following keys (0-100 or 0-1 scale, all optional
        -- missing keys default to 50 / neutral):

            material_purity, contamination_level, damage_level,
            fabric_condition, durability, usability,
            environmental_benefit, recoverability, recycling_efficiency,
            fiber_recovery, fabric_quality, resource_value,
            processing_feasibility
        """
        g = lambda k, default=50.0: inputs.get(k, default)

        recyclability = self.calculate_recyclability_score(
            g("material_purity"), g("contamination_level"), g("damage_level")
        )
        reuse = self.calculate_reuse_score(
            g("fabric_condition"), g("durability"), g("usability")
        )
        sustainability = self.calculate_sustainability_score(
            g("environmental_benefit"), g("recoverability"), g("recycling_efficiency")
        )
        recovery = self.calculate_material_recovery_score(
            g("fiber_recovery"), g("fabric_quality"), g("resource_value")
        )
        circularity = self.calculate_circularity_score(
            recyclability=recyclability,
            material_condition=g("fabric_condition"),
            reuse_potential=reuse,
            environmental_benefit=g("environmental_benefit"),
            processing_feasibility=g("processing_feasibility"),
        )

        category = categorize(circularity, CIRCULARITY_CATEGORY_THRESHOLDS)

        return {
            "scores": {
                "recyclability": recyclability,
                "reuse": reuse,
                "sustainability": sustainability,
                "recovery": recovery,
                "circularity": circularity,
                "category": category,
            }
        }


waste_scoring_engine = WasteScoringEngine()
