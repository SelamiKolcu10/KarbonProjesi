"""
Audit Trail Logger - Transparent Calculation Documentation

Every calculation step must be justifiable and traceable.
This module generates detailed audit logs for regulatory compliance.
"""

from typing import List, Optional
from .models import AuditLogEntry


class AuditLogger:
    """
    Generates transparent audit trail for all calculations.
    
    Regulatory Requirement: CBAM requires full traceability of emission calculations.
    Source: Regulation (EU) 2023/1773, Article 6
    """
    
    def __init__(self):
        self.entries: List[AuditLogEntry] = []
        self._step_counter = 0
    
    def log(
        self,
        category: str,
        description: str,
        formula: Optional[str] = None,
        result: Optional[float] = None,
        unit: Optional[str] = None,
        source: Optional[str] = None
    ) -> None:
        """
        Add an entry to the audit log.
        
        Args:
            category: Calculation category (VALIDATION, SCOPE1, SCOPE2, FINANCIAL, TOTAL)
            description: Human-readable description
            formula: Mathematical formula used
            result: Calculated result
            unit: Unit of measurement
            source: Regulatory reference
        """
        self._step_counter += 1
        
        entry = AuditLogEntry(
            step=self._step_counter,
            category=category,  # type: ignore
            description=description,
            formula=formula,
            result=result,
            unit=unit,
            source=source
        )
        
        self.entries.append(entry)
    
    def get_entries(self) -> List[AuditLogEntry]:
        """Get all audit log entries"""
        return self.entries
    
    def format_text(self) -> str:
        """Format audit log as human-readable text"""
        lines = []
        lines.append("="*80)
        lines.append("AUDIT TRAIL - CBAM Emissions & Financial Calculation")
        lines.append("="*80)
        lines.append("")
        
        current_category = None
        
        for entry in self.entries:
            # Category header
            if entry.category != current_category:
                lines.append("")
                lines.append(f"[{entry.category}]")
                lines.append("-"*80)
                current_category = entry.category
            
            # Step entry
            step_line = f"Step {entry.step}: {entry.description}"
            lines.append(step_line)
            
            if entry.formula:
                lines.append(f"  Formula: {entry.formula}")
            
            if entry.result is not None:
                unit_str = f" {entry.unit}" if entry.unit else ""
                lines.append(f"  Result:  {entry.result:.6f}{unit_str}")
            
            if entry.source:
                lines.append(f"  Source:  {entry.source}")
            
            lines.append("")
        
        lines.append("="*80)
        lines.append("End of Audit Trail")
        lines.append("="*80)
        
        return "\n".join(lines)
    
    def reset(self) -> None:
        """Reset audit log (for new calculation)"""
        self.entries = []
        self._step_counter = 0


# Convenience functions for common log patterns
def create_scope1_log(
    logger: AuditLogger,
    fuel_type: str,
    consumption: float,
    emission_factor: float,
    emissions: float,
    unit: str,
    source: str
) -> None:
    """Log a Scope 1 (direct) emission calculation"""
    logger.log(
        category="SCOPE1",
        description=f"Scope 1 emissions from {fuel_type}",
        formula=f"{consumption:.2f} {unit} × {emission_factor:.4f} tCO2/{unit} = {emissions:.4f} tCO2e",
        result=emissions,
        unit="tCO2e",
        source=source
    )


def create_scope2_log(
    logger: AuditLogger,
    electricity_mwh: float,
    grid_factor: float,
    emissions: float,
    grid_region: str,
    source: str
) -> None:
    """Log a Scope 2 (indirect) emission calculation"""
    logger.log(
        category="SCOPE2",
        description=f"Scope 2 emissions from electricity consumption ({grid_region} grid)",
        formula=f"{electricity_mwh:.2f} MWh × {grid_factor:.4f} tCO2e/MWh = {emissions:.4f} tCO2e",
        result=emissions,
        unit="tCO2e",
        source=source
    )


def create_financial_log(
    logger: AuditLogger,
    emissions: float,
    free_allocation: float,
    ets_price: float,
    total_liability: float,
    source: str
) -> None:
    """Log financial impact calculation"""
    net_emissions = emissions - free_allocation
    
    logger.log(
        category="FINANCIAL",
        description="Net emissions subject to carbon pricing",
        formula=f"{emissions:.2f} tCO2e - {free_allocation:.2f} tCO2e (free allocation) = {net_emissions:.2f} tCO2e",
        result=net_emissions,
        unit="tCO2e",
        source=source
    )
    
    logger.log(
        category="FINANCIAL",
        description="Total financial liability (EU ETS price)",
        formula=f"{net_emissions:.2f} tCO2e × €{ets_price:.2f}/tCO2e = €{total_liability:.2f}",
        result=total_liability,
        unit="EUR",
        source=source
    )


def create_validation_log(
    logger: AuditLogger,
    description: str,
    result: bool,
    details: Optional[str] = None
) -> None:
    """Log a validation check result"""
    status = "✅ PASSED" if result else "❌ FAILED"
    full_desc = f"{description}: {status}"
    
    if details:
        full_desc += f" - {details}"
    
    logger.log(
        category="VALIDATION",
        description=full_desc,
        source="Physics-based sanity check"
    )
