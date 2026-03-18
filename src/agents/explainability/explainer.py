"""Explainability agent that reconstructs CBAM calculations into a legal audit trail."""

from __future__ import annotations

from typing import List, TYPE_CHECKING

from pydantic import BaseModel, Field

from src.agents.auditor.constants import (
    CBAM_PHASE_2026,
    COAL_CALORIFIC_VALUE,
    COAL_EMISSION_FACTOR,
    DEFAULT_PRECURSOR_FACTORS,
    ETS_PRICE_PER_TON_CO2,
    GRID_EMISSION_FACTOR_TURKEY,
    LIMESTONE_EF,
    NATURAL_GAS_TOTAL_FACTOR,
    STOICHIOMETRIC_C_TO_CO2,
)
from src.agents.auditor.models import InputPayload

if TYPE_CHECKING:
    from src.agents.strategist.chief_consultant import ExecutiveConsultingReport


class AuditStep(BaseModel):
    """Single explainable calculation step for regulator-facing audit evidence."""

    step_name: str = Field(..., description="Readable name of the calculation step")
    formula_applied: str = Field(..., description="Rendered formula with real input values")
    result_value: float = Field(..., description="Numeric result for this step")
    unit: str = Field(..., description="Unit of the result value")
    regulation_reference: str = Field(..., description="EU legal/regulatory reference")


class AuditTrailReport(BaseModel):
    """Full explainability report that enumerates all core CBAM calculation steps."""

    steps: List[AuditStep] = Field(default_factory=list)
    legal_disclaimer: str = Field(..., description="Legal disclaimer for regulatory usage")


class ExplainabilityAgent:
    """Builds a deterministic, human-readable audit trail from payload and report data."""

    REG_SCOPE1 = "Regulation (EU) 2023/1773, Annex IV + IPCC 2006 Guidelines"
    REG_SCOPE2 = "Regulation (EU) 2023/1773, Annex IV"
    REG_PROCESS = "Regulation (EU) 2023/1773, Annex IV + IPCC 2006 Volume 3"
    REG_PRECURSOR = "Regulation (EU) 2023/1773, Annex II (Default Values)"
    REG_FINANCIAL = "Regulation (EU) 2023/956, Article 21 and Article 36"

    def generate_audit_trail(
        self,
        payload: InputPayload,
        report: "ExecutiveConsultingReport",
    ) -> AuditTrailReport:
        """Generate mandatory explainability trail with 5 regulator-oriented calculation steps."""
        allocation_rate = payload.cbam_allocation_rate
        summary = report.audit_summary

        scope1_value = float(summary.get("scope_1_direct_tco2e", 0.0))
        scope2_value = float(summary.get("scope_2_indirect_tco2e", 0.0))
        process_value = float(summary.get("process_emissions_tco2e", 0.0))
        precursor_value = float(summary.get("precursor_emissions_tco2e", 0.0))
        total_emissions = float(summary.get("total_emissions_tco2e", 0.0))
        ets_price = float(summary.get("ets_price_eur_per_ton", ETS_PRICE_PER_TON_CO2))
        phase_factor = float(summary.get("cbam_phase_factor", CBAM_PHASE_2026))
        total_liability = float(summary.get("total_liability_eur", 0.0))
        effective_liability = float(summary.get("effective_liability_eur", 0.0))

        natural_gas_m3 = payload.natural_gas_consumption_m3 or 0.0
        coal_tons = payload.coal_consumption_tons or 0.0
        natural_gas_emissions = natural_gas_m3 * NATURAL_GAS_TOTAL_FACTOR
        coal_factor = COAL_EMISSION_FACTOR * COAL_CALORIFIC_VALUE
        coal_emissions = coal_tons * coal_factor

        grid_factor = (
            payload.dynamic_grid_factor
            if payload.dynamic_grid_factor is not None
            else GRID_EMISSION_FACTOR_TURKEY
        )
        scope2_unallocated = payload.electricity_consumption_mwh * grid_factor

        process_inputs = payload.process_inputs
        electrode_ton = process_inputs.electrode_consumption_ton if process_inputs else 0.0
        limestone_ton = process_inputs.limestone_consumption_ton if process_inputs else 0.0
        electrode_emissions = electrode_ton * STOICHIOMETRIC_C_TO_CO2
        limestone_emissions = limestone_ton * LIMESTONE_EF

        precursor_total = 0.0
        benchmark_total = 0.0
        for precursor in payload.precursors:
            material_key = precursor.material_name.lower().strip().replace(" ", "-")
            actual_factor = (
                precursor.embedded_emissions_factor
                if precursor.embedded_emissions_factor is not None
                else DEFAULT_PRECURSOR_FACTORS.get(material_key, 0.0)
            )
            default_factor = DEFAULT_PRECURSOR_FACTORS.get(material_key, actual_factor)
            precursor_total += precursor.quantity_ton * actual_factor
            benchmark_total += precursor.quantity_ton * default_factor

        net_liable_emissions = (
            total_liability / ets_price if ets_price > 0 else 0.0
        )
        free_allocation = max(0.0, total_emissions - net_liable_emissions)
        net_liable_emissions = max(0.0, total_emissions - free_allocation)

        steps = [
            AuditStep(
                step_name="Scope 1 (Direct Fuels)",
                formula_applied=(
                    f"(({natural_gas_m3:.4f} m3 x {NATURAL_GAS_TOTAL_FACTOR:.6f}) + "
                    f"({coal_tons:.4f} ton x {coal_factor:.6f})) x {allocation_rate:.4f} "
                    f"= ({natural_gas_emissions:.4f} + {coal_emissions:.4f}) x {allocation_rate:.4f}"
                ),
                result_value=scope1_value,
                unit="tCO2e",
                regulation_reference=self.REG_SCOPE1,
            ),
            AuditStep(
                step_name="Scope 2 (Electricity with Dynamic Grid & Allocation)",
                formula_applied=(
                    f"{payload.electricity_consumption_mwh:.4f} MWh x {grid_factor:.6f} tCO2e/MWh x "
                    f"{allocation_rate:.4f} = {scope2_unallocated:.4f} x {allocation_rate:.4f}"
                ),
                result_value=scope2_value,
                unit="tCO2e",
                regulation_reference=self.REG_SCOPE2,
            ),
            AuditStep(
                step_name="Process Emissions (Chemistry)",
                formula_applied=(
                    f"(({electrode_ton:.4f} ton x {STOICHIOMETRIC_C_TO_CO2:.3f}) + "
                    f"({limestone_ton:.4f} ton x {LIMESTONE_EF:.3f})) x {allocation_rate:.4f} "
                    f"= ({electrode_emissions:.4f} + {limestone_emissions:.4f}) x {allocation_rate:.4f}"
                ),
                result_value=process_value,
                unit="tCO2e",
                regulation_reference=self.REG_PROCESS,
            ),
            AuditStep(
                step_name="Precursor Emissions (Supplier Benchmark Comparison)",
                formula_applied=(
                    f"Sum(quantity_i x supplier_factor_i) = {precursor_total:.4f} tCO2e; "
                    f"CBAM default benchmark = {benchmark_total:.4f} tCO2e; "
                    f"Delta = {precursor_total - benchmark_total:.4f} tCO2e"
                ),
                result_value=precursor_value,
                unit="tCO2e",
                regulation_reference=self.REG_PRECURSOR,
            ),
            AuditStep(
                step_name="Financial Calculation (ETS Price x Phase-in Factor)",
                formula_applied=(
                    f"max(0, {total_emissions:.4f} - {free_allocation:.4f}) x {ets_price:.2f} EUR/tCO2e "
                    f"x {phase_factor:.4f} = {net_liable_emissions:.4f} x {ets_price:.2f} x {phase_factor:.4f}"
                ),
                result_value=effective_liability,
                unit="EUR",
                regulation_reference=self.REG_FINANCIAL,
            ),
        ]

        disclaimer = (
            "This audit trail is generated deterministically from declared input data and configured CBAM "
            "calculation constants. It supports regulator review but does not replace legal interpretation "
            "of Regulation (EU) 2023/956 and Regulation (EU) 2023/1773 by authorized authorities."
        )

        return AuditTrailReport(steps=steps, legal_disclaimer=disclaimer)
