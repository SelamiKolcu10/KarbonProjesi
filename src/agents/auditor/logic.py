"""
Core Calculation Engine - Scope Segregation & Financial Impact

This is the heart of Agent #2: The Auditor Engine.
Calculates Scope 1 & 2 emissions, financial liability, and generates audit trail.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from .models import (
    InputPayload,
    AuditOutput,
    ScopeEmissions,
    FinancialImpact,
    AnomalyFlag,
    AuditLogEntry,
    ProcessInputs,
    PrecursorInput
)
from .physics import PhysicsValidator
from .logger import (
    AuditLogger,
    create_scope1_log,
    create_scope2_log,
    create_financial_log,
    create_validation_log
)
from .constants import (
    NATURAL_GAS_TOTAL_FACTOR,
    COAL_EMISSION_FACTOR,
    COAL_CALORIFIC_VALUE,
    ETS_PRICE_PER_TON_CO2,
    FREE_ALLOCATION_DEFAULT,
    CBAM_PHASE_2026,
    LEGAL_REFERENCES,
    ELECTRODE_CO2_FACTOR,
    LIMESTONE_CO2_FACTOR,
    STOICHIOMETRIC_C_TO_CO2,
    LIMESTONE_EF,
    DEFAULT_PRECURSOR_FACTORS,
    get_emission_factors,
    get_ets_price,
    get_precursor_emission_factor
)


class AuditorEngine:
    """
    Main calculation engine for CBAM compliance auditing.
    
    Workflow:
    1. Validate input data (physics checks)
    2. Calculate Scope 1 emissions (direct)
    3. Calculate Scope 2 emissions (indirect)
    4. Calculate financial liability (EU ETS)
    5. Generate audit trail
    6. Return comprehensive audit report
    """
    
    def __init__(
        self,
        strict_physics: bool = False,
        cbam_phase_factor: float = CBAM_PHASE_2026,
        free_allocation: float = FREE_ALLOCATION_DEFAULT
    ):
        """
        Args:
            strict_physics: If True, raises on CRITICAL physics violations
            cbam_phase_factor: CBAM phase-in percentage (0.0 to 1.0)
            free_allocation: Free allocation in tCO2e (default: 0 for worst-case)
        """
        self.strict_physics = strict_physics
        self.cbam_phase_factor = cbam_phase_factor
        self.free_allocation = free_allocation
        
        self.validator = PhysicsValidator(strict_mode=strict_physics)
        self.logger = AuditLogger()
    
    def audit(
        self,
        input_data: InputPayload,
        ets_price_override: Optional[float] = None
    ) -> AuditOutput:
        """
        Main audit function - performs complete CBAM compliance audit.
        
        Args:
            input_data: Input payload from Agent #1 or manual entry
            ets_price_override: Override ETS price (for simulation)
            
        Returns:
            Complete audit output with emissions, financials, and audit trail
        """
        # Reset logger for new audit
        self.logger.reset()
        
        # Step 1: Physics validation
        anomalies = self._run_physics_validation(input_data)
        
        # Step 2: Get emission factors (with overrides if provided)
        factors = get_emission_factors(input_data.overrides)
        
        # Step 3: Calculate Scope 1 emissions
        allocation_rate = input_data.cbam_allocation_rate
        
        scope1_emissions = self._calculate_scope1(
            input_data.natural_gas_consumption_m3 or 0.0,
            input_data.coal_consumption_tons or 0.0,
            factors,
            allocation_rate
        )
        
        # Step 4: Calculate Scope 2 emissions (use dynamic_grid_factor if provided)
        grid_factor = input_data.dynamic_grid_factor if input_data.dynamic_grid_factor is not None else factors['grid_electricity']
        
        scope2_emissions = self._calculate_scope2(
            input_data.electricity_consumption_mwh,
            grid_factor,
            allocation_rate
        )
        
        # Step 5: Calculate Process Emissions (v2.0)
        process_emissions = 0.0
        if input_data.process_inputs:
            process_emissions = self._calculate_process_emissions(input_data.process_inputs, allocation_rate)
        
        # Step 6: Calculate Precursor Emissions (v2.0)
        precursor_emissions, confidence_penalty = self._calculate_precursor_emissions(
            input_data.precursors
        )
        
        # Step 7: Calculate totals and intensity
        total_emissions = (
            scope1_emissions['total'] + 
            scope2_emissions['total'] + 
            process_emissions + 
            precursor_emissions
        )
        
        # Energy intensity
        total_energy_mwh = input_data.electricity_consumption_mwh
        energy_intensity = (
            total_energy_mwh / input_data.production_quantity_tons
            if input_data.production_quantity_tons > 0
            else 0.0
        )
        
        # Emission intensity
        emission_intensity = (
            total_emissions / input_data.production_quantity_tons
            if input_data.production_quantity_tons > 0
            else 0.0
        )
        
        # Create detailed breakdown
        breakdown = {
            "natural_gas": scope1_emissions['natural_gas'],
            "coal": scope1_emissions['coal'],
            "electricity": scope2_emissions['total'],
            "process": process_emissions,
            "precursors": precursor_emissions
        }
        
        # Create ScopeEmissions object
        emissions = ScopeEmissions(
            scope_1_direct=scope1_emissions['total'],
            scope_2_indirect=scope2_emissions['total'],
            total_emissions=total_emissions,
            natural_gas_emissions=scope1_emissions['natural_gas'],
            coal_emissions=scope1_emissions['coal'],
            electricity_emissions=scope2_emissions['total'],
            process_emissions=process_emissions,
            precursor_emissions=precursor_emissions,
            emission_intensity_per_ton=emission_intensity,
            energy_intensity_mwh_per_ton=energy_intensity,
            breakdown=breakdown
        )
        
        # Step 8: Calculate confidence score (v2.0)
        # Start at 1.0, deduct confidence_penalty from precursors
        confidence_score = max(0.5, 1.0 - confidence_penalty)
        
        # Step 9: Calculate financial impact
        ets_price = ets_price_override or ETS_PRICE_PER_TON_CO2
        financials = self._calculate_financials(
            total_emissions,
            input_data.production_quantity_tons,
            ets_price
        )
        
        # Step 10: Determine compliance status
        is_compliant, compliance_notes = self._assess_compliance(anomalies, emissions)
        
        # Step 11: Create audit output
        has_process_inputs = input_data.process_inputs is not None
        total_precursors = len(input_data.precursors)
        
        audit_output = AuditOutput(
            input_summary={
                "facility": input_data.facility_name,
                "facility_id": input_data.facility_id,
                "period": input_data.reporting_period,
                "production": input_data.production_quantity_tons,
                "electricity": input_data.electricity_consumption_mwh,
                "natural_gas": input_data.natural_gas_consumption_m3,
                "coal": input_data.coal_consumption_tons,
                "process_inputs": has_process_inputs,
                "precursors_count": total_precursors,
                "cbam_allocation_rate": allocation_rate,
                "dynamic_grid_factor": input_data.dynamic_grid_factor
            },
            emissions=emissions,
            financials=financials,
            confidence_score=confidence_score,
            anomalies=anomalies,
            audit_trail=self.logger.get_entries(),
            is_compliant=is_compliant,
            compliance_notes=compliance_notes,
            audit_timestamp=datetime.now(),
            auditor_version="2.0.0",
            regulatory_framework=f"{LEGAL_REFERENCES['cbam_regulation']}, {LEGAL_REFERENCES['cbam_implementing']}"
        )
        
        return audit_output
    
    def _run_physics_validation(self, input_data: InputPayload) -> List[AnomalyFlag]:
        """Run physics-based validation checks"""
        anomalies = self.validator.validate_all(
            production_tons=input_data.production_quantity_tons,
            electricity_mwh=input_data.electricity_consumption_mwh,
            natural_gas_m3=input_data.natural_gas_consumption_m3 or 0.0,
            coal_tons=input_data.coal_consumption_tons or 0.0
        )
        
        # Log validation results
        if not anomalies:
            create_validation_log(
                self.logger,
                "Physics validation passed",
                True,
                "All inputs are within physically plausible ranges"
            )
        else:
            for anomaly in anomalies:
                create_validation_log(
                    self.logger,
                    f"Anomaly detected: {anomaly.code}",
                    False,
                    anomaly.message
                )
        
        return anomalies
    
    def _calculate_scope1(
        self,
        natural_gas_m3: float,
        coal_tons: float,
        factors: Dict[str, float],
        allocation_rate: float = 1.0
    ) -> Dict[str, float]:
        """
        Calculate Scope 1 (Direct) Emissions.
        
        Scope 1 includes emissions from:
        - On-site fuel combustion (natural gas, coal, etc.)
        - Process emissions (if applicable)
        
        Args:
            natural_gas_m3: Natural gas consumption
            coal_tons: Coal consumption
            factors: Emission factors dictionary
            allocation_rate: CBAM allocation rate (0.0 to 1.0)
            
        Returns:
            Dictionary with breakdown
        """
        # Natural gas emissions
        ng_emissions = natural_gas_m3 * factors['natural_gas']
        
        if natural_gas_m3 > 0:
            create_scope1_log(
                self.logger,
                fuel_type="Natural Gas",
                consumption=natural_gas_m3,
                emission_factor=factors['natural_gas'],
                emissions=ng_emissions,
                unit="m³",
                source=LEGAL_REFERENCES['ipcc_guidelines']
            )
        
        # Coal emissions
        coal_emissions = coal_tons * factors['coal']
        
        if coal_tons > 0:
            create_scope1_log(
                self.logger,
                fuel_type="Coal",
                consumption=coal_tons,
                emission_factor=factors['coal'],
                emissions=coal_emissions,
                unit="tons",
                source=LEGAL_REFERENCES['ipcc_guidelines']
            )
        
        total_scope1 = ng_emissions + coal_emissions
        
        # Apply allocation rate
        total_scope1_allocated = total_scope1 * allocation_rate
        ng_emissions_allocated = ng_emissions * allocation_rate
        coal_emissions_allocated = coal_emissions * allocation_rate
        
        # Log total
        self.logger.log(
            category="SCOPE1",
            description="Total Scope 1 (Direct) Emissions",
            formula=f"{ng_emissions:.4f} (gas) + {coal_emissions:.4f} (coal) = {total_scope1:.4f}",
            result=total_scope1,
            unit="tCO2e",
            source=LEGAL_REFERENCES['cbam_implementing']
        )
        
        if allocation_rate < 1.0:
            self.logger.log(
                category="SCOPE1",
                description=f"Allocation Rate Applied: {allocation_rate * 100:.1f}% (Only {allocation_rate * 100:.1f}% of emissions are attributed to CBAM products)",
                formula=f"{total_scope1:.4f} × {allocation_rate} = {total_scope1_allocated:.4f}",
                result=total_scope1_allocated,
                unit="tCO2e",
                source="Co-Production Allocation Rule"
            )
        
        return {
            'natural_gas': ng_emissions_allocated,
            'coal': coal_emissions_allocated,
            'total': total_scope1_allocated
        }
    
    def _calculate_scope2(
        self,
        electricity_mwh: float,
        grid_factor: float,
        allocation_rate: float = 1.0
    ) -> Dict[str, float]:
        """
        Calculate Scope 2 (Indirect) Emissions.
        
        Scope 2 includes emissions from purchased electricity.
        Uses location-based method (grid emission factor).
        
        Args:
            electricity_mwh: Electricity consumption
            grid_factor: Grid emission factor (tCO2e/MWh) - may be dynamic override
            allocation_rate: CBAM allocation rate (0.0 to 1.0)
            
        Returns:
            Dictionary with emissions
        """
        scope2_emissions = electricity_mwh * grid_factor
        
        create_scope2_log(
            self.logger,
            electricity_mwh=electricity_mwh,
            grid_factor=grid_factor,
            emissions=scope2_emissions,
            grid_region="Turkey",
            source=f"{LEGAL_REFERENCES['cbam_implementing']}, Annex IV"
        )
        
        # Apply allocation rate
        scope2_allocated = scope2_emissions * allocation_rate
        
        if allocation_rate < 1.0:
            self.logger.log(
                category="SCOPE2",
                description=f"Allocation Rate Applied: {allocation_rate * 100:.1f}% (Only {allocation_rate * 100:.1f}% of emissions are attributed to CBAM products)",
                formula=f"{scope2_emissions:.4f} × {allocation_rate} = {scope2_allocated:.4f}",
                result=scope2_allocated,
                unit="tCO2e",
                source="Co-Production Allocation Rule"
            )
        
        return {
            'total': scope2_allocated
        }
    
    def _calculate_process_emissions(
        self,
        inputs: ProcessInputs,
        allocation_rate: float = 1.0
    ) -> float:
        """
        v2.0 - Calculate Process Emissions (electrodes, limestone).
        
        Process emissions are Scope 1 emissions from chemical reactions:
        - Electrode oxidation: C + O₂ → CO₂ (Stoichiometric factor: 3.664)
        - Limestone calcination: CaCO₃ → CaO + CO₂ (Emission factor: 0.44)
        
        Args:
            inputs: ProcessInputs object with electrode and limestone consumption
            allocation_rate: CBAM allocation rate (0.0 to 1.0)
            
        Returns:
            Total process emissions in tCO2e (after allocation)
        """
        # Calculate Electrode Emissions: C → CO₂
        electrode_emissions = inputs.electrode_consumption_ton * STOICHIOMETRIC_C_TO_CO2
        
        # Calculate Limestone Emissions: CaCO₃ → CaO + CO₂
        limestone_emissions = inputs.limestone_consumption_ton * LIMESTONE_EF
        
        total_process = electrode_emissions + limestone_emissions
        
        # Apply allocation rate
        total_process_allocated = total_process * allocation_rate
        
        if allocation_rate < 1.0:
            self.logger.log(
                category="PROCESS",
                description=f"Allocation Rate Applied: {allocation_rate * 100:.1f}% (Only {allocation_rate * 100:.1f}% of emissions are attributed to CBAM products)",
                formula=f"{total_process:.4f} × {allocation_rate} = {total_process_allocated:.4f}",
                result=total_process_allocated,
                unit="tCO2e",
                source="Co-Production Allocation Rule"
            )
        
        return total_process_allocated
    
    def _calculate_precursor_emissions(
        self,
        precursors: List[PrecursorInput]
    ) -> tuple[float, float]:
        """
        v2.0 - Calculate Precursor Emissions (embedded emissions from materials).
        
        Precursors are materials with embedded emissions (ferro-alloys, scrap, etc.)
        These are upstream Scope 3 emissions that must be reported under CBAM.
        
        Args:
            precursors: List of PrecursorInput objects
            
        Returns:
            Tuple of (total_emissions, confidence_penalty)
            - total_emissions: Total embedded emissions in tCO2e
            - confidence_penalty: Penalty score (0.0 to 0.5) based on default factor usage
        """
        if not precursors or len(precursors) == 0:
            return 0.0, 0.0
        
        total_emissions = 0.0
        num_defaults_used = 0
        
        for precursor in precursors:
            # Determine emission factor
            if precursor.embedded_emissions_factor is not None:
                # User provided actual factor
                factor = precursor.embedded_emissions_factor
            else:
                # Use CBAM default factor
                material_key = precursor.material_name.lower()
                factor = DEFAULT_PRECURSOR_FACTORS.get(material_key, 0.0)
                num_defaults_used += 1
            
            # Calculate emissions for this precursor
            emissions = precursor.quantity_ton * factor
            total_emissions += emissions
        
        # Calculate confidence penalty (0.1 per default used, max 0.5)
        confidence_penalty = min(0.5, num_defaults_used * 0.1)
        
        return total_emissions, confidence_penalty
    
    def _calculate_financials(
        self,
        total_emissions: float,
        production_tons: float,
        ets_price: float
    ) -> FinancialImpact:
        """
        Calculate financial liability under EU ETS/CBAM.
        
        Formula:
        Net Liable Emissions = Total Emissions - Free Allocation
        Total Liability = Net Liable Emissions × ETS Price
        Effective Liability = Total Liability × CBAM Phase Factor
        
        Args:
            total_emissions: Total emissions (Scope 1 + 2)
            production_tons: Production quantity
            ets_price: EU ETS carbon price
            
        Returns:
            FinancialImpact object
        """
        # Net liable emissions
        net_liable_emissions = max(0.0, total_emissions - self.free_allocation)
        
        # Total liability (without phase-in)
        total_liability = net_liable_emissions * ets_price
        
        # Effective liability (with CBAM phase-in)
        effective_liability = total_liability * self.cbam_phase_factor
        
        # Per ton steel
        liability_per_ton = (
            effective_liability / production_tons
            if production_tons > 0
            else 0.0
        )
        
        # Log calculations
        create_financial_log(
            self.logger,
            emissions=total_emissions,
            free_allocation=self.free_allocation,
            ets_price=ets_price,
            total_liability=total_liability,
            source=f"{LEGAL_REFERENCES['cbam_regulation']}, Article 21"
        )
        
        # CBAM phase-in adjustment
        self.logger.log(
            category="FINANCIAL",
            description=f"CBAM phase-in adjustment ({self.cbam_phase_factor * 100:.1f}% of full price)",
            formula=f"€{total_liability:.2f} × {self.cbam_phase_factor} = €{effective_liability:.2f}",
            result=effective_liability,
            unit="EUR",
            source=f"{LEGAL_REFERENCES['cbam_regulation']}, Article 36 (Transitional Period)"
        )
        
        return FinancialImpact(
            total_emissions_tco2e=total_emissions,
            free_allocation_tco2e=self.free_allocation,
            net_liable_emissions_tco2e=net_liable_emissions,
            ets_price_eur_per_ton=ets_price,
            total_liability_eur=total_liability,
            liability_per_ton_steel_eur=liability_per_ton,
            cbam_phase_factor=self.cbam_phase_factor,
            effective_liability_eur=effective_liability
        )
    
    def _calculate_confidence_score(
        self,
        num_precursor_defaults: int,
        has_process_inputs: bool,
        total_precursors: int
    ) -> float:
        """
        v2.0 - Calculate confidence score based on data quality.
        
        Scoring heuristic:
        - Start at 1.0 (100% confidence)
        - Deduct 0.1 if precursor factors are defaults (not actuals)
        - Deduct 0.2 if process_inputs are missing/estimated
        - Minimum score: 0.5
        
        Args:
            num_precursor_defaults: Number of precursors using default factors
            has_process_inputs: Whether process inputs were provided
            total_precursors: Total number of precursors
            
        Returns:
            Confidence score (0.5 to 1.0)
        """
        score = 1.0
        
        # Deduct for default precursor factors
        if num_precursor_defaults > 0 and total_precursors > 0:
            # Deduct 0.1 for each precursor using defaults
            deduction = 0.1 * (num_precursor_defaults / total_precursors)
            score -= deduction
            self.logger.log(
                category="VALIDATION",
                description=f"Confidence: -{deduction:.2f} for {num_precursor_defaults}/{total_precursors} default precursor factors",
                formula=f"1.0 - {deduction:.2f} = {score:.2f}",
                result=score,
                unit="score",
                source="Data Quality Assessment"
            )
        
        # Deduct for missing process inputs
        if not has_process_inputs:
            score -= 0.2
            self.logger.log(
                category="VALIDATION",
                description="Confidence: -0.2 for missing process inputs (electrodes, limestone)",
                formula=f"{score + 0.2:.2f} - 0.2 = {score:.2f}",
                result=score,
                unit="score",
                source="Data Quality Assessment"
            )
        
        # Enforce minimum score
        final_score = max(0.5, score)
        
        if final_score < 1.0:
            self.logger.log(
                category="VALIDATION",
                description=f"Final Confidence Score: {final_score * 100:.0f}%",
                formula=f"max(0.5, {score:.2f}) = {final_score:.2f}",
                result=final_score,
                unit="score",
                source="Data Quality Assessment"
            )
        
        return final_score
    
    def _assess_compliance(
        self,
        anomalies: List[AnomalyFlag],
        emissions: ScopeEmissions
    ) -> tuple[bool, List[str]]:
        """
        Assess overall compliance status.
        
        A facility is non-compliant if:
        - CRITICAL anomalies are detected
        - Emission intensity is unrealistic
        
        Returns:
            (is_compliant, compliance_notes) tuple
        """
        notes = []
        
        # Check for critical anomalies
        critical_anomalies = [a for a in anomalies if a.level.value == "CRITICAL"]
        
        if critical_anomalies:
            notes.append(
                f"⚠️ {len(critical_anomalies)} CRITICAL data quality issue(s) detected. "
                "Manual review required before CBAM submission."
            )
        
        # Check for warnings
        warnings = [a for a in anomalies if a.level.value == "WARNING"]
        
        if warnings:
            notes.append(
                f"⚠️ {len(warnings)} WARNING(s) detected. Review recommended."
            )
        
        # Emission intensity check
        if emissions.emission_intensity_per_ton > 2.0:
            notes.append(
                f"High emission intensity ({emissions.emission_intensity_per_ton:.2f} tCO2e/ton). "
                "Consider energy efficiency improvements."
            )
        
        # Overall compliance
        is_compliant = len(critical_anomalies) == 0
        
        if is_compliant and not notes:
            notes.append("✅ All checks passed. Data is suitable for CBAM reporting.")
        
        return is_compliant, notes
    
    def get_audit_trail_text(self) -> str:
        """Get formatted audit trail as text"""
        return self.logger.format_text()
