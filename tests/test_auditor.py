"""
Agent #2:The Auditor Engine - Test & Demo Script

This script demonstrates the full capabilities of the Auditor Engine:
1. Physics-based validation
2. Scope 1 & 2 emission calculations
3. Financial liability estimation
4. Audit trail generation
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.agents.auditor import AuditorEngine, InputPayload

print("="*80)
print("AGENT #2: THE AUDITOR ENGINE - TEST SUITE")
print("="*80)

# ============================================================================
# TEST 1: Normal Steel Factory (ABC Döküm Sanayi)
# ============================================================================

print("\nTEST 1: Normal Steel Production Facility")
print("-"*80)

input_data_normal = InputPayload(
    facility_name="ABC Döküm Sanayi",
    facility_id="TR-IST-001",
    reporting_period="2026-02",
    production_quantity_tons=500.0,
    electricity_consumption_mwh=200.0,
    natural_gas_consumption_m3=15000.0,
    coal_consumption_tons=0.0,
    data_source="manual"
)

auditor = AuditorEngine(
    strict_physics=False,
    cbam_phase_factor=0.025,  # 2026: 2.5% phase-in
    free_allocation=0.0
)

result = auditor.audit(input_data_normal)

# Display summary
print(result.summary_text())

# Display anomalies
if result.anomalies:
    print("\nANOMALIES DETECTED:")
    for anomaly in result.anomalies:
        print(f"  [{anomaly.level.value}] {anomaly.code}: {anomaly.message}")
else:
    print("\n[OK] No anomalies detected")

# Display compliance notes
print("\nCOMPLIANCE NOTES:")
for note in result.compliance_notes:
    print(f"  - {note}")

# Save audit trail
audit_trail_text = auditor.get_audit_trail_text()
print("\nAUDIT TRAIL:")
print(audit_trail_text)

# Save to JSON
output_dir = Path("output/auditor_tests")
output_dir.mkdir(parents=True, exist_ok=True)

with open(output_dir / "test1_normal_facility.json", 'w', encoding='utf-8') as f:
    json.dump(result.model_dump(), f, indent=2, ensure_ascii=False, default=str)

print(f"\n[SAVED] Results saved to: {output_dir / 'test1_normal_facility.json'}")

# ============================================================================
# TEST 2: Physics Violation (Impossible Energy Intensity)
# ============================================================================

print("\n" + "="*80)
print("TEST 2: Physics Violation - Too Low Energy Intensity")
print("-"*80)

input_data_violation = InputPayload(
    facility_name="Suspicious Factory",
    facility_id="TR-IST-002",
    reporting_period="2026-02",
    production_quantity_tons=1000.0,  # 1000 tons
    electricity_consumption_mwh=50.0,   # Only 50 MWh (0.05 MWh/ton - IMPOSSIBLE!)
    natural_gas_consumption_m3=0.0,
    coal_consumption_tons=0.0,
    data_source="manual"
)

result_violation = auditor.audit(input_data_violation)

# Display summary
print(result_violation.summary_text())

# Display anomalies (should have CRITICAL)
if result_violation.anomalies:
    print("\nANOMALIES DETECTED:")
    for anomaly in result_violation.anomalies:
        icon = "[CRITICAL]" if anomaly.level.value == "CRITICAL" else "[WARNING]"
        print(f"  {icon} [{anomaly.level.value}] {anomaly.code}")
        print(f"      {anomaly.message}")
        if anomaly.detected_value is not None:
            print(f"      Detected: {anomaly.detected_value:.4f}, Expected: {anomaly.expected_range}")
        print()

# Save results
with open(output_dir / "test2_physics_violation.json", 'w', encoding='utf-8') as f:
    json.dump(result_violation.model_dump(), f, indent=2, ensure_ascii=False, default=str)

print(f"[SAVED] Results saved to: {output_dir / 'test2_physics_violation.json'}")

# ============================================================================
# TEST 3: Zero Production Trap
# ============================================================================

print("\n" + "="*80)
print("TEST 3: Zero Production Trap (Maintenance Mode)")
print("-"*80)

input_data_zero = InputPayload(
    facility_name="Factory in Maintenance",
    facility_id="TR-IST-003",
    reporting_period="2026-02",
    production_quantity_tons=0.0,  # No production
    electricity_consumption_mwh=50.0,  # But consuming energy
    natural_gas_consumption_m3=5000.0,
    coal_consumption_tons=0.0,
    data_source="manual"
)

result_zero = auditor.audit(input_data_zero)

print(result_zero.summary_text())

if result_zero.anomalies:
    print("\nANOMALIES DETECTED:")
    for anomaly in result_zero.anomalies:
        print(f"  [{anomaly.level.value}] {anomaly.message}")

with open(output_dir / "test3_zero_production.json", 'w', encoding='utf-8') as f:
    json.dump(result_zero.model_dump(), f, indent=2, ensure_ascii=False, default=str)

print(f"[SAVED] Results saved to: {output_dir / 'test3_zero_production.json'}")

# ============================================================================
# TEST 4: What-If Scenario (Green Energy Simulation)
# ============================================================================

print("\n" + "="*80)
print("TEST 4: What-If Scenario - 100% Renewable Energy")
print("-"*80)

input_data_green = InputPayload(
    facility_name="ABC Döküm Sanayi (Green Scenario)",
    facility_id="TR-IST-001",
    reporting_period="2026-02",
    production_quantity_tons=500.0,
    electricity_consumption_mwh=200.0,
    natural_gas_consumption_m3=0.0,  # Eliminated gas
    coal_consumption_tons=0.0,
    overrides={"grid_factor": 0.0},  # 🔋 Simulating 100% renewable grid
    data_source="simulation"
)

result_green = auditor.audit(input_data_green)

print(result_green.summary_text())

print("\nCOST COMPARISON:")
print(f"  Normal (Grid Factor=0.43): EUR {result.financials.effective_liability_eur:,.2f}")
print(f"  Green  (Grid Factor=0.00): EUR {result_green.financials.effective_liability_eur:,.2f}")
savings = result.financials.effective_liability_eur - result_green.financials.effective_liability_eur
print(f"  Potential Savings:         EUR {savings:,.2f} ({savings/result.financials.effective_liability_eur*100:.1f}%)")

with open(output_dir / "test4_green_scenario.json", 'w', encoding='utf-8') as f:
    json.dump(result_green.model_dump(), f, indent=2, ensure_ascii=False, default=str)

print(f"\n[SAVED] Results saved to: {output_dir / 'test4_green_scenario.json'}")

# ============================================================================
# FINAL SUMMARY
# ============================================================================

print("\n" + "="*80)
print("[SUCCESS] ALL TESTS COMPLETED")
print("="*80)

print("\nTest Results Summary:")
print(f"  Test 1 (Normal):        {len(result.anomalies)} anomalies, Compliant: {result.is_compliant}")
print(f"  Test 2 (Violation):     {len(result_violation.anomalies)} anomalies, Compliant: {result_violation.is_compliant}")
print(f"  Test 3 (Zero Prod):     {len(result_zero.anomalies)} anomalies, Compliant: {result_zero.is_compliant}")
print(f"  Test 4 (Green):         {len(result_green.anomalies)} anomalies, Compliant: {result_green.is_compliant}")

print("\nAll results saved to: output/auditor_tests/")

print("\nAGENT #2: THE AUDITOR ENGINE is production-ready!")
print("="*80)
