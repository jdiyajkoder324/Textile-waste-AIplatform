"""
environmental_impact_engine.py

TASK 2 - Environmental Impact Assessment Engine

    1. CO2 savings estimation
    2. Water savings estimation
    3. Landfill reduction analysis
    4. Resource conservation estimation
    5. Sustainability reporting (final JSON report)
"""

from typing import Dict, Any

from app.utils.sustainability_config import (
    CO2_PRODUCTION_FACTOR,
    WATER_FACTOR,
    ENERGY_RECOVERY_FACTOR,
    LANDFILL_DECOMPOSITION_YEARS,
    SUSTAINABILITY_RATING_THRESHOLDS,
    get_factor,
    categorize,
)


class EnvironmentalImpactEngine:

    # ------------------------------------------------------------------
    # 1. CO2 SAVINGS ESTIMATION
    #    CO2 Saved = Weight(kg) x Material Factor
    # ------------------------------------------------------------------
    def estimate_co2_savings(self, weight_kg: float, material_type: str) -> float:
        factor = get_factor(CO2_PRODUCTION_FACTOR, material_type)
        return round(weight_kg * factor, 3)

    # ------------------------------------------------------------------
    # 2. WATER SAVINGS ESTIMATION
    #    Water Saved = Weight x Water Factor
    # ------------------------------------------------------------------
    def estimate_water_savings(self, weight_kg: float, material_type: str) -> float:
        factor = get_factor(WATER_FACTOR, material_type)
        return round(weight_kg * factor, 2)

    # ------------------------------------------------------------------
    # 3. LANDFILL REDUCTION ANALYSIS
    # ------------------------------------------------------------------
    def analyze_landfill_reduction(
        self,
        weight_kg: float,
        material_type: str,
        total_facility_landfill_kg: float = 0.0,
    ) -> Dict[str, Any]:
        landfill_saved_kg = round(weight_kg, 3)

        percentage_reduction = 0.0
        if total_facility_landfill_kg > 0:
            percentage_reduction = round(
                min(landfill_saved_kg / total_facility_landfill_kg, 1.0) * 100, 2
            )

        decomposition_years = get_factor(
            {k: float(v) for k, v in LANDFILL_DECOMPOSITION_YEARS.items()}, material_type
        )

        return {
            "landfill_saved_kg": landfill_saved_kg,
            "percentage_reduction": percentage_reduction,
            "disposal_reduction": landfill_saved_kg,
            "avoided_decomposition_years": decomposition_years,
        }

    # ------------------------------------------------------------------
    # 4. RESOURCE CONSERVATION ESTIMATION
    # ------------------------------------------------------------------
    def estimate_resource_conservation(
        self, weight_kg: float, material_type: str
    ) -> Dict[str, Any]:
        energy_factor = get_factor(ENERGY_RECOVERY_FACTOR, material_type)
        water_factor = get_factor(WATER_FACTOR, material_type)
        carbon_factor = get_factor(CO2_PRODUCTION_FACTOR, material_type)

        energy_saved = round(weight_kg * energy_factor, 3)
        material_conserved = round(weight_kg, 3)
        water_conserved = round(weight_kg * water_factor, 2)
        carbon_conserved = round(weight_kg * carbon_factor, 3)

        return {
            "energy_saved": energy_saved,
            "material_conserved": material_conserved,
            "water_conserved": water_conserved,
            "carbon_conserved": carbon_conserved,
        }

    # ------------------------------------------------------------------
    # 5. SUSTAINABILITY REPORTING
    # ------------------------------------------------------------------
    def generate_environmental_report(
        self,
        weight_kg: float,
        material_type: str,
        total_facility_landfill_kg: float = 0.0,
    ) -> Dict[str, Any]:
        co2_saved = self.estimate_co2_savings(weight_kg, material_type)
        water_saved = self.estimate_water_savings(weight_kg, material_type)
        landfill = self.analyze_landfill_reduction(weight_kg, material_type, total_facility_landfill_kg)
        conservation = self.estimate_resource_conservation(weight_kg, material_type)

        # Blend CO2 + water + landfill into a single 0-100 style index for
        # rating purposes. Uses per-kg factor magnitude normalised against
        # the max factor seen in config, so it stays 0-100 regardless of
        # material.
        max_co2_factor = max(CO2_PRODUCTION_FACTOR.values())
        max_water_factor = max(WATER_FACTOR.values())

        co2_component = (get_factor(CO2_PRODUCTION_FACTOR, material_type) / max_co2_factor) * 100
        water_component = (get_factor(WATER_FACTOR, material_type) / max_water_factor) * 100

        index = round((co2_component * 0.5) + (water_component * 0.5), 2)
        rating = categorize(index, SUSTAINABILITY_RATING_THRESHOLDS)

        recommendation = (
            "High-impact material — prioritise recycling over disposal."
            if index >= 65
            else "Consider blended recovery strategies (mechanical + chemical recycling)."
        )

        return {
            "environmental_report": {
                "co2_saved": co2_saved,
                "water_saved": water_saved,
                "landfill_saved": landfill["landfill_saved_kg"],
                "energy_saved": conservation["energy_saved"],
                "rating": rating,
                "recommendation": recommendation,
                "details": {
                    "landfill_analysis": landfill,
                    "resource_conservation": conservation,
                },
            }
        }


environmental_impact_engine = EnvironmentalImpactEngine()
