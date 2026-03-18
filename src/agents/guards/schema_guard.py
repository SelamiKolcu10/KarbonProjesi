"""
Data Quality & Schema Guard Agent

Business-logic validation layer that runs before AuditorEngine and
ChiefConsultantAgent. This guard complements Pydantic type validation
with domain-specific data quality checks.
"""

from __future__ import annotations

from typing import List, Tuple

from src.agents.auditor.models import InputPayload


class DataQualityException(Exception):
    """Raised when payload fails business-logic validation."""


class DataQualityGuard:
    """
    Customs-check style business validation for incoming payloads.

    Returns:
        Tuple[bool, List[str]]:
            - bool: True if payload passed all business checks
            - List[str]: Validation error messages
    """

    def validate_business_logic(self, payload: InputPayload) -> Tuple[bool, List[str]]:
        """Validate payload against domain business rules."""
        errors: List[str] = []

        production_tons = payload.production_quantity_tons
        electricity_mwh = payload.electricity_consumption_mwh
        natural_gas_m3 = payload.natural_gas_consumption_m3 or 0.0
        allocation_rate = payload.cbam_allocation_rate

        # Rule 1: Zero production anomaly with meaningful energy usage.
        if production_tons == 0 and (electricity_mwh > 10 or natural_gas_m3 > 100):
            errors.append(
                "Critical Anomaly: Energy consumption detected while production is zero."
            )

        # Rule 2: Extreme energy intensity per ton.
        if production_tons > 0:
            intensity = electricity_mwh / production_tons
            if intensity > 5.0:
                errors.append(
                    "Data Quality Error: Energy intensity per ton is physically improbable. Check your units."
                )

        # Rule 3: Missing core energy data.
        if electricity_mwh == 0 and natural_gas_m3 == 0:
            errors.append("Insufficient Data: A factory must consume at least some energy.")

        # Rule 4: Allocation sanity check.
        if not (0.01 < allocation_rate < 1.0):
            errors.append(
                "Data Quality Error: cbam_allocation_rate must be strictly between 0.01 and 1.0."
            )

        return (len(errors) == 0, errors)
