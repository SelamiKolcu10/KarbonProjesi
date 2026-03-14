"""
Constants & Knowledge Base - Emission Factors and ETS Pricing

Source: 
- Regulation (EU) 2023/956 (CBAM Regulation)
- Regulation (EU) 2023/1773 (CBAM Implementing Regulation)
- IPCC Guidelines for National Greenhouse Gas Inventories
- Turkish Electricity Transmission Corporation (TEİAŞ) 2024 Data
"""

from typing import Dict, Any, Optional

# ============================================================================
# EMISSION FACTORS (tCO2e per unit)
# ============================================================================

# Natural Gas Combustion
# Source: IPCC (2006) - Table 1.2
NATURAL_GAS_CALORIFIC_VALUE = 0.0378  # GJ per m³ (approx for Turkish Natural Gas)
NATURAL_GAS_EMISSION_FACTOR = 0.0561  # tCO2 per GJ
NATURAL_GAS_TOTAL_FACTOR = NATURAL_GAS_CALORIFIC_VALUE * NATURAL_GAS_EMISSION_FACTOR  # tCO2 per m³

# Coal Combustion (for industry)
# Source: IPCC (2006)
COAL_EMISSION_FACTOR = 94.6  # tCO2 per TJ (94,600 kg CO2/TJ)
COAL_CALORIFIC_VALUE = 0.0256  # TJ per ton (approx)

# Electricity Grid Emission Factor
# Default: Turkey grid mix (2024 average)
# Source: TEİAŞ + IEA Turkey 2024 Report
GRID_EMISSION_FACTOR_TURKEY = 0.43  # tCO2e per MWh
GRID_EMISSION_FACTOR_EU_AVG = 0.275  # tCO2e per MWh (for comparison)

# ============================================================================
# PROCESS EMISSIONS FACTORS (v2.0)
# ============================================================================

# Stoichiometric Carbon to CO2 Conversion
# Chemistry: C + O2 → CO2 (Molecular weight ratio: 44/12 = 3.664)
STOICHIOMETRIC_C_TO_CO2 = 3.664  # Conversion factor for Carbon to CO2

# Electrode Consumption (Graphite electrodes in EAF)
# Source: CBAM Guidance Document - Annex I (Iron & Steel)
ELECTRODE_CO2_FACTOR = 3.664  # tCO2 per ton of graphite electrode

# Limestone Calcination (CaCO3 → CaO + CO2)
# Source: IPCC (2006) - Volume 3, Chapter 2.3
# Chemistry: CaCO3 releases CO2 when heated (flux material in steelmaking)
LIMESTONE_EF = 0.44  # Emission factor for Limestone calcination
LIMESTONE_CO2_FACTOR = 0.44  # tCO2 per ton of limestone

# ============================================================================
# DEFAULT PRECURSOR EMISSION FACTORS (v2.0)
# ============================================================================

# Default embedded emissions for common steel precursors/alloys
# Source: CBAM Default Values - Annex II, Table 1
# Note: These are fallback values. Actual supplier-specific values are preferred.
DEFAULT_PRECURSOR_FACTORS = {
    "ferro-manganese": 1.65,      # tCO2e per ton
    "ferro-silicon": 2.10,        # tCO2e per ton
    "ferro-chromium": 2.85,       # tCO2e per ton
    "ferro-nickel": 3.20,         # tCO2e per ton
    "silicon-manganese": 1.95,    # tCO2e per ton
    "scrap-steel": 0.35,          # tCO2e per ton (low due to recycling)
    "pig-iron": 2.30,             # tCO2e per ton
    "dri": 1.80,                  # tCO2e per ton (Direct Reduced Iron)
    "hbi": 1.85,                  # tCO2e per ton (Hot Briquetted Iron)
    "lime": 0.75,                 # tCO2e per ton
}

# ============================================================================
# STEEL INDUSTRY PHYSICS BENCHMARKS
# ============================================================================

# Minimum energy requirement for steel production
# Source: International Energy Agency - "Energy Technology Perspectives 2020"
STEEL_MIN_ENERGY_PER_TON = 0.2  # MWh/ton (200 kWh/ton minimum for Electric Arc Furnace)
STEEL_TYPICAL_ENERGY_PER_TON = 0.4  # MWh/ton (400 kWh/ton typical)
STEEL_MAX_ENERGY_PER_TON = 0.7  # MWh/ton (700 kWh/ton for inefficient plants)

# ============================================================================
# EU ETS PRICING
# ============================================================================

# Current EU ETS Carbon Price (as of March 2026)
# Source: European Energy Exchange (EEX) Spot Market
ETS_PRICE_PER_TON_CO2 = 85.00  # EUR per tCO2e

# Historical range for reference
ETS_PRICE_MIN_2024 = 65.00  # EUR
ETS_PRICE_MAX_2024 = 95.00  # EUR
ETS_PRICE_FORECAST_2030 = 120.00  # EUR (estimated)

# ============================================================================
# CBAM CARBON PRICE (Phase-in period)
# ============================================================================

# CBAM will use ETS price as reference
# Phase-in: 2026-2034 (gradual increase from 0% to 100% of free allocation phase-out)
CBAM_PHASE_2026 = 0.025  # 2.5% of full carbon price (transitional)
CBAM_PHASE_2027 = 0.05   # 5%
CBAM_PHASE_2030 = 0.80   # 80%
CBAM_PHASE_2034 = 1.00   # 100% (full implementation)

# ============================================================================
# FREE ALLOCATION ASSUMPTIONS
# ============================================================================

# Default: 0 for worst-case scenario (MVP)
# In reality, some installations get free allowances
FREE_ALLOCATION_DEFAULT = 0.0  # tCO2e

# Typical free allocation rates (for reference only)
FREE_ALLOCATION_BENCHMARK_STEEL = 1.328  # tCO2/ton crude steel (EU Benchmark)

# ============================================================================
# ANOMALY DETECTION THRESHOLDS
# ============================================================================

ANOMALY_THRESHOLDS = {
    # Energy intensity (MWh per ton)
    'energy_intensity_min': STEEL_MIN_ENERGY_PER_TON,
    'energy_intensity_max': STEEL_MAX_ENERGY_PER_TON,
    
    # Production vs Energy mismatch
    'zero_production_energy_threshold': 10.0,  # MWh (if production=0 but energy>10, flag it)
    
    # Emission intensity (tCO2 per ton steel)
    'emission_intensity_min': 0.1,  # Extremely efficient (unlikely)
    'emission_intensity_max': 2.5,  # Very inefficient (coal-heavy)
    
    # Financial liability (EUR per ton)
    'liability_per_ton_max': 250.0,  # EUR (sanity check)
}

# ============================================================================
# REGULATORY REFERENCES
# ============================================================================

LEGAL_REFERENCES = {
    'cbam_regulation': 'Regulation (EU) 2023/956 - CBAM Framework',
    'cbam_implementing': 'Regulation (EU) 2023/1773 - CBAM Implementation',
    'ets_directive': 'Directive 2003/87/EC - EU ETS',
    'ipcc_guidelines': 'IPCC (2006) Guidelines for National GHG Inventories',
    'steel_benchmark': 'Commission Decision 2011/278/EU - Benchmarks for Free Allocation'
}

# ============================================================================
# CONFIGURATION HELPERS
# ============================================================================

def get_emission_factors(overrides: Optional[Dict[str, Any]] = None) -> Dict[str, float]:
    """
    Get emission factors with optional overrides for simulation.
    
    Args:
        overrides: Dictionary with custom values (e.g., {"grid_factor": 0.0})
        
    Returns:
        Dictionary of emission factors
    """
    factors = {
        'natural_gas': NATURAL_GAS_TOTAL_FACTOR,
        'coal': COAL_EMISSION_FACTOR * COAL_CALORIFIC_VALUE,
        'grid_electricity': GRID_EMISSION_FACTOR_TURKEY,
        'electrode': ELECTRODE_CO2_FACTOR,
        'limestone': LIMESTONE_CO2_FACTOR,
    }
    
    if overrides:
        if 'grid_factor' in overrides:
            factors['grid_electricity'] = overrides['grid_factor']
        if 'natural_gas_factor' in overrides:
            factors['natural_gas'] = overrides['natural_gas_factor']
        if 'coal_factor' in overrides:
            factors['coal'] = overrides['coal_factor']
        if 'electrode_factor' in overrides:
            factors['electrode'] = overrides['electrode_factor']
        if 'limestone_factor' in overrides:
            factors['limestone'] = overrides['limestone_factor']
    
    return factors


def get_ets_price(year: int = 2026) -> float:
    """
    Get estimated ETS price for a given year.
    
    Args:
        year: Target year
        
    Returns:
        ETS price in EUR per tCO2e
    """
    if year <= 2024:
        return (ETS_PRICE_MIN_2024 + ETS_PRICE_MAX_2024) / 2
    elif year <= 2026:
        return ETS_PRICE_PER_TON_CO2
    elif year >= 2030:
        return ETS_PRICE_FORECAST_2030
    else:
        # Linear interpolation
        slope = (ETS_PRICE_FORECAST_2030 - ETS_PRICE_PER_TON_CO2) / (2030 - 2026)
        return ETS_PRICE_PER_TON_CO2 + slope * (year - 2026)


def get_precursor_emission_factor(material_name: str, custom_factor: Optional[float] = None) -> tuple[float, bool]:
    """
    Get emission factor for a precursor material.
    
    Args:
        material_name: Name of the precursor material (case-insensitive)
        custom_factor: Optional custom/supplier-specific factor
        
    Returns:
        Tuple of (emission_factor, is_default)
        - emission_factor: tCO2e per ton
        - is_default: True if using default CBAM value, False if using actual/custom value
    """
    # If custom factor provided, use it (preferred - actual data)
    if custom_factor is not None and custom_factor >= 0:
        return (custom_factor, False)
    
    # Otherwise, lookup in default table
    material_key = material_name.lower().strip().replace(" ", "-")
    
    if material_key in DEFAULT_PRECURSOR_FACTORS:
        return (DEFAULT_PRECURSOR_FACTORS[material_key], True)
    
    # If not found, use a conservative estimate (average of all defaults)
    avg_factor = sum(DEFAULT_PRECURSOR_FACTORS.values()) / len(DEFAULT_PRECURSOR_FACTORS)
    return (avg_factor, True)
