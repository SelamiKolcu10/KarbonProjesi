"""
Physics-Based Validation & Anomaly Detection Engine

This module performs sanity checks based on industrial physics principles
to detect data anomalies, impossible scenarios, and suspicious patterns.
"""

from typing import List, Tuple, Optional
from .models import AnomalyFlag, AnomalyLevel
from .constants import (
    STEEL_MIN_ENERGY_PER_TON,
    STEEL_MAX_ENERGY_PER_TON,
    ANOMALY_THRESHOLDS
)


class PhysicsValidator:
    """
    Physics-based validation engine for steel production data.
    
    Based on thermodynamic principles and industrial benchmarks from:
    - International Energy Agency (IEA)
    - World Steel Association (worldsteel)
    - IPCC Guidelines
    """
    
    def __init__(self, strict_mode: bool = False):
        """
        Args:
            strict_mode: If True, raises exceptions on CRITICAL anomalies.
                        If False, only flags them.
        """
        self.strict_mode = strict_mode
        self.anomalies: List[AnomalyFlag] = []
    
    def validate_all(
        self,
        production_tons: float,
        electricity_mwh: float,
        natural_gas_m3: float = 0.0,
        coal_tons: float = 0.0
    ) -> List[AnomalyFlag]:
        """
        Run all validation checks.
        
        Args:
            production_tons: Steel production quantity
            electricity_mwh: Electricity consumption
            natural_gas_m3: Natural gas consumption
            coal_tons: Coal consumption
            
        Returns:
            List of detected anomalies
        """
        self.anomalies = []
        
        # Check 1: Energy intensity
        self._check_energy_intensity(production_tons, electricity_mwh)
        
        # Check 2: Zero production trap
        self._check_zero_production_trap(production_tons, electricity_mwh)
        
        # Check 3: Negative values
        self._check_negative_values(production_tons, electricity_mwh, natural_gas_m3, coal_tons)
        
        # Check 4: Unrealistic consumption patterns
        self._check_consumption_patterns(production_tons, electricity_mwh, natural_gas_m3)
        
        return self.anomalies
    
    def _check_energy_intensity(
        self, 
        production_tons: float, 
        electricity_mwh: float
    ) -> None:
        """
        Check if energy consumption is physically plausible.
        
        Physics Rule: Electric Arc Furnace requires minimum 200 kWh/ton (0.2 MWh/ton)
        Source: IEA - Energy Technology Perspectives 2020
        """
        if production_tons == 0:
            return  # Will be caught by zero production check
        
        energy_intensity = electricity_mwh / production_tons
        
        # CRITICAL: Below physical minimum
        if energy_intensity < STEEL_MIN_ENERGY_PER_TON:
            self.anomalies.append(AnomalyFlag(
                level=AnomalyLevel.CRITICAL,
                code="PHYSICS_VIOLATION_MIN_ENERGY",
                message=(
                    f"Energy intensity ({energy_intensity:.3f} MWh/ton) is below physical minimum "
                    f"for steel production ({STEEL_MIN_ENERGY_PER_TON} MWh/ton). "
                    "This violates thermodynamic principles for Electric Arc Furnace."
                ),
                detected_value=energy_intensity,
                expected_range=f">= {STEEL_MIN_ENERGY_PER_TON} MWh/ton"
            ))
        
        # WARNING: Above typical maximum
        elif energy_intensity > STEEL_MAX_ENERGY_PER_TON:
            self.anomalies.append(AnomalyFlag(
                level=AnomalyLevel.WARNING,
                code="HIGH_ENERGY_INTENSITY",
                message=(
                    f"Energy intensity ({energy_intensity:.3f} MWh/ton) is above typical maximum "
                    f"({STEEL_MAX_ENERGY_PER_TON} MWh/ton). Plant may be inefficient or data error."
                ),
                detected_value=energy_intensity,
                expected_range=f"0.2 - {STEEL_MAX_ENERGY_PER_TON} MWh/ton"
            ))
    
    def _check_zero_production_trap(
        self,
        production_tons: float,
        electricity_mwh: float
    ) -> None:
        """
        Detect scenarios where energy is consumed but no production occurred.
        This could indicate:
        - Maintenance mode
        - Idle furnace
        - Data collection error
        """
        threshold = ANOMALY_THRESHOLDS['zero_production_energy_threshold']
        
        if production_tons == 0 and electricity_mwh > threshold:
            self.anomalies.append(AnomalyFlag(
                level=AnomalyLevel.WARNING,
                code="ZERO_PRODUCTION_WITH_ENERGY",
                message=(
                    f"No production reported ({production_tons} tons) but significant energy "
                    f"consumption detected ({electricity_mwh:.1f} MWh). "
                    "This may indicate maintenance/idle mode or data error."
                ),
                detected_value=electricity_mwh,
                expected_range="Energy should be near zero if production is zero"
            ))
        
        elif production_tons > 0 and electricity_mwh == 0:
            self.anomalies.append(AnomalyFlag(
                level=AnomalyLevel.CRITICAL,
                code="PRODUCTION_WITHOUT_ENERGY",
                message=(
                    f"Production reported ({production_tons} tons) but zero energy consumption. "
                    "This is physically impossible."
                ),
                detected_value=0.0,
                expected_range=f">= {production_tons * STEEL_MIN_ENERGY_PER_TON:.1f} MWh"
            ))
    
    def _check_negative_values(
        self,
        production_tons: float,
        electricity_mwh: float,
        natural_gas_m3: float,
        coal_tons: float
    ) -> None:
        """Check for negative values (data quality issue)"""
        
        if production_tons < 0:
            self.anomalies.append(AnomalyFlag(
                level=AnomalyLevel.CRITICAL,
                code="NEGATIVE_PRODUCTION",
                message="Production quantity is negative. Data error.",
                detected_value=production_tons,
                expected_range=">= 0"
            ))
        
        if electricity_mwh < 0:
            self.anomalies.append(AnomalyFlag(
                level=AnomalyLevel.CRITICAL,
                code="NEGATIVE_ELECTRICITY",
                message="Electricity consumption is negative. Data error.",
                detected_value=electricity_mwh,
                expected_range=">= 0"
            ))
        
        if natural_gas_m3 < 0:
            self.anomalies.append(AnomalyFlag(
                level=AnomalyLevel.CRITICAL,
                code="NEGATIVE_GAS",
                message="Natural gas consumption is negative. Data error.",
                detected_value=natural_gas_m3,
                expected_range=">= 0"
            ))
        
        if coal_tons < 0:
            self.anomalies.append(AnomalyFlag(
                level=AnomalyLevel.CRITICAL,
                code="NEGATIVE_COAL",
                message="Coal consumption is negative. Data error.",
                detected_value=coal_tons,
                expected_range=">= 0"
            ))
    
    def _check_consumption_patterns(
        self,
        production_tons: float,
        electricity_mwh: float,
        natural_gas_m3: float
    ) -> None:
        """
        Check for unrealistic consumption patterns.
        
        Example: Very high natural gas consumption relative to production
        may indicate heating/auxiliary uses beyond production.
        """
        if production_tons == 0:
            return
        
        # Natural gas check (if used)
        if natural_gas_m3 > 0:
            # Typical auxiliary gas consumption: ~20-50 m³ per ton
            gas_per_ton = natural_gas_m3 / production_tons
            
            if gas_per_ton > 100:  # Unusually high
                self.anomalies.append(AnomalyFlag(
                    level=AnomalyLevel.WARNING,
                    code="HIGH_GAS_CONSUMPTION",
                    message=(
                        f"Natural gas consumption ({gas_per_ton:.1f} m³/ton) is unusually high. "
                        "Typical range is 20-50 m³/ton for auxiliary uses in EAF."
                    ),
                    detected_value=gas_per_ton,
                    expected_range="20-50 m³/ton (typical)"
                ))
    
    def get_critical_anomalies(self) -> List[AnomalyFlag]:
        """Get only CRITICAL level anomalies"""
        return [a for a in self.anomalies if a.level == AnomalyLevel.CRITICAL]
    
    def get_warnings(self) -> List[AnomalyFlag]:
        """Get only WARNING level anomalies"""
        return [a for a in self.anomalies if a.level == AnomalyLevel.WARNING]
    
    def has_critical_issues(self) -> bool:
        """Check if any CRITICAL anomalies were detected"""
        return len(self.get_critical_anomalies()) > 0


# Standalone validation function
def validate_physics(
    production_qty: float,
    energy_consumption: float
) -> Tuple[bool, Optional[str]]:
    """
    Simple standalone validation function.
    
    Args:
        production_qty: Production in tons
        energy_consumption: Energy in MWh
        
    Returns:
        (is_valid, error_message) tuple
    """
    if production_qty == 0:
        if energy_consumption > ANOMALY_THRESHOLDS['zero_production_energy_threshold']:
            return False, "Zero production but significant energy consumption detected"
        return True, None
    
    if energy_consumption == 0:
        return False, "Production reported but zero energy consumption (impossible)"
    
    energy_intensity = energy_consumption / production_qty
    
    if energy_intensity < STEEL_MIN_ENERGY_PER_TON:
        return False, (
            f"Energy intensity ({energy_intensity:.3f} MWh/ton) below physical minimum "
            f"({STEEL_MIN_ENERGY_PER_TON} MWh/ton)"
        )
    
    if energy_intensity > STEEL_MAX_ENERGY_PER_TON:
        return False, (
            f"Energy intensity ({energy_intensity:.3f} MWh/ton) above typical maximum "
            f"({STEEL_MAX_ENERGY_PER_TON} MWh/ton)"
        )
    
    return True, None
