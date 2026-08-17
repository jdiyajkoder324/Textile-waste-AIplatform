"""
sustainability_config.py

Central, configurable source of truth for every constant used across the
Sustainability Intelligence Engine, Environmental Impact Assessment Engine,
Waste Scoring Engine and Recommendation Engine.

Keeping every number in ONE file means Milestone 3 calculations can be tuned
(or replaced with values from a research paper / govt datasheet) without
touching any business logic.
"""

from typing import Dict


# --------------------------------------------------------------------------
# 1. CO2 EMISSION FACTORS  (kg CO2 per kg of virgin material produced)
# --------------------------------------------------------------------------
CO2_PRODUCTION_FACTOR: Dict[str, float] = {
    "cotton": 5.8,
    "polyester": 9.2,
    "denim": 7.5,
    "silk": 4.5,
    "wool": 6.3,
    "jute": 2.5,
    "nylon": 8.4,
    "linen": 3.8,
    "rayon": 4.9,
    "acrylic": 8.9,
    "mixed": 6.5,          # fallback for blended/unknown fabrics
}

# Recycling emits far less CO2 than virgin production. Expressed as a
# fraction of the production factor that is SAVED when the item is
# recycled instead of land-filled + replaced with virgin material.
CO2_RECYCLING_SAVINGS_RATIO: float = 0.65

# Extra emission introduced by transportation & processing (kg CO2/kg),
# applied on top of / independent from production emissions.
CO2_TRANSPORT_FACTOR_PER_KG: float = 0.35
CO2_PROCESSING_FACTOR_PER_KG: float = 0.20


# --------------------------------------------------------------------------
# 2. WATER FOOTPRINT FACTORS (Litres saved per kg recycled instead of
#    producing virgin material)
# --------------------------------------------------------------------------
WATER_FACTOR: Dict[str, float] = {
    "cotton": 10000.0,
    "polyester": 3500.0,
    "silk": 5500.0,
    "denim": 8000.0,
    "wool": 6000.0,
    "jute": 2500.0,
    "nylon": 4200.0,
    "linen": 6500.0,
    "rayon": 3000.0,
    "acrylic": 3200.0,
    "mixed": 5500.0,
}


# --------------------------------------------------------------------------
# 3. LANDFILL / DISPOSAL
# --------------------------------------------------------------------------
# Average number of years a synthetic / natural textile takes to decompose
# in a landfill -- used only for reporting/context, not scoring maths.
LANDFILL_DECOMPOSITION_YEARS: Dict[str, int] = {
    "cotton": 5,
    "polyester": 200,
    "denim": 10,
    "silk": 4,
    "wool": 5,
    "jute": 2,
    "nylon": 40,
    "linen": 2,
    "rayon": 6,
    "acrylic": 200,
    "mixed": 50,
}


# --------------------------------------------------------------------------
# 4. ENERGY RECOVERY (kWh saved per kg when material is recovered instead
#    of being produced from virgin resources)
# --------------------------------------------------------------------------
ENERGY_RECOVERY_FACTOR: Dict[str, float] = {
    "cotton": 3.2,
    "polyester": 5.1,
    "denim": 4.0,
    "silk": 2.8,
    "wool": 3.6,
    "jute": 1.8,
    "nylon": 4.8,
    "linen": 2.4,
    "rayon": 2.9,
    "acrylic": 4.9,
    "mixed": 3.5,
}


# --------------------------------------------------------------------------
# 5. ESTIMATED MARKET VALUE OF RECOVERED MATERIAL (currency units per kg)
#    Kept generic ("units") since currency isn't specified by the project.
# --------------------------------------------------------------------------
RECOVERED_MATERIAL_VALUE_PER_KG: Dict[str, float] = {
    "cotton": 25.0,
    "polyester": 18.0,
    "denim": 22.0,
    "silk": 60.0,
    "wool": 40.0,
    "jute": 12.0,
    "nylon": 20.0,
    "linen": 30.0,
    "rayon": 15.0,
    "acrylic": 14.0,
    "mixed": 18.0,
}


# --------------------------------------------------------------------------
# 6. WASTE SCORING WEIGHTS  (Circularity Score formula -- must total 100)
# --------------------------------------------------------------------------
CIRCULARITY_WEIGHTS: Dict[str, float] = {
    "recyclability": 0.35,
    "condition": 0.20,
    "reuse_potential": 0.20,
    "environmental_benefit": 0.15,
    "processing_feasibility": 0.10,
}

assert abs(sum(CIRCULARITY_WEIGHTS.values()) - 1.0) < 1e-6, \
    "CIRCULARITY_WEIGHTS must sum to 1.0 (100%)"


# --------------------------------------------------------------------------
# 7. CATEGORY THRESHOLDS
# --------------------------------------------------------------------------
CIRCULARITY_CATEGORY_THRESHOLDS = [
    (90, "Excellent Recovery Potential"),
    (75, "High Recovery Potential"),
    (60, "Moderate Recovery Potential"),
    (40, "Limited Recovery Potential"),
    (0, "Disposal Recommended"),
]

SUSTAINABILITY_RATING_THRESHOLDS = [
    (85, "Excellent"),
    (65, "Good"),
    (40, "Average"),
    (0, "Poor"),
]


def get_factor(table: Dict[str, float], material_type: str) -> float:
    """
    Safe lookup helper -- normalises the material name and falls back to
    the 'mixed' bucket if an unknown / blended material type is supplied.
    """
    if not material_type:
        return table.get("mixed", 0.0)
    key = material_type.strip().lower()
    return table.get(key, table.get("mixed", 0.0))


def categorize(value: float, thresholds) -> str:
    """
    Generic threshold walker. `thresholds` must be a list of
    (min_value, label) tuples sorted descending by min_value.
    """
    for min_value, label in thresholds:
        if value >= min_value:
            return label
    return thresholds[-1][1]
