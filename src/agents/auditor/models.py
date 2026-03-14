"""
Pydantic V2 Data Models for Auditor Engine
Type-safe input/output schemas with validation
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Dict, Any, List, Optional, Literal
from datetime import datetime
from enum import Enum


class AnomalyLevel(str, Enum):
    """Anomaly severity levels"""
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"


class AnomalyFlag(BaseModel):
    """Anomaly detection result"""
    level: AnomalyLevel
    code: str = Field(..., description="Machine-readable anomaly code")
    message: str = Field(..., description="Human-readable description")
    detected_value: Optional[float] = Field(None, description="The anomalous value")
    expected_range: Optional[str] = Field(None, description="Expected range or threshold")
    
    model_config = ConfigDict(frozen=True)


class AuditLogEntry(BaseModel):
    """Single audit trail entry"""
    step: int = Field(..., ge=1, description="Step number in calculation sequence")
    category: Literal["VALIDATION", "SCOPE1", "SCOPE2", "PROCESS", "PRECURSOR", "FINANCIAL", "TOTAL"] = Field(
        ..., description="Calculation category"
    )
    description: str = Field(..., description="Human-readable calculation description")
    formula: Optional[str] = Field(None, description="Mathematical formula used")
    result: Optional[float] = Field(None, description="Calculated result")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    source: Optional[str] = Field(None, description="Regulatory reference")
    
    model_config = ConfigDict(frozen=True)


class PrecursorInput(BaseModel):
    """v2.0 - Precursor material with embedded emissions"""
    material_name: str = Field(..., min_length=1, description="Name of precursor material (e.g., 'Ferro-manganese')")
    quantity_ton: float = Field(..., ge=0, description="Quantity consumed in metric tons")
    embedded_emissions_factor: Optional[float] = Field(
        None, 
        ge=0, 
        description="Embedded CO2 factor (tCO2e/ton). If None, uses CBAM default values"
    )
    
    model_config = ConfigDict(frozen=True)


class ProcessInputs(BaseModel):
    """v2.0 - Process materials consumed in steel production"""
    electrode_consumption_ton: float = Field(0.0, ge=0, description="Graphite electrodes used in EAF (metric tons)")
    limestone_consumption_ton: float = Field(0.0, ge=0, description="Limestone flux materials (metric tons)")
    
    model_config = ConfigDict(frozen=True)


class InputPayload(BaseModel):
    """
    Input data from Agent #1 or manual entry.
    Mirrors the factory operational data required for CBAM compliance.
    """
    
    # Factory Identification
    facility_name: str = Field(..., min_length=1, description="Name of the steel production facility")
    facility_id: Optional[str] = Field(None, description="Unique facility identifier")
    reporting_period: str = Field(..., description="Reporting period (e.g., '2026-Q1', '2026-02')")
    
    # Production Data
    production_quantity_tons: float = Field(..., ge=0, description="Total steel production in metric tons")
    
    # Energy Consumption
    electricity_consumption_mwh: float = Field(..., ge=0, description="Total electricity consumption in MWh")
    natural_gas_consumption_m3: Optional[float] = Field(0.0, ge=0, description="Natural gas consumption in m³")
    coal_consumption_tons: Optional[float] = Field(0.0, ge=0, description="Coal consumption in metric tons")
    
    # Optional: Pre-calculated emissions (if available from Agent #1)
    direct_emissions_tco2e: Optional[float] = Field(default=None, ge=0, description="Pre-calculated Scope 1 emissions")
    indirect_emissions_tco2e: Optional[float] = Field(default=None, ge=0, description="Pre-calculated Scope 2 emissions")
    
    # v2.0 - Process Emissions & Precursors
    process_inputs: Optional[ProcessInputs] = Field(
        default_factory=ProcessInputs,
        description="Process materials (electrodes, limestone) consumed in production"
    )
    precursors: List[PrecursorInput] = Field(
        default_factory=list,
        description="List of precursor materials with embedded emissions"
    )
    
    # Co-Production Allocation (v3.0)
    cbam_allocation_rate: float = Field(
        default=1.0, ge=0.0, le=1.0,
        description="Percentage of total energy/process inputs dedicated to CBAM product (0.0 to 1.0)"
    )
    
    # Dynamic Grid Factor Override (v3.0)
    dynamic_grid_factor: Optional[float] = Field(
        default=None,
        description="External API override for grid emission factor (tCO2e/MWh). Falls back to static constant if None."
    )
    
    # Simulation Parameters (What-If Scenarios)
    overrides: Optional[Dict[str, float]] = Field(
        default=None, 
        description="Override emission factors for simulation (e.g., {'grid_factor': 0.0})"
    )
    
    # Metadata
    data_source: Optional[str] = Field("manual", description="Source of data (e.g., 'agent1', 'manual', 'scada')")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now, description="Data timestamp")
    
    @field_validator('reporting_period')
    @classmethod
    def validate_reporting_period(cls, v: str) -> str:
        """Ensure reporting period is in valid format"""
        if not v or len(v) < 6:
            raise ValueError("Reporting period must be at least 6 characters (e.g., '2026-Q1')")
        return v
    
    @field_validator('production_quantity_tons')
    @classmethod
    def validate_production(cls, v: float) -> float:
        """Ensure production is positive or zero"""
        if v < 0:
            raise ValueError("Production quantity cannot be negative")
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "facility_name": "ABC Döküm Sanayi",
                "facility_id": "TR-IST-001",
                "reporting_period": "2026-02",
                "production_quantity_tons": 500.0,
                "electricity_consumption_mwh": 200.0,
                "natural_gas_consumption_m3": 15000.0,
                "coal_consumption_tons": 0.0,
                "data_source": "agent1"
            }
        }
    )


class ScopeEmissions(BaseModel):
    """Emissions breakdown by scope"""
    scope_1_direct: float = Field(..., description="Scope 1 (direct) emissions in tCO2e")
    scope_2_indirect: float = Field(..., description="Scope 2 (indirect) emissions in tCO2e")
    total_emissions: float = Field(..., description="Total emissions (Scope 1 + Scope 2) in tCO2e")
    
    # Detailed breakdown
    natural_gas_emissions: float = Field(0.0, description="Emissions from natural gas in tCO2e")
    coal_emissions: float = Field(0.0, description="Emissions from coal in tCO2e")
    electricity_emissions: float = Field(0.0, description="Emissions from electricity in tCO2e")
    
    # v2.0 - Process & Precursor emissions
    process_emissions: float = Field(0.0, description="Process emissions (electrodes, limestone) in tCO2e")
    precursor_emissions: float = Field(0.0, description="Embedded emissions from precursors in tCO2e")
    
    # Intensity metrics
    emission_intensity_per_ton: float = Field(..., description="tCO2e per ton of steel produced")
    energy_intensity_mwh_per_ton: float = Field(..., description="MWh per ton of steel produced")
    
    # v2.0 - Detailed breakdown dictionary
    breakdown: Dict[str, float] = Field(
        default_factory=dict,
        description="Detailed emission breakdown by source (natural_gas, coal, electricity, process, precursors)"
    )
    
    model_config = ConfigDict(frozen=True)


class FinancialImpact(BaseModel):
    """Financial liability under EU ETS/CBAM"""
    total_emissions_tco2e: float = Field(..., description="Total emissions subject to carbon pricing")
    free_allocation_tco2e: float = Field(..., description="Free allocation (if any)")
    net_liable_emissions_tco2e: float = Field(..., description="Emissions subject to payment")
    
    ets_price_eur_per_ton: float = Field(..., description="EU ETS carbon price (EUR per tCO2e)")
    total_liability_eur: float = Field(..., description="Total estimated tax liability in EUR")
    liability_per_ton_steel_eur: float = Field(..., description="Liability per ton of steel (EUR/ton)")
    
    # CBAM phase-in factor (2026-2034)
    cbam_phase_factor: float = Field(..., ge=0.0, le=1.0, description="CBAM phase-in percentage")
    effective_liability_eur: float = Field(..., description="Effective liability after phase-in adjustment")
    
    model_config = ConfigDict(frozen=True)


class AuditOutput(BaseModel):
    """
    Complete audit output with all calculations, anomalies, and audit trail.
    This is the final deliverable from Agent #2.
    """
    
    # Input echo (for traceability)
    input_summary: Dict[str, Any] = Field(..., description="Summary of input data")
    
    # Core Results
    emissions: ScopeEmissions = Field(..., description="Emissions breakdown")
    financials: FinancialImpact = Field(..., description="Financial impact assessment")
    
    # v2.0 - Confidence Score
    confidence_score: float = Field(
        1.0, 
        ge=0.0, 
        le=1.0,
        description="Confidence score (0.0-1.0) based on data quality and completeness"
    )
    
    # Quality Assurance
    anomalies: List[AnomalyFlag] = Field(default_factory=list, description="Detected anomalies")
    audit_trail: List[AuditLogEntry] = Field(..., description="Complete calculation audit trail")
    
    # Compliance Status
    is_compliant: bool = Field(..., description="Overall compliance status")
    compliance_notes: List[str] = Field(default_factory=list, description="Compliance warnings/notes")
    
    # Metadata
    audit_timestamp: datetime = Field(default_factory=datetime.now, description="Audit execution timestamp")
    auditor_version: str = Field("1.0.0", description="Auditor engine version")
    regulatory_framework: str = Field("EU CBAM 2023/956", description="Regulatory framework applied")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "input_summary": {
                    "facility": "ABC Döküm Sanayi",
                    "period": "2026-02",
                    "production": 500.0
                },
                "emissions": {
                    "total_emissions": 86.0,
                    "scope_1_direct": 0.0,
                    "scope_2_indirect": 86.0
                },
                "financials": {
                    "total_liability_eur": 7310.00,
                    "ets_price_eur_per_ton": 85.00
                },
                "is_compliant": True
            }
        }
    )
    
    def summary_text(self) -> str:
        """Generate human-readable summary"""
        return f"""
CBAM Audit Report - {self.input_summary.get('facility', 'Unknown Facility')}
Period: {self.input_summary.get('period', 'Unknown')}
{'='*60}
Total Emissions: {self.emissions.total_emissions:.2f} tCO2e
  - Scope 1 (Direct): {self.emissions.scope_1_direct:.2f} tCO2e
  - Scope 2 (Indirect): {self.emissions.scope_2_indirect:.2f} tCO2e

Financial Liability: €{self.financials.total_liability_eur:,.2f}
  - ETS Price: €{self.financials.ets_price_eur_per_ton:.2f}/ton
  - Per Ton Steel: €{self.financials.liability_per_ton_steel_eur:.2f}/ton
  
Anomalies Detected: {len(self.anomalies)}
Compliance Status: {'✅ COMPLIANT' if self.is_compliant else '❌ NON-COMPLIANT'}
{'='*60}
"""
