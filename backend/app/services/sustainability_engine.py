"""
sustainability_engine.py

TASK 1 - Sustainability Intelligence Engine

Produces:
    - Carbon footprint estimation
    - Waste diversion analysis
    - Circular economy analysis
    - Resource recovery estimation
    - Sustainability benchmarking (rating + index + recommendations)

All numbers come from app.utils.sustainability_config so they can be tuned
without touching this file.
"""

from typing import Dict, Any

from app.utils.sustainability_config import (
    CO2_PRODUCTION_FACTOR,
    CO2_RECYCLING_SAVINGS_RATIO,
    CO2_TRANSPORT_FACTOR_PER_KG,
    CO2_PROCESSING_FACTOR_PER_KG,
    ENERGY_RECOVERY_FACTOR,
    RECOVERED_MATERIAL_VALUE_PER_KG,
    SUSTAINABILITY_RATING_THRESHOLDS,
    get_factor,
    categorize,
)


class SustainabilityEngine:
    """
    Stateless calculation engine. One instance can be safely reused across
    requests (no mutable state), but a fresh instance per call is cheap too.
    """

    # ------------------------------------------------------------------
    # 1. CARBON FOOTPRINT ESTIMATION
    # ------------------------------------------------------------------
    def calculate_carbon_footprint(
        self,
        weight_kg: float,
        material_type: str,
        is_recycled: bool = True,
        distance_km: float = 0.0,
    ) -> Dict[str, Any]:
        production_factor = get_factor(CO2_PRODUCTION_FACTOR, material_type)

        # Emissions that WOULD have been generated producing this item
        # from virgin material.
        current_emission = round(weight_kg * production_factor, 3)

        # Transportation & processing add-ons (always incurred).
        transport_emission = round(weight_kg * CO2_TRANSPORT_FACTOR_PER_KG
                                    * (1 + distance_km / 1000.0), 3)
        processing_emission = round(weight_kg * CO2_PROCESSING_FACTOR_PER_KG, 3)

        total_emission = round(current_emission + transport_emission + processing_emission, 3)

        # Savings only apply if the batch is actually being recycled/reused
        # instead of land-filled + replaced by new virgin material.
        recycling_savings = round(current_emission * CO2_RECYCLING_SAVINGS_RATIO, 3) if is_recycled else 0.0
        net_savings = round(recycling_savings - processing_emission, 3) if is_recycled else 0.0

        rating = categorize(
            (recycling_savings / current_emission * 100) if current_emission > 0 else 0,
            SUSTAINABILITY_RATING_THRESHOLDS,
        )

        return {
            "carbon_footprint": {
                "current_emission": total_emission,
                "recycling_savings": recycling_savings,
                "net_savings": net_savings,
                "transport_emission": transport_emission,
                "processing_emission": processing_emission,
                "rating": rating,
            }
        }

    # ------------------------------------------------------------------
    # 2. WASTE DIVERSION ANALYSIS
    # ------------------------------------------------------------------
    def calculate_waste_diversion(
        self,
        total_weight_kg: float,
        recycled_kg: float = 0.0,
        reused_kg: float = 0.0,
        recovered_kg: float = 0.0,
        landfilled_kg: float = 0.0,
    ) -> Dict[str, Any]:
        if total_weight_kg <= 0:
            return {
                "waste_diversion": {
                    "diverted_percentage": 0.0,
                    "recycled_percentage": 0.0,
                    "reuse_percentage": 0.0,
                    "recovery_percentage": 0.0,
                }
            }

        diverted_kg = recycled_kg + reused_kg + recovered_kg
        diverted_percentage = round(min(diverted_kg / total_weight_kg, 1.0) * 100, 2)
        recycled_percentage = round(min(recycled_kg / total_weight_kg, 1.0) * 100, 2)
        reuse_percentage = round(min(reused_kg / total_weight_kg, 1.0) * 100, 2)
        recovery_percentage = round(min(recovered_kg / total_weight_kg, 1.0) * 100, 2)

        return {
            "waste_diversion": {
                "diverted_percentage": diverted_percentage,
                "recycled_percentage": recycled_percentage,
                "reuse_percentage": reuse_percentage,
                "recovery_percentage": recovery_percentage,
            }
        }

    # ------------------------------------------------------------------
    # 3. CIRCULAR ECONOMY ANALYSIS
    # ------------------------------------------------------------------
    def calculate_circular_economy(
        self,
        recyclability_score: float,
        material_condition_score: float,
        reuse_potential_score: float,
        processing_feasibility_score: float,
    ) -> Dict[str, Any]:
        """
        All *_score arguments are expected on a 0-100 scale. This produces a
        higher level "circular economy score" distinct from (but related
        to) the detailed Circularity Score computed in the Waste Scoring
        Engine -- this one is meant for dashboard-level trend reporting.
        """
        utilization = round((material_condition_score + reuse_potential_score) / 2, 2)
        optimization = round((recyclability_score + processing_feasibility_score) / 2, 2)
        score = round((utilization * 0.5) + (optimization * 0.5), 2)

        category = categorize(score, [
            (85, "Highly Circular"),
            (65, "Circular"),
            (40, "Transitioning"),
            (0, "Linear"),
        ])

        return {
            "circular_economy": {
                "score": score,
                "utilization": utilization,
                "optimization": optimization,
                "category": category,
            }
        }

    # ------------------------------------------------------------------
    # 4. RESOURCE RECOVERY ESTIMATION
    # ------------------------------------------------------------------
    def calculate_resource_recovery(
        self,
        weight_kg: float,
        material_type: str,
        recovery_efficiency: float = 0.8,
    ) -> Dict[str, Any]:
        """
        recovery_efficiency: fraction (0-1) representing how much of the
        theoretical recoverable material is actually recoverable given
        contamination / damage — typically fed from the Waste Scoring
        Engine's recyclability score / 100.
        """
        recovery_efficiency = max(0.0, min(recovery_efficiency, 1.0))

        recoverable_material = round(weight_kg * recovery_efficiency, 3)

        value_per_kg = get_factor(RECOVERED_MATERIAL_VALUE_PER_KG, material_type)
        estimated_value = round(recoverable_material * value_per_kg, 2)

        energy_factor = get_factor(ENERGY_RECOVERY_FACTOR, material_type)
        energy_recovery = round(recoverable_material * energy_factor, 3)

        resource_efficiency = round(recovery_efficiency * 100, 2)

        return {
            "resource_recovery": {
                "recoverable_material": recoverable_material,
                "estimated_value": estimated_value,
                "energy_recovery": energy_recovery,
                "resource_efficiency": resource_efficiency,
            }
        }

    # ------------------------------------------------------------------
    # 5. SUSTAINABILITY BENCHMARKING
    # ------------------------------------------------------------------
    def benchmark_sustainability(
        self,
        carbon_footprint: Dict[str, Any],
        waste_diversion: Dict[str, Any],
        circular_economy: Dict[str, Any],
        resource_recovery: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Combines outputs from the other four calculators into one overall
        sustainability index (0-100) and produces plain-language
        recommendations.
        """
        cf = carbon_footprint["carbon_footprint"]
        wd = waste_diversion["waste_diversion"]
        ce = circular_economy["circular_economy"]
        rr = resource_recovery["resource_recovery"]

        # Normalise net carbon savings into a 0-100 component (relative to
        # current_emission, guarding against div-by-zero).
        current_emission = cf["current_emission"] or 1
        carbon_component = max(0.0, min((cf["net_savings"] / current_emission) * 100, 100))

        diversion_component = wd["diverted_percentage"]
        circularity_component = ce["score"]
        recovery_component = rr["resource_efficiency"]

        sustainability_index = round(
            (carbon_component * 0.25)
            + (diversion_component * 0.25)
            + (circularity_component * 0.30)
            + (recovery_component * 0.20),
            2,
        )

        rating = categorize(sustainability_index, SUSTAINABILITY_RATING_THRESHOLDS)

        recommendations = []
        if carbon_component < 40:
            recommendations.append("Increase recycled-content sourcing to cut net carbon emissions.")
        if diversion_component < 50:
            recommendations.append("Improve sorting workflows to raise landfill diversion rate.")
        if circularity_component < 60:
            recommendations.append("Prioritise material separation to unlock higher circularity.")
        if recovery_component < 60:
            recommendations.append("Reduce contamination at intake to improve resource recovery yield.")
        if not recommendations:
            recommendations.append("Maintain current sustainability practices — performance is strong.")

        return {
            "sustainability_index": sustainability_index,
            "rating": rating,
            "recommendations": recommendations,
        }


sustainability_engine = SustainabilityEngine()
