"""
Test script for Agent Auditor v2.0 upgrade
Demonstrates Process Emissions, Precursors, and Confidence Scoring
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
from src.agents.auditor.models import InputPayload, ProcessInputs, PrecursorInput
from src.agents.auditor.logic import AuditorEngine
import json


def test_v2_full_feature():
    """Test with all v2.0 features enabled"""
    
    # Create input with process emissions and precursors
    input_data = InputPayload(
        facility_name="ABC Steel Works (v2.0 Test)",
        facility_id="TR-IST-001",
        reporting_period="2026-03",
        production_quantity_tons=500.0,
        
        # Energy consumption
        electricity_consumption_mwh=200.0,
        natural_gas_consumption_m3=15000.0,
        coal_consumption_tons=0.0,
        data_source="manual",
        
        # v2.0 - Process Inputs (Electrodes & Limestone)
        process_inputs=ProcessInputs(
            electrode_consumption_ton=2.5,  # 2.5 tons of graphite electrodes
            limestone_consumption_ton=10.0  # 10 tons of limestone flux
        ),
        
        # v2.0 - Precursors with embedded emissions
        precursors=[
            PrecursorInput(
                material_name="ferro-manganese",
                quantity_ton=5.0,
                embedded_emissions_factor=1.65  # Actual supplier data
            ),
            PrecursorInput(
                material_name="ferro-silicon",
                quantity_ton=3.0,
                embedded_emissions_factor=None  # Will use CBAM default
            ),
            PrecursorInput(
                material_name="scrap-steel",
                quantity_ton=450.0,
                embedded_emissions_factor=0.35  # Actual supplier data
            )
        ]
    )
    
    # Run audit
    auditor = AuditorEngine(strict_physics=False)
    result = auditor.audit(input_data)
    
    # Display results
    print("=" * 70)
    print("CBAM Auditor v2.0 - Full Feature Test")
    print("=" * 70)
    print(f"Facility: {result.input_summary['facility']}")
    print(f"Period: {result.input_summary['period']}")
    print(f"Production: {result.input_summary['production']} tons")
    print()
    
    print("EMISSIONS BREAKDOWN:")
    print(f"  Scope 1 (Fuel):        {result.emissions.scope_1_direct:>10.2f} tCO2e")
    print(f"  Scope 2 (Electricity): {result.emissions.scope_2_indirect:>10.2f} tCO2e")
    print(f"  Process Emissions:     {result.emissions.process_emissions:>10.2f} tCO2e  ⭐ NEW")
    print(f"  Precursor Emissions:   {result.emissions.precursor_emissions:>10.2f} tCO2e  ⭐ NEW")
    print(f"  {'─' * 50}")
    print(f"  TOTAL EMISSIONS:       {result.emissions.total_emissions:>10.2f} tCO2e")
    print()
    
    print(f"CONFIDENCE SCORE: {result.confidence_score * 100:.0f}%  ⭐ NEW")
    print()
    
    print("FINANCIAL IMPACT:")
    print(f"  Total Liability:  €{result.financials.total_liability_eur:>12,.2f}")
    print(f"  Per Ton Steel:    €{result.financials.liability_per_ton_steel_eur:>12,.2f}/ton")
    print()
    
    print("COMPLIANCE STATUS:", "✅ COMPLIANT" if result.is_compliant else "❌ NON-COMPLIANT")
    print()
    
    # Show breakdown
    print("DETAILED PROCESS BREAKDOWN:")
    if input_data.process_inputs:
        print(f"  Electrode (C→CO2):     {input_data.process_inputs.electrode_consumption_ton} ton × 3.664 = {input_data.process_inputs.electrode_consumption_ton * 3.664:.2f} tCO2e")
        print(f"  Limestone (CaCO3):     {input_data.process_inputs.limestone_consumption_ton} ton × 0.44 = {input_data.process_inputs.limestone_consumption_ton * 0.44:.2f} tCO2e")
    print()
    
    print("PRECURSOR BREAKDOWN:")
    if input_data.precursors:
        for precursor in input_data.precursors:
            factor = precursor.embedded_emissions_factor or "default"
            print(f"  {precursor.material_name:20s} {precursor.quantity_ton:>8.2f} ton  (factor: {factor})")
    
    print("=" * 70)
    
    return result


def test_v2_without_process():
    """Test without process inputs (should lower confidence score)"""
    
    input_data = InputPayload(
        facility_name="XYZ Steel (No Process Data)",
        facility_id="TR-IST-002",
        reporting_period="2026-03",
        production_quantity_tons=300.0,
        electricity_consumption_mwh=120.0,
        natural_gas_consumption_m3=0.0,
        coal_consumption_tons=0.0,
        data_source="manual",
        
        # No process_inputs provided
        process_inputs=None,
        
        # Only precursors
        precursors=[
            PrecursorInput(
                material_name="scrap-steel",
                quantity_ton=280.0,
                embedded_emissions_factor=None  # Using default
            )
        ]
    )
    
    auditor = AuditorEngine()
    result = auditor.audit(input_data)
    
    print("\nTEST: Without Process Inputs")
    print(f"Confidence Score: {result.confidence_score * 100:.0f}% (expected: <100% due to missing data)")
    print(f"Total Emissions: {result.emissions.total_emissions:.2f} tCO2e")
    print()
    
    return result


def test_v2_backward_compatible():
    """Test backward compatibility - v1.0 style input (no process/precursors)"""
    
    input_data = InputPayload(
        facility_name="Legacy Steel (v1.0 Compatible)",
        facility_id="TR-IST-003",
        reporting_period="2026-03",
        production_quantity_tons=400.0,
        electricity_consumption_mwh=160.0,
        natural_gas_consumption_m3=10000.0,
        coal_consumption_tons=0.0,
        data_source="manual"
        # No process_inputs, no precursors
    )
    
    auditor = AuditorEngine()
    result = auditor.audit(input_data)
    
    print("\nTEST: Backward Compatibility (v1.0 style)")
    print(f"Confidence Score: {result.confidence_score * 100:.0f}%")
    print(f"Process Emissions: {result.emissions.process_emissions:.2f} tCO2e (expected: 0.0)")
    print(f"Precursor Emissions: {result.emissions.precursor_emissions:.2f} tCO2e (expected: 0.0)")
    print(f"Total Emissions: {result.emissions.total_emissions:.2f} tCO2e")
    print()
    
    return result


if __name__ == "__main__":
    print("\n🧬 CBAM Auditor v2.0 - Upgrade Verification Tests\n")
    
    # Test 1: Full v2.0 features
    result1 = test_v2_full_feature()
    
    # Test 2: Missing process data
    result2 = test_v2_without_process()
    
    # Test 3: Backward compatibility
    result3 = test_v2_backward_compatible()
    
    print("=" * 70)
    print("✅ All v2.0 tests completed successfully!")
    print("=" * 70)
    
    # Save one result to JSON for inspection
    with open("output/auditor_v2_demo.json", "w", encoding="utf-8") as f:
        json.dump(result1.model_dump(mode='python'), f, indent=2, default=str)
    
    print("\n📄 Full audit report saved to: output/auditor_v2_demo.json")
